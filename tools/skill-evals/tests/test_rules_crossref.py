from pathlib import Path

from conftest import CANONICAL_BODY, write_good_full

from skill_evals.lint import lint

PI_HEADER = "| Skill | Flags | Why it fits local |\n|-------|-------|-------------------|"


def _integration(*targets: str) -> str:
    rows = "\n".join(f"| `{t}` | Relates. |" for t in targets)
    return CANONICAL_BODY.replace(
        "## Integration with Other Skills\n\n| Skill | Relationship |\n|-------|-------------|\n",
        "## Integration with Other Skills\n\n| Skill | Relationship |\n|-------|-------------|\n"
        + rows + "\n",
    )


def _repo(tmp_path: Path) -> tuple[Path, Path]:
    root = tmp_path / "repo"
    skills = root / "skills"
    skills.mkdir(parents=True)
    return root, skills


def _messages(skills, rule, root=None, **kw):
    return [f.message for f in lint(skills, only=[rule], repo_root=root, **kw)]


def _write_pi(root: Path, names, green=None, footer=None):
    green = len(names) if green is None else green
    rows = "\n".join(f"| {n} | | because |" for n in names)
    total = footer if footer is not None else len(names)
    (root / "pi").mkdir(exist_ok=True)
    (root / "pi" / "SKILLS-local.md").write_text(
        f"# Local\n\n## 🟢 Green — ship as-is ({green})\n\n{PI_HEADER}\n{rows}\n\n"
        f"> Counts: 🟢 {total} · 🟡 0 · 🔴 0 = {total}.\n"
    )


# --- SK050 / SK051 / SK052 ---------------------------------------------------------


def test_sk050_flags_an_integration_target_that_is_not_a_skill(tmp_path: Path):
    root, skills = _repo(tmp_path)
    write_good_full(skills, "alpha", body=_integration("tdd"))
    write_good_full(skills, "tdd-loop")
    messages = _messages(skills, "SK050", root)
    assert "names `tdd`, which is not a skill" in messages[0]
    assert "did you mean 'tdd-loop'?" in messages[0]


def test_sk050_accepts_a_resolving_target(tmp_path: Path):
    root, skills = _repo(tmp_path)
    write_good_full(skills, "alpha", body=_integration("beta"))
    write_good_full(skills, "beta")
    assert _messages(skills, "SK050", root) == []


def test_sk050_accepts_an_allowlisted_non_skill(tmp_path: Path):
    root, skills = _repo(tmp_path)
    write_good_full(skills, "alpha", body=_integration("cargo-audit"))
    assert _messages(skills, "SK050", root, known_non_skills={"cargo-audit"}) == []


def test_sk050_ignores_the_relationship_column(tmp_path: Path):
    """Only the first column is a declaration; the prose column name-drops freely."""
    root, skills = _repo(tmp_path)
    body = CANONICAL_BODY.replace(
        "|-------|-------------|\n",
        "|-------|-------------|\n| `beta` | Runs after `some-unrelated-tool`. |\n",
    )
    write_good_full(skills, "alpha", body=body)
    write_good_full(skills, "beta")
    assert _messages(skills, "SK050", root) == []


def test_sk051_flags_a_one_directional_reference(tmp_path: Path):
    root, skills = _repo(tmp_path)
    write_good_full(skills, "alpha", body=_integration("beta"))
    write_good_full(skills, "beta")
    assert "does not name `alpha` back" in _messages(skills, "SK051", root)[0]


def test_sk051_accepts_a_reciprocal_pair(tmp_path: Path):
    root, skills = _repo(tmp_path)
    write_good_full(skills, "alpha", body=_integration("beta"))
    write_good_full(skills, "beta", body=_integration("alpha"))
    assert _messages(skills, "SK051", root) == []


def test_sk052_flags_a_stale_skill_name_in_prose(tmp_path: Path):
    root, skills = _repo(tmp_path)
    write_good_full(skills, "alpha",
                    body=CANONICAL_BODY + "\nSee `dotnet-security-review-federal` for gov work.\n")
    write_good_full(skills, "security-review-federal")
    assert "stale rename?" in _messages(skills, "SK052", root)[0]


