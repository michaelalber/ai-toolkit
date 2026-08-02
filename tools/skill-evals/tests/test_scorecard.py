from pathlib import Path

import pytest
from conftest import CANONICAL_BODY, filler, write_good_full, write_skill, write_tiny

from skill_evals import rubric as rubric_mod
from skill_evals import scorecard
from skill_evals.corpus import discover, load_skill
from skill_evals.lint import build_context, evidence_for

REPO_ROOT = Path(__file__).resolve().parents[3]
REAL_RUBRIC = REPO_ROOT / rubric_mod.RUBRIC_PATH


@pytest.fixture(scope="module")
def rubric():
    if not REAL_RUBRIC.is_file():
        pytest.skip("real scoring-rubric.md not present")
    return rubric_mod.load(REAL_RUBRIC)


class Verdict:
    def __init__(self, score, parsed=True, reasoning="because"):
        self.score = score  # already normalised 0-1, as RubricJudge returns
        self.parsed = parsed
        self.reasoning = reasoning


class FakeJudge:
    """Returns a scripted verdict per call; records the prompts it saw."""

    def __init__(self, verdicts):
        self._verdicts = list(verdicts)
        self.prompts = []

    def score(self, *, criteria, prompt, output, reference=None):
        self.prompts.append(criteria)
        return self._verdicts.pop(0) if self._verdicts else Verdict(0.75)


# --- evidence pack -----------------------------------------------------------------


def test_evidence_reports_measured_facts(skills_dir: Path):
    write_good_full(skills_dir, "alpha")
    ev = evidence_for(load_skill(skills_dir / "alpha"))
    assert ev["name"] == "alpha"
    assert ev["tier"] == "full"
    assert ev["line_count"] > 100
    assert "Core Philosophy" in ev["sections"]
    assert any("conventions.md" in f for f in ev["reference_files"])
    assert ev["unresolved_pointers"] == []


def test_evidence_reports_unresolved_pointers(skills_dir: Path):
    body = CANONICAL_BODY.replace("references/templates.md", "references/gone.md")
    write_good_full(skills_dir, "alpha", body=body)
    ev = evidence_for(load_skill(skills_dir / "alpha"))
    assert ev["unresolved_pointers"] == ["references/gone.md"]


def test_evidence_reports_shared_state_tags(skills_dir: Path):
    for name in ("python-security-review", "rust-security-review"):
        body = CANONICAL_BODY.replace("good-full-state", "security-review-state")
        write_good_full(skills_dir, name, body=body)
    skills = discover(skills_dir)
    ctx = build_context(skills)
    ev = evidence_for(skills[0], ctx)
    assert "security-review-state" in ev["state_tag_shared_with"]
    assert len(ev["state_tag_shared_with"]["security-review-state"]) == 2


def test_evidence_marks_a_declared_family_as_declared(skills_dir: Path):
    for name in ("python-security-review", "rust-security-review"):
        body = CANONICAL_BODY.replace("good-full-state", "security-review-state")
        write_good_full(skills_dir, name, body=body)
    skills = discover(skills_dir)
    ctx = build_context(skills, state_tag_families={
        "security-review-state": {"skills": [s.name for s in skills], "rationale": "family"}
    })
    ev = evidence_for(skills[0], ctx)
    assert ev["state_tag_declared_family"] == ["security-review-state"]


# --- deterministic overrides -------------------------------------------------------


def test_d3_override_fires_on_an_oversized_skill(rubric):
    d3 = rubric.by_key("d3")
    assert scorecard.deterministic_override(d3, {"line_count": 450})[0] == 1
    assert scorecard.deterministic_override(d3, {"line_count": 350})[0] == 2
    assert scorecard.deterministic_override(d3, {"line_count": 280})[0] == 3


def test_d3_leaves_a_lean_skill_to_the_judge(rubric):
    assert scorecard.deterministic_override(rubric.by_key("d3"), {"line_count": 150}) is None


def test_d5_override_fires_on_an_undeclared_collision(rubric):
    ev = {"state_tag_shared_with": {"tdd-state": ["tdd-loop", "tdd-agent"]},
          "state_tag_declared_family": [], "state_tags": ["tdd-state"], "tier": "full"}
    score, why = scorecard.deterministic_override(rubric.by_key("d5"), ev)
    assert score == 2 and "tdd-state" in why


def test_d5_does_not_punish_a_declared_family(rubric):
    ev = {"state_tag_shared_with": {"security-review-state": ["a", "b"]},
          "state_tag_declared_family": ["security-review-state"],
          "state_tags": ["security-review-state"], "tier": "full"}
    assert scorecard.deterministic_override(rubric.by_key("d5"), ev) is None


