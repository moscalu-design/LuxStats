#!/usr/bin/env python3
"""Generate the Markdown STATEC source-catalog report.

Reads the cached unified catalog (run scripts/refresh_source_catalog.py first)
and writes reports/statec_source_catalog_report.md.

Usage:
    python scripts/generate_source_report.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.data.source_catalog import load_unified_source_catalog  # noqa: E402
from src.reports.source_catalog_report import save_report  # noqa: E402


def main() -> int:
    records = load_unified_source_catalog()
    if not records:
        print("No catalog found. Run scripts/refresh_source_catalog.py first.",
              file=sys.stderr)
        return 1
    path = save_report(records)
    print(f"Wrote report for {len(records)} sources -> {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