def test_sk052_ignores_single_word_tokens(tmp_path: Path):
    """A backticked `python` would prefix-match python-* and bury the real hits."""
    root, skills = _repo(tmp_path)
    write_good_full(skills, "alpha", body=CANONICAL_BODY + "\nWritten in `python` throughout.\n")
    write_good_full(skills, "python-feature-slice")
    assert _messages(skills, "SK052", root) == []


def test_sk052_stays_quiet_about_unrelated_tools(tmp_path: Path):
    """`cargo-audit` resembles no skill, so it is not a rename and not reported."""
    root, skills = _repo(tmp_path)
    write_good_full(skills, "alpha", body=CANONICAL_BODY + "\nRun `cargo-audit` first.\n")
    assert _messages(skills, "SK052", root) == []


# --- SK053 / SK054 / SK055: the Pi triage doc --------------------------------------


def test_sk053_flags_a_skill_with_no_triage_row(tmp_path: Path):
    root, skills = _repo(tmp_path)
    write_good_full(skills, "alpha")
    write_good_full(skills, "beta")
    _write_pi(root, ["alpha"])
    assert "no Green/Yellow/Red row" in _messages(skills, "SK053", root)[0]


def test_sk053_reads_rows_that_are_not_backticked(tmp_path: Path):
    """The evals.md grep assumed backticks and so matched nothing, ever."""
    root, skills = _repo(tmp_path)
    write_good_full(skills, "alpha")
    _write_pi(root, ["alpha"])
    assert _messages(skills, "SK053", root) == []


def test_sk054_flags_a_triage_row_for_a_deleted_skill(tmp_path: Path):
    root, skills = _repo(tmp_path)
    write_good_full(skills, "tdd-loop")
    _write_pi(root, ["tdd-loop", "tdd"])
    assert "lists `tdd`, which is not a skill" in _messages(skills, "SK054", root)[0]


def test_sk055_flags_a_heading_count_that_disagrees_with_its_rows(tmp_path: Path):
    root, skills = _repo(tmp_path)
    write_good_full(skills, "alpha")
    _write_pi(root, ["alpha"], green=38)
    assert "heading claims 38 but has 1 rows" in _messages(skills, "SK055", root)[0]


def test_sk055_flags_a_footer_total_that_disagrees(tmp_path: Path):
    root, skills = _repo(tmp_path)
    write_good_full(skills, "alpha")
    write_good_full(skills, "beta")
    _write_pi(root, ["alpha", "beta"], footer=85)
    assert any("footer total is 85 but there are 2 rows" in m
               for m in _messages(skills, "SK055", root))


def test_sk055_silent_when_counts_agree(tmp_path: Path):
    root, skills = _repo(tmp_path)
    write_good_full(skills, "alpha")
    _write_pi(root, ["alpha"])
    assert _messages(skills, "SK055", root) == []


def test_pi_rules_are_silent_without_the_document(tmp_path: Path):
    root, skills = _repo(tmp_path)
    write_good_full(skills, "alpha")
    for rule in ("SK053", "SK054", "SK055"):
        assert _messages(skills, rule, root) == []


# --- SK056 / SK057: README ---------------------------------------------------------


def _write_readme(root: Path, names, *, badge=None, glance=None):
    rows = "\n".join(f"| `{n}` | Does a thing. |" for n in names)
    badge = len(names) if badge is None else badge
    glance = len(names) if glance is None else glance
    (root / "README.md").write_text(
        f"# Toolkit\n\n[![Skills](https://img.shields.io/badge/skills-{badge}-blue)](#skills)\n\n"
        f"## At a glance\n\n| | Count |\n|--|-------|\n"
        f"| Skills (team) | {glance} |\n| Skills (professional) | 0 |\n\n"
        f"## Team Skills\n\n### Suite\n\n| Skill | Description |\n|-------|-------------|\n"
        f"{rows}\n\n"
        f"## Agents\n\n| Agent | Description |\n|-------|-------------|\n"
        f"| `some-agent` | An agent, not a skill. |\n"
    )


def test_sk056_flags_a_skill_missing_from_the_readme(tmp_path: Path):
    root, skills = _repo(tmp_path)
    write_good_full(skills, "alpha")
    write_good_full(skills, "beta")
    _write_readme(root, ["alpha"])
    assert "not listed in any README skill table" in _messages(skills, "SK056", root)[0]


