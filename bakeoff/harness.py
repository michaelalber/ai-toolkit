# <AI-Generated START>
"""Bake-off: each model x task in a tool loop against Ollama, one model loaded at a time.

Usage: python harness.py [--host URL] [--models pi|m1,m2] [--tasks t1,t2] [--tag NAME] [--n 3]
--models defaults to 'pi': the local Ollama models listed in ~/.pi/agent/models.json.
Sampling defaults to each model's own Modelfile settings, as Pi runs it; --fixed-sampling sends
temperature 0 and a fixed num_ctx instead (comparable with bake-offs before 2026-11-22).
Appends rows to results.jsonl and writes results-<tag>.md (pass counts per model x task, then every run).
"""
import argparse
import json
import math
import os
import shutil
import statistics
import tempfile
import time
import urllib.request
from pathlib import Path

from sandbox import PYTEST_CMD, Sandbox

HERE = Path(__file__).parent
PI_MODELS_JSON = Path.home() / ".pi" / "agent" / "models.json"


def pi_models(path=None, provider="ollama"):
    """Model ids of Pi's local provider: the bake-off tests the lineup the agent actually uses,
    so the list cannot go stale. Cloud providers are not read."""
    path = Path(path or PI_MODELS_JSON)
    if not path.is_file():
        raise SystemExit(f"{path} not found: pass --models m1,m2 to name the models to test")
    return [m["id"] for m in json.loads(path.read_text())["providers"][provider]["models"]]


def resolve_models(spec):
    """'pi' = Pi's local models; otherwise a comma-separated list."""
    return pi_models() if spec == "pi" else [m.strip() for m in spec.split(",") if m.strip()]
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


# Files that change how tests are collected or graded rather than what the code does.
# shortcut: model-written source can still patch the test runner at import time; hidden tests are the real fix.
GRADER_CONFIG = ("conftest.py", "pytest.ini", "pyproject.toml", "setup.cfg", "tox.ini",
                 "sitecustomize.py", "usercustomize.py", "*.pth", "Directory.Build.*", "Directory.Packages.props")


def restore_tests(src, work, globs=("test_*.py",)):
    """Reset protected test and grader-config files in work to the task original; delete ones the model
    added. True if any was added, edited or deleted."""
    globs = (*globs, *GRADER_CONFIG)
    tampered = False
    for f in [f for g in globs for f in Path(work).rglob(g)]:
        if f.is_file() and not (Path(src) / f.relative_to(work)).exists():
            f.unlink()
            tampered = True
    for t in (f for g in globs for f in Path(src).rglob(g)):
        dst = Path(work) / t.relative_to(src)
        if not dst.exists() or dst.read_bytes() != t.read_bytes():
            tampered = True
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(t, dst)
    return tampered


def load_hidden(task):
    """Held-out tests for a task as {relative path: bytes}. They live outside tasks/ so the model never sees
    them; loaded up front so pi_bench can lock hidden/ for the whole batch."""
    root = HERE / "hidden" / task
    return {f.relative_to(root): f.read_bytes() for f in root.rglob("*") if f.is_file()} if root.is_dir() else {}


def hidden_passed(sb, files):
    """Add the held-out tests to the workdir and run the full suite. None when the task has none.
    Catches solutions that special-case the visible tests."""
    if not files:
        return None
    for rel, data in files.items():
        p = sb.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
    return sb.run_tests()[0]


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


