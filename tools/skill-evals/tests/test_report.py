import json
from pathlib import Path

from skill_evals import report
from skill_evals.findings import Finding, FindingSet, Severity
from skill_evals.report import to_json, to_markdown, to_text


def _findings() -> FindingSet:
    return FindingSet([
        Finding("SK042", Severity.ERROR, "references/gone.md does not exist",
                skill="tdd-agent", file=Path("skills/tdd-agent/SKILL.md"), line=103,
                evals_tc="TC1"),
        Finding("SK008", Severity.WARNING, "description has no negative boundary",
                skill="tdd-agent", file=Path("skills/tdd-agent/SKILL.md")),
    ])


def test_text_report_shows_rule_severity_and_location():
    out = to_text(_findings(), total_skills=94)
    assert "SK042" in out
    assert "skills/tdd-agent/SKILL.md:103" in out
    assert "references/gone.md does not exist" in out


def test_text_report_counts_errors_and_warnings():
    assert "94 skills: 1 error(s), 1 warning(s)" in to_text(_findings(), total_skills=94)


def test_text_report_says_clean_when_empty():
    assert "clean" in to_text(FindingSet(), total_skills=94)


def test_text_report_groups_by_rule():
    fs = FindingSet([
        Finding("SK042", Severity.ERROR, "a", skill="x"),
        Finding("SK042", Severity.ERROR, "b", skill="y"),
    ])
    assert to_text(fs).count("SK042 —") == 1


def test_markdown_report_is_a_table():
    md = to_markdown(_findings(), total_skills=94)
    assert md.startswith("# Skill lint")
    assert "| Rule | Severity | Skill | Location | Finding |" in md
    assert "`SK042`" in md


def test_markdown_report_omits_the_table_when_clean():
    md = to_markdown(FindingSet(), total_skills=94)
    assert "| Rule |" not in md
    assert "clean" in md


def test_json_report_is_machine_readable():
    payload = json.loads(to_json(_findings(), total_skills=94))
    assert payload["total_skills"] == 94
    assert payload["errors"] == 1 and payload["warnings"] == 1
    first = payload["findings"][0]
    assert first["rule"] == "SK042"
    assert first["line"] == 103
    assert first["evals_tc"] == "TC1"


def test_json_report_puts_errors_first():
    payload = json.loads(to_json(_findings()))
    assert [f["severity"] for f in payload["findings"]] == ["error", "warning"]


# --- routing report ----------------------------------------------------------------


class _Run:
    manifest = {"roster_size": 91, "roster_withheld": ["grill-me", "grill-with-docs"]}


class _Summary:
    accuracy = 0.88
    top2_accuracy = 0.90
    total = 60
    exact = 53
    missed = 7
    parse_failures = 0
    parse_failure_rate = 0.0


class _Collision:
    expected = "tdd-loop"
    chosen = "tdd-agent"
    count = 3
    total = 6
    rate = 0.5


class _RoutingResult:
    run = _Run()
    summary = _Summary()
    collisions: list = []
    breaches: list = []
    confusion: dict = {}
    roster_sha = "abc123def456789"
    roster_mode = "full"


def test_routing_report_shows_accuracy_and_roster_identity():
    out = report.routing_to_text(_RoutingResult())
    assert "top-1 accuracy:  0.88" in out
    assert "91 skills" in out
    assert "abc123def456" in out


def test_routing_report_notes_withheld_skills():
    out = report.routing_to_text(_RoutingResult())
    assert "withheld:        2 disable-model-invocation skills" in out


def test_routing_report_says_so_when_there_are_no_collisions():
    assert "No description collisions" in report.routing_to_text(_RoutingResult())


def test_routing_report_tabulates_collisions():
    result = _RoutingResult()
    result.collisions = [_Collision()]
    out = report.routing_to_text(result)
    assert "`tdd-loop` | `tdd-agent` | 50%" in out


def test_routing_report_flags_breaches():
    result = _RoutingResult()
    result.breaches = ["grill-me"]
    assert "was auto-selected" in report.routing_to_text(result)


