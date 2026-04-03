"""Tests for markdown_builder module."""
from __future__ import annotations

from pathlib import Path

from pdf2md.markdown_builder import build_markdown, _table_to_markdown
from pdf2md.models import Block, ExtractedPage, Span, Table


def _span(text: str, bold: bool = False, italic: bool = False, mono: bool = False) -> Span:
    return Span(
        text=text,
        font_name="Courier" if mono else "Helvetica",
        font_size=12.0,
        is_bold=bold,
        is_italic=italic,
        is_monospace=mono,
    )


def _block(text: str, heading: int | None = None, code: bool = False) -> Block:
    return Block(
        spans=[_span(text)],
        block_type="text",
        bbox=(0, 0, 100, 20),
        page_number=1,
        heading_level=heading,
        is_code_block=code,
    )


class TestTableToMarkdown:
    def test_two_column_table(self) -> None:
        table = Table(
            cells=[["Name", "Value"], ["foo", "bar"], ["baz", "qux"]],
            page_number=1,
            bbox=(0, 0, 100, 60),
        )
        md = _table_to_markdown(table)
        lines = md.splitlines()
        assert lines[0] == "| Name | Value |"
        assert lines[1] == "| --- | --- |"
        assert lines[2] == "| foo | bar |"

    def test_empty_table_returns_empty_string(self) -> None:
        table = Table(cells=[], page_number=1, bbox=(0, 0, 0, 0))
        assert _table_to_markdown(table) == ""

    def test_none_cells_become_empty_strings(self) -> None:
        table = Table(cells=[["A", None], [None, "B"]], page_number=1, bbox=(0, 0, 100, 40))
        md = _table_to_markdown(table)
        assert "| A |  |" in md
        assert "|  | B |" in md


class TestBuildMarkdown:
    def test_heading_rendered_with_hash_prefix(self) -> None:
        block = _block("Introduction", heading=1)
        page = ExtractedPage(page_number=1, blocks=[block])
        md = build_markdown([page], source_path=Path("test.pdf"), total_pages=1)
        assert "# Introduction" in md

    def test_h2_rendered_correctly(self) -> None:
        block = _block("Section", heading=2)
        page = ExtractedPage(page_number=1, blocks=[block])
        md = build_markdown([page], source_path=Path("test.pdf"), total_pages=1)
        assert "## Section" in md

    def test_code_block_wrapped_in_fences(self) -> None:
        block = _block("def foo(): pass", code=True)
        page = ExtractedPage(page_number=1, blocks=[block])
        md = build_markdown([page], source_path=Path("test.pdf"), total_pages=1)
        assert "```" in md
        assert "def foo(): pass" in md

    def test_metadata_front_matter_included(self) -> None:
        page = ExtractedPage(page_number=1, blocks=[_block("text")])
        md = build_markdown(
            [page],
            source_path=Path("report.pdf"),
            total_pages=5,
            include_metadata=True,
        )
        assert md.startswith("---")
        assert "source: report.pdf" in md
        assert "pages: 5" in md

    def test_metadata_not_included_by_default(self) -> None:
        page = ExtractedPage(page_number=1, blocks=[_block("text")])
        md = build_markdown([page], source_path=Path("report.pdf"), total_pages=1)
        assert not md.startswith("---")

    def test_bold_span_rendered_with_asterisks(self) -> None:
        block = Block(
            spans=[_span("Important", bold=True)],
            block_type="text",
            bbox=(0, 0, 100, 20),
            page_number=1,
        )
        page = ExtractedPage(page_number=1, blocks=[block])
        md = build_markdown([page], source_path=Path("t.pdf"), total_pages=1)
        assert "**Important**" in md