def run_one(host, model, task, tag, modelfile_defaults=False, headers=None, run=0):
    """headers set = remote/cloud host: auth is sent and local memory probing (/api/ps) is skipped.
    run: repeat index (0-based) for --n repeats."""
    src = HERE / "tasks" / task
    work = Path(tempfile.mkdtemp(prefix=f"bake-{task}-"))
    shutil.copytree(src, work, dirs_exist_ok=True)
    cfg = load_task_config(src)
    sb = Sandbox(work, cfg["test_cmd"], cfg["test_timeout"])
    msgs = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": (work / "spec.md").read_text()}]
    row = {"round": tag, "model": model, "task": task, "run": run,
           "sampling": "modelfile" if modelfile_defaults else "fixed", "turns": 0, "tool_calls": 0, "tool_errors": 0,
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
    row["hidden_passed"] = hidden_passed(sb, load_hidden(task))
    row["gen_tok_s"] = round(row["eval_tokens"] / (row["eval_ns"] / 1e9), 1) if row["eval_ns"] else None
    shutil.rmtree(work, ignore_errors=True)
    return row


def fmt_hidden(v):
    return "" if v is None else "PASS" if v else "FAIL"


def wilson(k, n, z=1.96):
    """95% Wilson score interval for k passes in n runs. Unlike k/n +/- a normal margin it stays
    inside [0, 1] and is honest at the small n a bake-off has."""
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    margin = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return max(0.0, centre - margin), min(1.0, centre + margin)


def _k_of_n(values):
    vals = [v for v in values if v is not None]
    if not vals:
        return ""
    lo, hi = wilson(sum(vals), len(vals))
    return f"{sum(vals)}/{len(vals)} ({round(lo * 100)}–{round(hi * 100)}%)"


def parse_parameters(text):
    """Ollama /api/show 'parameters' ("key   value" lines) as a dict; repeated keys (stop) become
    lists, and values are parsed as JSON where they can be (numbers, quoted strings)."""
    out = {}
    for line in text.splitlines():
        key, _, raw = line.strip().partition(" ")
        if not key:
            continue
        try:
            value = json.loads(raw.strip())
        except ValueError:
            value = raw.strip()
        if key in out:
            out[key] = (out[key] if isinstance(out[key], list) else [out[key]]) + [value]
        else:
            out[key] = value
    return out


def model_info(host, model, tags, headers=None):
    """What was actually tested: the digest (from /api/tags) and the Modelfile settings and
    quantization (from /api/show). A failing /api/show leaves the settings empty, never the run."""
    digest = next((m.get("digest") for m in tags if m.get("name") == model), None)
    try:
        show = post(host, "/api/show", {"model": model}, timeout=30, headers=headers)
    except Exception:  # metadata only; one unreachable endpoint must not stop the bake-off
        show = {}
    return {"model_digest": digest,
            "quantization": (show.get("details") or {}).get("quantization_level"),
            "model_params": parse_parameters(show.get("parameters") or "")}


def models_table(rows):
    """One row per model: digest, quantization and the sampling settings that applied. With
    Modelfile sampling and no num_ctx in the Modelfile, the server's OLLAMA_CONTEXT_LENGTH applies."""
    out = ["| model | digest | quant | num_ctx | other settings |", "|---|---|---|---|---|"]
    for model in dict.fromkeys(r["model"] for r in rows):
        r = next(x for x in rows if x["model"] == model and x.get("model_params") is not None)
        params = dict(r.get("model_params") or {})
        if r.get("sampling") == "fixed":
            params.update(temperature=0, num_ctx=NUM_CTX)
        num_ctx = params.pop("num_ctx", "server default")
        params.pop("stop", None)  # prompt-format tokens, not sampling settings
        other = ", ".join(f"{k}={v}" for k, v in sorted(params.items()))
        out.append(f"| {model} | {(r.get('model_digest') or '')[:12]} | {r.get('quantization') or ''} | "
                   f"{num_ctx} | {other} |")
    return "\n".join(out)


def aggregate(rows):
    """Pass counts over repeated runs per model x task, plus a total per model. One run of 6 tasks swings
    a pass rate by 17 points and temperature 0 is not deterministic on Ollama, so read k/n, not one PASS."""
    out = ["| model | task | pass | hidden | median wall s |", "|---|---|---|---|---|"]
    for model in dict.fromkeys(r["model"] for r in rows):
        mine = [r for r in rows if r["model"] == model]
        for task in dict.fromkeys(r["task"] for r in mine):
            runs = [r for r in mine if r["task"] == task]
            out.append(f"| {model} | {task} | {_k_of_n(r['passed'] for r in runs)} | "
                       f"{_k_of_n(r.get('hidden_passed') for r in runs)} | "
                       f"{statistics.median(r['wall_s'] for r in runs):.1f} |")
        out.append(f"| **{model}** | **all** | **{_k_of_n(r['passed'] for r in mine)}** | "
                   f"**{_k_of_n(r.get('hidden_passed') for r in mine)}** |  |")
    return "\n".join(out)


def summarize(rows):
    out = ["| model | task | pass | hidden | turns | tool err | gen tok/s | wall s | peak mem GB | tampered | error |",
           "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        out.append(f"| {r['model']} | {r['task']} | {'PASS' if r['passed'] else 'FAIL'} | "
                   f"{fmt_hidden(r.get('hidden_passed'))} | {r['turns']} | "
                   f"{r['tool_errors']}/{r['tool_calls']} | {r['gen_tok_s']} | {r['wall_s']} | {r['mem_gb']} | "
                   f"{'YES' if r['tests_tampered'] else ''} | {r['error'] or ''} |")
    return "\n".join(out)


def parse_args(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="http://localhost:11434")
    ap.add_argument("--models", default="pi",
                    help="comma-separated models, or 'pi' (default) for the local models in "
                         "~/.pi/agent/models.json")
    ap.add_argument("--tasks", default=",".join(TASKS))
    ap.add_argument("--tag", default="hard")
    ap.add_argument("--n", type=int, default=3, help="runs per model x task (>=3 to see run-to-run variance)")
    # Default: each model's own Modelfile settings, as Pi runs it. --fixed-sampling reproduces
    # bake-offs from before 2026-11-22 (temperature 0, num_ctx 32768).
    ap.add_argument("--modelfile-defaults", dest="modelfile_defaults", action="store_true",
                    default=True, help="send no num_ctx/temperature overrides (the default)")
    ap.add_argument("--fixed-sampling", dest="modelfile_defaults", action="store_false",
                    help=f"send temperature 0 and num_ctx {NUM_CTX} (comparable with older results)")
    ap.add_argument("--cloud", action="store_true",
                    help="Ollama Cloud: host https://ollama.com, Bearer auth from $OLLAMA_API_KEY, no local preflight")
    return ap.parse_args(argv)


def main():
    a = parse_args()
    if a.n < 1:
        raise SystemExit("--n must be >= 1")
    models = resolve_models(a.models)
    headers = auth_headers("OLLAMA_API_KEY") if a.cloud else None
    host = "https://ollama.com" if a.cloud else a.host
    tags = []
    if not a.cloud:
        tags = get(host, "/api/tags")["models"]
        if missing := [m for m in models if m not in {x["name"] for x in tags}]:
            raise SystemExit(f"Models not installed on host: {missing}")
        if busy := loaded(host):
            raise SystemExit(f"Refusing to start: models already loaded on host: {busy}")
    rows = []
    for model in models:  # repeats stay inside one model load: one model in memory at a time
        info = model_info(host, model, tags, headers)
        for i in range(a.n):
            for task in a.tasks.split(","):
                row = {**run_one(host, model, task, a.tag, a.modelfile_defaults, headers, run=i), **info}
                rows.append(row)
                with open(HERE / "results.jsonl", "a") as f:
                    f.write(json.dumps(row) + "\n")
                print(row, flush=True)
        if not a.cloud:
            unload(host, model)  # one model at a time
            if loaded(host):
                raise SystemExit(f"Model still loaded after unload: {loaded(host)}")
    (HERE / f"results-{a.tag}.md").write_text(
        f"## Pass counts ({a.n} runs per model x task, "
        f"{'Modelfile' if a.modelfile_defaults else 'fixed: temperature 0'} sampling)\n\n"
        f"{aggregate(rows)}\n\nIntervals are 95% Wilson confidence intervals; overlapping "
        f"intervals mean the difference may be noise.\n\n## Models tested\n\n{models_table(rows)}\n\n"
        f"## Every run\n\n{summarize(rows)}\n")


if __name__ == "__main__":
    main()
# <AI-Generated END>
