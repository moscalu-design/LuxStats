"""Home page: a guided front door to Luxembourg statistics."""

from __future__ import annotations

import streamlit as st

from src.concept_view import render_concept
from src.concepts import get_concept
from src.data.analysis_cards import commune_cards, comparison_cards, popular_cards
from src.data.communes import list_communes
from src.data.priority_topics import home_question_cards
from src.search import NO_RESULTS_HINT, search_communes, search_concepts, search_source_visualizations
from src.ui.cards import render_analysis_grid, render_metric_grid, render_question_grid
from src.ui.catalog_views import render_coverage_section, render_source_coverage_badges
from src.ui.page_header import render_page_header
from src.ui.source_visualizer import status_label
from src.ui_components import section_header

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
    ("", "Tourism", "Accommodation arrivals, overnight stays, and short-term tourism indicators.",
     "pages/15_Tourism.py"),
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
                    st.markdown(f"**{name}**")
                    st.caption(blurb)
                    st.page_link(page, label=f"Explore {name}", use_container_width=True)


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
        f"{total} matching result(s)" if total else "",
    )
    if not results and not commune_results and not source_hits:
        st.info(NO_RESULTS_HINT)
        return
    if commune_results:
        for result in commune_results:
            _commune_card(result, key_prefix="commune_search")
    if results:
        render_metric_grid(results, key_prefix="search", columns=2)
    if source_hits:
        section_header("Source-backed matches")
        grouped = [
            ("Chart-ready concepts", {"chart_ready"}),
            ("Preview-ready sources", {"preview_ready"}),
            ("Downloadable-only sources", {"downloadable_only"}),
            ("Unresolved official sources", set()),
        ]
        shown: set[str] = set()
        for label, statuses in grouped:
            rows = [
                row for row in source_hits[:5]
                if row["source_id"] not in shown
                and (row["visualization_status"] in statuses if statuses else row["visualization_status"] not in {"chart_ready", "preview_ready", "downloadable_only"})
            ]
            if not rows:
                continue
            st.caption(label)
            for row in rows:
                shown.add(row["source_id"])
                with st.container(border=True):
                    badge_class = _status_badge_class(row["visualization_status"])
                    st.markdown(
                        f"<span class='lux-tag'>{row['category']}</span> "
                        f"<span class='lux-tag {badge_class}'>{status_label(row['visualization_status'])}</span>",
                        unsafe_allow_html=True,
                    )
                    st.markdown(f"**{row['title']}**")
                    st.caption(row["reason"])
                    if row["visualization_status"] == "chart_ready" and row.get("mapped_metric_id"):
                        if st.button("Open chart", key=f"home_src_{row['source_id']}", use_container_width=True):
                            st.session_state["open_concept"] = row["mapped_metric_id"]
                            st.rerun()
                    else:
                        st.page_link("pages/13_Source_Library.py", label=row["recommended_action"], use_container_width=True)


def _render_question_cards() -> None:
    cards = home_question_cards(limit=8)
    render_question_grid(cards, key_prefix="home_question", columns=4)


def _render_commune_quick_search() -> None:
    with st.container(border=True):
        st.markdown("#### Look up your commune")
        commune = st.selectbox(
            "Choose a commune",
            list_communes(),
            index=list_communes().index("Hesperange"),
            label_visibility="collapsed",
        )
        if st.button("Open commune profile", use_container_width=True):
            st.session_state["selected_commune"] = commune
            st.switch_page("pages/3_Commune_Portal.py")


def render_home() -> None:
    render_page_header("home", eyebrow="Official STATEC / LUSTAT data")

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

    st.markdown(
        """
        <div class="lux-howto">
            <div class="lux-howto-step"><strong>Search a topic</strong><span>Use everyday words like salary, housing, population or inflation.</span></div>
            <div class="lux-howto-step"><strong>Open a question</strong><span>Start from a curated public-interest card when you are not sure what to search.</span></div>
            <div class="lux-howto-step"><strong>View official data</strong><span>Chart-ready concepts use confirmed mappings only.</span></div>
            <div class="lux-howto-step"><strong>Inspect sources</strong><span>Open source links and readiness details when you need the record behind a chart.</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    section_header("Start with a question",
                   "Source-backed entry points for the statistics people ask for most.")
    _render_question_cards()

    section_header("Popular statistics",
                   "Chart-ready answers backed by confirmed official datasets.")
    render_analysis_grid(popular_cards(), key_prefix="popular", columns=3)

    section_header("Common comparisons",
                   "Put places, sectors or trends side by side.")
    render_analysis_grid(comparison_cards(), key_prefix="compare", columns=3)

    section_header("Browse by topic", "Pick an area and jump straight to curated charts.")
    _render_topic_grid()

    section_header("Explore by commune",
                   "Local statistics for any of Luxembourg's 100 communes.")
    left, right = st.columns([1, 2])
    with left:
        _render_commune_quick_search()
    with right:
        render_analysis_grid(commune_cards(), key_prefix="commune", columns=2)

    with st.container(border=True):
        st.markdown("#### What changed recently?")
        st.caption(
            "See the latest official figures and the biggest recent moves in "
            "housing, salaries, population, jobs and prices."
        )
        st.page_link("pages/5_What_Changed.py", label="Open What Changed?")

    section_header("Data coverage",
                   "Every official STATEC source the portal has cataloged.")
    render_coverage_section()
    render_source_coverage_badges(label="Product readiness")

    with st.container(border=True):
        st.markdown("#### Visualize or inspect any source")
        st.caption(
            "Every cataloged source now has a safe next step: open a chart, preview a table, "
            "download the official file, or see the mapping work needed."
        )
        st.page_link("pages/13_Source_Library.py", label="Open the Source Library readiness view")

    with st.container(border=True):
        st.markdown("#### For advanced users")
        st.caption(
            "Want the raw data? The Dataset Explorer lets you search all "
            "official STATEC / LUSTAT datasets, inspect dimensions, and export CSVs."
        )
        st.page_link("pages/11_Dataset_Explorer.py", label="Open the Dataset Explorer")
