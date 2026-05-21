"""Reusable comparison engine.

Two kinds of comparison are supported, both deterministic and driven by the
curated catalog:

* **Metric comparison** — compare series within one curated concept (for
  example several economic sectors, or women vs men).
* **Commune comparison** — compare the same commune-level dataset across
  several communes (for example Luxembourg City vs Hesperange vs Esch).

Every function handles missing or empty data gracefully and never raises for
ordinary "no data" situations.
"""

from __future__ import annotations

from dataclasses import replace

import pandas as pd
import plotly.graph_objects as go

from src.catalog import STARTER_CATALOG, is_placeholder_dataset_id
from src.charts import bar_chart, line_chart, style_value_axis
from src.concept_view import build_series
from src.concepts import Concept, all_concepts, get_concept
from src.data.commune_portal import CommuneDataset, filter_dataset_for_commune
from src.data.communes import list_communes
from src.data_access import get_dataset
from src.transforms import time_series

_EMPTY = pd.DataFrame(columns=["Year", "Series", "Value"])


# --------------------------------------------------------------------------
# Metric comparison (series within one concept)
# --------------------------------------------------------------------------

def get_comparable_metrics() -> list[Concept]:
    """Concepts that expose a dimension worth comparing (a ``series_dim``)."""
    return [c for c in all_concepts() if c.series_dim]


def _series_label_column(df: pd.DataFrame, dimension: str | None) -> str | None:
    if not dimension:
        return None
    if f"{dimension}_LABEL" in df.columns:
        return f"{dimension}_LABEL"
    if dimension in df.columns:
        return dimension
    return None


def get_comparison_options(metric_id: str) -> list[str]:
    """Return the items (series values) available to compare for a metric.

    Returns an empty list when the metric is unknown, has no comparable
    dimension, or the dataset cannot be loaded.
    """
    concept = get_concept(metric_id)
    if concept is None or not concept.series_dim:
        return []
    try:
        raw = get_dataset(concept.dataset_id)
    except Exception:  # noqa: BLE001 - missing data must not crash callers
        return []
    col = _series_label_column(raw, concept.series_dim)
    if not col:
        return []
    values = sorted(raw[col].dropna().astype(str).unique().tolist())
    return [v for v in values if v and v != "_T"]


def build_comparison_dataframe(
    metric_id: str,
    selected_items: list[str],
    time_range: tuple[int, int] | None = None,
) -> pd.DataFrame:
    """Build a tidy Year/Series/Value frame for the selected items.

    Empty input or unavailable data yields an empty (correctly-typed) frame.
    """
    concept = get_concept(metric_id)
    if concept is None or not selected_items:
        return _EMPTY.copy()
    try:
        raw = get_dataset(concept.dataset_id)
    except Exception:  # noqa: BLE001
        return _EMPTY.copy()
    # Reuse the tested concept reducer, but with the user's chosen series.
    variant = replace(concept, default_series=list(selected_items), transform=None)
    tidy = build_series(variant, raw)
    if tidy.empty:
        return _EMPTY.copy()
    if time_range:
        low, high = time_range
        tidy = tidy[(tidy["Year"] >= low) & (tidy["Year"] <= high)]
    return tidy.reset_index(drop=True)


# --------------------------------------------------------------------------
# Commune comparison (one dataset, several communes)
# --------------------------------------------------------------------------

def get_commune_comparison_metrics() -> list[CommuneDataset]:
    """Confirmed commune-level catalog datasets that can be compared."""
    out: list[CommuneDataset] = []
    for entry in STARTER_CATALOG:
        if is_placeholder_dataset_id(entry.dataset_id):
            continue
        if not (entry.commune_portal or entry.geographic_level == "commune"):
            continue
        out.append(
            CommuneDataset(
                dataset_id=entry.dataset_id,
                title=entry.friendly_title,
                topic=entry.theme,
                description=entry.description,
                geography_column=entry.geography_column or entry.commune_name_column,
                value_column=entry.value_column,
                time_column=entry.time_column,
                source_status=entry.status,
                notes=entry.notes,
                default_filters=dict(entry.default_filters),
            )
        )
    return out


def get_commune_comparison_options() -> list[str]:
    """All commune names available to compare."""
    return list_communes()


def _apply_filters(df: pd.DataFrame, dataset: CommuneDataset) -> pd.DataFrame:
    work = df.copy()
    for column, expected in (dataset.default_filters or {}).items():
        if column in work.columns:
            work = work[work[column].astype(str) == str(expected)]
    return work


def build_commune_comparison_dataframe(
    dataset_id: str,
    communes: list[str],
    time_range: tuple[int, int] | None = None,
) -> pd.DataFrame:
    """Build a tidy Year/Series(commune)/Value frame across communes."""
    dataset = next(
        (d for d in get_commune_comparison_metrics() if d.dataset_id == dataset_id),
        None,
    )
    if dataset is None or not communes:
        return _EMPTY.copy()
    try:
        raw = _apply_filters(get_dataset(dataset.dataset_id), dataset)
    except Exception:  # noqa: BLE001
        return _EMPTY.copy()

    frames: list[pd.DataFrame] = []
    for commune in communes:
        rows = filter_dataset_for_commune(raw, commune, dataset)
        series = time_series(rows, dataset.value_column, dataset.time_column)
        if series.empty:
            continue
        series = series.rename(
            columns={dataset.time_column: "Year", dataset.value_column: "Value"}
        )
        series["Year"] = (
            series["Year"].astype(str).str[:4]
        )
        series = series[series["Year"].str.fullmatch(r"\d{4}")]
        if series.empty:
            continue
        series["Year"] = series["Year"].astype(int)
        series["Series"] = commune
        frames.append(series[["Year", "Series", "Value"]])

    if not frames:
        return _EMPTY.copy()
    tidy = pd.concat(frames, ignore_index=True)
    if time_range:
        low, high = time_range
        tidy = tidy[(tidy["Year"] >= low) & (tidy["Year"] <= high)]
    return tidy.sort_values(["Series", "Year"]).reset_index(drop=True)


# --------------------------------------------------------------------------
# Chart
# --------------------------------------------------------------------------

def render_comparison_chart(
    df: pd.DataFrame,
    *,
    value_format: str = "number",
    chart: str = "line",
    title: str | None = None,
) -> go.Figure | None:
    """Build a Plotly figure for a comparison frame, or None when empty."""
    if df is None or df.empty:
        return None
    if chart == "bar":
        latest_year = int(df["Year"].max())
        latest = df[df["Year"] == latest_year]
        fig = bar_chart(latest, x="Series", y="Value", title=title)
        fig.update_layout(showlegend=False)
        style_value_axis(fig, value_format, axis="y")
    else:
        fig = line_chart(df, x="Year", y="Value", color="Series", title=title)
        style_value_axis(fig, value_format, axis="y")
    fig.update_xaxes(title_text="")
    fig.update_yaxes(title_text="")
    return fig
