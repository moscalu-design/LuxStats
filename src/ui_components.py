"""Reusable Streamlit UI components."""

from __future__ import annotations

import os
from html import escape
from collections.abc import Mapping
from typing import Any

import pandas as pd
import streamlit as st

from src.config import APP_TAGLINE, APP_TITLE, STATEC_SOURCE
from src.ui.layout import render_app_sidebar


def mirror_streamlit_secrets() -> None:
    """Reserved hook for non-sensitive Streamlit Cloud configuration."""
    try:
        # The app is intentionally deterministic and does not mirror API keys.
        # Keep this hook so older deployments that import it do not break.
        os.environ.setdefault("LUXSTATS_STREAMLIT", "1")
    except Exception:
        pass


def configure_page(title: str = APP_TITLE) -> None:
    st.set_page_config(page_title=title, page_icon="📊", layout="wide")
    inject_style()


def inject_style() -> None:
    st.markdown(
        """
        <style>
        :root {
            --lux-ink: #1f2933;
            --lux-muted: #5f6b7a;
            --lux-line: #dfe6ee;
            --lux-soft: #f7f9fb;
            --lux-blue: #255f85;
            --lux-green: #557a5f;
            --lux-gold: #9a6a16;
        }
        .block-container {padding-top: 1.35rem; padding-bottom: 2.4rem; max-width: 1120px;}
        h1, h2, h3 {color: var(--lux-ink);}
        h2 {font-size: 1.45rem;}
        h3 {font-size: 1.1rem;}
        section[data-testid="stSidebar"] {
            background: #fbfcfd;
            border-right: 1px solid var(--lux-line);
        }
        section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
            padding-top: 1rem;
        }
        section[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"] {
            min-height: 2rem;
            padding: .28rem .45rem;
            border-radius: 6px;
            font-size: .92rem;
        }
        section[data-testid="stSidebar"] a[aria-current="page"] {
            background: #edf3f7;
            color: var(--lux-blue);
            font-weight: 650;
        }
        .lux-sidebar-title {
            color: var(--lux-ink);
            font-size: 1.05rem;
            font-weight: 750;
            margin: .1rem 0 0 0;
        }
        .lux-sidebar-group {
            color: var(--lux-muted);
            font-size: .7rem;
            font-weight: 750;
            letter-spacing: .02em;
            text-transform: uppercase;
            margin: 1rem 0 .25rem 0;
        }
        div[data-testid="stMetric"] {
            background: var(--lux-soft);
            border: 1px solid var(--lux-line);
            border-radius: 8px;
            padding: .62rem .75rem;
        }
        .lux-hero {
            border: 1px solid var(--lux-line);
            border-radius: 8px;
            padding: clamp(.9rem, 2vw, 1.35rem);
            background: #ffffff;
            margin-bottom: 1rem;
        }
        .lux-kicker {
            color: var(--lux-blue);
            font-weight: 700;
            font-size: .82rem;
            letter-spacing: 0;
            text-transform: uppercase;
            margin-bottom: .25rem;
        }
        .lux-hero h1 {
            font-size: clamp(1.85rem, 4vw, 2.65rem);
            line-height: 1.08;
            margin: 0 0 .45rem 0;
        }
        .lux-hero p {
            color: var(--lux-muted);
            font-size: 1rem;
            line-height: 1.45;
            max-width: 760px;
            margin-bottom: 0;
        }
        .lux-page-header {
            border-bottom: 1px solid var(--lux-line);
            padding: 0 0 .75rem 0;
            margin-bottom: .85rem;
        }
        .lux-page-header h1 {
            font-size: clamp(1.6rem, 3vw, 2.35rem);
            line-height: 1.1;
            margin: 0 0 .3rem 0;
        }
        .lux-page-header p {
            color: var(--lux-muted);
            font-size: .98rem;
            line-height: 1.45;
            max-width: 820px;
            margin: 0;
        }
        .lux-card {
            border: 1px solid var(--lux-line);
            border-radius: 8px;
            padding: .78rem .85rem;
            background: #ffffff;
            min-height: 112px;
        }
        .lux-card h3 {font-size: 1rem; margin: 0 0 .25rem 0;}
        .lux-card p {line-height: 1.4;}
        .lux-muted {color: var(--lux-muted);}
        .lux-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: .7rem;
            margin: .25rem 0 .9rem 0;
        }
        .lux-topic-card {
            border: 1px solid var(--lux-line);
            border-radius: 8px;
            padding: .8rem .85rem;
            background: #ffffff;
            min-height: 126px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
        .lux-topic-card h3 {font-size: 1.02rem; margin: 0 0 .4rem 0;}
        .lux-topic-card p {color: var(--lux-muted); line-height: 1.45; margin: 0;}
        .lux-card-action {
            color: var(--lux-blue);
            font-weight: 700;
            margin-top: .65rem;
            font-size: .86rem;
        }
        .lux-source {
            border-left: 4px solid var(--lux-green);
            background: #f7faf7;
            padding: .85rem 1rem;
            border-radius: 6px;
        }
        .lux-status-panel {
            border: 1px solid var(--lux-line);
            border-radius: 8px;
            padding: 1rem;
            background: #ffffff;
            margin: .75rem 0 1rem 0;
        }
        .lux-status-panel h3 {font-size: 1rem; margin: 0 0 .5rem 0;}
        .lux-status-row {
            display: flex;
            gap: .65rem;
            align-items: flex-start;
            padding: .45rem 0;
            border-top: 1px solid #edf1f5;
        }
        .lux-status-row:first-of-type {border-top: 0;}
        .lux-status-icon {
            width: 1.5rem;
            height: 1.5rem;
            border-radius: 999px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            background: #eef5f8;
            color: var(--lux-blue);
            font-weight: 800;
            flex: 0 0 auto;
        }
        .lux-status-row strong {display: block; color: var(--lux-ink);}
        .lux-status-row span {color: var(--lux-muted); line-height: 1.4;}
        .lux-caveat {
            border-left: 4px solid var(--lux-gold);
            background: #fffaf0;
            border-radius: 6px;
            padding: .85rem 1rem;
            color: #3f3120;
        }
        .lux-tag {
            display: inline-block;
            background: #e8f0f4;
            color: var(--lux-blue);
            font-weight: 700;
            font-size: .66rem;
            text-transform: uppercase;
            letter-spacing: .02em;
            padding: .08rem .42rem;
            border-radius: 999px;
            margin-right: .32rem;
            vertical-align: middle;
        }
        .lux-status-chart-ready {background: #e9f4ee; color: #315f3f;}
        .lux-status-preview-ready {background: #edf3f8; color: #255f85;}
        .lux-status-downloadable-only {background: #f7f1df; color: #7b5513;}
        .lux-status-unresolved {background: #f1f3f5; color: #536171;}
        .lux-card-meta {
            color: var(--lux-muted);
            font-size: .8rem;
            line-height: 1.35;
            margin-top: .3rem;
        }
        .lux-howto {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: .65rem;
            margin: .25rem 0 .95rem 0;
        }
        .lux-howto-step {
            border: 1px solid var(--lux-line);
            border-radius: 8px;
            padding: .7rem .8rem;
            background: var(--lux-soft);
            min-height: 86px;
        }
        .lux-howto-step strong {
            display: block;
            font-size: .9rem;
            margin-bottom: .2rem;
        }
        .lux-howto-step span {
            color: var(--lux-muted);
            font-size: .84rem;
            line-height: 1.35;
        }
        .lux-explain {
            background: var(--lux-soft);
            border-radius: 8px;
            padding: .8rem 1rem;
            color: #3a4654;
            line-height: 1.5;
            margin: .7rem 0 .3rem 0;
            font-size: .95rem;
        }
        .lux-section-title {
            font-size: 1.18rem;
            font-weight: 700;
            color: var(--lux-ink);
            margin: 1.2rem 0 .12rem 0;
        }
        .lux-section-sub {
            color: var(--lux-muted);
            margin-bottom: .45rem;
            font-size: .92rem;
        }
        /* Make the search box feel like the front door of the app. */
        div[data-testid="stTextInput"] input {
            font-size: 1rem;
            padding: .55rem .75rem;
        }
        div[data-testid="stTextInput"] input:focus {
            border-color: var(--lux-blue);
        }
        /* Bordered containers used as cards. */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            border-radius: 10px;
        }
        @media (max-width: 760px) {
            .block-container {padding-left: 1rem; padding-right: 1rem;}
            .lux-grid, .lux-howto {grid-template-columns: 1fr;}
            .lux-hero {padding: 1rem;}
            .lux-hero p {font-size: 1rem;}
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar() -> None:
    render_app_sidebar()


def section_header(title: str, subtitle: str = "") -> None:
    """Consistent section heading used across the portal."""
    st.markdown(f"<div class='lux-section-title'>{escape(title)}</div>", unsafe_allow_html=True)
    if subtitle:
        st.markdown(f"<div class='lux-section-sub'>{escape(subtitle)}</div>", unsafe_allow_html=True)


def render_topic_cards(cards: list[Mapping[str, str]]) -> None:
    html_cards = []
    for card in cards:
        icon = escape(card.get("icon", ""))
        title = escape(card["title"])
        description = escape(card["description"])
        action = escape(card.get("action", "Open dashboard"))
        html_cards.append(
            f"""
            <div class="lux-topic-card">
                <div>
                    <h3>{icon} {title}</h3>
                    <p>{description}</p>
                </div>
                <div class="lux-card-action">{action}</div>
            </div>
            """
        )
    st.markdown(f"""<div class="lux-grid">{''.join(html_cards)}</div>""", unsafe_allow_html=True)


def page_hero(kicker: str, title: str, body: str) -> None:
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


def download_csv(
    df: pd.DataFrame,
    file_name: str,
    label: str = "Download the data",
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
