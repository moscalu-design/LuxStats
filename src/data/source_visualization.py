"""Visualization readiness index for official STATEC/LUSTAT sources."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Any

from src.config import CATALOG_DIR, REPORTS_DIR
from src.concepts import get_concept
from src.data.file_ingestion import is_file_cached
from src.data.source_catalog import load_unified_source_catalog
from src.data.source_mapping import enrich_with_mapping_status, mapping_status
from src.data.source_metric_mapper import mapped_metric_id

VISUALIZATION_INDEX_PATH = CATALOG_DIR / "source_visualization_index.json"
VISUALIZATION_REPORT_PATH = REPORTS_DIR / "source_visualization_index.md"

VISUALIZATION_STATUSES = (
    "chart_ready",
    "preview_ready",
    "downloadable_only",
    "needs_column_mapping",
    "needs_excel_inspection",
    "needs_manual_review",
    "not_chartable",
    "ignored_low_priority",
)


def load_source_library() -> list[dict[str, Any]]:
    return load_unified_source_catalog()


def load_source_mappings() -> dict[str, str]:
    mappings: dict[str, str] = {}
    for record in load_source_library():
        metric_id = mapped_metric_id(record)
        if metric_id:
            mappings[record["source_id"]] = metric_id
    return mappings


def _base(source_record: dict[str, Any]) -> dict[str, Any]:
    metric_id = mapped_metric_id(source_record)
    concept = get_concept(metric_id) if metric_id else None
    return {
        "source_id": source_record.get("source_id", ""),
        "title": source_record.get("title", ""),
        "source_type": source_record.get("source_type", ""),
        "category": source_record.get("category", "Other / Unknown"),
        "visualization_status": "not_chartable",
        "mapping_status": mapping_status(source_record),
        "mapped_metric_id": metric_id,
        "confidence": 0.0,
        "reason": "",
        "recommended_action": "",
        "time_column": "TIME_PERIOD" if concept else "",
        "value_column": "OBS_VALUE" if concept else "",
        "group_column": concept.series_dim if concept and concept.series_dim else "",
        "geography_column": "",
        "frequency": "annual" if concept and concept.freq == "Annual" else "unknown",
        "default_chart_type": concept.chart if concept else "",
        "chart_route_or_action": f"concept:{metric_id}" if metric_id else "",
        "priority": source_record.get("priority", "low"),
        "priority_score": source_record.get("priority_score", 0),
        "geographic_level": source_record.get("geographic_level", "unknown"),
        "file_url": source_record.get("file_url", ""),
        "source_page_url": source_record.get("source_page_url", ""),
        "api_url": source_record.get("api_url", ""),
        "dataset_id": source_record.get("dataset_id", ""),
        "last_checked": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def assess_source_visualization_status(source_record: dict[str, Any]) -> dict[str, Any]:
    """Classify the safest available experience for one official source."""
    out = _base(source_record)
    source_type = str(source_record.get("source_type") or "")
    file_type = str(source_record.get("file_type") or "").lower()
    priority = str(source_record.get("priority") or "low")
    status = out["mapping_status"]

    if status == "mapped_to_metric":
        out.update({
            "visualization_status": "chart_ready",
            "confidence": 1.0,
            "reason": "Mapped to a curated chart-ready metric.",
            "recommended_action": "Open chart",
        })
        return out

    if status == "mapped_to_commune_portal":
        out.update({
            "visualization_status": "chart_ready",
            "confidence": 0.85,
            "reason": "Mapped to a confirmed Commune Portal metric.",
            "recommended_action": "Open commune profile or Compare.",
            "default_chart_type": "commune_profile",
            "chart_route_or_action": "page:pages/3_Commune_Portal.py",
        })
        return out

    if source_type == "PUBLICATION_PDF":
        out.update({
            "visualization_status": "needs_manual_review",
            "confidence": 0.9,
            "reason": "PDF-only publication cannot be charted safely without manual extraction.",
            "recommended_action": "Open official PDF and decide whether an annex/table should be mapped.",
        })
        return out

    if priority == "low":
        out.update({
            "visualization_status": "ignored_low_priority",
            "confidence": 0.7,
            "reason": "Cataloged but low priority for the public portal.",
            "recommended_action": "Keep searchable; map only if a public question needs it.",
        })
        return out

    if source_type in {"STATEC_EXCEL", "PUBLICATION_EXCEL", "OTHER_FORMAT"}:
        if file_type in {"xlsx", "xls", "xlsm", "csv"}:
            cached = is_file_cached(source_record)
            out.update({
                "visualization_status": "preview_ready" if cached else "needs_excel_inspection",
                "confidence": 0.75 if cached else 0.65,
                "reason": (
                    "File is cached locally and can be previewed before mapping."
                    if cached else
                    "Official file exists; download/inspect sheets before chart mapping."
                ),
                "recommended_action": "Preview source" if cached else "Inspect source",
            })
            return out
        out.update({
            "visualization_status": "downloadable_only" if source_record.get("file_url") else "not_chartable",
            "confidence": 0.7,
            "reason": "Official file is available but not in a directly previewable table format.",
            "recommended_action": "Download official file",
        })
        return out

    if source_type == "LUSTAT_API":
        out.update({
            "visualization_status": "needs_column_mapping",
            "confidence": 0.8,
            "reason": "Machine-readable API dataset exists, but no safe public chart mapping is confirmed.",
            "recommended_action": "Inspect dimensions and add a curated metric mapping.",
            "time_column": "TIME_PERIOD",
            "value_column": "OBS_VALUE",
            "frequency": "unknown",
        })
        return out

    out.update({
        "visualization_status": "downloadable_only" if source_record.get("file_url") else "not_chartable",
        "confidence": 0.5,
        "reason": "The source is cataloged but does not expose a known chartable structure.",
        "recommended_action": "Open official source details",
    })
    return out


def build_source_visualization_index() -> list[dict[str, Any]]:
    records = enrich_with_mapping_status(load_source_library())
    index = [assess_source_visualization_status(record) for record in records]
    index.sort(
        key=lambda row: (
            row["visualization_status"] != "chart_ready",
            row["visualization_status"] != "preview_ready",
            -int(row.get("priority_score") or 0),
            row.get("category", ""),
            row.get("title", ""),
        )
    )
    return index


def save_source_visualization_index(index: list[dict[str, Any]] | None = None) -> None:
    CATALOG_DIR.mkdir(parents=True, exist_ok=True)
    rows = index if index is not None else build_source_visualization_index()
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "count": len(rows),
        "records": rows,
    }
    VISUALIZATION_INDEX_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def load_source_visualization_index() -> list[dict[str, Any]]:
    if not VISUALIZATION_INDEX_PATH.exists():
        return build_source_visualization_index()
    try:
        payload = json.loads(VISUALIZATION_INDEX_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return build_source_visualization_index()
    records = payload.get("records", [])
    return records if isinstance(records, list) else []


def get_visualization_status(source_id: str) -> dict[str, Any] | None:
    return next((row for row in load_source_visualization_index() if row.get("source_id") == source_id), None)


def _filter_status(statuses: set[str], topic: str | None = None) -> list[dict[str, Any]]:
    rows = [row for row in load_source_visualization_index() if row.get("visualization_status") in statuses]
    if topic:
        rows = [row for row in rows if row.get("category") == topic or row.get("category") == _topic_to_category(topic)]
    return rows


def get_chart_ready_sources(topic: str | None = None) -> list[dict[str, Any]]:
    return _filter_status({"chart_ready"}, topic)


def get_preview_ready_sources(topic: str | None = None) -> list[dict[str, Any]]:
    return _filter_status({"preview_ready"}, topic)


def get_sources_needing_mapping(topic: str | None = None) -> list[dict[str, Any]]:
    return _filter_status({"needs_column_mapping", "needs_excel_inspection"}, topic)


def get_sources_needing_review(topic: str | None = None) -> list[dict[str, Any]]:
    return _filter_status({"needs_manual_review"}, topic)


def visualization_summary(rows: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    rows = rows if rows is not None else load_source_visualization_index()
    counts = Counter(row.get("visualization_status", "not_chartable") for row in rows)
    by_topic: dict[str, Counter] = defaultdict(Counter)
    for row in rows:
        by_topic[row.get("category", "Other / Unknown")][row.get("visualization_status", "not_chartable")] += 1
    return {
        "total": len(rows),
        "counts": dict(counts),
        "chart_ready": counts["chart_ready"],
        "preview_ready": counts["preview_ready"],
        "downloadable_only": counts["downloadable_only"],
        "needs_mapping": counts["needs_column_mapping"] + counts["needs_excel_inspection"],
        "needs_manual_review": counts["needs_manual_review"],
        "not_chartable": counts["not_chartable"],
        "ignored_low_priority": counts["ignored_low_priority"],
        "by_topic": {topic: dict(counter) for topic, counter in by_topic.items()},
    }


def generate_visualization_report(index: list[dict[str, Any]] | None = None) -> str:
    rows = index if index is not None else load_source_visualization_index()
    summary = visualization_summary(rows)
    high_priority = [
        row for row in rows
        if row.get("priority") == "high"
        and row.get("visualization_status") in {"needs_column_mapping", "needs_excel_inspection", "needs_manual_review"}
    ][:25]
    topic_lines = []
    for topic, counts in sorted(summary["by_topic"].items()):
        topic_lines.append(f"- {topic}: {counts.get('chart_ready', 0)} chart-ready, {counts.get('preview_ready', 0)} preview-ready, {counts.get('needs_column_mapping', 0) + counts.get('needs_excel_inspection', 0)} need mapping")
    task_lines = [
        f"- `{row.get('source_id')}` - {row.get('title')} ({row.get('visualization_status')}: {row.get('recommended_action')})"
        for row in high_priority
    ]
    return "\n".join([
        "# Source Visualization Index",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
        "",
        "## Summary",
        "",
        f"- Total sources: {summary['total']:,}",
        f"- Chart-ready: {summary['chart_ready']:,}",
        f"- Preview-ready: {summary['preview_ready']:,}",
        f"- Downloadable only: {summary['downloadable_only']:,}",
        f"- Needs mapping: {summary['needs_mapping']:,}",
        f"- Needs manual review: {summary['needs_manual_review']:,}",
        f"- Not chartable: {summary['not_chartable']:,}",
        f"- Low priority / archived: {summary['ignored_low_priority']:,}",
        "",
        "## Chart-Ready by Topic",
        "",
        *(topic_lines or ["No chart-ready sources are indexed yet."]),
        "",
        "## Highest-Priority Mapping Tasks",
        "",
        *(task_lines or ["No high-priority mapping tasks are currently flagged."]),
        "",
        "## Recommended Next Work",
        "",
        "1. Promote high-priority API sources by adding curated `Concept` mappings.",
        "2. Download and inspect high-priority Excel/publication annexes before charting.",
        "3. Keep PDF-only sources in manual review unless a table/annex can be mapped.",
    ])


def save_visualization_report(index: list[dict[str, Any]] | None = None) -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    VISUALIZATION_REPORT_PATH.write_text(generate_visualization_report(index), encoding="utf-8")


def _topic_to_category(topic: str) -> str:
    return {
        "Salaries": "Salaries / Income",
        "Salaries & Income": "Salaries / Income",
        "Prices & Inflation": "Prices / Inflation",
        "Economy": "Economy / National Accounts",
    }.get(topic, topic)
