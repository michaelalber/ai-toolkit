# <AI-Generated START>
"""Command-line interface for skill-evals.

Exit codes are uniform across every command:

  0  clean — no ERROR findings, no regression
  1  gate failure — an ERROR finding (or, later, a routing/scorecard regression)
  2  usage or environment — bad path, no skills found, unknown rule
  3  judge unusable — reserved for the LLM layers, so "the model is broken" never
     reads as "the skills are bad"

Warnings never affect the exit code unless --strict. That flag is the ratchet: promote a
warning class to error once the corpus is clean on it.
"""

from __future__ import annotations

from pathlib import Path

import typer

from . import report as reporting
from .baselines import load_known_non_skills, load_state_tag_families
from .corpus import discover
from .lint import dump_baseline
from .lint import lint as run_lint

app = typer.Typer(
    help="Lint and evaluate the ai-toolkit skill corpus.", no_args_is_help=True
)

EXIT_OK = 0
EXIT_GATE = 1
EXIT_USAGE = 2
EXIT_JUDGE = 3

# Above this, the endpoint is broken and the scores say nothing about the skills.
MAX_PARSE_FAILURE_RATE = 0.10


def find_repo_root(start: Path | None = None) -> Path:
    """Walk up for the directory holding skills/ — so the tool runs from anywhere."""
    current = (start or Path.cwd()).resolve()
    for candidate in [current, *current.parents]:
        if (candidate / "skills").is_dir() and (candidate / "CLAUDE.md").is_file():
            return candidate
    return current


def _resolve_paths(repo_root: str | None, skills_dir: str | None) -> tuple[Path, Path]:
    """Pair a skills tree with the repo whose metadata the repo-scoped rules check.

    An explicit --skills-dir implies its own repo: pointing at one tree while checking a
    different repo's README and Pi triage doc would report a mountain of nonsense.
    """
    if repo_root:
        root = Path(repo_root)
        return root, Path(skills_dir) if skills_dir else root / "skills"
    if skills_dir:
        path = Path(skills_dir)
        return path.parent, path
    root = find_repo_root()
    return root, root / "skills"


@app.command()
def lint(
    skills_dir: str = typer.Option(None, help="Defaults to <repo root>/skills."),
    repo_root: str = typer.Option(None, help="Defaults to the detected repository root."),
    output_format: str = typer.Option("text", "--format", help="text|json|markdown"),
    rule: list[str] = typer.Option(None, "--rule", help="Run only these rules (repeatable)."),
    baseline: str = typer.Option(None, help="YAML of accepted findings to suppress."),
    strict: bool = typer.Option(False, help="Fail on warnings too."),
):
    root, skills_path = _resolve_paths(repo_root, skills_dir)

    try:
        findings = run_lint(
            skills_path,
            repo_root=root,
            only=list(rule) if rule else None,
            baseline=baseline,
            state_tag_families=load_state_tag_families(root),
            known_non_skills=load_known_non_skills(root),
        )
        total = len(discover(skills_path))
    except FileNotFoundError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=EXIT_USAGE) from exc
    except KeyError as exc:  # unknown --rule
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=EXIT_USAGE) from exc

    renderers = {
        "text": reporting.to_text,
        "json": reporting.to_json,
        "markdown": reporting.to_markdown,
    }
    if output_format not in renderers:
        typer.echo(f"unknown format {output_format!r}; use text|json|markdown", err=True)
        raise typer.Exit(code=EXIT_USAGE)
    typer.echo(renderers[output_format](findings, total_skills=total))

    failed = findings.errors or (strict and findings.warnings)
    if failed:
        raise typer.Exit(code=EXIT_GATE)


@app.command("write-baseline")
def write_baseline(
    out: str = typer.Argument(..., help="Path to write the baseline YAML."),
    skills_dir: str = typer.Option(None),
    repo_root: str = typer.Option(None),
    note: str = typer.Option("", help="Why these findings are accepted."),
):
    """Snapshot the current findings as accepted.

    Used once, immediately before fixing a batch of real defects, so the acceptance tests
    that prove the linter works keep passing after the corpus goes clean.
    """
    root, skills_path = _resolve_paths(repo_root, skills_dir)
    findings = run_lint(
        skills_path,
        repo_root=root,
        state_tag_families=load_state_tag_families(root),
        known_non_skills=load_known_non_skills(root),
    )
    Path(out).write_text(dump_baseline(findings, note=note, repo_root=root))
    typer.echo(f"wrote {len(findings)} accepted finding(s) to {out}")


