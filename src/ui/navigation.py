"""Centralized product navigation for the Streamlit app."""

from __future__ import annotations

from dataclasses import dataclass

import streamlit as st


@dataclass(frozen=True)
class NavItem:
    label: str
    page: str
    icon: str | None
    group: str
    description: str = ""


NAV_GROUPS: tuple[tuple[str, tuple[NavItem, ...]], ...] = (
    (
        "Main",
        (
            NavItem("Home", "app.py", None, "Main", "Start with search and key questions."),
            NavItem("Find a Statistic", "pages/1_Find_a_Statistic.py", None, "Main", "Search charts, communes and sources."),
            NavItem("Compare", "pages/4_Compare.py", None, "Main", "Compare places and groups."),
            NavItem("Build a Chart", "pages/2_Build_a_Chart.py", None, "Main", "Create a supported chart."),
            NavItem("What Changed?", "pages/5_What_Changed.py", None, "Main", "Recent updates and movements."),
        ),
    ),
    (
        "Topics",
        (
            NavItem("Housing", "pages/6_Housing.py", None, "Topics"),
            NavItem("Salaries & Income", "pages/7_Salaries.py", None, "Topics"),
            NavItem("Population", "pages/8_Population.py", None, "Topics"),
            NavItem("Labour Market", "pages/9_Labour_Market.py", None, "Topics"),
            NavItem("Prices & Inflation", "pages/10_Prices_Inflation.py", None, "Topics"),
            NavItem("Economy", "pages/14_Economy.py", None, "Topics"),
            NavItem("Tourism", "pages/15_Tourism.py", None, "Topics"),
        ),
    ),
    (
        "Data & Sources",
        (
            NavItem("Dataset Explorer", "pages/11_Dataset_Explorer.py", None, "Data & Sources", "Inspect API/chart-ready data."),
            NavItem("Source Library", "pages/13_Source_Library.py", None, "Data & Sources", "All official records and readiness."),
        ),
    ),
    (
        "About / Help",
        (
            NavItem("About Data", "pages/12_About_Data.py", None, "About / Help", "Methods, cache and limits."),
        ),
    ),
)


def all_nav_items() -> list[NavItem]:
    return [item for _, items in NAV_GROUPS for item in items]


def nav_page_paths() -> set[str]:
    return {item.page for item in all_nav_items()}


def render_navigation() -> None:
    """Render compact grouped navigation in the left sidebar."""
    st.sidebar.markdown("<div class='lux-sidebar-title'>LuxStats</div>", unsafe_allow_html=True)
    st.sidebar.caption("Official Luxembourg statistics.")
    for group, items in NAV_GROUPS:
        st.sidebar.markdown(f"<div class='lux-sidebar-group'>{group}</div>", unsafe_allow_html=True)
        for item in items:
            kwargs = {"label": item.label}
            if item.icon:
                kwargs["icon"] = item.icon
            st.sidebar.page_link(item.page, **kwargs)
    st.sidebar.caption("Official STATEC / LUSTAT data only.")
