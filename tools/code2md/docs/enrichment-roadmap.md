# code2md Enrichment Roadmap & Status

Working tracker for the phased LLM-enrichment effort. **The design rationale lives in
[`enrichment-design.md`](enrichment-design.md); this file is the execution state** — what's done,
what's next, and the concrete steps/acceptance for each phase. Update the status line and the
"Delivered / Next actions" of a phase as work lands.

**Status legend:** ✅ done · 🚧 in progress · ⬜ planned · ⏸ blocked

---

## Cross-cutting decisions (locked — apply to every phase)

1. **Bridge, not authority.** Generated text is embedded/matched to improve recall and may ride
   along in context, but the real source code is always the citation and wins on conflict.
2. **Provenance on everything generated:** front-matter `generated: true`, `model`, `generated_at`,
   `derived_from: <real path>`. Filterable, rebuildable, auditable.
3. **Separation.** Generated docs live under `_enriched/` in the *project* collection only; never
   contaminate `is_code` chunks or vetted shared collections.
4. **SHA-keyed caching** (code hash + model id) → re-runs only touch changed files.
5. **Models & prompts are config/versioned, never hardcoded.** Model required via `--model` /
   `CODE2MD_ENRICH_MODEL`. Prompts in `src/code2md/prompts/*.txt`.
6. **Model tiering.** Use the **strongest** model at build time (errors here poison retrieval
   permanently); the 30B local model is only the *runtime* consumer.
7. **Cloud is opt-in and privacy-gated.** Ollama Cloud (bigger models) is allowed for
   **non-sensitive/OSS** code; keep **proprietary/CUI local**. Local is the default. API key from
   `OLLAMA_API_KEY` **env only** (never a flag — flags leak to `ps`/history), never logged.

---

## Phase 1 — per-file summaries + questions ✅ DONE

Shipped in `ai-toolkit` commit **92a59b9** (`main`).

**Delivered**
- `code2md enrich <scan-dir>` subcommand (CLI split into explicit `scan` + `enrich`).
- `enrich/`: `ollama_client.py`, `config.py`, `scandoc.py`, `cache.py`, `summarize.py`;
  prompt `prompts/summarize.txt`.
- Per-file `_enriched/<path>.enriched.md` = NL summary + "questions this file answers" + key
  symbols, prose (`is_code=False`), with provenance + `derived_from`.
- **No grounded-code-mcp changes** — ingested as-is.

**Verified**
- 49 tests, 93% coverage.
- Live `qwen3-coder:30b` (Mac Mini): faithful summaries, no hallucination in sample.
- Bridge payoff: NL query *"what happens when a file fails to parse during ingestion"* →
  the enriched doc **outranked** the raw code (0.4734 vs 0.4363), both → `ingest.py`.
- Isolation: prose enrichments absent from `search_code_examples`.

**Deferred follow-ups**
- Full 37-file enrich of the `grounded_code_mcp` scan (only 3 files enriched so far).
- Cloud-model support (see Cross-cutting backlog).

---

## Phase 2 — project architecture brief ⬜ PLANNED

**Goal.** One LLM-synthesized prose doc per project that *augments* (never replaces) the mechanical
`_overview.md` — system purpose, major components + interactions, entry points, notable patterns.

**Artifact.** `_enriched/_architecture.md`, `kind: architecture-brief`, standard provenance.

**Inputs.** The mechanical `_overview.md` (deps/counts/module map stay authoritative) + the Phase 1
per-file summaries (cheaper and more faithful than re-reading all code).

**Steps.**
1. `enrich/architecture.py`: gather overview + `_enriched/*.enriched.md` summaries → prompt.
2. `prompts/architecture.txt` (versioned).
3. Wire into `enrich` behind `--level`/flag; cache by hash of the inputs + model.

**Acceptance.** Brief names the real top-level components (cross-check against module map); deps and
counts remain sourced from the mechanical overview; provenance present; reads as reviewable prose.

---

## Phase 3 — concept-graph relationships ⬜ PLANNED  ← the "graph stuff"

**Goal.** Generate per-project `RELATIONSHIPS.md` feeding grounded-code-mcp's concept graph
(`query_graph`) — pre-computed multi-hop structure, the biggest win for a 30B runtime model and the
highest-risk artifact (a bad edge injects false *routing*, not a false fact).

**⚠️ Pre-requisite — VERIFIED 2026-07-06: the linkage is BROKEN system-wide.** Blocks Phase 3.

Graph expansion in `search_knowledge` matches `source_path.startswith(slug + "/")` (server.py:344),
where `slug` is run through `slugify()` — which strips `/` and `.` and maps `_`→`-`
(graph_store.py:158-161). But graph node `source_slug`s are **document-name slugs**
(`google-aip`, `wcag-22`, `zalando`), while chunk `source_path`s are **collection-prefixed**
(`api-design/google-aip/121.md`). A path starting `api-design/` can never `startswith("google-aip/")`,
so expansion matches **nothing** — confirmed live: a query strongly matching the 27-edge concept
`resource-oriented-design` returned only `[vector]` hits, zero `[graph-expanded]`. (`query_graph`
traversal works; only the `search_knowledge` auto-expansion is dead.) The existing slugs are also
often semantically wrong (`resource-oriented-design` → `source_slug: wcag-22`).

