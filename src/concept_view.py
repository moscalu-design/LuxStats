"""Turn a curated Concept into a finished, friendly chart block.

This is the single reusable component behind every chart in the portal:
the home page, the topic dashboards, and search results all call
``render_concept`` so the experience stays consistent.
"""

from __future__ import annotations

import re

import pandas as pd
import streamlit as st

from src.charts import line_chart, ranked_bar_chart, style_value_axis
from src.concepts import Concept
from src.data_access import get_dataset
from src.formatting import format_delta, format_value
from src.metadata import get_dataset_metadata
from src.ui.source_badges import render_freshness_badge, render_source_expander
from src.ui.time_controls import apply_time_filter, render_time_controls
from src.ui_components import download_csv

_YEAR_RE = re.compile(r"^\d{4}$")


@st.cache_data(ttl=6 * 3600, show_spinner=False)
def _load_raw(dataset_id: str, refresh_token: int = 0) -> pd.DataFrame:
    """Fetch (and cache) the raw LUSTAT dataset behind a concept."""
    return get_dataset(dataset_id, refresh=refresh_token > 0)


def _label_column(df: pd.DataFrame, dimension: str | None) -> str | None:
    """Prefer the human-readable LABEL column for a dimension when present."""
    if not dimension:
        return None
    label = f"{dimension}_LABEL"
    if label in df.columns:
        return label
    if dimension in df.columns:
        return dimension
    return None


def build_series(concept: Concept, raw: pd.DataFrame) -> pd.DataFrame:
    """Reduce a raw SDMX dataframe to a tidy Year / Series / Value frame."""
    empty = pd.DataFrame(columns=["Year", "Series", "Value"])
    if raw.empty or "OBS_VALUE" not in raw.columns or "TIME_PERIOD" not in raw.columns:
        return empty

    work = raw[raw["OBS_VALUE"].notna()].copy()

    if concept.freq:
        freq_col = _label_column(work, "FREQ")
        if freq_col:
            work = work[work[freq_col] == concept.freq]

    for dimension, value in concept.filters.items():
        col = _label_column(work, dimension)
        if col:
            work = work[work[col] == value]

    series_col = _label_column(work, concept.series_dim)
    if series_col and concept.default_series:
        work = work[work[series_col].isin(concept.default_series)]

    work["Year"] = work["TIME_PERIOD"].astype(str).str[:4]
    work = work[work["Year"].map(lambda v: bool(_YEAR_RE.match(v)))]
    if work.empty:
        return empty
    work["Year"] = work["Year"].astype(int)

    if series_col:
        tidy = work.groupby(["Year", series_col], as_index=False)["OBS_VALUE"].mean()
        tidy = tidy.rename(columns={series_col: "Series", "OBS_VALUE": "Value"})
        if concept.series_labels:
            tidy["Series"] = tidy["Series"].map(
                lambda name: concept.series_labels.get(name, name)
            )
    else:
        tidy = work.groupby("Year", as_index=False)["OBS_VALUE"].mean()
        tidy = tidy.rename(columns={"OBS_VALUE": "Value"})
        tidy["Series"] = concept.title

    tidy = tidy.sort_values(["Series", "Year"])

    if concept.transform == "yoy":
        parts = []
        for _, group in tidy.groupby("Series", sort=False):
            group = group.sort_values("Year").copy()
            group["Value"] = group["Value"].pct_change() * 100
            parts.append(group)
        tidy = pd.concat(parts, ignore_index=True).dropna(subset=["Value"])

    return tidy.sort_values(["Series", "Year"]).reset_index(drop=True)


def _latest_metric(series_frame: pd.DataFrame) -> tuple[float | None, float | None]:
    """Return (latest value, change vs previous year) for one series."""
    ordered = series_frame.sort_values("Year")
    values = ordered["Value"].tolist()
    if not values:
        return None, None
    latest = values[-1]
    delta = (latest - values[-2]) if len(values) > 1 else None
    return latest, delta


