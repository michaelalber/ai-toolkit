"""Engine selection and auto-detection for pdf2md."""
from __future__ import annotations

from pathlib import Path
from typing import Literal

from rich.console import Console

from pdf2md.engines.base import Engine
from pdf2md.engines.docling_engine import DoclingEngine
from pdf2md.engines.fast import FastEngine

console = Console(stderr=True)

# Minimum average characters per sampled page to consider a PDF text-extractable.
# Scanned PDFs have ~0 extractable chars; real digital PDFs have hundreds or more.
# 50 leaves headroom above empty while staying well below any real document.
_TEXT_THRESHOLD = 50
_SAMPLE_PAGES = 3


def _avg_chars(pdf_path: Path) -> float:
    """Return the average extractable character count across the first few pages."""
    try:
        import fitz  # type: ignore[import-untyped]

        doc = fitz.open(str(pdf_path))
        sample = min(_SAMPLE_PAGES, doc.page_count)
        if sample == 0:
            doc.close()
            return 0.0
        total = sum(len(doc[i].get_text()) for i in range(sample))
        doc.close()
        return total / sample
    except Exception:
        return 0.0


def select_engine(
    choice: Literal["auto", "fast", "docling"],
    pdf_path: Path,
) -> Engine:
    """Return an :class:`Engine` instance for *choice*.

    ``auto`` samples up to three pages to estimate whether the PDF has a
    text layer.  If the average character count falls below the threshold
    (likely a scanned document), DoclingEngine is chosen; otherwise FastEngine.
    """
    if choice == "fast":
        return FastEngine()
    if choice == "docling":
        return DoclingEngine()

    # auto
    avg = _avg_chars(pdf_path)
    if avg < _TEXT_THRESHOLD:
        console.print(
            f"[cyan]auto[/] detected likely scanned PDF "
            f"(avg {avg:.0f} chars/page < {_TEXT_THRESHOLD}). "
            "Using [bold]docling[/] engine."
        )
        return DoclingEngine()

    return FastEngine()


__all__ = ["Engine", "FastEngine", "DoclingEngine", "select_engine"]
