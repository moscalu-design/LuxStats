"""Reusable Streamlit UI components."""

from __future__ import annotations

import os
from html import escape
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
        :root {
            --lux-ink: #1f2933;
            --lux-muted: #5f6b7a;
            --lux-line: #dfe6ee;
            --lux-soft: #f7f9fb;
            --lux-blue: #255f85;
            --lux-green: #557a5f;
            --lux-gold: #9a6a16;
        }
        .block-container {padding-top: 2rem; padding-bottom: 3rem; max-width: 1180px;}
        h1, h2, h3 {color: var(--lux-ink);}
        div[data-testid="stMetric"] {
            background: var(--lux-soft);
            border: 1px solid var(--lux-line);
            border-radius: 8px;
            padding: 0.75rem 0.9rem;
        }
        .lux-hero {
            border: 1px solid var(--lux-line);
            border-radius: 8px;
            padding: clamp(1rem, 3vw, 2rem);
            background:
                linear-gradient(135deg, rgba(37, 95, 133, .10), rgba(85, 122, 95, .08)),
                #ffffff;
            margin-bottom: 1.25rem;
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
            font-size: clamp(2rem, 5vw, 3.4rem);
            line-height: 1.05;
            margin: 0 0 .65rem 0;
        }
        .lux-hero p {
            color: var(--lux-muted);
            font-size: 1.08rem;
            line-height: 1.55;
            max-width: 760px;
            margin-bottom: 0;
        }
        .lux-card {
            border: 1px solid var(--lux-line);
            border-radius: 8px;
            padding: 1rem;
            background: #ffffff;
            min-height: 132px;
        }
        .lux-card h3 {font-size: 1.05rem; margin: 0 0 .35rem 0;}
        .lux-card p {line-height: 1.45;}
        .lux-muted {color: var(--lux-muted);}
        .lux-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: .85rem;
            margin: .35rem 0 1.1rem 0;
        }
        .lux-topic-card {
            border: 1px solid var(--lux-line);
            border-radius: 8px;
            padding: 1rem;
            background: #ffffff;
            min-height: 154px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
        .lux-topic-card h3 {font-size: 1.02rem; margin: 0 0 .4rem 0;}
        .lux-topic-card p {color: var(--lux-muted); line-height: 1.45; margin: 0;}
        .lux-card-action {
            color: var(--lux-blue);
            font-weight: 700;
            margin-top: .9rem;
            font-size: .92rem;
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
        @media (max-width: 760px) {
            .block-container {padding-left: 1rem; padding-right: 1rem;}
            .lux-grid {grid-template-columns: 1fr;}
            .lux-hero {padding: 1rem;}
            .lux-hero p {font-size: 1rem;}
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar() -> None:
    st.sidebar.title("LuxStats")
    st.sidebar.caption(APP_TAGLINE)
    st.sidebar.markdown("---")
    st.sidebar.caption("Use the page list above to move between dashboards. Start with Salaries or Dataset Explorer for live LUSTAT data.")


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


def download_csv(df: pd.DataFrame, file_name: str, label: str = "Download the data") -> None:
    st.download_button(
        label,
        data=df.to_csv(index=False).encode("utf-8"),
        file_name=file_name,
        mime="text/csv",
    )
