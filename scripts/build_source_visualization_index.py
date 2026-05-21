#!/usr/bin/env python3
"""Build the cached source visualization readiness index."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.data.source_visualization import (
    build_source_visualization_index,
    save_source_visualization_index,
    save_visualization_report,
    visualization_summary,
)


def main() -> None:
    index = build_source_visualization_index()
    save_source_visualization_index(index)
    save_visualization_report(index)
    summary = visualization_summary(index)
    print(
        "Built source visualization index: "
        f"{summary['total']} sources, "
        f"{summary['chart_ready']} chart-ready, "
        f"{summary['preview_ready']} preview-ready, "
        f"{summary['needs_mapping']} needing mapping."
    )


if __name__ == "__main__":
    main()