@app.command()
def route(
    dataset: str = typer.Option("datasets/routing.jsonl", help="Routing cases (JSONL)."),
    models: str = typer.Option(None, help="Comma-separated models; defaults to config."),
    roster_mode: str = typer.Option("full", help="full|shard|truncated"),
    shards: int = typer.Option(3, help="shard mode only: how many shards to split into."),
    samples: int = typer.Option(1, help="Repeat each case N times and average."),
    floor: float = typer.Option(0.85, help="Minimum top-1 accuracy before this gate fails."),
    out: str = typer.Option("runs", help="Directory for the run artifact."),
    config: str = typer.Option(None, help="Path to a models.yaml."),
    skills_dir: str = typer.Option(None),
    repo_root: str = typer.Option(None),
    show_confusion: bool = typer.Option(False, "--confusion", help="Print the confusion matrix."),
):
    """Does the model pick the right skill? Measures trigger precision and collisions."""
    from . import routing_run
    from ._ollama import EndpointError

    root, skills_path = _resolve_paths(repo_root, skills_dir)
    try:
        result = routing_run.execute(
            skills_dir=skills_path,
            dataset=Path(dataset),
            models=[m.strip() for m in models.split(",")] if models else None,
            roster_mode=roster_mode,
            shards=shards,
            samples=samples,
            out_dir=Path(out),
            config_path=Path(config) if config else None,
            repo_root=root,
        )
    except (routing_run.RoutingSetupError, EndpointError) as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=EXIT_USAGE) from exc

    typer.echo(reporting.routing_to_text(result, show_confusion=show_confusion))
    typer.echo(f"\nsaved run: {result.artifact}")

    if result.summary.parse_failure_rate > MAX_PARSE_FAILURE_RATE:
        typer.echo(
            f"\njudge/model unusable: {result.summary.parse_failures} of "
            f"{result.summary.total} replies could not be parsed. Fix the endpoint before "
            "reading these scores as skill quality.",
            err=True,
        )
        raise typer.Exit(code=EXIT_JUDGE)
    if result.summary.accuracy < floor:
        typer.echo(
            f"\nrouting accuracy {result.summary.accuracy:.2f} is below the {floor:.2f} floor",
            err=True,
        )
        raise typer.Exit(code=EXIT_GATE)
    if result.breaches:
        typer.echo(
            f"\ndisable-model-invocation skills were auto-selected: "
            f"{', '.join(result.breaches)}",
            err=True,
        )
        raise typer.Exit(code=EXIT_GATE)


@app.command()
def scorecard(
    only: list[str] = typer.Option(None, "--only", help="Score just these skills (repeatable)."),
    changed_since: str = typer.Option(None, help="Score only skills touched since this git ref."),
    models: str = typer.Option(None, help="Comma-separated; the first is used as the subject."),
    judge_model: str = typer.Option(None, help="Judge model; defaults to config's judge.model."),
    samples: int = typer.Option(1, help="Repeat each dimension N times and take the median."),
    out: str = typer.Option("runs", help="Directory for the run artifact."),
    config: str = typer.Option(None, help="Path to a models.yaml."),
    gate: bool = typer.Option(False, help="Fail on any DEPRECATE verdict."),
    limit: int = typer.Option(None, help="Show only the N weakest skills."),
    skills_dir: str = typer.Option(None),
    repo_root: str = typer.Option(None),
):
    """Score every skill against skill-creator's 10-dimension rubric."""
    from . import scorecard_run
    from ._ollama import EndpointError
    from .routing_run import RoutingSetupError
    from .rubric import RubricParseError
    from .scorecard import parse_failure_rate

    root, skills_path = _resolve_paths(repo_root, skills_dir)
    try:
        result = scorecard_run.execute(
            skills_dir=skills_path,
            repo_root=root,
            only=list(only) if only else None,
            changed_since=changed_since,
            models=[m.strip() for m in models.split(",")] if models else None,
            judge_model=judge_model,
            samples=samples,
            out_dir=Path(out),
            config_path=Path(config) if config else None,
            state_tag_families=load_state_tag_families(root),
        )
    except (RoutingSetupError, RubricParseError, FileNotFoundError, EndpointError) as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=EXIT_USAGE) from exc

    typer.echo(reporting.scorecard_to_text(result, limit=limit))
    typer.echo(f"\nsaved run: {result.artifact}")

    if parse_failure_rate(result.scores) > MAX_PARSE_FAILURE_RATE:
        typer.echo(
            "\njudge unusable: too many replies could not be parsed. Fix the judge model "
            "before reading these scores as skill quality.",
            err=True,
        )
        raise typer.Exit(code=EXIT_JUDGE)

    if gate and result.deprecate:
        typer.echo(f"\nDEPRECATE verdict on: {', '.join(result.deprecate)}", err=True)
        raise typer.Exit(code=EXIT_GATE)


