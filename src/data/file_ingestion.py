"""Download and inspection layer for STATEC Excel / CSV source files.

The goal is not to perfectly normalize every workbook — STATEC files are
irregular. The goal is a reliable pipeline: catalog → download → inspect →
preview, with an honest ingestion status on every file.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import pandas as pd

from src.config import CACHE_DIR
from src.data.communes import list_communes
from src.data.statec_web import REQUEST_TIMEOUT, USER_AGENT, is_allowed_url

INGEST_DIR = CACHE_DIR / "ingest"

# Ingestion lifecycle states.
INGESTION_STATES = [
    "cataloged",          # known, not downloaded
    "downloaded",         # file is on disk
    "inspected",          # sheets/columns read
    "importable",         # has plausible time + value columns
    "needs_manual_mapping",  # readable but structure unclear
    "failed",             # download or read failed
]

_TIME_HINTS = ("year", "annee", "année", "time", "period", "periode", "période",
               "date", "trimestre", "quarter", "month", "mois")
_GEO_HINTS = ("commune", "municipalit", "canton", "geo", "localite", "localité",
              "region", "région", "pays", "country")
_COMMUNE_NAMES = {c.casefold() for c in list_communes()}


def _filename_for(file_url: str) -> str:
    name = urlparse(file_url).path.rsplit("/", 1)[-1]
    return re.sub(r"[^A-Za-z0-9._-]", "_", name) or "source_file"


def cached_file_path(source_record: dict[str, Any]) -> Path:
    """Where a source file is (or would be) cached on disk."""
    return INGEST_DIR / _filename_for(source_record.get("file_url", ""))


def is_file_cached(source_record: dict[str, Any]) -> bool:
    path = cached_file_path(source_record)
    return path.exists() and path.stat().st_size > 0


def download_source_file(source_record: dict[str, Any],
                         force_refresh: bool = False) -> Path:
    """Download a source file to the local cache; return its path.

    Raises ``ValueError`` for a non-official domain and ``requests`` errors
    on network failure.
    """
    import requests

    file_url = source_record.get("file_url", "")
    if not file_url:
        raise ValueError("Source record has no file_url to download.")
    if not is_allowed_url(file_url):
        raise ValueError(f"Refusing to download a non-official domain: {file_url}")
    path = cached_file_path(source_record)
    if path.exists() and path.stat().st_size > 0 and not force_refresh:
        return path
    resp = requests.get(file_url, headers={"User-Agent": USER_AGENT},
                        timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    INGEST_DIR.mkdir(parents=True, exist_ok=True)
    path.write_bytes(resp.content)
    return path


def cache_source_file(source_record: dict[str, Any]) -> Path:
    """Ensure a source file is cached locally; return its path."""
    return download_source_file(source_record, force_refresh=False)


def _engine_for(path: Path) -> str | None:
    suffix = path.suffix.lower()
    if suffix == ".xls":
        return "xlrd"
    if suffix in (".xlsx", ".xlsm"):
        return "openpyxl"
    return None


def list_excel_sheets(path: Path | str) -> list[str]:
    """List sheet names in an Excel workbook; empty list on failure."""
    path = Path(path)
    try:
        with pd.ExcelFile(path, engine=_engine_for(path)) as book:
            return list(book.sheet_names)
    except Exception:  # noqa: BLE001
        return []


def safe_read_excel(path: Path | str, sheet_name: str | int | None = 0,
                    **kwargs: Any) -> pd.DataFrame:
    """Read an Excel sheet defensively; return an empty frame on any failure."""
    path = Path(path)
    try:
        if path.suffix.lower() == ".csv":
            return pd.read_csv(path, dtype=str, **kwargs)
        df = pd.read_excel(path, sheet_name=sheet_name, engine=_engine_for(path),
                           **kwargs)
        return df if isinstance(df, pd.DataFrame) else pd.DataFrame()
    except Exception:  # noqa: BLE001
        return pd.DataFrame()


def normalize_excel_table(df: pd.DataFrame) -> pd.DataFrame:
    """Light, non-destructive cleanup: trim names, drop fully-empty rows/cols."""
    if df is None or df.empty:
        return pd.DataFrame()
    out = df.copy()
    out.columns = [str(c).strip() for c in out.columns]
    out = out.dropna(axis=0, how="all").dropna(axis=1, how="all")
    return out.reset_index(drop=True)


def preview_excel_sheet(path: Path | str, sheet_name: str | int | None = 0,
                        rows: int = 20) -> pd.DataFrame:
    """Return the first ``rows`` of a sheet, cleaned, for on-screen preview."""
    return normalize_excel_table(safe_read_excel(path, sheet_name=sheet_name)).head(rows)


def _classify_columns(df: pd.DataFrame) -> dict[str, list[str]]:
    time_cols, geo_cols, value_cols = [], [], []
    for col in df.columns:
        name = str(col).strip().casefold()
        series = df[col]
        if any(h in name for h in _TIME_HINTS):
            time_cols.append(str(col))
        if any(h in name for h in _GEO_HINTS):
            geo_cols.append(str(col))
        numeric = pd.to_numeric(series, errors="coerce")
        if numeric.notna().mean() > 0.6 and str(col) not in time_cols:
            value_cols.append(str(col))
    return {"time": time_cols, "geography": geo_cols, "value": value_cols}


def _detect_communes(df: pd.DataFrame) -> list[str]:
    found: set[str] = set()
    for col in df.columns:
        try:
            values = df[col].dropna().astype(str).str.strip().str.casefold()
        except Exception:  # noqa: BLE001
            continue
        for value in values.unique():
            if value in _COMMUNE_NAMES:
                found.add(value)
        if len(found) > 30:
            break
    return sorted(found)


def inspect_excel_file(path: Path | str) -> dict[str, Any]:
    """Inspect a workbook: sheets, columns, likely roles, detected communes."""
    path = Path(path)
    info: dict[str, Any] = {
        "path": str(path),
        "sheet_names": [],
        "sheet_count": 0,
        "sheets": [],
        "detected_communes": [],
        "notes": "",
        "status": "downloaded",
    }
    if not path.exists():
        info["status"] = "failed"
        info["notes"] = "File is not downloaded yet."
        return info

    sheets = list_excel_sheets(path) if path.suffix.lower() != ".csv" else ["(csv)"]
    if not sheets:
        info["status"] = "failed"
        info["notes"] = "Could not open the file as an Excel/CSV workbook."
        return info

    info["sheet_names"] = sheets
    info["sheet_count"] = len(sheets)
    importable = False
    all_communes: set[str] = set()
    for sheet in sheets:
        sheet_arg = None if sheet == "(csv)" else sheet
        df = normalize_excel_table(safe_read_excel(path, sheet_name=sheet_arg))
        roles = _classify_columns(df) if not df.empty else {"time": [], "geography": [], "value": []}
        communes = _detect_communes(df) if not df.empty else []
        all_communes.update(communes)
        if roles["time"] and roles["value"]:
            importable = True
        info["sheets"].append({
            "name": sheet,
            "rows": int(len(df)),
            "columns": [str(c) for c in df.columns][:40],
            "likely_time_columns": roles["time"],
            "likely_geography_columns": roles["geography"],
            "likely_value_columns": roles["value"][:10],
            "detected_communes": communes[:10],
        })
    info["detected_communes"] = sorted(all_communes)
    info["status"] = "importable" if importable else "needs_manual_mapping"
    info["notes"] = (
        "At least one sheet has a plausible time + value structure."
        if importable else
        "Readable, but no clear time/value structure was detected — this file "
        "needs a manual column mapping before it can be charted."
    )
    return info


def extract_excel_metadata(path: Path | str) -> dict[str, Any]:
    """Compact metadata summary for a workbook (sheet count, total rows)."""
    info = inspect_excel_file(path)
    return {
        "path": info["path"],
        "sheet_count": info["sheet_count"],
        "total_rows": sum(s["rows"] for s in info["sheets"]),
        "has_commune_data": bool(info["detected_communes"]),
        "status": info["status"],
    }


def ingestion_status(source_record: dict[str, Any]) -> str:
    """Current ingestion state for a source record (no network access)."""
    file_url = source_record.get("file_url", "")
    if not file_url:
        return "cataloged"
    if not is_file_cached(source_record):
        return "cataloged"
    return inspect_excel_file(cached_file_path(source_record)).get("status", "downloaded")
