# <AI-Generated START>
import json
from pathlib import Path

import pi_bench


def test_bare_cmd_disables_context_files_extensions_skills_and_mcp():
    # Arrange / Act
    cmd = pi_bench.build_cmd("flint:40b-a2b-qat-int4", guarded=False, prompt="do it")
    # Assert
    for flag in ("--no-context-files", "--no-extensions", "--no-skills", "--no-mcp"):
        assert flag in cmd
    assert cmd[-1] == "do it"


def test_guarded_cmd_keeps_the_users_real_setup():
    cmd = pi_bench.build_cmd("flint:40b-a2b-qat-int4", guarded=True, prompt="do it")
    for flag in ("--no-context-files", "--no-extensions", "--no-skills", "--no-mcp"):
        assert flag not in cmd


def test_both_cmds_are_noninteractive_json_ephemeral_on_the_local_provider():
    for guarded in (False, True):
        cmd = pi_bench.build_cmd("m:tag", guarded=guarded, prompt="p")
        assert cmd[0] == "pi"
        assert "-p" in cmd and "--no-session" in cmd
        assert cmd[cmd.index("--mode") + 1] == "json"
        assert cmd[cmd.index("--model") + 1] == "ollama/m:tag"


def test_prompt_gives_the_real_test_command_and_says_proceed_without_confirmation():
    p = pi_bench.build_prompt("SPEC TEXT", ["dotnet", "test", "Ledger.Tests"])
    assert p.startswith("SPEC TEXT")
    assert "dotnet test Ledger.Tests" in p
    assert "without waiting for confirmation" in p


def _ev(**kw):
    return json.dumps(kw)


def test_parse_events_counts_turns_tool_calls_and_grounding_calls():
    # Arrange
    lines = [
        _ev(type="turn_start"),
        _ev(type="tool_execution_start", toolName="bash", args={"command": "grounded-code-mcp search \"x\" --collection dotnet --json"}),
        _ev(type="tool_execution_start", toolName="read", args={"path": "a.cs"}),
        _ev(type="turn_start"),
        _ev(type="tool_execution_start", toolName="grounded_search_knowledge", args={}),
        "not json at all",
        _ev(type="tool_execution_start", toolName="bash", args={"command": "dotnet test"}),
    ]
    # Act
    s = pi_bench.parse_events(lines)
    # Assert
    assert s == {"turns": 2, "tool_calls": 4, "grounding_calls": 2, "last_stop": None}


def test_parse_events_records_the_last_message_stop_reason():
    lines = [_ev(type="message_end", message={"role": "assistant", "stopReason": "toolUse"}),
             _ev(type="message_end", message={"role": "assistant", "stopReason": "length"})]
    assert pi_bench.parse_events(lines)["last_stop"] == "length"


def test_events_file_is_unique_per_run_and_under_the_events_dir():
    a = pi_bench.events_file("guardrails2", "hard_cs_ledger", "bare", 0)
    b = pi_bench.events_file("guardrails2", "hard_cs_ledger", "guarded", 0)
    c = pi_bench.events_file("guardrails2", "hard_cs_ledger", "bare", 1)
    assert len({a, b, c}) == 3
    assert a.parent == pi_bench.EVENTS_DIR and a.suffix == ".jsonl"


def test_opencode_cmd_is_standalone_json_auto_on_the_mini_provider():
    cmd = pi_bench.build_cmd("flint:40b-a2b-qat-int4", guarded=True, prompt="p", harness="opencode")
    assert cmd[:2] == ["opencode", "run"]
    assert "--standalone" in cmd and "--auto" in cmd
    assert cmd[cmd.index("--format") + 1] == "json"
    assert cmd[cmd.index("-m") + 1] == "ollama-macmini/flint:40b-a2b-qat-int4"
    assert cmd[-1] == "p"


