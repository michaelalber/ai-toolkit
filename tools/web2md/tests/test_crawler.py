"""Unit tests for crawler.py — httpx calls mocked via respx."""
from __future__ import annotations

import pytest
import respx
import httpx

from web2md.crawler import _has_skip_extension, crawl


class TestHasSkipExtension:
    @pytest.mark.parametrize("url", [
        "https://example.com/file.pdf",
        "https://example.com/image.png",
        "https://example.com/style.css",
        "https://example.com/app.js",
    ])
    def test_skips_non_html(self, url: str) -> None:
        assert _has_skip_extension(url) is True

    @pytest.mark.parametrize("url", [
        "https://example.com/page",
        "https://example.com/guide/intro",
        "https://example.com/",
    ])
    def test_allows_html_pages(self, url: str) -> None:
        assert _has_skip_extension(url) is False


class TestCrawl:
    @respx.mock
    def test_single_page_no_links(self) -> None:
        respx.get("https://example.com/").mock(
            return_value=httpx.Response(
                200,
                text="<html><body><p>No links here.</p></body></html>",
                headers={"content-type": "text/html"},
            )
        )
        urls = crawl("https://example.com/", max_pages=10)
        assert urls == ["https://example.com/"]

    @respx.mock
    def test_follows_internal_links(self) -> None:
        respx.get("https://example.com/").mock(
            return_value=httpx.Response(
                200,
                text='<html><body><a href="/about">About</a></body></html>',
                headers={"content-type": "text/html"},
            )
        )
        respx.get("https://example.com/about").mock(
            return_value=httpx.Response(
                200,
                text="<html><body><p>About page.</p></body></html>",
                headers={"content-type": "text/html"},
            )
        )
        urls = crawl("https://example.com/", max_pages=10)
        assert "https://example.com/" in urls
        assert "https://example.com/about" in urls

    @respx.mock
    def test_does_not_follow_external_links(self) -> None:
        respx.get("https://example.com/").mock(
            return_value=httpx.Response(
                200,
                text='<html><body><a href="https://other.com/page">External</a></body></html>',
                headers={"content-type": "text/html"},
            )
        )
        urls = crawl("https://example.com/", max_pages=10)
        assert not any("other.com" in u for u in urls)

    @respx.mock
    def test_max_pages_respected(self) -> None:
        respx.get("https://example.com/").mock(
            return_value=httpx.Response(
                200,
                text=(
                    '<html><body>'
                    '<a href="/p1">1</a><a href="/p2">2</a><a href="/p3">3</a>'
                    '</body></html>'
                ),
                headers={"content-type": "text/html"},
            )
        )
        for i in range(1, 4):
            respx.get(f"https://example.com/p{i}").mock(
                return_value=httpx.Response(
                    200,
                    text="<html><body>page</body></html>",
                    headers={"content-type": "text/html"},
                )
            )
        urls = crawl("https://example.com/", max_pages=2)
        assert len(urls) <= 2

    @respx.mock
    def test_skips_failed_requests(self) -> None:
        respx.get("https://example.com/").mock(
            return_value=httpx.Response(
                200,
                text='<html><body><a href="/broken">x</a></body></html>',
                headers={"content-type": "text/html"},
            )
        )
        respx.get("https://example.com/broken").mock(
            return_value=httpx.Response(404, text="Not found")
        )
        urls = crawl("https://example.com/", max_pages=10)
        assert "https://example.com/broken" not in urls

    @respx.mock
    def test_same_prefix_restricts_crawl(self) -> None:
        respx.get("https://example.com/docs/").mock(
            return_value=httpx.Response(
                200,
                text=(
                    '<html><body>'
                    '<a href="/docs/page">Doc</a>'
                    '<a href="/blog/post">Blog</a>'
                    '</body></html>'
                ),
                headers={"content-type": "text/html"},
            )
        )
        respx.get("https://example.com/docs/page").mock(
            return_value=httpx.Response(
                200,
                text="<html><body>doc page</body></html>",
                headers={"content-type": "text/html"},
            )
        )
        urls = crawl("https://example.com/docs/", max_pages=10, same_prefix=True)
        assert not any("/blog/" in u for u in urls)
        assert any("/docs/" in u for u in urls)

    @respx.mock
    def test_max_depth_zero_stops_at_root(self) -> None:
        respx.get("https://example.com/").mock(
            return_value=httpx.Response(
                200,
                text='<html><body><a href="/about">About</a></body></html>',
                headers={"content-type": "text/html"},
            )
        )
        respx.get("https://example.com/about").mock(
            return_value=httpx.Response(
                200,
                text="<html><body>about</body></html>",
                headers={"content-type": "text/html"},
            )
        )
        urls = crawl("https://example.com/", max_pages=10, max_depth=0)
        assert urls == ["https://example.com/"]

    @respx.mock
    def test_max_depth_one_follows_direct_links_only(self) -> None:
        respx.get("https://example.com/").mock(
            return_value=httpx.Response(
                200,
                text='<html><body><a href="/about">About</a></body></html>',
                headers={"content-type": "text/html"},
            )
        )
        respx.get("https://example.com/about").mock(
            return_value=httpx.Response(
                200,
                text='<html><body><a href="/deep">Deep</a></body></html>',
                headers={"content-type": "text/html"},
            )
        )
        respx.get("https://example.com/deep").mock(
            return_value=httpx.Response(
                200,
                text="<html><body>deep</body></html>",
                headers={"content-type": "text/html"},
            )
        )
        urls = crawl("https://example.com/", max_pages=10, max_depth=1)
        assert "https://example.com/" in urls
        assert "https://example.com/about" in urls
        assert "https://example.com/deep" not in urls

    @respx.mock
    def test_max_depth_none_is_unlimited(self) -> None:
        respx.get("https://example.com/").mock(
            return_value=httpx.Response(
                200,
                text='<html><body><a href="/about">About</a></body></html>',
                headers={"content-type": "text/html"},
            )
        )
        respx.get("https://example.com/about").mock(
            return_value=httpx.Response(
                200,
                text='<html><body><a href="/deep">Deep</a></body></html>',
                headers={"content-type": "text/html"},
            )
        )
        respx.get("https://example.com/deep").mock(
            return_value=httpx.Response(
                200,
                text="<html><body>deep</body></html>",
                headers={"content-type": "text/html"},
            )
        )
        urls = crawl("https://example.com/", max_pages=10, max_depth=None)
        assert "https://example.com/deep" in urls

    @respx.mock
    def test_deduplicates_visited_urls(self) -> None:
        # Two links both pointing to the same page — should only visit once
        respx.get("https://example.com/").mock(
            return_value=httpx.Response(
                200,
                text='<html><body><a href="/p">link 1</a><a href="/p">link 2</a></body></html>',
                headers={"content-type": "text/html"},
            )
        )
        respx.get("https://example.com/p").mock(
            return_value=httpx.Response(
                200,
                text="<html><body>page</body></html>",
                headers={"content-type": "text/html"},
            )
        )
        urls = crawl("https://example.com/", max_pages=10)
        assert urls.count("https://example.com/p") == 1
