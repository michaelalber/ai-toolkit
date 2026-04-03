from __future__ import annotations

import sys
from pathlib import Path
from typing import Literal

from rich.console import Console

from pdf2md.models import ConversionConfig

console = Console(stderr=True)


def _resolve_output(input_path: Path, output_path: Path | None, is_batch: bool) -> Path:
    if output_path is not None:
        return output_path
    if is_batch:
        return input_path.parent / "output"
    return input_path.with_suffix(".md")


def _parse_page_range(page_range: str, total_pages: int) -> list[int]:
    """Return 0-based page indices from a range string like '1-3,5,7-9'."""
    pages: set[int] = set()
    for part in page_range.split(","):
        part = part.strip()
        if "-" in part:
            start_s, end_s = part.split("-", 1)
            start, end = int(start_s), int(end_s)
            pages.update(range(start - 1, min(end, total_pages)))
        else:
            idx = int(part) - 1
            if 0 <= idx < total_pages:
                pages.add(idx)
    return sorted(pages)


def _convert_single(config: ConversionConfig) -> None:
    from pdf2md.extractor import extract_pages
    from pdf2md.heading_detector import compute_document_stats, annotate_headings
    from pdf2md.code_detector import annotate_code_blocks
    from pdf2md.table_detector import extract_tables
    from pdf2md.image_extractor import extract_images
    from pdf2md.cleaner import clean_pages
    from pdf2md.markdown_builder import build_markdown

    if config.verbose:
        console.print(f"[bold cyan]Opening[/] {config.input_path}")

    try:
        import fitz  # type: ignore[import-untyped]
        doc = fitz.open(str(config.input_path))
    except Exception as exc:
        console.print(f"[bold red]Error[/] opening {config.input_path}: {exc}", style="red")
        sys.exit(1)

    if doc.needs_pass:
        console.print(f"[yellow]Skipping[/] {config.input_path}: password-protected PDF")
        doc.close()
        return

    total_pages = doc.page_count
    page_indices = (
        _parse_page_range(config.page_range, total_pages)
        if config.page_range
        else list(range(total_pages))
    )

    pages = extract_pages(doc, page_indices, verbose=config.verbose)
    doc.close()

    stats = compute_document_stats(pages)
    annotate_headings(pages, stats)

    if not config.no_code_blocks:
        annotate_code_blocks(pages)

    if not config.no_tables:
        extract_tables(config.input_path, pages, page_indices, verbose=config.verbose)

    if not config.no_images:
        image_dir = config.output_path.parent / f"{config.output_path.stem}_images"
        extract_images(config.input_path, pages, image_dir, config.image_format, verbose=config.verbose)

    pages = clean_pages(pages)

    markdown = build_markdown(
        pages=pages,
        source_path=config.input_path,
        total_pages=total_pages,
        include_metadata=config.metadata,
    )

    if config.chunk_by_heading:
        _write_chunks(markdown, config.output_path)
    else:
        config.output_path.parent.mkdir(parents=True, exist_ok=True)
        config.output_path.write_text(markdown, encoding="utf-8")
        if config.verbose:
            console.print(f"[bold green]Written[/] {config.output_path}")


def _write_chunks(markdown: str, base_output: Path) -> None:
    """Split markdown at H1 boundaries and write one file per chunk."""
    import re

    base_output.parent.mkdir(parents=True, exist_ok=True)
    chunks: list[tuple[str, str]] = []
    current_title = "preamble"
    current_lines: list[str] = []

    for line in markdown.splitlines(keepends=True):
        if line.startswith("# ") and current_lines:
            chunks.append((current_title, "".join(current_lines)))
            current_title = re.sub(r"[^\w\s-]", "", line[2:].strip()).lower()
            current_title = re.sub(r"[\s]+", "-", current_title)
            current_lines = [line]
        else:
            current_lines.append(line)

    if current_lines:
        chunks.append((current_title, "".join(current_lines)))

    for slug, content in chunks:
        out = base_output.parent / f"{base_output.stem}_{slug}.md"
        out.write_text(content, encoding="utf-8")


def run(
    input_path: Path,
    output_path: Path | None,
    page_range: str | None,
    no_images: bool,
    no_tables: bool,
    no_code_blocks: bool,
    image_format: Literal["png", "jpg"],
    chunk_by_heading: bool,
    metadata: bool,
    verbose: bool,
) -> None:
    if input_path.is_dir():
        pdf_files = sorted(input_path.glob("*.pdf"))
        if not pdf_files:
            console.print(f"[yellow]No PDF files found in {input_path}[/]")
            return

        out_dir = _resolve_output(input_path, output_path, is_batch=True)
        out_dir.mkdir(parents=True, exist_ok=True)

        for pdf in pdf_files:
            cfg = ConversionConfig(
                input_path=pdf,
                output_path=out_dir / pdf.with_suffix(".md").name,
                page_range=page_range,
                no_images=no_images,
                no_tables=no_tables,
                no_code_blocks=no_code_blocks,
                image_format=image_format,
                chunk_by_heading=chunk_by_heading,
                metadata=metadata,
                verbose=verbose,
            )
            _convert_single(cfg)
    else:
        resolved_output = _resolve_output(input_path, output_path, is_batch=False)
        cfg = ConversionConfig(
            input_path=input_path,
            output_path=resolved_output,
            page_range=page_range,
            no_images=no_images,
            no_tables=no_tables,
            no_code_blocks=no_code_blocks,
            image_format=image_format,
            chunk_by_heading=chunk_by_heading,
            metadata=metadata,
            verbose=verbose,
        )
        _convert_single(cfg)
