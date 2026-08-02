# <AI-Generated START>
"""The `skill_rubric` scorer — was the skill actually followed?

One judge call **per criterion**, averaged. A single "rate this 1-5 overall" call collapses
five independent questions into one impression; per-criterion calls tell you *which*
constraint was ignored, which is the difference between a score and a bug report.

Alongside the judged score, a deterministic `structural` sub-score checks three things no
judge is needed for: did the reply emit the skill's state tag, did it name the workflow
phases, and did it invent a `references/` filename that does not exist. Reported beside the
judged score, never averaged into it — measured facts and opinions do not mix.
"""

from __future__ import annotations

import re

from .._ollama import require

_mods = require()
register = _mods["scorers_base"].register
_ScoreResult = _mods["scorers_base"].ScoreResult

_REFERENCE = re.compile(r"references/[\w./-]+\.md")


@register("skill_rubric")
def skill_rubric(output: str, spec: dict, context: dict):
    judge = context.get("judge")
    if judge is None:
        raise RuntimeError(
            "no judge in scoring context; build one with judging.build_judge() and pass "
            "it in context['judge']"
        )

    criteria = spec.get("criteria") or []
    if not criteria:
        raise ValueError("skill_rubric needs a non-empty 'criteria' list")

    threshold = float(spec.get("threshold", 0.7))
    prompt = context.get("prompt", "")

    per_criterion = []
    parse_failures = 0
    for criterion in criteria:
        verdict = judge.score(criteria=criterion, prompt=prompt, output=output)
        if not getattr(verdict, "parsed", True):
            parse_failures += 1
            continue
        per_criterion.append({"criterion": criterion, "score": verdict.score,
                              "reasoning": verdict.reasoning})

    structural = _structural(output, spec)
    if not per_criterion:
        return _ScoreResult(
            0.0, False, "every criterion judgement was unparseable",
            metadata={"parse_failure": True, "structural": structural},
        )

    score = sum(c["score"] for c in per_criterion) / len(per_criterion)
    weakest = min(per_criterion, key=lambda c: c["score"])
    detail = f"{score:.2f} over {len(per_criterion)} criteria; weakest: {weakest['criterion']}"
    return _ScoreResult(
        score,
        score >= threshold,
        detail,
        metadata={
            "threshold": threshold,
            "per_criterion": per_criterion,
            "structural": structural,
            "n_parse_failures": parse_failures,
        },
    )


def _structural(output: str, spec: dict) -> dict:
    """Facts about the reply that need no judge at all."""
    tag = spec.get("state_tag")
    phases = spec.get("phases") or []
    known_references = set(spec.get("known_references") or [])

    named = set(_REFERENCE.findall(output))
    return {
        "emitted_state_block": bool(tag) and f"<{tag}>" in output,
        "phases_named": [p for p in phases if p in output],
        "phases_missing": [p for p in phases if p not in output],
        # A skill that sends the agent to a file that does not exist is worse than one
        # that sends it nowhere.
        "hallucinated_references": sorted(named - known_references) if known_references else [],
    }
# <AI-Generated END>
