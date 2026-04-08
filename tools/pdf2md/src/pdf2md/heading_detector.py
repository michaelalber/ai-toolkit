from __future__ import annotations

import statistics

from pdf2md.models import Block, DocumentStats, ExtractedPage


def compute_document_stats(pages: list[ExtractedPage]) -> DocumentStats:
    """Compute font-size thresholds from all spans in the document.

    Uses the median body font size as a baseline, then applies multipliers
    to derive heading thresholds.  Scanning the full document (not per-page)
    prevents false positives from locally large fonts.
    """
    all_sizes: list[float] = []
    for page in pages:
        all_sizes.extend(page.raw_font_sizes)

    if not all_sizes:
        # Fallback: assume 12pt body
        median = 12.0
    else:
        median = statistics.median(all_sizes)

    return DocumentStats(
        median_font_size=median,
        h1_threshold=median * 1.4,
        h2_threshold=median * 1.2,
        h3_threshold=median * 1.05,
    )


def _block_max_font_size(block: Block) -> float:
    if not block.spans:
        return 0.0
    return max(span.font_size for span in block.spans)


def _block_is_all_bold(block: Block) -> bool:
    return bool(block.spans) and all(span.is_bold for span in block.spans)


def _block_is_all_caps(block: Block) -> bool:
    text = "".join(span.text for span in block.spans).strip()
    return bool(text) and text == text.upper() and any(c.isalpha() for c in text)


def annotate_headings(pages: list[ExtractedPage], stats: DocumentStats) -> None:
    """Mutate blocks in-place to set ``heading_level`` (1, 2, 3, or None)."""
    for page in pages:
        for block in page.blocks:
            if block.block_type != "text" or not block.spans:
                continue

            max_size = _block_max_font_size(block)

            if max_size >= stats.h1_threshold:
                block.heading_level = 1
            elif max_size >= stats.h2_threshold:
                block.heading_level = 2
            elif max_size >= stats.h3_threshold and _block_is_all_bold(block):
                block.heading_level = 3
            elif (
                _block_is_all_caps(block)
                and _block_is_all_bold(block)
                and max_size >= stats.median_font_size * 0.95
            ):
                # Same-size ALL-CAPS bold lines treated as H3
                block.heading_level = 3
            else:
                block.heading_level = None
