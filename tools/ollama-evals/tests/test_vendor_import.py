"""Converters that turn pinned upstream datasets into ollama-evals cases."""

import json

from ollama_evals.cases import Case
from ollama_evals.vendor_import import bfcl_case, ifeval_case, main, sample

BFCL_ROW = {
    "id": "irrelevance_1",
    "question": [[{"role": "user", "content": "Solve x^2 + 2x + 3 = 0."}]],
    "function": [{"name": "math.sum", "description": "Sum a list.", "parameters": {
        "type": "dict",
        "properties": {
            "numbers": {"type": "array", "items": {"type": "float"}, "description": "Numbers."},
            "pair": {"type": "tuple", "items": {"type": "integer"}},
            "anything": {"type": "any"},
        },
        "required": ["numbers"],
    }}],
}


def test_bfcl_case_expects_no_call_and_keeps_the_question():
    case = bfcl_case(BFCL_ROW, "abc123")
    assert case["id"] == "bfcl-irrelevance_1"
    assert case["messages"] == [{"role": "user", "content": "Solve x^2 + 2x + 3 = 0."}]
    assert case["scorer"] == {"type": "tool_use", "expected": {"no_call": True}}
    assert case["source"] == {"dataset": "gorilla-llm/Berkeley-Function-Calling-Leaderboard",
                              "file": "BFCL_v3_irrelevance.json", "commit": "abc123",
                              "license": "Apache-2.0", "upstream_id": "irrelevance_1"}
    Case.from_dict(case)  # loads as a normal case


def test_bfcl_tools_become_json_schema_with_safe_names():
    fn = bfcl_case(BFCL_ROW, "c")["tools"][0]["function"]
    assert fn["name"] == "math_sum"  # dots are not valid in OpenAI-style tool names
    params = fn["parameters"]
    assert params["type"] == "object"
    assert params["properties"]["numbers"]["items"] == {"type": "number"}
    assert params["properties"]["pair"]["type"] == "array"
    assert "type" not in params["properties"]["anything"]
    assert params["required"] == ["numbers"]
    assert BFCL_ROW["function"][0]["parameters"]["type"] == "dict"  # input not mutated


IFEVAL_ROW = {
    "key": 1001,
    "prompt": "Write a haiku. Do not use commas.",
    "instruction_id_list": ["punctuation:no_comma", "startend:end_checker"],
    "kwargs": [{}, {"end_phrase": "Peace.", "num_words": None}],
}


def test_ifeval_case_keeps_instructions_and_drops_empty_kwargs():
    case = ifeval_case(IFEVAL_ROW, "def456")
    assert case["id"] == "ifeval-1001"
    assert case["prompt"] == "Write a haiku. Do not use commas."
    assert case["scorer"] == {"type": "ifeval", "instructions": [
        {"id": "punctuation:no_comma", "kwargs": {}},
        {"id": "startend:end_checker", "kwargs": {"end_phrase": "Peace."}},
    ]}
    assert case["source"]["commit"] == "def456"
    Case.from_dict(case)


def test_ifeval_case_with_an_unsupported_instruction_is_skipped():
    row = {**IFEVAL_ROW, "instruction_id_list": ["language:response_language"],
           "kwargs": [{"language": "fr"}]}
    assert ifeval_case(row, "c") is None


def test_sample_is_deterministic_and_keeps_source_order():
    rows = list(range(100))
    picked = sample(rows, 10, seed=7)
    assert picked == sample(rows, 10, seed=7)
    assert picked == sorted(picked) and len(picked) == 10
    assert sample(rows, 500, seed=7) == rows


def test_main_writes_jsonl(tmp_path):
    src = tmp_path / "in.json"
    rows = [BFCL_ROW, {**BFCL_ROW, "id": "irrelevance_2"}]
    src.write_text("".join(json.dumps(r) + "\n" for r in rows))
    out = tmp_path / "out.jsonl"
    main(["bfcl", str(src), str(out), "--commit", "abc", "--limit", "1"])
    lines = out.read_text().splitlines()
    assert len(lines) == 1 and json.loads(lines[0])["source"]["commit"] == "abc"


def test_main_excludes_reviewed_out_upstream_ids_after_sampling(tmp_path):
    src = tmp_path / "in.json"
    rows = [{**BFCL_ROW, "id": f"irrelevance_{i}"} for i in range(3)]
    src.write_text("".join(json.dumps(r) + "\n" for r in rows))
    out = tmp_path / "out.jsonl"
    excluded = "irrelevance_0,irrelevance_2"
    main(["bfcl", str(src), str(out), "--commit", "abc", "--exclude", excluded])
    assert [json.loads(x)["id"] for x in out.read_text().splitlines()] == ["bfcl-irrelevance_1"]
