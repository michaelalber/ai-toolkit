from pathlib import Path

import pytest
from conftest import CANONICAL_BODY, write_good_full

from skill_evals import quality
from skill_evals.corpus import load_skill

pytest.importorskip("ollama_evals", reason="LLM layer needs the llm extra")

from ollama_evals.scorers import score_output  # noqa: E402

import skill_evals.scorers  # noqa: E402,F401  (registers skill_rubric)

# --- the system prompt is the skill body, frontmatter stripped ---------------------


def test_system_prompt_is_the_body_without_frontmatter(skills_dir: Path):
    write_good_full(skills_dir, "alpha")
    prompt = quality.system_prompt(load_skill(skills_dir / "alpha"))
    assert prompt.startswith("# alpha") or prompt.startswith("# Good Full")
    assert "audience: team" not in prompt
    assert "## Workflow" in prompt


# --- derive_criteria: from the skill's own words ----------------------------------


def test_constraints_are_derived_from_the_skill(skills_dir: Path):
    write_good_full(skills_dir, "alpha")
    derived = quality.derive_criteria(load_skill(skills_dir / "alpha"))
    assert derived.constraints == ["FIRST", "SECOND", "THIRD"]


def test_constraint_rationale_after_a_dash_is_trimmed(skills_dir: Path):
    body = CANONICAL_BODY.replace(
        "1. FIRST — do the first thing.",
        "1. SEMVER — breaking changes require a major bump; verify with cargo semver-checks.",
    )
    write_good_full(skills_dir, "alpha", body=body)
    assert quality.derive_criteria(load_skill(skills_dir / "alpha")).constraints[0] == "SEMVER"


def test_workflow_phases_are_derived(skills_dir: Path):
    write_good_full(skills_dir, "alpha")
    derived = quality.derive_criteria(load_skill(skills_dir / "alpha"))
    assert derived.phases == ["DETECT", "ACT", "VERIFY"]


def test_state_fields_are_derived(skills_dir: Path):
    write_good_full(skills_dir, "alpha")
    derived = quality.derive_criteria(load_skill(skills_dir / "alpha"))
    assert derived.state_fields == ["phase", "last_action", "next_action"]


def test_exit_criteria_are_derived(skills_dir: Path):
    write_good_full(skills_dir, "alpha")
    derived = quality.derive_criteria(load_skill(skills_dir / "alpha"))
    assert derived.exit_criteria == "the thing is done and proven"


def test_criteria_render_as_checkable_statements(skills_dir: Path):
    write_good_full(skills_dir, "alpha")
    rendered = quality.derive_criteria(load_skill(skills_dir / "alpha")).as_list()
    assert any("state block" in c for c in rendered)
    assert any("DETECT -> ACT -> VERIFY" in c for c in rendered)
    assert any("FIRST" in c for c in rendered)
    assert any("exit criteria" in c for c in rendered)


def test_a_skill_with_no_state_block_derives_no_state_criteria(skills_dir: Path):
    body = CANONICAL_BODY.replace("<good-full-state>", "").replace("</good-full-state>", "")
    write_good_full(skills_dir, "alpha", body=body)
    assert quality.derive_criteria(load_skill(skills_dir / "alpha")).state_fields == []


# --- the skill_rubric scorer -------------------------------------------------------


class Verdict:
    def __init__(self, score, parsed=True, reasoning="ok"):
        self.score = score
        self.parsed = parsed
        self.reasoning = reasoning


class SequenceJudge:
    def __init__(self, verdicts):
        self._verdicts = list(verdicts)
        self.seen = []

    def score(self, *, criteria, prompt, output, reference=None):
        self.seen.append(criteria)
        return self._verdicts.pop(0) if self._verdicts else Verdict(1.0)


SPEC = {"type": "skill_rubric", "criteria": ["does A", "does B", "does C"], "threshold": 0.7}


def test_one_judge_call_per_criterion():
    judge = SequenceJudge([Verdict(1.0)] * 3)
    score_output("out", SPEC, {"judge": judge})
    assert judge.seen == ["does A", "does B", "does C"]