def test_d5_override_fires_on_a_missing_state_block(rubric):
    ev = {"state_tag_shared_with": {}, "state_tag_declared_family": [],
          "state_tags": [], "tier": "full"}
    assert scorecard.deterministic_override(rubric.by_key("d5"), ev)[0] == 1


def test_d9_override_scales_with_reference_count(rubric):
    d9 = rubric.by_key("d9")
    assert scorecard.deterministic_override(d9, {"reference_files": [], "tier": "full"})[0] == 1
    assert scorecard.deterministic_override(d9, {"reference_files": ["a"], "tier": "full"})[0] == 3
    assert scorecard.deterministic_override(
        d9, {"reference_files": ["a", "b"], "tier": "full"}
    ) is None


def test_d9_exempts_a_sub_20_line_skill(rubric):
    assert scorecard.deterministic_override(
        rubric.by_key("d9"), {"reference_files": [], "tier": "exempt"}
    ) is None


def test_a_dimension_with_no_override_is_left_to_the_judge(rubric):
    assert scorecard.deterministic_override(rubric.by_key("d1"), {"line_count": 100}) is None


# --- scoring a skill ---------------------------------------------------------------


def test_every_dimension_is_scored(skills_dir: Path, rubric):
    write_good_full(skills_dir, "alpha")
    result = scorecard.score_skill(load_skill(skills_dir / "alpha"), rubric, FakeJudge([]))
    assert len(result.dimensions) == 10
    assert not result.incomplete


def test_the_judge_is_asked_once_per_non_overridden_dimension(skills_dir: Path, rubric):
    write_good_full(skills_dir, "alpha")
    judge = FakeJudge([])
    scorecard.score_skill(load_skill(skills_dir / "alpha"), rubric, judge)
    # 10 dimensions, minus whichever were decided statically
    assert 1 <= len(judge.prompts) <= 10


def test_the_prompt_carries_the_evidence_pack(skills_dir: Path, rubric):
    write_good_full(skills_dir, "alpha")
    judge = FakeJudge([])
    scorecard.score_skill(load_skill(skills_dir / "alpha"), rubric, judge)
    assert "MEASURED FACTS" in judge.prompts[0]
    assert "line_count" in judge.prompts[0]
    assert "do not recount" in judge.prompts[0]


def test_the_prompt_carries_only_one_dimensions_criteria(skills_dir: Path, rubric):
    write_good_full(skills_dir, "alpha")
    judge = FakeJudge([])
    scorecard.score_skill(load_skill(skills_dir / "alpha"), rubric, judge)
    first = judge.prompts[0]
    assert first.count("SCORING CRITERIA") == 1
    assert "DIMENSION" in first


def test_judge_scores_are_denormalised_to_the_rubric_scale(skills_dir: Path, rubric):
    write_good_full(skills_dir, "alpha")
    result = scorecard.score_skill(
        load_skill(skills_dir / "alpha"), rubric, FakeJudge([Verdict(1.0)] * 10)
    )
    judged = [d for d in result.dimensions if d.source == scorecard.JUDGE]
    assert all(d.score == 5.0 for d in judged)  # 1.0 normalised -> 5 on the rubric


def test_a_static_override_beats_the_judge(skills_dir: Path, rubric):
    """A 500-line skill scores 1 on layout no matter how the judge feels about it."""
    body = CANONICAL_BODY + "\n" + "\n".join(f"pad {i}" for i in range(500))
    write_good_full(skills_dir, "fat", body=body)
    result = scorecard.score_skill(
        load_skill(skills_dir / "fat"), rubric, FakeJudge([Verdict(1.0)] * 10)
    )
    d3 = next(d for d in result.dimensions if d.key == "d3")
    assert d3.score == 1.0 and d3.source == scorecard.STATIC


def test_a_parse_failure_omits_the_dimension_rather_than_scoring_zero(skills_dir: Path, rubric):
    write_good_full(skills_dir, "alpha")
    result = scorecard.score_skill(
        load_skill(skills_dir / "alpha"), rubric, FakeJudge([Verdict(0.0, parsed=False)])
    )
    failed = [d for d in result.dimensions if d.parse_failure]
    assert len(failed) == 1
    assert failed[0].score is None          # omitted, not 0
    assert result.incomplete
    assert result.verdict(rubric) == "INCOMPLETE"


