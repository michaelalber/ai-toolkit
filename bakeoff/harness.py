# <AI-Generated START>
"""Bake-off: each model x task in a tool loop against Ollama, one model loaded at a time.

Usage: python harness.py [--host URL] [--models m1,m2] [--tasks t1,t2] [--tag NAME]
Appends rows to results.jsonl and writes results-<tag>.md (summary table).
"""
import argparse
import json
import os
import shutil
import tempfile
import time
import urllib.request
from pathlib import Path

from sandbox import PYTEST_CMD, Sandbox

HERE = Path(__file__).parent
MODELS = [
    "flint:40b-a2b-gguf-nvfp4",
    "devstral-small-2:latest",
    "muse-glimmer:30b-mlx",
    "gpt-oss:20b",
    "laguna-xs-2.1:nvfp4",
    "gemma4:26b-nvfp4",
    "gemma4:31b-nvfp4",
    "gemma4:26b-mxfp8",
    "granite4.2:30b-q5_K_M",
    "nemotron-3.5-lightning:30b-mlx",
    "nemotron-3.5-bolt:e4b-mlx-bf16",
]
TASKS = ["hard_debug", "hard_refactor", "hard_spec", "hard_cs_ledger", "hard_py_jobs", "hard_php_booking"]
MAX_TURNS = 30
TASK_WALL_CAP_S = 900
NUM_CTX = 32768  # 48GB M4 Pro, iogpu.wired_limit_mb=40960: headroom beside the largest model
SYSTEM = "You are a coding agent. Use the tools to read files, edit them, and run tests. Stop calling tools when all tests pass."


def _tool(name, desc, props=None):
    return {"type": "function", "function": {"name": name, "description": desc, "parameters": {
        "type": "object", "properties": props or {}, "required": list(props or {})}}}


TOOLS = [
    _tool("list_files", "List files in the workdir"),
    _tool("read_file", "Read a file", {"path": {"type": "string"}}),
    _tool("write_file", "Create/overwrite a file", {"path": {"type": "string"}, "content": {"type": "string"}}),
    _tool("run_tests", "Run the test suite in the workdir"),
]


def load_task_config(task_dir):
    """Per-task test command, protected test-file globs and timeout from optional task.json; defaults to pytest.
    `{bakeoff}` in test_cmd expands to this directory, so task.json never hardcodes a home path."""
    cfg = {"test_cmd": PYTEST_CMD, "test_globs": ["test_*.py"], "test_timeout": 60}
    p = Path(task_dir) / "task.json"
    if p.exists():
        cfg.update(json.loads(p.read_text()))
    cfg["test_cmd"] = [a.replace("{bakeoff}", str(HERE)) for a in cfg["test_cmd"]]
    return cfg


def build_options(modelfile_defaults):
    """Request options. Empty when the model's own Modelfile params (e.g. an -agent variant) are under test."""
    return {} if modelfile_defaults else {"num_ctx": NUM_CTX, "temperature": 0}


def restore_tests(src, work, globs=("test_*.py",)):
    """Reset every protected test file in work to the task original. True if any was edited or deleted."""
    tampered = False
    for t in (f for g in globs for f in Path(src).rglob(g)):
        dst = Path(work) / t.relative_to(src)
        if not dst.exists() or dst.read_bytes() != t.read_bytes():
            tampered = True
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(t, dst)
    return tampered


def auth_headers(env_var):
    """Bearer header from an env var (Ollama Cloud). The key is never printed or logged."""
    if not env_var:
        return {}
    key = os.environ.get(env_var)
    if not key:
        raise SystemExit(f"{env_var} is not set")
    return {"Authorization": f"Bearer {key}"}


def get(host, path, timeout=10):
    return json.load(urllib.request.urlopen(host + path, timeout=timeout))


def post(host, path, body, timeout=600, headers=None):
    req = urllib.request.Request(host + path, json.dumps(body).encode(),
                                 {"Content-Type": "application/json", **(headers or {})})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def loaded(host):
    return [m["name"] for m in get(host, "/api/ps").get("models", [])]


def loaded_gb(host):
    return sum(m.get("size", 0) for m in get(host, "/api/ps").get("models", [])) / 1e9


def unload(host, model):
    post(host, "/api/generate", {"model": model, "keep_alive": 0}, timeout=120)


