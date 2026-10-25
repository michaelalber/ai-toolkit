<!-- <AI-Generated START> -->

# LPN-Engine v1 — Implementation Plan

| | |
|---|---|
| **Status** | Proposed — not yet started |
| **Date** | 2026-11-01 |
| **Scope** | Local, privacy-first code-generation engine: LLM proposal + deterministic verification, exposed to editors as an MCP server |
| **Hardware target** | Mac mini M4 Pro, 48 GB, Ollama host at `http://127.0.0.1:11434` |

---

## 1. Context & Goal

The LPN-Engine addresses Gary Marcus's core LLM critiques — hallucinated facts, brittleness,
lack of deterministic logic — by putting the LLM *between* deterministic gates rather than
trusting its output:

- **Hallucination** → retrieval-grounded generation with a hard citation-membership gate, plus
  compiler/linter verification of the code itself.
- **Brittleness** → Ollama `format:` JSON-schema-constrained decoding, so output always parses
  (with a belt-and-suspenders language-tag strip — see §3.3).
- **No deterministic logic** → real compilers are the authority; the model proposes, tools dispose.
  Failure feedback loops back into the prompt (rejection sampling with verifier feedback, max 3).

It is deliberately **not** a deep neurosymbolic reasoner: the symbolic layer *validates*, it does
not derive. That is the honest scope of v1.

## 2. The One Shaping Decision

**A local service, not a script — exposed via MCP.** Cursor, VS Code, Claude Code, and Pi all
speak MCP; no editor plugin is ever written. A plain REST route stays for curl/scripts.

```
┌── Clients ──────────────────────────────────────────────────┐
│ Cursor / VS Code / Claude Code / Pi   (MCP, stdio)          │
│ curl / scripts                       (REST, :8899)          │
└──────────────┬──────────────────────────────────────────────┘
               ▼
┌── lpn-engine (FastAPI + FastMCP wrapper, Python 3.12) ──────┐
│  generate(prompt, language)                                 │
│   1. RETRIEVE  embed query → Qdrant top-k (k=4, lang filter)│
│   2. CONSTRAIN Ollama /api/chat, format=JSON schema         │
│   3. VERIFY    citations ⊆ retrieved ids (non-empty)        │
│                + per-language verifier (parse/compile)      │
│   4. REPAIR    fail → append verifier stderr + raw output,  │
│      re-generate (max 3)                                    │
└──┬───────────────────┬───────────────────────┬──────────────┘
   ▼                   ▼                       ▼
 Ollama :11434     Qdrant local           Verifier pool
 + embed model     + fastembed            (per-language CLIs)
```

## 3. Verified Findings (measured on the target box, 2026-11-01)

These are facts from probing `127.0.0.1`, not spec-sheet claims.

### 3.1 Model benchmark — schema-constrained codegen, same prompt, same options

| Model | Speed | Thinking toks | Schema output | Executed correctly |
|---|---|---|---|---|
| `qwen3.6-35b-a3b-coding-agent` (MoE) | **65–74 tok/s** | ~900 | ✅ clean JSON | ✅ |
| `qwen3.6:27b-coding-nvfp4` (dense) | 25.6 tok/s | ~550 | ❌ `python{...}` prefix | — |
| `qwen3.8-27b-agent` (dense) | 23.3 tok/s | ~100 | ❌ `python{...}` prefix | — |

**Decision: `qwen3.6:35b-a3b-coding-nvfp4` (or its `-agent` twin) is the generator.**
The newer qwen3.8 line is a general agent/chat model — no code advantage and 2.8× slower for
this task. Higher version ≠ better generator.

### 3.2 Verifier commands — corrected against the original blueprint

