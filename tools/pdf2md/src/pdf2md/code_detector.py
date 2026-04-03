from __future__ import annotations

from pdf2md.models import Block, ExtractedPage


def _block_all_monospace(block: Block) -> bool:
    return bool(block.spans) and all(span.is_monospace for span in block.spans)


def _block_any_monospace(block: Block) -> bool:
    return any(span.is_monospace for span in block.spans)


def annotate_code_blocks(pages: list[ExtractedPage]) -> None:
    """Mutate blocks in-place to set ``is_code_block``.

    Merges adjacent all-monospace text blocks into a single code block by
    joining their spans.  Mixed blocks (some monospace, some not) are left
    for the markdown builder to handle at the span level.
    """
    for page in pages:
        _merge_adjacent_code_blocks(page.blocks)

    for page in pages:
        for block in page.blocks:
            if block.block_type == "text" and _block_all_monospace(block):
                block.is_code_block = True


def _merge_adjacent_code_blocks(blocks: list[Block]) -> None:
    """Merge consecutive all-monospace blocks into one in-place."""
    i = 0
    while i < len(blocks) - 1:
        current = blocks[i]
        nxt = blocks[i + 1]
        if (
            current.block_type == "text"
            and nxt.block_type == "text"
            and _block_all_monospace(current)
            and _block_all_monospace(nxt)
        ):
            # Absorb next block's spans into current
            current.spans.extend(nxt.spans)
            # Expand bbox to union of both
            cx0, cy0, cx1, cy1 = current.bbox
            nx0, ny0, nx1, ny1 = nxt.bbox
            current.bbox = (min(cx0, nx0), min(cy0, ny0), max(cx1, nx1), max(cy1, ny1))
            del blocks[i + 1]
            # Don't advance i — check again in case the next block also qualifies
        else:
            i += 1
