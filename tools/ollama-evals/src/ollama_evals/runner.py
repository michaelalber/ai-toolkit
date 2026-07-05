# <AI-Generated START>
"""Run a suite of cases across one or more models and record a scored artifact.

Because Pi, Goose, and Open WebUI share the Ollama backend, running a model here measures
what all three would get from that model. A per-case failure is recorded, not raised, so a
single bad response never aborts a whole run.
"""

from __future__ import annotations

import json
import statistics
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from .cases import Case
from .scorers import score_output

OUTPUT_PREVIEW_CHARS = 600


@dataclass
class CaseResult:
    model: str
    case_id: str
    category: str
    score: float
    passed: bool
    detail: str = ""
    output: str = ""


@dataclass
class RunResult:
    manifest: dict
    results: list[CaseResult] = field(default_factory=list)

    def category_means(self) -> dict[str, dict[str, float]]:
        out: dict[str, dict[str, list[float]]] = {}
        for r in self.results:
            out.setdefault(r.model, {}).setdefault(r.category, []).append(r.score)
        return {m: {c: statistics.mean(v) for c, v in cats.items()} for m, cats in out.items()}

    def overall_means(self) -> dict[str, float]:
        by_model: dict[str, list[float]] = {}
        for r in self.results:
            by_model.setdefault(r.model, []).append(r.score)
        return {m: statistics.mean(v) for m, v in by_model.items()}

    def to_dict(self) -> dict:
        return {"manifest": self.manifest, "results": [asdict(r) for r in self.results]}


def run_suite(
    client,
    cases: list[Case],
    models: list[str],
    *,
    config=None,
    judge=None,
    samples: int = 1,
    system_prompt: str | None = None,
    run_id: str | None = None,
    created_at: str | None = None,
) -> RunResult:
    temperature = getattr(config, "temperature", 0.0)
    seed = getattr(config, "seed", 7)
    num_ctx = getattr(config, "num_ctx", None)

    manifest = {
        "run_id": run_id or uuid.uuid4().hex[:12],
        "created_at": created_at or datetime.now(timezone.utc).isoformat(),
        "base_url": getattr(config, "base_url", None),
        "models": models,
        "temperature": temperature,
        "seed": seed,
        "num_ctx": num_ctx,
        "n_cases": len(cases),
        "samples": samples,
    }

    results: list[CaseResult] = []
    for model in models:
        for case in cases:
            results.append(
                _run_one(
                    client, model, case, judge, samples,
                    temperature, seed, num_ctx, system_prompt,
                )
            )
    return RunResult(manifest=manifest, results=results)


def _run_one(client, model, case, judge, samples, temperature, seed, num_ctx, system_prompt):
    try:
        scores: list[float] = []
        passes: list[bool] = []
        last_detail = ""
        last_output = ""
        for _ in range(max(1, samples)):
            messages = list(case.messages or [])
            if system_prompt:
                messages = [{"role": "system", "content": system_prompt}, *messages]
            result = client.chat(
                model=model,
                messages=messages,
                temperature=temperature,
                seed=seed,
                num_ctx=num_ctx,
                tools=case.tools,
            )
            context = {
                "tool_calls": getattr(result, "tool_calls", []),
                "prompt": case.user_prompt,
                "judge": judge,
                "reference": case.reference,
            }
            scored = score_output(result.content, case.scorer, context)
            scores.append(scored.score)
            passes.append(scored.passed)
            last_detail = scored.detail
            last_output = result.content
        passed = sum(passes) > len(passes) / 2 if len(passes) > 1 else passes[0]
        return CaseResult(
            model=model,
            case_id=case.id,
            category=case.category,
            score=statistics.mean(scores),
            passed=passed,
            detail=last_detail,
            output=last_output[:OUTPUT_PREVIEW_CHARS],
        )
    except Exception as exc:  # noqa: BLE001 - a bad response must not abort the run
        return CaseResult(model, case.id, case.category, 0.0, False, detail=f"error: {exc}")


def save_run(run: RunResult, out_dir: str | Path) -> Path:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{run.manifest['run_id']}.run.json"
    path.write_text(json.dumps(run.to_dict(), indent=2))
    return path


def load_run(path: str | Path) -> RunResult:
    data = json.loads(Path(path).read_text())
    results = [CaseResult(**r) for r in data["results"]]
    return RunResult(manifest=data["manifest"], results=results)
# <AI-Generated END>
