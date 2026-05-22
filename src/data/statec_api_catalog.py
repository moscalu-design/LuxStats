"""LUSTAT API catalog builder.

Fetches the full LUSTAT (STATEC) SDMX dataflow list, categorizes every
dataflow with the transparent rules in :mod:`src.data.categorization`, and
saves a JSON catalog the app can load without touching the network.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from src.config import CATALOG_DIR
from src.data.categorization import (
    categorize,
    extract_keywords,
    infer_geographic_level,
)
from src.cache import load_dataflows
from src.statec_client import Dataflow, StatecClient

API_CATALOG_PATH = CATALOG_DIR / "lustat_api_catalog.json"
SOURCE_TYPE = "LUSTAT_API"
LUSTAT_AGENCY = "LU1"

# Categories that justify surfacing a dataflow in the curated portal flows.
_PORTAL_CATEGORIES = {
    "Population", "Communes / Geography", "Housing", "Salaries / Income",
    "Labour Market", "Prices / Inflation", "Economy / National Accounts",
}

_DATASET_OVERRIDES: dict[str, dict[str, Any]] = {
    "DSD_TOUR_ARR@DF_D5301": {
        "source_page_url": (
            "https://lustat.statec.lu/vis?lc=en&tm=DF_D5301&pg=0&snb=1&"
            "df[ds]=ds-release&df[id]=DSD_TOUR_ARR%40DF_D5301&df[ag]=LU1&"
            "df[vs]=1.0&dq=..A..._T..&lom=LASTNPERIODS&lo=1&to[TIME_PERIOD]=false"
        ),
        "keywords": [
            "tourism", "tourists", "arrivals", "accommodation", "hotels",
            "overnight stays", "nights", "Luxembourg tourism", "D5301",
        ],
        "notes": (
            "Official LUSTAT tourism arrivals dataflow. Kept unmapped until "
            "dimensions and default filters are reviewed for a public chart."
        ),
    },
}


def fetch_lustat_dataflows(force_refresh: bool = False) -> list[Dataflow]:
    """Return every LUSTAT dataflow, using the on-disk dataflow cache."""
    return load_dataflows(StatecClient(), force_refresh=force_refresh)


def parse_lustat_dataflows(flows: list[Dataflow]) -> list[dict[str, Any]]:
    """Reduce raw Dataflow objects to plain dicts (id, title, version)."""
    parsed: list[dict[str, Any]] = []
    for flow in flows:
        parsed.append(
            {
                "dataset_id": flow.id,
                "title": flow.name_en or flow.name_fr or flow.id,
                "title_fr": flow.name_fr or "",
                "version": flow.version,
                "agency": flow.agency or LUSTAT_AGENCY,
            }
        )
    return parsed


def categorize_api_dataset(title: str, description: str, dataset_id: str) -> str:
    """Categorize a LUSTAT dataflow from its title, description and id."""
    return categorize(" ".join([title or "", description or "", dataset_id or ""]))


def _api_data_url(dataset_id: str, agency: str, version: str) -> str:
    return f"https://lustat.statec.lu/rest/data/{agency},{dataset_id},{version}/all"


def build_api_catalog(force_refresh: bool = False) -> list[dict[str, Any]]:
    """Build the categorized LUSTAT API catalog (list of records)."""
    flows = fetch_lustat_dataflows(force_refresh=force_refresh)
    parsed = parse_lustat_dataflows(flows)
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    records: list[dict[str, Any]] = []
    for item in parsed:
        title = item["title"]
        dataset_id = item["dataset_id"]
        text = f"{title} {item['title_fr']} {dataset_id}"
        category = categorize_api_dataset(title, item["title_fr"], dataset_id)
        geo = infer_geographic_level(text)
        override = _DATASET_OVERRIDES.get(dataset_id, {})
        keywords = list(dict.fromkeys(extract_keywords(text) + override.get("keywords", [])))
        records.append(
            {
                "dataset_id": dataset_id,
                "title": title,
                "description": item["title_fr"],
                "source_type": SOURCE_TYPE,
                "source_url": _api_data_url(dataset_id, item["agency"], item["version"]),
                "source_page_url": override.get("source_page_url", ""),
                "category": category,
                "subcategory": "",
                "keywords": keywords,
                "geographic_level": geo,
                "recommended_for_portal": category in _PORTAL_CATEGORIES,
                "recommended_for_commune_portal": geo in {"commune", "canton"},
                "last_catalog_refresh": now,
                "notes": override.get("notes", "Auto-categorized from the LUSTAT dataflow list."),
            }
        )
    records.sort(key=lambda r: r["dataset_id"])
    return records


def save_api_catalog(records: list[dict[str, Any]]) -> None:
    """Persist the API catalog to JSON."""
    CATALOG_DIR.mkdir(parents=True, exist_ok=True)
    API_CATALOG_PATH.write_text(
        json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def load_api_catalog() -> list[dict[str, Any]]:
    """Load the saved API catalog, or an empty list when it is missing."""
    if not API_CATALOG_PATH.exists():
        return []
    try:
        return json.loads(API_CATALOG_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
