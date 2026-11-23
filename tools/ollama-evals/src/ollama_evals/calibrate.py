# <AI-Generated START>
"""Judge calibration: measure a judge's agreement with human labels.

An uncalibrated LLM-as-judge is worse than none. Before trusting the judge as a gate,
run it against a small human-labelled set and check agreement (aim for >= 0.8).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class CalibrationExample:
    id: str
    prompt: str
    output: str
    criteria: str
    human_score: float


@dataclass
class CalibrationResult:
    n: int
    agreement: float
    rows: list[dict] = field(default_factory=list)
    false_passes: list[str] = field(default_factory=list)  # judge passed, human failed
    false_fails: list[str] = field(default_factory=list)   # judge failed, human passed
    unparsed: list[str] = field(default_factory=list)      # judge reply unreadable


def load_calibration(path: str | Path) -> list[CalibrationExample]:
    examples: list[CalibrationExample] = []
    for line in Path(path).read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        d = json.loads(line)
        examples.append(
            CalibrationExample(
                id=d["id"],
                prompt=d["prompt"],
                output=d["output"],
                criteria=d["criteria"],
                human_score=float(d["human_score"]),
            )
        )
    return examples


def calibrate(judge, examples: list[CalibrationExample], pass_threshold: float = 0.7):
    """pass_threshold matches the judge scorer's default (0.7): a 3/5 verdict fails a real
    case, so it must fail here too. An unreadable verdict never counts as agreement."""
    result = CalibrationResult(n=len(examples), agreement=0.0)
    agree = 0
    for ex in examples:
        verdict = judge.score(criteria=ex.criteria, prompt=ex.prompt, output=ex.output)
        parsed = getattr(verdict, "parsed", True)
        predicted_pass = verdict.score >= pass_threshold
        human_pass = ex.human_score >= pass_threshold
        matched = parsed and predicted_pass == human_pass
        agree += int(matched)
        if not parsed:
            result.unparsed.append(ex.id)
        elif predicted_pass and not human_pass:
            result.false_passes.append(ex.id)
        elif human_pass and not predicted_pass:
            result.false_fails.append(ex.id)
        result.rows.append(
            {
                "id": ex.id,
                "judge_score": verdict.score,
                "human_score": ex.human_score,
                "agree": matched,
            }
        )
    result.agreement = agree / result.n if result.n else 0.0
    return result
# <AI-Generated END>
