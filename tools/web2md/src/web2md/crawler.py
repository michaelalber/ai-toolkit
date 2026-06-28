"""BFS web crawler for same-domain link discovery."""
from __future__ import annotations

from collections import deque
from typing import Optional
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup
from rich.console import Console

console = Console(stderr=True)

# Suffixes that are not HTML pages and should never be queued as crawl targets.
_SKIP_EXTENSIONS = {
    ".pdf", ".zip", ".tar", ".gz", ".png", ".jpg", ".jpeg", ".gif",
    ".svg", ".ico", ".woff", ".woff2", ".ttf", ".eot", ".mp4", ".mp3",
    ".webm", ".css", ".js", ".json", ".xml",
}


def crawl(
    start_url: str,
    max_pages: int,
    same_prefix: bool = False,
    max_depth: Optional[int] = None,
    verbose: bool = False,
) -> list[str]:
    """BFS from start_url; return discovered page URLs in visit order.

    By default stays on the same domain. With same_prefix=True, only follows
    links whose URL begins with start_url (useful for a docs subtree).

    max_depth bounds how many link-hops from start_url to follow: the root is
    depth 0, its direct links are depth 1, and so on. None (the default) means
    no depth limit — crawling is bounded only by max_pages.
    """
    parsed = urlparse(start_url)
    allowed_netloc = parsed.netloc

    def is_allowed(url: str) -> bool:
        p = urlparse(url)
        if p.netloc != allowed_netloc:
            return False
        if same_prefix and not url.startswith(start_url):
            return False
        return True

    visited: set[str] = set()
    queue: deque[tuple[str, int]] = deque([(start_url, 0)])
    result: list[str] = []

    while queue and len(result) < max_pages:
        url, depth = queue.popleft()
        url = url.split("#")[0]  # strip fragment
        if url in visited:
            continue
        visited.add(url)

        if _has_skip_extension(url):
            continue

        try:
            response = httpx.get(url, follow_redirects=True, timeout=30)
            response.raise_for_status()
        except Exception as exc:
            if verbose:
                console.print(f"[yellow]Skipping {url}: {exc}[/]")
            continue

        content_type = response.headers.get("content-type", "")
        if "html" not in content_type:
            continue

        result.append(url)
        if verbose:
            console.print(f"  [dim]{len(result)}/{max_pages}[/] {url}")

        # Stop expanding links once we have reached the configured depth.
        if max_depth is not None and depth >= max_depth:
            continue

        soup = BeautifulSoup(response.text, "html.parser")
        base = f"{parsed.scheme}://{parsed.netloc}"
        for tag in soup.find_all("a", href=True):
            href: str = tag["href"].split("#")[0]
            if not href or href.startswith("mailto:") or href.startswith("javascript:"):
                continue
            absolute = urljoin(base, href)
            if is_allowed(absolute) and absolute not in visited:
                queue.append((absolute, depth + 1))

    return result


def _has_skip_extension(url: str) -> bool:
    path = urlparse(url).path.lower()
    return any(path.endswith(ext) for ext in _SKIP_EXTENSIONS)
