import json
from pathlib import Path

from ollama_evals.cases import Case, load_cases
from ollama_evals.runner import load_run, run_suite, save_run


class ScriptedClient:
    """Returns canned content/tool_calls keyed by model name."""

    def __init__(self, by_model):
        self._by_model = by_model

    def chat(self, model, messages, **kwargs):
        spec = self._by_model[model]

        class R:
            content = spec.get("content", "")
            tool_calls = spec.get("tool_calls", [])

        return R()


def _cases():
    return [
        Case(id="c1", category="chat", prompt="2+2?", scorer={"type": "contains", "value": "4"}),
        Case(
            id="c2",
            category="structured",
            prompt="give json",
            scorer={"type": "contains", "value": "ok"},
        ),
    ]


def test_run_suite_scores_each_model_and_case():
    client = ScriptedClient(
        {
            "good": {"content": "4 ok"},  # passes both (c1 exact via trim, c2 contains)
            "bad": {"content": "5 nope"},  # fails both
        }
    )
    cases = [
        Case(id="c1", category="chat", prompt="2+2?", scorer={"type": "contains", "value": "4"}),
        Case(
            id="c2",
            category="structured",
            prompt="j",
            scorer={"type": "contains", "value": "ok"},
        ),
    ]
    run = run_suite(client, cases, models=["good", "bad"], run_id="r1", created_at="t")

    assert len(run.results) == 4  # 2 models x 2 cases
    means = run.overall_means()
    assert means["good"] == 1.0
    assert means["bad"] == 0.0


def test_run_suite_aggregates_by_category():
    client = ScriptedClient({"m": {"content": "4 ok"}})
    run = run_suite(client, _cases(), models=["m"], run_id="r", created_at="t")
    cat = run.category_means()
    assert cat["m"]["chat"] == 1.0
    assert cat["m"]["structured"] == 1.0


def test_run_suite_records_error_without_crashing():
    class Boom:
        def chat(self, **kwargs):
            raise RuntimeError("model offline")

    run = run_suite(Boom(), _cases(), models=["m"], run_id="r", created_at="t")
    assert all(not r.passed for r in run.results)
    assert any("model offline" in r.detail for r in run.results)


def test_tool_use_case_passes_tool_calls_to_scorer():
    call = {"name": "get_weather", "arguments": {"city": "Paris"}}
    client = ScriptedClient({"m": {"content": "", "tool_calls": [call]}})
    cases = [
        Case(
            id="t1",
            category="tool_use",
            prompt="weather in Paris?",
            scorer={"type": "tool_use", "expected": call},
        )
    ]
    run = run_suite(client, cases, models=["m"], run_id="r", created_at="t")
    assert run.results[0].passed


def test_save_and_load_run_roundtrip(tmp_path: Path):
    client = ScriptedClient({"m": {"content": "4 ok"}})
    run = run_suite(client, _cases(), models=["m"], run_id="r1", created_at="t")
    path = save_run(run, tmp_path)
    loaded = load_run(path)
    assert loaded.manifest["run_id"] == "r1"
    assert loaded.overall_means()["m"] == 1.0


def test_load_cases_from_jsonl(tmp_path: Path):
    f = tmp_path / "coding.jsonl"
    line_a = {
        "id": "a",
        "category": "coding",
        "prompt": "x",
        "scorer": {"type": "exact", "value": "1"},
    }
    line_b = {
        "id": "b",
        "category": "coding",
        "messages": [{"role": "user", "content": "y"}],
        "scorer": {"type": "contains", "value": "z"},
    }
    f.write_text(json.dumps(line_a) + "\n\n" + json.dumps(line_b) + "\n")
    cases = load_cases(f)
    assert [c.id for c in cases] == ["a", "b"]
    assert cases[0].messages == [{"role": "user", "content": "x"}]  # prompt -> messages
    assert cases[1].category == "coding"
