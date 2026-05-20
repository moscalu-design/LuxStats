"""Dataset metadata helpers."""

from __future__ import annotations

from typing import Any

import pandas as pd

from src.cache import get_dataset_meta
from src.catalog import catalog_entry


def latest_period(df: pd.DataFrame) -> str | None:
    if df.empty or "TIME_PERIOD" not in df.columns:
        return None
    values = df["TIME_PERIOD"].dropna().astype(str)
    if values.empty:
        return None
    return values.sort_values().iloc[-1]


def get_dataset_metadata(dataset_id: str, df: pd.DataFrame | None = None) -> dict[str, Any]:
    cache_meta = get_dataset_meta(dataset_id) or {}
    curated = catalog_entry(dataset_id) or {}
    return {
        "dataset_id": dataset_id,
        "dataset_name": curated.get("friendly_title")
        or cache_meta.get("name_en")
        or cache_meta.get("name_fr")
        or dataset_id,
        "source": "STATEC / LUSTAT",
        "latest_period": latest_period(df) if df is not None else None,
        "last_fetched": cache_meta.get("fetched_at"),
        "notes": curated.get("notes") or "Official data from STATEC / LUSTAT. Check source details for exact definitions.",
        "row_count": cache_meta.get("row_count"),
        "columns": cache_meta.get("columns", []),
    }
