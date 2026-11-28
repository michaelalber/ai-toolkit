---
date: 2026-01-13
repository: lpn-engine (new repo, location TBD — see §1 Q1)
topic: "LPN-Engine v1 — RAG-grounded, compiler-verified code generation via MCP"
tags: [qraspi, questions, lpn-engine, local-ai]
phase: Questions (Q)
qraspi_project: lpn-engine
status: awaiting-answers

<qraspi-questions-state>
phase: COMPLETE
project_slug: lpn-engine
project_folder: thoughts/shared/qraspi/2026-01-13-lpn-engine/
areas_covered: [functional-scope | quality-attributes | integration | compliance | deployment | domain-model]
question_count: 17
blocking_flagged: 5   # Q1, Q5, Q8, Q13, Q17
context_budget: under-40
file_status: awaiting-answers    # YAML frontmatter stays awaiting-answers until human fills all A: lines
</qraspi-questions-state>

---

# Questions: LPN-Engine v1

## How to use this file
Answer each question inline on its `**A:` line. Resolve every [BLOCKING] item before
Research. Leave non-blocking items unanswered only if you accept the agent's stated assumption.

## Open questions

### Functional scope
1. [BLOCKING] Where does the lpn-engine repo live? New standalone repository, subdirectory under `ai-toolkit` (e.g., `lpn-engine/`), or elsewhere? The v1 plan (§5) sketches a layout but does not commit to a location. This affects CI config, dependency management, and path conventions throughout every phase.
    **A:** A subdirectory under the ai-toolkit, lpn-engine

2. Should the verifier pool default to LSP-backed semantic checks (pylsp, typescript-language-server, phpactor) when they install cleanly during Phase 2, or stay parse-only CLI verifiers? The v1 plan (§10, §12.2) makes this a pre-Phase-2 decision; Research needs to evaluate both paths now so Architecture can lock one.
    **A:**

3. Ingest is specified as a standalone script (`ingest/chunk.py`). Should ingest also be exposed as an API endpoint (`POST /ingest`) in addition to the CLI, or stay CLI-only for v1?
    **A:**

4. The repair loop fires on verifier failure with up to 3 retries (§11.3). Should the engine support a "silent success" mode — return after any number of retries without reporting attempt count to the client — or is the attempt log always returned (current design)?
    **A:**

### Quality attributes (the -ilities)
5. [BLOCKING] The v1 plan (§3.1) benchmarked the MoE generator at ~4k context. At realistic prompt sizes (16–32k with doc context), does the target Mac mini M4 Pro 48 GB have sufficient headroom for qwen3.6-35b + snowflake-arctic-embed2 co-resident + KV caches? The v2 roadmap (§C) flags ~43 GB before KV — any constraint here affects phase ordering and whether skeleton includes context-window guardrails.
    **A:**

6. Target end-to-end latency for the MCP tool response. With a generate → verify → repair loop, what is the acceptable upper bound that still makes "inline editor assistance" useful? This shapes whether Phase 5 needs streaming progress notifications (deferred per §10).
    **A:**

7. Availability: should lpn-engine auto-start on boot (systemd launchd service) or run manually when needed? Affects skeleton's deployment artifacts.
    **A:**

### Integration / external systems
8. [BLOCKING] Ollama and Qdrant hosts are specified by LAN IP in the v1 plan (§3: `192.168.42.165`). Should these be resolvable via hostname (e.g., `ollama.local`, `qdrant.local`) or environment variables rather than hardcoded IPs? The v1 plan says "env vars only" in §8 but the module contracts (§11.3) bake IPs into defaults.
    **A:**

9. Roslyn sidecar port: v1 plan defaults to `5100`. Is this port available on the target box, or does it conflict with an existing service? Affects Phase 1 and Phase 2 skeleton.
    **A:**

10. Which repos will be ingested first for testing? The ingest + retrieve gate (§4) requires "one real repo per language." Research needs concrete repos to validate the tree-sitter chunker against actual codebases, not just `tests/fixtures/`.
    **A:**

### Compliance / regulatory
11. The overview states "no cloud, no data leaving our network." Are there any formal compliance frameworks (NIST 800-53, CUI handling, FIPS) that apply to this engine, or is it internal-only with privacy-by-architecture sufficient for v1? This determines whether the federal overlay skill applies to Architecture phase ADRs.
    **A:**

12. Generated code carries citations back to internal documentation. Is there a concern about citation leakage — e.g., returning documentation snippets in the response alongside or instead of doc IDs, exposing proprietary content to the editor client? Current design (§7) returns only doc ID strings.
    **A:**

### Deployment / runtime target
13. [BLOCKING] Service port: v1 plan uses `8899` for the REST/MCP endpoint (see §11.6 gate commands). Confirm this is available and desired, or specify a different port or socket path.
    **A:**

14. The v1 plan requires external binaries on PATH: `node`, `rustc`, `php`, `dotnet` SDK ≥ 8. Which of these are already installed on the Mac mini? PHP is flagged "⚠️ VERIFY: not installed" (§3.2). Research needs to confirm availability so Architecture can decide whether PHP verifier ships as a `# VERIFY` skip or requires installation in Phase 1.
    **A:**

15. Process management: Python virtual environment (venv) managed how — `uv run`, manual activation, containerized? This affects the skeleton's startup script and CI config.
    **A:**

### Data & domain model
16. Qdrant persistent storage path: where does the `lpn_docs` collection live on disk? Mirror grounded-code-mcp's pattern (separate persistent volume) or let Qdrant use its default? Affects ingest reproducibility and whether a fresh session can re-ingest without losing prior data.
    **A:**

17. [BLOCKING] Document chunking: tree-sitter "symbol" extraction — what counts as a symbol per language? E.g., Java: class + method; Rust: fn + impl block + trait; Python: top-level def + class; PHP: function + class/method; C#: class + method/property. Should nested functions, private members, and macros be included or excluded? This shapes the chunker's AST traversal logic in Phase 4.
    **A:**

## Assumptions (only if not answered above)
- If Q2 is unanswered: default to CLI-based verifiers (parse/lint level); defer LSP swap as a post-v1 item per §10.
- If Q3 is unanswered: ingest stays CLI-only (`python -m ingest.chunk`). API endpoint added only if Phase 5 reveals user demand for it.
- If Q4 is unanswered: attempt log always returned in response (current design).
- If Q6 is unanswered: no explicit upper bound; v1 prioritizes correctness over latency.
- If Q7 is unanswered: manual start only (no daemon); user runs it when needed.
- If Q8 is unanswered: env vars with hardcoded IP as fallback default only for initial development.
- If Q9 is unanswered: `5100` assumed available; test at Phase 2 startup and fail loud if port is bound.
- If Q10 is unanswered: agent will propose repos at Research phase based on language availability.
- If Q14 is unanswered: assume `node`, `rustc`, `dotnet` installed; PHP not installed — ship verifier as `# VERIFY` skip for v1.
- If Q15 is unanswered: use `uv` (venv in `.venv/`, `uv run python -m lpn.mcp_server`).
