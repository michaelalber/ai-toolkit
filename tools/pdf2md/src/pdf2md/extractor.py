from __future__ import annotations

from pathlib import Path

from rich.console import Console
from rich.progress import track

from pdf2md.models import Block, ExtractedPage, Span

console = Console(stderr=True)

# PyMuPDF font flags
_FLAG_BOLD = 1 << 4
_FLAG_ITALIC = 1 << 1

# Monospace font name pattern (compiled once at import)
import re

_MONOSPACE_RE = re.compile(
    r"courier|monaco|consolas|menlo|inconsolata|"
    r"dejavu.?mono|jetbrains.?mono|fira.?code|"
    r"source.?code|lucida.?console|andale.?mono|"
    r"liberation.?mono|noto.?mono|ubuntu.?mono",
    re.IGNORECASE,
)


def _is_monospace(font_name: str, font_flags: int) -> bool:
    # Bit 0 in PDF font flags = FixedPitch
    if font_flags & 1:
        return True
    return bool(_MONOSPACE_RE.search(font_name))


def _span_from_raw(raw: dict) -> Span:
    flags = raw.get("flags", 0)
    font_name: str = raw.get("font", "")
    font_size: float = raw.get("size", 12.0)
    return Span(
        text=raw.get("text", ""),
        font_name=font_name,
        font_size=font_size,
        is_bold=bool(flags & _FLAG_BOLD),
        is_italic=bool(flags & _FLAG_ITALIC),
        is_monospace=_is_monospace(font_name, flags),
    )


def extract_pages(
    doc: object,
    page_indices: list[int],
    verbose: bool = False,
) -> list[ExtractedPage]:
    """Extract structured page data from an open fitz.Document.

    Args:
        doc: An open ``fitz.Document`` instance.
        page_indices: 0-based list of page indices to process.
        verbose: When True, show a progress bar.

    Returns:
        List of :class:`~pdf2md.models.ExtractedPage` in page order.
    """
    results: list[ExtractedPage] = []
    iterator = (
        track(page_indices, description="Extracting pages…", console=console)
        if verbose
        else page_indices
    )

    for idx in iterator:
        page = doc[idx]  # type: ignore[index]
        page_data = page.get_text("dict", flags=0)  # type: ignore[attr-defined]

        extracted = ExtractedPage(page_number=idx + 1)

        for raw_block in page_data.get("blocks", []):
            block_type_code: int = raw_block.get("type", 0)

            if block_type_code == 1:
                # Image block — defer to image_extractor; record placeholder
                bbox = tuple(raw_block.get("bbox", (0, 0, 0, 0)))
                extracted.blocks.append(
                    Block(
                        spans=[],
                        block_type="image",
                        bbox=bbox,  # type: ignore[arg-type]
                        page_number=idx + 1,
                    )
                )
                continue

            # Text block: collect lines → spans
            spans: list[Span] = []
            for line in raw_block.get("lines", []):
                for raw_span in line.get("spans", []):
                    text = raw_span.get("text", "").strip()
                    if not text:
                        continue
                    span = _span_from_raw(raw_span)
                    spans.append(span)
                    extracted.raw_font_sizes.append(span.font_size)

            if not spans:
                continue

            bbox = tuple(raw_block.get("bbox", (0, 0, 0, 0)))
            extracted.blocks.append(
                Block(
                    spans=spans,
                    block_type="text",
                    bbox=bbox,  # type: ignore[arg-type]
                    page_number=idx + 1,
                )
            )

        results.append(extracted)

    return results
