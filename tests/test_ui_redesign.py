"""Tests covering the 2026 UX/UI redesign.

These lock in the redesigned framework: a single compact sidebar, a focused
landing page, consistent page headers, and the centralized theme — without
weakening the deterministic, source-backed product rules.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


# -- Theme / design system ------------------------------------------------
def test_theme_module_exposes_design_system() -> None:
    from src.ui import theme

    assert callable(theme.inject_theme)
    assert callable(theme.section_header)
    assert callable(theme.empty_state)
    assert callable(theme.trust_note)
    # Design tokens are real colour values, centralized in one place.
    for token in (theme.INK, theme.BLUE, theme.GREEN, theme.LINE):
        assert token.startswith("#")


def test_ui_components_reexports_theme_helpers() -> None:
    from src import ui_components

    for name in ("section_header", "empty_state", "trust_note", "inject_style"):
        assert hasattr(ui_components, name)


def test_default_streamlit_nav_is_disabled() -> None:
    """The redesign hides Streamlit's auto-nav so only one sidebar shows."""
    config = (ROOT / ".streamlit" / "config.toml").read_text(encoding="utf-8")
    assert "showSidebarNavigation = false" in config


# -- Landing page ---------------------------------------------------------
def test_home_has_focused_landing_sections() -> None:
    from src import home

    assert len(home.TOPIC_TILES) == 7
    assert len(home.TOOL_TILES) == 4
    src = (ROOT / "src" / "home.py").read_text(encoding="utf-8")
    for section in ("Start with a question", "Explore by topic",
                    "Tools for deeper analysis"):
        assert section in src
    # The cluttered legacy sections must be gone.
    assert "lux-howto" not in src
    assert "Common comparisons" not in src


def test_home_topic_tiles_point_at_real_pages() -> None:
    from src import home

    for _icon, _name, _blurb, page in home.TOPIC_TILES + home.TOOL_TILES:
        assert (ROOT / page).exists(), f"missing {page}"


# -- Topic pages ----------------------------------------------------------
def test_topic_pages_show_honest_empty_state() -> None:
    src = (ROOT / "src" / "topic_page.py").read_text(encoding="utf-8")
    assert "empty_state(" in src
    assert "still being mapped" in src


def test_tourism_is_a_first_class_topic() -> None:
    from src.topic_page import _TOPIC_CATEGORY, _TOPIC_PAGE_ID

    assert "Tourism" in _TOPIC_CATEGORY
    assert _TOPIC_PAGE_ID["Tourism"] == "tourism"


# -- Trust / determinism --------------------------------------------------
def test_about_page_explains_trust_and_determinism() -> None:
    src = (ROOT / "pages" / "12_About_Data.py").read_text(encoding="utf-8")
    for phrase in ("Deterministic", "STATEC / LUSTAT", "ready to chart"):
        assert phrase.lower() in src.lower()


def test_redesign_adds_no_runtime_ai() -> None:
    """The redesign must not introduce any model/chatbot dependency."""
    for rel in ("src/home.py", "src/topic_page.py", "src/ui/theme.py",
                "src/ui/navigation.py"):
        text = (ROOT / rel).read_text(encoding="utf-8").lower()
        for token in ("openai", "anthropic", "gpt-", "chat_input"):
            assert token not in text, f"{rel} contains {token!r}"
