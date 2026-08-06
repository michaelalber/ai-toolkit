# <AI-Generated START>
"""Executing a scorecard run.

Persistence reuses ollama-evals wholesale: each dimension becomes a ``CaseResult`` with
``category="rubric-dN"`` and ``case_id=<skill>``, so ``compare_runs`` works untouched and
its existing any-category gate fires when a single dimension degrades corpus-wide. That
reuse is the reason the scorecard needs no comparison logic of its own.
"""

from __future__ import annotations

import re
import subprocess  # noqa: S404 - only ever runs a fixed `git diff --name-only` argv
from dataclasses import dataclass
from pathlib import Path

from . import scorecard as scorecard_mod
from ._ollama import (
    EndpointError,
    OllamaEvalsMissing,
    describe_endpoint_error,
    endpoint_errors,
    require,
)
from .corpus import discover
from .lint import build_context
from .routing_run import RoutingSetupError

# A git revision, never an option: must not start with '-'.
_GIT_REF = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/~^:@{}-]*$")


@dataclass
class ScorecardResult:
    scores: list
    rubric: object
    summary: dict
    run: object
    artifact: Path | None = None

    @property
    def deprecate(self) -> list[str]:
        return sorted(
            s.skill for s in self.scores if s.verdict(self.rubric) == "DEPRECATE"
        )

    @property
    def revise(self) -> list[str]:
        return sorted(s.skill for s in self.scores if s.verdict(self.rubric) == "REVISE")


def execute(
    *,
    skills_dir: Path,
    repo_root: Path,
    only: list[str] | None = None,
    changed_since: str | None = None,
    models: list[str] | None = None,
    judge_model: str | None = None,
    samples: int = 1,
    out_dir: Path | None = None,
    config_path: Path | None = None,
    client=None,
    judge=None,
    state_tag_families: dict | None = None,
) -> ScorecardResult:
    try:
        mods = require()
    except OllamaEvalsMissing as exc:
        raise RoutingSetupError(str(exc)) from exc

    rubric = scorecard_mod.load_rubric(repo_root)
    skills = discover(skills_dir)
    selected = _select(skills, only, changed_since, repo_root)
    if not selected:
        raise RoutingSetupError("no skills selected")

    cfg = _config(mods, config_path)
    model_list = models or list(getattr(cfg, "models", []) or [])
    if not model_list:
        raise RoutingSetupError("no models specified (use --models or set models: in config)")
    model = model_list[0]

    if judge is None:
        client = client or mods["client"].OllamaClient(cfg.base_url)
        judge = (
            mods["judging"].RubricJudge(client, judge_model)
            if judge_model
            else mods["judging"].build_judge(cfg, client)
        )

    ctx = build_context(skills, repo_root=repo_root, state_tag_families=state_tag_families)
    try:
        scores = [
            scorecard_mod.score_skill(skill, rubric, judge, ctx, samples=samples)
            for skill in selected
        ]
    except endpoint_errors() as exc:
        raise EndpointError(
            describe_endpoint_error(
                exc, getattr(cfg, "base_url", "?"), judge_model or getattr(cfg.judge, "model", None)
            )
        ) from exc

    run = mods["runner"].RunResult(
        manifest={
            "run_id": _run_id(),
            "suite": "scorecard",
            "models": [model],
            "base_url": getattr(cfg, "base_url", None),
            "samples": samples,
            "n_cases": len(selected),
            "rubric_sha256": rubric.sha256,
            "n_dimensions": len(rubric.dimensions),
        },
        results=scorecard_mod.to_case_results(scores, model, mods["runner"].CaseResult),
    )
    artifact = mods["runner"].save_run(run, out_dir) if out_dir else None

    return ScorecardResult(
        scores=scores,
        rubric=rubric,
        summary=scorecard_mod.summarise(scores, rubric),
        run=run,
        artifact=artifact,
    )


def _select(skills, only, changed_since, repo_root):
    if only:
        wanted = set(only)
        chosen = [s for s in skills if s.name in wanted]
        missing = wanted - {s.name for s in chosen}
        if missing:
            raise RoutingSetupError(f"unknown skill(s): {', '.join(sorted(missing))}")
        return chosen
    if changed_since:
        touched = _changed_skills(repo_root, changed_since)
        return [s for s in skills if s.name in touched]
    return skills


def _changed_skills(repo_root: Path, ref: str) -> set[str]:
    if not _GIT_REF.match(ref):
        # Passed straight to git. Without this, `--changed-since --upload-pack=...` would
        # reach git as an option rather than a revision.
        raise RoutingSetupError(
            f"{ref!r} is not a valid git revision (letters, digits, and ./_-~^:@{{}} only)"
        )
    try:
        out = subprocess.run(  # noqa: S603 - fixed argv, no shell, no user interpolation
            ["git", "diff", "--name-only", ref, "--", "skills/"],
            cwd=repo_root, capture_output=True, text=True, check=True, timeout=30,
        ).stdout
    except (subprocess.SubprocessError, OSError) as exc:
        raise RoutingSetupError(f"could not read git diff against {ref!r}: {exc}") from exc
    names = set()
    for line in out.splitlines():
        parts = Path(line).parts
        if len(parts) >= 2 and parts[0] == "skills":
            names.add(parts[1])
    return names


def _run_id() -> str:
    """A fresh id per invocation.

    Two back-to-back runs (e.g. a manual variance check) must land in distinct
    artifacts, never overwrite each other silently. Matches ollama-evals'
    ``runner.save_run`` default (``uuid.uuid4().hex[:12]``); this used to hash
    (rubric, model, n) instead, so identical repeat invocations collided on the
    same filename and clobbered the prior run's data.
    """
    import uuid

    return uuid.uuid4().hex[:12]


def _config(mods, config_path: Path | None):
    resolve = mods["config"].resolve_config_path
    load = mods["config"].load_config
    if config_path:
        return load(config_path)
    return load(resolve(Path(__file__).resolve().parents[2]))
# <AI-Generated END>
