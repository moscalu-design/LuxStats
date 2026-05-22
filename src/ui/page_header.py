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
        "Luxembourg statistics, made easier",
        "Search a topic, open a chart, or inspect the official source behind it.",
    ),
    "find": PageHeader(
        "Find a statistic",
        "Search official Luxembourg statistics in plain words.",
    ),
    "commune": PageHeader(
        "Commune portal",
        "Pick a commune and see its local statistics in one profile.",
    ),
    "compare": PageHeader(
        "Compare statistics",
        "Put communes, sectors or groups side by side.",
    ),
    "builder": PageHeader(
        "Build a chart",
        "Create a chart from official statistics — no dataset codes needed.",
    ),
    "changes": PageHeader(
        "What changed?",
        "The latest official figures and the biggest recent moves.",
    ),
    "housing": PageHeader(
        "Housing",
        "Housing prices, construction and the size of new homes.",
    ),
    "salaries": PageHeader(
        "Salaries & income",
        "Pay by sector, the gender pay gap and the minimum wage.",
    ),
    "population": PageHeader(
        "Population",
        "How many people live in Luxembourg, and how that changes.",
    ),
    "labour": PageHeader(
        "Labour market",
        "Jobs, employment and unemployment over time.",
    ),
    "prices": PageHeader(
        "Prices & inflation",
        "Consumer prices and the cost of living.",
    ),
    "economy": PageHeader(
        "Economy",
        "GDP, short-term indicators and economic activity.",
    ),
    "tourism": PageHeader(
        "Tourism",
        "Accommodation arrivals and short-term tourism indicators.",
    ),
    "source_library": PageHeader(
        "Source Library",
        "Advanced: every official source, its readiness and mapping status.",
    ),
    "dataset_explorer": PageHeader(
        "Dataset Explorer",
        "Advanced: search raw LUSTAT datasets and export CSVs.",
    ),
    "about": PageHeader(
        "About Data",
        "Where the numbers come from and how to read this site.",
    ),
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