def _render_metrics(concept: Concept, tidy: pd.DataFrame) -> None:
    if concept.chart == "ranked_bar":
        latest_year = int(tidy["Year"].max())
        latest = tidy[tidy["Year"] == latest_year]
        if latest.empty:
            return
        top = latest.loc[latest["Value"].idxmax()]
        bottom = latest.loc[latest["Value"].idxmin()]
        col1, col2, col3 = st.columns(3)
        col1.metric("Highest", format_value(top["Value"], concept.value_format),
                    help=str(top["Series"]))
        col2.metric("Lowest", format_value(bottom["Value"], concept.value_format),
                    help=str(bottom["Series"]))
        col3.metric("Latest year", str(latest_year))
        return

    series_names = list(dict.fromkeys(tidy["Series"].tolist()))[:4]
    columns = st.columns(len(series_names)) if series_names else []
    for column, name in zip(columns, series_names):
        value, delta = _latest_metric(tidy[tidy["Series"] == name])
        column.metric(
            name,
            format_value(value, concept.value_format),
            delta=format_delta(delta, concept.value_format),
        )


def _render_chart(concept: Concept, tidy: pd.DataFrame) -> pd.DataFrame:
    """Draw the chart and return the dataframe that backs it (for download)."""
    if concept.chart == "ranked_bar":
        latest_year = int(tidy["Year"].max())
        latest = tidy[tidy["Year"] == latest_year].copy()
        fig = ranked_bar_chart(latest, "Series", "Value", top_n=15)
        fig.update_layout(hovermode="closest", showlegend=False)
        fig.update_xaxes(title_text="")
        fig.update_yaxes(title_text="")
        style_value_axis(fig, concept.value_format, axis="x")
        fig.update_traces(marker_color="#1f6f8b")
        st.plotly_chart(fig, use_container_width=True)
        st.caption(f"Most recent year available: {latest_year}.")
        return latest.rename(columns={"Series": "Category"})[["Category", "Value"]]

    multi = tidy["Series"].nunique() > 1
    fig = line_chart(tidy, x="Year", y="Value", color="Series" if multi else None)
    fig.update_layout(showlegend=multi)
    fig.update_xaxes(title_text="", dtick=_year_dtick(tidy))
    fig.update_yaxes(title_text="")
    style_value_axis(fig, concept.value_format, axis="y")
    st.plotly_chart(fig, use_container_width=True)
    return tidy[["Year", "Series", "Value"]]


def _year_dtick(tidy: pd.DataFrame) -> int:
    span = int(tidy["Year"].max()) - int(tidy["Year"].min())
    if span <= 12:
        return 1
    if span <= 40:
        return 5
    return 20


def render_concept(concept: Concept, *, key: str | None = None) -> None:
    """Render the full chart block for one curated concept."""
    key = key or concept.id
    container = st.container(border=True)
    with container:
        st.markdown(f"#### {concept.title}")
        st.markdown(
            f"<span class='lux-tag'>{concept.topic}</span> "
            f"<span class='lux-muted'>{concept.description}</span>",
            unsafe_allow_html=True,
        )

        try:
            with st.spinner("Loading the latest official figures…"):
                raw = _load_raw(concept.dataset_id)
        except Exception as exc:  # noqa: BLE001 - surface a friendly message
            st.warning("This statistic could not be loaded right now. Please try again later.")
            with st.expander("Advanced details"):
                st.caption(f"Dataset ID: `{concept.dataset_id}`")
                st.code(str(exc))
            return

        tidy = build_series(concept, raw)
        if tidy.empty:
            st.info("No chartable data was returned for this statistic yet.")
            with st.expander("Advanced details"):
                st.caption(f"Dataset ID: `{concept.dataset_id}` · rows fetched: {len(raw):,}")
            return

        meta = get_dataset_metadata(concept.dataset_id, raw)
        meta.update({
            "geographic_level": concept.geographic_level,
            "unit_note": concept.unit_note,
            "caveat": concept.caveat,
        })
        render_freshness_badge(meta, tidy.rename(columns={"Year": "TIME_PERIOD"}))

        selection = render_time_controls(tidy, "Year", f"{key}_{concept.id}")
        filtered_tidy = apply_time_filter(tidy, "Year", selection)
        if filtered_tidy.empty:
            st.info("No data exists for the selected period. Choose a wider range.")
            return

        _render_metrics(concept, filtered_tidy)
        chart_df = _render_chart(concept, filtered_tidy)

        if concept.explanation:
            st.markdown(
                f"<div class='lux-explain'><strong>What this means.</strong> "
                f"{concept.explanation}</div>",
                unsafe_allow_html=True,
            )

        render_source_expander(meta, raw)

        download_csv(
            chart_df,
            f"{concept.id}.csv",
            "⬇︎ Download this data (CSV)",
        )
