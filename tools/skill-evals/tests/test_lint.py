from pathlib import Path

import pytest
from conftest import CANONICAL_BODY, write_good_full

from skill_evals.findings import Finding, FindingSet, Severity
from skill_evals.lint import dump_baseline, lint, load_baseline
from skill_evals.rules import all_rules, get_rule, rule


def test_every_registered_rule_has_a_summary():
    for r in all_rules():
        assert r.summary.strip(), f"{r.id} has no summary"


def test_every_registered_rule_has_a_known_scope():
    assert {r.scope for r in all_rules()} <= {"skill", "repo"}


def test_rule_ids_are_unique():
    ids = [r.id for r in all_rules()]
    assert len(ids) == len(set(ids))


def test_get_rule_lists_known_ids_on_a_typo():
    with pytest.raises(KeyError) as exc:
        get_rule("SK0042")
    assert "SK042" in str(exc.value)


def test_duplicate_rule_id_is_rejected():
    with pytest.raises(ValueError):
        rule("SK001", severity=Severity.ERROR)(lambda skill, ctx: [])


def test_only_filter_runs_just_that_rule(skills_dir: Path):
    write_good_full(skills_dir, "s", body=CANONICAL_BODY.replace("references/templates.md",
                                                                 "references/gone.md"))
    assert {f.rule_id for f in lint(skills_dir, only=["SK042"])} == {"SK042"}


def test_a_crashing_rule_becomes_a_finding_not_an_abort(skills_dir: Path):
    """One broken rule must not hide the other 30."""
    from skill_evals.corpus import load_skill
    from skill_evals.lint import _run

    write_good_full(skills_dir, "s")

    def boom(skill, ctx):
        raise RuntimeError("rule is broken")

    findings = _run(get_rule("SK042"), boom, load_skill(skills_dir / "s"), None)
    assert "rule crashed" in findings[0].message
    assert findings[0].severity is Severity.ERROR
    assert findings[0].skill == "s"


# --- baselines ---------------------------------------------------------------------


def test_baseline_suppresses_a_known_finding(skills_dir: Path, tmp_path: Path):
    write_good_full(skills_dir, "s", body=CANONICAL_BODY.replace("references/templates.md",
                                                                 "references/gone.md"))
    findings = lint(skills_dir, only=["SK042"])
    assert len(findings) == 1

    baseline = tmp_path / "known.yaml"
    baseline.write_text(dump_baseline(findings, note="accepted at adoption"))
    assert list(lint(skills_dir, only=["SK042"], baseline=baseline)) == []


def test_baseline_does_not_suppress_a_new_finding(skills_dir: Path, tmp_path: Path):
    write_good_full(skills_dir, "known", body=CANONICAL_BODY.replace("references/templates.md",
                                                                     "references/gone.md"))
    baseline = tmp_path / "known.yaml"
    baseline.write_text(dump_baseline(lint(skills_dir, only=["SK042"])))

    write_good_full(skills_dir, "fresh", body=CANONICAL_BODY.replace("references/templates.md",
                                                                     "references/also-gone.md"))
    remaining = lint(skills_dir, only=["SK042"], baseline=baseline).findings
    assert [f.skill for f in remaining] == ["fresh"]


def test_baseline_identity_ignores_line_numbers():
    """An unrelated edit that shifts a finding down must not un-baseline it."""
    a = Finding("SK042", Severity.ERROR, "x missing", skill="s", file=Path("a"), line=10)
    b = Finding("SK042", Severity.ERROR, "x missing", skill="s", file=Path("a"), line=99)
    assert a.key() == b.key()


def test_missing_baseline_file_is_not_an_error(skills_dir: Path, tmp_path: Path):
    write_good_full(skills_dir, "s")
    assert list(lint(skills_dir, baseline=tmp_path / "absent.yaml")) == []


def test_load_baseline_of_none_is_empty():
    assert load_baseline(None) == set()


# --- FindingSet --------------------------------------------------------------------


def test_finding_set_partitions_by_severity():
    fs = FindingSet([
        Finding("A", Severity.ERROR, "e"),
        Finding("B", Severity.WARNING, "w"),
    ])
    assert len(fs.errors) == 1 and len(fs.warnings) == 1


def test_finding_set_sorts_errors_before_warnings():
    fs = FindingSet([
        Finding("Z", Severity.WARNING, "w"),
        Finding("A", Severity.ERROR, "e"),
    ])
    assert [f.rule_id for f in fs.sorted()] == ["A", "Z"]


def test_finding_location_prefers_file_and_line():
    assert Finding("A", Severity.ERROR, "m", file=Path("x.md"), line=7).location == "x.md:7"
    assert Finding("A", Severity.ERROR, "m", skill="s").location == "s"
