from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from code2md import __version__
from code2md.converter import convert_file, write_document
from code2md.enrich.cache import EnrichCache
from code2md.enrich.config import resolve_model, resolve_ollama_host
from code2md.enrich.ollama_client import OllamaClient, OllamaError
from code2md.enrich.relate_cache import RelateCache
from code2md.enrich.relationships import extract_relationships, render_relationships
from code2md.enrich.scandoc import parse_scan_doc
from code2md.enrich.summarize import (
    iter_enrichable_docs,
    render_enriched_doc,
    summarize_document,
    write_enriched,
)
from code2md.enrich.verify import verify_all
from code2md.models import ScanConfig, collection_suffix, slugify_name
from code2md.overview import build_overview, write_overview
from code2md.walker import git_commit, iter_source_files


class EnrichLevel(str, Enum):
    """Which enrichment artifacts to generate."""

    summaries = "summaries"  # Phase 1: per-file NL summaries + questions
    graph = "graph"  # Phase 3: RELATIONSHIPS.md concept graph
    full = "full"  # both

app = typer.Typer(
    name="code2md",
    help="Scan a codebase into language-tagged Markdown for RAG ingestion.",
    add_completion=False,
)

console = Console(stderr=True)


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"code2md {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        bool | None,
        typer.Option(
            "--version", callback=_version_callback, is_eager=True, help="Show version and exit."
        ),
    ] = None,
) -> None:
    """code2md — codebase → Markdown for RAG, with optional LLM enrichment."""


@app.command()
def scan(
    repo: Annotated[
        Path,
        typer.Argument(help="Path to the repository / project directory to scan."),
    ],
    out: Annotated[
        Path | None,
        typer.Option("--out", help="Output directory. Defaults to ./output/<name>."),
    ] = None,
    name: Annotated[
        str | None,
        typer.Option(
            "--name", help="Project name / collection suffix. Defaults to the repo dir name."
        ),
    ] = None,
    overview: Annotated[
        bool,
        typer.Option("--overview/--no-overview", help="Also emit a synthesized _overview.md."),
    ] = True,
    metadata: Annotated[
        bool,
        typer.Option(
            "--metadata/--no-metadata", help="Prepend YAML front-matter to each document."
        ),
    ] = True,
    max_file_kb: Annotated[
        int,
        typer.Option("--max-file-kb", help="Skip source files larger than this many KiB."),
    ] = 512,
    verbose: Annotated[
        bool,
        typer.Option("--verbose/--quiet", help="Show per-file progress."),
    ] = False,
) -> None:
    """Convert every source file under REPO into language-tagged Markdown."""
    repo = repo.resolve()
    if not repo.is_dir():
        typer.echo(f"Error: {repo} is not a directory.", err=True)
        raise typer.Exit(code=1)

    project_name = slugify_name(name if name is not None else repo.name)
    out_dir = out if out is not None else Path("output") / project_name

    config = ScanConfig(
        repo_path=repo,
        out_dir=out_dir,
        name=project_name,
        overview=overview,
        metadata=metadata,
        max_file_kb=max_file_kb,
        verbose=verbose,
    )

    sources = iter_source_files(config.repo_path, config.max_file_kb)
    if not sources:
        console.print(f"[yellow]No source files found under[/] {repo}")
        raise typer.Exit(code=1)

    commit = git_commit(config.repo_path)
    for index, source_file in enumerate(sources, 1):
        content = convert_file(source_file, config.name, commit, config.metadata)
        written = write_document(source_file, config.out_dir, content)
        if config.verbose:
            console.print(f"[dim]{index}/{len(sources)}[/] {written}")

    if config.overview:
        overview_md = build_overview(config.repo_path, config.name, sources)
        write_overview(config.out_dir, overview_md)

    # soft_wrap keeps the ingest command on one line so the path stays copy-pasteable.
    console.print(
        f"[bold green]Scanned[/] {len(sources)} file(s) → {config.out_dir}", soft_wrap=True
    )
    console.print(
        "[cyan]Ingest with:[/] "
        f"grounded-code-mcp ingest {config.out_dir} --collection {collection_suffix(config.name)}",
        soft_wrap=True,
    )


