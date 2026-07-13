"""URL → Markdown conversion via docling."""
from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path

from docling.document_converter import DocumentConverter
from rich.console import Console

from web2md.models import ConversionConfig

console = Console(stderr=True)

_IMAGE_RE = re.compile(r"!\[.*?\]\(.*?\)\n?")
_TABLE_RE = re.compile(r"(?m)^(\|[^\n]+\|\n)+")


def convert_url(config: ConversionConfig) -> str:
    """Convert a single URL to Markdown using Docling and return the text."""
    if config.verbose:
        console.print(f"[cyan]Converting[/] {config.url}")

    converter = DocumentConverter()
    result = converter.convert(config.url)
    markdown: str = result.document.export_to_markdown()

    if config.no_images:
        markdown = _IMAGE_RE.sub("", markdown)

    if config.no_tables:
        markdown = _TABLE_RE.sub("", markdown)

    return markdown


def build_front_matter(url: str) -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return (
        "---\n"
        f"source: {url}\n"
        f"extracted_at: {timestamp}\n"
        f"tool: web2md/0.1.0\n"
        "---\n\n"
    )


def write_chunks(markdown: str, base_output: Path) -> list[Path]:
    """Split markdown at H1 boundaries and write one file per chunk.

    Returns the list of files written.
    """
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

    written: list[Path] = []
    for slug, content in chunks:
        out = base_output.parent / f"{base_output.stem}_{slug}.md"
        out.write_text(content, encoding="utf-8")
        written.append(out)
    return written


def convert_and_write(config: ConversionConfig) -> None:
    """Convert a URL and write the result to config.output_path."""
    markdown = convert_url(config)

    if config.metadata:
        markdown = build_front_matter(config.url) + markdown

    if config.chunk_by_heading:
        written = write_chunks(markdown, config.output_path)
        if config.verbose:
            for p in written:
                console.print(f"[bold green]Written[/] {p}")
    else:
        config.output_path.parent.mkdir(parents=True, exist_ok=True)
        config.output_path.write_text(markdown, encoding="utf-8")
        if config.verbose:
            console.print(f"[bold green]Written[/] {config.output_path}")
