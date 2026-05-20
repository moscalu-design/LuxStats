"""Home page for the statistics portal."""

from __future__ import annotations

import streamlit as st

from src.catalog import search_catalog
from src.ui_components import caveat_panel, page_hero, render_topic_cards, status_panel


TOPIC_CARDS = [
    {"icon": "🏠", "title": "Housing", "description": "Prices, rents, affordability, and local comparisons.", "action": "Dataset IDs to confirm"},
    {"icon": "💶", "title": "Salaries", "description": "Live LUSTAT dataflow search, caching, quick charts, and CSV export.", "action": "Ready to explore"},
    {"icon": "👥", "title": "Population", "description": "Population growth, communes, age groups, and nationality when available.", "action": "Dataset IDs to confirm"},
    {"icon": "🧰", "title": "Labour Market", "description": "Jobs, unemployment, sectors, and worker groups.", "action": "Dataset IDs to confirm"},
    {"icon": "📈", "title": "Prices & Inflation", "description": "Consumer prices, inflation trends, and spending categories.", "action": "Dataset IDs to confirm"},
    {"icon": "🏛️", "title": "Economy", "description": "Business and economic indicators from official data.", "action": "Catalog placeholder"},
]


def render_home() -> None:
    page_hero(
        "Luxembourg in plain numbers",
        "Friendly statistics for everyday questions",
        "Explore official Luxembourg statistics with clear labels, source notes, and practical starter dashboards. "
        "The salary explorer and dataset search use live STATEC / LUSTAT dataflows; other topics stay clearly marked until their official IDs are confirmed.",
    )

    status_panel(
        "What can I do here today?",
        [
            ("1", "Explore salaries with live data", "Search salary, wage, and income dataflows, cache datasets, chart them, and export CSV files."),
            ("2", "Find candidate datasets", "Use the curated catalog and live dataflow search to discover official LUSTAT sources by topic."),
            ("3", "Track what still needs verification", "Topic dashboards show TODO_CONFIRM_* placeholders instead of pretending unverified IDs are official."),
        ],
    )

    query = st.text_input(
        "Find a topic or dataset",
        placeholder="Try house prices, wages, population by commune, inflation...",
    )
    if query:
        matches = search_catalog(query=query)
        st.caption(f"{len(matches)} curated matches")
        st.dataframe(
            matches[["theme", "friendly_title", "description", "dataset_id", "status"]],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.caption("Search covers friendly names, descriptions, aliases, and placeholder IDs in the curated catalog.")

    st.subheader("Explore by topic")
    render_topic_cards(TOPIC_CARDS)

    st.subheader("Good next steps")
    col1, col2 = st.columns(2)
    with col1:
        st.page_link("pages/3_Salaries.py", label="Open the salary explorer", icon="💶")
        st.caption("Best when you want to fetch live LUSTAT salary-related dataflows and build a quick chart.")
    with col2:
        st.page_link("pages/7_Dataset_Explorer.py", label="Open the dataset explorer", icon="🔎")
        st.caption("Best when you want to inspect curated candidates or search live LUSTAT dataflows.")

    caveat_panel(
        "Placeholder dashboards are intentionally conservative: they describe planned views, but they do not display fake data or invented official dataset IDs."
    )
