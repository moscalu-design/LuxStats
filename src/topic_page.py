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
from src.ui_components import page_hero, section_header

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
}

_FALLBACK_INTRO = ("📊", "Statistics", "Explore official Luxembourg statistics for this topic.")

# Cross-topic navigation shown at the foot of every topic page.
_NAV: list[tuple[str, str, str, str]] = [
    ("Housing", "pages/2_Housing.py", "Housing", "🏠"),
    ("Salaries", "pages/3_Salaries.py", "Salaries", "💶"),
    ("Population", "pages/4_Population.py", "Population", "👥"),
    ("Labour Market", "pages/5_Labour_Market.py", "Jobs & unemployment", "🧰"),
    ("Prices & Inflation", "pages/6_Prices_Inflation.py", "Prices & inflation", "📈"),
]


def render_topic_page(topic: str) -> None:
    """Render a friendly, curated dashboard for one portal topic."""
    icon, headline, intro = TOPIC_INTRO.get(topic, _FALLBACK_INTRO)
    page_hero(f"{icon} Luxembourg statistics", headline, intro)

    concepts = concepts_for_topic(topic)
    if not concepts:
        st.info(
            "Curated charts for this topic are still being prepared. In the "
            "meantime you can search every official dataset in the Dataset Explorer."
        )
        st.page_link("pages/7_Dataset_Explorer.py", label="Open the Dataset Explorer", icon="🔎")
        return

    if len(concepts) > 1:
        section_header(
            "Charts in this section",
            "Each card is a ready-made chart — explore it, read what it means, "
            "and download the data.",
        )

    for concept in concepts:
        render_concept(concept, key=f"topic_{concept.id}")

    st.divider()
    _render_more_topics(topic)


def _render_more_topics(current: str) -> None:
    """Compact links to the other topic pages, so users never feel stuck."""
    section_header("Explore another topic")
    others = [item for item in _NAV if item[0] != current]
    cols = st.columns(len(others))
    for col, (_topic, page, label, icon) in zip(cols, others):
        with col:
            st.page_link(page, label=label, icon=icon, use_container_width=True)
