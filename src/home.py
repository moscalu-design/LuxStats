"""Home page: find a Luxembourg statistic fast."""

from __future__ import annotations

import streamlit as st

from src.concept_view import render_concept
from src.concepts import Concept, get_concept, popular_concepts
from src.search import NO_RESULTS_HINT, search_communes, search_concepts
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
    ("📍", "Commune Portal", "Choose one commune and see local statistics in one place.",
     "pages/9_Commune_Portal.py"),
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


def _commune_card(result: dict[str, str], key_prefix: str) -> None:
    with st.container(border=True):
        st.markdown("<span class='lux-tag'>Commune</span>", unsafe_allow_html=True)
        st.markdown(f"**{result['title']}**")
        st.caption(result["description"])
        if st.button(
            "Open commune profile →",
            key=f"{key_prefix}_{result['commune']}_{result['tab']}",
            use_container_width=True,
        ):
            st.session_state["selected_commune"] = result["commune"]
            st.switch_page("pages/9_Commune_Portal.py")


def _commune_grid(results: list[dict[str, str]], key_prefix: str) -> None:
    cols = st.columns(min(2, len(results))) if results else []
    for col, result in zip(cols, results):
        with col:
            _commune_card(result, key_prefix)


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
        commune_results = search_communes(query)
        total = len(results) + len(commune_results)
        section_header(
            f"Results for “{query.strip()}”",
            f"{total} matching result(s)" if total else "",
        )
        if not results and not commune_results:
            st.info(NO_RESULTS_HINT)
        else:
            if commune_results:
                _commune_grid(commune_results, key_prefix="commune_search")
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
