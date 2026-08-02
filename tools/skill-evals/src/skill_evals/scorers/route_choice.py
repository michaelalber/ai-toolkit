# <AI-Generated START>
"""The `skill_choice` scorer — did the model route to the right skill?

Three outcomes are kept distinct on purpose:

* a **wrong choice** is a routing failure, and says the descriptions overlap
* an **unparseable reply** is a *judge/model* failure and is counted separately; folding it
  into "wrong" would blame the skill descriptions for a broken endpoint
* a **runner-up hit** earns half credit, because "second on a 94-way choice" is materially
  different from "not in the running"
"""

from __future__ import annotations

from .._ollama import require

_mods = require()
register = _mods["scorers_base"].register
_ScoreResult = _mods["scorers_base"].ScoreResult
extract_json_obj = _mods["judging"].extract_json_obj

NONE = "none"


@register("skill_choice")
def skill_choice(output: str, spec: dict, context: dict):
    expected = spec.get("expected")
    acceptable = {a for a in (spec.get("acceptable") or ([expected] if expected else []))}

    payload = extract_json_obj(output)
    if payload is None or "skill" not in payload:
        return _ScoreResult(
            0.0, False,
            f"unparseable routing reply: {output.strip()[:120]!r}",
            metadata={"parse_failure": True, "chosen": None, "expected": expected},
        )

    chosen = _name(payload.get("skill"))
    runner_up = _name(payload.get("runner_up"))
    metadata = {"chosen": chosen, "runner_up": runner_up, "expected": expected}

    if expected is None:
        hit = chosen == NONE
        detail = "correctly declined" if hit else f"fired {chosen!r} when no skill should"
        return _ScoreResult(1.0 if hit else 0.0, hit, detail, metadata=metadata)

    if chosen in acceptable:
        return _ScoreResult(1.0, True, f"chose {chosen!r}", metadata=metadata)
    if runner_up in acceptable:
        return _ScoreResult(
            0.5, False, f"chose {chosen!r}; {runner_up!r} was runner-up", metadata=metadata
        )
    return _ScoreResult(
        0.0, False, f"chose {chosen!r}, expected one of {sorted(acceptable)}", metadata=metadata
    )


def _name(value) -> str:
    return str(value or NONE).strip().strip("`").lower() or NONE
# <AI-Generated END>
