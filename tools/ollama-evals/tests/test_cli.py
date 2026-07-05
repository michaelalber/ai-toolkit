import json
from pathlib import Path

from typer.testing import CliRunner

from ollama_evals import cli
from ollama_evals.runner import CaseResult, RunResult, save_run

runner = CliRunner()


class FakeChat:
    def __init__(self, content="", tool_calls=None):
        self.content = content
        self.tool_calls = tool_calls or []


class FakeClient:
    def __init__(self, content="answer here", models=None):
        self._content = content
        self._models = models or ["qwen2.5-coder:7b", "llama3.1:8b"]

    def chat(self, **kwargs):
        return FakeChat(self._content)

    def list_models(self):
        return self._models


def _patch_client(monkeypatch, client):
    monkeypatch.setattr(cli, "resolve_client", lambda cfg: client)


def test_list_models(monkeypatch):
    _patch_client(monkeypatch, FakeClient(models=["m1", "m2"]))
    result = runner.invoke(cli.app, ["list-models"])
    assert result.exit_code == 0
    assert "m1" in result.output and "m2" in result.output


def test_run_creates_artifact_and_prints_matrix(monkeypatch, tmp_path: Path):
    ds = tmp_path / "datasets"
    ds.mkdir()
    scorer = {"type": "contains", "value": "answer"}
    case = {"id": "x", "category": "coding", "prompt": "q", "scorer": scorer}
    (ds / "coding.jsonl").write_text(json.dumps(case) + "\n")
    _patch_client(monkeypatch, FakeClient(content="the answer is here"))

    out = tmp_path / "runs"
    result = runner.invoke(
        cli.app,
        ["run", "--models", "m", "--suite", "coding", "--datasets-dir", str(ds), "--out", str(out)],
    )
    assert result.exit_code == 0, result.output
    assert "coding" in result.output
    assert list(out.glob("*.run.json"))  # artifact written


def test_run_with_no_models_errors(monkeypatch, tmp_path: Path):
    ds = tmp_path / "datasets"
    ds.mkdir()
    scorer = {"type": "contains", "value": "a"}
    case = {"id": "x", "category": "coding", "prompt": "q", "scorer": scorer}
    (ds / "coding.jsonl").write_text(json.dumps(case) + "\n")
    # config has no models and none passed
    cfg = tmp_path / "empty.yaml"
    cfg.write_text("models: []\n")
    result = runner.invoke(
        cli.app,
        ["run", "--suite", "coding", "--datasets-dir", str(ds), "--config", str(cfg)],
    )
    assert result.exit_code == 2


def _make_run(tmp_path, run_id, model, score):
    run = RunResult(
        manifest={"run_id": run_id, "models": [model]},
        results=[CaseResult(model, "c1", "coding", score, score == 1.0)],
    )
    return save_run(run, tmp_path)


def test_compare_passes_when_improved(tmp_path: Path):
    base = _make_run(tmp_path, "b", "old", 0.5)
    cand = _make_run(tmp_path, "c", "new", 1.0)
    result = runner.invoke(cli.app, ["compare", str(base), str(cand)])
    assert result.exit_code == 0
    assert "PASS" in result.output


def test_compare_fails_and_exits_nonzero_on_regression(tmp_path: Path):
    base = _make_run(tmp_path, "b", "old", 1.0)
    cand = _make_run(tmp_path, "c", "new", 0.3)
    html = tmp_path / "report.html"
    result = runner.invoke(
        cli.app, ["compare", str(base), str(cand), "--threshold", "0.1", "--html", str(html)]
    )
    assert result.exit_code == 1
    assert "REGRESSION" in result.output
    assert html.exists() and "<html" in html.read_text().lower()


def test_report_renders_and_writes_html(tmp_path: Path):
    run_path = _make_run(tmp_path, "r", "m", 1.0)
    html = tmp_path / "matrix.html"
    result = runner.invoke(cli.app, ["report", str(run_path), "--html", str(html)])
    assert result.exit_code == 0
    assert "coding" in result.output
    assert html.exists()


def test_calibrate_reports_agreement(monkeypatch, tmp_path: Path):
    # Judge always scores 5/5 -> agrees with human-good, disagrees with human-bad.
    _patch_client(monkeypatch, FakeClient(content='{"score": 5, "reasoning": "ok"}'))
    calib = tmp_path / "calib.jsonl"
    rows = [
        {"id": "g", "prompt": "p", "output": "o", "criteria": "c", "human_score": 1.0},
        {"id": "b", "prompt": "p", "output": "o", "criteria": "c", "human_score": 0.0},
    ]
    calib.write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    result = runner.invoke(cli.app, ["calibrate", "--dataset", str(calib)])
    assert result.exit_code == 0
    assert "agreement: 0.50" in result.output
