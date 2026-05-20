from __future__ import annotations

from src.page_helpers import dashboard_placeholder
from src.ui_components import configure_page, render_sidebar

configure_page("LuxStats - Population")
render_sidebar()
dashboard_placeholder(
    "Population",
    "Follow how Luxembourg's population changes nationally and across communes.",
    [
        "Population over time",
        "Population growth rate",
        "Top growing communes",
        "Age groups and nationality where available",
    ],
)
