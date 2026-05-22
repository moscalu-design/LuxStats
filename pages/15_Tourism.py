from __future__ import annotations

from src.topic_page import render_topic_page
from src.ui_components import configure_page, render_sidebar

configure_page("LuxStats - Tourism")
render_sidebar()
render_topic_page("Tourism")
