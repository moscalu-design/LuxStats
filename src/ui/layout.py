"""Layout helpers that keep page setup consistent."""

from __future__ import annotations

from src.ui.navigation import render_navigation


def render_app_sidebar() -> None:
    """Shared sidebar wrapper used by legacy page imports."""
    render_navigation()
