"""Reusable Streamlit UI components.

The visual design system lives in :mod:`src.ui.theme`. This module wires it
into page setup and keeps a few small shared widgets (source notice, CSV
download). New components belong in :mod:`src.ui`.
"""

from __future__ import annotations

import os
from html import escape
from collections.abc import Mapping
from typing import Any

import pandas as pd
import streamlit as st

from src.config import APP_TITLE, STATEC_SOURCE
from src.ui.layout import render_app_sidebar
from src.ui.theme import empty_state, inject_theme, section_header, trust_note

__all__ = [
    "mirror_streamlit_secrets",
    "configure_page",
    "inject_style",
    "render_sidebar",
    "section_header",
    "empty_state",
    "trust_note",
    "page_hero",
    "status_panel",
    "caveat_panel",
    "data_source_info",
    "what_box",
    "download_csv",
    "render_topic_cards",
]


def mirror_streamlit_secrets() -> None:
    """Reserved hook for non-sensitive Streamlit Cloud configuration."""
    try:
        # The app is intentionally deterministic and does not mirror API keys.
        # Keep this hook so older deployments that import it do not break.
        os.environ.setdefault("LUXSTATS_STREAMLIT", "1")
    except Exception:
        pass


def configure_page(title: str = APP_TITLE) -> None:
    """Standard page setup: metadata + LuxStats design system."""
    st.set_page_config(page_title=title, page_icon="📊", layout="wide")
    inject_theme()


def inject_style() -> None:
    """Backwards-compatible alias for :func:`src.ui.theme.inject_theme`."""
    inject_theme()


def render_sidebar() -> None:
    render_app_sidebar()


def render_topic_cards(cards: list[Mapping[str, str]]) -> None:
    """Legacy topic-card grid kept for backwards compatibility."""
    cols = st.columns(min(3, len(cards)) or 1)
    for col, card in zip(cols, cards):
        with col:
            with st.container(border=True):
                icon = card.get("icon", "")
                st.markdown(f"**{icon} {card['title']}**".strip())
                st.caption(card["description"])


def page_hero(kicker: str, title: str, body: str) -> None:
    """Legacy hero block; new pages use src.ui.page_header."""
    st.markdown(
        f"""
        <section class="lux-hero">
            <div class="lux-kicker">{escape(kicker)}</div>
            <h1>{escape(title)}</h1>
            <p>{escape(body)}</p>
        </section>
        """,
        unsafe_allow_html=True,
    )


def status_panel(title: str, items: list[tuple[str, str, str]]) -> None:
    rows = []
    for marker, heading, body in items:
        rows.append(
            f"""
            <div class="lux-status-row">
                <div class="lux-status-icon">{escape(marker)}</div>
                <div><strong>{escape(heading)}</strong><span>{escape(body)}</span></div>
            </div>
            """
        )
    st.markdown(
        f"""
        <div class="lux-status-panel">
            <h3>{escape(title)}</h3>
            {''.join(rows)}
        </div>
        """,
        unsafe_allow_html=True,
    )


def caveat_panel(body: str) -> None:
    st.markdown(f"""<div class="lux-caveat">{escape(body)}</div>""", unsafe_allow_html=True)


def data_source_info(
    *,
    dataset_name: str,
    dataset_id: str,
    source: str = STATEC_SOURCE,
    latest_period: str | None = None,
    last_fetched: Any = None,
    row_count: int | None = None,
    columns: list[str] | None = None,
    notes: str | None = None,
) -> None:
    size_bits = []
    if row_count is not None:
        size_bits.append(f"{row_count:,} rows")
    if columns:
        size_bits.append(f"{len(columns):,} columns")
    size_text = f"<br>{' · '.join(size_bits)}" if size_bits else ""
    st.markdown(
        f"""
        <div class="lux-source">
            <strong>{escape(dataset_name)}</strong><br>
            Dataset ID: <code>{escape(dataset_id)}</code> · Source: {escape(source)}<br>
            Latest available period: {escape(str(latest_period or "Not loaded yet"))}
            · Last fetched: {escape(str(last_fetched or "Not cached yet"))}
            {size_text}
        </div>
        """,
        unsafe_allow_html=True,
    )
    if notes:
        with st.expander("Source details and caveats", expanded=False):
            st.write(notes)


def what_box(title: str, body: str) -> None:
    st.info(f"**{title}**\n\n{body}")


def download_csv(
    df: pd.DataFrame,
    file_name: str,
    label: str = "Download the data (CSV)",
    key: str | None = None,
) -> None:
    if df is None or df.empty:
        st.caption("No downloadable rows are available for this view yet.")
        return
    st.download_button(
        label,
        data=df.to_csv(index=False).encode("utf-8"),
        file_name=file_name,
        mime="text/csv",
        key=key or f"dl_{file_name}",
    )
