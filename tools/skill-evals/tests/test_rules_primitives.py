# <AI-Generated START>
"""SK070-SK073 — agents and commands stay in sync with skills/ and with each other."""

from pathlib import Path

from conftest import write_good_full

from skill_evals.lint import lint


def _repo(tmp_path: Path) -> tuple[Path, Path]:
    root = tmp_path / "repo"
    skills = root / "skills"
    skills.mkdir(parents=True)
    write_good_full(skills, "tdd-loop")
    write_good_full(skills, "research-synthesis")
    return root, skills


def _agent(root: Path, name: str, *, claude=(), opencode=(), body=""):
    """Write a Claude/OpenCode agent pair loading the given skills."""
    c_dir, o_dir = root / "claude" / "agents", root / "opencode" / "agents"
    c_dir.mkdir(parents=True, exist_ok=True)
    o_dir.mkdir(parents=True, exist_ok=True)
    listed = "".join(f"  - {s}\n" for s in claude)
    (c_dir / f"{name}.md").write_text(
        f"---\nname: {name}\ndescription: d\nskills:\n{listed}---\n\n# {name}\n\n{body}\n"
    )
    calls = "\n".join(f'| `skill({{ name: "{s}" }})` | When needed |' for s in opencode)
    (o_dir / f"{name}.md").write_text(
        f"---\ndescription: d\nmode: subagent\n---\n\n# {name}\n\n{calls}\n\n{body}\n"
    )


def _command(root: Path, platform: str, name: str, body: str = "Use the tdd-loop skill."):
    base = root / platform / "commands"
    base.mkdir(parents=True, exist_ok=True)
    (base / f"{name}.md").write_text(f"---\ndescription: d\n---\n\n{body}\n")


def _messages(skills, rule, root):
    return [f.message for f in lint(skills, only=[rule], repo_root=root)]


# --- SK070 ---------------------------------------------------------------------------


def test_sk070_flags_a_claude_skills_entry_that_is_not_a_skill(tmp_path: Path):
    root, skills = _repo(tmp_path)
    _agent(root, "tdd-agent", claude=["tdd"], opencode=["tdd-loop"])
    messages = _messages(skills, "SK070", root)
    assert len(messages) == 1
    assert "claude agent 'tdd-agent' loads `tdd`, which is not a skill" in messages[0]
    assert "did you mean 'tdd-loop'?" in messages[0]


def test_sk070_flags_an_opencode_skill_call_that_is_not_a_skill(tmp_path: Path):
    root, skills = _repo(tmp_path)
    _agent(root, "research-agent", claude=["research-synthesis"],
           opencode=["research-synthesis", "rag-pipeline-python"])
    messages = _messages(skills, "SK070", root)
    assert messages == ["opencode agent 'research-agent' loads `rag-pipeline-python`, "
                        "which is not a skill"]


def test_sk070_reads_skills_when_the_description_is_not_strict_yaml(tmp_path: Path):
    """An unquoted `: ` in a description breaks strict YAML; Claude Code still loads it."""
    root, skills = _repo(tmp_path)
    _agent(root, "fed-agent", claude=["tdd-loop"], opencode=["tdd-loop"])
    path = root / "claude" / "agents" / "fed-agent.md"
    path.write_text(path.read_text().replace(
        "description: d", 'description: Reviews code. Trigger phrases: "fed review"'))
    assert _messages(skills, "SK070", root) == []
    assert _messages(skills, "SK071", root) == []


def test_sk070_ignores_a_placeholder_skill_name(tmp_path: Path):
    root, skills = _repo(tmp_path)
    _agent(root, "code-review-agent", claude=["tdd-loop"],
           opencode=["tdd-loop", "<lang>-security-review"])
    assert _messages(skills, "SK070", root) == []


# --- SK071 ---------------------------------------------------------------------------


def test_sk071_flags_an_agent_pair_that_loads_different_skills(tmp_path: Path):
    root, skills = _repo(tmp_path)
    _agent(root, "research-agent", claude=["research-synthesis"],
           opencode=["research-synthesis", "tdd-loop"])
    messages = _messages(skills, "SK071", root)
    assert len(messages) == 1
    assert "'research-agent' loads different skills" in messages[0]
    assert "OpenCode only: tdd-loop" in messages[0]


def test_sk071_silent_when_the_pair_loads_the_same_skills(tmp_path: Path):
    root, skills = _repo(tmp_path)
    _agent(root, "tdd-agent", claude=["tdd-loop", "research-synthesis"],
           opencode=["research-synthesis", "tdd-loop"])
    assert _messages(skills, "SK071", root) == []


# --- SK072 ---------------------------------------------------------------------------


def test_sk072_flags_a_command_present_for_one_runtime_only(tmp_path: Path):
    root, skills = _repo(tmp_path)
    _command(root, "claude", "tdd")
    _command(root, "claude", "research")
    _command(root, "opencode", "tdd")
    assert _messages(skills, "SK072", root) == [
        "command '/research' exists for Claude Code but not OpenCode"
    ]


def test_sk072_silent_when_commands_are_in_parity(tmp_path: Path):
    root, skills = _repo(tmp_path)
    for platform in ("claude", "opencode"):
        _command(root, platform, "tdd")
    assert _messages(skills, "SK072", root) == []


# --- SK073 ---------------------------------------------------------------------------


def _tdd_commands(root: Path):
    for platform in ("claude", "opencode"):
        _command(root, platform, "tdd")


