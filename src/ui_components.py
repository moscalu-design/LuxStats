"""Reusable Streamlit UI components."""

from __future__ import annotations

import os
from collections.abc import Mapping
from typing import Any

import pandas as pd
import streamlit as st

from src.config import APP_TAGLINE, APP_TITLE, STATEC_SOURCE


def mirror_streamlit_secrets() -> None:
    """Expose Streamlit Cloud secrets as env vars for optional integrations."""
    try:
        for key in ("ANTHROPIC_API_KEY", "ANTHROPIC_MODEL"):
            if key in st.secrets and not os.environ.get(key):
                os.environ[key] = str(st.secrets[key])
    except Exception:
        pass


def configure_page(title: str = APP_TITLE) -> None:
    st.set_page_config(page_title=title, page_icon="📊", layout="wide")
    inject_style()


def inject_style() -> None:
    st.markdown(
        """
        <style>
        .block-container {padding-top: 2rem; padding-bottom: 3rem;}
        div[data-testid="stMetric"] {
            background: #f7f9fb;
            border: 1px solid #e3e8ef;
            border-radius: 8px;
            padding: 0.75rem 0.9rem;
        }
        .lux-card {
            border: 1px solid #e3e8ef;
            border-radius: 8px;
            padding: 1rem;
            background: #ffffff;
            min-height: 132px;
        }
        .lux-card h3 {font-size: 1.05rem; margin: 0 0 .35rem 0;}
        .lux-muted {color: #5f6b7a;}
        .lux-source {
            border-left: 4px solid #6b8f71;
            background: #f7faf7;
            padding: .85rem 1rem;
            border-radius: 6px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar() -> None:
    st.sidebar.title("LuxStats")
    st.sidebar.caption(APP_TAGLINE)
    st.sidebar.markdown("---")
    st.sidebar.caption("Use the page list above to move between dashboards.")


def render_topic_cards(cards: list[Mapping[str, str]]) -> None:
    cols = st.columns(3)
    for idx, card in enumerate(cards):
        with cols[idx % 3]:
            st.markdown(
                f"""
                <div class="lux-card">
                    <h3>{card.get("icon", "")} {card["title"]}</h3>
                    <p class="lux-muted">{card["description"]}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )


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
            <strong>{dataset_name}</strong><br>
            Dataset ID: <code>{dataset_id}</code> · Source: {source}<br>
            Latest available period: {latest_period or "Not loaded yet"} · Last fetched: {last_fetched or "Not cached yet"}
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


def download_csv(df: pd.DataFrame, file_name: str, label: str = "Download the data") -> None:
    st.download_button(
        label,
        data=df.to_csv(index=False).encode("utf-8"),
        file_name=file_name,
        mime="text/csv",
    )
