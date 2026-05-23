"""Home page: the front door to Luxembourg statistics.

The landing page answers four questions fast — what LuxStats is, what you can
do, where to start, and whether the data can be trusted — then gets out of the
way. Search is the headline action; everything else is a calm second tier.
"""

from __future__ import annotations

from html import escape

import streamlit as st

from src.concept_view import render_concept
from src.concepts import get_concept
from src.data.priority_topics import home_question_cards
from src.search import NO_RESULTS_HINT, search_communes, search_concepts, search_source_visualizations
from src.ui.cards import render_metric_grid, render_question_grid
from src.ui.source_visualizer import status_label
from src.ui.theme import section_header, trust_note

# Topic -> (icon, name, one-line description, page path).
TOPIC_TILES: list[tuple[str, str, str, str]] = [
    ("🏠", "Housing", "Prices, construction and the size of new homes.",
     "pages/6_Housing.py"),
    ("💶", "Salaries & income", "Pay by sector, the gender pay gap, minimum wage.",
     "pages/7_Salaries.py"),
    ("👥", "Population", "How many people live here, and how that changes.",
     "pages/8_Population.py"),
    ("🧰", "Labour market", "Jobs, employment and unemployment over time.",
     "pages/9_Labour_Market.py"),
    ("📈", "Prices & inflation", "Consumer prices and the cost of living.",
     "pages/10_Prices_Inflation.py"),
    ("🏦", "Economy", "GDP and short-term economic indicators.",
     "pages/14_Economy.py"),
    ("🧳", "Tourism", "Accommodation arrivals and overnight stays.",
     "pages/15_Tourism.py"),
    ("🤖", "AI adoption", "How widely companies use AI, and what for.",
     "pages/16_AI.py"),
]

# Secondary tools — useful, but not the headline. (icon, name, blurb, page).
TOOL_TILES: list[tuple[str, str, str, str]] = [
    ("⚖️", "Compare", "Put communes, sectors or groups side by side.",
     "pages/4_Compare.py"),
    ("🛠️", "Build a chart", "Make your own chart without dataset codes.",
     "pages/2_Build_a_Chart.py"),
    ("📍", "Commune portal", "All local statistics for one commune.",
     "pages/3_Commune_Portal.py"),
    ("🆕", "What changed?", "Latest figures and the biggest recent moves.",
     "pages/5_What_Changed.py"),
]


def _render_hero() -> None:
    st.markdown(
        """
        <section class="lux-hero">
            <h1>LuxStats</h1>
            <p>Official Luxembourg statistics, made easier to find and compare.</p>
        </section>
        """,
        unsafe_allow_html=True,
    )


def _render_tiles(items: list[tuple[str, str, str, str]], *, columns: int) -> None:
    """Render a compact grid of routing tiles."""
    for start in range(0, len(items), columns):
        cols = st.columns(columns)
        for col, (icon, name, blurb, page) in zip(cols, items[start:start + columns]):
            with col:
                with st.container(border=True):
                    st.markdown(
                        f"<div class='lux-tile-icon'>{escape(icon)}</div>"
                        f"<h4>{escape(name)}</h4>"
                        f"<p>{escape(blurb)}</p>",
                        unsafe_allow_html=True,
                    )
                    st.page_link(page, label=f"Open {name.lower()}",
                                 use_container_width=True)


def _commune_card(result: dict[str, str], key_prefix: str) -> None:
    with st.container(border=True):
        st.markdown("<span class='lux-tag'>Commune</span>", unsafe_allow_html=True)
        st.markdown(f"**{result['title']}**")
        st.caption(result["description"])
        if st.button(
            "Open commune profile",
            key=f"{key_prefix}_{result['commune']}_{result['tab']}",
            use_container_width=True,
        ):
            st.session_state["selected_commune"] = result["commune"]
            st.switch_page("pages/3_Commune_Portal.py")


def _status_badge_class(status: str) -> str:
    if status in {"chart_ready", "preview_ready", "downloadable_only"}:
        return f"lux-status-{status.replace('_', '-')}"
    return "lux-status-unresolved"


def _render_search_results(query: str) -> None:
    results = search_concepts(query)
    commune_results = search_communes(query)
    source_hits = search_source_visualizations(query, limit=5)
    total = len(results) + len(commune_results) + len(source_hits)
    section_header(
        f"Results for “{query.strip()}”",
        f"{total} matching result(s)" if total else "Nothing matched that search.",
    )
    if not results and not commune_results and not source_hits:
        st.info(NO_RESULTS_HINT)
        return

    if results or commune_results:
        for result in commune_results:
            _commune_card(result, key_prefix="commune_search")
        if results:
            render_metric_grid(results, key_prefix="search", columns=2)

    if source_hits:
        section_header(
            "Official sources",
            "Chart-ready and preview-ready sources rank ahead of records still being mapped.",
        )
        grouped = [
            ("Ready to chart", {"chart_ready"}),
            ("Ready to preview", {"preview_ready"}),
            ("Download only", {"downloadable_only"}),
            ("Needs mapping or review", set()),
        ]
        shown: set[str] = set()
        for label, statuses in grouped:
            rows = [
                row for row in source_hits[:5]
                if row["source_id"] not in shown
                and (row["visualization_status"] in statuses if statuses
                     else row["visualization_status"] not in
                     {"chart_ready", "preview_ready", "downloadable_only"})
            ]
            if not rows:
                continue
            st.caption(label)
            for row in rows:
                shown.add(row["source_id"])
                with st.container(border=True):
                    badge_class = _status_badge_class(row["visualization_status"])
                    st.markdown(
                        f"<span class='lux-tag'>{row['category']}</span>"
                        f"<span class='lux-tag {badge_class}'>"
                        f"{status_label(row['visualization_status'])}</span>",
                        unsafe_allow_html=True,
                    )
                    st.markdown(f"**{row['title']}**")
                    st.caption(row["reason"])
                    if row["visualization_status"] == "chart_ready" and row.get("mapped_metric_id"):
                        if st.button("Open chart", key=f"home_src_{row['source_id']}",
                                     use_container_width=True):
                            st.session_state["open_concept"] = row["mapped_metric_id"]
                            st.rerun()
                    else:
                        st.page_link("pages/13_Source_Library.py",
                                     label=row["recommended_action"],
                                     use_container_width=True)


def render_home() -> None:
    _render_hero()

    query = st.text_input(
        "Search Luxembourg statistics",
        placeholder="Try “housing prices”, “median salary”, “inflation”, “Hesperange”…",
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

    # ---- Start with a question ------------------------------------------
    section_header(
        "Start with a question",
        "Common questions people ask of Luxembourg statistics.",
    )
    render_question_grid(home_question_cards(limit=6), key_prefix="home_question",
                         columns=3)

    # ---- Explore by topic -----------------------------------------------
    section_header("Explore by topic", "Seven areas, each with charts and official sources.")
    _render_tiles(TOPIC_TILES, columns=4)

    # ---- Tools for deeper analysis --------------------------------------
    section_header("Tools for deeper analysis",
                   "When search and topics are not enough.")
    _render_tiles(TOOL_TILES, columns=4)

    # ---- Trust ----------------------------------------------------------
    st.markdown("<div style='height:1.4rem'></div>", unsafe_allow_html=True)
    trust_note(
        "Every chart is built from official STATEC / LUSTAT data, with the source "
        "and a CSV download one click away. LuxStats is deterministic: there is no "
        "chatbot and no AI-generated answers — just the official figures."
    )
