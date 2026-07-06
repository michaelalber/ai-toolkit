# code2md Enrichment Design

LLM-generated context to make the RAG store support **smaller (~30B) local models** as the
runtime consumer, without compromising grounded-code-mcp's anti-hallucination guarantee.

---

## Goal & framing

For a frontier model, RAG is a *fact-checker*; for a 30B local model, RAG is its *working
memory*. So the bar for coverage, retrievability, and pre-digestion is higher. The strategy is to
**split cognition by when it happens**:

- **Build time** (offline, once, cached, reviewable) — the *hard* work: summaries, hypothetical
  questions, relationship extraction. Use the **strongest** model available; errors here poison
  retrieval permanently.
- **Run time** (every query, 30B local) — the *easy* work: synthesize an answer over context that
  is already pre-digested, structured, and grounded.

## Invariants (non-negotiable)

1. **Bridge, not authority.** Generated text may be *embedded and matched* to improve recall, and
   may *ride along in context* to reduce the runtime model's synthesis burden — but the real
   source code is always what's cited and what wins on conflict. A generated doc never stands
   alone as the answer.
2. **Provenance on everything generated.** `generated: true`, `model`, `generated_at`, and
   `derived_from: <real path>` in front-matter. Filterable, rebuildable, never mistaken for
   ground truth.
3. **Separation.** Generated docs live under a distinct `_enriched/` subtree in the *project*
   collection only. They never contaminate `is_code` code chunks or the vetted shared collections.
4. **Graph edges are source-attributed and verified.** A wrong edge injects a false *relevance
   judgment* (see Graph section) — the one place generation can corrupt retrieval invisibly.
5. **Cache by content SHA.** Re-enrich only changed files. LLM passes are slow.
6. **Models & prompts are config/versioned, never hardcoded** (project AI/ML standard).

## Architecture — two decoupled phases

```
code2md scan <repo>              (deterministic, existing)
   → sources/<project-slug>/**.md            [code docs — the AUTHORITY]

code2md enrich <scan-dir>        (NEW, LLM, opt-in)
   → sources/<project-slug>/_enriched/**      [summaries + questions — the BRIDGE]
   → sources/<project-slug>/RELATIONSHIPS.md  [graph feed]

grounded-code-mcp ingest sources/<project-slug>   (deterministic, existing)
grounded-code-mcp ingest --force ...  OR  build-graph   (rebuilds the concept graph)
```

