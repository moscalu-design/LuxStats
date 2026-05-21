"""Guided 'Build a Chart' tool.

Lets a visitor create a chart from official statistics in a few clicks, with
no dataset codes in sight. It is driven entirely by the curated concept
catalog and reuses the comparison engine for series selection.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from src.analysis.comparison import (
    build_comparison_dataframe,
    get_comparison_options,
    render_comparison_chart,
)
from src.charts import line_chart, ranked_bar_chart, style_value_axis
from src.concept_view import build_series
from src.concepts import Concept, concepts_for_topic, get_concept, topics_with_concepts
from src.data.source_visualization import get_chart_ready_sources, get_sources_needing_mapping
from src.data_access import get_dataset
from src.formatting import format_value
from src.metadata import get_dataset_metadata
from src.ui.explanations import render_chart_explanation
from src.ui.source_badges import render_source_expander
from src.ui.time_controls import apply_time_filter, render_time_controls
from src.ui_components import download_csv

# Topics offered in the builder, in product order. Only topics with curated
# concepts appear, so every choice leads to a real chart.
_TOPIC_ORDER = [
    "Housing", "Salaries", "Population", "Labour Market", "Prices & Inflation",
]


def get_topics() -> list[str]:
    """Topics that have at least one curated, chartable metric."""
    available = set(topics_with_concepts())
    ordered = [t for t in _TOPIC_ORDER if t in available]
    return ordered + sorted(available.difference(ordered))


def get_metrics_for_topic(topic: str) -> list[Concept]:
    """Curated metrics available for a topic."""
    return concepts_for_topic(topic)


def get_chart_ready_source_options(topic: str | None = None) -> list[dict]:
    """Chart-ready visualization-index entries that can be safely surfaced."""
    return get_chart_ready_sources(topic)


def get_available_filters(metric_id: str) -> dict[str, object]:
    """Describe the filters a metric supports: series options and year range."""
    concept = get_concept(metric_id)
    if concept is None:
        return {"series": [], "years": None}
    series = get_comparison_options(metric_id) if concept.series_dim else []
    years = None
    try:
        tidy = build_series(concept, get_dataset(concept.dataset_id))
        if not tidy.empty:
            years = (int(tidy["Year"].min()), int(tidy["Year"].max()))
    except Exception:  # noqa: BLE001
        years = None
    return {"series": series, "years": years}


def build_chart_from_selection(selection: dict) -> pd.DataFrame:
    """Build the tidy dataframe behind a builder selection.

    ``selection`` keys: ``metric_id``, ``series`` (list), ``time_range`` (tuple).
    Returns an empty frame when the selection cannot be charted.
    """
    metric_id = selection.get("metric_id")
    concept = get_concept(metric_id) if metric_id else None
    if concept is None:
        return pd.DataFrame(columns=["Year", "Series", "Value"])
    series = selection.get("series") or []
    time_range = selection.get("time_range")
    if concept.series_dim and series:
        return build_comparison_dataframe(metric_id, series, time_range)
    try:
        tidy = build_series(concept, get_dataset(concept.dataset_id))
    except Exception:  # noqa: BLE001
        return pd.DataFrame(columns=["Year", "Series", "Value"])
    if time_range and not tidy.empty:
        low, high = time_range
        tidy = tidy[(tidy["Year"] >= low) & (tidy["Year"] <= high)]
    return tidy.reset_index(drop=True)


def _chart_choices(concept: Concept) -> list[str]:
    if concept.chart == "ranked_bar":
        return ["Ranking", "Bar", "Table"]
    return ["Line", "Bar", "Table"]


def render_chart_builder() -> None:
    """Render the full guided chart-builder flow."""
    topics = get_topics()
    if not topics:
        st.info("No curated metrics are available to build a chart from yet.")
        return

    mode = st.radio(
        "Mode",
        ["Beginner: curated metrics", "Advanced: all chart-ready sources"],
        horizontal=True,
    )

    st.markdown("**Step 1 — Choose a topic**")
    topic = st.selectbox("Topic", topics, label_visibility="collapsed")

    if mode.startswith("Advanced"):
        ready_sources = get_chart_ready_source_options(topic)
        mapped_sources = [row for row in ready_sources if row.get("mapped_metric_id")]
        pending_sources = get_sources_needing_mapping(topic)
        if mapped_sources:
            source = st.selectbox(
                "Chart-ready source",
                mapped_sources,
                format_func=lambda row: row.get("title", "Official source"),
            )
            metric_id = source.get("mapped_metric_id")
            metric = get_concept(metric_id) if metric_id else None
            if metric is None:
                st.info("This chart-ready source opens in another page, such as Commune Portal or Compare.")
                return
        else:
            st.info("No chart-ready source mappings exist for this topic yet.")
            metric = None
        if pending_sources:
            with st.expander("Available sources that still need mapping", expanded=False):
                for row in pending_sources[:8]:
                    st.write(f"- **{row['title']}** — {row['recommended_action']}")
        if metric is None:
            return
    else:
        metrics = get_metrics_for_topic(topic)
        if not metrics:
            st.info("This topic is ready in the interface, but no supported "
                    "dataset has been connected yet.")
            return

        st.markdown("**Step 2 — Choose a metric**")
        metric = st.selectbox(
            "Metric", metrics, format_func=lambda c: c.title, label_visibility="collapsed"
        )

    filters = get_available_filters(metric.id)
    series_options = filters["series"]
    selected_series: list[str] = []
    if series_options:
        st.markdown("**Step 3 — Choose what to compare** (optional)")
        default = [s for s in metric.default_series if s in series_options]
        selected_series = st.multiselect(
            "Items to show", series_options, default=default,
            label_visibility="collapsed",
        )

    st.markdown("**Step 4 — Choose a chart type**")
    chart_type = st.radio(
        "Chart type", _chart_choices(metric), horizontal=True,
        label_visibility="collapsed",
    )

    selection = {
        "metric_id": metric.id,
        "series": selected_series,
        "time_range": None,
    }
    with st.spinner("Building your chart from official figures…"):
        df = build_chart_from_selection(selection)

    st.divider()
    if df.empty:
        st.info("No chartable data was returned for this selection. Try a wider "
                "time period or different items to compare.")
        return

    st.markdown("**Time period**")
    selection_control = render_time_controls(df, "Year", f"builder_{metric.id}")
    df = apply_time_filter(df, "Year", selection_control)
    if df.empty:
        st.info("No data exists for the selected period. Choose a wider range.")
        return

    st.markdown(f"#### {metric.title}")
    _render_built_chart(df, metric, chart_type)

    render_chart_explanation(metric)

    try:
        meta = get_dataset_metadata(metric.dataset_id, get_dataset(metric.dataset_id))
    except Exception:  # noqa: BLE001
        meta = {"dataset_id": metric.dataset_id, "source": "STATEC / LUSTAT"}
    meta.update({
        "geographic_level": metric.geographic_level,
        "unit_note": metric.unit_note,
        "caveat": metric.caveat,
    })
    render_source_expander(meta, df)
    download_csv(df, f"{metric.id}_custom.csv", "⬇︎ Download this data (CSV)")


def _render_built_chart(df: pd.DataFrame, concept: Concept, chart_type: str) -> None:
    if chart_type == "Table":
        display = df.copy()
        display["Value"] = display["Value"].map(
            lambda v: format_value(v, concept.value_format)
        )
        st.dataframe(display, use_container_width=True, hide_index=True)
        return

    multi = df["Series"].nunique() > 1
    if chart_type in ("Ranking", "Bar"):
        latest_year = int(df["Year"].max())
        latest = df[df["Year"] == latest_year]
        if chart_type == "Ranking":
            fig = ranked_bar_chart(latest, "Series", "Value", top_n=20)
            style_value_axis(fig, concept.value_format, axis="x")
        else:
            fig = render_comparison_chart(latest, value_format=concept.value_format,
                                          chart="bar")
        fig.update_layout(showlegend=False)
        fig.update_xaxes(title_text="")
        fig.update_yaxes(title_text="")
        st.plotly_chart(fig, use_container_width=True)
        st.caption(f"Most recent year available: {latest_year}.")
        return

    fig = line_chart(df, x="Year", y="Value", color="Series" if multi else None)
    fig.update_layout(showlegend=multi)
    fig.update_xaxes(title_text="")
    fig.update_yaxes(title_text="")
    style_value_axis(fig, concept.value_format, axis="y")
    st.plotly_chart(fig, use_container_width=True)
