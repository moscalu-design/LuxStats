"""Reusable page headers with consistent purpose statements."""

from __future__ import annotations

from dataclasses import dataclass
from html import escape
from typing import Callable

import streamlit as st


@dataclass(frozen=True)
class PageHeader:
    title: str
    subtitle: str


PAGE_HEADERS: dict[str, PageHeader] = {
    "home": PageHeader(
        "Luxembourg Statistics Explorer",
        "Search a topic, open a curated chart, or inspect the official source when you need the details.",
    ),
    "find": PageHeader("Find a Statistic", "Search official Luxembourg statistics, charts, communes, and source records."),
    "commune": PageHeader("Commune Portal", "Choose a commune and explore local statistics in one place."),
    "compare": PageHeader("Compare Statistics", "Compare communes, sectors, years, and indicators using official data."),
    "builder": PageHeader("Build a Chart", "Create a chart from chart-ready official sources in a few clicks."),
    "changes": PageHeader("What Changed?", "See recent updates and movements in key Luxembourg indicators."),
    "housing": PageHeader("Housing", "Explore housing prices, rents, construction, permits, and market indicators."),
    "salaries": PageHeader("Salaries & Income", "Compare salaries, wages, income indicators, and minimum wage data."),
    "population": PageHeader("Population", "Explore population growth, migration, ageing, fertility, and communes."),
    "labour": PageHeader("Labour Market", "Track employment, unemployment, jobseekers, vacancies, and labour indicators."),
    "prices": PageHeader("Prices & Inflation", "Follow consumer prices, inflation, CPI components, and cost-of-living indicators."),
    "economy": PageHeader("Economy", "Explore GDP, short-term indicators, confidence, and economic activity."),
    "tourism": PageHeader(
        "Tourism",
        "Official Luxembourg tourism statistics, including accommodation arrivals and related short-term indicators.",
    ),
    "source_library": PageHeader("Source Library", "Advanced inventory of official sources, readiness states, and mapping work."),
    "dataset_explorer": PageHeader("Dataset Explorer", "Advanced inspection for curated API entries and live LUSTAT dataflows."),
    "about": PageHeader("About Data", "Learn how LuxStats uses official STATEC/LUSTAT sources."),
}


def get_page_header(page_id: str) -> PageHeader:
    return PAGE_HEADERS[page_id]


def render_page_header(
    page_id: str,
    *,
    eyebrow: str | None = None,
    coverage: Callable[[], None] | None = None,
    action: Callable[[], None] | None = None,
) -> None:
    header = get_page_header(page_id)
    st.markdown(
        f"""
        <section class="lux-page-header">
            <div class="lux-kicker">{escape(eyebrow or "LuxStats")}</div>
            <h1>{escape(header.title)}</h1>
            <p>{escape(header.subtitle)}</p>
        </section>
        """,
        unsafe_allow_html=True,
    )
    if coverage or action:
        left, right = st.columns([3, 1])
        if coverage:
            with left:
                coverage()
        if action:
            with right:
                action()
