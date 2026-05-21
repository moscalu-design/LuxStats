"""Derived source-to-product mapping status.

The committed source catalog is intentionally broad. This module derives which
sources are already useful in the public product and which high-priority
records deserve mapping next.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from src.catalog import STARTER_CATALOG, is_placeholder_dataset_id
from src.concepts import all_concepts
from src.data.priority_topics import priority_for_category
from src.data.source_catalog import load_unified_source_catalog, search_source_catalog


def chart_ready_dataset_ids() -> set[str]:
    return {concept.dataset_id for concept in all_concepts()}


def commune_ready_dataset_ids() -> set[str]:
    ids: set[str] = set()
    for entry in STARTER_CATALOG:
        if entry.commune_portal and not is_placeholder_dataset_id(entry.dataset_id):
            ids.add(entry.dataset_id)
    return ids


def mapping_status(record: dict[str, Any]) -> str:
    dataset_id = str(record.get("dataset_id") or "")
    if dataset_id and dataset_id in chart_ready_dataset_ids():
        return "mapped_to_metric"
    if dataset_id and dataset_id in commune_ready_dataset_ids():
        return "mapped_to_commune_portal"
    if record.get("source_type") == "PUBLICATION_PDF":
        return "needs_manual_review"
    if record.get("priority") == "low":
        return "ignored_low_priority"
    return "unmapped"


def enrich_with_mapping_status(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    enriched = []
    for record in records:
        out = dict(record)
        out["mapping_status"] = mapping_status(record)
        out["chart_ready"] = out["mapping_status"] == "mapped_to_metric"
        out["commune_portal_ready"] = out["mapping_status"] == "mapped_to_commune_portal"
        enriched.append(out)
    return enriched


def source_coverage(category: str | None = None) -> dict[str, Any]:
    records = load_unified_source_catalog()
    if category and category != "All":
        records = [record for record in records if record.get("category") == category]
    enriched = enrich_with_mapping_status(records)
    counts = defaultdict(int)
    for record in enriched:
        counts[record["mapping_status"]] += 1
    return {
        "total": len(enriched),
        "chart_ready": counts["mapped_to_metric"],
        "commune_ready": counts["mapped_to_commune_portal"],
        "publication_annexes": len([r for r in enriched if r.get("source_type") == "PUBLICATION_EXCEL"]),
        "publications": len([r for r in enriched if str(r.get("source_type", "")).startswith("PUBLICATION")]),
        "high_priority": len([r for r in enriched if r.get("priority") == "high"]),
        "unmapped_high_priority": len([r for r in enriched if r.get("priority") == "high" and r["mapping_status"] == "unmapped"]),
        "mapping_counts": dict(counts),
    }


def high_priority_unmapped(category: str | None = None, limit: int = 20) -> list[dict[str, Any]]:
    filters = {"priority": "high"}
    if category:
        filters["category"] = category
    records = enrich_with_mapping_status(search_source_catalog("", filters))
    records = [record for record in records if record["mapping_status"] in {"unmapped", "needs_manual_review"}]
    records.sort(
        key=lambda record: (
            -priority_for_category(str(record.get("category") or "")),
            -int(record.get("priority_score") or 0),
            str(record.get("title") or ""),
        )
    )
    return records[:limit]
