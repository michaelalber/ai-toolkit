# <AI-Generated START>
"""Guardrails test: the same model in a coding agent, bare vs. the user's real setup (global rules + grounding).

Harnesses: pi, opencode (both bare and guarded), claude (guarded only — bare needs an API key, see plan D5).
Usage: python pi_bench.py [--harness pi|opencode|claude] [--model M] [--tasks t1,t2] [--n 3] [--tag NAME]
Grades with the bake-off's restored original tests. Appends rows to pi-results.jsonl, writes results-<tag>.md.
"""
import argparse
import contextlib
import json
import os
import shlex
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from harness import HERE, TASK_WALL_CAP_S, load_task_config, restore_tests
from sandbox import Sandbox

MODEL = "flint:40b-a2b-qat-int4"
TASKS = ["hard_cs_ledger", "hard_py_jobs", "hard_php_booking"]
EVENTS_DIR = HERE / "pibench-events"
BARE_FLAGS = ["--no-context-files", "--no-extensions", "--no-skills", "--no-mcp"]
# Same for both configs. Needed because the user's AGENTS.md says "Do NOT begin until confirmed",
# which would stall a non-interactive run; and the specs mention the harness's run_tests tool.
PROMPT_SUFFIX = ("\n\nThis is a non-interactive run: context is confirmed, so proceed through all the changes "
                 "without waiting for confirmation. There is no run_tests tool here; run the tests with:\n"
                 "`{cmd}`\nStop when all tests pass.")


DEFAULT_MODEL = {"pi": MODEL, "opencode": MODEL, "claude": "sonnet"}
OLLAMA_V1 = "http://localhost:11434/v1"  # Ollama v1 API base for the bake-off harness
CLAUDE_TOOLS = ["Bash", "Read", "Edit", "Write", "Glob", "Grep"]


def build_cmd(model, guarded, prompt, harness="pi"):
    if harness == "opencode":  # bare vs guarded differs by environment, not flags (see run_env)
        return ["opencode", "run", "--standalone", "--format", "json", "--auto",
                "-m", f"ollama-macmini/{model}", prompt]
    if harness == "claude":  # prompt first: --allowedTools is variadic and would swallow it
        return ["claude", "-p", prompt, "--output-format", "stream-json", "--verbose",
                "--model", model, "--allowedTools", *CLAUDE_TOOLS]
    return ["pi", "-p", "--no-session", "--mode", "json", "--model", f"ollama/{model}",
            *([] if guarded else BARE_FLAGS), prompt]


def configs(harness):
    return (True,) if harness == "claude" else (False, True)


PI_AGENT_SRC = Path.home() / ".pi" / "agent"


def install_sigterm_exit():
    """Turn SIGTERM (e.g. a stopped background task) into SystemExit so context managers restore permissions."""
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(143))


def _pi_bare_agent_dir(scratch, src):
    """Pi has no flag to skip ~/.pi/agent/APPEND_SYSTEM.md, so a bare run gets its own agent dir:
    models.json + settings.json only (packages dropped) — no AGENTS.md, appended prompt, or extensions."""
    agent = Path(scratch) / "pi-agent"
    agent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(Path(src) / "models.json", agent / "models.json")
    settings = json.loads((Path(src) / "settings.json").read_text())
    settings.pop("packages", None)
    (agent / "settings.json").write_text(json.dumps(settings, indent=2))
    return agent


def run_env(harness, guarded, scratch, work, pi_agent_src=PI_AGENT_SRC):
    """Environment for a run. PWD always points at the workdir: OpenCode resolved its project root
    from an inherited PWD and edited the task originals. OpenCode has no flag to skip its global
    AGENTS.md, so a bare run also points XDG_CONFIG_HOME at a minimal config: provider only, no
    rules, skills, plugins or MCP. shortcut: bare also drops the user's permission denies."""
    env = {**os.environ, "PWD": str(work)}
    if harness == "pi" and not guarded:
        return {**env, "PI_CODING_AGENT_DIR": str(_pi_bare_agent_dir(scratch, pi_agent_src))}
    if harness != "opencode" or guarded:
        return env
    cfg_dir = Path(scratch) / "opencode"
    cfg_dir.mkdir(parents=True, exist_ok=True)
    model = {"name": "Flint", "tool_call": True, "reasoning": True,
             "limit": {"context": 131072, "output": 32768}}
    (cfg_dir / "opencode.json").write_text(json.dumps({
        "$schema": "https://opencode.ai/config.json",
        "provider": {"ollama-macmini": {"npm": "@ai-sdk/openai-compatible", "name": "Mac Mini Ollama",
                                        "options": {"baseURL": OLLAMA_V1, "apiKey": "ollama"},
                                        "models": {MODEL: model}}},
    }, indent=2))
    return {**env, "XDG_CONFIG_HOME": str(scratch)}


