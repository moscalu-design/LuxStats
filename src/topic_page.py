"""Curated topic dashboard pages.

A topic page is a thin, friendly wrapper around the curated concept layer:
a plain-language intro followed by every ready-to-chart statistic for that
topic. There are no raw dataset IDs or SDMX terms here — those stay tucked
inside the "Source, units and advanced details" expander of each chart.
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
from src.ui_components import section_header

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

# Plain-language framing for each topic page: (icon, headline, intro).
TOPIC_INTRO: dict[str, tuple[str, str, str]] = {
    "Housing": (
        "🏠",
        "Housing in Luxembourg",
        "How much new housing the country builds, and how big new homes are — "
        "in plain language, straight from official figures.",
    ),
    "Salaries": (
        "💶",
        "Salaries in Luxembourg",
        "What people earn here: typical pay by sector, how women's and men's "
        "pay compare, and the legal minimum wage over time.",
    ),
    "Population": (
        "👥",
        "Luxembourg's population",
        "How many people live in Luxembourg and how that has changed, including "
        "the split between Luxembourgers and foreign residents.",
    ),
    "Labour Market": (
        "🧰",
        "Jobs & unemployment",
        "How healthy the job market is — how many people are in work, and how "
        "many are looking for a job.",
    ),
    "Prices & Inflation": (
        "📈",
        "Prices & inflation",
        "The cost of living in Luxembourg: consumer prices over time and how "
        "fast they rise each year.",
    ),
    "Economy": (
        "🏦",
        "Luxembourg's economy",
        "GDP, short-term indicators, business activity and other economic "
        "signals. Chart-ready views are added only when the official source "
        "is mapped safely.",
    ),
    "Tourism": (
        "",
        "Tourism",
        "Official Luxembourg tourism statistics, including accommodation arrivals "
        "and related short-term indicators.",
    ),
}

_FALLBACK_INTRO = ("📊", "Statistics", "Explore official Luxembourg statistics for this topic.")

_TOPIC_PAGE_ID = {
    "Housing": "housing",
    "Salaries": "salaries",
    "Population": "population",
    "Labour Market": "labour",
    "Prices & Inflation": "prices",
    "Economy": "economy",
    "Tourism": "tourism",
}

# Cross-topic navigation shown at the foot of every topic page.
_NAV: list[tuple[str, str, str, str]] = [
    ("Housing", "pages/6_Housing.py", "Housing", "🏠"),
    ("Salaries", "pages/7_Salaries.py", "Salaries", "💶"),
    ("Population", "pages/8_Population.py", "Population", "👥"),
    ("Labour Market", "pages/9_Labour_Market.py", "Jobs & unemployment", "🧰"),
    ("Prices & Inflation", "pages/10_Prices_Inflation.py", "Prices & inflation", "📈"),
    ("Economy", "pages/14_Economy.py", "Economy", "🏦"),
    ("Tourism", "pages/15_Tourism.py", "Tourism", ""),
]


def render_topic_page(topic: str) -> None:
    """Render a friendly, curated dashboard for one portal topic."""
    page_id = _TOPIC_PAGE_ID.get(topic)
    if page_id:
        render_page_header(page_id, eyebrow="Topic")
    else:
        icon, headline, intro = TOPIC_INTRO.get(topic, _FALLBACK_INTRO)
        st.title(f"{icon} {headline}")
        st.caption(intro)

    concepts = concepts_for_topic(topic)
    if not concepts:
        st.info(
            "Chart-ready metrics for this topic are still being mapped. The "
            "official sources are cataloged below, but they are kept out of "
            "beginner charts until the mapping is confirmed."
        )
        category = _TOPIC_CATEGORY.get(topic)
        if category:
            render_source_coverage_badges(category, label=f"{topic} coverage")
            sources = get_sources_by_category(category)
            with st.expander("Official sources not yet mapped to charts", expanded=True):
                render_source_records(sources, key_prefix=f"unmapped_{topic}", limit=8)
        st.page_link("pages/13_Source_Library.py", label="Open the Source Library", icon="🗂️")
        return

    if len(concepts) > 1:
        section_header(
            "Charts in this section",
            "Each card is a ready-made chart — explore it, read what it means, "
            "and download the data.",
        )

    for concept in concepts:
        render_concept(concept, key=f"topic_{concept.id}")

    if topic == "Population":
        render_nationality_section()

    st.divider()
    category = _TOPIC_CATEGORY.get(topic)
    if category:
        with st.expander(f"{topic} source readiness", expanded=False):
            render_source_coverage_badges(category, label=f"{topic} coverage")
    _render_chart_ready_sources(topic)
    _render_topic_sources(topic)
    _render_selected_topic_source(topic)
    _render_go_deeper()
    _render_more_topics(topic)


def _render_chart_ready_sources(topic: str) -> None:
    category = _TOPIC_CATEGORY.get(topic)
    if not category:
        return
    ready = get_chart_ready_sources(category)
    mapped_more = [row for row in ready if row.get("mapped_metric_id")]
    if mapped_more:
        with st.expander("More chart-ready source mappings", expanded=False):
            st.caption("These official sources already have safe visualization routes in LuxStats.")
            for row in mapped_more[:4]:
                if render_source_card(row, row, key=f"topic_ready_{row['source_id']}"):
                    st.session_state[f"topic_selected_source_{topic}"] = row["source_id"]
                    st.rerun()
    needs = get_sources_needing_mapping(category)
    if needs:
        with st.expander("Sources available but not mapped yet", expanded=False):
            st.caption("These sources are official and relevant, but need confirmed columns, filters, or sheet mapping before charting.")
            for row in needs[:6]:
                if render_source_card(row, row, key=f"topic_needs_{row['source_id']}"):
                    st.session_state[f"topic_selected_source_{topic}"] = row["source_id"]
                    st.rerun()


def _render_selected_topic_source(topic: str) -> None:
    source_id = st.session_state.get(f"topic_selected_source_{topic}")
    if not source_id:
        return
    readiness = get_visualization_status(str(source_id))
    if not readiness:
        return
    section_header("Selected source", "Safest available view for the source you opened.")
    render_universal_source_viewer(
        readiness,
        readiness,
        key_prefix=f"topic_selected_{source_id}",
    )


def _render_topic_sources(topic: str) -> None:
    """Show official STATEC sources cataloged for this topic, if any."""
    category = _TOPIC_CATEGORY.get(topic)
    if not category:
        return
    sources = get_sources_by_category(category)
    if not sources:
        return
    with st.expander(f"Official sources for {topic.lower()} "
                     f"({len(sources)} cataloged)", expanded=False):
        st.caption(
            "Beyond the curated charts above, these official STATEC / LUSTAT "
            "sources cover this topic — API datasets, Excel tables and "
            "publication annexes."
        )
        render_source_records(sources, key_prefix=f"topicsrc_{topic}", limit=6)


def _render_go_deeper() -> None:
    """Point users at the comparison and chart-builder tools."""
    section_header("Go deeper")
    left, right = st.columns(2)
    with left:
        st.page_link("pages/4_Compare.py", label="Compare sectors, groups or communes",
                     use_container_width=True)
    with right:
        st.page_link("pages/2_Build_a_Chart.py", label="Build your own chart",
                     use_container_width=True)


def _render_more_topics(current: str) -> None:
    """Compact links to the other topic pages, so users never feel stuck."""
    section_header("Explore another topic")
    others = [item for item in _NAV if item[0] != current]
    cols = st.columns(len(others))
    for col, (_topic, page, label, _icon) in zip(cols, others):
        with col:
            st.page_link(page, label=label, use_container_width=True)
