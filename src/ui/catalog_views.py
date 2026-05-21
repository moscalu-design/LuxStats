"""Reusable views over the unified STATEC source catalog.

These render catalog records inside the existing product pages (Home, topic
pages, Commune Portal, What Changed) without exposing raw JSON.
"""

from __future__ import annotations

from typing import Any

import streamlit as st

from src.data.source_catalog import catalog_summary

_TYPE_LABEL = {
    "LUSTAT_API": "LUSTAT API",
    "STATEC_EXCEL": "STATEC Excel",
    "PUBLICATION_EXCEL": "Publication Excel",
    "PUBLICATION_PDF": "Publication PDF",
    "OTHER_FORMAT": "Other format",
}


def render_coverage_section() -> None:
    """Home-page 'data coverage' strip plus a link to the Source Library."""
    summary = catalog_summary()
    if not summary["total"]:
        with st.container(border=True):
            st.markdown("#### 🗂️ Data coverage")
            st.caption(
                "The STATEC source catalog has not been built on this "
                "deployment yet. A maintainer can run "
                "`python scripts/refresh_source_catalog.py`."
            )
            st.page_link("pages/13_Source_Library.py", label="Open the Source Library")
        return
    with st.container(border=True):
        st.markdown("#### 🗂️ Data coverage")
        st.caption("Official STATEC / LUSTAT sources this portal has cataloged.")
        cols = st.columns(4)
        cols[0].metric("LUSTAT API datasets", f"{summary['api']:,}")
        cols[1].metric("Excel data files", f"{summary['excel']:,}")
        cols[2].metric("Publication annexes", f"{summary['publications']:,}")
        cols[3].metric("Commune-level sources", f"{summary['commune_level']:,}")
        st.page_link("pages/13_Source_Library.py",
                     label="Explore all sources in the Source Library")


def render_source_records(
    records: list[dict[str, Any]],
    *,
    key_prefix: str,
    limit: int = 6,
    empty_message: str = "No matching official sources were cataloged.",
) -> None:
    """Render a compact, friendly list of source-catalog records."""
    if not records:
        st.caption(empty_message)
        return
    for record in records[:limit]:
        with st.container(border=True):
            st.markdown(
                f"<span class='lux-tag'>{record.get('category', '')}</span> "
                f"<span class='lux-tag'>{_TYPE_LABEL.get(record.get('source_type',''), record.get('source_type',''))}</span>",
                unsafe_allow_html=True,
            )
            st.markdown(f"**{record.get('title', 'Untitled source')}**")
            bits = []
            if record.get("publication_family"):
                bits.append(record["publication_family"])
            if record.get("publication_date"):
                bits.append(str(record["publication_date"]))
            if record.get("geographic_level") not in (None, "", "unknown"):
                bits.append(record["geographic_level"])
            if bits:
                st.caption(" · ".join(bits))
            links = []
            if record.get("file_url"):
                links.append(f"[Data file]({record['file_url']})")
            if record.get("api_url"):
                links.append(f"[API endpoint]({record['api_url']})")
            if record.get("source_page_url"):
                links.append(f"[Source page]({record['source_page_url']})")
            if links:
                st.markdown(" · ".join(links))
    remaining = len(records) - limit
    if remaining > 0:
        st.caption(f"+ {remaining} more — see the Source Library.")
        st.page_link("pages/13_Source_Library.py", label="Open the Source Library")
