# Skills on Local Inference (PI + Ollama) — Triage

Classifies every skill in `skills/` by how well it performs under **PI on a local
Ollama 32B model**, where the model is weaker at planning, sustained multi-turn
coherence, and judgment than a frontier cloud model, and the context window is
smaller (32K–128K vs. 200K+).

**This is a routing guide, not a fork.** The skill *format* is identical across
Claude Code, OpenCode, and PI (the Agent Skills standard). Skills ship from the
single `skills/` source tree. This doc decides which to expose, which to trim into
a lite variant under `pi/skills/`, and which to leave for cloud.

---

## Target environment (assumptions)

| | |
|---|---|
| Hardware | Mac Mini, 48 GB unified memory |
| Primary model | `qwen2.5-coder:32b` (~20 GB Q4 + q8 KV cache) — "best code quality locally" |
| Alternates | `devstral-small-2:24b` (128K ctx, strong agentic), `phi4-reasoning:14b` |
| Context window | 128K on the 24–32B tier; **32K** on smaller models — the binding limit |
| Tool calling | Rated "excellent" at this tier — file scaffolding is reliable |

The governing principle: **a skill's local usefulness is inversely proportional to
how much it leans on the model's own reasoning, and directly proportional to how
much procedure it encodes that the model would otherwise botch.**

---

## Legend

| Tier | Meaning | Action |
|------|---------|--------|
| 🟢 **Green** | Bounded, procedural, single-pass. Encodes a checklist/template the model just executes. *More* valuable on 32B — it offloads the planning the model is weak at. | Ship as-is from `skills/`. |
| 🟡 **Yellow** | Single-pass but reasoning-, judgment-, or reference-heavy. Works on 32B, but output is shallower. | Ship, and author a **lite variant** in `pi/skills/` for the ones you use most. |
| 🔴 **Red** | Long multi-phase autonomous loops or parallel subagent fan-out. Coherence/tooling demands exceed sustained 32B capability. | Don't expose for unattended use locally. Run on cloud, or drive interactively one step at a time. |

