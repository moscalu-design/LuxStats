from __future__ import annotations

import streamlit as st

from src.concept_view import render_concept
from src.concepts import all_concepts, get_concept
from src.data.source_catalog import search_source_catalog
from src.data.source_mapping import enrich_with_mapping_status
from src.search import NO_RESULTS_HINT, search_communes, search_concepts, search_source_visualizations
from src.ui.cards import render_metric_grid
from src.ui.catalog_views import render_source_records
from src.ui.source_visualizer import status_label
from src.ui.page_header import render_page_header
from src.ui_components import configure_page, render_sidebar, section_header

configure_page("LuxStats - Find a Statistic")
render_sidebar()

render_page_header("find")

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
    source_hits = search_source_visualizations(query)
    sources = enrich_with_mapping_status(search_source_catalog(query))
    source_hit_ids = {row["source_id"] for row in source_hits}
    raw_sources = [
        s for s in sources
        if s["mapping_status"] not in {"mapped_to_metric", "mapped_to_commune_portal"}
        and s["source_id"] not in source_hit_ids
    ]
    total = len(results) + len(commune_results) + len(source_hits) + len(raw_sources)
    section_header(
        f"Results for “{query.strip()}”",
        f"{total} matching result(s)" if total else "",
    )
    if not results and not commune_results and not source_hits and not raw_sources:
        st.info(NO_RESULTS_HINT)
    else:
        if results or commune_results:
            section_header("Best matches", "Ready-to-view charts and commune profiles come first.")
            for result in commune_results:
                _commune_card(result)
        if results:
            render_metric_grid(results, key_prefix="finder", columns=2)

    if source_hits:
        section_header("Source-backed matches", "Chart-ready and preview-ready sources are ranked ahead of raw records.")
        for row in source_hits[:6]:
            with st.container(border=True):
                st.markdown(
                    f"<span class='lux-tag'>{row['category']}</span> "
                    f"<span class='lux-tag'>{status_label(row['visualization_status'])}</span>",
                    unsafe_allow_html=True,
                )
                st.markdown(f"**{row['title']}**")
                st.caption(row["reason"])
                if row["visualization_status"] == "chart_ready" and row.get("mapped_metric_id"):
                    if st.button("Open chart", key=f"finder_src_{row['source_id']}", use_container_width=True):
                        st.session_state["open_concept"] = row["mapped_metric_id"]
                        st.rerun()
                else:
                    st.page_link("pages/13_Source_Library.py", label=row["recommended_action"], use_container_width=True)

    if raw_sources:
        if results:
            section_header(
                "Available official sources",
                f"{len(raw_sources)} STATEC / LUSTAT source(s) also match — these "
                "are raw datasets and files, not curated charts.",
            )
        else:
            section_header(
                "Official sources you can explore",
                "No curated chart matches yet, but these official STATEC "
                "sources do — open them in the Source Library.",
            )
        render_source_records(raw_sources, key_prefix="finder_sources", limit=6)
else:
    st.caption(
        "Type a question above, or browse every ready-to-chart statistic below. "
        "Searching also reaches official sources that are not charted yet."
    )
    section_header(
        "All ready-to-chart statistics",
        "Each one is backed by a confirmed STATEC / LUSTAT dataset.",
    )
    render_metric_grid(all_concepts(), key_prefix="finder_all", columns=2)
