from __future__ import annotations

from dotenv import load_dotenv

from src.salary_explorer import render_salaries_page
from src.ui_components import configure_page, mirror_streamlit_secrets, render_sidebar

load_dotenv()
mirror_streamlit_secrets()
configure_page("LuxStats - Salaries")
render_sidebar()
render_salaries_page()
