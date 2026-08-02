import json
from pathlib import Path

import pytest
from conftest import write_good_full

pytest.importorskip("ollama_evals", reason="LLM layer needs the llm extra")

from skill_evals import quality_run  # noqa: E402
from skill_evals.routing_run import RoutingSetupError  # noqa: E402

DATASETS = Path(__file__).resolve().parents[1] / "datasets"


class RecordingClient:
    def __init__(self, content="the reply"):
        self._content = content
        self.sent = []

    def chat(self, model, messages, **kwargs):
        self.sent.append(messages)

        class R:
            pass

        R.content = self._content
        R.tool_calls = []
        return R()


class Verdict:
    def __init__(self, score=1.0, parsed=True, reasoning="ok"):
        self.score = score
        self.parsed = parsed
        self.reasoning = reasoning


class FakeJudge:
    def __init__(self, score=1.0):
        self._score = score

    def score(self, **kwargs):
        return Verdict(self._score)


class Cfg:
    base_url = "http://unused"
    models = ["fake"]
    temperature = 0.0
    seed = 7
    num_ctx = 32768


@pytest.fixture(autouse=True)
def _stub_config(monkeypatch):
    monkeypatch.setattr(quality_run, "_config", lambda *a, **k: Cfg())


def _dataset(tmp_path: Path, rows) -> Path:
    path = tmp_path / "quality.jsonl"
    path.write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    return path


def _case(skill="alpha", **scorer):
    spec = {"type": "skill_rubric", "skill": skill, "criteria": ["does the thing"]}
    spec.update(scorer)
    return {"id": f"q-{skill}", "category": "quality", "system_from_skill": skill,
            "prompt": "do the thing", "scorer": spec}


def _run(skills_dir, dataset, client=None, judge=None, **kw):
    return quality_run.execute(
        skills_dir=skills_dir, dataset=dataset, models=["fake"],
        client=client or RecordingClient(), judge=judge or FakeJudge(), **kw,
    )


def test_the_skill_body_becomes_the_system_prompt(skills_dir: Path, tmp_path: Path):
    write_good_full(skills_dir, "alpha")
    client = RecordingClient()
    _run(skills_dir, _dataset(tmp_path, [_case()]), client=client)

    system = client.sent[0][0]
    assert system["role"] == "system"
    assert "## Workflow" in system["content"]
    assert "audience: team" not in system["content"]  # frontmatter stripped


def test_the_body_is_read_from_disk_not_the_dataset(skills_dir: Path, tmp_path: Path):
    """A SKILL.md pasted into the dataset would go stale the moment the skill changed."""
    write_good_full(skills_dir, "alpha")
    ds = _dataset(tmp_path, [_case()])
    assert "## Workflow" not in ds.read_text()

    client = RecordingClient()
    _run(skills_dir, ds, client=client)
    assert "## Workflow" in client.sent[0][0]["content"]


def test_editing_the_skill_changes_the_next_run(skills_dir: Path, tmp_path: Path):
    write_good_full(skills_dir, "alpha")
    ds = _dataset(tmp_path, [_case()])

    write_good_full(skills_dir, "alpha",
                    body="# Alpha\n\n> \"e\"\n\n## Workflow\n\nBRAND NEW INSTRUCTION\n")
    client = RecordingClient()
    _run(skills_dir, ds, client=client)
    assert "BRAND NEW INSTRUCTION" in client.sent[0][0]["content"]


def test_manifest_records_the_skills_under_test(skills_dir: Path, tmp_path: Path):
    for name in ("alpha", "beta"):
        write_good_full(skills_dir, name)
    ds = _dataset(tmp_path, [_case("alpha"), _case("beta")])
    result = _run(skills_dir, ds)
    assert result.run.manifest["skills_under_test"] == ["alpha", "beta"]
    assert result.run.manifest["suite"] == "quality"


def test_only_filters_to_named_skills(skills_dir: Path, tmp_path: Path):
    for name in ("alpha", "beta"):
        write_good_full(skills_dir, name)
    ds = _dataset(tmp_path, [_case("alpha"), _case("beta")])
    result = _run(skills_dir, ds, only=["beta"])
    assert result.run.manifest["skills_under_test"] == ["beta"]


