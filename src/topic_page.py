"""Curated topic dashboard pages.

A topic page is a friendly wrapper around the curated concept layer: a short
intro, every ready-to-chart statistic for that topic, then official-source
context tucked behind a single expander. Raw dataset IDs and SDMX terms never
appear by default — they stay inside each chart's advanced details.

Topics with no confirmed charts show an honest, calm limited state instead of
pretending coverage exists.
"""

from __future__ import annotations

import streamlit as st

from src.concept_view import render_concept
from src.concepts import concepts_for_topic
from src.data.source_catalog import get_sources_by_category
from src.data.source_visualization import (
    get_chart_ready_sources,
    get_sources_needing_mapping,
    get_visualization_status,
)
from src.ui.catalog_views import render_source_coverage_badges, render_source_records
from src.ui.nationality_explorer import render_nationality_section
from src.ui.page_header import render_page_header
from src.ui.source_visualizer import render_source_card, render_universal_source_viewer
from src.ui.theme import empty_state, section_header

# Topic -> unified-catalog category, used to surface connected official sources.
_TOPIC_CATEGORY: dict[str, str] = {
    "Housing": "Housing",
    "Salaries": "Salaries / Income",
    "Population": "Population",
    "Labour Market": "Labour Market",
    "Prices & Inflation": "Prices / Inflation",
    "Economy": "Economy / National Accounts",
    "Tourism": "Tourism",
}

_TOPIC_PAGE_ID = {
    "Housing": "housing",
    "Salaries": "salaries",
    "Population": "population",
    "Labour Market": "labour",
    "Prices & Inflation": "prices",
    "Economy": "economy",
    "Tourism": "tourism",
    "AI Adoption": "ai",
}

# Cross-topic navigation shown at the foot of every topic page.
_NAV: list[tuple[str, str]] = [
    ("Housing", "pages/6_Housing.py"),
    ("Salaries & income", "pages/7_Salaries.py"),
    ("Population", "pages/8_Population.py"),
    ("Labour market", "pages/9_Labour_Market.py"),
    ("Prices & inflation", "pages/10_Prices_Inflation.py"),
    ("Economy", "pages/14_Economy.py"),
    ("Tourism", "pages/15_Tourism.py"),
    ("AI adoption", "pages/16_AI.py"),
]

# Topic -> page path, for the "you are here" check in the more-topics footer.
_TOPIC_PAGE = {
    "Housing": "pages/6_Housing.py",
    "Salaries": "pages/7_Salaries.py",
    "Population": "pages/8_Population.py",
    "Labour Market": "pages/9_Labour_Market.py",
    "Prices & Inflation": "pages/10_Prices_Inflation.py",
    "Economy": "pages/14_Economy.py",
    "Tourism": "pages/15_Tourism.py",
    "AI Adoption": "pages/16_AI.py",
}


def render_topic_page(topic: str) -> None:
    """Render a friendly, curated dashboard for one portal topic."""
    page_id = _TOPIC_PAGE_ID.get(topic)
    if page_id:
        render_page_header(page_id, eyebrow="Topic")
    else:
        st.title(topic)

    concepts = concepts_for_topic(topic)
    category = _TOPIC_CATEGORY.get(topic)

    if concepts:
        if len(concepts) > 1:
            section_header(
                "Charts in this topic",
                "Each card is a ready-made chart — explore it, read what it "
                "means, and download the data.",
            )
        for concept in concepts:
            render_concept(concept, key=f"topic_{concept.id}")
        if topic == "Population":
            render_nationality_section()
    else:
        section_header("Charts in this topic")
        empty_state(
            "Confirmed charts are still being mapped",
            "No statistic for this topic has a confirmed chart yet. The official "
            "sources are cataloged below — LuxStats only charts them once the "
            "mapping is verified, so nothing here is guessed.",
        )

    _render_sources_section(topic, category)
    _render_selected_topic_source(topic)
    _render_go_deeper()
    _render_more_topics(topic)


def _render_sources_section(topic: str, category: str | None) -> None:
    """One consolidated, collapsed section for official-source context."""
    if not category:
        return
    sources = get_sources_by_category(category)
    chart_ready = [r for r in get_chart_ready_sources(category) if r.get("mapped_metric_id")]
    needs_mapping = get_sources_needing_mapping(category)
    if not sources and not chart_ready and not needs_mapping:
        return

    section_header("Official sources behind this topic")
    with st.expander(f"Source coverage and readiness ({len(sources)} cataloged)",
                     expanded=False):
        render_source_coverage_badges(category, label=f"{topic} coverage")

        if chart_ready:
            st.caption("**More chart-ready sources** — already safe to visualize.")
            for row in chart_ready[:4]:
                if render_source_card(row, row, key=f"topic_ready_{row['source_id']}"):
                    st.session_state[f"topic_selected_source_{topic}"] = row["source_id"]
                    st.rerun()

        if needs_mapping:
            st.caption("**Sources not yet mapped** — official and relevant, but "
                       "they need confirmed columns or sheet mapping before charting.")
            for row in needs_mapping[:5]:
                if render_source_card(row, row, key=f"topic_needs_{row['source_id']}"):
                    st.session_state[f"topic_selected_source_{topic}"] = row["source_id"]
                    st.rerun()

        if sources:
            st.caption("**All cataloged sources for this topic**")
            render_source_records(sources, key_prefix=f"topicsrc_{topic}", limit=6)


def _render_selected_topic_source(topic: str) -> None:
    source_id = st.session_state.get(f"topic_selected_source_{topic}")
    if not source_id:
        return
    readiness = get_visualization_status(str(source_id))
    if not readiness:
        return
    section_header("Selected source", "The safest available view for the source you opened.")
    render_universal_source_viewer(
        readiness,
        readiness,
        key_prefix=f"topic_selected_{source_id}",
    )


def _render_go_deeper() -> None:
    """Point users at the comparison and chart-builder tools."""
    section_header("Go deeper")
    left, right = st.columns(2)
    with left:
        st.page_link("pages/4_Compare.py", label="Compare places, sectors or groups",
                     use_container_width=True)
    with right:
        st.page_link("pages/2_Build_a_Chart.py", label="Build your own chart",
                     use_container_width=True)


def _render_more_topics(current: str) -> None:
    """Compact links to the other topic pages, so users never feel stuck."""
    current_page = _TOPIC_PAGE.get(current)
    others = [(label, page) for label, page in _NAV if page != current_page]
    section_header("Explore another topic")
    for start in range(0, len(others), 3):
        cols = st.columns(3)
        for col, (label, page) in zip(cols, others[start:start + 3]):
            with col:
                st.page_link(page, label=label, use_container_width=True)