def run_one(host, model, task, tag, modelfile_defaults=False, headers=None):
    """headers set = remote/cloud host: auth is sent and local memory probing (/api/ps) is skipped."""
    src = HERE / "tasks" / task
    work = Path(tempfile.mkdtemp(prefix=f"bake-{task}-"))
    shutil.copytree(src, work, dirs_exist_ok=True)
    cfg = load_task_config(src)
    sb = Sandbox(work, cfg["test_cmd"], cfg["test_timeout"])
    msgs = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": (work / "spec.md").read_text()}]
    row = {"round": tag, "model": model, "task": task, "turns": 0, "tool_calls": 0, "tool_errors": 0,
           "eval_tokens": 0, "eval_ns": 0, "prompt_tokens": 0, "prompt_ns": 0, "mem_gb": 0.0, "error": None}
    t0 = time.time()
    try:
        while row["turns"] < MAX_TURNS and time.time() - t0 < TASK_WALL_CAP_S:
            r = post(host, "/api/chat", {"model": model, "messages": msgs, "tools": TOOLS, "stream": False,
                                        "options": build_options(modelfile_defaults)}, headers=headers)
            row["turns"] += 1
            row["eval_tokens"] += r.get("eval_count", 0)
            row["eval_ns"] += r.get("eval_duration", 0)
            row["prompt_tokens"] += r.get("prompt_eval_count", 0)
            row["prompt_ns"] += r.get("prompt_eval_duration", 0)
            if not headers:
                row["mem_gb"] = max(row["mem_gb"], round(loaded_gb(host), 1))  # peak across turns
            msg = r["message"]
            msgs.append(msg)
            calls = msg.get("tool_calls") or []
            if not calls:
                break
            for c in calls:
                fn = c["function"]
                text, err = sb.call(fn["name"], fn.get("arguments") or {})
                row["tool_calls"] += 1
                row["tool_errors"] += err
                msgs.append({"role": "tool", "tool_name": fn["name"], "content": text})
    except Exception as e:  # record and move on; one bad model must not kill the bake-off
        row["error"] = repr(e)[:300]
    row["wall_s"] = round(time.time() - t0, 1)
    row["tests_tampered"] = restore_tests(src, work, cfg["test_globs"])  # grade against the original tests, but flag it
    row["passed"] = sb.run_tests()[0]
    row["gen_tok_s"] = round(row["eval_tokens"] / (row["eval_ns"] / 1e9), 1) if row["eval_ns"] else None
    shutil.rmtree(work, ignore_errors=True)
    return row


def summarize(rows):
    out = ["| model | task | pass | turns | tool err | gen tok/s | wall s | peak mem GB | tampered | error |",
           "|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        out.append(f"| {r['model']} | {r['task']} | {'PASS' if r['passed'] else 'FAIL'} | {r['turns']} | "
                   f"{r['tool_errors']}/{r['tool_calls']} | {r['gen_tok_s']} | {r['wall_s']} | {r['mem_gb']} | "
                   f"{'YES' if r['tests_tampered'] else ''} | {r['error'] or ''} |")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="http://localhost:11434")
    ap.add_argument("--models", default=",".join(MODELS))
    ap.add_argument("--tasks", default=",".join(TASKS))
    ap.add_argument("--tag", default="hard")
    ap.add_argument("--modelfile-defaults", action="store_true",
                    help="send no num_ctx/temperature overrides; test the model's own Modelfile params")
    ap.add_argument("--cloud", action="store_true",
                    help="Ollama Cloud: host https://ollama.com, Bearer auth from $OLLAMA_API_KEY, no local preflight")
    a = ap.parse_args()
    models = a.models.split(",")
    headers = auth_headers("OLLAMA_API_KEY") if a.cloud else None
    host = "https://ollama.com" if a.cloud else a.host
    if not a.cloud:
        if missing := [m for m in models if m not in {x["name"] for x in get(host, "/api/tags")["models"]}]:
            raise SystemExit(f"Models not installed on host: {missing}")
        if busy := loaded(host):
            raise SystemExit(f"Refusing to start: models already loaded on host: {busy}")
    rows = []
    for model in models:
        for task in a.tasks.split(","):
            row = run_one(host, model, task, a.tag, a.modelfile_defaults, headers)
            rows.append(row)
            with open(HERE / "results.jsonl", "a") as f:
                f.write(json.dumps(row) + "\n")
            print(row, flush=True)
        if not a.cloud:
            unload(host, model)  # one model at a time
            if loaded(host):
                raise SystemExit(f"Model still loaded after unload: {loaded(host)}")
    (HERE / f"results-{a.tag}.md").write_text(summarize(rows) + "\n")


if __name__ == "__main__":
    main()
# <AI-Generated END>