| Lang | Command | Strength | Notes |
|---|---|---|---|
| Python | `ast.parse()` in-process, then `ruff check -` | parse + lint | ruff reads stdin via `-` |
| JS | `printf '%s' "$code" \| node --check -` | parse | **verified** on Node 22; older Node needs temp file |
| Rust | `rustc --edition=2021 - --crate-type=lib --emit=metadata --out-dir <tmp>` | **full type-check** | blueprint's `-o /dev/null` **always fails** (tmp-file next to output); default edition 2015 rejects `async` — both verified |
| PHP | temp file → `php -l file.php` | parse | ⚠️ **VERIFY:** `php -l` does not read stdin; php not installed on dev box |
| C# | Roslyn sidecar: minimal ASP.NET API, `POST /verify` → `CSharpCompilation` in-memory → diagnostics | full type-check | `dotnet build` needs a project + multi-second cold start; a persistent sidecar is the smallest correct thing |

### 3.3 Generator output is untrusted even under schema enforcement

Under this Ollama build's `qwen3.5` renderer/parser, both dense models prepended a bare `python`
tag before constrained JSON. Engine mitigations (both cheap, both required):

1. Strip a leading `\s*\w+\s*(?={)` language-tag before `json.loads`.
2. On parse failure, feed the **raw output** back as repair context — not a bare "try again".

### 3.4 `-agent` Modelfile presets

Raw `{{ .Prompt }}` template → **call `/api/chat`, never `/api/generate`**. Defaults to override
per-request: `num_ctx` 131072 (waste) → set 16–32k; `presence_penalty` 1.5 is high for code.

## 4. Component Decisions

| Concern | Pick | Rejected alternative (why) |
|---|---|---|
| Service | FastAPI + `Pipeline` class | None needed — house pattern |
| Editor interface | **FastMCP** server, one tool `generate_verified_code` | Editor plugins (never free), GBNF grammars (overkill next to `format:`) |
| Generator | `qwen3.6:35b-a3b-coding-nvfp4`, via `/api/chat`, `num_predict ≥ 2048` (thinking burns tokens), `temperature 0.2`, `keep_alive "30m"` | qwen3.8-27b (dense, slower, non-coding); granite4.2 (keep as fallback) |
| Embedder | `snowflake-arctic-embed2` (already resident, 8192 ctx) | bge/nomic (no local advantage) |
| Doc chunking | **tree-sitter** (c-sharp, php, python, javascript, rust grammars) — chunk per *symbol* (fn/class/method + docstring + source span) | Fixed-size chunks (accuracy killer); one parser per language in its own AST lib (5 pipelines to maintain) |
| Vector store | Qdrant local (already running this stack) | sqlite-vec (viable, no reason to switch) |
| Citation gate | `citations ⊆ retrieved doc_ids` **and** `len > 0` | Blueprint's `all([]) == True` hole |
| Language dispatch | Client passes `language` as a tool arg | Blueprint had the *model* guess it — a hallucination the schema invites |
| Config | `lpn.yaml`: model names, k, max_retries, per-language verifier commands | Hardcoded model strings (house rule; models churn) |

## 5. Repo Layout

```
lpn-engine/
├── lpn/
│   ├── config.py        # pydantic-settings ← lpn.yaml
│   ├── retrieve.py      # embed + Qdrant query
│   ├── generate.py      # ollama /api/chat, schema, tag-strip, repair loop
│   ├── verify/          # base.py + python.py js.py rust.py php.py csharp.py
│   └── mcp_server.py    # FastMCP: generate_verified_code
├── ingest/chunk.py      # tree-sitter symbol extractor → Qdrant
├── sidecar-roslyn/      # one .csproj, one Program.cs
├── tests/
│   ├── fixtures/{python,js,rust,php,csharp}/{valid,bad}.*
│   └── test_*.py
└── lpn.yaml
```

## 6. Phases & Acceptance Gates

Each phase is independently verifiable; do not start the next until its gate passes.

| # | Phase | Gate (binary, verifiable) |
|---|---|---|
| 1 | **Skeleton** — FastAPI app, `/health`, config, CI | CI green |
| 2 | **Verifier pool** — 5 verifiers × golden fixtures | 5/5 valid pass, 5/5 known-bad rejected with stderr captured; PHP gate can ship as `# VERIFY` until php is installed |
| 3 | **Generation loop** — ollama client, schema, tag-strip, ≤3 repairs | prompt "write invalid python" either recovers in ≤3 or raises; a `python{`-prefixed output still parses (unit test the strip) |
| 4 | **Ingest + retrieve** — tree-sitter chunker over one real repo per language into Qdrant | query for a known symbol name returns its chunk in top-4 |
| 5 | **MCP wrapper** — FastMCP tool over the pipeline | callable from Cursor *and* Pi end-to-end; returns code + citations + attempt log |

