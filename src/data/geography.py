"""Geospatial foundation for commune-level data.

This module is a deliberate, honest placeholder. The portal does not ship
commune boundary polygons, so it never fakes a map. Instead it exposes a
clean hook: drop a GeoJSON file at ``data/geography/communes.geojson`` (keyed
by commune name in a ``name`` property) and map views light up automatically.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.config import DATA_DIR

GEOGRAPHY_DIR = DATA_DIR / "geography"
COMMUNE_GEOJSON_PATH = GEOGRAPHY_DIR / "communes.geojson"

# Property in each GeoJSON feature expected to hold the commune name.
COMMUNE_NAME_PROPERTY = "name"


def commune_boundaries_available() -> bool:
    """True only when a real commune-boundary GeoJSON file is present."""
    return COMMUNE_GEOJSON_PATH.exists() and COMMUNE_GEOJSON_PATH.stat().st_size > 0


def get_commune_geojson() -> dict[str, Any] | None:
    """Load the commune-boundary GeoJSON, or None when it is not connected."""
    if not commune_boundaries_available():
        return None
    try:
        return json.loads(COMMUNE_GEOJSON_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def geography_status() -> dict[str, Any]:
    """Describe what geospatial data is connected, for UI and tests."""
    available = commune_boundaries_available()
    return {
        "boundaries_available": available,
        "geojson_path": str(COMMUNE_GEOJSON_PATH),
        "name_property": COMMUNE_NAME_PROPERTY,
        "message": (
            "Commune boundary data is connected — map views are available."
            if available
            else "Map view is not available yet because commune boundary "
            "data has not been connected."
        ),
        # TODO: connect official LAU commune boundaries from the Luxembourg
        # geoportal (data.public.lu) as data/geography/communes.geojson.
    }
