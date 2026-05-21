from __future__ import annotations

import pandas as pd
import streamlit as st

from src.data.file_ingestion import (
    cached_file_path,
    download_source_file,
    inspect_excel_file,
    is_file_cached,
    preview_excel_sheet,
)
from src.data.source_catalog import (
    SOURCE_TYPES,
    catalog_generated_at,
    load_unified_source_catalog,
    search_source_catalog,
)
from src.ui_components import configure_page, page_hero, render_sidebar, section_header

configure_page("LuxStats - Source Library")
render_sidebar()


@st.cache_data(ttl=3600, show_spinner=False)
def _catalog() -> list[dict]:
    return load_unified_source_catalog()


page_hero(
    "Source Library",
    "Browse the official STATEC / LUSTAT sources connected to this portal",
    "Every official source the portal knows about — LUSTAT API datasets, "
    "STATEC Excel tables, and publication annexes — categorized and searchable "
    "in one place. This is an advanced page; most visitors should start from "
    "Find a Statistic or the topic pages.",
)

records = _catalog()
if not records:
    st.warning(
        "The source catalog has not been built yet. A maintainer can build it "
        "by running `python scripts/refresh_source_catalog.py` and committing "
        "the generated files in `data/catalog/`."
    )
    st.stop()

generated = catalog_generated_at()
st.caption(f"{len(records):,} sources cataloged"
           + (f" · last refreshed {generated}" if generated else ""))

# --- Filters --------------------------------------------------------------
categories = ["All"] + sorted({r["category"] for r in records if r.get("category")})
families = ["All"] + sorted({r["publication_family"] for r in records
                             if r.get("publication_family")})
file_types = ["All"] + sorted({r["file_type"] for r in records if r.get("file_type")})

query = st.text_input(
    "Search sources",
    placeholder="housing prices · salaries by commune · inflation · tourism…",
)

row1 = st.columns(3)
with row1[0]:
    category = st.selectbox("Category", categories)
with row1[1]:
    source_type = st.selectbox("Source type", ["All"] + SOURCE_TYPES)
with row1[2]:
    geo = st.selectbox("Geographic level",
                       ["All", "national", "commune", "canton", "region", "unknown"])
row2 = st.columns(3)
with row2[0]:
    priority = st.selectbox("Priority", ["All", "high", "medium", "low"])
with row2[1]:
    family = st.selectbox("Publication family", families)
with row2[2]:
    file_type = st.selectbox("File type", file_types)
row3 = st.columns(2)
with row3[0]:
    rec_portal = st.checkbox("Recommended for the portal only")
with row3[1]:
    rec_commune = st.checkbox("Commune-level only")

filters = {
    "category": category,
    "source_type": source_type,
    "geographic_level": geo,
    "priority": priority,
    "publication_family": family,
    "file_type": file_type,
    "recommended_for_portal": rec_portal,
    "recommended_for_commune_portal": rec_commune,
}
results = search_source_catalog(query, filters, records=records)

# --- Results table --------------------------------------------------------
section_header(f"{len(results):,} matching source(s)")
if not results:
    st.info("No sources match these filters. Try a broader search or reset the "
            "filters above.")
    st.stop()

table = pd.DataFrame([
    {
        "Title": r["title"],
        "Category": r["category"],
        "Type": r["source_type"],
        "Geography": r["geographic_level"],
        "Priority": r["priority"],
    }
    for r in results[:500]
])
st.dataframe(table, use_container_width=True, hide_index=True)
if len(results) > 500:
    st.caption("Showing the first 500 rows — narrow the filters to see the rest.")

# --- Source detail --------------------------------------------------------
section_header("Source details", "Open one source for advanced details.")
options = results[:500]
chosen = st.selectbox(
    "Open a source",
    options,
    format_func=lambda r: f"[{r['source_type']}] {r['title']}",
)

if chosen is not None:
    with st.container(border=True):
        st.markdown(f"#### {chosen['title']}")
        st.markdown(
            f"<span class='lux-tag'>{chosen['category']}</span> "
            f"<span class='lux-tag'>{chosen['source_type']}</span> "
            f"<span class='lux-muted'>{chosen['geographic_level']} · "
            f"priority: {chosen['priority']}</span>",
            unsafe_allow_html=True,
        )
        if chosen.get("description"):
            st.caption(chosen["description"])
        if chosen.get("source_page_url"):
            st.markdown(f"🔗 [Source page]({chosen['source_page_url']})")
        if chosen.get("file_url"):
            st.markdown(f"📄 [Data file]({chosen['file_url']})")
        if chosen.get("api_url"):
            st.markdown(f"🔌 [API endpoint]({chosen['api_url']})")

        if chosen["source_type"] == "LUSTAT_API":
            st.caption(f"Dataset ID: `{chosen['dataset_id']}`")

        # File inspection for Excel / other-format sources.
        if chosen.get("file_url") and chosen["source_type"] in {
            "STATEC_EXCEL", "OTHER_FORMAT", "PUBLICATION_EXCEL",
        }:
            cached = is_file_cached(chosen)
            st.caption(f"Local cache: {'downloaded' if cached else 'not downloaded yet'}")
            cols = st.columns(2)
            if cols[0].button("⬇︎ Download / cache this file", key="dl_source"):
                try:
                    with st.spinner("Downloading from STATEC…"):
                        download_source_file(chosen)
                    st.success("File cached.")
                    st.rerun()
                except Exception as exc:  # noqa: BLE001
                    st.error(f"Download failed: {exc}")
            if cached and cols[1].button("🔍 Inspect sheets", key="inspect_source"):
                st.session_state["inspect_source_id"] = chosen["source_id"]

            if cached and st.session_state.get("inspect_source_id") == chosen["source_id"]:
                info = inspect_excel_file(cached_file_path(chosen))
                st.markdown(f"**Status:** `{info['status']}` — {info['notes']}")
                st.markdown(f"**Sheets ({info['sheet_count']}):** "
                            + ", ".join(info["sheet_names"]) or "—")
                if info["detected_communes"]:
                    st.markdown(f"**Communes detected:** {len(info['detected_communes'])}")
                if info["sheet_names"]:
                    sheet = st.selectbox("Preview a sheet", info["sheet_names"])
                    preview = preview_excel_sheet(cached_file_path(chosen), sheet)
                    if preview.empty:
                        st.info("This sheet could not be previewed.")
                    else:
                        st.dataframe(preview, use_container_width=True, hide_index=True)

        with st.expander("Advanced details (raw catalog record)"):
            st.json(chosen)

        if chosen.get("priority_reason"):
            st.caption(f"Priority reasoning: {chosen['priority_reason']} "
                       f"(score {chosen.get('priority_score', 0)})")