def test_the_total_excludes_omitted_dimensions(skills_dir: Path, rubric):
    write_good_full(skills_dir, "alpha")
    result = scorecard.score_skill(
        load_skill(skills_dir / "alpha"), rubric,
        FakeJudge([Verdict(0.0, parsed=False)] + [Verdict(1.0)] * 9),
    )
    assert result.total == sum(d.score for d in result.scored)
    assert all(d.score is not None for d in result.scored)


def test_samples_are_aggregated_by_median(skills_dir: Path, rubric):
    """One outlier sample must not drag a baseline."""
    write_good_full(skills_dir, "alpha")
    judge = FakeJudge([Verdict(0.0), Verdict(1.0), Verdict(1.0)] * 10)
    result = scorecard.score_skill(load_skill(skills_dir / "alpha"), rubric, judge, samples=3)
    judged = [d for d in result.dimensions if d.source == scorecard.JUDGE]
    assert judged[0].score == 5.0  # median of (1, 5, 5), not the mean of 3.67


# --- aggregation --------------------------------------------------------------------


def _score(name, per_dimension, rubric):
    s = scorecard.SkillScore(skill=name)
    for d in rubric.dimensions:
        s.dimensions.append(
            scorecard.DimensionScore(d.key, d.number, d.name, float(per_dimension))
        )
    return s


def test_summary_counts_verdicts(rubric):
    scores = [_score("a", 5, rubric), _score("b", 5, rubric), _score("c", 2, rubric)]
    summary = scorecard.summarise(scores, rubric)
    assert summary["verdicts"]["EXEMPLARY"] == 2   # 50/50
    assert summary["verdicts"]["DEPRECATE"] == 1   # 20/50
    assert summary["n_skills"] == 3
    assert summary["max_total"] == 50


def test_parse_failure_rate_is_over_dimension_calls(rubric):
    good = _score("a", 5, rubric)
    bad = scorecard.SkillScore(skill="b")
    for d in rubric.dimensions:
        bad.dimensions.append(
            scorecard.DimensionScore(d.key, d.number, d.name, None, parse_failure=True)
        )
    assert scorecard.parse_failure_rate([good, bad]) == 0.5


def test_case_results_are_one_row_per_dimension(rubric):
    from ollama_evals.runner import CaseResult

    rows = scorecard.to_case_results([_score("alpha", 5, rubric)], "m", CaseResult)
    assert len(rows) == 10
    assert {r.category for r in rows} == {f"rubric-d{i}" for i in range(1, 11)}
    assert all(r.case_id == "alpha" for r in rows)


def test_case_result_scores_are_normalised_for_the_compare_gate(rubric):
    from ollama_evals.runner import CaseResult

    rows = scorecard.to_case_results([_score("alpha", 5, rubric)], "m", CaseResult)
    assert all(r.score == 1.0 for r in rows)          # 5 -> 1.0
    assert all(r.metadata["raw_score"] == 5.0 for r in rows)


def test_omitted_dimensions_produce_no_case_result(rubric):
    from ollama_evals.runner import CaseResult

    s = scorecard.SkillScore(skill="a")
    s.dimensions.append(scorecard.DimensionScore("d1", 1, "x", None, parse_failure=True))
    assert scorecard.to_case_results([s], "m", CaseResult) == []


# --- tier interaction ---------------------------------------------------------------


def test_a_tiny_skill_is_not_punished_for_having_no_references(skills_dir: Path, rubric):
    write_tiny(skills_dir)
    result = scorecard.score_skill(
        load_skill(skills_dir / "tiny-shim"), rubric, FakeJudge([Verdict(1.0)] * 10)
    )
    d9 = next(d for d in result.dimensions if d.key == "d9")
    assert d9.source == scorecard.JUDGE  # left to judgement, not forced to 1


def test_a_full_skill_with_no_references_is_forced_to_one(skills_dir: Path, rubric):
    write_skill(skills_dir, "bare", body=CANONICAL_BODY)
    result = scorecard.score_skill(
        load_skill(skills_dir / "bare"), rubric, FakeJudge([Verdict(1.0)] * 10)
    )
    d9 = next(d for d in result.dimensions if d.key == "d9")
    assert d9.score == 1.0 and d9.source == scorecard.STATIC


def test_a_single_reference_file_caps_hygiene_at_three(skills_dir: Path, rubric):
    write_skill(skills_dir, "thin", body=CANONICAL_BODY, references={"conventions.md": filler()})
    result = scorecard.score_skill(
        load_skill(skills_dir / "thin"), rubric, FakeJudge([Verdict(1.0)] * 10)
    )
    d9 = next(d for d in result.dimensions if d.key == "d9")
    assert d9.score == 3.0
