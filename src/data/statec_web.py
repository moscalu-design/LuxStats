"""Polite, domain-restricted web access for the STATEC crawlers.

Crawling rules enforced here:

* only official Luxembourg statistics domains are ever fetched;
* every request has a timeout and a descriptive User-Agent;
* fetched pages are cached on disk so a refresh does not re-download;
* a short delay is inserted between live requests.

Nothing in this module runs at app load time — it is only used by the
catalog-refresh scripts.
"""

from __future__ import annotations

import hashlib
import re
import time
from pathlib import Path
from urllib.parse import urlparse

import requests

from src.config import CACHE_DIR

# The only domains the crawlers are ever allowed to touch.
ALLOWED_DOMAINS = {
    "statistiques.public.lu",
    "data.public.lu",
    "lustat.statec.lu",
}

PAGE_CACHE_DIR = CACHE_DIR / "pages"
USER_AGENT = "LuxStats-portal/1.0 (statistics portal; contact via repository)"
REQUEST_TIMEOUT = 30
POLITE_DELAY_SECONDS = 1.0
PAGE_CACHE_TTL_SECONDS = 7 * 24 * 3600

_last_request_at = 0.0


def normalize_url(url: str, base: str = "https:") -> str:
    """Turn a protocol-relative ``//host/path`` URL into an absolute https URL."""
    url = (url or "").strip()
    if url.startswith("//"):
        return f"https:{url}"
    if url.startswith("/"):
        return url  # caller must resolve relative paths against a base
    return url


def domain_of(url: str) -> str:
    return (urlparse(url).hostname or "").lower()


def is_allowed_url(url: str) -> bool:
    """True only for official Luxembourg statistics domains over http(s)."""
    parsed = urlparse(normalize_url(url))
    if parsed.scheme not in {"http", "https"}:
        return False
    host = (parsed.hostname or "").lower()
    return any(host == d or host.endswith("." + d) for d in ALLOWED_DOMAINS)


def _cache_path(url: str) -> Path:
    digest = hashlib.sha1(url.encode("utf-8")).hexdigest()[:20]
    return PAGE_CACHE_DIR / f"{digest}.html"


def polite_get(url: str, *, force_refresh: bool = False) -> str:
    """Fetch a page politely, with caching. Raises on a disallowed domain.

    Raises :class:`requests.RequestException` on network failure so callers
    can degrade gracefully.
    """
    global _last_request_at
    url = normalize_url(url)
    if not is_allowed_url(url):
        raise ValueError(f"Refusing to fetch a non-official domain: {url}")

    cache_path = _cache_path(url)
    if not force_refresh and cache_path.exists():
        age = time.time() - cache_path.stat().st_mtime
        if age < PAGE_CACHE_TTL_SECONDS and cache_path.stat().st_size > 0:
            return cache_path.read_text(encoding="utf-8", errors="ignore")

    # Be polite: never fire two live requests back to back.
    wait = POLITE_DELAY_SECONDS - (time.time() - _last_request_at)
    if wait > 0:
        time.sleep(wait)
    resp = requests.get(
        url, headers={"User-Agent": USER_AGENT}, timeout=REQUEST_TIMEOUT
    )
    _last_request_at = time.time()
    resp.raise_for_status()

    PAGE_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(resp.text, encoding="utf-8")
    return resp.text


_HREF_RE = re.compile(r'href=["\']([^"\']+)["\']', re.IGNORECASE)


def extract_links(html: str) -> list[str]:
    """Return every absolute/protocol-relative href found in a page."""
    links: list[str] = []
    for raw in _HREF_RE.findall(html or ""):
        url = normalize_url(raw)
        if url.startswith("http"):
            links.append(url)
    return links


def extract_file_links(html: str, extensions: tuple[str, ...]) -> list[str]:
    """Return de-duplicated links whose path ends with one of ``extensions``."""
    wanted = tuple(e.lower().lstrip(".") for e in extensions)
    found: list[str] = []
    for url in extract_links(html):
        path = urlparse(url).path.lower()
        if path.rsplit(".", 1)[-1] in wanted and url not in found:
            found.append(url)
    return found
