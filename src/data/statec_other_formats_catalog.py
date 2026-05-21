"""Catalog of STATEC 'Data - other formats' Excel / CSV files.

STATEC publishes a single 'list of tables by theme' page that links directly
to its downloadable Excel and CSV tables. Cataloging it is therefore one
polite request — no deep crawling needed.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlparse

from src.config import CATALOG_DIR
from src.data.categorization import (
    categorize,
    extract_keywords,
    infer_geographic_level,
    looks_like_housing_data,
    looks_like_short_term_indicator,
)
from src.data.statec_web import normalize_url, polite_get

OTHER_FORMATS_CATALOG_PATH = CATALOG_DIR / "statec_other_formats_catalog.json"

# The one page that links STATEC's downloadable tables, in both languages.
SEED_PAGES = [
    "https://statistiques.public.lu/en/donnees/liste-tableaux-par-theme.html",
    "https://statistiques.public.lu/en/donnees/indicateurs-court-terme.html",
]

_EXCEL_EXT = {"xlsx", "xls"}
_OTHER_EXT = {"csv", "zip"}
_DATA_EXT = _EXCEL_EXT | _OTHER_EXT

# Anchor with a data-file href: capture href, extension and link text.
_ANCHOR_RE = re.compile(
    r'<a\b[^>]*href=["\']([^"\']+\.(xlsx|xls|csv|zip))["\'][^>]*>(.*?)</a>',
    re.IGNORECASE | re.DOTALL,
)
_TAG_RE = re.compile(r"<[^>]+>")


def _clean_text(html_fragment: str) -> str:
    return re.sub(r"\s+", " ", _TAG_RE.sub(" ", html_fragment or "")).strip()


def crawl_other_formats(force_refresh: bool = False) -> list[dict[str, Any]]:
    """Discover STATEC other-format data files from the seed pages.

    Returns raw discoveries: ``file_url``, ``title``, ``source_page_url``.
    Network failures are swallowed per page so a partial catalog still builds.
    """
    discoveries: dict[str, dict[str, Any]] = {}
    for page_url in SEED_PAGES:
        try:
            html = polite_get(page_url, force_refresh=force_refresh)
        except Exception:  # noqa: BLE001 - skip an unreachable page
            continue
        for match in _ANCHOR_RE.finditer(html):
            file_url = normalize_url(match.group(1))
            title = _clean_text(match.group(3))
            if file_url not in discoveries:
                discoveries[file_url] = {
                    "file_url": file_url,
                    "title": title,
                    "source_page_url": page_url,
                }
            elif not discoveries[file_url]["title"] and title:
                discoveries[file_url]["title"] = title
    return list(discoveries.values())


def _filename(file_url: str) -> str:
    return urlparse(file_url).path.rsplit("/", 1)[-1]


def build_other_formats_catalog(force_refresh: bool = False) -> list[dict[str, Any]]:
    """Build the categorized other-formats catalog."""
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    records: list[dict[str, Any]] = []
    for item in crawl_other_formats(force_refresh=force_refresh):
        file_url = item["file_url"]
        filename = _filename(file_url)
        file_type = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        title = item["title"] or filename
        # The URL path (e.g. .../economie-totale-prix/prix/E5012.xls) carries
        # strong category signal alongside the human title.
        text = f"{title} {file_url}"
        records.append(
            {
                "source_type": "STATEC_EXCEL" if file_type in _EXCEL_EXT else "OTHER_FORMAT",
                "title": title,
                "category": categorize(text),
                "source_page_url": item["source_page_url"],
                "file_url": file_url,
                "file_type": file_type,
                "filename": filename,
                "language": "fr" if "/fr/" in file_url else
                            ("en" if "/en/" in file_url else "unknown"),
                "publication_date": None,
                "keywords": extract_keywords(text),
                "geographic_level": infer_geographic_level(text),
                "looks_commune_level": infer_geographic_level(text) in {"commune", "canton"},
                "looks_housing": looks_like_housing_data(text),
                "looks_short_term": looks_like_short_term_indicator(text),
                "should_import": file_type in _DATA_EXT,
                "last_seen": now,
                "notes": "Discovered from the STATEC list-of-tables-by-theme page.",
            }
        )
    records.sort(key=lambda r: (r["category"], r["filename"]))
    return records


def save_other_formats_catalog(records: list[dict[str, Any]]) -> None:
    CATALOG_DIR.mkdir(parents=True, exist_ok=True)
    OTHER_FORMATS_CATALOG_PATH.write_text(
        json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def load_other_formats_catalog() -> list[dict[str, Any]]:
    if not OTHER_FORMATS_CATALOG_PATH.exists():
        return []
    try:
        return json.loads(OTHER_FORMATS_CATALOG_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
