"""Home page: a guided front door to Luxembourg statistics."""

from __future__ import annotations

import streamlit as st

from src.concept_view import render_concept
from src.concepts import get_concept
from src.data.analysis_cards import commune_cards, comparison_cards, popular_cards
from src.search import NO_RESULTS_HINT, search_communes, search_concepts
from src.ui.cards import render_analysis_grid, render_metric_grid
from src.ui_components import page_hero, section_header

# Topic -> (icon, name, one-line description, page path).
TOPIC_CARDS = [
    ("🏠", "Housing", "New homes, building permits, and how big homes are.",
     "pages/6_Housing.py"),
    ("💶", "Salaries", "Pay by sector, the gender pay gap, and the minimum wage.",
     "pages/7_Salaries.py"),
    ("👥", "Population", "How many people live in Luxembourg, and how that changes.",
     "pages/8_Population.py"),
    ("🧰", "Labour Market", "Jobs and unemployment over time.",
     "pages/9_Labour_Market.py"),
    ("📈", "Prices & Inflation", "The cost of living and the inflation rate.",
     "pages/10_Prices_Inflation.py"),
    ("📍", "Commune Portal", "Choose one commune and see local statistics in one place.",
     "pages/3_Commune_Portal.py"),
]


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
            st.switch_page("pages/3_Commune_Portal.py")


def _render_topic_grid() -> None:
    for row_start in range(0, len(TOPIC_CARDS), 3):
        cols = st.columns(3)
        for col, (icon, name, blurb, page) in zip(cols, TOPIC_CARDS[row_start:row_start + 3]):
            with col:
                with st.container(border=True):
                    st.markdown(f"### {icon} {name}")
                    st.caption(blurb)
                    st.page_link(page, label=f"Explore {name}", use_container_width=True)


def _render_search_results(query: str) -> None:
    results = search_concepts(query)
    commune_results = search_communes(query)
    total = len(results) + len(commune_results)
    section_header(
        f"Results for “{query.strip()}”",
        f"{total} matching result(s)" if total else "",
    )
    if not results and not commune_results:
        st.info(NO_RESULTS_HINT)
        return
    if commune_results:
        for result in commune_results:
            _commune_card(result, key_prefix="commune_search")
    if results:
        render_metric_grid(results, key_prefix="search", columns=2)


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

    # A chart opened from a card or a search result.
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
        _render_search_results(query)
        return

    section_header("Popular statistics",
                   "The questions people ask most — one click to a clear answer.")
    render_analysis_grid(popular_cards(), key_prefix="popular", columns=3)

    section_header("Common comparisons",
                   "Put places, sectors or trends side by side.")
    render_analysis_grid(comparison_cards(), key_prefix="compare", columns=3)

    section_header("Browse by topic", "Pick an area and jump straight to curated charts.")
    _render_topic_grid()

    section_header("Explore by commune",
                   "Local statistics for any of Luxembourg's 100 communes.")
    render_analysis_grid(commune_cards(), key_prefix="commune", columns=2)

    with st.container(border=True):
        st.markdown("#### 🆕 What changed recently?")
        st.caption(
            "See the latest official figures and the biggest recent moves in "
            "housing, salaries, population, jobs and prices."
        )
        st.page_link("pages/5_What_Changed.py", label="Open What Changed?")

    with st.container(border=True):
        st.markdown("#### 🔎 For advanced users")
        st.caption(
            "Want the raw data? The Dataset Explorer lets you search all "
            "official STATEC / LUSTAT datasets, inspect dimensions, and export CSVs."
        )
        st.page_link("pages/11_Dataset_Explorer.py", label="Open the Dataset Explorer")
