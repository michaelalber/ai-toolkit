from __future__ import annotations

import re
import unicodedata
from collections import Counter

from pdf2md.models import Block, ExtractedPage, Span

# Patterns for artifacts that should be removed
_PAGE_NUMBER_RE = re.compile(r"^\s*\d+\s*$")
_PAGE_OF_RE = re.compile(r"^\s*[Pp]age\s+\d+\s+of\s+\d+\s*$")
_MIN_PAGES_FOR_HEADER_DETECTION = 3


def _block_text(block: Block) -> str:
    return " ".join(span.text for span in block.spans).strip()


def _detect_running_headers_footers(pages: list[ExtractedPage]) -> set[str]:
    """Return text strings that appear as first or last block on 3+ pages."""
    if len(pages) < _MIN_PAGES_FOR_HEADER_DETECTION:
        return set()

    first_block_texts: list[str] = []
    last_block_texts: list[str] = []

    for page in pages:
        text_blocks = [b for b in page.blocks if b.block_type == "text" and b.spans]
        if text_blocks:
            first_block_texts.append(_block_text(text_blocks[0]))
            last_block_texts.append(_block_text(text_blocks[-1]))

    recurring: set[str] = set()
    for text, count in Counter(first_block_texts).items():
        if text and count >= _MIN_PAGES_FOR_HEADER_DETECTION:
            recurring.add(text)
    for text, count in Counter(last_block_texts).items():
        if text and count >= _MIN_PAGES_FOR_HEADER_DETECTION:
            recurring.add(text)

    return recurring


def _normalize_text(text: str) -> str:
    """Apply Unicode NFKC normalization to resolve ligatures, smart quotes, etc."""
    return unicodedata.normalize("NFKC", text)


def _clean_span(span: Span) -> Span:
    return Span(
        text=_normalize_text(span.text),
        font_name=span.font_name,
        font_size=span.font_size,
        is_bold=span.is_bold,
        is_italic=span.is_italic,
        is_monospace=span.is_monospace,
    )


def clean_pages(pages: list[ExtractedPage]) -> list[ExtractedPage]:
    """Remove artifacts and normalize text across all pages.

    Mutations performed:
    - Strip running headers and footers (same text on 3+ pages).
    - Remove lone page-number lines.
    - Apply Unicode NFKC normalization to all span text.
    - Drop blocks that become empty after cleaning.
    """
    recurring = _detect_running_headers_footers(pages)

    cleaned: list[ExtractedPage] = []
    for page in pages:
        clean_blocks: list[Block] = []
        for block in page.blocks:
            if block.block_type != "text":
                clean_blocks.append(block)
                continue

            text = _block_text(block)

            # Remove page numbers and running headers/footers
            if _PAGE_NUMBER_RE.match(text) or _PAGE_OF_RE.match(text):
                continue
            if text in recurring:
                continue

            # Normalize span text
            normalized_spans = [_clean_span(s) for s in block.spans]
            # Drop spans that became empty after normalization
            normalized_spans = [s for s in normalized_spans if s.text.strip()]
            if not normalized_spans:
                continue

            clean_block = Block(
                spans=normalized_spans,
                block_type=block.block_type,
                bbox=block.bbox,
                page_number=block.page_number,
                heading_level=block.heading_level,
                is_code_block=block.is_code_block,
            )
            clean_blocks.append(clean_block)

        cleaned.append(
            ExtractedPage(
                page_number=page.page_number,
                blocks=clean_blocks,
                tables=page.tables,
                image_paths=page.image_paths,
                raw_font_sizes=page.raw_font_sizes,
            )
        )

    return cleaned
