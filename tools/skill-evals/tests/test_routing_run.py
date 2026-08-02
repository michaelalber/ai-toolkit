import json
from pathlib import Path

import pytest
from conftest import write_good_full

pytest.importorskip("ollama_evals", reason="LLM layer needs the llm extra")

from skill_evals import routing_run  # noqa: E402
from skill_evals.corpus import discover  # noqa: E402

DATASETS = Path(__file__).resolve().parents[1] / "datasets"


class ScriptedClient:
    """Replies with a chosen skill per case id; records the messages it was sent."""

    def __init__(self, by_case=None, default='{"skill": "none"}'):
        self._by_case = by_case or {}
        self._default = default
        self.sent = []

    def chat(self, model, messages, **kwargs):
        self.sent.append(messages)
        user = next(m["content"] for m in reversed(messages) if m["role"] == "user")
        content = self._by_case.get(user, self._default)

        class R:
            pass

        R.content = content
        R.tool_calls = []
        return R()


class Cfg:
    base_url = "http://unused"
    models = ["fake"]
    temperature = 0.0
    seed = 7
    num_ctx = 32768


def _corpus(skills_dir: Path, names):
    for name in names:
        write_good_full(
            skills_dir, name,
            frontmatter={"name": name, "audience": "team",
                         "description": f"Handles {name}. Use when {name}. Not for others."},
        )
    return discover(skills_dir)


def _dataset(tmp_path: Path, rows) -> Path:
    path = tmp_path / "routing.jsonl"
    path.write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    return path


def _run(skills_dir, dataset, client, **kw):
    return routing_run.execute(
        skills_dir=skills_dir, dataset=dataset, models=["fake"],
        client=client, config_path=None, **kw,
    )


@pytest.fixture(autouse=True)
def _stub_config(monkeypatch):
    monkeypatch.setattr(routing_run, "_config", lambda *a, **k: Cfg())


# --- prompt assembly ---------------------------------------------------------------


def test_each_case_receives_the_roster_as_its_system_prompt(skills_dir: Path, tmp_path: Path):
    _corpus(skills_dir, ["alpha", "beta"])
    ds = _dataset(tmp_path, [{"id": "c1", "category": "routing", "prompt": "do alpha",
                              "scorer": {"type": "skill_choice", "expected": "alpha"}}])
    client = ScriptedClient({"do alpha": '{"skill": "alpha"}'})
    _run(skills_dir, ds, client)

    system = client.sent[0][0]
    assert system["role"] == "system"
    assert "- alpha:" in system["content"] and "- beta:" in system["content"]
    assert '"runner_up"' in system["content"]


def test_manifest_records_the_roster_identity(skills_dir: Path, tmp_path: Path):
    skills = _corpus(skills_dir, ["alpha", "beta"])
    ds = _dataset(tmp_path, [{"id": "c1", "category": "routing", "prompt": "x",
                              "scorer": {"type": "skill_choice", "expected": "alpha"}}])
    result = _run(skills_dir, ds, ScriptedClient())

    from skill_evals import roster as roster_mod
    assert result.run.manifest["roster_sha256"] == roster_mod.build(skills).sha256
    assert result.run.manifest["roster_size"] == 2
    assert result.run.manifest["suite"] == "routing"


def test_shard_mode_still_shows_the_model_the_expected_skill(skills_dir: Path, tmp_path: Path):
    _corpus(skills_dir, [f"skill-{i}" for i in range(9)])
    ds = _dataset(tmp_path, [{"id": "c1", "category": "routing", "prompt": "x",
                              "scorer": {"type": "skill_choice", "expected": "skill-7"}}])
    client = ScriptedClient()
    _run(skills_dir, ds, client, roster_mode="shard", shards=3)
    assert "- skill-7:" in client.sent[0][0]["content"]


def test_shard_mode_sends_a_smaller_roster(skills_dir: Path, tmp_path: Path):
    _corpus(skills_dir, [f"skill-{i}" for i in range(9)])
    ds = _dataset(tmp_path, [{"id": "c1", "category": "routing", "prompt": "x",
                              "scorer": {"type": "skill_choice", "expected": "skill-7"}}])
    client = ScriptedClient()
    _run(skills_dir, ds, client, roster_mode="shard", shards=3)
    assert client.sent[0][0]["content"].count("\n- ") < 9


# --- results ------------------------------------------------------------------------


def test_summary_and_collisions_are_computed(skills_dir: Path, tmp_path: Path):
    _corpus(skills_dir, ["tdd-loop", "tdd-agent"])
    rows = [
        {"id": f"c{i}", "category": "routing", "prompt": f"tdd request {i}",
         "scorer": {"type": "skill_choice", "expected": "tdd-loop"}}
        for i in range(4)
    ]
    ds = _dataset(tmp_path, rows)
    client = ScriptedClient({
        "tdd request 0": '{"skill": "tdd-agent"}',
        "tdd request 1": '{"skill": "tdd-agent"}',
        "tdd request 2": '{"skill": "tdd-loop"}',
        "tdd request 3": '{"skill": "tdd-loop"}',
    })
    result = _run(skills_dir, ds, client)

    assert result.summary.accuracy == 0.5
    assert len(result.collisions) == 1
    assert (result.collisions[0].expected, result.collisions[0].chosen) == ("tdd-loop",
                                                                            "tdd-agent")


