"""UI components for safely exploring any cataloged official source."""

from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st

from src.concept_view import render_concept
from src.concepts import get_concept
from src.data.file_ingestion import (
    cached_file_path,
    download_source_file,
    inspect_excel_file,
    is_file_cached,
    preview_excel_sheet,
)
from src.data.source_metric_mapper import mapping_template
from src.data.source_visualization import VISUALIZATION_STATUSES, visualization_summary
from src.ui_components import download_csv

STATUS_LABELS = {
    "chart_ready": "Chart ready",
    "preview_ready": "Preview ready",
    "downloadable_only": "Download only",
    "needs_column_mapping": "Needs mapping",
    "needs_excel_inspection": "Needs inspection",
    "needs_manual_review": "Manual review",
    "not_chartable": "Not chartable",
    "ignored_low_priority": "Low priority",
}


def status_label(status: str) -> str:
    return STATUS_LABELS.get(status, status.replace("_", " ").title())


def render_visualization_summary(rows: list[dict[str, Any]]) -> None:
    summary = visualization_summary(rows)
    with st.container(border=True):
        st.markdown("#### Visualization readiness")
        cols = st.columns(6)
        cols[0].metric("Sources", f"{summary['total']:,}")
        cols[1].metric("Chart-ready", f"{summary['chart_ready']:,}")
        cols[2].metric("Preview-ready", f"{summary['preview_ready']:,}")
        cols[3].metric("Needs mapping", f"{summary['needs_mapping']:,}")
        cols[4].metric("Manual review", f"{summary['needs_manual_review']:,}")
        cols[5].metric("Low priority", f"{summary['ignored_low_priority']:,}")


def render_status_badge(status: str) -> None:
    status_class = (
        f"lux-status-{status.replace('_', '-')}"
        if status in {"chart_ready", "preview_ready", "downloadable_only"}
        else "lux-status-unresolved"
    )
    st.markdown(
        f"<span class='lux-tag {status_class}'>{status_label(status)}</span>",
        unsafe_allow_html=True,
    )


def render_source_card(record: dict[str, Any], readiness: dict[str, Any], *, key: str) -> bool:
    """Render a compact source card. Return True when user asks to open it."""
    with st.container(border=True):
        st.markdown(
            f"<span class='lux-tag'>{record.get('category', '')}</span> "
            f"<span class='lux-tag'>{record.get('source_type', '')}</span> "
            f"<span class='lux-tag'>{status_label(readiness.get('visualization_status', ''))}</span>",
            unsafe_allow_html=True,
        )
        st.markdown(f"**{record.get('title', 'Untitled source')}**")
        st.caption(readiness.get("reason", "Official source catalog record."))
        cols = st.columns([2, 1])
        with cols[0]:
            st.caption(
                f"Priority: {record.get('priority', 'unknown')} · "
                f"Geography: {record.get('geographic_level', 'unknown')}"
            )
        with cols[1]:
            return st.button(
                readiness.get("recommended_action") or "Open source",
                key=key,
                use_container_width=True,
            )
    return False


def render_universal_source_viewer(record: dict[str, Any], readiness: dict[str, Any], *, key_prefix: str) -> None:
    """Render the safest available experience for one source."""
    with st.container(border=True):
        st.markdown(f"### {record.get('title', 'Official source')}")
        st.markdown(
            f"<span class='lux-tag'>{record.get('category', '')}</span> "
            f"<span class='lux-tag'>{record.get('source_type', '')}</span> "
            f"<span class='lux-tag'>{status_label(readiness.get('visualization_status', ''))}</span>",
            unsafe_allow_html=True,
        )
        st.caption(readiness.get("reason", "Official source catalog record."))
        st.caption(f"Recommended action: {readiness.get('recommended_action', 'Review source')}")

        status = readiness.get("visualization_status")
        if status == "chart_ready":
            _render_chart_ready(record, readiness, key_prefix)
        elif status in {"preview_ready", "needs_excel_inspection"}:
            _render_file_preview(record, readiness, key_prefix)
        elif status in {"needs_column_mapping", "needs_manual_review", "downloadable_only", "not_chartable", "ignored_low_priority"}:
            _render_mapping_guidance(record, readiness)

        _render_source_links(record)
        with st.expander("Advanced source record", expanded=False):
            st.json(record)
            st.json(readiness)


