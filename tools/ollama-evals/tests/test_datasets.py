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
    assert len(examples) >= 4
    goods = sum(1 for e in examples if e.human_score >= 0.5)
    bads = len(examples) - goods
    assert goods and bads  # need both classes to measure agreement meaningfully
