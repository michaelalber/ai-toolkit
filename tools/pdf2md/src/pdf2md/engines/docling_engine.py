"""DoclingEngine — ML-powered extraction via IBM Docling.

Best for: scanned PDFs, complex multi-column layouts, academic documents,
          documents with formulas or mixed image/text pages.
Requires: pip install 'pdf2md[docling]'

Note: Docling downloads layout models (~500 MB) on first run.
      Subsequent runs use the cached models.
      Page-range filtering is not supported; the full document is converted.
"""
from __future__ import annotations

import re

from rich.console import Console

from pdf2md.models import ConversionConfig

console = Console(stderr=True)

_IMAGE_RE = re.compile(r"!\[.*?\]\(.*?\)\n?")
_TABLE_RE = re.compile(r"(?m)^(\|[^\n]+\|\n)+")


class DoclingEngine:
    """Extraction pipeline backed by Docling's ML document converter."""

    def convert(self, config: ConversionConfig) -> str:
        try:
            from docling.document_converter import DocumentConverter  # type: ignore[import-untyped]
        except ImportError as exc:
            raise RuntimeError(
                "Docling is not installed. Run: pip install 'pdf2md[docling]'"
            ) from exc

        if config.page_range:
            console.print(
                "[yellow]Warning:[/] --page-range is not supported with --engine docling; "
                "the full document will be converted."
            )

        if config.verbose:
            console.print(
                f"[cyan]docling engine[/] — converting {config.input_path.name} "
                "(models load on first run)"
            )

        converter = DocumentConverter()
        result = converter.convert(str(config.input_path))
        markdown: str = result.document.export_to_markdown()

        if config.no_images:
            markdown = _IMAGE_RE.sub("", markdown)

        if config.no_tables:
            markdown = _TABLE_RE.sub("", markdown)

        return markdown