def test_claude_cmd_puts_the_prompt_before_the_variadic_tool_list():
    cmd = pi_bench.build_cmd("sonnet", guarded=True, prompt="do it", harness="claude")
    assert cmd[:3] == ["claude", "-p", "do it"]
    assert cmd[cmd.index("--output-format") + 1] == "stream-json"
    assert cmd[cmd.index("--model") + 1] == "sonnet"
    assert "Bash" in cmd[cmd.index("--allowedTools") + 1:]


def test_claude_runs_guarded_only_and_the_others_run_both():
    assert pi_bench.configs("claude") == (True,)
    assert set(pi_bench.configs("pi")) == {False, True}
    assert set(pi_bench.configs("opencode")) == {False, True}


def test_every_run_env_sets_pwd_to_the_workdir(tmp_path):
    # OpenCode resolved its project root from an inherited PWD and edited the task originals.
    for harness in ("pi", "opencode", "claude"):
        for guarded in (False, True):
            env = pi_bench.run_env(harness, guarded, scratch=tmp_path / "s", work=tmp_path / "w")
            assert env["PWD"] == str(tmp_path / "w"), (harness, guarded)


def test_tasks_digest_changes_when_a_task_file_changes(tmp_path):
    # Arrange
    (tmp_path / "t1").mkdir()
    f = tmp_path / "t1" / "Money.cs"
    f.write_text("stub")
    (tmp_path / "t1" / "obj").mkdir()
    before = pi_bench.tasks_digest(tmp_path)
    # Act: build output must not count, a source edit must
    (tmp_path / "t1" / "obj" / "x.dll").write_text("build output")
    unchanged = pi_bench.tasks_digest(tmp_path)
    f.write_text("implemented")
    # Assert
    assert unchanged == before
    assert pi_bench.tasks_digest(tmp_path) != before


def test_read_only_tasks_blocks_writes_to_sources_and_restores_them(tmp_path):
    # Arrange — an agent found the originals by absolute path and edited them
    src = tmp_path / "t1" / "Money.cs"
    src.parent.mkdir()
    src.write_text("stub")
    (tmp_path / "t1" / "obj").mkdir()
    build = tmp_path / "t1" / "obj" / "x.dll"
    build.write_text("b")
    # Act / Assert — sources are read-only inside the block, writable again after
    with pi_bench.read_only_tasks(tmp_path):
        try:
            src.write_text("escaped")
            wrote = True
        except PermissionError:
            wrote = False
        assert not wrote
        build.write_text("build output still writable")
    src.write_text("writable again")
    assert src.read_text() == "writable again"


def test_read_only_tasks_also_blocks_replace_by_rename(tmp_path):
    # OpenCode's edit tool writes a new file and renames it over the original — a read-only
    # file in a writable directory does not stop that.
    src = tmp_path / "t1" / "graph.py"
    src.parent.mkdir()
    src.write_text("original")
    with pi_bench.read_only_tasks(tmp_path):
        try:
            tmp = tmp_path / "t1" / ".graph.py.tmp"
            tmp.write_text("escaped")
            tmp.replace(src)
            replaced = True
        except PermissionError:
            replaced = False
        assert not replaced
    assert src.read_text() == "original"
    (tmp_path / "t1" / "new.py").write_text("dirs writable again")


def test_hidden_dir_cannot_be_listed_or_read_inside_the_block_and_is_restored(tmp_path):
    # An agent found the reference solutions by searching the bake-off folder and cat'ed them.
    ref = tmp_path / "reference"
    (ref / "t1").mkdir(parents=True)
    (ref / "t1" / "graph.py").write_text("solution")
    with pi_bench.hidden_dir(ref):
        try:
            list(ref.iterdir())
            listed = True
        except PermissionError:
            listed = False
        assert not listed
    assert (ref / "t1" / "graph.py").read_text() == "solution"


def test_workdir_copied_from_read_only_tasks_accepts_new_files(tmp_path):
    src = tmp_path / "tasks" / "t1"
    (src / "jobs").mkdir(parents=True)
    (src / "jobs" / "graph.py").write_text("x")
    with pi_bench.read_only_tasks(tmp_path / "tasks"):
        work = tmp_path / "work"
        pi_bench.shutil.copytree(src, work)
        pi_bench.make_writable(work)
        (work / "jobs" / "new_helper.py").write_text("agent may add files")
        (work / "jobs" / "graph.py").write_text("and edit them")


