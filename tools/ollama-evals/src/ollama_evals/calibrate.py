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


def calibrate(judge, examples: list[CalibrationExample], pass_threshold: float = 0.5):
    rows = []
    agree = 0
    for ex in examples:
        verdict = judge.score(criteria=ex.criteria, prompt=ex.prompt, output=ex.output)
        predicted_pass = verdict.score >= pass_threshold
        human_pass = ex.human_score >= pass_threshold
        matched = predicted_pass == human_pass
        agree += int(matched)
        rows.append(
            {
                "id": ex.id,
                "judge_score": verdict.score,
                "human_score": ex.human_score,
                "agree": matched,
            }
        )
    n = len(examples)
    return CalibrationResult(n=n, agreement=(agree / n if n else 0.0), rows=rows)
# <AI-Generated END>
