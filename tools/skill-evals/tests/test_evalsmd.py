from pathlib import Path

from skill_evals import evalsmd
from skill_evals.evalsmd import RunRecord
from skill_evals.findings import Finding, FindingSet, Severity

SAMPLE = """\
# Evals

## Test Cases

### Test Case 1: New Skill Completeness

**Input:** a new SKILL.md

**Pass Criteria:**
- [ ] five sections present

- **Last Run:** — | **Result:** —

---

### Test Case 2: Agent Parity

**Pass Criteria:**
- [ ] both runtimes

- **Last Run:** — | **Result:** —

## Taste Rules
"""


def _record(case=1, result="PASS — 0 error(s)"):
    return RunRecord(case, "2026-08-02", "skill-evals lint", result)


def test_fills_the_named_test_case():
    out = evalsmd.update(SAMPLE, [_record(1)])
    assert "- **Last Run:** 2026-08-02 (`skill-evals lint`) | **Result:** PASS — 0 error(s)" in out


def test_leaves_other_test_cases_untouched():
    out = evalsmd.update(SAMPLE, [_record(1)])
    after_tc2 = out.split("### Test Case 2")[1]
    assert "- **Last Run:** — | **Result:** —" in after_tc2


def test_updates_several_cases_at_once():
    out = evalsmd.update(SAMPLE, [_record(1, "PASS"), _record(2, "FAIL")])
    assert out.count("2026-08-02") == 2


def test_is_idempotent():
    once = evalsmd.update(SAMPLE, [_record(1)])
    assert evalsmd.update(once, [_record(1)]) == once


def test_rewriting_replaces_rather_than_appends():
    once = evalsmd.update(SAMPLE, [_record(1, "FAIL — 7 errors")])
    twice = evalsmd.update(once, [_record(1, "PASS — 0 errors")])
    assert "PASS — 0 errors" in twice
    assert "FAIL — 7 errors" not in twice


def test_nothing_else_in_the_document_changes():
    out = evalsmd.update(SAMPLE, [_record(1)])
    for line in ("**Input:** a new SKILL.md", "- [ ] five sections present", "## Taste Rules"):
        assert line in out
    assert len(out.splitlines()) == len(SAMPLE.splitlines())


def test_separate_last_run_and_result_lines_are_both_handled():
    text = (
        "### Test Case 3: Something\n\n"
        "- **Last Run:** —\n"
        "- **Result:** —\n"
    )
    out = evalsmd.update(text, [_record(3, "PASS")])
    assert "- **Last Run:** 2026-08-02 (`skill-evals lint`)" in out
    assert "- **Result:** PASS" in out


def test_a_case_with_no_record_is_left_alone():
    assert evalsmd.update(SAMPLE, []) == SAMPLE


def test_trailing_newline_is_preserved():
    assert evalsmd.update(SAMPLE, [_record(1)]).endswith("\n")


def test_update_file_reports_whether_it_changed(tmp_path: Path):
    path = tmp_path / "evals.md"
    path.write_text(SAMPLE)
    assert evalsmd.update_file(path, [_record(1)]) is True
    assert evalsmd.update_file(path, [_record(1)]) is False  # already current


# --- record builders ---------------------------------------------------------------


def test_lint_record_reports_pass_when_clean():
    record = evalsmd.record_from_lint(FindingSet(), "2026-08-02", total_skills=94)
    assert record.result.startswith("PASS — 0 error(s)")
    assert "94 skills" in record.result


def test_lint_record_reports_fail_with_counts():
    findings = FindingSet([
        Finding("SK042", Severity.ERROR, "x"),
        Finding("SK008", Severity.WARNING, "y"),
    ])
    record = evalsmd.record_from_lint(findings, "2026-08-02")
    assert record.result.startswith("FAIL — 1 error(s), 1 warning(s)")


def test_lint_record_targets_test_case_one():
    assert evalsmd.record_from_lint(FindingSet(), "2026-08-02").test_case == 1


class _Summary:
    accuracy = 0.88
    total = 60
    parse_failures = 0


class _RoutingResult:
    summary = _Summary()
    collisions: list = []
    breaches: list = []


def test_routing_record_summarises_accuracy():
    record = evalsmd.record_from_routing(_RoutingResult(), "2026-08-02")
    assert record.test_case == 10
    assert "top-1 0.88 over 60 cases" in record.result
    assert record.result.startswith("PASS")


def test_routing_record_fails_on_a_breach():
    result = _RoutingResult()
    result.breaches = ["grill-me"]
    assert evalsmd.record_from_routing(result, "2026-08-02").result.startswith("FAIL")


class _ScorecardResult:
    summary = {"verdicts": {"PASS": 10, "REVISE": 2}, "mean_total": 41.5, "max_total": 50}
    deprecate: list = []


def test_scorecard_record_summarises_verdicts():
    record = evalsmd.record_from_scorecard(_ScorecardResult(), "2026-08-02")
    assert record.test_case == 9
    assert "mean 41.5/50" in record.result
    assert "10 PASS" in record.result and "2 REVISE" in record.result


def test_scorecard_record_fails_on_a_deprecate():
    result = _ScorecardResult()
    result.deprecate = ["some-skill"]
    assert evalsmd.record_from_scorecard(result, "2026-08-02").result.startswith("FAIL")
