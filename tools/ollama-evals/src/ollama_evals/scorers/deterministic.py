# <AI-Generated START>
"""Deterministic scorers: exact, contains, regex, json_schema.

Cheap, fast, and un-gameable — the strongest regression canaries. json_schema uses the
`jsonschema` library rather than a hand-rolled validator.
"""

from __future__ import annotations

import json
import re

import jsonschema

from .base import ScoreResult, register


@register("exact")
def exact(output: str, spec: dict, context: dict) -> ScoreResult:
    expected = spec["value"]
    got = output.strip()
    exp = expected.strip()
    if not spec.get("case_sensitive", False):
        got, exp = got.lower(), exp.lower()
    passed = got == exp
    return ScoreResult(1.0 if passed else 0.0, passed, "" if passed else f"expected {expected!r}")


@register("contains")
def contains(output: str, spec: dict, context: dict) -> ScoreResult:
    if "all" in spec:
        needles = spec["all"]
        hits = [n for n in needles if n in output]
        score = len(hits) / len(needles) if needles else 1.0
        passed = len(hits) == len(needles)
        missing = [n for n in needles if n not in output]
        return ScoreResult(score, passed, "" if passed else f"missing {missing}")
    needle = spec["value"]
    passed = needle in output
    return ScoreResult(1.0 if passed else 0.0, passed, "" if passed else f"missing {needle!r}")


@register("regex")
def regex(output: str, spec: dict, context: dict) -> ScoreResult:
    flags = re.IGNORECASE if not spec.get("case_sensitive", False) else 0
    passed = re.search(spec["pattern"], output, flags) is not None
    return ScoreResult(1.0 if passed else 0.0, passed, "" if passed else "pattern not found")


@register("json_schema")
def json_schema(output: str, spec: dict, context: dict) -> ScoreResult:
    payload = _extract_json(output)
    if payload is None:
        return ScoreResult(0.0, False, "no valid JSON found in output")
    try:
        jsonschema.validate(payload, spec["schema"])
    except jsonschema.ValidationError as exc:
        return ScoreResult(0.0, False, f"schema violation: {exc.message}")
    return ScoreResult(1.0, True)


_FENCE = re.compile(r"```(?:json)?\s*(.*?)```", re.DOTALL)


def _extract_json(output: str):
    """Return parsed JSON from the output, tolerating a surrounding ```json fence."""
    candidates = [output]
    m = _FENCE.search(output)
    if m:
        candidates.insert(0, m.group(1))
    for candidate in candidates:
        try:
            return json.loads(candidate.strip())
        except json.JSONDecodeError:
            continue
    return None
# <AI-Generated END>
