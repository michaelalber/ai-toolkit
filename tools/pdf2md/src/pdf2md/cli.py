from __future__ import annotations

from pathlib import Path
from typing import Annotated, Optional

import typer

from pdf2md import __version__

app = typer.Typer(
    name="pdf2md",
    help="Convert PDF files to AI-agent-friendly Markdown.",
    add_completion=False,
)


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"pdf2md {__version__}")
        raise typer.Exit()


@app.command()
def convert(
    input_path: Annotated[
        Path,
        typer.Argument(
            help="Path to a PDF file or directory of PDF files.",
            exists=True,
        ),
    ],
    output_path: Annotated[
        Optional[Path],
        typer.Argument(
            help=(
                "Output path. File path for single PDF; directory for batch mode. "
                "Defaults to INPUT with .md extension (single) or ./output/ (batch)."
            ),
        ),
    ] = None,
    page_range: Annotated[
        Optional[str],
        typer.Option(
            "--page-range",
            help='Page range to extract, e.g. "1-5" or "3,7,9-12". Default: all.',
        ),
    ] = None,
    no_images: Annotated[
        bool,
        typer.Option("--no-images", help="Skip image extraction entirely."),
    ] = False,
    no_tables: Annotated[
        bool,
        typer.Option("--no-tables", help="Skip table detection; render rows as plain text."),
    ] = False,
    no_code_blocks: Annotated[
        bool,
        typer.Option("--no-code-blocks", help="Skip monospace detection; render as plain paragraphs."),
    ] = False,
    image_format: Annotated[
        str,
        typer.Option("--image-format", help="Image output format for sidecar files.", show_default=True),
    ] = "png",
    chunk_by_heading: Annotated[
        bool,
        typer.Option("--chunk-by-heading", help="Write one .md file per top-level heading."),
    ] = False,
    metadata: Annotated[
        bool,
        typer.Option("--metadata", help="Prepend YAML front-matter block (source, pages, timestamp)."),
    ] = False,
    verbose: Annotated[
        bool,
        typer.Option("--verbose/--quiet", help="Show per-page progress."),
    ] = False,
    version: Annotated[
        Optional[bool],
        typer.Option(
            "--version",
            callback=_version_callback,
            is_eager=True,
            help="Show version and exit.",
        ),
    ] = None,
) -> None:
    """Convert a PDF file (or directory of PDFs) to Markdown."""
    if image_format not in ("png", "jpg"):
        typer.echo(f"Error: --image-format must be 'png' or 'jpg', got '{image_format}'.", err=True)
        raise typer.Exit(code=1)

    from pdf2md.converter import run

    run(
        input_path=input_path,
        output_path=output_path,
        page_range=page_range,
        no_images=no_images,
        no_tables=no_tables,
        no_code_blocks=no_code_blocks,
        image_format=image_format,  # type: ignore[arg-type]
        chunk_by_heading=chunk_by_heading,
        metadata=metadata,
        verbose=verbose,
    )
