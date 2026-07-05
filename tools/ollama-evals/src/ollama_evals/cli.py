# <AI-Generated START>
"""Command-line interface for ollama-evals.

Commands:
  run          run a suite across models and save a scored artifact + matrix
  compare      compare two runs; regression beyond --threshold exits non-zero (CI gate)
  report       re-render a saved run as Markdown / HTML
  calibrate    measure the judge's agreement with human labels
  list-models  list models available on the configured Ollama server
"""

from __future__ import annotations

from pathlib import Path

import typer

from .calibrate import calibrate as run_calibration
from .calibrate import load_calibration
from .cases import load_cases
from .client import OllamaClient
from .compare import compare_runs
from .config import load_config, resolve_config_path
from .judging import build_judge
from .report import (
    comparison_to_html,
    comparison_to_markdown,
    run_to_html,
    run_to_markdown,
)
from .runner import load_run, run_suite, save_run

app = typer.Typer(help="Evaluate and regression-test local Ollama models.", no_args_is_help=True)

SUITES = ["coding", "chat", "tool_use", "structured"]


def resolve_config(config_path: str | None):
    path = Path(config_path) if config_path else resolve_config_path(Path.cwd())
    return load_config(path)


def resolve_client(config):  # seam: patched in tests so no live Ollama is needed
    return OllamaClient(config.base_url)


def _load_cases(datasets_dir: str, suite: str):
    names = SUITES if suite == "all" else [suite]
    cases = []
    for name in names:
        path = Path(datasets_dir) / f"{name}.jsonl"
        if path.exists():
            cases.extend(load_cases(path))
    return cases


@app.command()
def run(
    models: str = typer.Option(None, help="Comma-separated models; defaults to config."),
    suite: str = typer.Option("all", help="coding|chat|tool_use|structured|all"),
    datasets_dir: str = typer.Option("datasets"),
    out: str = typer.Option("runs", help="Directory for the run artifact."),
    samples: int = typer.Option(1, help="Repeat each case N times and average."),
    config: str = typer.Option(None, help="Path to a models.yaml."),
):
    cfg = resolve_config(config)
    model_list = [m.strip() for m in models.split(",")] if models else cfg.models
    if not model_list:
        typer.echo("no models specified (use --models or set models: in config)", err=True)
        raise typer.Exit(code=2)

    cases = _load_cases(datasets_dir, suite)
    if not cases:
        typer.echo(f"no cases found in {datasets_dir!r} for suite {suite!r}", err=True)
        raise typer.Exit(code=2)

    client = resolve_client(cfg)
    needs_judge = any(c.scorer["type"] == "judge" for c in cases)
    judge = build_judge(cfg, client) if needs_judge else None

    result = run_suite(client, cases, model_list, config=cfg, judge=judge, samples=samples)
    path = save_run(result, out)
    typer.echo(run_to_markdown(result))
    typer.echo(f"\nsaved run: {path}")


@app.command()
def compare(
    baseline: str = typer.Argument(..., help="Baseline run .json"),
    candidate: str = typer.Argument(..., help="Candidate run .json"),
    threshold: float = typer.Option(0.05, help="Max tolerated score drop before failing."),
    model_baseline: str = typer.Option(None),
    model_candidate: str = typer.Option(None),
    html: str = typer.Option(None, help="Write a self-contained HTML report here."),
):
    reg = compare_runs(
        load_run(baseline),
        load_run(candidate),
        model_baseline=model_baseline,
        model_candidate=model_candidate,
        threshold=threshold,
    )
    typer.echo(comparison_to_markdown(reg))
    if html:
        Path(html).write_text(comparison_to_html(reg))
        typer.echo(f"\nwrote HTML: {html}")
    if reg.regressed:
        raise typer.Exit(code=1)  # CI gate


@app.command()
def report(
    run_file: str = typer.Argument(..., help="A saved run .json"),
    html: str = typer.Option(None, help="Write a self-contained HTML matrix here."),
):
    result = load_run(run_file)
    typer.echo(run_to_markdown(result))
    if html:
        Path(html).write_text(run_to_html(result))
        typer.echo(f"\nwrote HTML: {html}")


@app.command()
def calibrate(
    dataset: str = typer.Option("datasets/judge-calibration.jsonl"),
    config: str = typer.Option(None),
):
    cfg = resolve_config(config)
    judge = build_judge(cfg, resolve_client(cfg))
    result = run_calibration(judge, load_calibration(dataset))
    typer.echo(f"judge agreement: {result.agreement:.2f} over {result.n} labelled examples")
    if result.agreement < 0.8:
        typer.echo("WARNING: agreement < 0.80 — do not trust this judge as a gate yet.", err=True)


@app.command("list-models")
def list_models(config: str = typer.Option(None)):
    cfg = resolve_config(config)
    for model in resolve_client(cfg).list_models():
        typer.echo(model)


if __name__ == "__main__":  # pragma: no cover
    app()
# <AI-Generated END>
