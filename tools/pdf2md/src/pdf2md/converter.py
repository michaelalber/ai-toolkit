from __future__ import annotations

import re
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


def _build_front_matter(source_path: Path, total_pages: int) -> str:
    from datetime import datetime, timezone

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return (
        "---\n"
        f"source: {source_path.name}\n"
        f"pages: {total_pages}\n"
        f"extracted_at: {timestamp}\n"
        f"tool: pdf2md/0.1.0\n"
        "---\n\n"
    )


def _write_chunks(markdown: str, base_output: Path) -> None:
    """Split markdown at H1 boundaries and write one file per chunk."""
    base_output.parent.mkdir(parents=True, exist_ok=True)
    chunks: list[tuple[str, str]] = []
    current_title = "preamble"
    current_lines: list[str] = []

    for line in markdown.splitlines(keepends=True):
        if line.startswith("# ") and current_lines:
            chunks.append((current_title, "".join(current_lines)))
            current_title = re.sub(r"[^\w\s-]", "", line[2:].strip()).lower()
            current_title = re.sub(r"\s+", "-", current_title)
            current_lines = [line]
        else:
            current_lines.append(line)

    if current_lines:
        chunks.append((current_title, "".join(current_lines)))

    for slug, content in chunks:
        out = base_output.parent / f"{base_output.stem}_{slug}.md"
        out.write_text(content, encoding="utf-8")


def _get_total_pages(pdf_path: Path) -> int | None:
    """Return the page count of a PDF, or None on error."""
    try:
        import fitz  # type: ignore[import-untyped]

        doc = fitz.open(str(pdf_path))
        count = doc.page_count
        doc.close()
        return count
    except Exception:
        return None


def _is_password_protected(pdf_path: Path) -> bool:
    try:
        import fitz  # type: ignore[import-untyped]

        doc = fitz.open(str(pdf_path))
        protected = bool(doc.needs_pass)
        doc.close()
        return protected
    except Exception:
        return False


def _convert_single(config: ConversionConfig) -> None:
    from pdf2md.engines import select_engine

    if _is_password_protected(config.input_path):
        console.print(
            f"[yellow]Skipping[/] {config.input_path}: password-protected PDF"
        )
        return

    total_pages = _get_total_pages(config.input_path)
    if total_pages is None:
        console.print(
            f"[bold red]Error[/] reading {config.input_path}", style="red"
        )
        sys.exit(1)

    engine = select_engine(config.engine, config.input_path)
    markdown = engine.convert(config)

    if config.metadata:
        markdown = _build_front_matter(config.input_path, total_pages) + markdown

    if config.chunk_by_heading:
        _write_chunks(markdown, config.output_path)
    else:
        config.output_path.parent.mkdir(parents=True, exist_ok=True)
        config.output_path.write_text(markdown, encoding="utf-8")
        if config.verbose:
            console.print(f"[bold green]Written[/] {config.output_path}")


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
    engine: Literal["auto", "fast", "docling"],
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
                engine=engine,
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
            engine=engine,
        )
        _convert_single(cfg)