def test_sk073_flags_a_bare_command_name_used_for_a_skill_in_an_agent(tmp_path: Path):
    root, skills = _repo(tmp_path)
    _tdd_commands(root)
    _agent(root, "qrspi-implement", claude=["tdd-loop"], opencode=["tdd-loop"],
           body="Each slice is one cycle; the inner loop is delegated to `tdd`.")
    messages = _messages(skills, "SK073", root)
    assert len(messages) == 2  # once per runtime
    assert "`tdd` is a command, not a skill; closest skill is `tdd-loop`" in messages[0]


def test_sk073_flags_a_bare_command_name_used_for_a_skill_in_a_command(tmp_path: Path):
    root, skills = _repo(tmp_path)
    _tdd_commands(root)
    for platform in ("claude", "opencode"):
        _command(root, platform, "qraspi-implement", body="Inner loop: `tdd`.")
    messages = _messages(skills, "SK073", root)
    assert len(messages) == 2
    assert "command '/qraspi-implement'" in messages[0]


def test_sk073_flags_a_hyphenated_stale_skill_name(tmp_path: Path):
    root, skills = _repo(tmp_path)
    _agent(root, "a", claude=["tdd-loop"], opencode=["tdd-loop"],
           body="Synthesize with `research-synthesizer`.")
    assert "closest is `research-synthesis`" in _messages(skills, "SK073", root)[0]


def test_sk073_ignores_generic_words_and_reference_file_names(tmp_path: Path):
    root, skills = _repo(tmp_path)
    refs = skills / "tdd-loop" / "references"
    refs.mkdir(exist_ok=True)
    (refs / "tdd-loop-archetype.md").write_text("x")
    _agent(root, "a", claude=["tdd-loop"], opencode=["tdd-loop"],
           body="Use the `skill` tool; run `test`; see `tdd-loop-archetype`.")
    assert _messages(skills, "SK073", root) == []


def test_sk073_accepts_skills_agents_and_slash_commands(tmp_path: Path):
    root, skills = _repo(tmp_path)
    _agent(root, "tdd-agent", claude=["tdd-loop"], opencode=["tdd-loop"],
           body="Load `tdd-loop`; hand off to `tdd-agent`; the user may type `/tdd`.")
    assert _messages(skills, "SK073", root) == []


# --- SK074: least privilege for read-only agents (OWASP LLM06 / Agentic ASI02) --------


def _read_only(root: Path, *names: str):
    base = root / "tools" / "skill-evals" / "baselines"
    base.mkdir(parents=True, exist_ok=True)
    listed = "".join(f"  {n}: reviewer\n" for n in names)
    (base / "read-only-agents.yaml").write_text(f"agents:\n{listed}")


def _tooled_agent(root: Path, name: str, *, claude_tools: str | None, opencode_flags: dict):
    c_dir, o_dir = root / "claude" / "agents", root / "opencode" / "agents"
    c_dir.mkdir(parents=True, exist_ok=True)
    o_dir.mkdir(parents=True, exist_ok=True)
    tools_line = f"tools: {claude_tools}\n" if claude_tools is not None else ""
    (c_dir / f"{name}.md").write_text(f"---\nname: {name}\ndescription: d\n{tools_line}---\n")
    flags = "".join(f"  {k}: {str(v).lower()}\n" for k, v in opencode_flags.items())
    (o_dir / f"{name}.md").write_text(f"---\ndescription: d\nmode: subagent\ntools:\n{flags}---\n")


READ_ONLY_FLAGS = {"read": True, "edit": False, "write": False, "bash": True}


def test_sk074_flags_a_read_only_claude_agent_granted_edit_or_write(tmp_path: Path):
    root, skills = _repo(tmp_path)
    _read_only(root, "rev-agent")
    _tooled_agent(root, "rev-agent", claude_tools="Read, Edit, Write, Bash",
                  opencode_flags=READ_ONLY_FLAGS)
    messages = _messages(skills, "SK074", root)
    assert len(messages) == 1
    assert "claude agent 'rev-agent'" in messages[0] and "Edit, Write" in messages[0]


def test_sk074_flags_a_read_only_opencode_agent_with_edit_true(tmp_path: Path):
    root, skills = _repo(tmp_path)
    _read_only(root, "rev-agent")
    _tooled_agent(root, "rev-agent", claude_tools="Read, Bash",
                  opencode_flags={**READ_ONLY_FLAGS, "edit": True})
    messages = _messages(skills, "SK074", root)
    assert len(messages) == 1
    assert "opencode agent 'rev-agent'" in messages[0] and "edit" in messages[0]


def test_sk074_flags_a_read_only_claude_agent_with_no_tools_line(tmp_path: Path):
    """No `tools:` line means the agent inherits every tool, including Edit and Write."""
    root, skills = _repo(tmp_path)
    _read_only(root, "rev-agent")
    _tooled_agent(root, "rev-agent", claude_tools=None, opencode_flags=READ_ONLY_FLAGS)
    assert "inherits every tool" in _messages(skills, "SK074", root)[0]


def test_sk074_accepts_a_read_only_agent_with_read_tools(tmp_path: Path):
    root, skills = _repo(tmp_path)
    _read_only(root, "rev-agent")
    _tooled_agent(root, "rev-agent", claude_tools="Read, Bash, Glob, Grep",
                  opencode_flags=READ_ONLY_FLAGS)
    assert _messages(skills, "SK074", root) == []


def test_sk074_ignores_agents_not_declared_read_only(tmp_path: Path):
    root, skills = _repo(tmp_path)
    _read_only(root, "rev-agent")
    _tooled_agent(root, "builder-agent", claude_tools="Read, Edit, Write, Bash",
                  opencode_flags={**READ_ONLY_FLAGS, "edit": True, "write": True})
    assert _messages(skills, "SK074", root) == []
# <AI-Generated END>
