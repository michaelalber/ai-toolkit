# <AI-Generated START>
"""L4 — score every skill against the 10-dimension rubric.

One judge call per **dimension**, not per skill. A single ten-score call anchors all ten on
one impression and separates poorly; per-dimension prompts carry only that dimension's
criteria table (so they fit a small num_ctx), a parse failure costs one dimension instead
of ten, and each dimension becomes an independently comparable metric for the compare gate.

Determinism comes from four layers, in increasing order of force:

1. temperature 0 / fixed seed
2. a measured **evidence pack** so the judge never has to count
3. a response contract whose ``evidence`` field must quote the file verbatim
4. **deterministic overrides** for the mechanical dimensions — where a fact decides the
   score outright, the computed value wins and the judge's opinion is discarded

A dimension that cannot be parsed is *omitted from the total*, never scored 0: a broken
judge must not read as a bad skill.
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass, field

from . import rubric as rubric_mod
from .lint import evidence_for

STATIC = "static"
JUDGE = "judge"

_PROMPT = """You are scoring one dimension of one AI skill definition. Be strict.

DIMENSION {number} — {name}
{question}

SCORING CRITERIA (choose the integer whose criteria the skill actually meets):
{criteria}

MEASURED FACTS about this skill (these are already verified — do not recount them):
{evidence}

SKILL.md:
---
{body}
---

Reply with ONLY a JSON object:
{{"score": <1-5>, "evidence": "<a short phrase copied VERBATIM from SKILL.md>", \
"reasoning": "<one sentence>"}}"""


@dataclass
class DimensionScore:
    key: str
    number: int
    name: str
    score: float | None
    source: str = JUDGE
    reasoning: str = ""
    parse_failure: bool = False


@dataclass
class SkillScore:
    skill: str
    dimensions: list[DimensionScore] = field(default_factory=list)

    @property
    def scored(self) -> list[DimensionScore]:
        return [d for d in self.dimensions if d.score is not None]

    @property
    def total(self) -> float:
        return sum(d.score for d in self.scored if d.score is not None)

    @property
    def incomplete(self) -> bool:
        return len(self.scored) < len(self.dimensions)

    @property
    def parse_failures(self) -> int:
        return sum(1 for d in self.dimensions if d.parse_failure)

    def verdict(self, rubric) -> str:
        if self.incomplete:
            return "INCOMPLETE"
        return rubric.verdict(self.total)


def score_skill(skill, rubric, judge, ctx=None, samples: int = 1) -> SkillScore:
    evidence = evidence_for(skill, ctx)
    result = SkillScore(skill=skill.name)
    for dimension in rubric.dimensions:
        result.dimensions.append(_score_dimension(skill, dimension, evidence, judge, samples))
    return result


def _score_dimension(skill, dimension, evidence, judge, samples: int) -> DimensionScore:
    override = deterministic_override(dimension, evidence)
    if override is not None:
        value, why = override
        return DimensionScore(dimension.key, dimension.number, dimension.name, float(value),
                              source=STATIC, reasoning=why)

    prompt = _PROMPT.format(
        number=dimension.number,
        name=dimension.name,
        question=dimension.question,
        criteria=dimension.criteria_table(),
        evidence="\n".join(f"- {k}: {v}" for k, v in evidence.items()),
        body=skill.text,
    )

    scores: list[float] = []
    reasoning = ""
    for _ in range(max(1, samples)):
        verdict = judge.score(criteria=prompt, prompt=skill.name, output=skill.text)
        if not getattr(verdict, "parsed", True):
            continue
        # RubricJudge normalises 1-5 to 0-1; bring it back to the rubric's own scale.
        scores.append(verdict.score * 4.0 + 1.0)
        reasoning = verdict.reasoning

    if not scores:
        return DimensionScore(dimension.key, dimension.number, dimension.name, None,
                              reasoning="judge reply unparseable", parse_failure=True)
    # Median, not mean: one outlier sample must not drag a baseline.
    return DimensionScore(dimension.key, dimension.number, dimension.name,
                          float(statistics.median(scores)), reasoning=reasoning)


def deterministic_override(dimension, evidence) -> tuple[int, str] | None:
    """Where a measured fact decides the score outright, the fact wins.

    Roughly three of the ten dimensions become fully reproducible this way, which is what
    makes a scorecard usable as a regression baseline on a local model.
    """
    key = dimension.key

    if key == "d3":  # Lean Layout Discipline
        lines = evidence["line_count"]
        if lines > 400:
            return 1, f"{lines} lines — over 400"
        if lines > 320:
            return 2, f"{lines} lines — 320-400 band"
        if lines > 250:
            return 3, f"{lines} lines — 250-320 band"
        return None

    if key == "d5":  # State Block Presence and Uniqueness
        undeclared = [
            tag for tag in evidence["state_tag_shared_with"]
            if tag not in evidence["state_tag_declared_family"]
        ]
        if undeclared:
            return 2, f"state tag collides outside a declared family: {', '.join(undeclared)}"
        if not evidence["state_tags"] and evidence["tier"] == "full":
            return 1, "no state block in a full-template skill"
        return None

    if key == "d9":  # Reference Hygiene
        n = len(evidence["reference_files"])
        if evidence["tier"] == "exempt":
            return None  # a sub-20-line skill needs no references at all
        if n == 0:
            return 1, "references/ missing or empty"
        if n == 1:
            return 3, "only one reference file"
        return None

    return None


def summarise(scores, rubric) -> dict:
    verdicts: dict[str, int] = {}
    for s in scores:
        verdicts[s.verdict(rubric)] = verdicts.get(s.verdict(rubric), 0) + 1
    totals = [s.total for s in scores if not s.incomplete]
    return {
        "n_skills": len(scores),
        "verdicts": verdicts,
        "mean_total": statistics.mean(totals) if totals else 0.0,
        "median_total": statistics.median(totals) if totals else 0.0,
        "max_total": rubric.max_total,
        "parse_failures": sum(s.parse_failures for s in scores),
        "n_dimension_calls": sum(len(s.dimensions) for s in scores),
    }


def parse_failure_rate(scores) -> float:
    calls = sum(len(s.dimensions) for s in scores)
    return sum(s.parse_failures for s in scores) / calls if calls else 0.0


def to_case_results(scores, model: str, case_result_cls):
    """One CaseResult per dimension, so ollama-evals' compare gate works untouched.

    Category is the dimension (``rubric-d3``), case id is the skill — which makes the
    existing any-category gate fire when a single dimension degrades corpus-wide.
    """
    rows = []
    for skill_score in scores:
        for d in skill_score.dimensions:
            if d.score is None:
                continue
            rows.append(
                case_result_cls(
                    model, skill_score.skill, f"rubric-{d.key}",
                    (d.score - 1.0) / 4.0,  # normalise to 0-1 for compare_runs
                    d.score >= 4.0,
                    detail=d.reasoning,
                    metadata={"raw_score": d.score, "source": d.source},
                )
            )
    return rows


def load_rubric(repo_root) -> rubric_mod.Rubric:
    return rubric_mod.load(repo_root / rubric_mod.RUBRIC_PATH)
# <AI-Generated END>
