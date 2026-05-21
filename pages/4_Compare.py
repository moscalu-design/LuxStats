from __future__ import annotations

import streamlit as st

from src.analysis.comparison import (
    build_commune_comparison_dataframe,
    build_comparison_dataframe,
    get_commune_comparison_metrics,
    get_commune_comparison_options,
    get_comparable_metrics,
    get_comparison_options,
    render_comparison_chart,
)
from src.concepts import get_concept
from src.metadata import get_dataset_metadata
from src.ui.explanations import render_chart_explanation
from src.ui.source_badges import render_source_expander
from src.ui_components import configure_page, download_csv, page_hero, render_sidebar, section_header

configure_page("LuxStats - Compare")
render_sidebar()

page_hero(
    "Compare",
    "Put places, sectors and trends side by side",
    "Compare communes head to head, or compare sectors and groups within one "
    "statistic. Sensible defaults are chosen for you — adjust as you like.",
)

mode = st.radio(
    "What do you want to compare?",
    ["Compare communes", "Compare sectors & groups"],
    horizontal=True,
)


def _years(df) -> tuple[int, int] | None:
    if df.empty:
        return None
    lo, hi = int(df["Year"].min()), int(df["Year"].max())
    return (lo, hi) if lo < hi else None


# --------------------------------------------------------------------------
if mode == "Compare communes":
    section_header("Step 1 — Choose a metric")
    datasets = get_commune_comparison_metrics()
    if not datasets:
        st.info("No confirmed commune-level datasets are connected yet.")
        st.stop()
    dataset = st.selectbox(
        "Commune metric", datasets, format_func=lambda d: f"{d.title} ({d.topic})",
        label_visibility="collapsed",
    )

    section_header("Step 2 — Choose communes to compare")
    communes = st.multiselect(
        "Communes",
        get_commune_comparison_options(),
        default=["Luxembourg", "Hesperange", "Esch-sur-Alzette"],
        label_visibility="collapsed",
    )
    if not communes:
        st.info("Pick at least one commune to build a comparison.")
        st.stop()

    with st.spinner("Loading official commune figures…"):
        df = build_commune_comparison_dataframe(dataset.dataset_id, communes)

    if df.empty:
        st.info(
            "This dataset does not have comparable values for the chosen "
            "communes. Try other communes, or another metric."
        )
        st.stop()

    years = _years(df)
    if years:
        section_header("Step 3 — Choose a time period")
        lo, hi = st.slider("Years", years[0], years[1], years,
                           label_visibility="collapsed")
        df = df[(df["Year"] >= lo) & (df["Year"] <= hi)]

    section_header(dataset.title)
    fig = render_comparison_chart(df, value_format="number", chart="line",
                                  title=None)
    if fig is not None:
        st.plotly_chart(fig, use_container_width=True)
    st.caption(f"Comparing {len(communes)} commune(s) · Source: STATEC / LUSTAT.")
    meta = get_dataset_metadata(dataset.dataset_id)
    meta["geographic_level"] = "commune"
    meta["notes"] = dataset.notes
    render_source_expander(meta, df)
    download_csv(df, f"compare_{dataset.dataset_id}.csv",
                 "⬇︎ Download this comparison (CSV)")

# --------------------------------------------------------------------------
else:
    section_header("Step 1 — Choose a metric")
    metrics = get_comparable_metrics()
    if not metrics:
        st.info("No comparable metrics are available yet.")
        st.stop()
    concept = st.selectbox(
        "Metric", metrics, format_func=lambda c: f"{c.title} ({c.topic})",
        label_visibility="collapsed",
    )

    section_header("Step 2 — Choose what to compare")
    with st.spinner("Loading available options…"):
        options = get_comparison_options(concept.id)
    if not options:
        st.info(
            "This metric does not expose comparable groups in the connected "
            "data. Try a different metric."
        )
        st.stop()
    default = [s for s in concept.default_series if s in options] or options[:2]
    items = st.multiselect("Items", options, default=default,
                           label_visibility="collapsed")
    if not items:
        st.info("Pick at least one item to compare.")
        st.stop()

    with st.spinner("Building your comparison…"):
        df = build_comparison_dataframe(concept.id, items)
    if df.empty:
        st.info("No comparable data was returned for this selection.")
        st.stop()

    years = _years(df)
    if years:
        section_header("Step 3 — Choose a time period")
        lo, hi = st.slider("Years", years[0], years[1], years,
                           label_visibility="collapsed")
        df = df[(df["Year"] >= lo) & (df["Year"] <= hi)]

    chart_type = st.radio("Chart type", ["Line", "Bar"], horizontal=True)
    section_header(concept.title)
    fig = render_comparison_chart(
        df, value_format=concept.value_format,
        chart="bar" if chart_type == "Bar" else "line",
    )
    if fig is not None:
        st.plotly_chart(fig, use_container_width=True)
    render_chart_explanation(concept)
    meta = get_dataset_metadata(concept.dataset_id)
    meta.update({
        "geographic_level": concept.geographic_level,
        "unit_note": concept.unit_note,
        "caveat": concept.caveat,
    })
    render_source_expander(meta, df)
    download_csv(df, f"compare_{concept.id}.csv",
                 "⬇︎ Download this comparison (CSV)")
