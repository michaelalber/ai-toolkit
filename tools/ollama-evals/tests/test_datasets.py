"""Every shipped dataset must load and reference only registered scorers."""

from pathlib import Path

import pytest

from ollama_evals.calibrate import load_calibration
from ollama_evals.cases import load_cases
from ollama_evals.scorers import get_scorer

DATASETS = Path(__file__).resolve().parent.parent / "datasets"
CASE_FILES = ["coding.jsonl", "chat.jsonl", "tool_use.jsonl", "structured.jsonl"]


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
