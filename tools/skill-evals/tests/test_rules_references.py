from pathlib import Path

from conftest import CANONICAL_BODY, filler, write_good_full, write_skill, write_tiny

from skill_evals.lint import lint


def _ids(skills_dir: Path, rule: str) -> list[str]:
    return [f.rule_id for f in lint(skills_dir, only=[rule])]


def _findings(skills_dir: Path, rule: str):
    return lint(skills_dir, only=[rule]).findings


# --- SK040 / SK041 -----------------------------------------------------------------


def test_sk040_flags_a_full_skill_without_references(skills_dir: Path):
    write_skill(skills_dir, "s", body=CANONICAL_BODY)
    assert "no references/ directory" in _findings(skills_dir, "SK040")[0].message


def test_sk040_exempts_a_sub_20_line_skill(skills_dir: Path):
    """The 2026-07-22 decision: a 19-line skill has no depth to relocate."""
    write_tiny(skills_dir)
    assert _ids(skills_dir, "SK040") == []


def test_sk041_flags_a_full_skill_with_one_reference(skills_dir: Path):
    write_skill(skills_dir, "s", body=CANONICAL_BODY, references={"conventions.md": filler()})
    assert "full tier requires 2" in _findings(skills_dir, "SK041")[0].message


def test_sk041_accepts_two_references_for_full(clean_corpus: Path):
    assert _ids(clean_corpus, "SK041") == []


def test_sk041_requires_only_one_for_minimal(skills_dir: Path):
    body = "# T\n\nSee `references/notes.md`.\n\n" + "\n".join(f"step {i}" for i in range(30))
    write_skill(skills_dir, "s", body=body, references={"notes.md": filler()})
    assert _ids(skills_dir, "SK041") == []


# --- SK042: the dangling-pointer rule ----------------------------------------------


def test_sk042_flags_a_pointer_with_no_file(skills_dir: Path):
    body = CANONICAL_BODY.replace("references/templates.md", "references/gone.md")
    write_good_full(skills_dir, "s", body=body)
    finding = _findings(skills_dir, "SK042")[0]
    assert "references/gone.md does not exist" in finding.message
    assert finding.line > 0


def test_sk042_resolves_relative_to_the_owning_skill(skills_dir: Path):
    """The tdd-agent defect: the file exists, but under a *different* skill."""
    write_good_full(skills_dir, "tdd-loop",
                    references={"conventions.md": filler(), "templates.md": filler(),
                                "code-smells.md": filler()})
    body = CANONICAL_BODY + "\nSee `references/code-smells.md` during REFACTOR.\n"
    write_good_full(skills_dir, "tdd-agent", body=body)
    findings = _findings(skills_dir, "SK042")
    assert [f.skill for f in findings] == ["tdd-agent"]
    assert "skills/tdd-agent/" in findings[0].message


def test_sk042_accepts_pointers_that_resolve(clean_corpus: Path):
    assert _ids(clean_corpus, "SK042") == []


def test_sk042_resolves_a_pointer_into_a_subdirectory(skills_dir: Path):
    d = write_good_full(skills_dir, "s",
                        body=CANONICAL_BODY + "\nSee `references/archetypes/python.md`.\n")
    (d / "references" / "archetypes").mkdir()
    (d / "references" / "archetypes" / "python.md").write_text(filler())
    assert _ids(skills_dir, "SK042") == []


# --- SK043 / SK044 -----------------------------------------------------------------


def test_sk043_flags_an_unreachable_reference_file(skills_dir: Path):
    write_good_full(skills_dir, "s",
                    references={"conventions.md": filler(), "templates.md": filler(),
                                "orphan.md": filler()})
    assert "never named in SKILL.md" in _findings(skills_dir, "SK043")[0].message


def test_sk043_accepts_fully_pointed_references(clean_corpus: Path):
    assert _ids(clean_corpus, "SK043") == []


def test_sk044_flags_a_stub_reference(skills_dir: Path):
    write_good_full(skills_dir, "s",
                    references={"conventions.md": filler(), "templates.md": "just one line"})
    assert "a stub, not depth" in _findings(skills_dir, "SK044")[0].message


def test_sk044_accepts_substantive_references(clean_corpus: Path):
    assert _ids(clean_corpus, "SK044") == []
