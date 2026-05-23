"""Centralized product navigation for the Streamlit app.

LuxStats hides Streamlit's default multipage auto-nav (see ``.streamlit/
config.toml`` and ``src/ui/theme.py``) and renders this single, compact
sidebar instead. The hierarchy is deliberate:

* **Primary** — the everyday journeys, always visible and unlabelled so they
  read as the main menu.
* **Topics** — the seven statistics areas, visually subordinate.
* **More tools** — advanced builders and source-inspection pages, tucked
  inside a collapsed expander so they never dominate.
"""

from __future__ import annotations

from dataclasses import dataclass

import streamlit as st


@dataclass(frozen=True)
class NavItem:
    label: str
    page: str
    group: str
    icon: str | None = None
    description: str = ""


# Group order matters: it is the order the sidebar renders in.
NAV_GROUPS: tuple[tuple[str, tuple[NavItem, ...]], ...] = (
    (
        "Primary",
        (
            NavItem("Home", "app.py", "Primary", description="Start here."),
            NavItem("Find a statistic", "pages/1_Find_a_Statistic.py", "Primary",
                    description="Search official statistics in plain words."),
            NavItem("Compare", "pages/4_Compare.py", "Primary",
                    description="Put places or groups side by side."),
            NavItem("What changed?", "pages/5_What_Changed.py", "Primary",
                    description="Latest figures and recent moves."),
        ),
    ),
    (
        "Topics",
        (
            NavItem("Housing", "pages/6_Housing.py", "Topics"),
            NavItem("Salaries & income", "pages/7_Salaries.py", "Topics"),
            NavItem("Population", "pages/8_Population.py", "Topics"),
            NavItem("Labour market", "pages/9_Labour_Market.py", "Topics"),
            NavItem("Prices & inflation", "pages/10_Prices_Inflation.py", "Topics"),
            NavItem("Economy", "pages/14_Economy.py", "Topics"),
            NavItem("Tourism", "pages/15_Tourism.py", "Topics"),
            NavItem("AI adoption", "pages/16_AI.py", "Topics"),
        ),
    ),
    (
        "More tools",
        (
            NavItem("Build a chart", "pages/2_Build_a_Chart.py", "More tools",
                    description="Create a chart without dataset codes."),
            NavItem("Commune portal", "pages/3_Commune_Portal.py", "More tools",
                    description="One commune, all its local statistics."),
            NavItem("Dataset explorer", "pages/11_Dataset_Explorer.py", "More tools",
                    description="Advanced: search raw LUSTAT datasets."),
            NavItem("Source library", "pages/13_Source_Library.py", "More tools",
                    description="Advanced: every official source and its readiness."),
            NavItem("About the data", "pages/12_About_Data.py", "More tools",
                    description="Where the numbers come from."),
        ),
    ),
)

# Groups whose items are advanced and rendered inside a collapsed expander.
_COLLAPSED_GROUPS = {"More tools"}


def all_nav_items() -> list[NavItem]:
    return [item for _, items in NAV_GROUPS for item in items]


def nav_page_paths() -> set[str]:
    return {item.page for item in all_nav_items()}


def primary_items() -> list[NavItem]:
    return [item for item in all_nav_items() if item.group == "Primary"]


def topic_items() -> list[NavItem]:
    return [item for item in all_nav_items() if item.group == "Topics"]


def _render_links(items: tuple[NavItem, ...]) -> None:
    for item in items:
        kwargs: dict[str, object] = {"label": item.label}
        if item.icon:
            kwargs["icon"] = item.icon
        st.page_link(item.page, **kwargs)


def render_navigation() -> None:
    """Render the single, compact LuxStats sidebar."""
    with st.sidebar:
        st.markdown("<div class='lux-brand'>LuxStats</div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='lux-brand-sub'>Official Luxembourg statistics</div>",
            unsafe_allow_html=True,
        )
        for group, items in NAV_GROUPS:
            if group in _COLLAPSED_GROUPS:
                with st.expander(group, expanded=False):
                    _render_links(items)
                continue
            if group != "Primary":
                st.markdown(
                    f"<div class='lux-nav-group'>{group}</div>", unsafe_allow_html=True
                )
            _render_links(items)
        st.markdown(
            "<div class='lux-sidebar-foot'>Source-backed and deterministic. "
            "Official STATEC / LUSTAT data only.</div>",
            unsafe_allow_html=True,
        )
