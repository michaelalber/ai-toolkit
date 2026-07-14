# code2md

Scan a codebase into **AI-agent-friendly Markdown** — one language-tagged document per source
file, plus a synthesized project overview — ready for ingestion into a RAG knowledge base such as
[grounded-code-mcp](https://codeberg.org/michaelkalber/grounded-code-mcp).

Where [`pdf2md`](../pdf2md) and [`web2md`](../web2md) convert *documents* and *web pages*,
`code2md` converts *your own project's source code*, so an AI coding session can ground answers in
the actual codebase instead of guessing.

---

## How it fits grounded-code-mcp

grounded-code-mcp ingests Markdown, not raw source files. Its code-awareness (function-boundary
chunking, and the `search_code_examples(language=…)` filter) keys off the **fence language label**
inside Markdown. `code2md` emits each source file as a fenced block tagged with a label from
grounded-code-mcp's known-language set — so the existing pipeline works with **zero changes** to
the server.

Project code lands in its **own collection** (`grounded_project_{name}`), keeping churny snapshots
out of the shared, vetted collections like `grounded_internal`.

---

## Features

- **Per-file code documents** — every source file → `path/to/file.ext.md` with a
  ` ```<language> ` fence and YAML front-matter (`source`, `path`, `language`, `extracted_at`,
  `git_commit`).
- **Repo overview** (`_overview.md`) — README excerpt, language/module breakdown, and declared
  dependencies (`pyproject.toml` / `package.json` / `Cargo.toml`). Emitted as prose so it lands as
  text chunks.
- **`.gitignore`-aware** — uses `git ls-files` in a git repo; falls back to a `pathspec` walk.
- **Fence-safe** — source containing ```` ``` ```` gets a longer outer fence automatically.
- **`--max-file-kb`** — skip oversized files. **`--no-overview`** / **`--no-metadata`** toggles.
- **Optional LLM enrichment** (`code2md enrich`) — per-file NL summaries and a verified concept
  graph (`RELATIONSHIPS.md`) as retrieval bridges; provenance-marked, SHA-cached, ingested
  unchanged. See [Enrichment](#enrichment-optional-llm).

## Installation

Requires Python ≥ 3.10. Use [`uv`](https://docs.astral.sh/uv/) (recommended) or `pip`.

```bash
cd tools/code2md
uv run code2md --help
```

## Usage

```bash
# Scan a project into ./output/myapp/
code2md scan ~/AppDev/myapp --name myapp

# Explicit output dir + verbose
code2md scan ~/AppDev/myapp --out /tmp/code2md/myapp --name myapp --verbose
```

The output directory name is a **single, hyphenated slug** (`My App` → `my-app`) and
becomes the ingested chunks' `source_path` prefix. Point `--out` at a **top-level**
directory under grounded-code-mcp's `sources/` (e.g. `sources/my-app/`, *not* a nested
`sources/projects/my-app/`) — a single-segment prefix is what the concept-graph
`source_slug` matches against, so graph expansion in `search_knowledge` can resolve
project edges back to real chunks.

Then wire it into grounded-code-mcp in two steps:

**1. Register the collection** (one-time, per project) in your **user** config
(`~/.config/grounded-code-mcp/config.toml`). `search_knowledge` validates its `collection`
argument against the `[collections]` allowlist, so without this the prose overview is not
searchable (code *is*, because `search_code_examples` skips the allowlist):

```toml
[collections]
# key = source_path prefix (the single-segment slug dir under sources/)
# value = the ingest --collection name below (search_knowledge validates against these)
"my-app" = "project_my_app"
```

This lives in the user config, not the committed project config — project snapshots are
machine-specific and churny.

**2. Ingest** (the tool prints this line for you):

```bash
grounded-code-mcp ingest sources/my-app --collection project_my_app
```

`--collection` overrides path-based collection derivation, producing `grounded_project_my_app`.
The scan lands **under** grounded-code-mcp's `sources/` as a single-segment slug dir so its
chunks' `source_path` prefix (`my-app/…`) matches the concept-graph `source_slug`; gitignore the
per-project scan dirs to keep churny snapshots out of the committed tree. Re-running is cheap:
grounded-code-mcp's SHA-256 change detection re-ingests only files that changed.

> The MCP server reads `[collections]` at startup — restart it after step 1 so
> `search_knowledge` picks up the new collection. (The CLI `grounded-code-mcp search` re-reads
> config each run and needs no restart.)

## Enrichment (optional, LLM)

`code2md enrich` uses a local model to generate **retrieval bridges** — content that makes
natural-language queries land on the right code. It runs at three levels, selected with `--level`:

- **`summaries`** (default, Phase 1) — a natural-language summary and the questions each file
  answers, written per file under `_enriched/`. These are prose (`is_code=False`), so they match
  NL queries yet stay out of `search_code_examples`.
- **`graph`** (Phase 3) — a verified **concept graph** (`RELATIONSHIPS.md` at the scan root):
  source-attributed `"A" → verb → "B"` edges that pre-compute the multi-hop structure small models
  are worst at. Every edge passes a **verification pass** — a second model call confirms the cited
  code actually supports the edge, and unsupported edges are dropped. This is the guard against
  hallucinated *routing* (a false edge that steers retrieval to real-but-irrelevant code).
- **`full`** — both.

All output carries provenance (`generated: true`, `model`, `derived_from`) and **never replaces**
the real code (the authority). grounded-code-mcp ingests it unchanged — `RELATIONSHIPS.md` is the
concept-graph feed its existing parser already consumes, so `ingest --force` (or `build-graph`)
rebuilds the graph with **no server change**.

```bash
# scan first, then enrich the scan output
code2md scan ~/AppDev/myapp --out /tmp/scan/myapp --name myapp

# Phase 1 only (default): per-file summaries + questions
code2md enrich /tmp/scan/myapp --model qwen3-coder:30b --ollama-host http://<host>:11434

# full: summaries + verified concept graph, with a smaller model for the verify pass
code2md enrich /tmp/scan/myapp --level full \
  --model qwen3-coder:30b --verify-model qwen2.5-coder:7b \
  --ollama-host http://<host>:11434 --verbose
```

The model is **required** (via `--model` or `CODE2MD_ENRICH_MODEL`) — never hardcoded, since
build-time generation should use your strongest available coding model. `--verify-model` defaults
to `--model`; `--timeout` sets the per-request timeout (default 180s). Results are SHA-cached
(keyed by code hash + model id) in `_enriched/enrich-manifest.json` and
`_enriched/relate-manifest.json`, so re-runs regenerate only changed files — pass `--force` to
re-enrich regardless. See [`docs/enrichment-design.md`](docs/enrichment-design.md) for the full
design (Phase 2: a project architecture brief; Phase 4: an optional server-side provenance filter).

> **Bridge, not authority:** enriched docs are prose (`is_code=False`), so they match NL queries
> and stay out of `search_code_examples`. In testing, the generated bridge for a file *outranks*
> the raw code for a natural-language question — while the code remains the citation.

## Language coverage

Extensions map to fence labels that are a **subset of grounded-code-mcp's `KNOWN_LANGUAGES`**
(`tests/test_language.py` enforces this): python, csharp, javascript, typescript, java, go, rust,
cpp, c, php, ruby, scala, kotlin, swift, r, sql, bash, html, css. Prose (`.md`/`.rst`/`.txt`) and
data/config (`.json`/`.yaml`/`.toml`) are intentionally excluded from per-file conversion — README
and dependency manifests flow into the overview instead.

## Development

```bash
cd tools/code2md
uv run pytest                 # with coverage
uv run pytest --no-cov -q
uv run --extra dev ruff check src tests   # lint
uv run --extra dev mypy src               # type-check
uv run --extra dev bandit -c pyproject.toml -r src  # security lint (medium+: add -ll)
```