@app.command()
def enrich(
    scan_dir: Annotated[
        Path,
        typer.Argument(help="A code2md scan output directory to enrich."),
    ],
    model: Annotated[
        str | None,
        typer.Option("--model", help="Ollama model for extraction (or CODE2MD_ENRICH_MODEL env)."),
    ] = None,
    level: Annotated[
        EnrichLevel,
        typer.Option(
            "--level", help="Which artifacts: summaries (Phase 1), graph (Phase 3), full."
        ),
    ] = EnrichLevel.summaries,
    verify_model: Annotated[
        str | None,
        typer.Option(
            "--verify-model", help="Model for the graph verification pass. Defaults to --model."
        ),
    ] = None,
    ollama_host: Annotated[
        str | None,
        typer.Option("--ollama-host", help="Ollama base URL (or OLLAMA_HOST env)."),
    ] = None,
    force: Annotated[
        bool,
        typer.Option("--force", help="Re-enrich even if the cached SHA + model match."),
    ] = False,
    timeout: Annotated[
        float,
        typer.Option("--timeout", help="Per-request timeout in seconds."),
    ] = 180.0,
    verbose: Annotated[
        bool,
        typer.Option("--verbose/--quiet", help="Show per-file progress."),
    ] = False,
) -> None:
    """Generate LLM enrichment for a scan.

    ``--level summaries`` (default) emits per-file NL summaries + hypothetical
    questions under SCAN_DIR/_enriched/ (Phase 1). ``--level graph`` extracts a
    verified concept-graph RELATIONSHIPS.md at the scan root (Phase 3). ``--level
    full`` does both. All output is provenance-marked and points back to the real
    code; grounded-code-mcp ingests it unchanged.
    """
    scan_dir = scan_dir.resolve()
    if not scan_dir.is_dir():
        typer.echo(f"Error: {scan_dir} is not a directory.", err=True)
        raise typer.Exit(code=1)

    resolved_model = resolve_model(model)
    if not resolved_model:
        typer.echo("Error: no model. Pass --model or set CODE2MD_ENRICH_MODEL.", err=True)
        raise typer.Exit(code=1)

    host = resolve_ollama_host(ollama_host)
    client = OllamaClient(host, timeout_s=timeout)

    docs = iter_enrichable_docs(scan_dir)
    if not docs:
        console.print(f"[yellow]No scan documents to enrich under[/] {scan_dir}")
        raise typer.Exit(code=1)

    if level in (EnrichLevel.summaries, EnrichLevel.full):
        _run_summaries(scan_dir, docs, client, resolved_model, force, verbose)
    if level in (EnrichLevel.graph, EnrichLevel.full):
        _run_graph(
            scan_dir, docs, client, resolved_model, verify_model or resolved_model, force, verbose
        )


def _run_summaries(
    scan_dir: Path,
    docs: list[Path],
    client: OllamaClient,
    model: str,
    force: bool,
    verbose: bool,
) -> None:
    """Phase 1: per-file NL summaries + questions → SCAN_DIR/_enriched/."""
    cache = EnrichCache.load(scan_dir)
    generated = skipped = failed = 0
    for index, doc_path in enumerate(docs, 1):
        parsed = parse_scan_doc(doc_path, scan_dir)
        if not parsed.code.strip():
            continue
        if not force and cache.is_fresh(parsed, model):
            skipped += 1
            continue
        try:
            enrichment = summarize_document(parsed, client, model)
        except OllamaError as exc:
            failed += 1
            console.print(f"[red]enrich failed[/] {parsed.path}: {exc}")
            continue
        content = render_enriched_doc(parsed, enrichment, model)
        write_enriched(scan_dir, parsed, content)
        cache.update(parsed, model)
        generated += 1
        if verbose:
            console.print(f"[dim]{index}/{len(docs)}[/] enriched {parsed.path}")

    cache.save()
    console.print(
        f"[bold green]Enriched[/] {generated} file(s) "
        f"([dim]{skipped} cached, {failed} failed[/]) → {scan_dir}/_enriched",
        soft_wrap=True,
    )


def _run_graph(
    scan_dir: Path,
    docs: list[Path],
    client: OllamaClient,
    model: str,
    verify_model: str,
    force: bool,
    verbose: bool,
) -> None:
    """Phase 3: extract + verify concept-graph triples → SCAN_DIR/RELATIONSHIPS.md.

    Per-file extraction (each edge cites its derived-from code) followed by a
    verification pass that drops edges the code does not support. Verified edges are
    cached so unchanged files still contribute to the rebuilt aggregate document.
    """
    project_slug = slugify_name(scan_dir.name)
    cache = RelateCache.load(scan_dir)
    all_triples = []
    generated = skipped = failed = 0
    for index, doc_path in enumerate(docs, 1):
        parsed = parse_scan_doc(doc_path, scan_dir)
        if not parsed.code.strip():
            continue
        if not force and cache.is_fresh(parsed, model):
            all_triples.extend(cache.get_triples(parsed))
            skipped += 1
            continue
        try:
            extracted = extract_relationships(parsed, client, model)
            verified = verify_all(
                extracted, {parsed.rel_doc_path.as_posix(): parsed.code}, client, verify_model
            )
        except OllamaError as exc:
            failed += 1
            console.print(f"[red]graph extract failed[/] {parsed.path}: {exc}")
            continue
        cache.update(parsed, model, verified)
        all_triples.extend(verified)
        generated += 1
        if verbose:
            console.print(
                f"[dim]{index}/{len(docs)}[/] {parsed.path}: {len(verified)} edge(s)"
            )

    cache.save()
    rel_path = scan_dir / "RELATIONSHIPS.md"
    rel_path.write_text(render_relationships(all_triples, project_slug, model), encoding="utf-8")
    console.print(
        f"[bold green]Graph[/] {len(all_triples)} edge(s) from {generated} file(s) "
        f"([dim]{skipped} cached, {failed} failed[/]) → {rel_path}",
        soft_wrap=True,
    )
    console.print(
        "[cyan]Rebuild the concept graph with:[/] "
        f"grounded-code-mcp ingest {scan_dir} "
        f"--collection {collection_suffix(project_slug)} --force",
        soft_wrap=True,
    )
