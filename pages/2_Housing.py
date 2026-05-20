from __future__ import annotations

from src.page_helpers import dashboard_placeholder
from src.ui_components import configure_page, render_sidebar

configure_page("LuxStats - Housing")
render_sidebar()
dashboard_placeholder(
    "Housing",
    "Explore housing prices, rents, affordability, and commune or region comparisons.",
    [
        "Median or average prices over time",
        "Price comparison by commune or region",
        "Indexed price growth",
        "Rent trends where official data is available",
    ],
)
