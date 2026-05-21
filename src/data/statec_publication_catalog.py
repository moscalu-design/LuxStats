"""Catalog of STATEC publication annexes (PDF reports and Excel attachments).

STATEC groups publications into series ('Le logement en chiffres', 'Regards',
…). Each series index page links the individual PDF issues and, sometimes,
their Excel annexes. This module catalogs those links from a small, fixed set
of series pages — it does not crawl the whole site.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlparse

from src.config import CATALOG_DIR
from src.data.categorization import categorize, extract_keywords
from src.data.statec_web import normalize_url, polite_get

PUBLICATION_CATALOG_PATH = CATALOG_DIR / "statec_publication_catalog.json"

# Fixed set of publication series to catalog: slug -> (family, category hint).
PUBLICATION_SERIES: dict[str, tuple[str, str]] = {
    "logement-chiffres": ("Le logement en chiffres", "Housing"),
    "regards": ("Regards", ""),
    "economie-statistiques": ("Économie & Statistiques", "Economy / National Accounts"),
    "conjoncture-flash": ("Conjoncture Flash", "Economy / National Accounts"),
    "note-conjoncture": ("Note de conjoncture", "Economy / National Accounts"),
}

_SERIES_URL = "https://statistiques.public.lu/en/publications/series/{slug}.html"
_FILE_EXT = ("pdf", "xlsx", "xls")
_YEAR_RE = re.compile(r"/((?:19|20)\d{2})/")
_TAG_RE = re.compile(r"<[^>]+>")
_ANCHOR_RE = re.compile(
    r'<a\b[^>]*href=["\']([^"\']+\.(pdf|xlsx|xls))["\'][^>]*>(.*?)</a>',
    re.IGNORECASE | re.DOTALL,
)


def _clean_text(fragment: str) -> str:
    return re.sub(r"\s+", " ", _TAG_RE.sub(" ", fragment or "")).strip()


def _infer_date(url: str) -> str | None:
    match = _YEAR_RE.search(url)
    return match.group(1) if match else None


def crawl_publication_series(
    slug: str, force_refresh: bool = False
) -> list[dict[str, Any]]:
    """Catalog the PDF/Excel attachments linked from one series index page."""
    family, _ = PUBLICATION_SERIES.get(slug, (slug, ""))
    url = _SERIES_URL.format(slug=slug)
    try:
        html = polite_get(url, force_refresh=force_refresh)
    except Exception:  # noqa: BLE001 - a missing/renamed series is not fatal
        return []
    found: dict[str, dict[str, Any]] = {}
    for match in _ANCHOR_RE.finditer(html):
        file_url = normalize_url(match.group(1))
        ext = match.group(2).lower()
        text = _clean_text(match.group(3))
        if file_url in found:
            continue
        found[file_url] = {
            "file_url": file_url,
            "file_type": ext,
            "title": text,
            "publication_family": family,
            "slug": slug,
            "source_page_url": url,
            "publication_date": _infer_date(file_url),
        }
    return list(found.values())


def build_publication_catalog(force_refresh: bool = False) -> list[dict[str, Any]]:
    """Build the categorized publication-annex catalog."""
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    records: list[dict[str, Any]] = []
    for slug, (family, category_hint) in PUBLICATION_SERIES.items():
        for item in crawl_publication_series(slug, force_refresh=force_refresh):
            filename = urlparse(item["file_url"]).path.rsplit("/", 1)[-1]
            title = item["title"] or filename
            ext = item["file_type"]
            text = f"{title} {family} {filename}"
            category = category_hint or categorize(text)
            records.append(
                {
                    "source_type": "PUBLICATION_PDF" if ext == "pdf" else "PUBLICATION_EXCEL",
                    "title": title,
                    "category": category,
                    "publication_family": family,
                    "publication_date": item["publication_date"],
                    "source_page_url": item["source_page_url"],
                    "file_url": item["file_url"],
                    "file_type": ext,
                    "filename": filename,
                    "keywords": extract_keywords(text),
                    "last_seen": now,
                    "notes": f"Annex discovered on the '{family}' series page.",
                }
            )
    records.sort(key=lambda r: (r["publication_family"],
                                r["publication_date"] or "", r["filename"]))
    return records


def save_publication_catalog(records: list[dict[str, Any]]) -> None:
    CATALOG_DIR.mkdir(parents=True, exist_ok=True)
    PUBLICATION_CATALOG_PATH.write_text(
        json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def load_publication_catalog() -> list[dict[str, Any]]:
    if not PUBLICATION_CATALOG_PATH.exists():
        return []
    try:
        return json.loads(PUBLICATION_CATALOG_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
