from pathlib import Path

from conftest import CANONICAL_BODY, write_good_full, write_good_minimal, write_skill, write_tiny

from skill_evals.lint import lint


def _ids(skills_dir: Path, rule: str) -> list[str]:
    return [f.rule_id for f in lint(skills_dir, only=[rule])]


def _messages(skills_dir: Path, rule: str) -> list[str]:
    return [f.message for f in lint(skills_dir, only=[rule])]


# --- SK020 line budget -------------------------------------------------------------


def test_sk020_flags_a_full_skill_over_200_lines(skills_dir: Path):
    body = CANONICAL_BODY + "\n" + "\n".join(f"padding {i}" for i in range(220))
    write_good_full(skills_dir, "fat", body=body)
    assert "exceeds the full budget of 200" in _messages(skills_dir, "SK020")[0]


def test_sk020_flags_a_minimal_skill_over_100_lines(skills_dir: Path):
    """Over 100 lines a skill is judged as FULL, so it is the 200 ceiling that applies."""
    body = "# T\n\n" + "\n".join(f"step {i}" for i in range(250))
    write_skill(skills_dir, "long", body=body, references={"a.md": "x" * 40})
    assert _ids(skills_dir, "SK020") == ["SK020"]


def test_sk020_accepts_a_skill_within_budget(clean_corpus: Path):
    assert _ids(clean_corpus, "SK020") == []


def test_sk020_never_applies_to_an_exempt_skill(skills_dir: Path):
    write_tiny(skills_dir)
    assert _ids(skills_dir, "SK020") == []


# --- SK021 / SK022 / SK023 sections ------------------------------------------------


def test_sk021_flags_missing_canonical_sections(skills_dir: Path):
    body = CANONICAL_BODY.replace("## Output Template", "## Something Else")
    write_good_full(skills_dir, "s", body=body)
    assert "Output Template" in _messages(skills_dir, "SK021")[0]


def test_sk021_does_not_apply_to_minimal_skills(skills_dir: Path):
    write_good_minimal(skills_dir)
    assert _ids(skills_dir, "SK021") == []


def test_sk022_flags_sections_out_of_order(skills_dir: Path):
    body = (
        "# T\n\n> \"e\"\n\n## Workflow\n\nw\n\n## Core Philosophy\n\nc\n\n"
        "## State Block\n\n```\n<s-state>\nphase: A\n</s-state>\n```\n\n"
        "## Output Template\n\nSee `references/conventions.md`.\n\n"
        "## Integration with Other Skills\n\n| Skill | Relationship |\n|---|---|\n"
        + "\n".join(f"note {i}" for i in range(100))  # past the minimal ceiling
    )
    write_good_full(skills_dir, "s", body=body)
    assert "out of order" in _messages(skills_dir, "SK022")[0]


def test_sk023_flags_a_non_canonical_section(skills_dir: Path):
    body = CANONICAL_BODY + "\n## Error Recovery\n\nSteps that belong in references/.\n"
    write_good_full(skills_dir, "s", body=body)
    assert "Error Recovery" in _messages(skills_dir, "SK023")[0]


def test_sk023_accepts_the_canonical_set(clean_corpus: Path):
    assert _ids(clean_corpus, "SK023") == []


# --- SK024 epigraph ----------------------------------------------------------------


def test_sk024_flags_a_missing_epigraph(skills_dir: Path):
    body = CANONICAL_BODY.replace('> "An epigraph that says something."\n', "")
    write_good_full(skills_dir, "s", body=body)
    assert _ids(skills_dir, "SK024") == ["SK024"]


# --- SK025 / SK025b constraints ----------------------------------------------------


def test_sk025_flags_too_few_constraints(skills_dir: Path):
    body = CANONICAL_BODY.replace("3. THIRD — do the third thing.\n", "")
    body = body.replace("2. SECOND — do the second thing.\n", "")
    write_good_full(skills_dir, "s", body=body)
    assert "expected 3-6" in _messages(skills_dir, "SK025")[0]


