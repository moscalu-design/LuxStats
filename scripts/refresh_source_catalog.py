#!/usr/bin/env python3
"""Refresh the unified STATEC source catalog.

This script performs network access (LUSTAT API + a few official STATEC
pages). It is intentionally NOT run at app load time — the Streamlit app
loads the cached JSON catalogs that this script produces.

Usage:
    python scripts/refresh_source_catalog.py [--force]

    --force   bypass page/dataflow caches and re-download everything
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.data.source_catalog import refresh_unified_source_catalog  # noqa: E402


def main() -> int:
    force = "--force" in sys.argv
    print("Refreshing the STATEC source catalog"
          + (" (forced re-download)" if force else "") + " …")
    try:
        counts = refresh_unified_source_catalog(force_refresh=force)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: catalog refresh failed: {exc}", file=sys.stderr)
        return 1
    print("Catalog refreshed:")
    for key, value in counts.items():
        print(f"  {key:>14}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
