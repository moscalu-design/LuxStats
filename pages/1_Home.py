from __future__ import annotations

from dotenv import load_dotenv

from src.home import render_home
from src.ui_components import configure_page, mirror_streamlit_secrets, render_sidebar

load_dotenv()
mirror_streamlit_secrets()
configure_page("LuxStats - Home")
render_sidebar()
render_home()
