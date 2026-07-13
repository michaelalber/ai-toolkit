from __future__ import annotations

from pathlib import Path

from rich.console import Console

from pdf2md.models import ExtractedPage, Table

console = Console(stderr=True)


def _bboxes_overlap(
    a: tuple[float, float, float, float], b: tuple[float, float, float, float]
) -> bool:
    """Return True if two bounding boxes share any area."""
    ax0, ay0, ax1, ay1 = a
    bx0, by0, bx1, by1 = b
    return ax0 < bx1 and ax1 > bx0 and ay0 < by1 and ay1 > by0


# A real table has at least 2 columns and 2 rows, and is not mostly empty.
# Single-column or sparse "tables" are usually shredded diagrams / line-art,
# which produce meaningless Markdown noise that hurts RAG ingestion.
_MIN_TABLE_ROWS = 2
_MIN_TABLE_COLS = 2
_MIN_FILLED_RATIO = 0.3


def _is_meaningful_table(cells: list[list[str | None]]) -> bool:
    """Return True if *cells* looks like a real data table, not diagram noise."""
    rows = len(cells)
    if rows < _MIN_TABLE_ROWS:
        return False
    cols = max((len(row) for row in cells), default=0)
    if cols < _MIN_TABLE_COLS:
        return False

    total = sum(len(row) for row in cells)
    if total == 0:
        return False
    filled = sum(1 for row in cells for cell in row if (cell or "").strip())
    return filled / total >= _MIN_FILLED_RATIO


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
        import pdfplumber
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

                for raw_table, bbox in zip(raw_tables, table_bboxes, strict=False):
                    if not raw_table:
                        continue

                    cells: list[list[str | None]] = [
                        [cell if cell else "" for cell in row]
                        for row in raw_table
                    ]
                    # Skip shredded diagrams / sparse line-art masquerading as
                    # tables; leave their overlapping text blocks as prose.
                    if not _is_meaningful_table(cells):
                        continue
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
