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
| Alternates | `qwen3.6-35b-a3b-agent` (128K ctx, fast MoE), `qwen3-coder-30b-agent` |
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

## 🟢 Green — ship as-is (38)

These get *more* reliable on a weak model because the skill carries the procedure.

| Skill | Flags | Why it fits local |
|-------|-------|-------------------|
| cargo-package-scaffold | | Bounded scaffold + CI template; fixed step sequence |
| nuget-package-scaffold | 📚 | Bounded scaffold; MCP only enriches conventions |
| pypi-package-scaffold | 📚 | Bounded scaffold |
| php-package-scaffold | 📚 | Bounded scaffold |
| axum-scaffolder | 📚 | Typed-endpoint scaffold, compile-time verified |
| fastapi-scaffolder | 📚 | Router + Pydantic template |
| minimal-api-scaffolder | 📚 | Endpoint template |
| dotnet-controller-api-scaffolder | 📚 | Conforms to detected conventions; mechanical |
| php-api-scaffolder | 📚 | Laravel endpoint template |
| react-app-scaffolder | 📚 | Vite app skeleton; fixed layout |
| vue-app-scaffolder | 📚 | Vite app skeleton; fixed layout |
| react-component-scaffolder | 📚 | Single component + test; tightly bounded |
| vue-component-scaffolder | 📚 | Single SFC + test; tightly bounded |
| dotnet-vertical-slice | 📚 | Feature-folder CQRS scaffold; procedural |
| python-feature-slice | 📚 | Feature-folder scaffold |
| php-feature-slice | 📚 | Feature-folder scaffold |
| rust-feature-slice | 📚 | Feature-module scaffold |
| react-feature-slice | 📚 | Feature-folder scaffold |
| vue-feature-slice | 📚 | Feature-folder scaffold |
| test-scaffold | | Naming/mock conventions; template-driven |
| ef-migration-manager | | Lifecycle checklist with safety gates |
| alembic-migration-manager | 📚 | Lifecycle checklist |
| sqlx-migration-manager | 📚 | Lifecycle checklist + query verification |
| php-migration-manager | 📚 | Lifecycle checklist |
| environment-health | | Docker/service diagnostics; deterministic checks |
| session-context | | Git summarization + ADR matching; bounded |
| jira-review | | Readiness checklist; bounded |
| jira-comment-writer | | Plain-language rewrite — bounded transform, ideal for local |
| architecture-journal | 📚 | ADR template fill + retro prompts |
| supply-chain-audit | 📚 | Tool-driven scan (cargo-audit/npm/pip); mechanical |
| zoom-out | | Map callers/dependents; bounded read |
| tdd | | The RED-GREEN-REFACTOR discipline — exactly the guardrail a weak model needs |
| qrspi-questions | | Surface unknowns; bounded interactive Q&A |
| qraspi-questions | | Surface unknowns (greenfield) |
| qraspi-skeleton | | Walking-skeleton scaffold from accepted ADRs |
| para-file | | Config-driven PARA filing; the actionability decision tree is encoded, so the model just executes it |

---

## 🟡 Yellow — usable, author a lite variant (52)

Single-pass but lean on judgment, synthesis, or large reference/input loads. The
32B model produces the *structure* of a good result with shallower content. The
lite-variant recipe: trim SKILL.md, inline the output template, cut reference hops,
make steps explicit and imperative (the same treatment that produced the lean Pi global).