Post-v1.5 candidates (only if measured failure rates demand): semantic judge
(`granite4.2:30b-q5_K_M`), pyright/phpstan verifiers, `tsc` for TypeScript.

## 7. API Surface

**MCP tool / REST `POST /generate`**

```json
{ "prompt": "Write a thread-safe counter in Rust", "language": "rust" }
→ 200 {
  "code": "...",
  "language": "rust",
  "citations": ["doc_rust_01"],
  "attempts": [{"ok": false, "stderr": "..."}, {"ok": true}],
  "model": "qwen3.6:35b-a3b-coding-nvfp4"
}
→ 422 { "error": "repair_exhausted", "attempts": [...] }
```

## 8. Security Invariants

- **Compile, never execute** generated code. (rustc proc-macro expansion is the residual
  surface; stdin-only with no extern crates keeps it low.)
- Doc corpus is untrusted **data**: chunks interpolated as data, never as instructions.
- No secrets in `lpn.yaml` — env vars only.
- Verifiers run with a 5 s timeout and write only to their own tmpdir.

## 9. Non-Goals for v1

Every deferred idea — with its promotion trigger — lives in `docs/lpn-engine-v2-roadmap.md`; do
not re-propose items from that file into v1 without the trigger firing.

Editor plugins · GBNF grammars · multi-model routing · test-execution sandbox ·
semantic/behavioral correctness guarantees · multi-language responses · TypeScript ·
a second embedder.

