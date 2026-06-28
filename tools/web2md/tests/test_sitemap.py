"""Unit tests for sitemap.py — httpx calls mocked via respx."""
from __future__ import annotations

import pytest
import respx
import httpx

from conftest import SAMPLE_SITEMAP, SITEMAP_INDEX
from web2md.sitemap import fetch_sitemap_urls


class TestFetchSitemapUrls:
    @respx.mock
    def test_returns_all_page_urls(self) -> None:
        respx.get("https://example.com/sitemap.xml").mock(
            return_value=httpx.Response(
                200,
                text=SAMPLE_SITEMAP,
                headers={"content-type": "application/xml"},
            )
        )
        urls = fetch_sitemap_urls("https://example.com/sitemap.xml")
        assert "https://example.com/" in urls
        assert "https://example.com/about" in urls
        assert "https://example.com/guide" in urls
        assert len(urls) == 3

    @respx.mock
    def test_follows_sitemap_index(self) -> None:
        respx.get("https://example.com/sitemap-index.xml").mock(
            return_value=httpx.Response(200, text=SITEMAP_INDEX)
        )
        respx.get("https://example.com/sitemap-pages.xml").mock(
            return_value=httpx.Response(200, text=SAMPLE_SITEMAP)
        )
        urls = fetch_sitemap_urls("https://example.com/sitemap-index.xml")
        assert len(urls) == 3

    @respx.mock
    def test_skips_unreachable_sitemap(self) -> None:
        respx.get("https://example.com/sitemap.xml").mock(
            return_value=httpx.Response(404, text="Not found")
        )
        urls = fetch_sitemap_urls("https://example.com/sitemap.xml")
        assert urls == []

    @respx.mock
    def test_returns_empty_on_invalid_xml(self) -> None:
        respx.get("https://example.com/sitemap.xml").mock(
            return_value=httpx.Response(200, text="<not valid xml")
        )
        urls = fetch_sitemap_urls("https://example.com/sitemap.xml")
        assert urls == []