def test_score_is_the_mean_across_criteria():
    judge = SequenceJudge([Verdict(1.0), Verdict(1.0), Verdict(0.25)])
    r = score_output("out", SPEC, {"judge": judge})
    assert r.score == pytest.approx(0.75)
    assert r.passed


def test_below_threshold_does_not_pass():
    judge = SequenceJudge([Verdict(0.5), Verdict(0.5), Verdict(0.5)])
    assert not score_output("out", SPEC, {"judge": judge}).passed


def test_the_weakest_criterion_is_named():
    judge = SequenceJudge([Verdict(1.0), Verdict(0.0), Verdict(1.0)])
    assert "does B" in score_output("out", SPEC, {"judge": judge}).detail


def test_per_criterion_scores_are_kept():
    judge = SequenceJudge([Verdict(1.0), Verdict(0.5), Verdict(0.0)])
    meta = score_output("out", SPEC, {"judge": judge}).metadata
    assert [c["score"] for c in meta["per_criterion"]] == [1.0, 0.5, 0.0]


def test_an_unparseable_criterion_is_skipped_not_scored_zero():
    judge = SequenceJudge([Verdict(1.0), Verdict(0.0, parsed=False), Verdict(1.0)])
    r = score_output("out", SPEC, {"judge": judge})
    assert r.score == 1.0  # the mean of the two that parsed
    assert r.metadata["n_parse_failures"] == 1


def test_all_criteria_unparseable_is_flagged_as_a_judge_failure():
    judge = SequenceJudge([Verdict(0.0, parsed=False)] * 3)
    r = score_output("out", SPEC, {"judge": judge})
    assert r.metadata["parse_failure"] is True
    assert not r.passed


def test_missing_judge_raises():
    with pytest.raises(RuntimeError, match="no judge"):
        score_output("out", SPEC, {})


def test_empty_criteria_raises():
    with pytest.raises(ValueError, match="criteria"):
        score_output("out", {"type": "skill_rubric", "criteria": []}, {"judge": SequenceJudge([])})


# --- the deterministic structural sub-score ----------------------------------------


def _spec(**kw):
    return {"type": "skill_rubric", "criteria": ["c"], **kw}


def test_structural_detects_the_state_block():
    judge = SequenceJudge([Verdict(1.0)])
    out = "Working...\n<alpha-state>\nphase: DETECT\n</alpha-state>"
    meta = score_output(out, _spec(state_tag="alpha-state"), {"judge": judge}).metadata
    assert meta["structural"]["emitted_state_block"] is True


def test_structural_notices_a_missing_state_block():
    judge = SequenceJudge([Verdict(1.0)])
    meta = score_output("no block", _spec(state_tag="alpha-state"), {"judge": judge}).metadata
    assert meta["structural"]["emitted_state_block"] is False


def test_structural_tracks_which_phases_were_named():
    judge = SequenceJudge([Verdict(1.0)])
    meta = score_output(
        "DETECT then ACT", _spec(phases=["DETECT", "ACT", "VERIFY"]), {"judge": judge}
    ).metadata
    assert meta["structural"]["phases_named"] == ["DETECT", "ACT"]
    assert meta["structural"]["phases_missing"] == ["VERIFY"]


def test_structural_flags_a_hallucinated_reference():
    judge = SequenceJudge([Verdict(1.0)])
    out = "See references/conventions.md and references/invented.md."
    meta = score_output(
        out, _spec(known_references=["references/conventions.md"]), {"judge": judge}
    ).metadata
    assert meta["structural"]["hallucinated_references"] == ["references/invented.md"]


def test_structural_is_reported_beside_the_score_not_averaged_in():
    """Measured facts and judged opinions must not be mixed into one number."""
    judge = SequenceJudge([Verdict(1.0)])
    r = score_output("nothing structural here", _spec(state_tag="alpha-state"), {"judge": judge})
    assert r.score == 1.0  # unaffected by the failed structural check
    assert r.metadata["structural"]["emitted_state_block"] is False