def test_sk025_flags_a_missing_constraints_list(skills_dir: Path):
    body = CANONICAL_BODY.replace("**Non-Negotiable Constraints:**", "**Some Other Heading:**")
    write_good_full(skills_dir, "s", body=body)
    assert "no numbered 'Non-Negotiable Constraints' list" in _messages(skills_dir, "SK025")[0]


def test_sk025_accepts_six_constraints(skills_dir: Path):
    """qraspi-skeleton, a stated gold standard, carries six."""
    extra = "4. FOURTH — x.\n5. FIFTH — y.\n6. SIXTH — z.\n"
    body = CANONICAL_BODY.replace("3. THIRD — do the third thing.\n",
                                  "3. THIRD — do the third thing.\n" + extra)
    write_good_full(skills_dir, "s", body=body)
    assert _ids(skills_dir, "SK025") == []


def test_sk025b_flags_non_sequential_numbering(skills_dir: Path):
    """The real corpus does this — tdd-agent numbers its constraints 1,2,3,4,4."""
    body = CANONICAL_BODY.replace("3. THIRD — do the third thing.",
                                  "2. THIRD — do the third thing.")
    write_good_full(skills_dir, "s", body=body)
    assert "not sequential" in _messages(skills_dir, "SK025b")[0]


def test_sk025b_accepts_sequential_numbering(clean_corpus: Path):
    assert _ids(clean_corpus, "SK025b") == []


# --- SK026 tables ------------------------------------------------------------------


def test_sk026_flags_a_large_inline_table(skills_dir: Path):
    rows = "\n".join(f"| item{i} | meaning {i} |" for i in range(10))
    body = CANONICAL_BODY.replace(
        "## Workflow", f"## Workflow\n\n| Principle | Why |\n|---|---|\n{rows}\n", 1
    )
    write_good_full(skills_dir, "s", body=body)
    assert "10-row table inline" in _messages(skills_dir, "SK026")[0]


def test_sk026_exempts_the_integration_table(skills_dir: Path):
    rows = "\n".join(f"| `other-{i}` | Relates. |" for i in range(10))
    body = CANONICAL_BODY.replace(
        "| `good-minimal` | Runs after this one. |", rows
    )
    write_good_full(skills_dir, "s", body=body)
    assert _ids(skills_dir, "SK026") == []


# --- SK027 placeholders ------------------------------------------------------------


def test_sk027_flags_a_todo(skills_dir: Path):
    write_good_full(skills_dir, "s", body=CANONICAL_BODY + "\nTODO: write the rest.\n")
    assert _ids(skills_dir, "SK027") == ["SK027"]


def test_sk027_flags_a_fill_in_placeholder(skills_dir: Path):
    write_good_full(skills_dir, "s", body=CANONICAL_BODY + "\nSee [fill in the name].\n")
    assert _ids(skills_dir, "SK027") == ["SK027"]


def test_sk027_ignores_an_id_format_placeholder(skills_dir: Path):
    """`REQ-XXX` and `DRAFT-NNN` are ID *formats* the skill teaches, not unfinished text."""
    body = CANONICAL_BODY + "\nAssigns canonical `REQ-XXX` IDs from `DRAFT-NNN` documents.\n"
    write_good_full(skills_dir, "s", body=body)
    assert _ids(skills_dir, "SK027") == []


def test_sk027_still_flags_a_bare_xxx(skills_dir: Path):
    write_good_full(skills_dir, "s", body=CANONICAL_BODY + "\nXXX finish this section.\n")
    assert _ids(skills_dir, "SK027") == ["SK027"]


def test_sk027_ignores_placeholders_inside_code_fences(skills_dir: Path):
    """A state block legitimately shows `[description]` as a field placeholder."""
    body = CANONICAL_BODY + "\n```\nTODO: this is sample output, not an unfinished skill\n```\n"
    write_good_full(skills_dir, "s", body=body)
    assert _ids(skills_dir, "SK027") == []
