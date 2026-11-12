# <AI-Generated START>
"""SK060-SK065 — the three global instruction files (Claude Code, OpenCode, Pi).

Each test builds a tiny repo with only the files the rule reads, so a red test shows the
exact deviation that trips it.
"""

from pathlib import Path

from skill_evals.lint import lint

CORE = (
    "<!-- core:start -->\n## Mode\n\n- Interactive: ask. Non-interactive: proceed.\n"
    "<!-- core:end -->\n"
)
GLOBALS = {
    "claude": "claude/global/CLAUDE.md",
    "opencode": "opencode/global/AGENTS.md",
    "pi": "pi/global/AGENTS.md",
}


def _repo(tmp_path: Path, files: dict[str, str] | None = None) -> tuple[Path, Path]:
    root = tmp_path / "repo"
    skills = root / "skills"
    skills.mkdir(parents=True)
    for rel, text in (files or {}).items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
    return root, skills


def _globals(core: str = CORE, **overrides: str) -> dict[str, str]:
    files = {path: f"# {name}\n\n{core}\n## Harness\n\nTool-specific notes.\n"
             for name, path in GLOBALS.items()}
    files.update({GLOBALS[k]: v for k, v in overrides.items()})
    return files


def _messages(tmp_path, rule, files, **kw):
    root, skills = _repo(tmp_path, files)
    return [f.message for f in lint(skills, only=[rule], repo_root=root, **kw)]


# --- no globals at all: every rule stays silent (fixture repos for other rules) ------


def test_global_rules_are_silent_when_no_global_files_exist(tmp_path: Path):
    for rule in ("SK060", "SK061", "SK062", "SK063", "SK064", "SK065"):
        assert _messages(tmp_path / rule, rule, {}) == [], rule


# --- SK060: exactly one CORE block ----------------------------------------------------


def test_sk060_accepts_one_core_block_per_global(tmp_path: Path):
    assert _messages(tmp_path, "SK060", _globals()) == []


def test_sk060_flags_a_global_without_core_markers(tmp_path: Path):
    files = _globals(pi="# pi\n\nNo markers here.\n")
    messages = _messages(tmp_path, "SK060", files)
    assert len(messages) == 1
    assert "pi/global/AGENTS.md" in messages[0] and "core" in messages[0].lower()


def test_sk060_flags_two_core_blocks(tmp_path: Path):
    files = _globals(opencode=f"# oc\n\n{CORE}\n{CORE}")
    assert len(_messages(tmp_path, "SK060", files)) == 1


# --- SK061: CORE identical across globals --------------------------------------------


def test_sk061_accepts_identical_cores(tmp_path: Path):
    assert _messages(tmp_path, "SK061", _globals()) == []


def test_sk061_flags_a_drifted_core_and_names_the_file(tmp_path: Path):
    drifted = CORE.replace("proceed", "proceed carefully")
    files = _globals(claude=f"# claude\n\n{drifted}")
    messages = _messages(tmp_path, "SK061", files)
    assert len(messages) == 1
    assert "claude/global/CLAUDE.md" in messages[0]


# --- SK062: size budget ---------------------------------------------------------------


def test_sk062_accepts_files_within_budget(tmp_path: Path):
    assert _messages(tmp_path, "SK062", _globals()) == []


def test_sk062_flags_a_pi_global_over_its_budget(tmp_path: Path):
    files = _globals(pi=f"# pi\n\n{CORE}\n" + "x" * 5000)
    messages = _messages(tmp_path, "SK062", files)
    assert len(messages) == 1
    assert "pi/global/AGENTS.md" in messages[0] and "budget" in messages[0]


# --- SK063: no unconditional confirmation gate ----------------------------------------


def test_sk063_accepts_a_gate_scoped_to_interactive_mode(tmp_path: Path):
    files = _globals(pi=f"# pi\n\n{CORE}\n- **Non-interactive**: do not wait for confirmation.\n")
    assert _messages(tmp_path, "SK063", files) == []


def test_sk063_flags_an_unconditional_do_not_begin_gate(tmp_path: Path):
    files = _globals(
        opencode=f"# oc\n\n{CORE}\n4. **Do NOT begin work until context is confirmed**\n"
    )
    messages = _messages(tmp_path, "SK063", files)
    assert len(messages) == 1
    assert "opencode/global/AGENTS.md" in messages[0]


def test_sk063_ignores_until_confirmed_that_is_not_about_starting_work(tmp_path: Path):
    files = _globals(pi=f"# pi\n\n{CORE}\nAssume recalled signatures are wrong until confirmed.\n")
    assert _messages(tmp_path, "SK063", files) == []


def test_sk063_ignores_do_not_start_without_a_confirmation(tmp_path: Path):
    files = _globals(
        claude=f"# c\n\n{CORE}\nDo not start a task whose acceptance criteria cannot be stated.\n"
    )
    assert _messages(tmp_path, "SK063", files) == []


def test_sk063_flags_finish_show_stop_until_confirmed(tmp_path: Path):
    files = _globals(
        claude=f"# c\n\n{CORE}\nDo not begin a second change until the first is confirmed.\n"
    )
    assert len(_messages(tmp_path, "SK063", files)) == 1


# --- SK064: no personal strings in the public global templates -------------------------


def test_sk064_flags_a_private_lan_address(tmp_path: Path):
    files = _globals()
    files["opencode/global/opencode.json"] = '{"baseURL": "http://192.168.1.20:11434/v1"}'
    messages = _messages(tmp_path, "SK064", files)
    assert len(messages) == 1 and "192.168.1.20" in messages[0]


def test_sk064_accepts_a_placeholder_host(tmp_path: Path):
    files = _globals()
    files["pi/global/models.json"] = '{"baseUrl": "http://YOUR-OLLAMA-HOST:11434/v1"}'
    assert _messages(tmp_path, "SK064", files) == []


def test_sk064_flags_terms_from_a_private_blocklist(tmp_path: Path):
    blocklist = tmp_path / "blocklist.txt"
    blocklist.write_text("# private terms, one per line\nAcmeCorp\n")
    files = _globals(pi=f"# pi\n\n{CORE}\nUsed at AcmeCorp only.\n")
    messages = _messages(tmp_path, "SK064", files, private_blocklist=blocklist)
    assert len(messages) == 1 and "pi/global/AGENTS.md" in messages[0]


# --- SK065: referenced global/ paths exist --------------------------------------------


def test_sk065_flags_a_reference_to_a_missing_global_file(tmp_path: Path):
    files = _globals()
    files["pi/global/README.md"] = "Copy `pi/global/router-config.json.example` to enable it.\n"
    messages = _messages(tmp_path, "SK065", files)
    assert len(messages) == 1 and "pi/global/router-config.json.example" in messages[0]


def test_sk065_accepts_references_that_resolve(tmp_path: Path):
    files = _globals()
    files["pi/global/Modelfile-flint-agent"] = "FROM flint\n"
    files["scripts/install-pi.sh"] = (
        "ollama create flint-agent -f pi/global/Modelfile-flint-agent\n"
    )
    assert _messages(tmp_path, "SK065", files) == []
# <AI-Generated END>
