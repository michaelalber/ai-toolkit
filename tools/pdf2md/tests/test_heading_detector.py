"""Tests for heading_detector module."""
from __future__ import annotations

import pytest

from pdf2md.heading_detector import (
    annotate_headings,
    compute_document_stats,
    strip_heading_noise,
)
from pdf2md.models import Block, ExtractedPage, Span


class TestStripHeadingNoise:
    def test_removes_dotted_leader_and_page_number(self) -> None:
        assert strip_heading_noise("Foundations .......... 1") == "Foundations"

    def test_removes_trailing_folio(self) -> None:
        assert strip_heading_noise("What is API security? 3") == "What is API security?"

    def test_preserves_numeric_section_prefix(self) -> None:
        assert strip_heading_noise("1.1 An analogy 4") == "1.1 An analogy"

    def test_leaves_clean_heading_untouched(self) -> None:
        assert strip_heading_noise("Secure API development") == "Secure API development"

    def test_preserves_short_structural_heading_with_number(self) -> None:
        # "OAuth 2" / "Chapter 2" must keep their number — not a TOC folio.
        assert strip_heading_noise("OAuth 2") == "OAuth 2"
        assert strip_heading_noise("Chapter 2") == "Chapter 2"


def _make_span(text: str, size: float, bold: bool = False) -> Span:
    return Span(
        text=text,
        font_name="Helvetica",
        font_size=size,
        is_bold=bold,
        is_italic=False,
        is_monospace=False,
    )


def _make_block(text: str, size: float, bold: bool = False) -> Block:
    return Block(
        spans=[_make_span(text, size, bold)],
        block_type="text",
        bbox=(0, 0, 100, 20),
        page_number=1,
    )


def _make_page(*blocks: Block, sizes: list[float] | None = None) -> ExtractedPage:
    page = ExtractedPage(page_number=1, blocks=list(blocks))
    if sizes is not None:
        page.raw_font_sizes = sizes
    else:
        page.raw_font_sizes = [s for b in blocks for s in (span.font_size for span in b.spans)]
    return page


class TestComputeDocumentStats:
    def test_median_with_uniform_sizes(self) -> None:
        page = _make_page(
            *[_make_block("text", 12.0) for _ in range(10)],
        )
        stats = compute_document_stats([page])
        assert stats.median_font_size == pytest.approx(12.0)
        assert stats.h1_threshold == pytest.approx(12.0 * 1.4)
        assert stats.h2_threshold == pytest.approx(12.0 * 1.2)

    def test_falls_back_to_12pt_when_no_sizes(self) -> None:
        page = ExtractedPage(page_number=1)
        stats = compute_document_stats([page])
        assert stats.median_font_size == pytest.approx(12.0)

    def test_uses_all_pages_not_just_first(self) -> None:
        # 9 pages of 10pt body, 1 page with a 24pt title
        pages = [_make_page(_make_block("body", 10.0)) for _ in range(9)]
        pages.append(_make_page(_make_block("Title", 24.0)))
        stats = compute_document_stats(pages)
        # Median should still be dominated by 10pt spans
        assert stats.median_font_size == pytest.approx(10.0)


class TestAnnotateHeadings:
    def test_large_font_is_h1(self) -> None:
        block = _make_block("Big Title", 24.0)
        # Need enough 12pt body text so the document median stays at 12pt,
        # making the H1 threshold 16.8pt — well below the 24pt title.
        body_blocks = [_make_block(f"body {i}", 12.0) for i in range(9)]
        page = _make_page(block, *body_blocks)
        stats = compute_document_stats([page])
        annotate_headings([page], stats)
        assert block.heading_level == 1

    def test_medium_font_is_h2(self) -> None:
        block = _make_block("Section", 15.0)
        page = _make_page(block, *[_make_block("body", 12.0) for _ in range(8)])
        stats = compute_document_stats([page])
        annotate_headings([page], stats)
        assert block.heading_level == 2

    def test_body_size_is_not_heading(self) -> None:
        block = _make_block("Normal paragraph", 12.0)
        page = _make_page(*[_make_block("body", 12.0) for _ in range(10)])
        stats = compute_document_stats([page])
        annotate_headings([page], stats)
        assert block.heading_level is None

    def test_all_caps_bold_same_size_is_h3(self) -> None:
        block = _make_block("INTRODUCTION", 12.0, bold=True)
        page = _make_page(block, *[_make_block("body", 12.0) for _ in range(9)])
        stats = compute_document_stats([page])
        annotate_headings([page], stats)
        assert block.heading_level == 3

    def test_all_sizes_equal_no_headings(self) -> None:
        blocks = [_make_block("text", 12.0) for _ in range(5)]
        page = _make_page(*blocks)
        stats = compute_document_stats([page])
        annotate_headings([page], stats)
        assert all(b.heading_level is None for b in blocks)
