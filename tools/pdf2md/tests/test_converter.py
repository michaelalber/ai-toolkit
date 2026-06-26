"""Tests for converter helper logic (page-range parsing, output resolution, chunking)."""
from __future__ import annotations

from pathlib import Path

from pdf2md.converter import (
    _build_front_matter,
    _parse_page_range,
    _resolve_output,
    _write_chunks,
)


class TestParsePageRange:
    def test_single_range(self) -> None:
        assert _parse_page_range("1-3", total_pages=10) == [0, 1, 2]

    def test_single_page(self) -> None:
        assert _parse_page_range("5", total_pages=10) == [4]

    def test_mixed_list_and_ranges(self) -> None:
        assert _parse_page_range("1,3,5-7", total_pages=10) == [0, 2, 4, 5, 6]

    def test_range_clamped_to_total(self) -> None:
        assert _parse_page_range("8-100", total_pages=10) == [7, 8, 9]

    def test_out_of_bounds_single_page_dropped(self) -> None:
        assert _parse_page_range("99", total_pages=10) == []

    def test_duplicates_collapsed_and_sorted(self) -> None:
        assert _parse_page_range("3,1-2,2", total_pages=10) == [0, 1, 2]

    def test_whitespace_tolerated(self) -> None:
        assert _parse_page_range(" 1 , 2 ", total_pages=10) == [0, 1]


class TestResolveOutput:
    def test_explicit_output_wins(self) -> None:
        out = _resolve_output(Path("in.pdf"), Path("custom.md"), is_batch=False)
        assert out == Path("custom.md")

    def test_single_defaults_to_md_suffix(self) -> None:
        out = _resolve_output(Path("/docs/book.pdf"), None, is_batch=False)
        assert out == Path("/docs/book.md")

    def test_batch_defaults_to_output_dir(self) -> None:
        out = _resolve_output(Path("/docs/ebooks"), None, is_batch=True)
        assert out == Path("/docs/output")


class TestBuildFrontMatter:
    def test_contains_provenance_fields(self) -> None:
        fm = _build_front_matter(Path("/docs/report.pdf"), total_pages=42)
        assert fm.startswith("---\n")
        assert "source: report.pdf" in fm
        assert "pages: 42" in fm
        assert "tool: pdf2md/0.1.0" in fm
        assert fm.rstrip().endswith("---")


class TestWriteChunks:
    def test_splits_at_h1_boundaries(self, tmp_path: Path) -> None:
        markdown = (
            "# Chapter One\n\nIntro text.\n\n"
            "# Chapter Two\n\nMore text.\n"
        )
        base = tmp_path / "book.md"
        _write_chunks(markdown, base)

        files = sorted(p.name for p in tmp_path.glob("*.md"))
        # NOTE: a document that opens directly on an H1 labels that first
        # section "preamble" (there is no content preceding it to separate);
        # every subsequent H1 is slugged from its heading text.
        assert files == ["book_chapter-two.md", "book_preamble.md"]
        assert "Intro text." in (tmp_path / "book_preamble.md").read_text()
        assert "More text." in (tmp_path / "book_chapter-two.md").read_text()

    def test_content_before_first_heading_is_preamble(self, tmp_path: Path) -> None:
        markdown = "Loose intro.\n\n# Real Chapter\n\nBody.\n"
        base = tmp_path / "doc.md"
        _write_chunks(markdown, base)

        names = {p.name for p in tmp_path.glob("*.md")}
        assert "doc_preamble.md" in names
        assert "Loose intro." in (tmp_path / "doc_preamble.md").read_text()

    def test_heading_slug_strips_punctuation(self, tmp_path: Path) -> None:
        # Leading content forces the heading to start a fresh (slugged) chunk
        # rather than being absorbed into the preamble.
        markdown = "Front.\n\n# Chapter 1: Introduction!\n\nText.\n"
        base = tmp_path / "x.md"
        _write_chunks(markdown, base)

        names = {p.name for p in tmp_path.glob("*.md")}
        assert "x_chapter-1-introduction.md" in names
