<!-- <AI-Generated START> -->

# LPN-Engine v2 — Candidate Roadmap (parking lot)

| | |
|---|---|
| **Status** | Icebox — nothing here is committed; each item carries its promotion trigger |
| **Date** | 2026-11-01 |
| **Rule** | v1 (`docs/lpn-engine-v1-plan.md`) ships first. An item moves out of this file only when its trigger fires **and** v1 gates are green |

Deferred ideas gathered during the v1 design pass, so they are not re-proposed (or forgotten)
every planning session. Grouped by theme.

## A. Verification depth (closing v1's honest weakness)

| Item | What it buys | Promotion trigger |
|---|---|---|
| **LSP-backed verifiers** for Python/JS/PHP (mcp-language-server pattern: pylsp, typescript-language-server, phpactor) | Semantic diagnostics replace parse-only — closes the §3.2 strength gap without per-language sidecars | v1 §10 open item resolves "LSP installs cleanly" in Phase 2 |
| pyright / phpstan / `tsc` CLIs | Same goal, CLI flavor — simpler than LSP, weaker than LSP | Only if LSP proves operationally annoying |
| **TypeScript support** (schema language enum + verifier) | 6th language | First TS request from a team |
| Sandboxed **test execution** of generated snippets (never raw exec; container + no network) | "Compiles" → "passes a self-test" | Only when compile-pass rate is high but semantic complaints accumulate |

## B. Generation quality

| Item | What it buys | Promotion trigger |
|---|---|---|
| **Semantic judge** (`granite4.2:30b-q5_K_M` — already on the box): "does the code match the doc intent" LLM check after compile | Catches the class compile can't: right syntax, wrong meaning | Measured: >N% of returned code fails human review for semantic (not syntax) reasons |
| **Regression/eval matrix** via tools/ollama-evals | Real model-benchmark rig instead of the §3.1 single-prompt bench | Becomes *pre-v1* if model comparisons keep recurring (§12.3 #2) |
| Multi-model routing (e.g., MoE first, dense fallback, judge last) | Quality/latency tuning | Only after the eval matrix exists to justify it |
| GBNF grammars per language | Harder syntactic guarantee at the decoding layer | Only if tag-strip + repair loop measurably fails on some model |

## C. Interface & ops

| Item | What it buys | Promotion trigger |
|---|---|---|
| MCP **progress notifications** (streaming repair attempts) | UX during multi-attempt repairs | First user complaint about silent latency; v1 stays unary (§10 open item) |
| Richer ingest metadata (call-graph edges from tree-sitter) | Retrieval of *related* symbols, not just matching ones | Recall complaints on real repos, not fixtures |
| Multi-language per response | Cross-stack features in one call | Actual demand; v1 schema is single-language by design |
| Citation **relevance** check (not just membership): cited IDs must overlap the code's symbols | Catches "cites a real but irrelevant doc" — the one hole the §4 gate leaves open | First observed instance of relevant-but-cited-gaming in review |

## Explicitly staying out (re-propose only with new evidence)

Editor plugins · fine-tuning · executing generated code unsandboxed · behavioral/correctness
guarantees (stays the honest boundary in `docs/lpn-engine-overview.md`).

## Memory-budget note (48 GB box)

Judge + generator coexistence is ~43 GB before KV caches — do not co-run two big LLMs
(v1 plan, model sizing). Any v2 item that adds a second resident model must budget KV at its
configured `num_ctx` first.

<!-- <AI-Generated END> -->
