# <AI-Generated START>
"""Executing an output-quality run.

Each case names the skill whose body becomes its system prompt (``system_from_skill``),
resolved here at run time rather than pasted into the dataset — a copied SKILL.md would go
stale the moment the skill was edited, and the eval would then be scoring a fossil.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from . import quality as quality_mod
from . import scorers  # noqa: F401 - registers skill_rubric
from ._ollama import (
    EndpointError,
    OllamaEvalsMissing,
    describe_endpoint_error,
    endpoint_errors,
    require,
)
from .corpus import discover
from .routing_run import RoutingSetupError


@dataclass
class QualityResult:
    run: object
    artifact: Path | None = None

    @property
    def rows(self):
        return [r for r in getattr(self.run, "results", []) if r.category == "quality"]

    @property
    def failed(self) -> list[str]:
        return sorted(
            r.case_id for r in self.rows
            if not r.passed and not (r.metadata or {}).get("parse_failure")
        )

    @property
    def parse_failure_rate(self) -> float:
        rows = self.rows
        if not rows:
            return 0.0
        return sum(1 for r in rows if (r.metadata or {}).get("parse_failure")) / len(rows)


def execute(
    *,
    skills_dir: Path,
    dataset: Path,
    only: list[str] | None = None,
    models: list[str] | None = None,
    judge_model: str | None = None,
    samples: int = 1,
    out_dir: Path | None = None,
    config_path: Path | None = None,
    repo_root: Path | None = None,
    client=None,
    judge=None,
) -> QualityResult:
    try:
        mods = require()
    except OllamaEvalsMissing as exc:
        raise RoutingSetupError(str(exc)) from exc

    if not dataset.is_file():
        raise RoutingSetupError(f"no quality dataset at {dataset}")

    skills = {s.name: s for s in discover(skills_dir)}
    cases = mods["cases"].load_cases(dataset)
    if only:
        wanted = set(only)
        cases = [c for c in cases if _skill_of(c) in wanted]
    if not cases:
        raise RoutingSetupError(f"{dataset} yielded no cases for this selection")

    for case in cases:
        name = _skill_of(case)
        if name not in skills:
            raise RoutingSetupError(f"case {case.id!r} names unknown skill {name!r}")
        # Resolved now, from disk — never a copy pasted into the dataset.
        case.system = quality_mod.system_prompt(skills[name])

    cfg = _config(mods, config_path)
    model_list = models or list(getattr(cfg, "models", []) or [])
    if not model_list:
        raise RoutingSetupError("no models specified (use --models or set models: in config)")

    client = client or mods["client"].OllamaClient(cfg.base_url)
    if judge is None:
        judge = (
            mods["judging"].RubricJudge(client, judge_model)
            if judge_model
            else mods["judging"].build_judge(cfg, client)
        )

    try:
        run = mods["runner"].run_suite(
            client, cases, model_list,
            config=cfg, judge=judge, samples=samples, suite="quality",
            output_preview_chars=4000,  # 600 truncates the reply a human must adjudicate
        )
    except endpoint_errors() as exc:
        raise EndpointError(describe_endpoint_error(exc, cfg.base_url, model_list[0])) from exc

    run.manifest["skills_under_test"] = sorted({_skill_of(c) for c in cases})
    artifact = mods["runner"].save_run(run, out_dir) if out_dir else None
    return QualityResult(run=run, artifact=artifact)


def _skill_of(case) -> str:
    return getattr(case, "system_from_skill", None) or (case.scorer or {}).get("skill") or ""


def _config(mods, config_path: Path | None):
    resolve = mods["config"].resolve_config_path
    load = mods["config"].load_config
    if config_path:
        return load(config_path)
    return load(resolve(Path(__file__).resolve().parents[2]))
# <AI-Generated END>
