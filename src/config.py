"""Shared configuration for paths, labels, and app defaults."""

from __future__ import annotations

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
CACHE_DIR = DATA_DIR / "cache"
METADATA_DIR = DATA_DIR / "metadata"
# Curated source catalogs are committed to the repo so the deployed app has
# data without crawling; raw downloaded files stay in the gitignored cache.
CATALOG_DIR = DATA_DIR / "catalog"
REPORTS_DIR = ROOT_DIR / "reports"

APP_TITLE = "Luxembourg Statistics Portal"
APP_TAGLINE = "Explore official Luxembourg statistics through simple interactive charts."
STATEC_SOURCE = "STATEC / LUSTAT"

THEME_ORDER = [
    "Housing",
    "Salaries",
    "Population",
    "Labour Market",
    "Prices & Inflation",
    "Economy",
    "Education",
    "Mobility",
    "Public Finance",
]
