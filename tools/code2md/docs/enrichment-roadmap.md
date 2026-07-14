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
- Live `qwen3-coder:30b` (local 30B host): faithful summaries, no hallucination in sample.
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

## Phase 3 — concept-graph relationships 🚧 GENERATION DONE — live ingest/acceptance pending on the KB host  ← the "graph stuff"

> **Status (2026-07-13):** slices 1–6 are **merged to `main`** via merge commit **`7dbdf1b`**
> (`feat/code2md-graphrag-slug-layout`, branch since deleted); the grounded `exclude_filenames` change
> (slice 6) is **confirmed merged on grounded `main`**. **Slice 7 generation is done and validated** —
> a full grounded-code-mcp scan enriched on the mac-mini Ollama produced a **269-edge, 0-failed
> `RELATIONSHIPS.md`**, every edge with a resolving `source_slug` and a 16/16 spot-check of accuracy
> (details in slice 7 below). **Remaining:** the live half — `ingest --force` → `query-graph` →
> graph-expanded `search` — runs on the mac-mini KB host, plus the 2-segment layout caveat in slice 7.

**Goal.** Generate per-project `RELATIONSHIPS.md` feeding grounded-code-mcp's concept graph
(`query_graph`) — pre-computed multi-hop structure, the biggest win for a 30B runtime model and the
highest-risk artifact (a bad edge injects false *routing*, not a false fact).

**✅ Pre-requisite UNBLOCKED (2026-07-05).** Work item (A) shipped (branch
`feat/code2md-graphrag-slug-layout`): the scan dir is now a single hyphenated segment
`sources/<project-slug>/`, so each chunk's `source_path` prefix equals the graph builder's
default `source_slug = slugify(parent-dir-name)` (`graph_builder.py:182`), which
`search_knowledge` matches verbatim (`server.py:344`). The original diagnosis is kept below for
context; (B) — the general server-side fix for the *other* collections — remains scheduled in
Phase 4.

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

**Decisions locked (2026-07-05).**
- **Extraction granularity: per-file, name-merged.** Extract the relationships each source file
  participates in (the file is the authority + the verification `derived_from`); cross-file edges
  merge automatically because concept ids are `slugify(name)`. Only approach compatible with the
  mandatory per-edge verification and Phase-1-style per-file caching.
- **CLI: `--level {summaries,graph,full}` on `enrich`** (default `summaries` = today's behaviour;
  `graph` = relationships + verify; `full` = both). Adds `--verify-model`.
- **Model tiering: cloud extract + local verify.** Extraction via a `<model>-cloud` Ollama tag
  (zero-code cloud path — no `Authorization` header work needed now; that stays backlog); verify on
  the local model. grounded-code-mcp is OSS, so cloud is within the privacy gate.
- **RELATIONSHIPS.md is graph-feed only.** Add `"RELATIONSHIPS.md"` to grounded's `config.toml`
  `exclude_filenames` so `ingest` parses it into the graph but does **not** embed it as a vector
  chunk (structured triples would be retrieval noise). Small cross-repo change — the design doc's
  "no server changes for Phase 3" note is amended by this.

**Steps (TDD slices, RED→GREEN each).**
1. `enrich/relationships.py`: `Triple`, `normalize_relation` (mirror parser; drop non-`VALID_RELATIONS`
   locally + log), defensive `parse_extraction_json`. Vendor `VALID_RELATIONS`/`VALID_DOMAINS` as
   versioned constants (separate repo → can't import grounded; a test pins samples + points at
   `graph_store.py`).
2. `render_relationships(...)` → parser-valid quoted triples + section headers + provenance
   front-matter; a **vendored copy of the parser regex** in the test proves parseability.
3. `prompts/relationships.txt` (injects the verb list + domain constraint) + `extract_relationships`.
4. `prompts/verify_edge.txt` + `enrich/verify.py` (`verify_triple`, `verify_all` drops unsupported).
5. Relationship cache (`relate-manifest.json`, SHA+model) + CLI `--level` wiring → writes
   `sources/<slug>/RELATIONSHIPS.md`, prints the `ingest --force` / `build-graph` hint.
6. ✅ **DONE + MERGED** — **(grounded repo)** `"RELATIONSHIPS.md"` added to `config.toml`
   `exclude_filenames` so the ingest scan skips it while `graph_builder`'s own rglob still parses it
   into the concept graph (graph-feed only, never an embedded vector chunk). RED→GREEN pair committed
   on grounded-code-mcp branch `feat/exclude-relationships-md-embedding` (`df7eceb` test, `b98e89a`
   feat). **Confirmed merged to grounded `main` (2026-07-13)** — `RELATIONSHIPS.md` is present in the
   committed `config.toml` `exclude_filenames`; PR #2 can be closed.