def test_make_writable_undoes_copied_read_only_bits(tmp_path):
    f = tmp_path / "a" / "x.php"
    f.parent.mkdir()
    f.write_text("x")
    f.chmod(0o444)
    pi_bench.make_writable(tmp_path)
    f.write_text("edited")
    assert f.read_text() == "edited"


def test_outside_refs_counts_references_to_the_original_tasks_dir():
    out = f'{{"path":"{pi_bench.HERE}/tasks/hard_php_booking/src/A.php"}}\n{{"path":"/tmp/w/src/A.php"}}'
    assert pi_bench.outside_refs(out) == 1


def test_reference_refs_counts_references_to_the_reference_solutions():
    out = f'cat {pi_bench.HERE}/reference/hard_py_jobs/jobs/graph.py; cat /tmp/w/jobs/graph.py'
    assert pi_bench.reference_refs(out) == 1


def test_opencode_bare_env_points_at_a_config_without_agents_md(tmp_path):
    # Arrange / Act
    env = pi_bench.run_env("opencode", guarded=False, scratch=tmp_path, work=tmp_path / "w")
    # Assert
    cfg_dir = tmp_path / "opencode"
    assert env["XDG_CONFIG_HOME"] == str(tmp_path)
    assert not (cfg_dir / "AGENTS.md").exists()
    cfg = json.loads((cfg_dir / "opencode.json").read_text())
    assert "flint:40b-a2b-qat-int4" in cfg["provider"]["ollama-macmini"]["models"]
    assert "mcp" not in cfg and "plugin" not in cfg


def test_guarded_runs_keep_the_users_config(tmp_path):
    for harness in ("opencode", "pi", "claude"):
        env = pi_bench.run_env(harness, True, scratch=tmp_path, work=tmp_path / "w")
        assert env.get("XDG_CONFIG_HOME") == pi_bench.os.environ.get("XDG_CONFIG_HOME")
        assert env.get("PI_CODING_AGENT_DIR") == pi_bench.os.environ.get("PI_CODING_AGENT_DIR")
    assert list(tmp_path.iterdir()) == []


def test_pi_bare_env_uses_an_agent_dir_without_rules_or_appended_prompt(tmp_path):
    # --no-context-files does not skip ~/.pi/agent/APPEND_SYSTEM.md; a separate agent dir does.
    src = tmp_path / "real-agent"
    src.mkdir()
    (src / "models.json").write_text('{"providers": {}}')
    (src / "settings.json").write_text('{"defaultModel": "m", "packages": ["git:x/ponytail"]}')
    (src / "AGENTS.md").write_text("rules")
    (src / "APPEND_SYSTEM.md").write_text("personal")
    # Act
    env = pi_bench.run_env("pi", False, scratch=tmp_path / "s", work=tmp_path / "w", pi_agent_src=src)
    # Assert
    agent = Path(env["PI_CODING_AGENT_DIR"])
    assert sorted(p.name for p in agent.iterdir()) == ["models.json", "settings.json"]
    settings = json.loads((agent / "settings.json").read_text())
    assert settings["defaultModel"] == "m" and "packages" not in settings


def test_sigterm_still_restores_permissions(tmp_path):
    f = tmp_path / "t1" / "a.py"
    f.parent.mkdir()
    f.write_text("x")
    pi_bench.install_sigterm_exit()
    try:
        with pi_bench.read_only_tasks(tmp_path):
            pi_bench.os.kill(pi_bench.os.getpid(), pi_bench.signal.SIGTERM)
    except SystemExit:
        pass
    f.write_text("writable after SIGTERM")


def test_events_file_includes_the_harness():
    assert "opencode" in pi_bench.events_file("g", "t", "bare", 0, harness="opencode").name


