from __future__ import annotations

import pandas as pd
import streamlit as st

from src.data.source_catalog import (
    SOURCE_TYPES,
    catalog_generated_at,
    load_unified_source_catalog,
    search_source_catalog,
)
from src.data.source_mapping import enrich_with_mapping_status, high_priority_unmapped, source_coverage
from src.data.source_visualization import load_source_visualization_index, visualization_summary
from src.ui.page_header import render_page_header
from src.ui.source_visualizer import (
    readiness_dataframe,
    readiness_options,
    render_source_card,
    render_universal_source_viewer,
    render_visualization_summary,
    status_label,
)
from src.ui_components import configure_page, render_sidebar, section_header

configure_page("LuxStats - Source Library")
render_sidebar()


@st.cache_data(ttl=3600, show_spinner=False)
def _catalog() -> list[dict]:
    return load_unified_source_catalog()


@st.cache_data(ttl=3600, show_spinner=False)
def _readiness() -> list[dict]:
    return load_source_visualization_index()


render_page_header("source_library", eyebrow="Advanced")

records = enrich_with_mapping_status(_catalog())
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
readiness_rows = _readiness()
readiness_by_id = {row["source_id"]: row for row in readiness_rows}
records_by_id = {row["source_id"]: row for row in records}

coverage = source_coverage()
with st.container(border=True):
    st.markdown("#### Catalog readiness")
    cols = st.columns(5)
    cols[0].metric("Sources", f"{coverage['total']:,}")
    cols[1].metric("Chart-ready", f"{coverage['chart_ready']:,}")
    cols[2].metric("Commune-ready", f"{coverage['commune_ready']:,}")
    cols[3].metric("Publication annexes", f"{coverage['publication_annexes']:,}")
    cols[4].metric("Needs mapping", f"{coverage['unmapped_high_priority']:,}")

render_visualization_summary(readiness_rows)

quick_cols = st.columns(3)
with quick_cols[0]:
    if st.button("Show chart-ready sources", use_container_width=True):
        st.session_state["source_status_filter"] = "chart_ready"
with quick_cols[1]:
    if st.button("Show sources needing mapping", use_container_width=True):
        st.session_state["source_status_filter"] = "needs_column_mapping"
with quick_cols[2]:
    if st.button("Show manual-review sources", use_container_width=True):
        st.session_state["source_status_filter"] = "needs_manual_review"

chart_ready_top = [row for row in readiness_rows if row["visualization_status"] == "chart_ready"][:6]
needs_mapping_top = [
    row for row in readiness_rows
    if row["priority"] == "high"
    and row["visualization_status"] in {"needs_column_mapping", "needs_excel_inspection", "needs_manual_review"}
][:6]
if chart_ready_top or needs_mapping_top:
    left, right = st.columns(2)
    with left:
        section_header("Open chart-ready sources")
        for row in chart_ready_top[:3]:
            record = records_by_id.get(row["source_id"], row)
            if render_source_card(record, row, key=f"open_ready_{row['source_id']}"):
                st.session_state["selected_source_id"] = row["source_id"]
    with right:
        section_header("Recommended mapping queue")
        for row in needs_mapping_top[:3]:
            record = records_by_id.get(row["source_id"], row)
            if render_source_card(record, row, key=f"open_mapping_{row['source_id']}"):
                st.session_state["selected_source_id"] = row["source_id"]

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
row4 = st.columns(2)
with row4[0]:
    mapping_status = st.selectbox(
        "Mapping status",
        ["All", "mapped_to_metric", "mapped_to_commune_portal", "unmapped", "needs_manual_review", "ignored_low_priority"],
    )
with row4[1]:
    show_count = st.selectbox("Rows to show", [50, 100, 250, 500], index=1)
row5 = st.columns(2)
status_default = st.session_state.pop("source_status_filter", "All")
with row5[0]:
    visualization_status = st.selectbox(
        "Visualization readiness",
        readiness_options(),
        index=readiness_options().index(status_default) if status_default in readiness_options() else 0,
    )
with row5[1]:
    sort_mode = st.selectbox(
        "Sort by",
        ["Chart-ready first", "High priority first", "Source type", "Category"],
    )

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
results = enrich_with_mapping_status(search_source_catalog(query, filters, records=records))
if mapping_status != "All":
    results = [record for record in results if record.get("mapping_status") == mapping_status]
if visualization_status != "All":
    results = [
        record for record in results
        if readiness_by_id.get(record["source_id"], {}).get("visualization_status") == visualization_status
    ]

def _sort_key(record: dict) -> tuple:
    ready = readiness_by_id.get(record["source_id"], {})
    status = ready.get("visualization_status", "")
    if sort_mode == "High priority first":
        return (-int(record.get("priority_score") or 0), record.get("title", ""))
    if sort_mode == "Source type":
        return (record.get("source_type", ""), record.get("title", ""))
    if sort_mode == "Category":
        return (record.get("category", ""), record.get("title", ""))
    return (
        status != "chart_ready",
        status != "preview_ready",
        -int(record.get("priority_score") or 0),
        record.get("title", ""),
    )

results = sorted(results, key=_sort_key)

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
        "Readiness": status_label(readiness_by_id.get(r["source_id"], {}).get("visualization_status", "")),
        "Action": readiness_by_id.get(r["source_id"], {}).get("recommended_action", ""),
        "Geography": r["geographic_level"],
        "Priority": r["priority"],
        "Mapping": r["mapping_status"],
        "Chart-ready": "Yes" if r.get("chart_ready") else "",
        "Commune": "Yes" if r.get("commune_portal_ready") else "",
    }
    for r in results[:show_count]
])
st.dataframe(table, use_container_width=True, hide_index=True)
if len(results) > show_count:
    st.caption(f"Showing the first {show_count} rows — narrow the filters to see the rest.")

with st.expander("Recommended next mappings", expanded=False):
    st.caption("High-priority official sources that are not yet mapped to a chart or commune profile.")
    todos = high_priority_unmapped(limit=12)
    if not todos:
        st.success("No high-priority unmapped source is currently flagged.")
    else:
        todo_table = pd.DataFrame(
            {
                "Title": item["title"],
                "Category": item["category"],
                "Type": item["source_type"],
                "Geography": item["geographic_level"],
                "Reason": item.get("priority_reason", ""),
            }
            for item in todos
        )
        st.dataframe(todo_table, use_container_width=True, hide_index=True)

with st.expander("Full readiness table", expanded=False):
    st.caption("Paginated advanced view of the visualization index, not a charting promise.")
    st.dataframe(readiness_dataframe([readiness_by_id[r["source_id"]] for r in results[:show_count] if r["source_id"] in readiness_by_id]), use_container_width=True, hide_index=True)

# --- Source detail --------------------------------------------------------
section_header("Universal source viewer", "Open one source for its safest available experience.")
options = results[:show_count]
selected_source_id = st.session_state.get("selected_source_id")
default_index = 0
if selected_source_id:
    default_index = next((idx for idx, row in enumerate(options) if row["source_id"] == selected_source_id), 0)
chosen = st.selectbox(
    "Open a source",
    options,
    format_func=lambda r: f"[{r['source_type']}] {r['title']}",
    index=default_index if options else None,
)

if chosen is not None:
    st.session_state["selected_source_id"] = chosen["source_id"]
    readiness = readiness_by_id.get(chosen["source_id"], {})
    render_universal_source_viewer(chosen, readiness, key_prefix=f"source_{chosen['source_id']}")
