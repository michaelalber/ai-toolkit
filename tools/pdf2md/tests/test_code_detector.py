"""Tests for code_detector module."""
from __future__ import annotations

from pdf2md.code_detector import annotate_code_blocks
from pdf2md.models import Block, ExtractedPage, Span


def _span(text: str, monospace: bool) -> Span:
    return Span(
        text=text,
        font_name="Courier" if monospace else "Helvetica",
        font_size=10.0,
        is_bold=False,
        is_italic=False,
        is_monospace=monospace,
    )


def _block(spans: list[Span], page: int = 1) -> Block:
    return Block(
        spans=spans,
        block_type="text",
        bbox=(0, 0, 100, 20),
        page_number=page,
    )


class TestAnnotateCodeBlocks:
    def test_all_monospace_block_is_code(self) -> None:
        block = _block([_span("def foo():", True), _span("    pass", True)])
        page = ExtractedPage(page_number=1, blocks=[block])
        annotate_code_blocks([page])
        assert block.is_code_block is True

    def test_no_monospace_block_is_not_code(self) -> None:
        block = _block([_span("Regular text.", False)])
        page = ExtractedPage(page_number=1, blocks=[block])
        annotate_code_blocks([page])
        assert block.is_code_block is False

    def test_mixed_block_is_not_code(self) -> None:
        block = _block([_span("See ", False), _span("foo()", True), _span(" for details.", False)])
        page = ExtractedPage(page_number=1, blocks=[block])
        annotate_code_blocks([page])
        assert block.is_code_block is False

    def test_adjacent_monospace_blocks_are_merged(self) -> None:
        b1 = _block([_span("line one", True)])
        b2 = _block([_span("line two", True)])
        page = ExtractedPage(page_number=1, blocks=[b1, b2])
        annotate_code_blocks([page])
        # After merge, only one block remains
        assert len(page.blocks) == 1
        assert page.blocks[0].is_code_block is True
        assert len(page.blocks[0].spans) == 2

    def test_non_adjacent_code_blocks_not_merged(self) -> None:
        b1 = _block([_span("code", True)])
        b_text = _block([_span("some prose", False)])
        b2 = _block([_span("more code", True)])
        page = ExtractedPage(page_number=1, blocks=[b1, b_text, b2])
        annotate_code_blocks([page])
        assert len(page.blocks) == 3
        assert page.blocks[0].is_code_block is True
        assert page.blocks[1].is_code_block is False
        assert page.blocks[2].is_code_block is True
