from __future__ import annotations

from src.page_helpers import dashboard_placeholder
from src.ui_components import configure_page, render_sidebar

configure_page("LuxStats - Labour Market")
render_sidebar()
dashboard_placeholder(
    "Labour Market",
    "Explore employment and unemployment indicators with simple filters.",
    [
        "Employment and unemployment over time",
        "Breakdowns by sex, age group, sector, or geography where available",
        "Latest values and recent changes",
    ],
)
