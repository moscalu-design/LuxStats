from __future__ import annotations

import streamlit as st

from src.concept_view import render_concept
from src.concepts import all_concepts, get_concept
from src.data.source_catalog import search_source_catalog
from src.search import NO_RESULTS_HINT, search_communes, search_concepts
from src.ui.cards import render_metric_grid
from src.ui.catalog_views import render_source_records
from src.ui_components import configure_page, page_hero, render_sidebar, section_header

configure_page("LuxStats - Find a Statistic")
render_sidebar()

page_hero(
    "Find a Statistic",
    "Search Luxembourg statistics in plain language",
    "Type what you are looking for — housing prices, median salary, population "
    "growth, inflation, or a commune name. You get friendly metric cards, not "
    "raw dataset codes.",
)

query = st.text_input(
    "Search Luxembourg statistics",
    placeholder="housing prices · salary by sector · population Hesperange · inflation…",
    key="finder_search",
    label_visibility="collapsed",
)


def _commune_card(result: dict[str, str]) -> None:
    with st.container(border=True):
        st.markdown("<span class='lux-tag'>Commune</span>", unsafe_allow_html=True)
        st.markdown(f"**{result['title']}**")
        st.caption(result["description"])
        if st.button(
            "Open commune profile →",
            key=f"finder_commune_{result['commune']}_{result['tab']}",
            use_container_width=True,
        ):
            st.session_state["selected_commune"] = result["commune"]
            st.switch_page("pages/3_Commune_Portal.py")


# A chart opened from a metric card.
open_id = st.session_state.get("open_concept")
if open_id:
    concept = get_concept(open_id)
    if concept is not None:
        section_header("Your chart")
        render_concept(concept, key=f"finder_{concept.id}")
        if st.button("← Back to search"):
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
    # Curated metrics rank first; raw official sources are offered below them.
    sources = search_source_catalog(query)
    if not results and not commune_results and not sources:
        st.info(NO_RESULTS_HINT)
    else:
        for result in commune_results:
            _commune_card(result)
        if results:
            render_metric_grid(results, key_prefix="finder", columns=2)

    if sources:
        if results:
            section_header(
                "Other official sources",
                f"{len(sources)} STATEC / LUSTAT source(s) also match — these "
                "are raw datasets and files, not curated charts.",
            )
        else:
            section_header(
                "Official sources you can explore",
                "No curated chart matches yet, but these official STATEC "
                "sources do — open them in the Source Library.",
            )
        render_source_records(sources, key_prefix="finder_sources", limit=6)
else:
    section_header(
        "All curated statistics",
        "Every metric here is backed by a confirmed STATEC / LUSTAT dataset.",
    )
    render_metric_grid(all_concepts(), key_prefix="finder_all", columns=2)
