from __future__ import annotations

from src.page_helpers import dashboard_placeholder
from src.ui_components import configure_page, render_sidebar

configure_page("LuxStats - Prices & Inflation")
render_sidebar()
dashboard_placeholder(
    "Prices & Inflation",
    "See how consumer prices change over time and compare categories when data supports it.",
    [
        "Inflation over time",
        "Consumer price index trends",
        "Category-level price changes",
        "Plain-language index explanations",
    ],
)