# Shapes copied from a real `opencode run --format json` capture (2026-11-09), trimmed.
def _oc(type_, **part):
    return json.dumps({"type": type_, "sessionID": "s", "part": part})


def test_parse_opencode_counts_steps_tools_grounding_and_last_stop_reason():
    lines = [
        _oc("step_start", type="step-start"),
        _oc("tool_use", type="tool", tool="shell", state={"status": "completed", "input": {"command": "ls"}}),
        _oc("tool_use", type="tool", tool="grounded-code-mcp_search_knowledge",
            state={"status": "completed", "input": {"query": "xunit theory"}}),
        _oc("step_finish", type="step-finish", reason="tool-calls"),
        _oc("step_start", type="step-start"),
        _oc("tool_use", type="tool", tool="shell",
            state={"status": "completed", "input": {"command": "grounded-code-mcp search \"x\" --json"}}),
        _oc("text", type="text", text="done"),
        _oc("step_finish", type="step-finish", reason="stop"),
        "not json",
    ]
    assert pi_bench.parse_opencode(lines) == {
        "turns": 2, "tool_calls": 3, "grounding_calls": 2, "last_stop": "stop"}


def test_parse_opencode_reports_a_length_stop():
    lines = [_oc("step_start", type="step-start"), _oc("step_finish", type="step-finish", reason="length")]
    assert pi_bench.parse_opencode(lines)["last_stop"] == "length"


def test_parse_opencode_on_the_real_capture():
    lines = (Path(__file__).parent / "fixtures" / "opencode-smoke.jsonl").read_text().splitlines()
    assert pi_bench.parse_opencode(lines) == {
        "turns": 2, "tool_calls": 1, "grounding_calls": 0, "last_stop": "stop"}


def test_opencode_has_a_parser():
    assert "opencode" in pi_bench.PARSERS


# Shapes from a real `claude -p --output-format stream-json --verbose` capture (2026-11-09), trimmed.
def _cc_tool(name, **inp):
    return json.dumps({"type": "assistant", "message": {"role": "assistant", "content": [
        {"type": "tool_use", "id": "t", "name": name, "input": inp}]}})


def _cc_result(**kw):
    return json.dumps({"type": "result", "subtype": "success", "is_error": False,
                       "num_turns": 3, "stop_reason": "end_turn", **kw})


def test_parse_claude_counts_tool_uses_grounding_and_reads_turns_from_result():
    lines = [
        json.dumps({"type": "system", "subtype": "init"}),
        _cc_tool("Bash", command="ls"),
        _cc_tool("mcp__grounded-code-mcp__search_knowledge", query="xunit", collection="dotnet"),
        json.dumps({"type": "user", "message": {"role": "user", "content": [{"type": "tool_result"}]}}),
        _cc_tool("Bash", command="grounded-code-mcp search x --json"),
        json.dumps({"type": "assistant", "message": {"content": [{"type": "text", "text": "done"}]}}),
        _cc_result(),
    ]
    assert pi_bench.parse_claude(lines) == {
        "turns": 3, "tool_calls": 3, "grounding_calls": 2, "last_stop": "end_turn"}


def test_parse_claude_reports_a_failed_result_subtype_as_the_stop():
    lines = [_cc_result(subtype="error_max_turns", is_error=True, stop_reason=None)]
    assert pi_bench.parse_claude(lines)["last_stop"] == "error_max_turns"


def test_parse_claude_without_a_result_event_still_counts():
    assert pi_bench.parse_claude([_cc_tool("Read", file_path="a.py")]) == {
        "turns": 0, "tool_calls": 1, "grounding_calls": 0, "last_stop": None}


def test_every_harness_has_a_parser():
    assert set(pi_bench.PARSERS) == {"pi", "opencode", "claude"}


def test_parse_events_on_empty_output_is_all_zero():
    assert pi_bench.parse_events([]) == {"turns": 0, "tool_calls": 0, "grounding_calls": 0, "last_stop": None}
# <AI-Generated END>
