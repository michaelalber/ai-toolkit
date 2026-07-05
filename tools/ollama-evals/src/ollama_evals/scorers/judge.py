# <AI-Generated START>
"""LLM-as-judge scorer.

Delegates the actual grading to a Judge object supplied in the scoring context
(``context["judge"]``), so the scorer stays framework-agnostic and unit-testable with a
fake judge. Build a real judge with ``ollama_evals.judging.build_judge``.
"""

from __future__ import annotations

from .base import ScoreResult, register


@register("judge")
def llm_judge(output: str, spec: dict, context: dict) -> ScoreResult:
    judge = context.get("judge")
    if judge is None:
        raise RuntimeError(
            "no judge in scoring context; construct one with judging.build_judge() and pass "
            "it in context['judge']"
        )
    threshold = float(spec.get("threshold", 0.7))
    verdict = judge.score(
        criteria=spec["criteria"],
        prompt=context.get("prompt", ""),
        output=output,
        reference=spec.get("reference") or context.get("reference"),
    )
    passed = verdict.score >= threshold
    return ScoreResult(verdict.score, passed, verdict.reasoning, metadata={"threshold": threshold})
# <AI-Generated END>
