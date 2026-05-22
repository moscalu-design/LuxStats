"""Central design system for LuxStats.

Every colour, radius, spacing token and component style lives here so the whole
portal stays visually consistent. Pages should not ship their own CSS — they
import the reusable components in :mod:`src.ui` instead.

The look is deliberately restrained: an official statistics product, calm and
trustworthy, not a dashboard demo.
"""

from __future__ import annotations

from html import escape

import streamlit as st

# --------------------------------------------------------------------------
# Design tokens
# --------------------------------------------------------------------------
INK = "#1a2230"
MUTED = "#5b6776"
FAINT = "#8b95a4"
LINE = "#e5e9f0"
SOFT = "#f5f7fa"
BLUE = "#1f6f8b"
BLUE_DARK = "#185970"
GREEN = "#3f7d5a"
AMBER = "#9a6a16"

_STYLE = f"""
<style>
:root {{
    --lux-ink: {INK};
    --lux-muted: {MUTED};
    --lux-faint: {FAINT};
    --lux-line: {LINE};
    --lux-soft: {SOFT};
    --lux-blue: {BLUE};
    --lux-blue-dark: {BLUE_DARK};
    --lux-green: {GREEN};
    --lux-amber: {AMBER};
    --lux-radius: 12px;
    --lux-radius-sm: 8px;
}}

/* ---- Page canvas ----------------------------------------------------- */
.stApp {{ background: #ffffff; }}
.block-container {{
    padding-top: 1.6rem;
    padding-bottom: 3rem;
    max-width: 1080px;
}}
html, body, [class*="css"] {{
    font-feature-settings: "kern" 1, "liga" 1;
    -webkit-font-smoothing: antialiased;
}}

/* ---- Typography ------------------------------------------------------ */
h1, h2, h3, h4 {{ color: var(--lux-ink); letter-spacing: -0.01em; }}
h1 {{ font-size: 1.7rem; font-weight: 750; }}
h2 {{ font-size: 1.3rem; font-weight: 700; }}
h3 {{ font-size: 1.06rem; font-weight: 700; }}
h4 {{ font-size: 0.98rem; font-weight: 700; }}
p, li {{ color: var(--lux-ink); }}
a {{ color: var(--lux-blue); }}
.lux-muted {{ color: var(--lux-muted); }}

/* Hide Streamlit's default multipage auto-nav; LuxStats ships its own. */
div[data-testid="stSidebarNav"] {{ display: none; }}
/* Trim the default header chrome. */
header[data-testid="stHeader"] {{ background: transparent; }}
#MainMenu, footer {{ visibility: hidden; }}

/* ---- Sidebar --------------------------------------------------------- */
section[data-testid="stSidebar"] {{
    background: #fbfcfd;
    border-right: 1px solid var(--lux-line);
    width: 16rem !important;
}}
section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {{
    padding: 1.1rem 0.9rem;
}}
.lux-brand {{
    font-size: 1.16rem;
    font-weight: 800;
    color: var(--lux-ink);
    letter-spacing: -0.02em;
    margin: 0;
}}
.lux-brand-sub {{
    font-size: 0.72rem;
    color: var(--lux-faint);
    margin: 0.05rem 0 0.55rem 0;
}}
.lux-nav-group {{
    color: var(--lux-faint);
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.07em;
    text-transform: uppercase;
    margin: 1.15rem 0 0.25rem 0.15rem;
}}
section[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"] {{
    min-height: 1.95rem;
    padding: 0.26rem 0.5rem;
    border-radius: var(--lux-radius-sm);
    font-size: 0.9rem;
    color: var(--lux-ink);
}}
section[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"]:hover {{
    background: #eef2f6;
}}
section[data-testid="stSidebar"] a[aria-current="page"] {{
    background: #e8f1f5;
    color: var(--lux-blue-dark);
    font-weight: 650;
}}
section[data-testid="stSidebar"] [data-testid="stExpander"] {{
    border: none;
    box-shadow: none;
}}
section[data-testid="stSidebar"] [data-testid="stExpander"] summary {{
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.07em;
    text-transform: uppercase;
    color: var(--lux-faint);
    padding-left: 0.15rem;
}}
.lux-sidebar-foot {{
    color: var(--lux-faint);
    font-size: 0.72rem;
    line-height: 1.4;
    margin-top: 1.3rem;
    padding-top: 0.7rem;
    border-top: 1px solid var(--lux-line);
}}

/* ---- Hero ------------------------------------------------------------ */
.lux-hero {{
    padding: 0.4rem 0 0.7rem 0;
    margin-bottom: 0.5rem;
}}
.lux-hero h1 {{
    font-size: clamp(1.8rem, 3.4vw, 2.3rem);
    font-weight: 800;
    line-height: 1.12;
    margin: 0 0 0.35rem 0;
}}
.lux-hero p {{
    color: var(--lux-muted);
    font-size: 1.02rem;
    line-height: 1.5;
    max-width: 640px;
    margin: 0;
}}

/* ---- Page header ----------------------------------------------------- */
.lux-page-header {{
    padding: 0 0 0.7rem 0;
    margin-bottom: 1rem;
    border-bottom: 1px solid var(--lux-line);
}}
.lux-kicker {{
    color: var(--lux-blue);
    font-weight: 700;
    font-size: 0.72rem;
    letter-spacing: 0.07em;
    text-transform: uppercase;
    margin-bottom: 0.3rem;
}}
.lux-page-header h1 {{
    font-size: 1.62rem;
    font-weight: 780;
    line-height: 1.15;
    margin: 0 0 0.25rem 0;
}}
.lux-page-header p {{
    color: var(--lux-muted);
    font-size: 0.96rem;
    line-height: 1.45;
    max-width: 720px;
    margin: 0;
}}

/* ---- Section headers ------------------------------------------------- */
.lux-section {{
    margin: 1.5rem 0 0.15rem 0;
}}
.lux-section-title {{
    font-size: 1.12rem;
    font-weight: 700;
    color: var(--lux-ink);
    margin: 0;
}}
.lux-section-sub {{
    color: var(--lux-muted);
    font-size: 0.9rem;
    margin: 0.1rem 0 0.55rem 0;
}}

/* ---- Cards ----------------------------------------------------------- */
div[data-testid="stVerticalBlockBorderWrapper"] {{
    border-radius: var(--lux-radius);
}}
div[data-testid="stVerticalBlockBorderWrapper"] > div {{
    border-color: var(--lux-line) !important;
}}
.lux-card, .lux-topic-card {{
    border: 1px solid var(--lux-line);
    border-radius: var(--lux-radius);
    padding: 0.95rem 1rem;
    background: #ffffff;
}}
.lux-card h3, .lux-topic-card h3 {{
    font-size: 1rem;
    margin: 0 0 0.3rem 0;
}}
.lux-card p, .lux-topic-card p {{
    color: var(--lux-muted);
    line-height: 1.45;
    margin: 0;
    font-size: 0.9rem;
}}
.lux-card-meta {{
    color: var(--lux-faint);
    font-size: 0.78rem;
    line-height: 1.35;
    margin-top: 0.3rem;
}}

/* ---- Tiles (homepage topic / tool grid) ------------------------------ */
.lux-tile {{
    border: 1px solid var(--lux-line);
    border-radius: var(--lux-radius);
    padding: 0.95rem 1rem;
    background: #ffffff;
    height: 100%;
}}
.lux-tile-icon {{ font-size: 1.2rem; line-height: 1; }}
.lux-tile h4 {{ margin: 0.35rem 0 0.2rem 0; font-size: 0.98rem; }}
.lux-tile p {{
    color: var(--lux-muted);
    font-size: 0.85rem;
    line-height: 1.4;
    margin: 0;
}}

/* ---- Badges / tags --------------------------------------------------- */
.lux-tag {{
    display: inline-block;
    background: #eef2f6;
    color: var(--lux-muted);
    font-weight: 700;
    font-size: 0.66rem;
    text-transform: uppercase;
    letter-spacing: 0.03em;
    padding: 0.1rem 0.45rem;
    border-radius: 999px;
    margin: 0 0.3rem 0.1rem 0;
    vertical-align: middle;
}}
.lux-status-chart-ready, .lux-status-chart_ready {{ background: #e7f2ec; color: #2f6647; }}
.lux-status-preview-ready, .lux-status-preview_ready {{ background: #e8f1f6; color: var(--lux-blue-dark); }}
.lux-status-downloadable-only, .lux-status-downloadable_only {{ background: #f6efdc; color: #7b5513; }}
.lux-status-unresolved {{ background: #eef0f2; color: #586577; }}

/* ---- Notices: source, caveat, explanation ---------------------------- */
.lux-source {{
    border-left: 3px solid var(--lux-green);
    background: #f4f9f5;
    padding: 0.7rem 0.9rem;
    border-radius: var(--lux-radius-sm);
    font-size: 0.9rem;
    color: #33433a;
}}
.lux-caveat {{
    border-left: 3px solid var(--lux-amber);
    background: #fdf8ec;
    border-radius: var(--lux-radius-sm);
    padding: 0.7rem 0.9rem;
    color: #4a3c22;
    font-size: 0.9rem;
}}
.lux-explain {{
    background: var(--lux-soft);
    border-radius: var(--lux-radius-sm);
    padding: 0.8rem 1rem;
    color: #3a4654;
    line-height: 1.55;
    margin: 0.6rem 0 0.2rem 0;
    font-size: 0.93rem;
}}
.lux-trust {{
    border: 1px solid var(--lux-line);
    border-radius: var(--lux-radius);
    background: var(--lux-soft);
    padding: 0.95rem 1.1rem;
}}
.lux-trust strong {{ color: var(--lux-ink); }}
.lux-trust p {{
    color: var(--lux-muted);
    font-size: 0.88rem;
    line-height: 1.5;
    margin: 0.25rem 0 0 0;
}}

/* ---- Empty states ---------------------------------------------------- */
.lux-empty {{
    border: 1px dashed var(--lux-line);
    border-radius: var(--lux-radius);
    background: var(--lux-soft);
    padding: 1.1rem 1.2rem;
    color: var(--lux-muted);
    font-size: 0.92rem;
    line-height: 1.5;
}}
.lux-empty strong {{ color: var(--lux-ink); display: block; margin-bottom: 0.2rem; }}

/* ---- Metrics --------------------------------------------------------- */
div[data-testid="stMetric"] {{
    background: var(--lux-soft);
    border: 1px solid var(--lux-line);
    border-radius: var(--lux-radius-sm);
    padding: 0.6rem 0.8rem;
}}
div[data-testid="stMetricLabel"] p {{
    color: var(--lux-muted);
    font-size: 0.82rem;
}}

/* ---- Inputs & buttons ----------------------------------------------- */
div[data-testid="stTextInput"] input {{
    font-size: 0.98rem;
    padding: 0.55rem 0.8rem;
    border-radius: var(--lux-radius-sm);
}}
div[data-testid="stTextInput"] input:focus {{
    border-color: var(--lux-blue);
    box-shadow: 0 0 0 2px rgba(31, 111, 139, 0.12);
}}
.stButton button, .stDownloadButton button {{
    border-radius: var(--lux-radius-sm);
    font-weight: 600;
}}
div[data-testid="stPageLink-NavLink"] {{ border-radius: var(--lux-radius-sm); }}

/* ---- Chart containers ------------------------------------------------ */
div[data-testid="stPlotlyChart"] {{
    border-radius: var(--lux-radius-sm);
    overflow: hidden;
}}

/* ---- Expanders ------------------------------------------------------- */
details[data-testid="stExpander"] {{
    border-radius: var(--lux-radius-sm);
    border-color: var(--lux-line);
}}

/* ---- Legacy status panel (older placeholder dashboards) -------------- */
.lux-status-panel {{
    border: 1px solid var(--lux-line);
    border-radius: var(--lux-radius);
    padding: 1rem;
    background: #ffffff;
    margin: 0.6rem 0 1rem 0;
}}
.lux-status-panel h3 {{ font-size: 1rem; margin: 0 0 0.5rem 0; }}
.lux-status-row {{
    display: flex;
    gap: 0.65rem;
    align-items: flex-start;
    padding: 0.45rem 0;
    border-top: 1px solid #eef1f5;
}}
.lux-status-row:first-of-type {{ border-top: 0; }}
.lux-status-icon {{
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
}}
.lux-status-row strong {{ display: block; color: var(--lux-ink); }}
.lux-status-row span {{ color: var(--lux-muted); line-height: 1.4; }}

/* ---- Responsive ------------------------------------------------------ */
@media (max-width: 820px) {{
    .block-container {{ padding-left: 1rem; padding-right: 1rem; }}
    .lux-hero h1 {{ font-size: 1.6rem; }}
    .lux-hero p {{ font-size: 0.96rem; }}
}}
</style>
"""


