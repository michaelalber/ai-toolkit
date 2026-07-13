"""Unit tests for models.url_to_slug."""
from __future__ import annotations

from web2md.models import url_to_slug


class TestUrlToSlug:
    def test_simple_page(self) -> None:
        assert url_to_slug("https://docs.example.com/guide/intro") == "docs-example-com_guide_intro"

    def test_trailing_slash_stripped(self) -> None:
        slug = url_to_slug("https://docs.example.com/guide/")
        assert slug == "docs-example-com_guide"

    def test_root_url(self) -> None:
        assert url_to_slug("https://example.com/") == "example-com"

    def test_deep_path(self) -> None:
        slug = url_to_slug("https://example.com/a/b/c")
        assert slug == "example-com_a_b_c"

    def test_no_path(self) -> None:
        assert url_to_slug("https://example.com") == "example-com"

    def test_special_chars_stripped(self) -> None:
        slug = url_to_slug("https://example.com/page?q=1#section")
        assert "?" not in slug
        assert "#" not in slug