@app.command("quality-scaffold")
def quality_scaffold(
    skill: list[str] = typer.Option(..., "--skill", help="Skill to scaffold a case for."),
    task: str = typer.Option("<describe a realistic task for this skill>"),
    skills_dir: str = typer.Option(None),
    repo_root: str = typer.Option(None),
):
    """Emit draft quality cases with criteria derived from each skill's own words.

    Prints JSONL to stdout for you to edit and append to datasets/quality.jsonl. The
    criteria come from the skill's Non-Negotiable Constraints, workflow phases, and state
    fields — that is what makes L3 measure the skill rather than the judge's mood.
    """
    import json as _json

    from . import quality as quality_mod
    from .corpus import load_skill

    _, skills_path = _resolve_paths(repo_root, skills_dir)
    for name in skill:
        path = skills_path / name
        if not (path / "SKILL.md").is_file():
            typer.echo(f"no such skill: {name}", err=True)
            raise typer.Exit(code=EXIT_USAGE)
        loaded = load_skill(path)
        derived = quality_mod.derive_criteria(loaded)
        case = {
            "id": f"q-{name}-001",
            "category": "quality",
            "system_from_skill": name,
            "prompt": task,
            "scorer": {
                "type": "skill_rubric",
                "skill": name,
                "threshold": 0.7,
                "criteria": derived.as_list(),
                "state_tag": loaded.state_tags[0] if loaded.state_tags else None,
                "phases": derived.phases,
                "known_references": sorted({p.target for p in loaded.reference_pointers}),
            },
            "tags": ["quality"],
        }
        typer.echo(_json.dumps(case))


@app.command()
def quality(
    dataset: str = typer.Option("datasets/quality.jsonl", help="Quality cases (JSONL)."),
    skill: list[str] = typer.Option(None, "--skill", help="Run only cases for these skills."),
    models: str = typer.Option(None, help="Comma-separated models; defaults to config."),
    judge_model: str = typer.Option(None, help="Judge model; defaults to config's judge.model."),
    samples: int = typer.Option(1),
    out: str = typer.Option("runs"),
    config: str = typer.Option(None),
    skills_dir: str = typer.Option(None),
    repo_root: str = typer.Option(None),
):
    """Inject a SKILL.md as the system prompt and judge the output against its own criteria."""
    from . import quality_run
    from ._ollama import EndpointError
    from .routing_run import RoutingSetupError

    root, skills_path = _resolve_paths(repo_root, skills_dir)
    try:
        result = quality_run.execute(
            skills_dir=skills_path,
            dataset=Path(dataset),
            only=list(skill) if skill else None,
            models=[m.strip() for m in models.split(",")] if models else None,
            judge_model=judge_model,
            samples=samples,
            out_dir=Path(out),
            config_path=Path(config) if config else None,
            repo_root=root,
        )
    except (RoutingSetupError, EndpointError) as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=EXIT_USAGE) from exc

    typer.echo(reporting.quality_to_text(result))
    typer.echo(f"\nsaved run: {result.artifact}")

    if result.parse_failure_rate > MAX_PARSE_FAILURE_RATE:
        typer.echo("\njudge unusable: too many replies could not be parsed.", err=True)
        raise typer.Exit(code=EXIT_JUDGE)
    if result.failed:
        typer.echo(f"\nbelow threshold: {', '.join(result.failed)}", err=True)
        raise typer.Exit(code=EXIT_GATE)


@app.command("evals-md")
def evals_md(
    write: bool = typer.Option(False, help="Rewrite evals.md in place (default: preview)."),
    date: str = typer.Option(..., help="The run date to record, e.g. 2026-08-02."),
    lint_only: bool = typer.Option(True, "--lint/--no-lint", help="Record a fresh lint run."),
    baseline: str = typer.Option(None, help="Baseline to apply when recording the lint run."),
    skills_dir: str = typer.Option(None),
    repo_root: str = typer.Option(None),
):
    """Fill in evals.md's Last Run / Result fields from a real run.

    Only those two fields change. The criteria are the human's and are never rewritten.
    """
    from . import evalsmd

    root, skills_path = _resolve_paths(repo_root, skills_dir)
    target = root / "evals.md"
    if not target.is_file():
        typer.echo(f"no evals.md at {target}", err=True)
        raise typer.Exit(code=EXIT_USAGE)

    records = []
    if lint_only:
        findings = run_lint(
            skills_path,
            repo_root=root,
            baseline=baseline,
            state_tag_families=load_state_tag_families(root),
            known_non_skills=load_known_non_skills(root),
        )
        records.append(
            evalsmd.record_from_lint(findings, date, total_skills=len(discover(skills_path)))
        )

    if not records:
        typer.echo("nothing to record", err=True)
        raise typer.Exit(code=EXIT_USAGE)

    for record in records:
        typer.echo(f"Test Case {record.test_case}: {record.last_run} | {record.result}")

    if write:
        changed = evalsmd.update_file(target, records)
        typer.echo(f"\n{'updated' if changed else 'already current'}: {target}")
    else:
        typer.echo("\n(preview — pass --write to apply)")


@app.command("list-rules")
def list_rules():
    from .rules import all_rules

    for r in all_rules():
        summary = r.summary.strip().splitlines()[0] if r.summary.strip() else ""
        typer.echo(f"{r.id:<8} {r.severity.value:<8} {r.scope:<6} {summary}")


if __name__ == "__main__":  # pragma: no cover
    app()
# <AI-Generated END>