| Skill | Flags | Local caveat |
|-------|-------|--------------|
| architecture-review | 📚 | Socratic critique needs the model to *be* the expert; shallower challenges |
| dotnet-architecture-checklist | | Checklist exec; interpretation is judgment |
| python-architecture-checklist | | Checklist exec |
| php-architecture-checklist | | Checklist exec |
| rust-architecture-checklist | | Checklist exec |
| react-architecture-checklist | | Checklist exec |
| vue-architecture-checklist | | Checklist exec |
| dependency-mapper | 📚 | Metrics are mechanical; the interpretation is judgment |
| technical-debt-assessor | 📚 | Cost/interest estimation needs judgment |
| improve-codebase-architecture | | Deep APOSD refactor reasoning |
| codebase-design | | Deep-module vocabulary; reference-heavy glossary |
| fitness-functions | | Authoring arch tests + CI wiring; multi-file |
| evaluate-tests | | Judges test quality against Beck criteria |
| doc-sync | | Staleness detection + generation; judgment |
| dotnet-security-review | | Exploitability judgment; tooling is mechanical |
| python-security-review | | Exploitability judgment |
| php-security-review | | Exploitability judgment |
| rust-security-review | | Exploitability + `unsafe` audit judgment |
| react-security-review | | Exploitability judgment |
| vue-security-review | | Exploitability judgment |
| security-review-federal | | NIST overlay on a base review; heavy reference load |
| oss-vetting | 📚 | OSS/SBOM assessment across four frameworks + license matrix; structure holds, framework-mapping judgment is shallower locally |
| automated-code-review | 📚 | Single-pass review engine; finding quality varies |
| legacy-migration-analyzer | 📚 | Assessment + plan synthesis |
| python-modernization-analyzer | 📚 | Assessment + plan synthesis |
| react-modernization-analyzer | 📚 | Assessment + plan synthesis |
| vue-modernization-analyzer | 📚 | Assessment + plan synthesis |
| rust-migration-analyzer | 📚 | Assessment + plan synthesis |
| 4d-schema-migration | 📚 | DDL gen is mechanical; UI/entity mapping is judgment |
| confluence-guide-writer | 📚 | Doc synthesis; bounded by source but prose-quality-sensitive |
| substack-writer | | Multi-pass editorial revision; prose-quality-sensitive, craft judgment shallower locally — drive one pass at a time |
| transcript-capture | 📚 | **Large input** — full transcript can saturate a 32K window |
| email-capture | 📚 | **Large input** — full thread can saturate a 32K window |
| capture-consolidate | 📚 | Dedup + contradiction detection across docs; judgment |
| pr-feedback-writer | | Communication coaching; needs nuance |
| spec-coach | 📚 | Interactive coach — needs the model to coach well |
| skill-creator | 📚 | Meta; must follow the 5-section template precisely |
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
| para-review | | Multi-phase audit + weekly ritual + summarize + archive; works but drift-judgment is shallower locally — drive one mode at a time |

---

## 🔴 Red — not for unattended local use (6)

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
| qrspi-research | 🧩 | Parallel fan-out — but ships a SEQUENTIAL FALLBACK; usable on Pi at 🟡 quality |
| qraspi-research | 🧩 | Same — sequential fallback in the inherited-repo branch |

---

## Cross-cutting notes

**`grounded-code-mcp` (📚 — 38 skills).** Roughly half the library cites the local
RAG server for authoritative grounding. It is itself a local server, so running it
on the Mac Mini keeps these skills fully functional offline. Without it, 📚 skills
silently fall back to the 32B model's training data — acceptable for scaffolders,
risky for the security and migration skills where the grounded standard *is* the value.
**Recommendation: run `grounded-code-mcp` locally.**

**Subagents (🧩).** Pi has no subagents — the docs are explicit that extensions
"cannot spawn child agent instances." Skills assuming parallel read-only fan-out
therefore collapse to single-threaded. The two research phases now carry an explicit
SEQUENTIAL FALLBACK (three ordered passes, each written to a file before the next),
so they remain usable on Pi at reduced objectivity; the rest of the 🧩 tier does not.

**Multi-phase work is fine on Pi.** QRSPI and QRASPI phases are artifact-gated: each
phase is one invocation that reads a markdown artifact and writes the next. That is
Pi-native — `/skill:qrspi-spec` works today, and `/tree` + `/fork` let you branch at a
gate and compare two plans in one session. What does NOT port is the *agents* that
drive phase-to-phase automatically; on Pi the human drives, which is the QRSPI design
anyway. See the Pi capability boundary in the root `AGENTS.md`.

**Context window.** On the 32K tier, watch the large-input 🟡 skills
(`transcript-capture`, `email-capture`) and any skill that loads multiple long
`references/` files mid-task — both can saturate the window and trip PI's compaction
loop. The 24–32B/128K tier removes most of this risk.

---

## Recommended next steps

1. **Wire `install-pi.sh`** to deploy the shared `skills/` tree to PI's skill dir
   (it currently installs no skills). Single source of truth — no fork.
2. **Stand up `grounded-code-mcp` locally** to keep the 38 📚 skills functional offline.
3. **Author lite variants** in `pi/skills/` for the handful of 🟡 skills you actually
   use most — start with the security reviews and architecture checklists, since those
   are the highest-value/highest-judgment combination.
4. **Suppress the 🔴 tier locally** (don't install, or mark them cloud-only) and reach
   for a cloud model when you need an autonomous loop or subagent fan-out — except the
   two research phases, which run sequentially on Pi.

> Counts: 🟢 34 · 🟡 45 · 🔴 6 = 85. (AI/ML skills moved to edge-ai-robotics-automation-toolkit.) Revisit when skills are added/removed or the
> primary local model changes.
