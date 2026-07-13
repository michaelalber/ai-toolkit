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

Then wire it into grounded-code-mcp in two steps:

**1. Register the collection** (one-time, per project) in your **user** config
(`~/.config/grounded-code-mcp/config.toml`). `search_knowledge` validates its `collection`
argument against the `[collections]` allowlist, so without this the prose overview is not
searchable (code *is*, because `search_code_examples` skips the allowlist):

```toml
[collections]
# value = the ingest --collection name below
"sources/projects/myapp" = "project_myapp"
```

This lives in the user config, not the committed project config — project snapshots are
machine-specific and churny.

**2. Ingest** (the tool prints this line for you):

```bash
grounded-code-mcp ingest /tmp/code2md/myapp --collection project_myapp
```

`--collection` overrides path-based collection derivation, producing `grounded_project_myapp`.
Keep the output directory **outside** grounded-code-mcp's committed `sources/` tree. Re-running
is cheap: grounded-code-mcp's SHA-256 change detection re-ingests only files that changed.

> The MCP server reads `[collections]` at startup — restart it after step 1 so
> `search_knowledge` picks up the new collection. (The CLI `grounded-code-mcp search` re-reads
> config each run and needs no restart.)

## Enrichment (optional, LLM) — Phase 1

`code2md enrich` uses a local model to generate **retrieval bridges** — a natural-language
summary and the questions each file answers — that make NL queries land on the right code.
Generated docs go under `_enriched/`, carry provenance (`generated: true`, `model`,
`derived_from`), and **never replace** the real code (the authority). grounded-code-mcp ingests
them unchanged; no server change.

```bash
# scan first, then enrich the scan output
code2md scan ~/AppDev/myapp --out /tmp/scan/myapp --name myapp
code2md enrich /tmp/scan/myapp --model qwen3-coder:30b --ollama-host http://<host>:11434
```

The model is **required** (via `--model` or `CODE2MD_ENRICH_MODEL`) — never hardcoded, since
build-time generation should use your strongest available coding model. Results are SHA-cached
(keyed by code hash + model id), so re-runs only regenerate changed files. See
[`docs/enrichment-design.md`](docs/enrichment-design.md) for the full design (Phases 2–4: an
architecture brief, concept-graph relationships with a verification pass, and an optional
server-side provenance filter).

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
