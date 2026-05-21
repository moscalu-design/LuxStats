from __future__ import annotations

from src.ui.chart_builder import render_chart_builder
from src.ui_components import configure_page, page_hero, render_sidebar

configure_page("LuxStats - Build a Chart")
render_sidebar()

page_hero(
    "Build a Chart",
    "Create a chart from official statistics in a few clicks",
    "Pick a topic, choose a metric, decide what to compare and how to show it. "
    "No dataset codes, no spreadsheets — just official Luxembourg figures.",
)

render_chart_builder()