**Flags:** 📚 depends on `grounded-code-mcp` (degrades to training-data fallback if
the MCP isn't running locally) · 🧩 relies on parallel subagents (PI support
uncertain; 32B can't sustain fan-out) · ⚠️ already deprecated in the toolkit.

---

## 🟢 Green — ship as-is (40)

These get *more* reliable on a weak model because the skill carries the procedure.

| Skill | Flags | Why it fits local |
|-------|-------|-------------------|
| cargo-package-scaffold | | Bounded scaffold + CI template; fixed step sequence |
| nuget-package-scaffold | 📚 | Bounded scaffold; MCP only enriches conventions |
| pypi-package-scaffold | 📚 | Bounded scaffold |
| php-package-scaffold | 📚 | Bounded scaffold |
| mcp-server-scaffold | | FastMCP template; deterministic structure |
| axum-scaffolder | 📚 | Typed-endpoint scaffold, compile-time verified |
| fastapi-scaffolder | 📚 | Router + Pydantic template |
| minimal-api-scaffolder | 📚 | Endpoint template |
| dotnet-controller-api-scaffolder | 📚 | Conforms to detected conventions; mechanical |
| php-api-scaffolder | 📚 | Laravel endpoint template |
| react-app-scaffolder | 📚 | Vite app skeleton; fixed layout |
| react-component-scaffolder | 📚 | Single component + test; tightly bounded |
| dotnet-vertical-slice | 📚 | Feature-folder CQRS scaffold; procedural |
| python-feature-slice | 📚 | Feature-folder scaffold |
| php-feature-slice | 📚 | Feature-folder scaffold |
| rust-feature-slice | 📚 | Feature-module scaffold |
| react-feature-slice | 📚 | Feature-folder scaffold |
| test-scaffold | | Naming/mock conventions; template-driven |
| ef-migration-manager | | Lifecycle checklist with safety gates |
| alembic-migration-manager | 📚 | Lifecycle checklist |
| sqlx-migration-manager | 📚 | Lifecycle checklist + query verification |
| php-migration-manager | 📚 | Lifecycle checklist |
| environment-health | | Docker/service diagnostics; deterministic checks |
| ollama-model-workflow | | Local LLM mgmt — *purpose-built* for this setup |
| session-context | | Git summarization + ADR matching; bounded |
| to-issues | | PRD → atomic issues; bounded decomposition |
| triage-issue | | Severity/root-cause classification; bounded |
| jira-review | | Readiness checklist; bounded |
| jira-comment-writer | | Plain-language rewrite — bounded transform, ideal for local |
| architecture-journal | 📚 | ADR template fill + retro prompts |
| anomaly-detection | 📚 | Statistical detection code gen; procedural |
| sensor-integration | 📚 | I2C/SPI/UART pipeline code; procedural |
| picar-x-behavior | | Composable behavior code gen; bounded |
| supply-chain-audit | 📚 | Tool-driven scan (cargo-audit/npm/pip); mechanical |
| zoom-out | | Map callers/dependents; bounded read |
| caveman | | Terse mode switch — *cuts* token use, a net win locally |
| tdd | | The RED-GREEN-REFACTOR discipline — exactly the guardrail a weak model needs |
| qrspi-questions | | Surface unknowns; bounded interactive Q&A |
| qraspi-questions | | Surface unknowns (greenfield) |
| qraspi-skeleton | | Walking-skeleton scaffold from accepted ADRs |

---

## 🟡 Yellow — usable, author a lite variant (52)

Single-pass but lean on judgment, synthesis, or large reference/input loads. The
32B model produces the *structure* of a good result with shallower content. The
lite-variant recipe: trim SKILL.md, inline the output template, cut reference hops,
make steps explicit and imperative (the same treatment that produced `AGENTS-lite.md`).

| Skill | Flags | Local caveat |
|-------|-------|--------------|
| architecture-review | 📚 | Socratic critique needs the model to *be* the expert; shallower challenges |
| dotnet-architecture-checklist | | Checklist exec; interpretation is judgment |
| python-architecture-checklist | | Checklist exec |
| php-architecture-checklist | | Checklist exec |
| rust-architecture-checklist | | Checklist exec |
| react-architecture-checklist | | Checklist exec |
| dependency-mapper | 📚 | Metrics are mechanical; the interpretation is judgment |
| technical-debt-assessor | 📚 | Cost/interest estimation needs judgment |
| improve-codebase-architecture | | Deep APOSD refactor reasoning |
| fitness-functions | | Authoring arch tests + CI wiring; multi-file |
| evaluate-tests | | Judges test quality against Beck criteria |
| doc-sync | | Staleness detection + generation; judgment |
| dotnet-security-review | | Exploitability judgment; tooling is mechanical |
| python-security-review | | Exploitability judgment |
| php-security-review | | Exploitability judgment |
| rust-security-review | | Exploitability + `unsafe` audit judgment |
| react-security-review | | Exploitability judgment |
| security-review-federal | | NIST overlay on a base review; heavy reference load |
| automated-code-review | 📚 | Single-pass review engine; finding quality varies |
| legacy-migration-analyzer | 📚 | Assessment + plan synthesis |
| python-modernization-analyzer | 📚 | Assessment + plan synthesis |
| react-modernization-analyzer | 📚 | Assessment + plan synthesis |
| rust-migration-analyzer | 📚 | Assessment + plan synthesis |
| 4d-schema-migration | 📚 | DDL gen is mechanical; UI/entity mapping is judgment |
| rag-pipeline-dotnet | 📚 | Multi-step build, reference-heavy |
| rag-pipeline-python | 📚 | Multi-step build (note: Ollama-native — good local fit) |
| confluence-guide-writer | 📚 | Doc synthesis; bounded by source but prose-quality-sensitive |
| transcript-capture | 📚 | **Large input** — full transcript can saturate a 32K window |
| email-capture | 📚 | **Large input** — full thread can saturate a 32K window |
| capture-consolidate | 📚 | Dedup + contradiction detection across docs; judgment |
| to-prd | | Synthesis from notes; judgment |
| pr-feedback-writer | | Communication coaching; needs nuance |
| spec-coach | 📚 | Interactive coach — needs the model to coach well |
| skill-creator | 📚 | Meta; must follow the 5-section template precisely |
| tdd-pair | 📚 | Role-based collaboration; multi-turn nuance |
| model-optimization | 📚 | Quantization/benchmark workflow; multi-step |
| edge-cv-pipeline | 📚 | Multi-step CV pipeline build |
| jetson-deploy | 📚 | Multi-step deploy + TensorRT conversion |
| fleet-management | 📚 | Rollout/rollback strategy; complex |
| research-synthesis | | Multi-source cross-referencing + credibility scoring |
| system-design-kata | | Design practice; model must act as examiner |
| pattern-tradeoff-analyzer | | Tradeoff reasoning |
| refactor-challenger | | Prioritization judgment |
| code-review-coach | 📚 | Compares to "expert analysis" — only as good as the model |
| security-review-trainer | 📚 | Generates subtle vulns + scores findings |
| grill-me | | Socratic interview; multi-turn judgment |
| domain-model | | DDD interrogation; judgment |
| qrspi-spec | | Design brain-dump + structure outline |
| qrspi-plan | | Spec → executable sliced plan; judgment |
| qraspi-plan | | Slice plan (greenfield) |
| qraspi-architecture | | Lock ADRs + C4 diagrams; design judgment |
| qraspi-graduate | | Greenfield→brownfield handoff; judgment |

---

## 🔴 Red — not for unattended local use (11)

Long autonomous loops, parallel subagent fan-out, or already-deprecated skills.
Run these on a cloud model — or, for the implement phases, drive them **interactively
one slice at a time** (the per-slice fresh-session checkpoints actually help a small
model, but the unattended loop will drift).

| Skill | Flags | Why not local |
|-------|-------|---------------|
| tdd-agent | 📚 | Fully autonomous RGR loop; loses discipline over many turns |
| task-decomposition | 🧩 | Multi-agent orchestration; PI subagent support uncertain |
| qrspi-implement | | Slice-by-slice autonomous loop with checkpoints |
| qraspi-implement | | Slice-by-slice autonomous loop (greenfield) |
| qrspi-research | 🧩 | Parallel read-only subagent fan-out |
| qraspi-research | 🧩 | Parallel subagent fan-out (greenfield) |
| rpi-research | ⚠️🧩 | Deprecated → use qrspi-research; also subagent-based |
| rpi-plan | ⚠️ | Deprecated → use qrspi-plan |
| rpi-implement | ⚠️ | Deprecated → use qrspi-implement |
| rpi-iterate | ⚠️ | Deprecated → edit spec + re-run qrspi-plan |
| spec-implement | ⚠️📚 | Deprecated → use QRSPI/QRASPI; autonomous |

---

## Cross-cutting notes

**`grounded-code-mcp` (📚 — 50 skills).** Roughly half the library cites the local
RAG server for authoritative grounding. It is itself a local server, so running it
on the Mac Mini keeps these skills fully functional offline. Without it, 📚 skills
silently fall back to the 32B model's training data — acceptable for scaffolders,
risky for the security and migration skills where the grounded standard *is* the value.
**Recommendation: run `grounded-code-mcp` locally.**

**Subagents (🧩).** Several research/orchestration skills assume parallel read-only
subagents. Confirm PI's subagent support before relying on these; if absent, they
collapse to single-threaded and lose their speed/coverage rationale.

**Context window.** On the 32K tier, watch the large-input 🟡 skills
(`transcript-capture`, `email-capture`) and any skill that loads multiple long
`references/` files mid-task — both can saturate the window and trip PI's compaction
loop. The 24–32B/128K tier removes most of this risk.

**Deprecated (⚠️).** The `rpi-*` and `spec-implement` skills are superseded by QRSPI
(brownfield) and QRASPI (greenfield). Don't invest in local variants of these.

---

## Recommended next steps

1. **Wire `install-pi.sh`** to deploy the shared `skills/` tree to PI's skill dir
   (it currently installs no skills). Single source of truth — no fork.
2. **Stand up `grounded-code-mcp` locally** to keep the 50 📚 skills functional offline.
3. **Author lite variants** in `pi/skills/` for the handful of 🟡 skills you actually
   use most — start with the security reviews and architecture checklists, since those
   are the highest-value/highest-judgment combination.
4. **Suppress the 🔴 tier locally** (don't install, or mark them cloud-only) and reach
   for a cloud model when you need an autonomous loop or subagent fan-out.

> Counts: 🟢 40 · 🟡 52 · 🔴 11 = 103. Revisit when skills are added/removed or the
> primary local model changes.
