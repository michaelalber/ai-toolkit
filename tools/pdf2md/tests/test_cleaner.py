"""Tests for cleaner module."""
from __future__ import annotations

from pdf2md.cleaner import clean_pages
from pdf2md.models import Block, ExtractedPage, Span


def _span(text: str) -> Span:
    return Span(text=text, font_name="Helvetica", font_size=12.0, is_bold=False, is_italic=False, is_monospace=False)


def _text_block(text: str, page: int = 1) -> Block:
    return Block(spans=[_span(text)], block_type="text", bbox=(0, 0, 100, 20), page_number=page)


class TestCleanPages:
    def test_removes_lone_page_numbers(self) -> None:
        block = _text_block("42")
        page = ExtractedPage(page_number=1, blocks=[block])
        cleaned = clean_pages([page])
        assert all(b.spans[0].text != "42" for b in cleaned[0].blocks if b.spans)

    def test_removes_page_of_pattern(self) -> None:
        block = _text_block("Page 3 of 10")
        page = ExtractedPage(page_number=1, blocks=[block])
        cleaned = clean_pages([page])
        assert len(cleaned[0].blocks) == 0

    def test_removes_running_header_appearing_on_3_plus_pages(self) -> None:
        pages = [
            ExtractedPage(
                page_number=i,
                blocks=[_text_block("Running Header", page=i), _text_block(f"Content {i}", page=i)],
            )
            for i in range(1, 6)
        ]
        cleaned = clean_pages(pages)
        for page in cleaned:
            texts = [" ".join(s.text for s in b.spans) for b in page.blocks]
            assert "Running Header" not in texts

    def test_preserves_unique_content(self) -> None:
        block = _text_block("Unique paragraph that appears once.")
        page = ExtractedPage(page_number=1, blocks=[block])
        cleaned = clean_pages([page])
        assert len(cleaned[0].blocks) == 1

    def test_unicode_normalization_resolves_ligatures(self) -> None:
        # 'ﬁ' is the fi ligature (U+FB01); NFKC should normalize it to 'fi'
        block = _text_block("\ufb01le")
        page = ExtractedPage(page_number=1, blocks=[block])
        cleaned = clean_pages([page])
        assert cleaned[0].blocks[0].spans[0].text == "file"
