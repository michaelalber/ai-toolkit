"""Every shipped dataset must load and reference only registered scorers."""

from pathlib import Path

import pytest

from ollama_evals.calibrate import load_calibration
from ollama_evals.cases import load_cases
from ollama_evals.scorers import get_scorer

DATASETS = Path(__file__).resolve().parent.parent / "datasets"
VENDORED = ["bfcl_irrelevance.jsonl", "ifeval.jsonl"]


@pytest.mark.parametrize("output", ["", "Hello, world.\n\n* a\n***\n\"quoted\" P.S. done"])
def test_every_ifeval_case_scores_without_error(output):
    from ollama_evals.scorers import score_output

    for case in load_cases(DATASETS / "ifeval.jsonl"):
        result = score_output(output, case.scorer, {})
        assert 0.0 <= result.score <= 1.0
CASE_FILES = ["coding.jsonl", "chat.jsonl", "tool_use.jsonl", "structured.jsonl", *VENDORED]


@pytest.mark.parametrize("name", VENDORED)
def test_vendored_cases_carry_attribution(name):
    import json

    for line in (DATASETS / name).read_text().splitlines():
        source = json.loads(line)["source"]
        assert source["license"] == "Apache-2.0"
        assert len(source["commit"]) == 40  # pinned to an upstream commit, not a branch
        assert source["dataset"] and source["upstream_id"] is not None


def test_every_dataset_file_is_a_cli_suite():
    from ollama_evals.cli import SUITES

    assert {n.removesuffix(".jsonl") for n in CASE_FILES} == set(SUITES)


@pytest.mark.parametrize("name", CASE_FILES)
def test_dataset_loads_with_registered_scorers(name):
    cases = load_cases(DATASETS / name)
    assert cases, f"{name} is empty"
    for case in cases:
        assert case.id
        get_scorer(case.scorer["type"])  # raises KeyError if unregistered


def test_case_ids_are_unique_across_datasets():
    seen = set()
    for name in CASE_FILES:
        for case in load_cases(DATASETS / name):
            assert case.id not in seen, f"duplicate case id: {case.id}"
            seen.add(case.id)


def test_calibration_set_loads_and_is_balanced():
    examples = load_calibration(DATASETS / "judge-calibration.jsonl")
    assert len(examples) >= 30
    goods = sum(1 for e in examples if e.human_score >= 0.7)
    assert 0.4 <= goods / len(examples) <= 0.6  # a lopsided set rewards an always-pass judge


def test_calibration_covers_every_judged_case_with_its_real_rubric():
    """Calibration must test the prompt and criteria the judge actually grades, with at
    least two passes and two fails for each judged case."""
    import json

    judged = {c.id: c for c in load_cases(DATASETS / "chat.jsonl") if c.scorer["type"] == "judge"}
    rows = [json.loads(x) for x in (DATASETS / "judge-calibration.jsonl").read_text().splitlines()]
    for case_id, case in judged.items():
        mine = [r for r in rows if r["case"] == case_id]
        assert all(r["prompt"] == case.user_prompt for r in mine), case_id
        assert all(r["criteria"] == case.scorer["criteria"] for r in mine), case_id
        assert sum(r["human_score"] >= 0.7 for r in mine) >= 2, case_id
        assert sum(r["human_score"] < 0.7 for r in mine) >= 2, case_id
    assert {r["case"] for r in rows} <= judged.keys()
    assert all(r.get("rationale") for r in rows)  # every label says why, for review
