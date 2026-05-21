from __future__ import annotations

from src.ui.chart_builder import render_chart_builder
from src.ui.page_header import render_page_header
from src.ui_components import configure_page, render_sidebar

configure_page("LuxStats - Build a Chart")
render_sidebar()

render_page_header("builder")

render_chart_builder()
