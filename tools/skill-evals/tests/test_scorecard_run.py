from pathlib import Path

import pytest
from conftest import write_good_full

pytest.importorskip("ollama_evals", reason="LLM layer needs the llm extra")

from skill_evals import rubric as rubric_mod  # noqa: E402
from skill_evals import scorecard_run  # noqa: E402
from skill_evals.routing_run import RoutingSetupError  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[3]
REAL_RUBRIC = REPO_ROOT / rubric_mod.RUBRIC_PATH


class Verdict:
    def __init__(self, score=0.75, parsed=True, reasoning="ok"):
        self.score = score
        self.parsed = parsed
        self.reasoning = reasoning


class FakeJudge:
    def __init__(self, verdict=None):
        self._verdict = verdict or Verdict()
        self.calls = 0

    def score(self, **kwargs):
        self.calls += 1
        return self._verdict


class Cfg:
    base_url = "http://unused"
    models = ["fake"]
    temperature = 0.0
    seed = 7
    num_ctx = 32768


@pytest.fixture(autouse=True)
def _stub_config(monkeypatch):
    monkeypatch.setattr(scorecard_run, "_config", lambda *a, **k: Cfg())


@pytest.fixture
def repo(tmp_path: Path):
    if not REAL_RUBRIC.is_file():
        pytest.skip("real scoring-rubric.md not present")
    root = tmp_path / "repo"
    skills = root / "skills"
    skills.mkdir(parents=True)
    target = root / rubric_mod.RUBRIC_PATH
    target.parent.mkdir(parents=True)
    target.write_text(REAL_RUBRIC.read_text())
    return root, skills


def _run(repo, **kw):
    root, skills = repo
    return scorecard_run.execute(
        skills_dir=skills, repo_root=root, models=["fake"], judge=FakeJudge(), **kw
    )


def test_scores_every_skill(repo):
    _, skills = repo
    for name in ("alpha", "beta"):
        write_good_full(skills, name)
    result = _run(repo)
    assert {s.skill for s in result.scores} == {"alpha", "beta"}
    assert result.summary["n_skills"] == 2


def test_manifest_pins_the_rubric_sha(repo):
    root, skills = repo
    write_good_full(skills, "alpha")
    result = _run(repo)
    expected = rubric_mod.load(root / rubric_mod.RUBRIC_PATH).sha256
    assert result.run.manifest["rubric_sha256"] == expected
    assert result.run.manifest["suite"] == "scorecard"
    assert result.run.manifest["n_dimensions"] == 10


def test_results_are_one_case_result_per_scored_dimension(repo):
    _, skills = repo
    write_good_full(skills, "alpha")
    result = _run(repo)
    assert len(result.run.results) == 10
    assert {r.category for r in result.run.results} == {f"rubric-d{i}" for i in range(1, 11)}


def test_only_selects_named_skills(repo):
    _, skills = repo
    for name in ("alpha", "beta", "gamma"):
        write_good_full(skills, name)
    assert {s.skill for s in _run(repo, only=["beta"]).scores} == {"beta"}


def test_only_with_an_unknown_skill_is_a_setup_error(repo):
    _, skills = repo
    write_good_full(skills, "alpha")
    with pytest.raises(RoutingSetupError, match="unknown skill"):
        _run(repo, only=["nope"])


def test_artifact_is_written(repo, tmp_path: Path):
    _, skills = repo
    write_good_full(skills, "alpha")
    result = _run(repo, out_dir=tmp_path / "runs")
    assert result.artifact.exists()


def test_run_id_is_fresh_per_invocation(repo):
    """Two back-to-back runs must not collide on the same artifact filename.

    Was pinned the other way (same inputs -> same run_id) until a real 3x variance
    check silently overwrote runs 1 and 2 with run 3 — the id was a hash of
    (rubric, model, n), which a repeat invocation always reproduces.
    """
    _, skills = repo
    write_good_full(skills, "alpha")
    assert _run(repo).run.manifest["run_id"] != _run(repo).run.manifest["run_id"]


def test_deprecate_and_revise_lists_are_derived(repo):
    _, skills = repo
    write_good_full(skills, "alpha")
    result = scorecard_run.execute(
        skills_dir=skills, repo_root=repo[0], models=["fake"],
        judge=FakeJudge(Verdict(0.0)),  # every judged dimension scores 1
    )
    assert result.deprecate == ["alpha"]
    assert result.revise == []


def test_no_models_is_a_setup_error(repo, monkeypatch):
    _, skills = repo
    write_good_full(skills, "alpha")

    class NoModels(Cfg):
        models = []

    monkeypatch.setattr(scorecard_run, "_config", lambda *a, **k: NoModels())
    with pytest.raises(RoutingSetupError, match="no models"):
        scorecard_run.execute(skills_dir=skills, repo_root=repo[0], judge=FakeJudge())


def test_a_missing_rubric_is_a_parse_error(tmp_path: Path):
    root = tmp_path / "bare"
    (root / "skills").mkdir(parents=True)
    with pytest.raises(rubric_mod.RubricParseError):
        scorecard_run.execute(skills_dir=root / "skills", repo_root=root, models=["m"],
                              judge=FakeJudge())


# --- --changed-since is passed to git, so it is validated --------------------------


@pytest.mark.parametrize("ref", ["--upload-pack=evil", "-x", "; rm -rf /", "a b", "$(id)"])
def test_a_ref_that_could_reach_git_as_an_option_is_rejected(repo, ref):
    _, skills = repo
    write_good_full(skills, "alpha")
    with pytest.raises(RoutingSetupError, match="not a valid git revision"):
        _run(repo, changed_since=ref)


@pytest.mark.parametrize("ref", ["HEAD~20", "main", "v1.2.3", "origin/main", "abc1234",
                                 "HEAD@{2}", "feature/thing"])
def test_ordinary_revisions_are_accepted(repo, ref, monkeypatch):
    _, skills = repo
    write_good_full(skills, "alpha")
    monkeypatch.setattr(scorecard_run, "_changed_skills", lambda root, r: {"alpha"})
    assert _run(repo, changed_since=ref).summary["n_skills"] == 1


def test_changed_since_narrows_the_selection(repo, monkeypatch):
    _, skills = repo
    for name in ("alpha", "beta"):
        write_good_full(skills, name)
    monkeypatch.setattr(scorecard_run, "_changed_skills", lambda root, ref: {"beta"})
    assert {s.skill for s in _run(repo, changed_since="HEAD~1").scores} == {"beta"}


def test_no_selection_is_a_setup_error(repo, monkeypatch):
    _, skills = repo
    write_good_full(skills, "alpha")
    monkeypatch.setattr(scorecard_run, "_changed_skills", lambda root, ref: set())
    with pytest.raises(RoutingSetupError, match="no skills selected"):
        _run(repo, changed_since="HEAD~1")
