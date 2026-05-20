"""Shared page helpers for curated dashboards."""

from __future__ import annotations

import streamlit as st

from src.catalog import search_catalog


def dashboard_placeholder(title: str, intro: str, examples: list[str], catalog_theme: str | None = None) -> None:
    catalog_theme = catalog_theme or title
    st.title(title)
    st.write(intro)
    st.info(
        "This dashboard is wired into the portal structure. The next step is to confirm the official LUSTAT dataset IDs "
        "for this theme, then connect the filters and charts below to cached data."
    )
    st.subheader("Planned views")
    for example in examples:
        st.write(f"- {example}")
    with st.expander("Candidate catalog entries", expanded=True):
        df = search_catalog(theme=catalog_theme)
        if df.empty:
            st.warning("No curated catalog entries are configured for this dashboard yet.")
            return
        columns = ["friendly_title", "description", "dataset_id", "dimensions", "keywords", "notes"]
        st.dataframe(df[columns], use_container_width=True, hide_index=True)
