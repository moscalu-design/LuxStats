"""Unified STATEC source catalog.

Combines three sub-catalogs into one searchable list of source records:

* LUSTAT API dataflows      (:mod:`src.data.statec_api_catalog`)
* STATEC other-format files (:mod:`src.data.statec_other_formats_catalog`)
* publication annexes       (:mod:`src.data.statec_publication_catalog`)

The app only ever *loads* the unified catalog from JSON. Rebuilding it (which
touches the network) is done by ``scripts/refresh_source_catalog.py``.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from src.config import CATALOG_DIR
from src.data.categorization import looks_like_short_term_indicator
from src.data.statec_api_catalog import build_api_catalog, load_api_catalog, save_api_catalog
from src.data.statec_other_formats_catalog import (
    build_other_formats_catalog,
    load_other_formats_catalog,
    save_other_formats_catalog,
)
from src.data.statec_publication_catalog import (
    build_publication_catalog,
    load_publication_catalog,
    save_publication_catalog,
)

UNIFIED_CATALOG_PATH = CATALOG_DIR / "unified_source_catalog.json"

SOURCE_TYPES = [
    "LUSTAT_API", "STATEC_EXCEL", "PUBLICATION_EXCEL", "PUBLICATION_PDF",
    "OTHER_FORMAT",
]

# Fields every unified record must carry.
REQUIRED_FIELDS = ("source_id", "source_type", "title", "category")

_HIGH_PRIORITY_CATEGORIES = {
    "Housing", "Salaries / Income", "Prices / Inflation", "Labour Market",
    "Population",
}
_MEDIUM_PRIORITY_CATEGORIES = {
    "Communes / Geography", "Economy / National Accounts", "Public Finance",
    "Enterprises / Business", "Construction", "Tourism", "Education",
    "Environment / Energy", "Health",
}
_MACHINE_READABLE = {"xlsx", "xls", "csv"}


# --------------------------------------------------------------------------
# Priority scoring (Feature 11)
# --------------------------------------------------------------------------

def assign_priority(record: dict[str, Any]) -> dict[str, Any]:
    """Return priority / priority_score / priority_reason for a record."""
    score = 0
    reasons: list[str] = []
    category = record.get("category", "")
    geo = record.get("geographic_level", "unknown")
    source_type = record.get("source_type", "")
    file_type = (record.get("file_type") or "").lower()
    text = f"{record.get('title','')} {' '.join(record.get('keywords',[]))}"

    if geo in {"commune", "canton"}:
        score += 3
        reasons.append("commune/canton-level data")
    if category in _HIGH_PRIORITY_CATEGORIES:
        score += 3
        reasons.append(f"high-value category ({category})")
    elif category in _MEDIUM_PRIORITY_CATEGORIES:
        score += 1
        reasons.append(f"useful category ({category})")
    elif category == "Other / Unknown":
        score -= 1
        reasons.append("uncategorized")

    if looks_like_short_term_indicator(text):
        score += 2
        reasons.append("short-term indicator")

    if source_type == "PUBLICATION_EXCEL":
        score += 2
        reasons.append("publication Excel annex")
    elif source_type == "STATEC_EXCEL":
        score += 1
        reasons.append("downloadable Excel table")
    elif source_type == "LUSTAT_API":
        score += 1
        reasons.append("machine-readable API dataset")
    elif source_type == "PUBLICATION_PDF":
        score -= 2
        reasons.append("PDF only — not machine-readable")

    if source_type != "LUSTAT_API" and file_type and file_type not in _MACHINE_READABLE:
        score -= 1

    if score >= 5:
        bucket = "high"
    elif score >= 2:
        bucket = "medium"
    else:
        bucket = "low"
    return {
        "priority": bucket,
        "priority_score": score,
        "priority_reason": "; ".join(reasons) or "no strong priority signal",
    }


# --------------------------------------------------------------------------
# Record normalization
# --------------------------------------------------------------------------

def _base_record(source_id: str, source_type: str) -> dict[str, Any]:
    return {
        "source_id": source_id,
        "source_type": source_type,
        "title": "",
        "description": "",
        "category": "Other / Unknown",
        "subcategory": "",
        "keywords": [],
        "dataset_id": "",
        "source_page_url": "",
        "file_url": "",
        "api_url": "",
        "file_type": "",
        "publication_family": "",
        "publication_date": None,
        "geographic_level": "unknown",
        "recommended_for_portal": False,
        "recommended_for_commune_portal": False,
        "recommended_for_housing": False,
        "recommended_for_what_changed": False,
        "last_seen": None,
        "last_downloaded": None,
        "notes": "",
    }


def _from_api(rec: dict[str, Any]) -> dict[str, Any]:
    out = _base_record(f"api:{rec['dataset_id']}", "LUSTAT_API")
    out.update({
        "title": rec.get("title", ""),
        "description": rec.get("description", ""),
        "category": rec.get("category", "Other / Unknown"),
        "keywords": rec.get("keywords", []),
        "dataset_id": rec.get("dataset_id", ""),
        "api_url": rec.get("source_url", ""),
        "source_page_url": rec.get("source_page_url") or "https://lustat.statec.lu/",
        "geographic_level": rec.get("geographic_level", "unknown"),
        "recommended_for_portal": rec.get("recommended_for_portal", False),
        "recommended_for_commune_portal": rec.get("recommended_for_commune_portal", False),
        "last_seen": rec.get("last_catalog_refresh"),
        "notes": rec.get("notes", ""),
    })
    return out


def _from_other_format(rec: dict[str, Any]) -> dict[str, Any]:
    out = _base_record(f"file:{rec.get('filename','')}", rec.get("source_type", "OTHER_FORMAT"))
    out.update({
        "title": rec.get("title", ""),
        "category": rec.get("category", "Other / Unknown"),
        "keywords": rec.get("keywords", []),
        "dataset_id": rec.get("dataset_id", ""),
        "source_page_url": rec.get("source_page_url", ""),
        "file_url": rec.get("file_url", ""),
        "file_type": rec.get("file_type", ""),
        "geographic_level": rec.get("geographic_level", "unknown"),
        "recommended_for_commune_portal": rec.get("looks_commune_level", False),
        "last_seen": rec.get("last_seen"),
        "notes": rec.get("notes", ""),
    })
    return out


def _from_publication(rec: dict[str, Any]) -> dict[str, Any]:
    out = _base_record(f"pub:{rec.get('filename','')}", rec.get("source_type", "PUBLICATION_PDF"))
    out.update({
        "title": rec.get("title", ""),
        "category": rec.get("category", "Other / Unknown"),
        "keywords": rec.get("keywords", []),
        "source_page_url": rec.get("source_page_url", ""),
        "file_url": rec.get("file_url", ""),
        "file_type": rec.get("file_type", ""),
        "publication_family": rec.get("publication_family", ""),
        "publication_date": rec.get("publication_date"),
        "last_seen": rec.get("last_seen"),
        "notes": rec.get("notes", ""),
    })
    return out


def _finalize(record: dict[str, Any]) -> dict[str, Any]:
    """Fill derived recommendation flags and priority on a unified record."""
    category = record["category"]
    record["recommended_for_housing"] = category == "Housing"
    record["recommended_for_what_changed"] = (
        record["source_type"] in {"PUBLICATION_EXCEL", "PUBLICATION_PDF"}
        or looks_like_short_term_indicator(record["title"])
    )
    if record["source_type"] in {"STATEC_EXCEL", "OTHER_FORMAT"} and not record["recommended_for_portal"]:
        record["recommended_for_portal"] = category in _HIGH_PRIORITY_CATEGORIES
    record.update(assign_priority(record))
    return record


# --------------------------------------------------------------------------
# Build / refresh / load
# --------------------------------------------------------------------------

def build_unified_source_catalog() -> list[dict[str, Any]]:
    """Build the unified catalog from the saved sub-catalogs."""
    records: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for rec in load_api_catalog():
        records.append(_from_api(rec))
    for rec in load_other_formats_catalog():
        records.append(_from_other_format(rec))
    for rec in load_publication_catalog():
        records.append(_from_publication(rec))

    unified: list[dict[str, Any]] = []
    for record in records:
        sid = record["source_id"]
        if not sid or sid in seen_ids:
            continue
        seen_ids.add(sid)
        unified.append(_finalize(record))
    unified.sort(key=lambda r: (-r["priority_score"], r["category"], r["title"]))
    return unified


def refresh_unified_source_catalog(force_refresh: bool = False) -> dict[str, int]:
    """Rebuild every sub-catalog (network) and the unified catalog; save all.

    Returns a count summary. Used by ``scripts/refresh_source_catalog.py``.
    """
    CATALOG_DIR.mkdir(parents=True, exist_ok=True)
    api = build_api_catalog(force_refresh=force_refresh)
    save_api_catalog(api)
    other = build_other_formats_catalog(force_refresh=force_refresh)
    save_other_formats_catalog(other)
    pubs = build_publication_catalog(force_refresh=force_refresh)
    save_publication_catalog(pubs)

    unified = build_unified_source_catalog()
    save_unified_source_catalog(unified)
    return {
        "api": len(api),
        "other_formats": len(other),
        "publications": len(pubs),
        "unified": len(unified),
    }


def save_unified_source_catalog(records: list[dict[str, Any]]) -> None:
    CATALOG_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "count": len(records),
        "records": records,
    }
    UNIFIED_CATALOG_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def load_unified_source_catalog() -> list[dict[str, Any]]:
    """Load the unified catalog from JSON; empty list when not built yet."""
    if not UNIFIED_CATALOG_PATH.exists():
        return []
    try:
        payload = json.loads(UNIFIED_CATALOG_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    return payload.get("records", []) if isinstance(payload, dict) else []


def catalog_generated_at() -> str | None:
    if not UNIFIED_CATALOG_PATH.exists():
        return None
    try:
        payload = json.loads(UNIFIED_CATALOG_PATH.read_text(encoding="utf-8"))
        return payload.get("generated_at")
    except (OSError, json.JSONDecodeError):
        return None


# --------------------------------------------------------------------------
# Search and filtered getters
# --------------------------------------------------------------------------

def search_source_catalog(
    query: str = "",
    filters: dict[str, Any] | None = None,
    records: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Search the unified catalog by free text and optional exact-match filters.

    ``filters`` keys may be: category, source_type, geographic_level,
    priority, publication_family, file_type, recommended_for_portal,
    recommended_for_commune_portal.
    """
    records = records if records is not None else load_unified_source_catalog()
    results = list(records)
    filters = filters or {}

    for key in ("category", "source_type", "geographic_level", "priority",
                "publication_family", "file_type"):
        value = filters.get(key)
        if value and value != "All":
            results = [r for r in results if r.get(key) == value]
    for flag in ("recommended_for_portal", "recommended_for_commune_portal"):
        if filters.get(flag):
            results = [r for r in results if r.get(flag)]

    query = (query or "").strip().lower()
    if query:
        terms = [t for t in query.split() if t]

        def matches(record: dict[str, Any]) -> bool:
            haystack = " ".join([
                str(record.get("title", "")),
                str(record.get("description", "")),
                str(record.get("dataset_id", "")),
                str(record.get("category", "")),
                str(record.get("publication_family", "")),
                " ".join(record.get("keywords", []) or []),
            ]).lower()
            return all(term in haystack for term in terms)

        results = [r for r in results if matches(r)]
    return results


