from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from web2md import __version__
from web2md.models import ConversionConfig, url_to_slug

app = typer.Typer(
    name="web2md",
    help="Convert web pages and documentation sites to AI-agent-friendly Markdown.",
    add_completion=False,
)

console = Console(stderr=True)


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"web2md {__version__}")
        raise typer.Exit()


@app.command()
def convert(
    url: Annotated[
        str,
        typer.Argument(
            help=(
                "URL to convert. With --crawl: the crawl root. "
                "With --sitemap: the sitemap.xml URL."
            ),
        ),
    ],
    output: Annotated[
        Path | None,
        typer.Argument(
            help=(
                "Output path. File for a single page; directory for --crawl / --sitemap. "
                "Defaults to <url-slug>.md (single) or ./output/ (batch)."
            ),
        ),
    ] = None,
    crawl: Annotated[
        bool,
        typer.Option("--crawl", help="BFS-crawl all internal pages starting from URL."),
    ] = False,
    sitemap: Annotated[
        bool,
        typer.Option("--sitemap", help="Parse URL as a sitemap.xml and convert all listed pages."),
    ] = False,
    max_pages: Annotated[
        int,
        typer.Option(
            "--max-pages",
            help="Maximum pages to convert in crawl or sitemap mode.",
            show_default=True,
        ),
    ] = 50,
    same_prefix: Annotated[
        bool,
        typer.Option(
            "--same-prefix",
            help=(
                "Crawl mode only: restrict links to those starting with the given URL "
                "(useful for a docs subtree, e.g. /guide/). Default: same domain."
            ),
        ),
    ] = False,
    max_depth: Annotated[
        int | None,
        typer.Option(
            "--max-depth",
            help=(
                "Crawl mode only: maximum link-hops to follow from the start URL "
                "(root = 0, its direct links = 1, ...). Default: unlimited."
            ),
        ),
    ] = None,
    no_images: Annotated[
        bool,
        typer.Option("--no-images", help="Strip image references from output."),
    ] = False,
    no_tables: Annotated[
        bool,
        typer.Option("--no-tables", help="Strip table markup from output."),
    ] = False,
    chunk_by_heading: Annotated[
        bool,
        typer.Option("--chunk-by-heading", help="Write one .md file per top-level (H1) heading."),
    ] = False,
    metadata: Annotated[
        bool,
        typer.Option(
            "--metadata", help="Prepend a YAML front-matter block (source URL, timestamp)."
        ),
    ] = False,
    verbose: Annotated[
        bool,
        typer.Option("--verbose/--quiet", help="Show per-page progress."),
    ] = False,
    version: Annotated[
        bool | None,
        typer.Option(
            "--version",
            callback=_version_callback,
            is_eager=True,
            help="Show version and exit.",
        ),
    ] = None,
) -> None:
    """Convert a web page (or site) to Markdown for RAG ingestion."""
    if crawl and sitemap:
        typer.echo("Error: --crawl and --sitemap are mutually exclusive.", err=True)
        raise typer.Exit(code=1)

    is_batch = crawl or sitemap

    if is_batch:
        out_dir = output if output is not None else Path("output")
        out_dir.mkdir(parents=True, exist_ok=True)
        urls = _collect_urls(
            url,
            crawl=crawl,
            sitemap=sitemap,
            max_pages=max_pages,
            same_prefix=same_prefix,
            max_depth=max_depth,
            verbose=verbose,
        )
        if not urls:
            console.print("[yellow]No URLs to convert.[/]")
            return
        _convert_batch(urls, out_dir, no_images, no_tables, chunk_by_heading, metadata, verbose)
    else:
        out_file = output if output is not None else Path(url_to_slug(url) + ".md")
        cfg = ConversionConfig(
            url=url,
            output_path=out_file,
            no_images=no_images,
            no_tables=no_tables,
            chunk_by_heading=chunk_by_heading,
            metadata=metadata,
            verbose=verbose,
        )
        _run_single(cfg)


def _collect_urls(
    url: str,
    *,
    crawl: bool,
    sitemap: bool,
    max_pages: int,
    same_prefix: bool,
    max_depth: int | None,
    verbose: bool,
) -> list[str]:
    if crawl:
        from web2md.crawler import crawl as do_crawl

        if verbose:
            depth_note = "unlimited depth" if max_depth is None else f"depth ≤ {max_depth}"
            console.print(f"[cyan]Crawling from[/] {url} (max {max_pages} pages, {depth_note})")
        return do_crawl(
            url, max_pages=max_pages, same_prefix=same_prefix, max_depth=max_depth, verbose=verbose
        )

    if sitemap:
        from web2md.sitemap import fetch_sitemap_urls

        if verbose:
            console.print(f"[cyan]Fetching sitemap[/] {url}")
        all_urls = fetch_sitemap_urls(url)
        if verbose:
            console.print(f"  Found {len(all_urls)} URLs in sitemap")
        return all_urls[:max_pages]

    return []


def _run_single(config: ConversionConfig) -> None:
    from web2md.converter import convert_and_write

    convert_and_write(config)


def _convert_batch(
    urls: list[str],
    out_dir: Path,
    no_images: bool,
    no_tables: bool,
    chunk_by_heading: bool,
    metadata: bool,
    verbose: bool,
) -> None:
    from web2md.converter import convert_and_write

    for i, url in enumerate(urls, 1):
        slug = url_to_slug(url)
        out_file = out_dir / f"{slug}.md"
        if not verbose:
            console.print(f"[dim]{i}/{len(urls)}[/] {url}")
        cfg = ConversionConfig(
            url=url,
            output_path=out_file,
            no_images=no_images,
            no_tables=no_tables,
            chunk_by_heading=chunk_by_heading,
            metadata=metadata,
            verbose=verbose,
        )
        try:
            convert_and_write(cfg)
        except Exception as exc:
            console.print(f"[bold red]Error[/] converting {url}: {exc}")