`<project-slug>` is a **single, hyphenated** segment (grounded's `slugify()` form) placed
directly under `sources/`, so each chunk's `source_path` = `<project-slug>/…` and a concept-graph
`source_slug` of `<project-slug>` prefix-matches it. A nested `sources/projects/<name>/` layout
breaks graph expansion — a two-segment prefix can't be matched by a single slug.

Generation lives entirely in `code2md`; grounded-code-mcp's ingest stays LLM-free. Adding a second
subcommand means `scan` becomes explicit (`code2md scan <repo>`), a small UX change from today's
flattened form.

---

## Artifact 1 — per-file enrichment sidecar (the bridge)

One prose doc per source file. Prose (`is_code=False`) so it matches natural-language queries the
raw code embeds far from — this is the HyDE / hypothetical-question technique from
`edge-ai/AI_Agents_and_Applications.md` (§8.4.4, §9.4).

Path: `_enriched/<rel>.enriched.md`. Example for `src/grounded_code_mcp/ingest.py`:

```markdown
---
source: grounded-code-mcp
path: _enriched/src/grounded_code_mcp/ingest.py.enriched.md
derived_from: grounded-code-mcp/src/grounded_code_mcp/ingest.py.md
generated: true
model: <build-time model id from config>
generated_at: 2026-07-06T...
tool: code2md/0.2.0
kind: file-summary
---

# Summary
The ingest pipeline orchestrates parse → chunk → embed → upsert, with SHA-256 change
detection so unchanged files are skipped …

# Questions this file answers
- How does ingestion decide whether a file needs re-embedding?
- Where are old chunks deleted when a source is re-ingested?
- How is the collection name chosen for a given source path?

# Key symbols
- `IngestionPipeline.ingest` — entry point; walks the source dir …
- `IngestionPipeline._process_file` — per-file: hash check, chunk, embed, store …
```

`derived_from` is the pointer back to the authority. The same query typically also retrieves the
real code chunk (both live in the collection), so the runtime model gets the digest **and** the
checkable source together.

## Artifact 2 — project architecture brief (the bridge, project-level)

One LLM-synthesized prose doc **augmenting** (not replacing) the mechanical `_overview.md`. Keeps
the deterministic facts (deps, counts, module map) authoritative; adds a reviewed narrative:
system purpose, major components and how they interact, entry points, notable patterns. Path:
`_enriched/_architecture.md`, same provenance front-matter, `kind: architecture-brief`. Low volume
(one per project), high value, easy to eyeball.

## Artifact 3 — RELATIONSHIPS.md (the concept graph feed)

The highest-leverage artifact for a 30B model — it pre-computes the multi-hop structure small
models are worst at — and the highest-risk, so it carries the most rigor.

**Format is fixed by the existing parser** (`graph_builder.py`), quoted form:

```
## <name>  <!-- domain: architecture -->

"IngestionPipeline" → orchestrates → "DocumentParser" [grounded-code-mcp] [architecture] [] [ingest.py: parse step]
"IngestionPipeline" → uses → "EmbeddingClient" [grounded-code-mcp] [architecture] [] [batch embed loop]
"DocumentChunker" → produces → "Chunk" [grounded-code-mcp] [python] [] []
```

Bracket order the parser expects: `[source_slug] [domain] [type] [description]`.

- **source_slug** (1st bracket) = the per-edge source attribution guardrail — set it to the
  project's single-segment chunk `source_path` prefix (`<project-slug>`) so graph expansion
  resolves edges back to real chunks. grounded's `graph_builder` slugifies this value, and
  `search_knowledge` then matches it verbatim as a `source_path` prefix (`server.py:344`), so the
  scan dir must already be in slugified hyphen form — which `code2md`'s `slugify_name` now
  guarantees (`slugify(dirname) == dirname`).
- **domain** must be one of `VALID_DOMAINS` (`graph_store.py:19-37`) — 15 values. There is **no
  project/codebase domain**; use `architecture` for structural concepts, or the project language
  when it matches (`python`, `rust`, `javascript`, `php`). Languages like go/java/cpp/c/etc. have
  no domain → default to `architecture`. (Adding a project domain is an optional server change.)
- **type** (optional) — one of `VALID_TYPES` {pattern, principle, practice, anti-pattern}. Leave
  blank for concrete code entities; a `ConnectionPool` isn't a "pattern".
- **verb** must normalise into `VALID_RELATIONS` (~100 verbs, `graph_store.py:48-152`). Invalid
  verbs emit a WARNING and are **dropped silently** — so the extraction prompt MUST be given the
  exact verb list and told to use only those. The vocabulary maps cleanly to code:
  structural (`contains`, `implements`, `extends`, `composes-with`, `wraps`), data-flow
  (`calls`, `produces`, `transforms`, `triggers`, `uses`, `returns`, `registers`, `resolves`),
  config/persistence (`configures`, `configured-via`, `stored-in`, `caches`, `exposes`).

**Verification pass (required for this artifact).** For each extracted triple, a second model call:
"Here is the code at `<derived_from>`. Does it support `<A> <rel> <B>`? yes/no + the line." Drop on
no. This is the guard against hallucinated *routing* — the trapdoor where a false edge steers
retrieval to real-but-irrelevant code that a 30B model will trust.

---

## Provenance & filtering

- **Zero-server-change path (Phases 1–3):** identify generated content by `source_path` prefix
  (`_enriched/`) + front-matter `generated: true`. Sufficient to keep it out of the vetted
  collections and to rebuild.
- **Full path (Phase 4, optional):** add a `generated` boolean to the chunk payload
  (`vectorstore.py` add_chunks) + a search filter, so retrieval can server-side include/exclude
  generated context. Also lets `search_code_examples` (already `is_code`-filtered) stay clean by
  construction. Small, contained server change.

## Model tiering & config

New `[enrich]` block in config (user or project):

```toml
[enrich]
enabled = false
ollama_host = "http://192.168.42.165:11434"
summary_model = "<strong local coding model>"   # build-time
graph_model   = "<strong local coding model>"   # build-time
verify_model  = "<can be smaller>"              # yes/no grounded check
max_concurrency = 2
```

Prompt templates live in versioned files (`src/code2md/prompts/*.txt`), not f-strings
(AI/ML standard). Model ids come from config — never bare strings in code.

## Caching & incrementality

Mirror the ingest manifest: an enrichment manifest keyed by source file SHA-256. On re-run,
regenerate only files whose hash changed; carry the model id in the cache key so a model change
invalidates. This makes `enrich` cheap to re-run and safe to schedule.

## Guardrails against context-stuffing

30B models have weaker long-context "needle" performance, so enrichment must raise **precision of
what's returned** (better matching + routing), not pile summaries + code + graph neighbours into
the window. Favour tighter, higher-signal returns over more tokens.

---

## grounded-code-mcp changes required

| Phase | Server change |
|---|---|
| 1 — per-file summaries + questions | **None** — markdown ingested as-is |
| 2 — architecture brief | **None** |
| 3 — RELATIONSHIPS.md → graph | **None** — `ingest --force` / `build-graph` already parse it |
| 4 — server-side provenance filter | `generated` payload field + filter; optional project `VALID_DOMAINS` entry; optional hard `derived_from` metadata for citation |

Phases 1–3 need **no** grounded-code-mcp code changes — the enrichment is just more markdown +
a RELATIONSHIPS.md, which the existing pipeline already consumes.

## CLI surface & new modules

- `code2md enrich <scan-dir> [--level summaries|graph|full] [--model ...] [--no-verify]`
- New modules: `enrich/summarize.py`, `enrich/questions.py`, `enrich/relationships.py`,
  `enrich/verify.py`, `enrich/ollama_client.py`, `enrich/cache.py`, `prompts/`.
- `scan` and `enrich` stay independent: deterministic scan cached separately from LLM enrichment.

## Phased rollout

1. **Phase 1** — `enrich` command → per-file summaries + hypothetical questions. No graph, no
   server change. **Ship + measure recall first.**
2. **Phase 2** — project architecture brief.
3. **Phase 3** — RELATIONSHIPS.md extraction + verification pass → graph expansion.
4. **Phase 4** (optional) — server-side provenance field + project domain.

## Acceptance criteria / evals

- **Recall:** a labelled set of NL questions about a project retrieves the correct file at hit@5
  measurably higher **with** enrichment than without.
- **Graph precision:** ≥ 90% of a sampled set of generated edges are supported by their cited code
  (post-verification).
- **Provenance:** 100% of generated docs carry `generated: true` + `model` + `derived_from`.
- **No contamination:** `search_code_examples` (is_code) returns zero generated docs; the vetted
  collections are unchanged.

## Risks & mitigations

| Risk | Mitigation |
|---|---|
| Hallucinated summary | Rides with code; provenance; never sole authority |
| Hallucinated graph edge (false routing) | Per-edge source_slug + verification pass + controlled verb vocab |
| Context stuffing dilutes signal | Precision-first; don't stuff the window |
| Stale enrichment after code change | SHA invalidation; re-enrich changed files only |
| Project language absent from VALID_DOMAINS | Default `architecture`; optional server domain add |
| source_slug ↔ source_path mismatch breaks expansion | Verify against `server.py:342-347` before Phase 3 |
