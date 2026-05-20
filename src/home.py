"""Home page for the statistics portal."""

from __future__ import annotations

import streamlit as st

from src.catalog import search_catalog
from src.ui_components import render_topic_cards


TOPIC_CARDS = [
    {"icon": "🏠", "title": "Housing", "description": "Prices, rents, affordability, and local comparisons."},
    {"icon": "💶", "title": "Salaries", "description": "Wages by time, sector, occupation, sex, education, and distribution."},
    {"icon": "👥", "title": "Population", "description": "Population growth, communes, age groups, and nationality when available."},
    {"icon": "🧰", "title": "Labour Market", "description": "Jobs, unemployment, sectors, and worker groups."},
    {"icon": "📈", "title": "Prices & Inflation", "description": "Consumer prices, inflation trends, and spending categories."},
    {"icon": "🏛️", "title": "Economy", "description": "Business and economic indicators from official data."},
]


def render_home() -> None:
    st.title("Luxembourg Statistics Portal")
    st.write("Explore official Luxembourg statistics through simple interactive charts.")

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

    st.subheader("Explore by topic")
    render_topic_cards(TOPIC_CARDS)

    st.subheader("Popular charts")
    st.write(
        "Starter dashboard slots are ready for housing prices, salaries by sector, population growth by commune, "
        "and inflation over time. Exact official dataset IDs are tracked in the Dataset Explorer."
    )
