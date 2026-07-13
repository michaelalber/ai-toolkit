"""CLI integration tests for the scan and enrich subcommands."""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from code2md.cli import app

runner = CliRunner()

_FAKE_JSON = json.dumps(
    {
        "summary": "Greets a user by name.",
        "questions": ["How do I greet a user?", "What does greet return?"],
        "symbols": [{"name": "greet", "description": "returns a greeting"}],
    }
)


class _FakeClient:
    """Stands in for OllamaClient; returns canned JSON for any prompt."""

    def __init__(self, *_args, **_kwargs) -> None:
        pass

    def generate(self, model: str, prompt: str, *, json_format: bool = True) -> str:
        return _FAKE_JSON


class TestFlags:
    def test_version(self) -> None:
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "0.2.0" in result.output

    def test_scan_missing_dir_errors(self, tmp_path: Path) -> None:
        result = runner.invoke(app, ["scan", str(tmp_path / "nope")])
        assert result.exit_code == 1


class TestScan:
    def test_produces_output_tree(self, sample_repo: Path, tmp_path: Path) -> None:
        out = tmp_path / "out"
        result = runner.invoke(
            app, ["scan", str(sample_repo), "--out", str(out), "--name", "myapp"]
        )
        assert result.exit_code == 0, result.output
        assert (out / "src" / "main.py.md").exists()
        assert (out / "src" / "util.ts.md").exists()
        assert (out / "_overview.md").exists()
        assert not (out / "secret.py.md").exists()
        doc = (out / "src" / "main.py.md").read_text()
        assert "```python" in doc
        assert "path: src/main.py" in doc

    def test_prints_ingest_command(self, sample_repo: Path, tmp_path: Path) -> None:
        out = tmp_path / "out"
        result = runner.invoke(
            app, ["scan", str(sample_repo), "--out", str(out), "--name", "My App"]
        )
        assert "--collection project_my_app" in result.output

    def test_no_overview_flag(self, sample_repo: Path, tmp_path: Path) -> None:
        out = tmp_path / "out"
        runner.invoke(app, ["scan", str(sample_repo), "--out", str(out), "--no-overview"])
        assert not (out / "_overview.md").exists()

    def test_empty_repo_exits_nonzero(self, tmp_path: Path) -> None:
        empty = tmp_path / "empty"
        empty.mkdir()
        result = runner.invoke(app, ["scan", str(empty), "--out", str(tmp_path / "o")])
        assert result.exit_code == 1


def _scan(sample_repo: Path, out: Path) -> None:
    result = runner.invoke(app, ["scan", str(sample_repo), "--out", str(out), "--name", "myapp"])
    assert result.exit_code == 0, result.output


class TestEnrich:
    @patch("code2md.cli.OllamaClient", _FakeClient)
    def test_generates_enriched_docs(self, sample_repo: Path, tmp_path: Path) -> None:
        out = tmp_path / "out"
        _scan(sample_repo, out)
        result = runner.invoke(app, ["enrich", str(out), "--model", "fake-model"])
        assert result.exit_code == 0, result.output

        enriched = out / "_enriched" / "src" / "main.py.enriched.md"
        assert enriched.exists()
        text = enriched.read_text()
        assert "generated: true" in text
        assert "model: fake-model" in text
        assert "derived_from: src/main.py.md" in text
        assert "Greets a user by name." in text
        assert "## Questions this file answers" in text
        # The overview is not enriched.
        assert not (out / "_enriched" / "_overview.enriched.md").exists()

    @patch("code2md.cli.OllamaClient", _FakeClient)
    def test_requires_a_model(self, sample_repo: Path, tmp_path: Path, monkeypatch) -> None:
        monkeypatch.delenv("CODE2MD_ENRICH_MODEL", raising=False)
        out = tmp_path / "out"
        _scan(sample_repo, out)
        result = runner.invoke(app, ["enrich", str(out)])
        assert result.exit_code == 1
        assert "no model" in result.output.lower()

    @patch("code2md.cli.OllamaClient", _FakeClient)
    def test_second_run_is_cached(self, sample_repo: Path, tmp_path: Path) -> None:
        out = tmp_path / "out"
        _scan(sample_repo, out)
        runner.invoke(app, ["enrich", str(out), "--model", "fake-model"])
        result = runner.invoke(app, ["enrich", str(out), "--model", "fake-model"])
        assert "cached" in result.output
        assert "Enriched 0 file(s)" in result.output

    def test_missing_scan_dir_errors(self, tmp_path: Path) -> None:
        result = runner.invoke(app, ["enrich", str(tmp_path / "nope"), "--model", "m"])
        assert result.exit_code == 1
