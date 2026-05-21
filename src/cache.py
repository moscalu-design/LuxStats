"""Local caching layer: filesystem CSVs + DuckDB tables.

Each downloaded dataflow becomes a DuckDB table named ``df_<dataflow_id>``.
Metadata about which datasets are cached lives in ``_meta_datasets``.
"""

from __future__ import annotations

import json
import os
import re
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any

import duckdb
import pandas as pd

from src.statec_client import Dataflow, StatecClient

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / "data" / "cache"
CSV_DIR = CACHE_DIR / "csv"
DUCKDB_PATH = CACHE_DIR / "lustat.duckdb"
DATAFLOWS_JSON = CACHE_DIR / "dataflows.json"

DATAFLOWS_TTL_SECONDS = 24 * 3600


def _ensure_dirs() -> None:
    CSV_DIR.mkdir(parents=True, exist_ok=True)


def _con() -> duckdb.DuckDBPyConnection:
    _ensure_dirs()
    con = duckdb.connect(str(DUCKDB_PATH))
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS _meta_datasets (
            dataset_id   TEXT PRIMARY KEY,
            agency       TEXT,
            version      TEXT,
            name_en      TEXT,
            name_fr      TEXT,
            table_name   TEXT,
            row_count    BIGINT,
            columns_json TEXT,
            fetched_at   TIMESTAMP
        )
        """
    )
    return con


def table_name_for(dataset_id: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9_]", "_", dataset_id)
    return f"df_{safe}"


# ----- Dataflow list cache -----------------------------------------------

def load_dataflows(client: StatecClient, force_refresh: bool = False) -> list[Dataflow]:
    _ensure_dirs()
    if (
        not force_refresh
        and DATAFLOWS_JSON.exists()
        and time.time() - DATAFLOWS_JSON.stat().st_mtime < DATAFLOWS_TTL_SECONDS
    ):
        raw = json.loads(DATAFLOWS_JSON.read_text(encoding="utf-8"))
        return [Dataflow(**r) for r in raw]
    flows = client.list_dataflows()
    DATAFLOWS_JSON.write_text(
        json.dumps([asdict(f) for f in flows], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return flows


# ----- Dataset cache -----------------------------------------------------

def is_dataset_cached(dataset_id: str) -> bool:
    if not DUCKDB_PATH.exists():
        return False
    con = _con()
    try:
        row = con.execute(
            "SELECT 1 FROM _meta_datasets WHERE dataset_id = ?", [dataset_id]
        ).fetchone()
        return row is not None
    finally:
        con.close()


def list_cached_datasets() -> pd.DataFrame:
    if not DUCKDB_PATH.exists():
        return pd.DataFrame()
    con = _con()
    try:
        return con.execute(
            """
            SELECT dataset_id, name_en, row_count, fetched_at, table_name
            FROM _meta_datasets
            ORDER BY fetched_at DESC
            """
        ).fetch_df()
    finally:
        con.close()


def fetch_and_cache_dataset(
    client: StatecClient,
    flow: Dataflow,
    force_refresh: bool = False,
) -> tuple[pd.DataFrame, Path]:
    """Fetch a dataflow, persist its CSV to disk, and load it into DuckDB."""
    _ensure_dirs()
    csv_path = CSV_DIR / f"{flow.id}.csv"
    if not force_refresh and csv_path.exists() and csv_path.stat().st_size > 0:
        csv_text = csv_path.read_text(encoding="utf-8")
    else:
        csv_text = client.get_data_csv(flow.flow_ref)
        csv_path.write_text(csv_text, encoding="utf-8")
    from src.statec_client import parse_sdmx_csv  # avoid cycle at import time
    df = parse_sdmx_csv(csv_text)
    if df.empty:
        return df, csv_path
    _write_to_duckdb(flow, df)
    return df, csv_path


def _write_to_duckdb(flow: Dataflow, df: pd.DataFrame) -> str:
    table = table_name_for(flow.id)
    con = _con()
    try:
        # Register DataFrame and overwrite the table atomically.
        con.register("incoming_df", df)
        con.execute(f'DROP TABLE IF EXISTS "{table}"')
        con.execute(f'CREATE TABLE "{table}" AS SELECT * FROM incoming_df')
        con.unregister("incoming_df")
        con.execute(
            """
            INSERT OR REPLACE INTO _meta_datasets
                (dataset_id, agency, version, name_en, name_fr,
                 table_name, row_count, columns_json, fetched_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """,
            [
                flow.id,
                flow.agency,
                flow.version,
                flow.name_en,
                flow.name_fr,
                table,
                int(len(df)),
                json.dumps(list(df.columns)),
            ],
        )
    finally:
        con.close()
    return table


def load_dataset(dataset_id: str) -> pd.DataFrame:
    table = table_name_for(dataset_id)
    con = _con()
    try:
        return con.execute(f'SELECT * FROM "{table}"').fetch_df()
    finally:
        con.close()


def get_dataset_meta(dataset_id: str) -> dict[str, Any] | None:
    con = _con()
    try:
        row = con.execute(
            """
            SELECT dataset_id, agency, version, name_en, name_fr,
                   table_name, row_count, columns_json, fetched_at
            FROM _meta_datasets WHERE dataset_id = ?
            """,
            [dataset_id],
        ).fetchone()
        if not row:
            return None
        keys = [
            "dataset_id", "agency", "version", "name_en", "name_fr",
            "table_name", "row_count", "columns_json", "fetched_at",
        ]
        meta = dict(zip(keys, row))
        meta["columns"] = json.loads(meta.pop("columns_json") or "[]")
        return meta
    finally:
        con.close()


def schema_for_query_builder(dataset_id: str, sample_per_column: int = 8) -> dict[str, Any]:
    """Compact schema description with sample values for deterministic tools."""
    meta = get_dataset_meta(dataset_id)
    if not meta:
        return {}
    df = load_dataset(dataset_id)
    cols: list[dict[str, Any]] = []
    for col in df.columns:
        series = df[col]
        dtype = str(series.dtype)
        sample: list[Any] = []
        try:
            if pd.api.types.is_numeric_dtype(series):
                sample = [
                    float(x) for x in series.dropna().head(sample_per_column).tolist()
                ]
            else:
                sample = (
                    series.dropna().astype(str).unique().tolist()[:sample_per_column]
                )
        except Exception:
            sample = []
        cols.append({"name": col, "dtype": dtype, "samples": sample})
    return {
        "dataset_id": dataset_id,
        "name": meta.get("name_en") or meta.get("name_fr") or dataset_id,
        "row_count": meta.get("row_count"),
        "columns": cols,
    }