Honesty clause for the README: **Rust and C# get type-checked; Python/JS/PHP get
parse-checked.** "Guaranteed to compile" (Rust/C#) or "guaranteed to parse" — never
"guaranteed correct."

## 10. Open Items to De-risk Early

- [ ] Install php on the dev box; confirm `php -l` temp-file behavior (§3.2)
- [ ] Build Roslyn sidecar; measure per-call latency (target < 500 ms warm)
- [ ] Re-bench the MoE generator at realistic 16–32k prompt sizes (benched at 4k)
- [ ] Confirm Qdrant host/persistent path convention (mirror grounded-code-mcp's config pattern)
- [ ] Decide whether `generate_verified_code` streams progress (MCP progress notifications) or stays unary
- [ ] Evaluate LSP-backed verifiers (the mcp-language-server pattern) vs parse-only CLIs for Python/JS/PHP **before Phase 2 is locked** (§12.1)
- [ ] Sanitize a copy of this plan (LAN IP, model inventory) before feeding any phase to a cloud model (§12.3 #4)

## 11. Implementation Contracts

Concrete enough that a local model (or a tired human) implements without guessing.
Where a value is marked *derive*, write a test that locks it in rather than trusting the sheet.

### 11.1 Dependencies (`pyproject.toml`)

Minimum floors — run `uv lock` at the end of Phase 1 and commit `uv.lock`; that file is the true pin.

```toml
[project]
name = "lpn-engine"
requires-python = ">=3.12"
dependencies = [
  "fastapi>=0.115",
  "uvicorn>=0.30",
  "fastmcp>=2.10",
  "qdrant-client>=1.11",
  "httpx>=0.27",              # ollama + sidecar calls
  "pydantic>=2.7",
  "pydantic-settings>=2.3",
  "tree-sitter>=0.23",
  "tree-sitter-language-pack>=0.7",  # one wheel: all 5 grammars
  "pyyaml>=6.0",
]
[dependency-groups]
dev = ["pytest>=8", "pytest-cov>=5", "ruff>=0.6"]
```

External binaries required on PATH: `node`, `rustc`, `php` (⚠️ install + verify per §10), `dotnet` SDK ≥ 8 (sidecar).

### 11.2 Module contracts (`lpn/`)

```python
# lpn/models.py
class DocChunk(BaseModel):
    doc_id: str            # "{relpath}::{symbol}"
    language: str          # python|rust|php|js|csharp
    path: str; symbol: str; content: str
    start_line: int; end_line: int

class VerifyResult(BaseModel):
    ok: bool; feedback: str    # feedback = verifier stderr/stdout, "" when ok

class Attempt(BaseModel):
    ok: bool; feedback: str = ""
    raw_prefix_stripped: bool = False   # tag-strip fired? (§3.3)

class GenerateResult(BaseModel):
    code: str; language: str
    citations: list[str]
    attempts: list[Attempt]
    model: str

class RepairExhausted(Exception):
    attempts: list[Attempt]

# lpn/retrieve.py
def retrieve(query: str, language: str, k: int = 4) -> list[DocChunk]: ...

# lpn/verify/base.py
def verify(code: str) -> VerifyResult: ...   # each language module implements this

# lpn/generate.py
def generate(prompt: str, language: str, docs: list[DocChunk]) -> GenerateResult:
    """Raises RepairExhausted after cfg.max_retries failed attempts."""

# lpn/mcp_server.py
@mcp.tool()
def generate_verified_code(prompt: str, language: str) -> dict:
    """Generate code grounded in our documentation and verified to parse/compile.
    language: one of python | rust | php | js | csharp"""
```

HTTP: `POST /generate` mirrors the tool; `GET /health` → `{"ok": true}` (Phase-1 gate).
**422 body on exhaustion:** `RepairExhausted.model_dump()` under `{"error": "repair_exhausted"}`.

### 11.3 Ollama payload constants (`lpn/config.py` defaults, env-overridable)

```python
OLLAMA_URL   = "http://127.0.0.1:11434/api/chat"   # /api/chat, never /api/generate (§3.4)
EMBED_URL    = "http://127.0.0.1:11434/api/embed"
MODEL        = "qwen3.6:35b-a3b-coding-nvfp4"
EMBED_MODEL  = "snowflake-arctic-embed2:latest"
OPTIONS = {"num_ctx": 24576, "num_predict": 2048, "temperature": 0.2, "keep_alive": "30m"}
MAX_RETRIES, K, VERIFY_TIMEOUT_S = 3, 4, 5

OUTPUT_SCHEMA = {
  "type": "object",
  "properties": {
    "code": {"type": "string"},
    "doc_citations": {"type": "array", "items": {"type": "string"}}
  },
  "required": ["code", "doc_citations"]
}
TAG_STRIP_RE = r"^\s*(?:```)?\w{0,12}\s*(?:```)?\s*(?=\{)"   # §3.3: strips bare 'python{...}'
```

Generate request shape: `{"model": MODEL, "messages": [...], "format": OUTPUT_SCHEMA,
"stream": false, "options": OPTIONS}`. Language is **not** in the schema (§4).

### 11.4 Qdrant schema (`ingest/chunk.py` asserts at connect)

```python
COLLECTION = "lpn_docs"
client.recreate_collection(COLLECTION, vectors_config=VectorParams(size=DIM, distance=Distance.COSINE))
# DIM: derive once — len(client.embed(...)[0]) on first embed, expected 1024 for arctic-embed2;
#      assert == 1024, else fail loud.
# point payload = DocChunk.model_dump(); point id = uuid5(doc_id)
# query filter: FieldCondition("language", MatchValue(language))
```

### 11.5 Prompt templates (versioned files, loaded once — never f-strings in code)

`lpn/prompts/generate.md`
```
You output JSON only: {"code": string, "doc_citations": string[]}.
Write {language} code. Cite ONLY these Doc IDs: {doc_ids}. No markdown fences.
Relevant documentation:
{doc_context}
Task: {prompt}
```

`lpn/prompts/repair.md`
```
Your previous {language} output FAILED deterministic verification.
Verifier feedback: {feedback}
Raw previous output: {bad_output}
Return corrected JSON only, same schema. Cite ONLY: {doc_ids}.
```

### 11.6 Gate commands (run at the end of each phase; non-zero exit = gate fails)

```bash
# Phase 1 — skeleton
curl -sf localhost:8899/health && uv lock --check && ruff check lpn && pytest -q

# Phase 2 — verifier pool (fixtures: tests/fixtures/<lang>/{valid,bad}.*)
pytest tests/verify -q            # 5×valid pass, 5×bad rejected w/ non-empty feedback
# C# sidecar separately:
curl -sf localhost:8899/health >/dev/null && curl -s -X POST localhost:5100/verify \
  -H 'content-type: application/json' -d '{"code":"class C{}"}' | grep '"ok":true'

# Phase 3 — generation loop
pytest tests/test_generate.py -q  # incl. tag_strip test + invalid-python recovery ≤3 attempts

# Phase 4 — ingest + retrieve
python -m ingest.chunk tests/fixtures && pytest tests/test_retrieve.py -q
#   gate inside test: query "reverse_string" → its chunk in top-4

# Phase 5 — end-to-end
curl -sf -X POST localhost:8899/generate -H 'content-type: application/json' \
  -d '{"prompt":"Thread-safe counter","language":"rust"}' | grep '"attempts"'
# + manual: same call succeeds as an MCP tool from Cursor and from Pi
```

### 11.7 Known weak spot

The **Roslyn sidecar** (C#) is the riskiest single component — a .NET process with a Python
caller across localhost. Build it in Phase 2 *first*, before the four CLI verifiers, so its
risk lands early. Contract: `POST /verify {"code": str} → {"ok": bool, "diagnostics":
[{"line": int, "severity": str, "message": str}]}`; `feedback` = diagnostics joined with `\n`.

## 12. Lessons from the Design Pass (2026-11-01)

### 12.1 Prior art — scanned; the build stands

GitHub/API sweep of adjacent work:

- **aider** (49.7k⭐) ships exactly the generate → lint/test → feedback → retry loop, locally,
  with Ollama. The repair-loop design is validated at scale — and its tree-sitter repo-map
  independently confirms the §4 ingest choice.
- **mcp-language-server** (1.6k⭐) ships compiler diagnostics as an MCP service via **LSP** —
  semantic, not parse-only. The cheapest known way to close the §3.2 strength gap for
  Python/JS/PHP without pyright/phpstan sidecars.
- **AlphaCodium** (CodiumAI) proves the same flow at research level; **outlines** proves
  constrained decoding is a commodity library primitive.
- **Nothing ships a runtime citation-membership gate** (rejecting generation that cites doc
  IDs not actually retrieved — RAGAS et al. check citations only as offline *evals*). That is
  LPN's differentiating piece: keep it first-class in implementation and any write-up.

### 12.2 Decisions recorded

- **Build vs. adopt** (aider + hooks): build. LPN is reusable infrastructure (polyglot
  verifier pool + citation gate as a service primitive); adopting couples us to a tool we
  don't control. Revisit only if the scope shrinks to one-off assistance.
- **Verifier strategy:** v1 default stays the §3.2 CLIs; if pylsp / typescript-language-server
  install cleanly during Phase 2, swap to LSP-backed semantic checks at comparable complexity.
- **Construction-assistant model:** local qwen3.6-coding default; cloud (kimi-k3) only after
  two failed gate attempts on the same phase, and only with a sanitized plan.

### 12.3 Meta-lessons — apply to every future phase

1. **Measure on the target box before writing it into a contract.** Three assumptions died by
   measurement in the design pass: nvfp4 "too slow on Metal" (73 tok/s), `node --check -`
   "broken" (works on Node 22), rustc `-o /dev/null` "fine" (always fails). Every
   environment-dependent value in §11 gets a startup assert, not a doc claim.
2. **Version number ≠ fitness.** qwen3.8-general loses to qwen3.6-coding on this exact task
   (2.8× slower, same schema bug). Any future model swap re-runs the §3.1 bench first; note
   that bench was single-prompt — a real regression matrix (tools/ollama-evals) is a pre-v1
   item if model comparisons keep coming up.
3. **When driving a local construction model, budget context, not intelligence.** One phase +
   the one relevant plan section per message; never paste the whole plan into a working session.
4. **Cloud escalation carries the privacy cost it was bought to avoid — sanitize first.**
   This plan contains LAN topology and the internal model inventory; strip before any cloud run.

<!-- <AI-Generated END> -->
