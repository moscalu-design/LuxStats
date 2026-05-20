"""Execute structured JSON query plans against DuckDB.

A query plan describes WHAT to compute; this module turns it into SQL and
runs it. The LLM is never trusted to do arithmetic — it only produces the
plan, and we validate every column reference against the actual schema.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import duckdb
import pandas as pd

from src.cache import DUCKDB_PATH, table_name_for

ALLOWED_AGGS = {"sum", "avg", "mean", "min", "max", "count", "median", "none"}
ALLOWED_ORDERS = {"asc", "desc"}


@dataclass
class QueryResult:
    sql: str
    df: pd.DataFrame
    plan: dict[str, Any]
    columns_used: list[str]
    warnings: list[str]


def _q(ident: str) -> str:
    return '"' + ident.replace('"', '""') + '"'


def _validate_columns(plan: dict[str, Any], schema_cols: list[str]) -> tuple[dict[str, Any], list[str]]:
    """Drop any references to columns that don't exist; return cleaned plan + warnings."""
    schema_set = set(schema_cols)
    warnings: list[str] = []

    def keep(col: str) -> bool:
        if col in schema_set:
            return True
        warnings.append(f"Unknown column dropped: {col}")
        return False

    cleaned = dict(plan)

    filters = cleaned.get("filters") or {}
    if isinstance(filters, dict):
        cleaned["filters"] = {k: v for k, v in filters.items() if keep(k)}
    else:
        cleaned["filters"] = {}
        warnings.append("filters must be an object; ignored")

    dims = cleaned.get("dimensions") or []
    cleaned["dimensions"] = [c for c in dims if isinstance(c, str) and keep(c)]

    measures = cleaned.get("measures") or []
    cleaned["measures"] = [c for c in measures if isinstance(c, str) and keep(c)]

    sort = cleaned.get("sort") or []
    clean_sort: list[dict[str, str]] = []
    for s in sort:
        if not isinstance(s, dict):
            continue
        col = s.get("column")
        order = (s.get("order") or "asc").lower()
        if col and (col in schema_set or _looks_like_alias(col, cleaned)):
            clean_sort.append({"column": col, "order": order if order in ALLOWED_ORDERS else "asc"})
    cleaned["sort"] = clean_sort

    agg = (cleaned.get("aggregation") or "none").lower()
    if agg not in ALLOWED_AGGS:
        warnings.append(f"Unknown aggregation '{agg}' — falling back to 'none'")
        agg = "none"
    if agg == "mean":
        agg = "avg"
    cleaned["aggregation"] = agg

    return cleaned, warnings


def _looks_like_alias(col: str, plan: dict[str, Any]) -> bool:
    # measures may be aliased after aggregation, e.g. OBS_VALUE -> OBS_VALUE
    return col in (plan.get("measures") or [])


def build_sql(plan: dict[str, Any], dataset_id: str) -> tuple[str, list[str]]:
    table = table_name_for(dataset_id)
    filters: dict[str, Any] = plan.get("filters") or {}
    dimensions: list[str] = plan.get("dimensions") or []
    measures: list[str] = plan.get("measures") or ["OBS_VALUE"]
    agg: str = plan.get("aggregation") or "none"
    sort: list[dict[str, str]] = plan.get("sort") or []
    limit: int | None = plan.get("limit")

    columns_used = list(dict.fromkeys(list(filters.keys()) + dimensions + measures))

    select_parts: list[str] = [_q(c) for c in dimensions]
    if agg == "none":
        select_parts.extend(_q(m) for m in measures)
    elif agg == "count":
        select_parts.append("COUNT(*) AS count")
    else:
        for m in measures:
            select_parts.append(f"{agg.upper()}({_q(m)}) AS {_q(m)}")

    if not select_parts:
        select_parts = ["*"]

    sql = f"SELECT {', '.join(select_parts)} FROM {_q(table)}"

    where_clauses: list[str] = []
    params: list[Any] = []
    for col, val in filters.items():
        if isinstance(val, list):
            if not val:
                continue
            placeholders = ", ".join(["?"] * len(val))
            where_clauses.append(f"{_q(col)} IN ({placeholders})")
            params.extend([str(v) for v in val])
        elif isinstance(val, dict):
            # Range filter: {"min": ..., "max": ...}
            if "min" in val and val["min"] is not None:
                where_clauses.append(f"{_q(col)} >= ?")
                params.append(val["min"])
            if "max" in val and val["max"] is not None:
                where_clauses.append(f"{_q(col)} <= ?")
                params.append(val["max"])
        else:
            where_clauses.append(f"{_q(col)} = ?")
            params.append(str(val))

    if where_clauses:
        sql += " WHERE " + " AND ".join(where_clauses)

    if agg != "none" and dimensions:
        sql += " GROUP BY " + ", ".join(_q(d) for d in dimensions)

    if sort:
        order_parts = [f"{_q(s['column'])} {s['order'].upper()}" for s in sort]
        sql += " ORDER BY " + ", ".join(order_parts)

    if isinstance(limit, int) and limit > 0:
        sql += f" LIMIT {min(limit, 100000)}"

    # Embed parameters via DuckDB's parameter binding done at execute() time.
    # We return the SQL with `?` placeholders, plus params via a side-channel.
    return sql, params


def execute_plan(plan: dict[str, Any], dataset_id: str, schema_cols: list[str]) -> QueryResult:
    cleaned, warnings = _validate_columns(plan, schema_cols)
    sql, params = build_sql(cleaned, dataset_id)
    con = duckdb.connect(str(DUCKDB_PATH))
    try:
        df = con.execute(sql, params).fetch_df()
    finally:
        con.close()

    rendered_sql = _render_sql_with_params(sql, params)
    return QueryResult(
        sql=rendered_sql,
        df=df,
        plan=cleaned,
        columns_used=list(df.columns),
        warnings=warnings,
    )


def _render_sql_with_params(sql: str, params: list[Any]) -> str:
    out = []
    pi = 0
    for ch in sql:
        if ch == "?" and pi < len(params):
            v = params[pi]
            pi += 1
            if isinstance(v, (int, float)):
                out.append(str(v))
            else:
                out.append("'" + str(v).replace("'", "''") + "'")
        else:
            out.append(ch)
    return "".join(out)
