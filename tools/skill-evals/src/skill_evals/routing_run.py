# <AI-Generated START>
"""Executing a routing run.

Kept out of cli.py so the orchestration is testable with a fake client and no live
endpoint, and so the CLI stays a thin argument-parsing layer.

Per-case system prompts carry the roster. In `shard` mode each case gets a *different*
roster — the one containing its expected skill — which is exactly what `Case.system`
(added to ollama-evals for this) exists to support.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from . import roster as roster_mod
from . import route as route_mod
from . import scorers  # noqa: F401 - registers skill_choice before any run
from ._ollama import (
    EndpointError,
    OllamaEvalsMissing,
    describe_endpoint_error,
    endpoint_errors,
    require,
)
from .corpus import discover


class RoutingSetupError(RuntimeError):
    """Anything that makes a run impossible before a single request is sent."""


@dataclass
class RoutingResult:
    run: object
    summary: route_mod.RoutingSummary
    collisions: list
    confusion: dict
    breaches: list[str]
    roster_sha: str
    roster_mode: str
    artifact: Path | None = None


def execute(
    *,
    skills_dir: Path,
    dataset: Path,
    models: list[str] | None = None,
    roster_mode: str = roster_mod.FULL,
    shards: int = 3,
    samples: int = 1,
    out_dir: Path | None = None,
    config_path: Path | None = None,
    repo_root: Path | None = None,
    client=None,
    collision_threshold: float = 0.2,
) -> RoutingResult:
    try:
        mods = require()
    except OllamaEvalsMissing as exc:
        raise RoutingSetupError(str(exc)) from exc

    if not dataset.is_file():
        raise RoutingSetupError(f"no routing dataset at {dataset}")

    skills = discover(skills_dir)
    cases = mods["cases"].load_cases(dataset)
    if not cases:
        raise RoutingSetupError(f"{dataset} contains no cases")
    _require_scorers(mods, cases)

    cfg = _config(mods, config_path, repo_root)
    model_list = models or list(getattr(cfg, "models", []) or [])
    if not model_list:
        raise RoutingSetupError("no models specified (use --models or set models: in config)")

    full_roster = roster_mod.build(skills, roster_mod.FULL)
    for case in cases:
        case.system = _roster_for(skills, case, roster_mode, shards).system_prompt()

    client = client or mods["client"].OllamaClient(cfg.base_url)
    try:
        run = mods["runner"].run_suite(
            client, cases, model_list,
            config=cfg, samples=samples, suite="routing",
            output_preview_chars=400,
        )
    except endpoint_errors() as exc:
        raise EndpointError(
            describe_endpoint_error(exc, cfg.base_url, model_list[0])
        ) from exc
    run.manifest["roster_sha256"] = full_roster.sha256
    run.manifest["roster_mode"] = roster_mode
    run.manifest["roster_size"] = len(full_roster.names)
    run.manifest["roster_withheld"] = list(full_roster.withheld)

    artifact = mods["runner"].save_run(run, out_dir) if out_dir else None

    return RoutingResult(
        run=run,
        summary=route_mod.summarise(run),
        collisions=route_mod.collisions(run, threshold=collision_threshold),
        confusion=route_mod.confusion_matrix(run),
        breaches=route_mod.never_auto_selected(run, _non_invocable(skills)),
        roster_sha=full_roster.sha256,
        roster_mode=roster_mode,
        artifact=artifact,
    )


def _require_scorers(mods, cases) -> None:
    """Fail loudly on an unregistered scorer type.

    The runner records a per-case exception as score 0.0 so one bad response cannot abort
    a run — which means a typo'd or unregistered scorer looks exactly like "the model got
    everything wrong". Checking up front keeps those two apart.
    """
    get_scorer = mods["scorers_base"].get_scorer
    for name in sorted({c.scorer.get("type") for c in cases}):
        try:
            get_scorer(name)
        except KeyError as exc:
            raise RoutingSetupError(str(exc).strip("\"'")) from exc


def _roster_for(skills, case, mode: str, shards: int):
    """A per-case roster, so a sharded run never hides the answer from the model."""
    if mode != roster_mod.SHARD:
        return roster_mod.build(skills, mode)
    expected = (case.scorer or {}).get("expected")
    index = abs(hash(case.id)) % max(1, shards) if expected is None else None
    if index is None:
        names = sorted(s.name for s in skills)
        index = names.index(expected) % shards if expected in names else 0
    return roster_mod.build(
        skills, roster_mod.SHARD, shards=shards, shard_index=index, must_include=expected
    )


def _non_invocable(skills) -> list[str]:
    return [s.name for s in skills if roster_mod.is_non_invocable(s)]


def _config(mods, config_path: Path | None, repo_root: Path | None):
    resolve = mods["config"].resolve_config_path
    load = mods["config"].load_config
    if config_path:
        return load(config_path)
    here = Path(__file__).resolve().parents[2]
    return load(resolve(here))
# <AI-Generated END>
