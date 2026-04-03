"""FastEngine — lightweight PyMuPDF + pdfplumber extraction pipeline.

Best for: digital (text-layer) PDFs where speed matters.
Not suitable for: scanned/image-only PDFs.
"""
from __future__ import annotations

import sys

from rich.console import Console

from pdf2md.models import ConversionConfig

console = Console(stderr=True)


class FastEngine:
    """Extraction pipeline backed by PyMuPDF and pdfplumber."""

    def convert(self, config: ConversionConfig) -> str:  # noqa: PLR0912
        from pdf2md.cleaner import clean_pages
        from pdf2md.code_detector import annotate_code_blocks
        from pdf2md.extractor import extract_pages
        from pdf2md.heading_detector import annotate_headings, compute_document_stats
        from pdf2md.image_extractor import extract_images
        from pdf2md.markdown_builder import build_markdown
        from pdf2md.table_detector import extract_tables

        try:
            import fitz  # type: ignore[import-untyped]

            doc = fitz.open(str(config.input_path))
        except Exception as exc:
            console.print(
                f"[bold red]Error[/] opening {config.input_path}: {exc}", style="red"
            )
            sys.exit(1)

        total_pages = doc.page_count

        from pdf2md.converter import _parse_page_range

        page_indices = (
            _parse_page_range(config.page_range, total_pages)
            if config.page_range
            else list(range(total_pages))
        )

        if config.verbose:
            console.print(
                f"[cyan]fast engine[/] — {total_pages} pages in {config.input_path.name}"
            )

        pages = extract_pages(doc, page_indices, verbose=config.verbose)
        doc.close()

        # Warn when pages appear to have no extractable text
        if config.verbose:
            empty = [p for p in pages if not p.raw_font_sizes]
            if empty:
                nums = ", ".join(str(p.page_number) for p in empty)
                console.print(
                    f"[yellow]Warning:[/] {len(empty)} page(s) with no extractable text "
                    f"(pages {nums}). Consider --engine docling for scanned PDFs."
                )

        stats = compute_document_stats(pages)
        annotate_headings(pages, stats)

        if not config.no_code_blocks:
            annotate_code_blocks(pages)

        if not config.no_tables:
            extract_tables(config.input_path, pages, page_indices, verbose=config.verbose)

        if not config.no_images:
            image_dir = config.output_path.parent / f"{config.output_path.stem}_images"
            extract_images(
                config.input_path, pages, image_dir, config.image_format, verbose=config.verbose
            )

        pages = clean_pages(pages)

        return build_markdown(
            pages=pages,
            source_path=config.input_path,
            total_pages=total_pages,
            include_metadata=False,
        )