def get_sources_by_category(category: str) -> list[dict[str, Any]]:
    return [r for r in load_unified_source_catalog() if r.get("category") == category]


def get_sources_by_type(source_type: str) -> list[dict[str, Any]]:
    return [r for r in load_unified_source_catalog() if r.get("source_type") == source_type]


def get_commune_level_sources() -> list[dict[str, Any]]:
    return [r for r in load_unified_source_catalog()
            if r.get("geographic_level") in {"commune", "canton"}]


def get_housing_sources() -> list[dict[str, Any]]:
    return [r for r in load_unified_source_catalog() if r.get("category") == "Housing"]


def get_salary_sources() -> list[dict[str, Any]]:
    return [r for r in load_unified_source_catalog()
            if r.get("category") == "Salaries / Income"]


def get_recent_publication_sources(limit: int = 25) -> list[dict[str, Any]]:
    pubs = [r for r in load_unified_source_catalog()
            if r.get("source_type") in {"PUBLICATION_EXCEL", "PUBLICATION_PDF"}]
    pubs.sort(key=lambda r: str(r.get("publication_date") or ""), reverse=True)
    return pubs[:limit]


def recommended_next_sources(limit: int = 15) -> list[dict[str, Any]]:
    """Highest-priority sources not yet wired into a curated metric."""
    ranked = sorted(
        load_unified_source_catalog(),
        key=lambda r: r.get("priority_score", 0),
        reverse=True,
    )
    return [r for r in ranked if r.get("priority") == "high"][:limit]