7. 🚧 **GENERATION DONE (2026-07-13); live ingest/acceptance pending on the mac-mini KB host.**
   - ✅ **Generated + validated:** local extract + local verify (`qwen3-coder:30b`, 70 min) on the
     grounded-code-mcp scan → **`RELATIONSHIPS.md` with 269 verified edges from 38/38 files, 0
     failed.** All 269 carry a resolving `source_slug` (`grounded-code-mcp`); domains valid
     (`architecture` 242, `python` 26); a 16-edge spot-check across `chunking.py`/`config.py` was
     **16/16** supported by cited code (≥90% bar met on the generation side). Artifact is **local +
     gitignored** in the (public) grounded repo — synced to the KB host out-of-band, never committed.
   - ⬜ **Live half (runs on the mac-mini KB host):** `ingest --force` → `query-graph "DocumentChunker"`
     → graph-expanded `search`. Blocked only on the operator run.
   - ⚠️ **Layout caveat:** the scan landed at `sources/projects/grounded-code-mcp/` (2-segment). Graph
     expansion matches `source_path.startswith("grounded-code-mcp/")`, so it works **only if** the
     host's `knowledge_base.sources_dir` = `…/sources/projects/` (→ `source_path = grounded-code-mcp/…`).
     If `sources_dir = …/sources/` (as it is for the other collections), paths become
     `projects/grounded-code-mcp/…` and auto-expansion returns nothing — reproducing the documented
     2-segment failure that motivates Phase 4 fix **(B)**. `query-graph` still works either way.
     **Next: use the 1-segment `sources/<slug>/` layout, or land Phase 4 (B).**

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
Decision made: **(C) both.** Work item **(A)** = restructure project scan output to a top-level
slugified dir `sources/<project-slug>/` so `source_path`/`source_slug` resolve cleanly:
1. ✅ **DONE (2026-07-05, uncommitted).** `slugify_name` now mirrors grounded's `slugify()` exactly
   (hyphenated, idempotent → `slugify(dirname) == dirname`); new `collection_suffix()` keeps
   collection names on the underscore convention (`my-app` → `project_my_app`). CLI ingest hint,
   README, and design-doc paths/examples moved from the 2-segment `sources/projects/<name>` to the
   1-segment `sources/<project-slug>/`. 63 tests pass (was 49), 93% cov. `test_models.py` added.
2. ✅ **No separate migration (2026-07-05).** grounded data is being rebuilt from scratch on the
   local host, so the new single-segment `sources/grounded-code-mcp/` layout is picked up on the
   fresh re-scan + re-ingest — no in-place migration of the old `projects/grounded_code_mcp`
   collection needed.
3. ✅ **Phase 3 code MERGED to `main` (2026-07-13, `7dbdf1b`).** Slices 1–6 (generation,
   verification, caching, `--level graph|full` wiring, and the grounded `exclude_filenames` change)
   are on `main`; the `feat/code2md-graphrag-slug-layout` branch has been merged and deleted (local
   + remote). ai-toolkit #2 is therefore superseded — **close it if still open.**
   **🚧 Slice 7 generation DONE (2026-07-13); live half pending.** Extract + verify on the
   grounded-code-mcp scan ran on the KB-host Ollama (`qwen3-coder:30b`, 70 min) →
   **`RELATIONSHIPS.md`, 269 verified edges, 0 failed, uniform `source_slug`, 16/16 spot-check.**
   Artifact is local + gitignored (public repo — never committed); synced to the KB host out-of-band.
   **Remaining (operator, on the KB host):** `ingest --force` → `query-graph "DocumentChunker"` →
   graph-expanded `search`, then the Phase 3 acceptance check. See the slice-7 **layout caveat**: the
   2-segment `sources/projects/` output only graph-expands if the host `sources_dir` = `…/sources/projects/`;
   otherwise switch to the 1-segment `sources/<slug>/` layout or land Phase 4 (B).
   grounded-code-mcp #2 (`exclude_filenames`, slice 6) is **confirmed merged on grounded `main`** —
   the graph feed depends on it; PR can be closed.
   ✅ **Tooling gate landed on `main` (2026-07-13).** The repo-wide ruff/mypy/bandit baseline for
   the four `tools/` utilities merged via **ai-toolkit #3** (`chore/tools-lint-typecheck-baseline`,
   merge `842804b`; branch since deleted); the Phase 3 source stays green under it (`b78646f`).
**(B)** the grounded-code-mcp chunk↔slug matching fix is scheduled in Phase 4.