def inject_theme() -> None:
    """Inject the LuxStats stylesheet. Call once per page, after set_page_config."""
    st.markdown(_STYLE, unsafe_allow_html=True)


# --------------------------------------------------------------------------
# Small render helpers that depend on the stylesheet above
# --------------------------------------------------------------------------
def section_header(title: str, subtitle: str = "") -> None:
    """Consistent section heading used across the portal."""
    sub = f"<div class='lux-section-sub'>{escape(subtitle)}</div>" if subtitle else ""
    st.markdown(
        f"<div class='lux-section'><div class='lux-section-title'>{escape(title)}</div>{sub}</div>",
        unsafe_allow_html=True,
    )


def empty_state(title: str, body: str) -> None:
    """A calm, helpful empty/limited state — never an alarming error."""
    st.markdown(
        f"<div class='lux-empty'><strong>{escape(title)}</strong>{escape(body)}</div>",
        unsafe_allow_html=True,
    )


def trust_note(body: str, *, heading: str = "Source-backed, no black box") -> None:
    """Short, calm trust panel: where the data comes from, and what the app is not."""
    st.markdown(
        f"<div class='lux-trust'><strong>{escape(heading)}</strong>"
        f"<p>{escape(body)}</p></div>",
        unsafe_allow_html=True,
    )
