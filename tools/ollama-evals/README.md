# ollama-evals

Evaluate and **regression-test local Ollama models** for coding, chat, tool-use, and
structured output — so you can confirm a model performs well and prove a *new* model has
not regressed against a *previous* one.

## Why this is frontend-agnostic

Pi, Goose, and Open WebUI are all *frontends* to the same Ollama backend. So "is the model
good?" is answered **once, at the API level** — the harness talks directly to Ollama's
OpenAI-compatible endpoint (`/v1/chat/completions`). The score you get is valid no matter
which of the three tools drives the model. (Testing an *agent harness itself* — tool-call
loops in Pi/Goose — is a separate, heavier concern; this tool measures the model.)

```
ollama-evals ──> http://<ollama-host>:11434/v1   (qwen2.5-coder:7b, llama3.1:8b, …)
                 └── the same model Pi / Goose / Open WebUI use
```

---

## What it measures

| Suite | Scorer | Signal |
|---|---|---|
| **coding** | code-execution | Generated code is run against hidden tests → objective pass/fail. The least-gameable coding signal. |
| **chat** | LLM-as-judge | Reasoning, instruction-following, summarization, tone — scored by a rubric (calibrate before trusting). |
| **tool_use** | trajectory | Did the model select the right tool with the right arguments? |
| **structured** | JSON-schema | Output validity and format adherence — cheap deterministic regression canaries. |

Scorer types: `exact`, `contains`, `regex`, `json_schema`, `code_exec`, `tool_use`, `judge`.

---

## Install

Dependencies are not vendored. Use [`uv`](https://docs.astral.sh/uv/) (recommended) or `pip`.

```bash
cd tools/ollama-evals

uv run ollama-evals --help          # run directly (ephemeral env)

# or install into the current environment
pip install -e .                    # core (deterministic + code-exec + rubric judge)
pip install -e '.[judge]'           # adds DeepEval for the optional / remote judge
pip install -e '.[dev]'             # test + lint extras
```

## Point it at your Ollama (LAN)

The committed config defaults to `http://127.0.0.1:11434/v1` and contains **no personal
host**. To use an Ollama on your LAN (e.g. a Mac mini), pick one:

```bash
# 1. environment variable (wins over everything)
export OLLAMA_BASE_URL=http://mac-mini.local:11434/v1

# 2. or a gitignored local config
cp models.yaml models.local.yaml    # then edit base_url in models.local.yaml
```

`models.local.yaml` and `*.local.yaml` are gitignored, so your host stays out of the repo.

---

## Quickstart

```bash
# Make sure the models are pulled on the Ollama host:
#   ollama pull qwen2.5-coder:7b && ollama pull llama3.1:8b

# 1. See what's available on the server
uv run ollama-evals list-models

# 2. Run the full suite across two models -> writes runs/<id>.run.json + prints a matrix
uv run ollama-evals run --models qwen2.5-coder:7b,llama3.1:8b

# 3. Run just one suite
uv run ollama-evals run --suite coding --models qwen2.5-coder:7b
```

### Regression-test a new model against the old one

```bash
# Baseline: the model you trust today
uv run ollama-evals run --models qwen2.5-coder:7b --out runs/baseline

# Candidate: the new / upgraded model
uv run ollama-evals run --models qwen2.5-coder:7b-v2 --out runs/candidate

# Gate: fails (exit 1) if the candidate drops more than the threshold on any category
uv run ollama-evals compare runs/baseline/<id>.run.json runs/candidate/<id>.run.json \
    --threshold 0.05 --html report.html
```

`compare` prints a per-category delta table + pairwise win/loss/tie and **exits non-zero on
regression** — drop it into CI to block a model swap that makes things worse.

### Re-render a saved run

```bash
uv run ollama-evals report runs/<id>.run.json --html matrix.html
```

---

## Calibrate the judge (do this before trusting chat scores)

An uncalibrated LLM-as-judge is worse than none. `datasets/judge-calibration.jsonl` holds
human-labelled good/bad answers; `calibrate` measures how often the judge agrees.

```bash
uv run ollama-evals calibrate            # aim for agreement >= 0.80
```

The default judge is a **local** Ollama model (see `judge:` in `models.yaml`) prompting a
1–5 rubric — fully offline, no extra dependencies. Set `judge.provider: remote` (and install
`.[judge]`) to use a DeepEval-backed or hosted judge; the API key is read from the
environment, never committed.

---

## Add a case

Cases are JSONL — one per line in `datasets/<suite>.jsonl`:

```json
{"id": "code-is-prime", "category": "coding",
 "prompt": "Write a Python function is_prime(n)...",
 "scorer": {"type": "code_exec", "timeout": 10,
            "test_code": "assert is_prime(13)\nassert not is_prime(1)"}}
```

Keep the set small and challenging — 100 well-constructed cases beat 1,000 noisy ones.
`tests/test_datasets.py` guards that every case loads and uses a registered scorer.

---

## Security

The code-execution scorer runs model-generated Python. Defense-in-depth: an isolated temp
directory, a wall-clock timeout, POSIX CPU/file-size limits, a minimal environment, an
isolated interpreter (`python -I`), and a preamble that disables network sockets from the
generated code.

**This stops accidental and casual-malicious code — it is not a substitute for OS-level
isolation.** For untrusted models, run the whole harness inside a container or `firejail`.

---

## Development

```bash
uv run --extra dev pytest          # 79 tests; Ollama is mocked, so CI needs no live server
uv run --extra dev ruff check src tests
```

| Module | Responsibility |
|---|---|
| `client.py` | Ollama OpenAI-compatible client (`/v1/chat/completions`, `/api/tags`) |
| `config.py` | Config + endpoint precedence (env > local.yaml > yaml > default) |
| `cases.py` | Case model + JSONL dataset loading |
| `scorers/` | `exact`, `contains`, `regex`, `json_schema`, `code_exec`, `tool_use`, `judge` |
| `judging.py` | Rubric (local) + DeepEval (opt-in) judges; pairwise compare |
| `runner.py` | Run model × case → scored artifact |
| `compare.py` | Per-category deltas, pairwise, regression gate |
| `report.py` | Markdown + self-contained HTML |
| `calibrate.py` | Judge-vs-human agreement |
| `cli.py` | `run` · `compare` · `report` · `calibrate` · `list-models` |