def test_sk056_flags_a_readme_entry_for_a_deleted_skill(tmp_path: Path):
    root, skills = _repo(tmp_path)
    write_good_full(skills, "tdd-loop")
    _write_readme(root, ["tdd-loop", "tdd"])
    assert any("README lists `tdd`" in m for m in _messages(skills, "SK056", root))


def test_sk056_ignores_the_agents_table(tmp_path: Path):
    """Agent tables share the backticked-first-column shape and must not be read as skills."""
    root, skills = _repo(tmp_path)
    write_good_full(skills, "alpha")
    _write_readme(root, ["alpha"])
    assert _messages(skills, "SK056", root) == []


def test_sk056_flags_a_skill_listed_twice(tmp_path: Path):
    root, skills = _repo(tmp_path)
    write_good_full(skills, "alpha")
    _write_readme(root, ["alpha", "alpha"])
    assert any("more than one suite table" in m for m in _messages(skills, "SK056", root))


def test_sk057_flags_a_stale_badge_count(tmp_path: Path):
    root, skills = _repo(tmp_path)
    write_good_full(skills, "alpha")
    _write_readme(root, ["alpha"], badge=94)
    assert "badge claims 94 skills; there are 1" in _messages(skills, "SK057", root)[0]


def test_sk057_flags_a_stale_at_a_glance_count(tmp_path: Path):
    root, skills = _repo(tmp_path)
    write_good_full(skills, "alpha")
    _write_readme(root, ["alpha"], glance=93)
    assert any("at-a-glance claims 93" in m for m in _messages(skills, "SK057", root))


def test_sk057_flags_a_stale_count_in_a_context_file(tmp_path: Path):
    root, skills = _repo(tmp_path)
    write_good_full(skills, "alpha")
    (root / "CLAUDE.md").write_text("A collection of 87 skills and agents.\n")
    messages = _messages(skills, "SK057", root)
    assert any("CLAUDE.md claims 87 skills; there are 1" in m for m in messages)


def test_sk057_reads_the_real_count_rather_than_hardcoding_one(tmp_path: Path):
    root, skills = _repo(tmp_path)
    for i in range(3):
        write_good_full(skills, f"skill-{i}")
    _write_readme(root, [f"skill-{i}" for i in range(3)])
    assert _messages(skills, "SK057", root) == []


# --- SK058 / SK059 -----------------------------------------------------------------


def _write_agents(root: Path, claude, opencode):
    for platform, names in (("claude", claude), ("opencode", opencode)):
        base = root / platform / "agents" / "team"
        base.mkdir(parents=True)
        for name in names:
            (base / f"{name}.md").write_text("agent")


def test_sk058_flags_an_agent_present_only_for_claude(tmp_path: Path):
    root, skills = _repo(tmp_path)
    write_good_full(skills, "alpha")
    _write_agents(root, ["a", "b"], ["a"])
    assert "'b' exists for Claude Code but not OpenCode" in _messages(skills, "SK058", root)[0]


def test_sk058_flags_an_agent_present_only_for_opencode(tmp_path: Path):
    root, skills = _repo(tmp_path)
    write_good_full(skills, "alpha")
    _write_agents(root, ["a"], ["a", "z"])
    assert "'z' exists for OpenCode but not Claude Code" in _messages(skills, "SK058", root)[0]


def test_sk058_silent_when_in_parity(tmp_path: Path):
    root, skills = _repo(tmp_path)
    write_good_full(skills, "alpha")
    _write_agents(root, ["a", "b"], ["b", "a"])
    assert _messages(skills, "SK058", root) == []


def test_sk059_flags_a_diverged_mirror_pair(tmp_path: Path):
    root, skills = _repo(tmp_path)
    write_good_full(skills, "alpha")
    (root / "CLAUDE.md").write_text("# Context\n\nOne version.\n")
    (root / "AGENTS.md").write_text("# Context\n\nA different version.\n")
    assert "mirror pair" in _messages(skills, "SK059", root)[0]


def test_sk059_accepts_identical_files(tmp_path: Path):
    root, skills = _repo(tmp_path)
    write_good_full(skills, "alpha")
    for name in ("CLAUDE.md", "AGENTS.md"):
        (root / name).write_text("# Context\n\nSame bytes.\n")
    assert _messages(skills, "SK059", root) == []