BUILD_DIRS = {"bin", "obj", "__pycache__", ".pytest_cache", "vendor"}


@contextlib.contextmanager
def read_only_tasks(root):
    """Make task sources read-only for a batch: an OpenCode run with --auto found the originals by
    absolute path (from the test command) and edited them. Build dirs stay writable."""
    # Directories too: OpenCode's edit tool writes a temp file and renames it over the original,
    # which a read-only file in a writable directory does not stop.
    paths = [p for p in Path(root).rglob("*")
             if not BUILD_DIRS & set(p.relative_to(root).parts)]
    paths.append(Path(root))
    modes = {p: p.stat().st_mode for p in paths}
    try:
        for p, m in sorted(modes.items(), key=lambda kv: -len(kv[0].parts)):  # children first
            p.chmod(m & ~0o222)
        yield
    finally:
        for p, m in sorted(modes.items(), key=lambda kv: len(kv[0].parts)):  # parents first
            p.chmod(m)


@contextlib.contextmanager
def hidden_dir(path):
    """Make a directory unlistable and unreadable for a batch: an agent with a shell found the
    reference solutions by searching the bake-off folder (its path leaks via the test command)."""
    path = Path(path)
    mode = path.stat().st_mode
    try:
        path.chmod(0)
        yield
    finally:
        path.chmod(mode)


def make_writable(root):
    """copytree keeps the read-only bits of the originals (files and dirs); the workdir must be writable."""
    for p in [Path(root), *Path(root).rglob("*")]:
        p.chmod(p.stat().st_mode | 0o200)


def outside_refs(out):
    """How often a run's events name the original tasks/ dir (escape attempts, blocked or not)."""
    return out.count(str(HERE / "tasks") + "/")


def reference_refs(out):
    """How often a run's events name the reference solutions — any hit makes the run suspect."""
    return out.count(str(HERE / "reference") + "/")


def tasks_digest(root):
    """Fingerprint of task sources (build output excluded). A run must never change it."""
    import hashlib
    h = hashlib.sha256()
    for p in sorted(Path(root).rglob("*")):
        if p.is_file() and not BUILD_DIRS & set(p.relative_to(root).parts):
            h.update(str(p.relative_to(root)).encode() + b"\0" + p.read_bytes())
    return h.hexdigest()


def build_prompt(spec, test_cmd):
    return spec + PROMPT_SUFFIX.format(cmd=shlex.join(test_cmd))


def parse_events(lines):
    """Turns, tool calls and grounding calls (CLI via bash, or a grounded-* extension tool) from Pi's JSON events."""
    s = {"turns": 0, "tool_calls": 0, "grounding_calls": 0, "last_stop": None}
    for line in lines:
        try:
            e = json.loads(line)
        except ValueError:
            continue
        msg = e.get("message") or {}
        if e.get("type") == "message_end" and msg.get("role") == "assistant":
            s["last_stop"] = msg.get("stopReason")
        elif e.get("type") == "turn_start":
            s["turns"] += 1
        elif e.get("type") == "tool_execution_start":
            s["tool_calls"] += 1
            name = e.get("toolName", "")
            cmd = (e.get("args") or {}).get("command", "")
            if name.startswith("grounded") or (name == "bash" and "grounded-code-mcp" in cmd):
                s["grounding_calls"] += 1
    return s


def events_file(tag, task, config, i, harness="pi"):
    prefix = "" if harness == "pi" else f"{harness}-"  # pi keeps its existing file names
    return EVENTS_DIR / f"{prefix}{tag}-{task}-{config}-{i}.jsonl"


def _is_grounding(tool_name, command):
    return "grounded" in tool_name or "grounded-code-mcp" in (command or "")


def parse_opencode(lines):
    """Steps (turns), tool calls, grounding calls and the last step's finish reason from `opencode run --format json`."""
    s = {"turns": 0, "tool_calls": 0, "grounding_calls": 0, "last_stop": None}
    for line in lines:
        try:
            e = json.loads(line)
        except ValueError:
            continue
        part = e.get("part") or {}
        if e.get("type") == "step_start":
            s["turns"] += 1
        elif e.get("type") == "tool_use":
            s["tool_calls"] += 1
            cmd = ((part.get("state") or {}).get("input") or {}).get("command", "")
            s["grounding_calls"] += _is_grounding(part.get("tool", ""), cmd)
        elif e.get("type") == "step_finish":
            s["last_stop"] = part.get("reason")
    return s