def test_a_case_naming_an_unknown_skill_is_a_setup_error(skills_dir: Path, tmp_path: Path):
    write_good_full(skills_dir, "alpha")
    with pytest.raises(RoutingSetupError, match="unknown skill"):
        _run(skills_dir, _dataset(tmp_path, [_case("ghost")]))


def test_a_missing_dataset_is_a_setup_error(skills_dir: Path, tmp_path: Path):
    write_good_full(skills_dir, "alpha")
    with pytest.raises(RoutingSetupError, match="no quality dataset"):
        _run(skills_dir, tmp_path / "absent.jsonl")


def test_an_empty_selection_is_a_setup_error(skills_dir: Path, tmp_path: Path):
    write_good_full(skills_dir, "alpha")
    with pytest.raises(RoutingSetupError, match="no cases"):
        _run(skills_dir, _dataset(tmp_path, [_case("alpha")]), only=["beta"])


def test_output_preview_is_wide_enough_to_adjudicate(skills_dir: Path, tmp_path: Path):
    """600 chars truncates the reply a human has to read."""
    write_good_full(skills_dir, "alpha")
    client = RecordingClient(content="z" * 3000)
    result = _run(skills_dir, _dataset(tmp_path, [_case()]), client=client)
    assert len(result.rows[0].output) == 3000


def test_failing_cases_are_listed(skills_dir: Path, tmp_path: Path):
    write_good_full(skills_dir, "alpha")
    ds = _dataset(tmp_path, [_case(threshold=0.9)])
    result = _run(skills_dir, ds, judge=FakeJudge(0.5))
    assert result.failed == ["q-alpha"]


def test_passing_cases_are_not_listed(skills_dir: Path, tmp_path: Path):
    write_good_full(skills_dir, "alpha")
    result = _run(skills_dir, _dataset(tmp_path, [_case()]), judge=FakeJudge(1.0))
    assert result.failed == []


def test_parse_failures_are_reported_separately_from_failures(skills_dir: Path, tmp_path: Path):
    write_good_full(skills_dir, "alpha")

    class Unparseable:
        def score(self, **kwargs):
            return Verdict(0.0, parsed=False)

    result = _run(skills_dir, _dataset(tmp_path, [_case()]), judge=Unparseable())
    assert result.parse_failure_rate == 1.0
    assert result.failed == []  # a broken judge is not a failing skill


def test_artifact_is_written(skills_dir: Path, tmp_path: Path):
    write_good_full(skills_dir, "alpha")
    result = _run(skills_dir, _dataset(tmp_path, [_case()]), out_dir=tmp_path / "runs")
    assert result.artifact.exists()


# --- the shipped dataset -----------------------------------------------------------


def test_shipped_quality_dataset_loads():
    from ollama_evals.cases import load_cases

    cases = load_cases(DATASETS / "quality.jsonl")
    assert len(cases) == 12
    assert len({c.id for c in cases}) == 12


def test_every_shipped_case_names_a_real_skill():
    from ollama_evals.cases import load_cases

    from skill_evals.corpus import discover

    names = {s.name for s in discover(Path(__file__).resolve().parents[3] / "skills")}
    for case in load_cases(DATASETS / "quality.jsonl"):
        assert case.scorer["skill"] in names, case.id


def test_every_shipped_case_has_a_real_task_and_criteria():
    from ollama_evals.cases import load_cases

    for case in load_cases(DATASETS / "quality.jsonl"):
        assert case.scorer["type"] == "skill_rubric"
        assert len(case.scorer["criteria"]) >= 5, f"{case.id} has thin criteria"
        assert "PLACEHOLDER" not in case.prompt
        assert len(case.prompt) > 40, f"{case.id} has a stub prompt"


def test_shipped_cases_declare_their_known_references():
    """So the structural sub-score can tell a real pointer from a hallucinated one."""
    from ollama_evals.cases import load_cases

    for case in load_cases(DATASETS / "quality.jsonl"):
        assert "known_references" in case.scorer, case.id
