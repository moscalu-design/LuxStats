"""Dashboard placeholder metadata used by topic pages."""

from __future__ import annotations

from dataclasses import dataclass

import streamlit as st

from src.page_helpers import dashboard_placeholder


@dataclass(frozen=True)
class DashboardSpec:
    theme: str
    page_title: str
    intro: str
    planned_views: tuple[str, ...]


DASHBOARD_SPECS: dict[str, DashboardSpec] = {
    "Housing": DashboardSpec(
        theme="Housing",
        page_title="Housing",
        intro="Explore housing prices, rents, affordability, and commune or region comparisons.",
        planned_views=(
            "Median or average prices over time",
            "Price comparison by commune or region",
            "Indexed price growth",
            "Rent trends where official data is available",
        ),
    ),
    "Population": DashboardSpec(
        theme="Population",
        page_title="Population",
        intro="Follow how Luxembourg's population changes nationally and across communes.",
        planned_views=(
            "Population over time",
            "Population growth rate",
            "Top growing communes",
            "Age groups and nationality where available",
        ),
    ),
    "Labour Market": DashboardSpec(
        theme="Labour Market",
        page_title="Labour Market",
        intro="Explore employment and unemployment indicators with simple filters.",
        planned_views=(
            "Employment and unemployment over time",
            "Breakdowns by sex, age group, sector, or geography where available",
            "Latest values and recent changes",
        ),
    ),
    "Prices & Inflation": DashboardSpec(
        theme="Prices & Inflation",
        page_title="Prices & Inflation",
        intro="See how consumer prices change over time and compare categories when data supports it.",
        planned_views=(
            "Inflation over time",
            "Consumer price index trends",
            "Category-level price changes",
            "Plain-language index explanations",
        ),
    ),
}


def render_topic_dashboard(theme: str) -> None:
    spec = DASHBOARD_SPECS.get(theme)
    if spec is None:
        st.error(f"No dashboard placeholder has been configured for {theme}.")
        return
    dashboard_placeholder(spec.page_title, spec.intro, list(spec.planned_views), catalog_theme=spec.theme)
