from __future__ import annotations

from src.dashboard_specs import render_topic_dashboard
from src.ui_components import configure_page, render_sidebar

configure_page("LuxStats - Housing")
render_sidebar()
render_topic_dashboard("Housing")
