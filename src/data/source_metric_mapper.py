"""Helpers for connecting source records to curated product metrics."""

from __future__ import annotations

from typing import Any

from src.concepts import all_concepts
from src.data.source_mapping import mapping_status


def metric_by_dataset_id() -> dict[str, str]:
    """Return dataset_id -> concept_id for chart-ready curated metrics."""
    return {concept.dataset_id: concept.id for concept in all_concepts()}


def metric_title_by_id() -> dict[str, str]:
    return {concept.id: concept.title for concept in all_concepts()}


def mapped_metric_id(source_record: dict[str, Any]) -> str | None:
    dataset_id = str(source_record.get("dataset_id") or "")
    return metric_by_dataset_id().get(dataset_id)


def mapping_template(source_record: dict[str, Any]) -> str:
    """Return a concise manual mapping template for an unmapped source."""
    title = source_record.get("title") or "Untitled official source"
    dataset_id = source_record.get("dataset_id") or ""
    return "\n".join(
        [
            f"Source: {title}",
            f"Source ID: {source_record.get('source_id', '')}",
            f"Dataset ID: {dataset_id or 'n/a'}",
            f"Type: {source_record.get('source_type', '')}",
            f"Category: {source_record.get('category', '')}",
            "Question this should answer: <plain-language question>",
            "Time column: <column name>",
            "Value column: <column name>",
            "Group/geography column: <optional column name>",
            "Filters/defaults: <safe beginner defaults>",
            "Chart type: line | ranking | bar | table",
            "Mapping status: needs_manual_review" if mapping_status(source_record) == "needs_manual_review" else "Mapping status: unmapped",
        ]
    )