def test_routing_report_marks_parse_failures_as_the_endpoint():
    result = _RoutingResult()
    result.summary = type("S", (_Summary,), {"parse_failures": 4})()
    assert "the endpoint, not the skills" in report.routing_to_text(result)


def test_routing_report_can_include_the_confusion_matrix():
    from collections import Counter

    result = _RoutingResult()
    result.confusion = {"tdd-loop": Counter({"tdd-agent": 2})}
    out = report.routing_to_text(result, show_confusion=True)
    assert "Confusion matrix" in out and "tdd-agent×2" in out


# --- scorecard report ---------------------------------------------------------------


class _Dim:
    def __init__(self, name, score):
        self.name = name
        self.score = score


class _SkillScore:
    def __init__(self, skill, total, verdict, weakest):
        self.skill = skill
        self.total = total
        self.applicable_max = 50  # every dimension applicable, for these fixtures
        self.incomplete = False
        self._verdict = verdict
        self.scored = [_Dim(weakest, 2.0), _Dim("Other", 5.0)]

    def verdict(self, rubric):
        return self._verdict


class _ScorecardResult:
    rubric = None
    scores = [
        _SkillScore("weak-skill", 24, "DEPRECATE", "References Depth"),
        _SkillScore("good-skill", 47, "EXEMPLARY", "Trigger Precision"),
    ]
    summary = {
        "n_skills": 2, "verdicts": {"DEPRECATE": 1, "EXEMPLARY": 1},
        "mean_total": 35.5, "median_total": 35.5, "max_total": 50,
        "parse_failures": 0, "n_dimension_calls": 20,
    }


def test_scorecard_report_shows_totals_and_verdicts():
    out = report.scorecard_to_text(_ScorecardResult())
    assert "mean total:      35.5 / 50" in out
    assert "| DEPRECATE | 1 |" in out
    assert "| EXEMPLARY | 1 |" in out


def test_scorecard_report_ranks_weakest_first():
    out = report.scorecard_to_text(_ScorecardResult())
    assert out.index("weak-skill") < out.index("good-skill")


def test_scorecard_report_names_the_weakest_dimension():
    assert "References Depth (2)" in report.scorecard_to_text(_ScorecardResult())


def test_scorecard_report_honours_a_limit():
    out = report.scorecard_to_text(_ScorecardResult(), limit=1)
    assert "weak-skill" in out and "good-skill" not in out


# --- quality report -----------------------------------------------------------------


class _Row:
    def __init__(self, case_id, score, passed, metadata):
        self.case_id = case_id
        self.score = score
        self.passed = passed
        self.metadata = metadata
        self.category = "quality"


class _QualityResult:
    def __init__(self, rows):
        self._rows = rows

    @property
    def rows(self):
        return self._rows


def test_quality_report_tabulates_structural_checks():
    rows = [_Row("q-tdd-loop", 0.58, False, {
        "structural": {"emitted_state_block": False, "phases_missing": ["RED"],
                       "hallucinated_references": []},
        "per_criterion": [{"criterion": "emits state", "score": 0.0}],
    })]
    out = report.quality_to_text(_QualityResult(rows))
    assert "`q-tdd-loop` | 0.58 | NO | no | RED |" in out


def test_quality_report_names_the_weakest_criterion_per_failure():
    rows = [_Row("q-x", 0.4, False, {
        "structural": {},
        "per_criterion": [{"criterion": "does A", "score": 0.9},
                          {"criterion": "does B", "score": 0.1}],
    })]
    out = report.quality_to_text(_QualityResult(rows))
    assert "does B (0.10)" in out


def test_quality_report_omits_the_weakest_section_when_all_pass():
    rows = [_Row("q-x", 1.0, True, {"structural": {}, "per_criterion": []})]
    out = report.quality_to_text(_QualityResult(rows))
    assert "Weakest criterion" not in out


def test_quality_report_flags_hallucinated_references():
    rows = [_Row("q-x", 0.9, True, {
        "structural": {"emitted_state_block": True, "phases_missing": [],
                       "hallucinated_references": ["references/invented.md"]},
        "per_criterion": [],
    })]
    assert "references/invented.md" in report.quality_to_text(_QualityResult(rows))