def test_a_disable_model_invocation_breach_is_reported(skills_dir: Path, tmp_path: Path):
    _corpus(skills_dir, ["alpha"])
    write_good_full(
        skills_dir, "grill-me",
        frontmatter={"name": "grill-me", "audience": "team", "disable-model-invocation": "true",
                     "description": "Interviews you. Use when grilling. Not for building."},
    )
    ds = _dataset(tmp_path, [{"id": "c1", "category": "routing", "prompt": "think it through",
                              "scorer": {"type": "skill_choice", "expected": None}}])
    result = _run(skills_dir, ds, ScriptedClient(default='{"skill": "grill-me"}'))
    assert result.breaches == ["grill-me"]


def test_no_breach_when_the_model_declines(skills_dir: Path, tmp_path: Path):
    _corpus(skills_dir, ["alpha"])
    write_good_full(
        skills_dir, "grill-me",
        frontmatter={"name": "grill-me", "audience": "team", "disable-model-invocation": "true",
                     "description": "Interviews you. Use when grilling. Not for building."},
    )
    ds = _dataset(tmp_path, [{"id": "c1", "category": "routing", "prompt": "x",
                              "scorer": {"type": "skill_choice", "expected": None}}])
    assert _run(skills_dir, ds, ScriptedClient()).breaches == []


def test_parse_failures_are_counted_not_scored_as_misses(skills_dir: Path, tmp_path: Path):
    _corpus(skills_dir, ["alpha"])
    ds = _dataset(tmp_path, [{"id": "c1", "category": "routing", "prompt": "x",
                              "scorer": {"type": "skill_choice", "expected": "alpha"}}])
    result = _run(skills_dir, ds, ScriptedClient(default="I'd use the alpha skill"))
    assert result.summary.parse_failures == 1
    assert result.summary.missed == 0


def test_artifact_is_written_when_an_out_dir_is_given(skills_dir: Path, tmp_path: Path):
    _corpus(skills_dir, ["alpha"])
    ds = _dataset(tmp_path, [{"id": "c1", "category": "routing", "prompt": "x",
                              "scorer": {"type": "skill_choice", "expected": "alpha"}}])
    out = tmp_path / "runs"
    result = _run(skills_dir, ds, ScriptedClient(), out_dir=out)
    assert result.artifact.exists()
    assert json.loads(result.artifact.read_text())["manifest"]["roster_mode"] == "full"


# --- setup errors --------------------------------------------------------------------


def test_missing_dataset_is_a_setup_error(skills_dir: Path, tmp_path: Path):
    _corpus(skills_dir, ["alpha"])
    with pytest.raises(routing_run.RoutingSetupError, match="no routing dataset"):
        _run(skills_dir, tmp_path / "absent.jsonl", ScriptedClient())


def test_empty_dataset_is_a_setup_error(skills_dir: Path, tmp_path: Path):
    _corpus(skills_dir, ["alpha"])
    empty = tmp_path / "empty.jsonl"
    empty.write_text("\n")
    with pytest.raises(routing_run.RoutingSetupError, match="no cases"):
        _run(skills_dir, empty, ScriptedClient())


def test_an_unregistered_scorer_is_a_setup_error_not_a_zero_score(skills_dir: Path,
                                                                  tmp_path: Path):
    """The runner records a per-case crash as 0.0, so this would otherwise read as
    'the model got everything wrong' rather than 'that scorer does not exist'."""
    _corpus(skills_dir, ["alpha"])
    ds = _dataset(tmp_path, [{"id": "c1", "category": "routing", "prompt": "x",
                              "scorer": {"type": "skill_choise", "expected": "alpha"}}])
    with pytest.raises(routing_run.RoutingSetupError) as exc:
        _run(skills_dir, ds, ScriptedClient())
    assert "skill_choise" in str(exc.value)
    assert "skill_choice" in str(exc.value)  # the real name is offered


def test_no_models_is_a_setup_error(skills_dir: Path, tmp_path: Path, monkeypatch):
    _corpus(skills_dir, ["alpha"])

    class NoModels(Cfg):
        models = []

    monkeypatch.setattr(routing_run, "_config", lambda *a, **k: NoModels())
    ds = _dataset(tmp_path, [{"id": "c1", "category": "routing", "prompt": "x",
                              "scorer": {"type": "skill_choice", "expected": "alpha"}}])
    with pytest.raises(routing_run.RoutingSetupError, match="no models"):
        routing_run.execute(skills_dir=skills_dir, dataset=ds, client=ScriptedClient())


# --- the shipped dataset ------------------------------------------------------------


def test_shipped_dataset_loads_and_every_case_is_unique():
    from ollama_evals.cases import load_cases

    cases = load_cases(DATASETS / "routing.jsonl")
    assert len(cases) == 60
    assert len({c.id for c in cases}) == 60


def test_shipped_dataset_uses_only_the_skill_choice_scorer():
    from ollama_evals.cases import load_cases

    for case in load_cases(DATASETS / "routing.jsonl"):
        assert case.scorer["type"] == "skill_choice"
        assert case.category == "routing"


def test_shipped_dataset_covers_all_five_strata():
    from ollama_evals.cases import load_cases

    tags = {t for c in load_cases(DATASETS / "routing.jsonl") for t in c.tags}
    assert {"canonical", "confusion-pair", "negative", "boundary", "non-invocable"} <= tags


def test_every_expected_skill_in_the_dataset_exists():
    """A case expecting a deleted skill would be permanently unpassable."""
    from ollama_evals.cases import load_cases

    repo_skills = {s.name for s in discover(Path(__file__).resolve().parents[3] / "skills")}
    for case in load_cases(DATASETS / "routing.jsonl"):
        for name in filter(None, [case.scorer.get("expected"), *case.scorer.get("acceptable", []),
                                  *case.scorer.get("confusable", [])]):
            assert name in repo_skills, f"{case.id} references unknown skill {name!r}"
