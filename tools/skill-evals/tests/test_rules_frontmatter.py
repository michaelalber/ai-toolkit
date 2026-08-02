from pathlib import Path

from conftest import write_good_full, write_skill

from skill_evals.findings import Severity
from skill_evals.lint import lint


def _ids(skills_dir: Path, rule: str | None = None) -> list[str]:
    findings = lint(skills_dir, only=[rule] if rule else None)
    return [f.rule_id for f in findings]


def _messages(skills_dir: Path, rule: str) -> list[str]:
    return [f.message for f in lint(skills_dir, only=[rule])]


def test_clean_corpus_reports_nothing(clean_corpus: Path):
    assert list(lint(clean_corpus)) == []


# --- SK001 -------------------------------------------------------------------------


def test_sk001_flags_missing_frontmatter(skills_dir: Path):
    write_skill(skills_dir, "bare", raw="# No Frontmatter\n\nbody\n")
    assert _ids(skills_dir, "SK001") == ["SK001"]


def test_sk001_flags_unterminated_frontmatter(skills_dir: Path):
    write_skill(skills_dir, "bad", raw="---\nname: bad\n\n# Title\n")
    assert _ids(skills_dir, "SK001") == ["SK001"]


def test_sk001_flags_invalid_yaml(skills_dir: Path):
    write_skill(skills_dir, "bad", raw="---\nname: [unclosed\n---\n\nbody\n")
    assert _ids(skills_dir, "SK001") == ["SK001"]


def test_sk001_accepts_valid_frontmatter(clean_corpus: Path):
    assert _ids(clean_corpus, "SK001") == []


# --- SK002 -------------------------------------------------------------------------


def test_sk002_flags_name_directory_mismatch(skills_dir: Path):
    write_good_full(
        skills_dir, "actual-dir",
        frontmatter={"name": "old-name", "audience": "team", "description": "Does. Use when."},
    )
    assert "does not match the directory" in _messages(skills_dir, "SK002")[0]


def test_sk002_flags_missing_name(skills_dir: Path):
    write_good_full(skills_dir, "s", frontmatter={"audience": "team", "description": "d"})
    assert _ids(skills_dir, "SK002") == ["SK002"]


def test_sk002_accepts_matching_name(clean_corpus: Path):
    assert _ids(clean_corpus, "SK002") == []


# --- SK003 / SK004 -----------------------------------------------------------------


def test_sk003_flags_missing_description(skills_dir: Path):
    write_good_full(skills_dir, "s", frontmatter={"name": "s", "audience": "team"})
    assert _ids(skills_dir, "SK003") == ["SK003"]


def test_sk004_flags_overlong_description(skills_dir: Path):
    write_good_full(
        skills_dir, "s",
        frontmatter={"name": "s", "audience": "team", "description": "x" * 1100},
    )
    assert "over the 1024 limit" in _messages(skills_dir, "SK004")[0]


def test_sk004_accepts_description_at_the_limit(skills_dir: Path):
    write_good_full(
        skills_dir, "s",
        frontmatter={"name": "s", "audience": "team", "description": "x" * 1024},
    )
    assert _ids(skills_dir, "SK004") == []


# --- SK005: the false-positive guard -----------------------------------------------


def test_sk005_flags_invalid_audience(skills_dir: Path):
    write_good_full(
        skills_dir, "s",
        frontmatter={"name": "s", "audience": "everyone", "description": "d. Use when. Not for."},
    )
    assert "'everyone' is not one of" in _messages(skills_dir, "SK005")[0]


def test_sk005_flags_missing_audience(skills_dir: Path):
    write_good_full(skills_dir, "s", frontmatter={"name": "s", "description": "d"})
    assert _ids(skills_dir, "SK005") == ["SK005"]


def test_sk005_accepts_professional(skills_dir: Path):
    write_good_full(
        skills_dir, "s",
        frontmatter={"name": "s", "audience": "professional", "description": "d. Use when."},
    )
    assert _ids(skills_dir, "SK005") == []


def test_sk005_ignores_an_audience_line_inside_the_state_block(skills_dir: Path):
    """The real corpus does this — confluence-guide-writer and jira-comment-writer.

    `audience:` is a legitimate *state field*. A grep-based rule flags them; a rule that
    parses the frontmatter mapping must not.
    """
    body = (
        "# S\n\n## Core Philosophy\n\nx\n\n## Workflow\n\ny\n\n## State Block\n\n"
        "```\n<s-state>\naudience: End-User | Client | Power User\n</s-state>\n```\n\n"
        "## Output Template\n\nSee `references/a.md`.\n\n## Integration with Other Skills\n\n"
        "| Skill | Relationship |\n|---|---|\n"
    )
    write_good_full(skills_dir, "s", body=body)
    assert _ids(skills_dir, "SK005") == []


# --- SK006 / SK007 / SK008 are warnings --------------------------------------------


def test_sk006_flags_first_person_description(skills_dir: Path):
    write_good_full(
        skills_dir, "s",
        frontmatter={"name": "s", "audience": "team",
                     "description": "I will scaffold things. Use when. Not for."},
    )
    findings = lint(skills_dir, only=["SK006"]).findings
    assert findings[0].severity is Severity.WARNING


def test_sk007_flags_missing_trigger_clause(skills_dir: Path):
    write_good_full(
        skills_dir, "s",
        frontmatter={"name": "s", "audience": "team", "description": "Scaffolds packages."},
    )
    assert _ids(skills_dir, "SK007") == ["SK007"]


def test_sk008_flags_missing_negative_boundary(skills_dir: Path):
    write_good_full(
        skills_dir, "s",
        frontmatter={"name": "s", "audience": "team",
                     "description": "Scaffolds packages. Use when publishing."},
    )
    findings = lint(skills_dir, only=["SK008"]).findings
    assert len(findings) == 1
    assert findings[0].severity is Severity.WARNING  # 40/94 lack this today


def test_sk008_accepts_a_not_for_clause(skills_dir: Path):
    write_good_full(
        skills_dir, "s",
        frontmatter={"name": "s", "audience": "team",
                     "description": "Scaffolds. Use when publishing. Not for internal libs."},
    )
    assert _ids(skills_dir, "SK008") == []


# --- SK009 / SK010 -----------------------------------------------------------------


def test_sk009_flags_unknown_key(skills_dir: Path):
    write_good_full(
        skills_dir, "s",
        frontmatter={"name": "s", "audience": "team", "description": "d. Use when. Not for.",
                     "colour": "blue"},
    )
    assert "colour" in _messages(skills_dir, "SK009")[0]


def test_sk009_accepts_vendored_attribution_keys(skills_dir: Path):
    write_good_full(
        skills_dir, "s",
        frontmatter={"name": "s", "audience": "team", "description": "d. Use when. Not for.",
                     "source": "https://example.com", "source_commit": "abc1234",
                     "source_note": "vendored", "disable-model-invocation": "true"},
    )
    assert _ids(skills_dir, "SK009") == []


def test_sk010_flags_missing_declared_reference(skills_dir: Path):
    write_good_full(
        skills_dir, "s",
        frontmatter={"name": "s", "audience": "team", "description": "d. Use when. Not for.",
                     "references": "[references/gone.md]"},
    )
    assert "does not exist" in _messages(skills_dir, "SK010")[0]


def test_sk010_accepts_a_declared_reference_that_exists(skills_dir: Path):
    write_good_full(
        skills_dir, "s",
        frontmatter={"name": "s", "audience": "team", "description": "d. Use when. Not for.",
                     "references": "[references/conventions.md]"},
    )
    assert _ids(skills_dir, "SK010") == []
