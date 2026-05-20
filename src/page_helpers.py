"""Shared page helpers for curated dashboards."""

from __future__ import annotations

import streamlit as st

from src.catalog import search_catalog
from src.ui_components import caveat_panel, status_panel


def dashboard_placeholder(title: str, intro: str, examples: list[str], catalog_theme: str | None = None) -> None:
    catalog_theme = catalog_theme or title
    st.title(title)
    st.write(intro)
    status_panel(
        "Dashboard status",
        [
            ("1", "Page shell is ready", "Navigation, planned views, and catalog context are in place."),
            ("2", "Official IDs still need confirmation", "Candidate entries keep TODO_CONFIRM_* IDs until they are verified from LUSTAT metadata."),
            ("3", "Charts come after verification", "Once IDs are confirmed, this page can connect filters and charts to cached official data."),
        ],
    )
    caveat_panel(
        "No placeholder figures are shown here. This page will only chart official data after the relevant LUSTAT dataflow IDs are confirmed."
    )
    st.subheader("Planned views")
    for idx, example in enumerate(examples, start=1):
        st.write(f"{idx}. {example}")

    st.subheader("Candidate data sources")
    df = search_catalog(theme=catalog_theme)
    if df.empty:
        st.warning("No curated catalog entries are configured for this dashboard yet.")
        return

    for row in df.to_dict("records"):
        with st.expander(row["friendly_title"], expanded=True):
            st.write(row["description"])
            st.caption(f"Dataset ID: `{row['dataset_id']}` · Status: `{row['status']}`")
            if row["dimensions"]:
                st.write("Likely filters once confirmed: " + ", ".join(row["dimensions"]))
            if row["notes"]:
                st.caption(row["notes"])

    with st.expander("Catalog table", expanded=False):
        columns = ["friendly_title", "description", "dataset_id", "dimensions", "keywords", "notes"]
        st.dataframe(df[columns], use_container_width=True, hide_index=True)
