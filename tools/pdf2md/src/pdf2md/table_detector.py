from __future__ import annotations

from pathlib import Path

from rich.console import Console

from pdf2md.models import ExtractedPage, Table

console = Console(stderr=True)


def _bboxes_overlap(a: tuple[float, float, float, float], b: tuple[float, float, float, float]) -> bool:
    """Return True if two bounding boxes share any area."""
    ax0, ay0, ax1, ay1 = a
    bx0, by0, bx1, by1 = b
    return ax0 < bx1 and ax1 > bx0 and ay0 < by1 and ay1 > by0


def extract_tables(
    pdf_path: Path,
    pages: list[ExtractedPage],
    page_indices: list[int],
    verbose: bool = False,
) -> None:
    """Extract tables via pdfplumber and mutate ``pages`` in-place.

    For each detected table:
    - Append a :class:`~pdf2md.models.Table` to the page's ``tables`` list.
    - Mark any text blocks whose bounding box overlaps the table region
      as ``block_type="table"`` so the markdown builder skips them (the
      table renderer handles that content instead).

    Note: pdfplumber's coordinate system has the y-axis origin at the **top**
    of the page (same as PyMuPDF), so no y-axis flip is needed.
    """
    try:
        import pdfplumber  # type: ignore[import-untyped]
    except ImportError:
        console.print("[yellow]pdfplumber not installed; skipping table extraction.[/]")
        return

    page_map: dict[int, ExtractedPage] = {p.page_number: p for p in pages}

    try:
        with pdfplumber.open(str(pdf_path)) as plumber_doc:
            for idx in page_indices:
                extracted = page_map.get(idx + 1)
                if extracted is None:
                    continue

                plumber_page = plumber_doc.pages[idx]
                raw_tables = plumber_page.extract_tables()
                table_bboxes = [t.bbox for t in plumber_page.find_tables()]

                for raw_table, bbox in zip(raw_tables, table_bboxes):
                    if not raw_table:
                        continue

                    cells: list[list[str | None]] = [
                        [cell if cell else "" for cell in row]
                        for row in raw_table
                    ]
                    extracted.tables.append(
                        Table(cells=cells, page_number=idx + 1, bbox=bbox)
                    )

                    # Suppress PyMuPDF text blocks that overlap this table
                    for block in extracted.blocks:
                        if block.block_type == "text" and _bboxes_overlap(block.bbox, bbox):
                            block.block_type = "table"

    except Exception as exc:
        if verbose:
            console.print(f"[yellow]Table extraction error on {pdf_path}: {exc}[/]")
