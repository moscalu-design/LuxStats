"""Detect recent, meaningful changes in official statistics.

Every figure here is calculated from real cached data. When the data does not
support a calculation the functions return ``None`` or an empty result — they
never invent an insight.
"""

from __future__ import annotations

from typing import Any

import pandas as pd

from src.cache import get_dataset_meta, is_dataset_cached, load_dataset
from src.concept_view import build_series
from src.concepts import Concept, all_concepts, get_concept
from src.data.commune_portal import CommuneDataset
from src.data.communes import list_communes
from src.transforms import normalize_columns


def _latest_period(df: pd.DataFrame) -> str | None:
    if df.empty or "TIME_PERIOD" not in df.columns:
        return None
    values = df["TIME_PERIOD"].dropna().astype(str)
    return values.sort_values().iloc[-1] if not values.empty else None


def get_recently_updated_metrics() -> list[dict[str, Any]]:
    """List curated metrics with their cache freshness, newest cache first.

    Uses only local cache metadata, so it is fast and never hits the network.
    """
    rows: list[dict[str, Any]] = []
    for concept in all_concepts():
        cached = is_dataset_cached(concept.dataset_id)
        meta = get_dataset_meta(concept.dataset_id) if cached else None
        latest = None
        if cached:
            try:
                latest = _latest_period(normalize_columns(load_dataset(concept.dataset_id)))
            except Exception:  # noqa: BLE001
                latest = None
        rows.append(
            {
                "metric_id": concept.id,
                "title": concept.title,
                "topic": concept.topic,
                "dataset_id": concept.dataset_id,
                "cached": cached,
                "last_fetched": (meta or {}).get("fetched_at"),
                "latest_period": latest,
            }
        )
    rows.sort(key=lambda r: (r["last_fetched"] is not None, str(r["last_fetched"] or "")),
              reverse=True)
    return rows


def calculate_latest_change(metric_id: str) -> dict[str, Any] | None:
    """Latest period vs the previous one for a curated metric.

    Returns ``None`` when the metric is unknown or has fewer than two periods.
    """
    concept = get_concept(metric_id)
    if concept is None:
        return None
    try:
        from src.data_access import get_dataset

        tidy = build_series(concept, get_dataset(concept.dataset_id))
    except Exception:  # noqa: BLE001
        return None
    if tidy.empty:
        return None
    # Collapse to one value per year (mean across series) for a headline move.
    yearly = tidy.groupby("Year", as_index=False)["Value"].mean().sort_values("Year")
    if len(yearly) < 2:
        return None
    latest = float(yearly["Value"].iloc[-1])
    previous = float(yearly["Value"].iloc[-2])
    delta = latest - previous
    return {
        "metric_id": metric_id,
        "title": concept.title,
        "value_format": concept.value_format,
        "latest_period": int(yearly["Year"].iloc[-1]),
        "previous_period": int(yearly["Year"].iloc[-2]),
        "latest_value": latest,
        "previous_value": previous,
        "delta": delta,
        "pct_change": (delta / previous * 100) if previous else None,
    }


def _commune_changes(
    df: pd.DataFrame,
    group_col: str,
    value_col: str,
    time_col: str,
) -> pd.DataFrame:
    """Per-commune change between the two most recent periods."""
    empty = pd.DataFrame(columns=[group_col, "previous", "latest", "change", "pct_change"])
    if df.empty or any(c not in df.columns for c in (group_col, value_col, time_col)):
        return empty
    work = df[[group_col, value_col, time_col]].copy()
    work[value_col] = pd.to_numeric(work[value_col], errors="coerce")
    work = work.dropna(subset=[value_col])
    known = {n.casefold() for n in list_communes()}
    work = work[work[group_col].astype(str).str.casefold().isin(known)]
    if work.empty:
        return empty
    periods = sorted(work[time_col].astype(str).unique())
    if len(periods) < 2:
        return empty
    latest_p, prev_p = periods[-1], periods[-2]
    latest = work[work[time_col].astype(str) == latest_p].groupby(group_col)[value_col].mean()
    prev = work[work[time_col].astype(str) == prev_p].groupby(group_col)[value_col].mean()
    merged = pd.concat({"latest": latest, "previous": prev}, axis=1).dropna()
    if merged.empty:
        return empty
    merged["change"] = merged["latest"] - merged["previous"]
    merged["pct_change"] = merged["change"] / merged["previous"].replace(0, pd.NA) * 100
    return merged.reset_index().rename(columns={"index": group_col})


def calculate_top_increases(
    df: pd.DataFrame,
    group_col: str,
    value_col: str = "OBS_VALUE",
    time_col: str = "TIME_PERIOD",
    top_n: int = 10,
) -> pd.DataFrame:
    """Communes with the biggest recent percentage increase."""
    changes = _commune_changes(df, group_col, value_col, time_col)
    if changes.empty:
        return changes
    return changes.sort_values("pct_change", ascending=False).head(top_n).reset_index(drop=True)


def calculate_top_decreases(
    df: pd.DataFrame,
    group_col: str,
    value_col: str = "OBS_VALUE",
    time_col: str = "TIME_PERIOD",
    top_n: int = 10,
) -> pd.DataFrame:
    """Communes with the biggest recent percentage decrease."""
    changes = _commune_changes(df, group_col, value_col, time_col)
    if changes.empty:
        return changes
    return changes.sort_values("pct_change", ascending=True).head(top_n).reset_index(drop=True)
