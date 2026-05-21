"""Centralized product navigation for the Streamlit app."""

from __future__ import annotations

from dataclasses import dataclass

import streamlit as st


@dataclass(frozen=True)
class NavItem:
    label: str
    page: str
    icon: str
    group: str
    description: str = ""


NAV_GROUPS: tuple[tuple[str, tuple[NavItem, ...]], ...] = (
    (
        "Main",
        (
            NavItem("Home", "app.py", "🏠", "Main", "Start with search and key questions."),
            NavItem("Find a Statistic", "pages/1_Find_a_Statistic.py", "🔍", "Main", "Search charts, communes and sources."),
            NavItem("Commune Portal", "pages/3_Commune_Portal.py", "📍", "Main", "Explore one commune."),
            NavItem("Compare", "pages/4_Compare.py", "📊", "Main", "Compare places and groups."),
            NavItem("Build a Chart", "pages/2_Build_a_Chart.py", "🛠️", "Main", "Create a supported chart."),
            NavItem("What Changed?", "pages/5_What_Changed.py", "🆕", "Main", "Recent updates and movements."),
        ),
    ),
    (
        "Topics",
        (
            NavItem("Housing", "pages/6_Housing.py", "🏠", "Topics"),
            NavItem("Salaries & Income", "pages/7_Salaries.py", "💶", "Topics"),
            NavItem("Population", "pages/8_Population.py", "👥", "Topics"),
            NavItem("Labour Market", "pages/9_Labour_Market.py", "🧰", "Topics"),
            NavItem("Prices & Inflation", "pages/10_Prices_Inflation.py", "📈", "Topics"),
            NavItem("Economy", "pages/14_Economy.py", "🏦", "Topics"),
        ),
    ),
    (
        "Advanced",
        (
            NavItem("Source Library", "pages/13_Source_Library.py", "🗂️", "Advanced", "All official records and readiness."),
            NavItem("Dataset Explorer", "pages/11_Dataset_Explorer.py", "🔎", "Advanced", "Inspect API/chart-ready data."),
            NavItem("About the Data", "pages/12_About_Data.py", "ℹ️", "Advanced", "Methods, cache and limits."),
        ),
    ),
)


def all_nav_items() -> list[NavItem]:
    return [item for _, items in NAV_GROUPS for item in items]


def nav_page_paths() -> set[str]:
    return {item.page for item in all_nav_items()}


def render_navigation() -> None:
    """Render compact grouped navigation in the left sidebar."""
    st.sidebar.markdown("### LuxStats")
    st.sidebar.caption("Official Luxembourg statistics, made explorable.")
    for group, items in NAV_GROUPS:
        st.sidebar.markdown("---")
        st.sidebar.markdown(f"**{group}**")
        for item in items:
            st.sidebar.page_link(item.page, label=item.label, icon=item.icon)
    st.sidebar.markdown("---")
    st.sidebar.caption("Official STATEC / LUSTAT data only.")
