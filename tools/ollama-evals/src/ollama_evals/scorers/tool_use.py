# <AI-Generated START>
"""Tool-use scorer: did the model select the right tool with the right arguments?

Reads the parsed ``tool_calls`` from the scoring context (populated by the runner from
the model's response). Scoring: 0.5 for selecting the expected tool + 0.5 weighted by
the fraction of expected arguments matched. Passes only on an exact tool + argument match.
"""

from __future__ import annotations

from .base import ScoreResult, register


@register("tool_use")
def tool_use(output: str, spec: dict, context: dict) -> ScoreResult:
    expected = spec["expected"]
    name = expected["name"]
    expected_args = expected.get("arguments")
    calls = context.get("tool_calls") or []

    matched = next((c for c in calls if c.get("name") == name), None)
    if matched is None:
        return ScoreResult(0.0, False, f"expected tool {name!r} was not called")

    if not expected_args:
        return ScoreResult(1.0, True)

    got_args = matched.get("arguments") or {}
    if not isinstance(got_args, dict):
        return ScoreResult(0.5, False, "tool arguments were not valid JSON object")

    hits = sum(1 for k, v in expected_args.items() if got_args.get(k) == v)
    ratio = hits / len(expected_args)
    score = 0.5 + 0.5 * ratio
    passed = ratio == 1.0
    detail = "" if passed else f"argument mismatch: expected {expected_args}, got {got_args}"
    return ScoreResult(score, passed, detail)
# <AI-Generated END>