def catalog_summary() -> dict[str, Any]:
    """Headline counts for the Home page 'data coverage' section."""
    records = load_unified_source_catalog()
    by_type: dict[str, int] = {t: 0 for t in SOURCE_TYPES}
    for r in records:
        by_type[r.get("source_type", "")] = by_type.get(r.get("source_type", ""), 0) + 1
    return {
        "total": len(records),
        "api": by_type.get("LUSTAT_API", 0),
        "excel": by_type.get("STATEC_EXCEL", 0) + by_type.get("PUBLICATION_EXCEL", 0),
        "other_format": by_type.get("OTHER_FORMAT", 0),
        "publications": by_type.get("PUBLICATION_EXCEL", 0) + by_type.get("PUBLICATION_PDF", 0),
        "commune_level": len([r for r in records
                              if r.get("geographic_level") in {"commune", "canton"}]),
        "categories": sorted({r.get("category", "") for r in records if r.get("category")}),
        "generated_at": catalog_generated_at(),
    }


def catalog_validation_issues(records: list[dict[str, Any]] | None = None) -> list[str]:
    """Flag unified records missing required fields or with duplicate ids."""
    records = records if records is not None else load_unified_source_catalog()
    issues: list[str] = []
    seen: set[str] = set()
    for record in records:
        sid = record.get("source_id", "")
        if sid in seen:
            issues.append(f"Duplicate source_id: {sid}")
        seen.add(sid)
        for field in REQUIRED_FIELDS:
            if not record.get(field):
                issues.append(f"{sid or '<no id>'} is missing required field {field!r}")
        if record.get("source_type") not in SOURCE_TYPES:
            issues.append(f"{sid} has unknown source_type {record.get('source_type')!r}")
    return issues
