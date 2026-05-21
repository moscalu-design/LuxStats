from __future__ import annotations

import streamlit as st

from src.cache import list_cached_datasets
from src.ui.page_header import render_page_header
from src.ui_components import configure_page, render_sidebar

configure_page("LuxStats - About Data")
render_sidebar()

render_page_header("about")
st.write(
    "LuxStats uses official data from STATEC / LUSTAT. Downloaded datasets are cached locally in DuckDB and CSV files "
    "so the app does not refetch the same data unnecessarily."
)

st.subheader("Cached datasets")
cached = list_cached_datasets()
if cached.empty:
    st.info("No datasets are cached yet.")
else:
    st.dataframe(cached, use_container_width=True, hide_index=True)

st.subheader("How to read the pages")
st.write("- Beginner mode shows friendly filters, charts, and explanations first.")
st.write("- Source details and technical codes stay inside expanders where possible.")
st.write("- Placeholder catalog IDs beginning with TODO_CONFIRM need confirmation against LUSTAT before dashboard wiring.")
