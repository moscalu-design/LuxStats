from __future__ import annotations

import streamlit as st
from dotenv import load_dotenv

from src.salary_explorer import render_salaries_page
from src.topic_page import render_topic_page
from src.ui_components import configure_page, mirror_streamlit_secrets, render_sidebar

load_dotenv()
mirror_streamlit_secrets()
configure_page("LuxStats - Salaries")
render_sidebar()

# Normal visitors get the curated salary charts straight away.
render_topic_page("Salaries")

# Power users can opt in to the raw dataset explorer. It is off by default so
# the page (and the sidebar) stays clean for everyone else.
st.divider()
with st.container(border=True):
    st.markdown("#### 🔧 Advanced: salary data explorer")
    st.caption(
        "For power users: browse raw STATEC / LUSTAT salary datasets, run a "
        "deterministic grouped query, and export the underlying data."
    )
    if st.toggle("Open the advanced salary explorer", value=False, key="salary_advanced"):
        render_salaries_page()