For our project it's doubly broken: chunks live at `projects/grounded_code_mcp/...`; `slugify` can't
hold a `/`, so no clean per-project slug prefix-matches a two-segment path (only the too-broad
`projects` would, bleeding across all projects).

**DECISION (2026-07-06): (C) both — (A) now to unblock Phase 3, (B) as the real fix in Phase 4.**

Options:
- **(A) Restructure project scan output to a top-level, pre-slugified dir** `sources/<project-slug>/`
  (hyphens, no underscores) so `source_path = "<project-slug>/..."` and a triple `source_slug` of
  `<project-slug>` resolves uniquely. Revisits the earlier `sources/projects/<name>` choice + the
  config key. Fixes *our* project only; contained; no server change.
- **(B) Fix grounded-code-mcp (recommended long-term).** Store a `source_slug`/collection token on
  each chunk at ingest and match graph expansion on *that* instead of a `source_path` prefix — repairs
  expansion for **every** collection (currently all broken), not just projects. Server change → fold
  into Phase 4. Also fix the distillation that assigns wrong slugs.
- **(C) Both:** (A) unblocks Phase 3 now; (B) is the real fix, scheduled in Phase 4.

**Artifact & format (fixed by the existing parser — `graph_builder.py`).** Quoted triples:
```
## <name>  <!-- domain: architecture -->
"IngestionPipeline" → orchestrates → "DocumentParser" [<source_slug>] [architecture] [] [ingest.py: parse step]
```
Bracket order: `[source_slug] [domain] [type] [description]`.
- **verb** must normalize into `VALID_RELATIONS` (~100, `graph_store.py:48-152`) — invalid verbs are
  **silently dropped**, so feed the exact list into the extraction prompt.
- **domain** ∈ `VALID_DOMAINS` (15, `graph_store.py:19-37`); no project domain → use `architecture`
  (or the project language when it matches). Adding a project domain = optional server change.
- **type** ∈ {pattern, principle, practice, anti-pattern} — leave blank for concrete code entities.
- **source_slug** (1st bracket) = per-edge source attribution guardrail; set per the pre-req.

**Verification pass (required).** Second model call per triple: "Here is the code at `<derived_from>`
— does it support `<A> <rel> <B>`? yes/no + line." Drop on no. This is the guard against hallucinated
routing.

**Model.** Strongest available — **this is the phase most justified for an Ollama Cloud model**;
extraction quality here has the largest and most permanent impact.

**Steps.**
1. Verify `source_slug` linkage (pre-req) — small experiment against a known collection.
2. `enrich/relationships.py` (extract) + `enrich/verify.py` (verification pass);
   `prompts/relationships.txt`, `prompts/verify_edge.txt` (both inject the controlled vocab).
3. Emit `RELATIONSHIPS.md` at the project scan root; `grounded-code-mcp ingest --force` /
   `build-graph` rebuilds the graph.

**Acceptance.** ≥90% of a sampled edge set is supported by its cited code (post-verify); every edge
carries a resolving `source_slug`; `query_graph` on a seeded concept returns project relationships;
graph expansion in `search_knowledge` pulls the right project chunks.

---

## Phase 4 — server-side provenance filter ⬜ PLANNED (optional)

**Goal.** Make generated context server-side filterable (include/exclude) instead of only
identifiable by `_enriched/` path prefix + front-matter.

**grounded-code-mcp changes** (the only phase that touches the server):
- Add a `generated` boolean to the chunk payload (`vectorstore.py` add_chunks) + a search filter.
- Optional: a project/`codebase` entry in `VALID_DOMAINS`; optional hard `derived_from` metadata for
  citation.

**Acceptance.** `search_knowledge` can include/exclude generated chunks; `search_code_examples`
stays clean by construction; vetted collections unchanged.

---

## Cross-cutting backlog

- ⬜ **Ollama Cloud support** (needed for Phases 2–3 build-time quality): optional `Authorization:
  Bearer` in `OllamaClient` from `OLLAMA_API_KEY` env (unlogged); configurable base URL /
  `--cloud`; default local (inert unless configured); README + design-doc notes; tests. Note the
  zero-code path: signed-in local Ollama + a `…-cloud` model tag proxies to cloud already.
- ⬜ Full-repo enrich of the `grounded_code_mcp` scan (~9 min warm) once Phase 1 follow-up is wanted.
- ⬜ Recall eval harness: labelled NL-question → expected-file set, measuring hit@k with vs without
  enrichment (Phase 1 acceptance criterion in the design doc).

## Open decisions

- Whether `enrich` grows a single `--level summaries|architecture|graph|full` flag or separate
  subcommands per phase.
- Whether to add a project domain to grounded-code-mcp `VALID_DOMAINS` (Phase 3/4) or stay on
  `architecture`.

## Next action

**Phase 3 pre-req is done — it failed: graph expansion is broken system-wide** (see Phase 3).
Decision made: **(C) both.** Immediate work = **(A)** restructure project scan output to a top-level
slugified dir `sources/<project-slug>/` so `source_path`/`source_slug` resolve cleanly:
1. Change code2md default out + docs from `sources/projects/<name>` to `sources/<project-slug>/`
   (hyphenated); update the ingest guidance + config-key example.
2. Migrate the existing `grounded_code_mcp` scan/collection to the new layout.
3. Then build Phase 3 relationship extraction + verification, with Ollama Cloud as the build model.
**(B)** the grounded-code-mcp chunk↔slug matching fix is scheduled in Phase 4.
