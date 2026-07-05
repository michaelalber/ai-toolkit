import pytest

from ollama_evals.scorers import get_scorer, score_output


def test_exact_match_trims_whitespace():
    r = score_output("  42\n", {"type": "exact", "value": "42"})
    assert r.passed and r.score == 1.0


def test_exact_mismatch_fails():
    r = score_output("43", {"type": "exact", "value": "42"})
    assert not r.passed and r.score == 0.0


def test_exact_case_sensitive_option():
    assert score_output("YES", {"type": "exact", "value": "yes"}).passed  # default: insensitive
    assert not score_output(
        "YES", {"type": "exact", "value": "yes", "case_sensitive": True}
    ).passed


def test_contains_single_value():
    assert score_output("def is_prime(n):", {"type": "contains", "value": "is_prime"}).passed
    assert not score_output("nope", {"type": "contains", "value": "is_prime"}).passed


def test_contains_all_of_list():
    spec = {"type": "contains", "all": ["import", "return"]}
    assert score_output("import x\nreturn 1", spec).passed
    r = score_output("import x", spec)
    assert not r.passed and 0.0 <= r.score < 1.0  # partial credit


def test_regex_match():
    assert score_output("result: 200 OK", {"type": "regex", "pattern": r"\b2\d\d\b"}).passed
    assert not score_output("nope", {"type": "regex", "pattern": r"\b2\d\d\b"}).passed


def test_json_schema_valid():
    spec = {
        "type": "json_schema",
        "schema": {
            "type": "object",
            "required": ["name", "age"],
            "properties": {"name": {"type": "string"}, "age": {"type": "integer"}},
        },
    }
    assert score_output('{"name": "Ada", "age": 36}', spec).passed


def test_json_schema_extracts_from_code_fence():
    spec = {"type": "json_schema", "schema": {"type": "object", "required": ["ok"]}}
    fenced = 'Here you go:\n```json\n{"ok": true}\n```\n'
    assert score_output(fenced, spec).passed


def test_json_schema_invalid_fails_with_detail():
    spec = {
        "type": "json_schema",
        "schema": {
            "type": "object",
            "required": ["age"],
            "properties": {"age": {"type": "integer"}},
        },
    }
    r = score_output('{"age": "not a number"}', spec)
    assert not r.passed and r.detail


def test_json_schema_malformed_json_fails():
    spec = {"type": "json_schema", "schema": {"type": "object"}}
    r = score_output("{not json", spec)
    assert not r.passed


def test_unknown_scorer_type_raises():
    with pytest.raises(KeyError):
        get_scorer("does-not-exist")
