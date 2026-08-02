import pytest

from skill_evals import route

pytest.importorskip("ollama_evals", reason="LLM layer needs the llm extra")

from ollama_evals.runner import CaseResult  # noqa: E402
from ollama_evals.scorers import score_output  # noqa: E402

import skill_evals.scorers  # noqa: E402,F401  (registers skill_choice)

SPEC = {"type": "skill_choice", "expected": "tdd-loop", "acceptable": ["tdd-loop"]}


def _score(reply, spec=None):
    return score_output(reply, spec or SPEC, {})


# --- the skill_choice truth table --------------------------------------------------


def test_exact_choice_scores_one():
    r = _score('{"skill": "tdd-loop", "runner_up": "tdd-agent"}')
    assert r.score == 1.0 and r.passed
    assert r.metadata["chosen"] == "tdd-loop"


def test_runner_up_hit_scores_half_and_does_not_pass():
    r = _score('{"skill": "tdd-agent", "runner_up": "tdd-loop"}')
    assert r.score == 0.5
    assert not r.passed  # second on a 94-way choice is not success
    assert "runner-up" in r.detail


def test_a_miss_scores_zero():
    r = _score('{"skill": "para-file", "runner_up": "para-review"}')
    assert r.score == 0.0 and not r.passed
    assert r.metadata["chosen"] == "para-file"


def test_any_acceptable_name_counts_as_exact():
    spec = {"type": "skill_choice", "expected": "tdd-loop",
            "acceptable": ["tdd-loop", "tdd-agent"]}
    assert _score('{"skill": "tdd-agent"}', spec).score == 1.0


def test_expected_none_rewards_declining():
    spec = {"type": "skill_choice", "expected": None}
    assert _score('{"skill": "none"}', spec).score == 1.0


def test_expected_none_penalises_firing():
    spec = {"type": "skill_choice", "expected": None}
    r = _score('{"skill": "para-file"}', spec)
    assert r.score == 0.0
    assert "when no skill should" in r.detail


def test_reply_is_normalised_for_case_and_backticks():
    assert _score('{"skill": "`TDD-Loop`"}').score == 1.0


def test_missing_runner_up_is_treated_as_none():
    r = _score('{"skill": "para-file"}')
    assert r.metadata["runner_up"] == "none"


def test_prose_around_the_json_is_tolerated():
    assert _score('Sure! {"skill": "tdd-loop"} — that one.').score == 1.0


# --- parse failure is NOT a routing failure ----------------------------------------


def test_unparseable_reply_is_flagged_separately():
    r = _score("I think you want the TDD one")
    assert r.score == 0.0
    assert r.metadata["parse_failure"] is True
    assert r.metadata["chosen"] is None


def test_a_genuine_miss_is_not_flagged_as_a_parse_failure():
    r = _score('{"skill": "para-file"}')
    assert "parse_failure" not in r.metadata


# --- aggregation -------------------------------------------------------------------


def _result(case_id, score, meta, category="routing"):
    return CaseResult("m", case_id, category, score, score >= 1.0, metadata=meta)


def test_summary_partitions_exact_runner_up_and_miss():
    results = [
        _result("a", 1.0, {"expected": "x", "chosen": "x"}),
        _result("b", 0.5, {"expected": "x", "chosen": "y", "runner_up": "x"}),
        _result("c", 0.0, {"expected": "x", "chosen": "z"}),
    ]
    s = route.summarise(results)
    assert (s.exact, s.runner_up, s.missed, s.total) == (1, 1, 1, 3)


def test_accuracy_excludes_parse_failures_from_the_denominator():
    """A broken endpoint must not read as poor skill descriptions."""
    results = [
        _result("a", 1.0, {"expected": "x", "chosen": "x"}),
        _result("b", 0.0, {"parse_failure": True, "expected": "x", "chosen": None}),
    ]
    s = route.summarise(results)
    assert s.accuracy == 1.0  # 1 of 1 scoreable, not 1 of 2
    assert s.parse_failures == 1
    assert s.parse_failure_rate == 0.5


def test_top2_accuracy_counts_runner_up_hits():
    results = [
        _result("a", 1.0, {"expected": "x", "chosen": "x"}),
        _result("b", 0.5, {"expected": "x", "chosen": "y", "runner_up": "x"}),
    ]
    s = route.summarise(results)
    assert s.accuracy == 0.5 and s.top2_accuracy == 1.0


def test_summary_of_nothing_is_zero_not_a_crash():
    s = route.summarise([])
    assert s.accuracy == 0.0 and s.parse_failure_rate == 0.0


def test_non_routing_results_are_ignored():
    results = [_result("a", 1.0, {"expected": "x", "chosen": "x"}, category="quality")]
    assert route.summarise(results).total == 0


def test_confusion_matrix_counts_expected_by_chosen():
    results = [
        _result("a", 0.0, {"expected": "tdd-loop", "chosen": "tdd-agent"}),
        _result("b", 0.0, {"expected": "tdd-loop", "chosen": "tdd-agent"}),
        _result("c", 1.0, {"expected": "tdd-loop", "chosen": "tdd-loop"}),
    ]
    matrix = route.confusion_matrix(results)
    assert matrix["tdd-loop"]["tdd-agent"] == 2
    assert matrix["tdd-loop"]["tdd-loop"] == 1


def test_confusion_matrix_skips_parse_failures():
    results = [_result("a", 0.0, {"parse_failure": True, "expected": "x", "chosen": None})]
    assert route.confusion_matrix(results) == {}


def test_collisions_report_pairs_over_the_threshold():
    results = [
        _result("a", 0.0, {"expected": "tdd-loop", "chosen": "tdd-agent"}),
        _result("b", 0.0, {"expected": "tdd-loop", "chosen": "tdd-agent"}),
        _result("c", 1.0, {"expected": "tdd-loop", "chosen": "tdd-loop"}),
        _result("d", 1.0, {"expected": "tdd-loop", "chosen": "tdd-loop"}),
    ]
    found = route.collisions(results, threshold=0.2)
    assert len(found) == 1
    assert (found[0].expected, found[0].chosen) == ("tdd-loop", "tdd-agent")
    assert found[0].rate == 0.5


def test_collisions_ignore_pairs_below_the_threshold():
    results = [_result(str(i), 1.0, {"expected": "x", "chosen": "x"}) for i in range(9)]
    results.append(_result("bad", 0.0, {"expected": "x", "chosen": "y"}))
    assert route.collisions(results, threshold=0.2) == []


def test_collisions_never_report_a_correct_choice():
    results = [_result("a", 1.0, {"expected": "x", "chosen": "x"})]
    assert route.collisions(results) == []


def test_collisions_are_sorted_by_rate():
    results = [
        _result("a", 0.0, {"expected": "p", "chosen": "q"}),   # 1/1 = 1.0
        _result("b", 0.0, {"expected": "x", "chosen": "y"}),   # 1/2 = 0.5
        _result("c", 1.0, {"expected": "x", "chosen": "x"}),
    ]
    found = route.collisions(results)
    assert [c.expected for c in found] == ["p", "x"]


def test_never_auto_selected_reports_a_breach():
    """disable-model-invocation skills must never be chosen."""
    results = [_result("a", 0.0, {"expected": None, "chosen": "grill-me"})]
    assert route.never_auto_selected(results, ["grill-me", "grilling"]) == ["grill-me"]


def test_never_auto_selected_is_empty_when_respected():
    results = [_result("a", 1.0, {"expected": None, "chosen": "none"})]
    assert route.never_auto_selected(results, ["grill-me"]) == []
