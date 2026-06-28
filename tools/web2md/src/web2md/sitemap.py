"""Sitemap.xml parser — supports standard sitemaps and sitemap index files."""
from __future__ import annotations

import xml.etree.ElementTree as ET

import httpx
from rich.console import Console

console = Console(stderr=True)

_MAX_SITEMAP_DEPTH = 3


def fetch_sitemap_urls(sitemap_url: str) -> list[str]:
    """Return all page URLs declared in sitemap_url.

    Follows sitemap index files recursively (up to _MAX_SITEMAP_DEPTH levels).
    """
    urls: list[str] = []
    _collect(sitemap_url, urls, depth=0)
    return urls


def _collect(url: str, acc: list[str], depth: int) -> None:
    if depth > _MAX_SITEMAP_DEPTH:
        return

    try:
        response = httpx.get(url, follow_redirects=True, timeout=30)
        response.raise_for_status()
    except Exception as exc:
        console.print(f"[yellow]Skipping sitemap {url}: {exc}[/]")
        return

    try:
        root = ET.fromstring(response.text)
    except ET.ParseError as exc:
        console.print(f"[yellow]Could not parse sitemap XML at {url}: {exc}[/]")
        return

    ns = _extract_ns(root.tag)

    # Sitemap index — each <sitemap> child points to another sitemap
    for child in root.findall(f"{ns}sitemap"):
        loc = child.findtext(f"{ns}loc")
        if loc:
            _collect(loc.strip(), acc, depth + 1)

    # Regular sitemap — each <url> child is a page
    for child in root.findall(f"{ns}url"):
        loc = child.findtext(f"{ns}loc")
        if loc:
            acc.append(loc.strip())


def _extract_ns(tag: str) -> str:
    """Return the namespace prefix string (e.g. '{http://...}') from an XML tag."""
    if tag.startswith("{"):
        return "{" + tag[1 : tag.index("}")] + "}"
    return ""
