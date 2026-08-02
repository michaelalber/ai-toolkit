import hashlib
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


class RecordingClient:
    """Captures the messages of every chat() call so prompt assembly can be asserted."""

    def __init__(self, content=""):
        self._content = content
        self.calls = []

    def chat(self, model, messages, **kwargs):
        self.calls.append(messages)
        content = self._content

        class R:
            pass

        R.content = content
        R.tool_calls = []
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


# --- Commit B/C: scorer metadata reaches the artifact; preview length is tunable -----


def test_scorer_metadata_is_preserved_on_case_result():
    """L2's confusion matrix reads metadata['chosen'] — the runner must not drop it."""
    from ollama_evals.scorers.base import register

    @register("_meta_probe")
    def _probe(output, spec, context):
        from ollama_evals.scorers.base import ScoreResult

        return ScoreResult(1.0, True, "ok", metadata={"chosen": "tdd-loop"})

    client = ScriptedClient({"m": {"content": "x"}})
    cases = [Case(id="c", category="routing", prompt="p", scorer={"type": "_meta_probe"})]
    run = run_suite(client, cases, ["m"], run_id="r", created_at="t")
    assert run.results[0].metadata == {"chosen": "tdd-loop"}


def test_output_preview_length_is_overridable():
    client = ScriptedClient({"m": {"content": "z" * 5000}})
    cases = [Case(id="c", category="x", prompt="p", scorer={"type": "contains", "value": "z"})]
    default = run_suite(client, cases, ["m"], run_id="r", created_at="t")
    assert len(default.results[0].output) == 600
    wide = run_suite(
        client, cases, ["m"], output_preview_chars=4000, run_id="r", created_at="t"
    )
    assert len(wide.results[0].output) == 4000


# --- Commit A: system prompt injection and provenance -------------------------------


def test_run_level_system_prompt_is_prepended():
    client = RecordingClient()
    cases = [Case(id="c", category="x", prompt="hi", scorer={"type": "contains", "value": ""})]
    run_suite(client, cases, ["m"], system_prompt="ACT AS X", run_id="r", created_at="t")
    assert client.calls[0][0] == {"role": "system", "content": "ACT AS X"}
    assert client.calls[0][1]["content"] == "hi"


def test_case_system_overrides_run_level_system_prompt():
    client = RecordingClient()
    cases = [
        Case(
            id="c",
            category="x",
            prompt="hi",
            scorer={"type": "contains", "value": ""},
            system="PER-CASE SKILL BODY",
        )
    ]
    run_suite(client, cases, ["m"], system_prompt="RUN LEVEL", run_id="r", created_at="t")
    assert client.calls[0][0] == {"role": "system", "content": "PER-CASE SKILL BODY"}
    assert not any(m["content"] == "RUN LEVEL" for m in client.calls[0])


def test_case_system_survives_jsonl_roundtrip(tmp_path: Path):
    f = tmp_path / "d.jsonl"
    row = {
        "id": "a",
        "category": "quality",
        "prompt": "q",
        "system": "SKILL BODY",
        "scorer": {"type": "contains", "value": "z"},
    }
    f.write_text(json.dumps(row) + "\n")
    assert load_cases(f)[0].system == "SKILL BODY"


def test_case_without_system_defaults_to_none():
    case = Case(id="c", category="x", prompt="p", scorer={"type": "exact", "value": "p"})
    assert case.system is None


def test_manifest_records_system_prompt_identity_not_text():
    client = RecordingClient()
    cases = [Case(id="c", category="x", prompt="hi", scorer={"type": "contains", "value": ""})]
    prompt = "a very long skill body" * 100
    run = run_suite(
        client, cases, ["m"], system_prompt=prompt, suite="quality", run_id="r", created_at="t"
    )
    assert run.manifest["system_prompt_sha256"] == hashlib.sha256(prompt.encode()).hexdigest()
    assert run.manifest["system_prompt_chars"] == len(prompt)
    assert run.manifest["suite"] == "quality"
    # the text itself must never be embedded — it would bloat every artifact
    assert prompt not in json.dumps(run.to_dict())


def test_manifest_system_prompt_fields_are_none_when_unset():
    client = RecordingClient()
    cases = [Case(id="c", category="x", prompt="hi", scorer={"type": "contains", "value": ""})]
    run = run_suite(client, cases, ["m"], run_id="r", created_at="t")
    assert run.manifest["system_prompt_sha256"] is None
    assert run.manifest["system_prompt_chars"] == 0


def test_load_run_accepts_artifact_without_new_manifest_keys(tmp_path: Path):
    """Artifacts saved before Commit A must still load."""
    legacy = {
        "manifest": {"run_id": "old", "models": ["m"]},
        "results": [
            {
                "model": "m",
                "case_id": "c1",
                "category": "coding",
                "score": 1.0,
                "passed": True,
                "detail": "",
                "output": "",
            }
        ],
    }
    path = tmp_path / "old.run.json"
    path.write_text(json.dumps(legacy))
    loaded = load_run(path)
    assert loaded.manifest["run_id"] == "old"
    assert loaded.results[0].metadata == {}


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
