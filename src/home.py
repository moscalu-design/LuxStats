"""Home page: find a Luxembourg statistic fast."""

from __future__ import annotations

import streamlit as st

from src.concept_view import render_concept
from src.concepts import Concept, get_concept, popular_concepts
from src.search import NO_RESULTS_HINT, search_concepts
from src.ui_components import page_hero, section_header


# Topic -> (icon, one-line description, page path). Only topics with real
# curated charts are shown, so every card leads somewhere useful.
TOPIC_CARDS = [
    ("🏠", "Housing", "New homes, building permits, and how big homes are.",
     "pages/2_Housing.py"),
    ("💶", "Salaries", "Pay by sector, the gender pay gap, and the minimum wage.",
     "pages/3_Salaries.py"),
    ("👥", "Population", "How many people live in Luxembourg, and how that changes.",
     "pages/4_Population.py"),
    ("🧰", "Labour Market", "Jobs and unemployment over time.",
     "pages/5_Labour_Market.py"),
    ("📈", "Prices & Inflation", "The cost of living and the inflation rate.",
     "pages/6_Prices_Inflation.py"),
    ("🔎", "All datasets", "Search every official STATEC / LUSTAT dataset.",
     "pages/7_Dataset_Explorer.py"),
]


def _open_concept(concept_id: str) -> None:
    st.session_state["open_concept"] = concept_id


def _concept_card(concept: Concept, *, key_prefix: str) -> None:
    """A compact, tappable card that opens a chart inline."""
    with st.container(border=True):
        st.markdown(
            f"<span class='lux-tag'>{concept.topic}</span>", unsafe_allow_html=True
        )
        st.markdown(f"**{concept.title}**")
        st.caption(concept.description)
        st.button(
            "Open chart →",
            key=f"{key_prefix}_{concept.id}",
            use_container_width=True,
            on_click=_open_concept,
            args=(concept.id,),
        )


def _grid(items: list[Concept], key_prefix: str, columns: int = 2) -> None:
    for row_start in range(0, len(items), columns):
        cols = st.columns(columns)
        for col, concept in zip(cols, items[row_start:row_start + columns]):
            with col:
                _concept_card(concept, key_prefix=key_prefix)


def _render_topic_grid() -> None:
    for row_start in range(0, len(TOPIC_CARDS), 3):
        cols = st.columns(3)
        for col, (icon, name, blurb, page) in zip(cols, TOPIC_CARDS[row_start:row_start + 3]):
            with col:
                with st.container(border=True):
                    st.markdown(f"### {icon} {name}")
                    st.caption(blurb)
                    st.page_link(page, label=f"Explore {name}", use_container_width=True)


def render_home() -> None:
    page_hero(
        "Luxembourg Statistics Explorer",
        "Find official Luxembourg statistics in seconds",
        "Housing, salaries, population, jobs and prices — explained in plain "
        "language, with clear charts you can explore and download. "
        "No codes, no jargon, no spreadsheets.",
    )

    query = st.text_input(
        "Search Luxembourg statistics",
        placeholder="Search housing prices, salaries, population, inflation…",
        key="home_search",
        label_visibility="collapsed",
    )

    # A chart the visitor opened from a card or a search result.
    open_id = st.session_state.get("open_concept")
    if open_id:
        concept = get_concept(open_id)
        if concept is not None:
            section_header("Your chart")
            render_concept(concept, key=f"home_{concept.id}")
            if st.button("← Back to browsing"):
                st.session_state.pop("open_concept", None)
                st.rerun()
            st.divider()

    if query.strip():
        results = search_concepts(query)
        section_header(
            f"Results for “{query.strip()}”",
            f"{len(results)} matching statistic(s)" if results else "",
        )
        if not results:
            st.info(NO_RESULTS_HINT)
        else:
            _grid(results, key_prefix="search")
        return

    section_header("Browse by topic", "Pick an area and jump straight to curated charts.")
    _render_topic_grid()

    section_header("Start with these popular charts",
                   "The statistics people look up most — one click to a clear chart.")
    _grid(popular_concepts(), key_prefix="popular")

    with st.container(border=True):
        st.markdown("#### 🔎 For advanced users")
        st.caption(
            "Want the raw data? The Dataset Explorer lets you search all 900+ "
            "official STATEC / LUSTAT datasets, inspect dimensions, and export CSVs."
        )
        st.page_link("pages/7_Dataset_Explorer.py", label="Open the Dataset Explorer")
