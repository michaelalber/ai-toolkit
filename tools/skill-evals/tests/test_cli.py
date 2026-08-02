import json
from pathlib import Path

import yaml
from conftest import CANONICAL_BODY, write_good_full
from typer.testing import CliRunner

from skill_evals import cli

runner = CliRunner()


def _invoke(*args):
    return runner.invoke(cli.app, list(args))


# --- exit codes --------------------------------------------------------------------


def test_lint_exits_zero_on_a_clean_corpus(clean_corpus: Path):
    result = _invoke("lint", "--skills-dir", str(clean_corpus))
    assert result.exit_code == 0, result.output
    assert "clean" in result.output


def test_lint_exits_one_on_an_error(skills_dir: Path):
    write_good_full(skills_dir, "s",
                    body=CANONICAL_BODY.replace("references/templates.md", "references/gone.md"))
    result = _invoke("lint", "--skills-dir", str(skills_dir))
    assert result.exit_code == 1
    assert "SK042" in result.output


def test_lint_exits_zero_on_warnings_alone(skills_dir: Path):
    write_good_full(skills_dir, "s",
                    frontmatter={"name": "s", "audience": "team",
                                 "description": "Scaffolds things."})  # no trigger, no boundary
    result = _invoke("lint", "--skills-dir", str(skills_dir))
    assert result.exit_code == 0
    assert "SK007" in result.output


def test_strict_promotes_warnings_to_a_gate_failure(skills_dir: Path):
    write_good_full(skills_dir, "s",
                    frontmatter={"name": "s", "audience": "team",
                                 "description": "Scaffolds things."})
    assert _invoke("lint", "--skills-dir", str(skills_dir), "--strict").exit_code == 1


def test_lint_exits_two_on_a_missing_skills_dir(tmp_path: Path):
    result = _invoke("lint", "--skills-dir", str(tmp_path / "nope"))
    assert result.exit_code == 2


def test_lint_exits_two_on_an_unknown_rule(clean_corpus: Path):
    result = _invoke("lint", "--skills-dir", str(clean_corpus), "--rule", "SK999")
    assert result.exit_code == 2
    assert "SK999" in result.output


def test_lint_exits_two_on_an_unknown_format(clean_corpus: Path):
    result = _invoke("lint", "--skills-dir", str(clean_corpus), "--format", "yaml")
    assert result.exit_code == 2


# --- output formats ----------------------------------------------------------------


def test_json_format_is_parseable(clean_corpus: Path):
    result = _invoke("lint", "--skills-dir", str(clean_corpus), "--format", "json")
    assert json.loads(result.output)["total_skills"] == 3


def test_markdown_format_renders_a_heading(clean_corpus: Path):
    result = _invoke("lint", "--skills-dir", str(clean_corpus), "--format", "markdown")
    assert "# Skill lint" in result.output


def test_rule_filter_restricts_the_run(skills_dir: Path):
    write_good_full(skills_dir, "s",
                    body=CANONICAL_BODY.replace("references/templates.md", "references/gone.md"),
                    frontmatter={"name": "s", "audience": "team", "description": "Scaffolds."})
    result = _invoke("lint", "--skills-dir", str(skills_dir), "--rule", "SK042", "--format", "json")
    rules = {f["rule"] for f in json.loads(result.output)["findings"]}
    assert rules == {"SK042"}


# --- baseline round trip -----------------------------------------------------------


def test_write_baseline_then_lint_is_clean(skills_dir: Path, tmp_path: Path):
    write_good_full(skills_dir, "s",
                    body=CANONICAL_BODY.replace("references/templates.md", "references/gone.md"))
    out = tmp_path / "known-defects.yaml"
    written = _invoke("write-baseline", str(out), "--skills-dir", str(skills_dir),
                      "--note", "accepted at adoption")
    assert written.exit_code == 0
    assert yaml.safe_load(out.read_text())["note"] == "accepted at adoption"

    after = _invoke("lint", "--skills-dir", str(skills_dir), "--baseline", str(out))
    assert after.exit_code == 0


# --- discovery ---------------------------------------------------------------------


def test_list_rules_names_every_rule():
    result = _invoke("list-rules")
    assert result.exit_code == 0
    for rule_id in ("SK001", "SK027", "SK032", "SK042"):
        assert rule_id in result.output


def test_find_repo_root_locates_the_toolkit():
    root = cli.find_repo_root(Path(__file__).resolve().parent)
    assert (root / "skills").is_dir()
    assert (root / "CLAUDE.md").is_file()


def test_find_repo_root_falls_back_to_the_start_directory(tmp_path: Path):
    assert cli.find_repo_root(tmp_path) == tmp_path.resolve()