def _render_chart_ready(record: dict[str, Any], readiness: dict[str, Any], key_prefix: str) -> None:
    metric_id = readiness.get("mapped_metric_id")
    concept = get_concept(metric_id) if metric_id else None
    if concept:
        render_concept(concept, key=f"{key_prefix}_{metric_id}")
        return
    if readiness.get("chart_route_or_action", "").startswith("page:"):
        st.info("This source is chart-ready inside the Commune Portal or Compare page.")
        st.page_link("pages/3_Commune_Portal.py", label="Open Commune Portal", use_container_width=True)
        st.page_link("pages/4_Compare.py", label="Open Compare", use_container_width=True)
        return
    st.info("This source is marked chart-ready, but the chart route is not configured yet.")


def _render_file_preview(record: dict[str, Any], readiness: dict[str, Any], key_prefix: str) -> None:
    if not record.get("file_url"):
        st.info("No downloadable table file is attached to this source.")
        return
    cached = is_file_cached(record)
    if not cached:
        st.info("Download and inspect the official file before creating a chart mapping.")
        if st.button("Download official file", key=f"{key_prefix}_download"):
            try:
                with st.spinner("Downloading official source file..."):
                    download_source_file(record)
                st.success("File cached. Reopen this source to inspect sheets.")
            except Exception as exc:  # noqa: BLE001
                st.error("This source file could not be downloaded right now.")
                with st.expander("Advanced details", expanded=False):
                    st.code(str(exc))
        return

    info = inspect_excel_file(cached_file_path(record))
    st.markdown(f"**Inspection status:** {info.get('status', 'unknown')}")
    st.caption(info.get("notes", ""))
    sheets = info.get("sheet_names") or []
    if not sheets:
        st.info("This file could not be previewed as a table.")
        return
    sheet = st.selectbox("Preview sheet", sheets, key=f"{key_prefix}_sheet")
    preview = preview_excel_sheet(cached_file_path(record), sheet)
    if preview.empty:
        st.info("This sheet has no previewable rows.")
    else:
        st.dataframe(preview, use_container_width=True, hide_index=True)
        download_csv(preview, f"{record.get('source_id', 'source')}_preview.csv", "Download preview", key=f"{key_prefix}_preview_dl")
    with st.expander("Detected columns and mapping hints", expanded=False):
        st.json(info)


def _render_mapping_guidance(record: dict[str, Any], readiness: dict[str, Any]) -> None:
    status = readiness.get("visualization_status")
    if status == "needs_column_mapping":
        st.info("This API source is machine-readable, but LuxStats needs a confirmed column and filter mapping before charting it.")
    elif status == "needs_manual_review":
        st.info("This source needs manual review before it can become a chart. PDF-only sources are not charted automatically.")
    elif status == "ignored_low_priority":
        st.info("This source is searchable and official, but it is low priority for public dashboards.")
    elif status == "downloadable_only":
        st.info("This source can be opened or downloaded, but it is not safely previewable as a table yet.")
    else:
        st.info("This source is not chartable with the current metadata.")
    with st.expander("Mapping template", expanded=False):
        st.code(mapping_template(record), language="text")


def _render_source_links(record: dict[str, Any]) -> None:
    links = []
    if record.get("source_page_url"):
        links.append(f"[Source page]({record['source_page_url']})")
    if record.get("file_url"):
        links.append(f"[Official file]({record['file_url']})")
    if record.get("api_url"):
        links.append(f"[API endpoint]({record['api_url']})")
    if links:
        st.markdown(" · ".join(links))


def readiness_options() -> list[str]:
    return ["All"] + list(VISUALIZATION_STATUSES)


def readiness_dataframe(rows: list[dict[str, Any]]) -> pd.DataFrame:
    return pd.DataFrame([
        {
            "Title": row.get("title"),
            "Category": row.get("category"),
            "Type": row.get("source_type"),
            "Readiness": status_label(row.get("visualization_status", "")),
            "Action": row.get("recommended_action"),
            "Priority": row.get("priority"),
            "Geography": row.get("geographic_level"),
            "Reason": row.get("reason"),
        }
        for row in rows
    ])