def parse_claude(lines):
    """Tool calls and grounding from assistant tool_use blocks; turns and stop from the final result event."""
    s = {"turns": 0, "tool_calls": 0, "grounding_calls": 0, "last_stop": None}
    for line in lines:
        try:
            e = json.loads(line)
        except ValueError:
            continue
        if e.get("type") == "assistant":
            for block in (e.get("message") or {}).get("content") or []:
                if block.get("type") == "tool_use":
                    s["tool_calls"] += 1
                    s["grounding_calls"] += _is_grounding(block.get("name", ""),
                                                          (block.get("input") or {}).get("command"))
        elif e.get("type") == "result":
            s["turns"] = e.get("num_turns", 0)
            s["last_stop"] = e.get("stop_reason") if e.get("subtype") == "success" else e.get("subtype")
    return s


PARSERS = {"pi": parse_events, "opencode": parse_opencode, "claude": parse_claude}


def run_one(model, task, guarded, tag, i=0, harness="pi"):
    src = HERE / "tasks" / task
    work = Path(tempfile.mkdtemp(prefix=f"pibench-{task}-"))
    scratch = Path(tempfile.mkdtemp(prefix="pibench-cfg-"))  # outside the workdir the model can see
    shutil.copytree(src, work, dirs_exist_ok=True)
    make_writable(work)
    cfg = load_task_config(src)
    prompt = build_prompt((work / "spec.md").read_text(), cfg["test_cmd"])
    row = {"round": tag, "harness": harness, "model": model, "task": task,
           "config": "guarded" if guarded else "bare", "error": None}
    t0 = time.time()
    try:
        out = subprocess.run(build_cmd(model, guarded, prompt, harness), cwd=work, capture_output=True,
                             text=True, timeout=TASK_WALL_CAP_S,
                             env=run_env(harness, guarded, scratch, work)).stdout
    except subprocess.TimeoutExpired as e:
        out = (e.stdout or b"").decode() if isinstance(e.stdout, bytes) else (e.stdout or "")
        row["error"] = "timeout"
    row["wall_s"] = round(time.time() - t0, 1)
    EVENTS_DIR.mkdir(exist_ok=True)
    events_file(tag, task, row["config"], i, harness).write_text(out)  # kept for diagnosing early stops
    row.update(PARSERS[harness](out.splitlines()))
    row["outside_refs"] = outside_refs(out)
    row["reference_refs"] = reference_refs(out)
    row["tests_tampered"] = restore_tests(src, work, cfg["test_globs"])
    row["passed"] = Sandbox(work, cfg["test_cmd"], cfg["test_timeout"]).run_tests()[0]
    shutil.rmtree(work, ignore_errors=True)
    shutil.rmtree(scratch, ignore_errors=True)
    return row


def summarize(rows):
    out = ["| harness | config | task | pass | turns | tool calls | grounding calls | last stop | wall s | tampered | error |",
           "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        out.append(f"| {r.get('harness', 'pi')} | {r['config']} | {r['task']} | {'PASS' if r['passed'] else 'FAIL'} | "
                   f"{r['turns']} | {r['tool_calls']} | {r['grounding_calls']} | {r.get('last_stop') or ''} | "
                   f"{r['wall_s']} | {'YES' if r['tests_tampered'] else ''} | {r['error'] or ''} |")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--harness", default="pi", choices=["pi", "opencode", "claude"])
    ap.add_argument("--model", default=None)
    ap.add_argument("--tasks", default=",".join(TASKS))
    ap.add_argument("--n", type=int, default=3)
    ap.add_argument("--tag", default="guardrails")
    a = ap.parse_args()
    if a.harness not in PARSERS:
        raise SystemExit(f"no event parser for {a.harness} yet (needs a captured sample)")
    model = a.model or DEFAULT_MODEL[a.harness]
    install_sigterm_exit()
    rows = []
    with read_only_tasks(HERE / "tasks"), hidden_dir(HERE / "reference"):  # digest check below = backstop
        for i in range(a.n):
            for task in a.tasks.split(","):
                order = configs(a.harness) if i % 2 == 0 else tuple(reversed(configs(a.harness)))
                for guarded in order:  # alternate order to spread drift
                    before = tasks_digest(HERE / "tasks")
                    row = run_one(model, task, guarded, a.tag, i, a.harness)
                    if tasks_digest(HERE / "tasks") != before:  # the agent escaped its workdir
                        raise SystemExit(f"ABORT: task originals changed during {row}; restore before rerunning")
                    rows.append(row)
                    with open(HERE / "pi-results.jsonl", "a") as f:
                        f.write(json.dumps(row) + "\n")
                    print(row, flush=True)
    (HERE / f"results-{a.tag}.md").write_text(summarize(rows) + "\n")


if __name__ == "__main__":
    main()
# <AI-Generated END>
