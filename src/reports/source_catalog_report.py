"""Generate a Markdown report summarizing the unified source catalog.

The report is generated entirely from the catalog data — nothing is written
by hand — so it always reflects the most recent refresh.
"""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from typing import Any

from src.config import REPORTS_DIR
from src.data.source_catalog import (
    catalog_generated_at,
    catalog_summary,
    load_unified_source_catalog,
    recommended_next_sources,
)

REPORT_PATH = REPORTS_DIR / "statec_source_catalog_report.md"


def _counts(records: list[dict[str, Any]], key: str) -> list[tuple[str, int]]:
    counter = Counter(str(r.get(key) or "—") for r in records)
    return sorted(counter.items(), key=lambda kv: (-kv[1], kv[0]))


def _table(rows: list[tuple[str, int]], header: tuple[str, str]) -> list[str]:
    lines = [f"| {header[0]} | {header[1]} |", "| --- | ---: |"]
    lines += [f"| {name} | {count} |" for name, count in rows]
    return lines


def _section_by_category(title: str, records: list[dict[str, Any]]) -> list[str]:
    lines = [f"## {title}", ""]
    if not records:
        lines += ["_No sources of this kind were discovered._", ""]
        return lines
    lines += _table(_counts(records, "category"), ("Category", "Sources"))
    lines.append("")
    return lines


def generate_report(records: list[dict[str, Any]] | None = None) -> str:
    """Build the Markdown source-catalog report as a string."""
    records = records if records is not None else load_unified_source_catalog()
    summary = catalog_summary() if records is None else None
    generated = catalog_generated_at() or "not yet generated"
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")

    api = [r for r in records if r["source_type"] == "LUSTAT_API"]
    excel = [r for r in records if r["source_type"] in {"STATEC_EXCEL", "OTHER_FORMAT"}]
    pubs = [r for r in records if r["source_type"] in {"PUBLICATION_EXCEL", "PUBLICATION_PDF"}]
    commune = [r for r in records if r.get("geographic_level") in {"commune", "canton"}]
    housing = [r for r in records if r.get("category") == "Housing"]
    salary = [r for r in records if r.get("category") == "Salaries / Income"]
    population = [r for r in records if r.get("category") == "Population"]
    short_term = [r for r in records if r.get("recommended_for_what_changed")]
    manual = [r for r in records
              if r.get("source_type") in {"STATEC_EXCEL", "OTHER_FORMAT", "PUBLICATION_EXCEL"}
              and r.get("priority") != "high"]

    lines: list[str] = [
        "# STATEC Source Catalog Report",
        "",
        f"_Report generated: {now}_  ",
        f"_Catalog last refreshed: {generated}_",
        "",
        "## 1. Executive summary",
        "",
        f"- **Total sources cataloged:** {len(records)}",
        f"- LUSTAT API datasets: {len(api)}",
        f"- STATEC Excel / other-format files: {len(excel)}",
        f"- Publication annexes (PDF + Excel): {len(pubs)}",
        f"- Commune / canton-level sources: {len(commune)}",
        f"- High-priority sources: {len([r for r in records if r.get('priority') == 'high'])}",
        "",
        "### Sources by type",
        "",
        *_table(_counts(records, "source_type"), ("Source type", "Count")),
        "",
        "### Sources by priority",
        "",
        *_table(_counts(records, "priority"), ("Priority", "Count")),
        "",
        *_section_by_category("2. LUSTAT API datasets by category", api),
        *_section_by_category("3. STATEC Excel / other-format files by category", excel),
        *_section_by_category("4. Publication annexes by category", pubs),
        *_section_by_category("5. Commune-level sources", commune),
        *_section_by_category("6. Housing sources", housing),
        *_section_by_category("7. Salary / income sources", salary),
        *_section_by_category("8. Population sources", population),
        *_section_by_category("9. Short-term / current-indicator sources", short_term),
    ]

    lines += ["## 10. Sources requiring manual mapping", ""]
    if manual:
        lines.append(f"{len(manual)} downloadable file(s) are cataloged but not "
                     "high priority — they likely need a manual column mapping "
                     "before they can be charted. Top examples:")
        lines.append("")
        for record in manual[:20]:
            lines.append(f"- **{record['title']}** "
                         f"({record['category']}, {record['source_type']})")
    else:
        lines.append("_None — every downloadable file is already high priority._")
    lines.append("")

    lines += ["## 11. Recommended next ingestion priorities", ""]
    nxt = recommended_next_sources(limit=20) if records is None else \
        sorted([r for r in records if r.get("priority") == "high"],
               key=lambda r: r.get("priority_score", 0), reverse=True)[:20]
    if nxt:
        lines += ["| Source | Category | Type | Score | Why |",
                  "| --- | --- | --- | ---: | --- |"]
        for r in nxt:
            title = str(r["title"]).replace("|", "/")[:60]
            lines.append(f"| {title} | {r['category']} | {r['source_type']} | "
                         f"{r.get('priority_score', 0)} | {r.get('priority_reason', '')} |")
    else:
        lines.append("_No sources are currently flagged as high priority._")
    lines.append("")
    return "\n".join(lines)


def save_report(records: list[dict[str, Any]] | None = None) -> str:
    """Generate the report and write it to ``reports/``; return the path."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(generate_report(records), encoding="utf-8")
    return str(REPORT_PATH)
