# AI Toolkit — Project Context
<!-- ⚠ PROJECT-LEVEL FILE — NOT GLOBAL
     This is the project-level AGENTS.md for OpenCode.
     It supplements your global opencode/global/AGENTS.md — it does NOT replace it.
     Global standards (coding style, security rules, quality gates) live in the global file.
     This file contains only what is specific to THIS repository.

     DISCIPLINE 2: Context Engineering — scoped to this project.
     Tells the agent everything it needs to KNOW about this repo.

     RELATED FILES:
       intent.md       — what the agent should optimize for (goals, values, tradeoff hierarchy)
       constraints.md  — musts, must-nots, preferences, escalation triggers
       evals.md        — test cases and CI gate definitions -->

---

## Project Overview

- **Name:** AI Toolkit
- **Purpose:** A collection of 91+ shareable skills and autonomous agents for AI-assisted software development. Supports Claude Code and OpenCode.
- **Phase:** Maintain — stable toolkit; work consists of adding new skills/agents, fixing existing ones, and keeping platform parity.
- **Jira project key:** N/A — task specs are tracked in conversation context or ad hoc
- **Definition of success:** Every skill and agent installs cleanly, follows the 10-section template exactly, and works out of the box without requiring external documentation.

---

## Technology Stack

- **Content format:** Markdown + YAML frontmatter — no compiled language, no build system
- **Agent platforms:** Claude Code (claude.ai/code) and OpenCode
- **Global install targets:** `~/.claude/` (Claude Code) and `~/.config/opencode/` (OpenCode)
- **Package manager:** None for skills/agents; `bun` used in `opencode/global/` for OpenCode config dependencies

---

## Architecture

- **Pattern:** Flat directories by domain — skills, agents, global config, and project templates are siblings, not layers
- **Two-level context stack:**
  - `claude/global/CLAUDE.md` + `opencode/global/AGENTS.md` + `pi/global/AGENTS.md` — universal standards, installed once globally
  - `CLAUDE.md` (root) + `AGENTS.md` (root) — this repo's context only
- **Key directories:**
  - `skills/{team,professional}/<name>/` — skill definition (`SKILL.md`) + supporting docs (`references/`); the `team`/`professional` subdirectory is selected by the skill's `audience:` frontmatter
  - `claude/agents/` — Claude Code agent definitions (`.md` with `skills:` frontmatter array)
  - `opencode/agents/` — OpenCode agent definitions (`.md` with boolean tool flags + `skill()` body calls)
  - `claude/commands/` — Claude Code user-invoked slash commands with shell injection
  - `opencode/commands/` — OpenCode command equivalents with agent routing and subtask isolation
  - `claude/global/` — global Claude Code files installed to `~/.claude/`
  - `claude/global/settings.json` — hooks: PreToolUse credential stop, PostToolUse build/lint gates
  - `opencode/global/` — global OpenCode files installed to `~/.config/opencode/`
  - `pi/global/` — global Pi files installed to `~/.pi/agent/`; `SYSTEM.md` is a per-project template
  - `project-templates/` — context file templates users copy into their own project roots
- **Non-obvious constraints:** `claude/global/`, `opencode/global/`, and `pi/global/` files affect every project on the user's machine — changes require explicit human approval before committing

---

## Key Files

| File | Why It Matters |
|---|---|
| `skills/professional/architecture-review/SKILL.md` | Gold standard for the 10-section skill template |
| `project-templates/AGENTS.md` | Template pattern this file follows |
| `claude/global/CLAUDE.md` | Global Claude Code standards — do not duplicate here |
| `opencode/global/AGENTS.md` | Global OpenCode standards — do not duplicate here |
| `pi/global/AGENTS.md` | Global Pi standards — do not duplicate here |
| `pi/global/SYSTEM.md` | Per-project Pi system prompt template — users copy to project root |
| `intent.md` | Goals, values, tradeoff hierarchy, and persistent decisions for this repo |
| `constraints.md` | Contribution constraints — read before any task |

---

## Persistent Decisions

| Date | Decision | Rationale |
|---|---|---|
| 2026-03-01 | 10-section template for skills and agents | Enforces completeness; gold standard is `skills/professional/architecture-review/SKILL.md` |
| 2026-03-01 | Claude Code uses `skills:` frontmatter array; OpenCode uses `skill()` body calls | Platform format requirements differ; behavior must be identical |
| 2026-04-18 | Specs live in Jira / Confluence, not local `spec.md` | Professional dev workflow; `spec.md` creates stale duplicates |
| 2026-04-18 | `project-templates/` renamed from `templates/` | "project-templates" makes the scope explicit — these are not global files |
| 2026-04-18 | Global files live in `claude/global/` and `opencode/global/` | Separates global standards from project-level context; aligns with install script targets |
| 2026-04-24 | Pi global files live in `pi/global/`; AGENTS.md installs to `~/.pi/agent/`; SYSTEM.md is a per-project template | Pi's `SYSTEM.md` is project-scoped (not a global config file); keeping it in `pi/global/` as a user-copyable template matches Pi's per-project design |
| 2026-04-24 | Commands layer added alongside agents | Commands are user-invoked (typed as `/command-name`); skills are model-invoked (autonomous). Different primitives, same platform directory scope. |
| 2026-04-24 | Hooks in `settings.json`, permissions in `settings.local.json` | Separation of concerns — deterministic enforcement (hooks) vs. interactive approval (permissions). Keep in separate files. |
| 2026-04-25 | Two-tier skill system: minimal (≤ 100 lines, ≥ 1 reference) and full-template (10 sections, ≤ 400 lines, ≥ 2 references) | Ported from mattpocock/skills — minimal tier handles mode switches, conversational tools, and single-instruction skills without the overhead of the 10-section template. |
| 2026-04-25 | `disable-model-invocation: true` frontmatter for interactive/conversational skills | Ported from mattpocock/skills — prevents auto-invocation by the model; grill-me, domain-model, zoom-out, caveman use this. |
| 2026-04-26 | Global template files (`claude/global/`, `opencode/global/`) must contain only generic, domain-level descriptions — no specific book titles, personal document names, or user-specific tool references | These files are public templates installable by any user. Personal enrichment belongs in the installed copies (`~/.claude/CLAUDE.md`, `~/.config/opencode/AGENTS.md`), not the repo source. |
| 2026-06-02 | QRSPI replaces RPI: deprecate the 4 rpi-* skills + `rpi-planner`/`rpi-implement` agents now (`disable-model-invocation: true` on skills + `DEPRECATED` description prefix); remove all rpi-* files at sunset ~2026-09-01 (Slice 7). The 3 read-only subagents were renamed `research-*` (workflow-neutral) and kept. | RPI delivered poor results (instruction-budget overflow, magic-words dependency, plan-reading illusion). Coexistence leaves the poor-outcome path discoverable; QRSPI is its replacement, so RPI is deprecated then removed. |
| 2026-06-02 | QRSPI vendors **0 new primitive skills** — `qrspi-implement` references the existing `tdd` skill as its inner loop; `qrspi-spec`/`qrspi-plan` carry the vertical-slice gate in their own content; all five cross-link `tdd` and the `*-feature-slice` scaffolders via Integration | `tdd` already IS the canonical RED-GREEN-REFACTOR loop purpose-built as a shared inner loop; a new `red-green-refactor` skill would be ~100% duplication. Honors DRY and the "Companion Skills" non-overlap doctrine. |
| 2026-06-02 | Minimal-tier definition broadened to include **thin, self-sufficient workflow-phase drivers (≤ ~40 imperative directives)**. All five `qrspi-*` phase skills use the minimal tier (≤ 100 lines, ≥ 1 reference), self-sufficient when invoked directly, overflow pushed to `references/` loaded just-in-time | QRSPI exists because prompts past ~150–200 instructions degrade; the full 10-section template reproduces the exact bloat QRSPI was created to fix, and is worst on smaller local models. Every section is an always-on per-invocation token tax. |
| 2026-06-02 | QRSPI artifacts co-locate in a per-feature folder `thoughts/shared/qrspi/YYYY-MM-DD-{slug}/` (`questions.md`, `research.md`, `spec.md`, `plan.md`, `implementation/slice-NN-*.md`) rather than scattering across `thoughts/shared/research|plans/` | QRSPI produces five tightly-coupled artifacts per feature; co-locating them makes a fresh session cheap (read the folder, not the transcript) and gives each slice log a clean resumption point. `spec.md`/`plan.md` carry a lifecycle `status:` (the `approved` gate blocks `qrspi-implement`). |
| 2026-06-03 | QRASPI greenfield workflow added: six phases Q→R→A→S→P→I + a terminal graduation handoff, the greenfield (V0/V1) counterpart to QRSPI. **2-agent topology split by edit access**: `qraspi-orchestrator` (no-Edit: Questions/Research/Architecture/Plan/Graduate) + `qraspi-builder` (Edit: Skeleton/Implement). | Greenfield's edit boundary differs from QRSPI's (Skeleton and Implement write source; Q/R/A/P/graduate are markdown), but it still splits cleanly into who-may-edit. A 3rd agent buys nothing — Skeleton and Implement share tools and the green-gate philosophy. QRASPI maps a problem domain; QRSPI maps an existing codebase. |
| 2026-06-03 | QRASPI extracts **one** new primitive skill, `fitness-functions` — the first new primitive since the QRSPI "vendored 0 primitives" decision. ADR-writing, C4, and walking-skeleton scaffolding were instead **folded** into the phase skills + `references/`. | `fitness-functions` has ≥2 callers (`qraspi-architecture` specifies them, `qraspi-skeleton` lands them as CI gates) and cross-workflow reuse (a brownfield QRSPI feature can add a CI-gate fitness function); no existing skill covers the surface (`dependency-mapper` covers only the coupling-metric category). The doctrine holds in spirit: extract only at ≥2 callers with no existing cover. |
| 2026-06-03 | QRASPI artifacts co-locate per project in `thoughts/shared/qraspi/YYYY-MM-DD-{slug}/` with **per-slice** `plan-{slice}.md` + `implementation-log-{slice}.md` (vs QRSPI's single `plan.md` + `implementation/slice-NN-*.md`); accepted ADRs live in the **target repo's** `docs/adr/NNNN-*.md`. | Greenfield grows slice-by-slice on the skeleton, so Plan/Implement run once per slice (default: the next unbuilt backlog slice from `skeleton.md`). ADRs are project artifacts QRSPI later reads, so they belong in the repo, not the qraspi feature folder. |
| 2026-06-03 | QRASPI ADRs use the **MADR** template (Title/Status/Context/Considered Options/Decision/Consequences) with **≥2 alternatives required** and an align-before-lock gate (proposed → human aligns → accepted). | "Alternatives Considered" is a MADR/Tyree addition, not original Nygard; QRASPI requires alternatives so a fait-accompli ADR cannot reach WRITE, and MADR carries them natively. `architecture-journal` keeps its own ADR variant; QRASPI's MADR template lives in `qraspi-architecture/references/adr-template.md`. |
| 2026-06-03 | QRASPI C4 diagrams use **Mermaid** `C4Context`/`C4Container` (Context + Container levels only). | The repo is markdown-native with no build system; Mermaid renders inline in GitHub/Codeberg/VS Code, is diffable, and is AI-generatable. Structurizr DSL is richer but needs tooling the repo lacks. |
| 2026-06-03 | QRASPI Skeleton's exit gate is **CI green** — a real CI/test run (build + unit + lint + fitness gates) exiting 0, captured as `ci_green`, never a claim. Hardware archetypes: host gates green + device-deploy as a documented manual gate. | A walking skeleton is executable by definition; an aspirational scaffold defeats the phase. The fitness functions `qraspi-architecture` specified are wired by `fitness-functions` and must pass as part of CI green; `qraspi-implement` keeps them green per slice. |
| 2026-06-03 | Deprecate `spec-implement` alongside RPI (`disable-model-invocation: true` + `DEPRECATED` description prefix; removal at sunset ~2026-09-01). Its `rpi-*` pointers in `spec-implement`, `tdd`, and `spec-coach` were scrubbed to QRSPI/QRASPI. | `spec-implement` was branded "the greenfield counterpart to RPI" and routed to the now-deprecated `/rpi-research` in five places; QRASPI (greenfield) and QRSPI (brownfield) subsume its spec → criteria → per-slice TDD flow with artifact-gated phases. Leaving it live keeps a stale path to a sunset workflow discoverable. |
| 2026-06-03 | Cross-language **architecture + security parity** for .NET/Python/PHP/Rust. Architecture: four `<lang>-architecture-checklist` skills sharing an identical Core Values + `DETECT→SCAN→REPORT(A–F)→RECOMMEND` workflow + output, differing only in language checks/tooling; `python-arch-review` (a misfit TDD-authoring hybrid) renamed/re-scoped to `python-architecture-checklist`; `php-architecture-checklist` created. Security: four `<lang>-security-review` bases share an OWASP core; **gov collapses to ONE language-agnostic `security-review-federal` overlay** (NIST 800-53 · CUI · DOE · POA&M · EO 14028 + per-language FIPS table), replacing `dotnet-security-review-federal` + `python-security-review-federal`. All trimmed lean; depth in `references/`. | User wants the four languages "in sync" (same workflow/values, language-specific specifics) and lean. Per-language skills (not one detecting skill) preserve trigger routing and match every other family. The federal overlay is ~80% language-agnostic policy, so one shared skill gives gov parity for all four languages at once and one place to keep NIST/CUI/POA&M in sync — far leaner than duplicating it 4×. `python-arch-review` was the lone misfit whose triggers collided with `tdd`/`python-feature-slice`/`python-security-review`. |
| 2026-06-03 | **React skill family** added (first frontend family), mirroring the .NET/Python/PHP/Rust families: `react-architecture-checklist`, `react-security-review`, `react-feature-slice`, `react-component-scaffolder`, `react-app-scaffolder`, `react-modernization-analyzer` (6 skills) + 6 agents in both runtimes (`react-feature-slice-agent`, `react-component-scaffold-agent`, `react-app-scaffold-agent`, `react-security-agent`, `react-modernization-agent`, `react-arch-checklist-agent`). React is a frontend library, so two backend archetypes were **remapped**: the HTTP `api-scaffolder` slot → `react-component-scaffolder` + `react-app-scaffolder` (the component/app is the front-end "unit"), and the DB `migration-manager` slot → `react-modernization-analyzer` (class→hooks, CRA→Vite, 17→18→19, JS→TS); the `*-package-scaffold` (npm) archetype was **dropped** to keep the family at the standard 6 skills. Federal overlay gained a React/TS FIPS row; `security-review` command dispatch adds `react`. | User asked for React "to mirror the php, python, etc." The remapping keeps the family the same size and shape while respecting that a frontend library has no HTTP endpoint or DB migration. **Grounding gap noted:** the KB has no React corpus (`grounded_javascript` is JS/TS + Vue, not React), so every React skill grounds TS via `collection="javascript"`, a11y via `collection="ui_ux"`, OWASP via `collection="internal"`, and cites **react.dev** as the primary authority. Follow-up (separate repo): add a `grounded_react` collection to grounded-code-mcp. |
| 2026-06-03 | Consolidate the TDD cluster 8→5. **Delete** `tdd-implementer` and `tdd-refactor` — their per-phase content folds into the canonical `tdd` skill's GREEN/REFACTOR sections + `references/` (green idioms, `code-smells`, `refactoring-catalog`, loaded on demand). **Merge** `tdd-verify` into `evaluate-tests` as a second "TDD compliance" mode (commit-history scorecard + AI anti-patterns). **Keep** `tdd` (the one loop), `tdd-agent` + `tdd-pair` (operating modes that defer to `tdd`), `evaluate-tests`, `test-scaffold`. Agents `tdd-agent`/`test-generation-agent` updated; no agent/command count change. | Eight overlapping TDD skills created an unanswerable routing question ("for GREEN, use `tdd` or `tdd-implementer`?"). The per-phase skills re-derived single phases of the loop `tdd` already owned whole, and the two auditors (`tdd-verify`, `evaluate-tests`) overlapped. One loop + modes + one auditor is focused and token-efficient; depth moved to load-on-demand `references/`. TDD/RGR is critical to AI-agent coding — clarity of "which skill" matters most here. |

---

## Open Loops

- [ ] Skill count (currently 102) — update this file and README when skills are added or removed. QRSPI added 5 phase skills 2026-06-02 (was 81); QRASPI added 8 (`fitness-functions` + the 7 phase/graduate skills) 2026-06-03 (was 86, → 94); TDD cluster consolidated 8→5 on 2026-06-03 (→ 91); cross-language architecture+security parity 2026-06-03 (renamed `python-arch-review`→`python-architecture-checklist`; +`php-architecture-checklist`, +`php-security-review`, +`security-review-federal`; −`dotnet-security-review-federal`, −`python-security-review-federal` → 92); PHP family parity 2026-06-03 (+`php-feature-slice`, +`php-api-scaffolder`, +`php-package-scaffold`, +`php-migration-manager` → 96); React family parity 2026-06-03 (+`react-architecture-checklist`, +`react-security-review`, +`react-feature-slice`, +`react-component-scaffolder`, +`react-app-scaffolder`, +`react-modernization-analyzer` → 102); the 4 deprecated `rpi-*` skills plus the deprecated `spec-implement` remain on disk until sunset ~2026-09-01 → 97.
- [x] Agent count parity — Claude Code (49) vs. OpenCode (49) — QRSPI added `qrspi-orchestrator` + `qrspi-implement` 2026-06-02 (was 35/35, resolved 2026-05-19); QRASPI added `qraspi-orchestrator` + `qraspi-builder` 2026-06-03 (was 37/37); PHP family parity 2026-06-03 added `php-feature-slice-agent`, `php-api-scaffold-agent`, `php-package-agent`, `php-migration-agent` in both runtimes (was 39/39, → 43/43); React family parity 2026-06-03 added `react-feature-slice-agent`, `react-component-scaffold-agent`, `react-app-scaffold-agent`, `react-security-agent`, `react-modernization-agent`, `react-arch-checklist-agent` in both runtimes (was 43/43, → 49/49); sunset removes `rpi-planner`/`rpi-implement` ~2026-09-01 → 47/47
- [x] Commands layer — `claude/commands/` (22 commands) and `opencode/commands/` (22 commands) — QRSPI added 5 (`/qrspi-questions`…`/qrspi-implement`) 2026-06-02 (was 10/10); QRASPI added 7 (`/qraspi-questions`…`/qraspi-graduate`) 2026-06-03 (was 15/15). No `rpi-*` commands, so sunset leaves commands at 22.

---

## Team

| Name | Role | Notes |
|---|---|---|
| Michael K. Alber | Owner / Primary contributor | Reviews all changes to global files and project-templates |

---

## Available Tools

- `grounded-code-mcp` — local knowledge base; preferred over training data for language idioms, security patterns, and framework APIs

---

## Project Boot Ritual

At the start of every session:

1. Read this file (`AGENTS.md`), `intent.md`, and `constraints.md`.
2. Check the active task context (Jira issue or conversation) for the current spec and acceptance criteria.
3. Confirm context — state: current phase, active task (if any), top 3 constraints, open loops.
4. Do NOT begin work until context is confirmed.

---

## Skill Conventions

Each skill lives in `skills/team/<name>/` or `skills/professional/<name>/` with a `SKILL.md` and a
`references/` directory. The `team` vs. `professional` subdirectory is selected by the `audience:`
frontmatter field and applied by `scripts/add_frontmatter.py` (which walks `skills/{team,professional}/*/`).

### SKILL.md Frontmatter

```yaml
---
name: skill-name
audience: team  # team | professional — selects the skills/<audience>/ install subdirectory
description: >
  What the skill does. Trigger phrases like "keyword1", "keyword2".
disable-model-invocation: true  # optional: prevents auto-invocation; use for interactive or conversational skills
---
```

### Skill Tiers

| Tier | When to use | SKILL.md size | References required |
|------|------------|--------------|---------------------|
| **Minimal** | Mode switches, conversational tools, single-instruction skills | ≤ 100 lines | ≥ 1 file |
| **Full-template** | Domain-expert skills with workflow, state tracking, and output templates | ≤ 400 lines (overflow → `references/`) | ≥ 2 files |

Minimal-tier skills have no prescribed section structure — just focused instructions.
Full-template skills follow the 10-section template; content that overflows 400 lines goes into `references/` files, not more sections.

### Description Format

The description field is the **only thing the model sees when deciding which skill to load**. Quality here determines trigger reliability.

- Max 1024 chars
- Third person: "Scaffolds...", "Audits...", "Extracts..." — not "I will..." or "You can..."
- First sentence: what the skill does
- Second sentence: "Use when [specific trigger scenarios]"
- Include "Do NOT use when..." for negative triggers

**Good:**
```yaml
description: >
  Scaffolds NuGet package metadata, CI/CD pipeline, and test harness.
  Use when publishing a new library to NuGet.org. Do NOT use for
  internal workspace-only libraries; use dotnet-vertical-slice instead.
```

**Bad (too vague — triggers on everything):**
```yaml
description: >
  A comprehensive and powerful tool for NuGet package management.
  Very useful for .NET developers.
```

### 10 Mandatory Sections (in order)

1. **Title + Epigraph** -- `# Skill Name` with 1-2 relevant quotes
2. **Core Philosophy** -- Non-negotiable constraints and design rationale
3. **Domain Principles Table** -- 10 principles with Priority, Description, Applied As columns
4. **Workflow** -- Phased lifecycle (e.g., DETECT, SCAN, REPORT, RECOMMEND) with exit criteria
5. **State Block** -- Unique XML tag (e.g., `<tdd-state>`, `<arch-review-state>`) for multi-turn tracking
6. **Output Templates** -- Markdown report templates with tables and checklists
7. **AI Discipline Rules** -- CRITICAL/REQUIRED rules with WRONG/RIGHT code examples
8. **Anti-Patterns Table** -- 10 anti-patterns with "Why It Fails" and "Correct Approach"
9. **Error Recovery** -- 3-4 scenarios with symptoms and numbered recovery steps
10. **Integration with Other Skills** -- Cross-references to related skills

Gold standard template: `skills/professional/architecture-review/SKILL.md`

### References Directory

Each `references/` directory contains 2-5 supporting files: code examples, decision matrices, checklists, configuration templates.

---

## Agent Conventions

Agents exist in two flavors with identical behavior but different formats:

### Claude Code (`claude/agents/<name>.md`)

```yaml
---
name: agent-name
description: What the agent does
tools: Read, Edit, Write, Bash, Glob, Grep
model: inherit
skills:
  - skill-name-1
  - skill-name-2
---
```

### OpenCode (`opencode/agents/<name>.md`)

```yaml
---
description: What the agent does
mode: subagent
tools:
  read: true
  edit: true
  write: true
  bash: true
  glob: true
  grep: true
---
```

Key difference: Claude uses `skills:` array in frontmatter; OpenCode uses `skill({ name: "..." })` calls in the body.

### 10 Mandatory Agent Sections (in order)

1. Title + Epigraph
2. Core Philosophy
3. Guardrails
4. Autonomous Protocol
5. Self-Check Loops
6. Error Recovery
7. AI Discipline Rules
8. Session Template
9. State Block (unique XML tag per agent, e.g., `<tdd-state>`, `<code-review-state>`)
10. Completion Criteria

---

## Editing Guidelines

- Follow the 10-section template when creating or modifying skills.
- Keep both `claude/agents/` and `opencode/agents/` versions in sync.
- Every skill must have a `references/` directory with at least 2 supporting files.
- State block XML tags must be unique across all skills and agents.
- Frontmatter `description` fields must include trigger phrases for slash-command discovery.
- In Python code examples, avoid PyTorch evaluation mode calls that trigger security hooks. Use `model.train(False)` instead.
- **`claude/global/` and `opencode/global/` files are public templates distributed to any user.** Never embed specific book titles, personal document names, personal file paths, or user-specific tool names in these files. Collection descriptions must describe topic domains (e.g., "Rust language: ownership, async, Tokio"), not the specific documents a particular user has ingested. Installed files (`~/.claude/CLAUDE.md`, `~/.config/opencode/AGENTS.md`) may contain personal references; the source template files must not.

---

## Skill Suites

| Suite | Skills | Focus |
|-------|--------|-------|
| TDD | tdd (the canonical loop) + tdd-agent / tdd-pair (operating modes) + evaluate-tests (quality & compliance audit) | Test-Driven Development lifecycle |
| Enterprise .NET | dotnet-vertical-slice, ef-migration-manager, nuget-package-scaffold, legacy-migration-analyzer, dotnet-architecture-checklist, dotnet-security-review, minimal-api-scaffolder, 4d-schema-migration | .NET patterns, migrations, security |
| Security (cross-language) | security-review-federal | Shared language-agnostic federal/gov overlay (NIST 800-53, FIPS, CUI, POA&M, EO 14028, DOE 205.1B) applied on top of any base `<lang>-security-review` |
| Edge/IoT | edge-cv-pipeline, jetson-deploy, sensor-integration, picar-x-behavior | Edge computing, CV, robotics |
| AI/ML | rag-pipeline-python, rag-pipeline-dotnet, mcp-server-scaffold, ollama-model-workflow | RAG, MCP servers, local LLMs |
| Coaching | architecture-review, pattern-tradeoff-analyzer, system-design-kata, dependency-mapper, code-review-coach, refactor-challenger, security-review-trainer, pr-feedback-writer, technical-debt-assessor, architecture-journal, grill-me, zoom-out, caveman, improve-codebase-architecture | Engineering judgment and communication modes |
| DDD | domain-model | Domain-Driven Design vocabulary and modeling |
| Product & GitHub | to-prd, to-issues, triage-issue | PRD creation, issue decomposition, bug triage |
| Agent Support | automated-code-review, test-scaffold, doc-sync, supply-chain-audit, environment-health, model-optimization, anomaly-detection, fleet-management, research-synthesis, session-context, task-decomposition | Domain knowledge for agents |
| Agent Design | spec-coach | Interactive spec design coach — skills, agents, PRDs, and GitHub Spec Kit |
| QRSPI Workflow | qrspi-questions, qrspi-research, qrspi-spec, qrspi-plan, qrspi-implement | Questions-Research-Spec-Plan-Implement: instruction-budget-disciplined replacement for RPI. No-magic-words artifact gates, ticket-hidden research, Design Brain-Dump → Structure Outline, vertical-slice plans, per-slice Red-Green-Refactor. Driven by the `qrspi-orchestrator` (alignment) + `qrspi-implement` (execution) agents and the renamed `research-*` read-only subagents. For an EXISTING codebase / adding a feature. |
| QRASPI Workflow | fitness-functions, qraspi-questions, qraspi-research, qraspi-architecture, qraspi-skeleton, qraspi-plan, qraspi-implement, qraspi-graduate | Questions-Research-Architecture-Skeleton-Plan-Implement for a NEW system (greenfield V0/V1), then graduation to QRSPI. Locks path-dependent decisions as MADR ADRs with alternatives + Mermaid C4, lands a runnable walking skeleton with fitness functions as merge-blocking CI gates (CI-green exit gate), grows it slice-by-slice with Red-Green-Refactor, then hands off to QRSPI. Driven by `qraspi-orchestrator` (no-edit Q/R/A/P/graduate) + `qraspi-builder` (edit Skeleton/Implement); `fitness-functions` is the one extracted primitive. For a NEW system from scratch — the greenfield counterpart to QRSPI. |
| RPI Workflow _(DEPRECATED — use QRSPI)_ | rpi-research, rpi-plan, rpi-implement, rpi-iterate | **Deprecated 2026-06-02; superseded by the QRSPI Workflow.** Research-Plan-Implement with session isolation and parallel subagents. Skills carry `disable-model-invocation: true`; scheduled for removal at sunset ~2026-09-01 (Slice 7). |
| Python | python-architecture-checklist, python-security-review, python-feature-slice, alembic-migration-manager, python-modernization-analyzer, fastapi-scaffolder, pypi-package-scaffold | Python patterns, migrations, security, packaging |
| PHP | php-architecture-checklist, php-security-review | PHP/Laravel architecture and security review |
| Rust | rust-architecture-checklist, rust-security-review, rust-feature-slice, sqlx-migration-manager, rust-migration-analyzer, axum-scaffolder, cargo-package-scaffold | Rust architecture, security, migrations, API scaffolding, packaging |
| Other | jira-review, jira-comment-writer, confluence-guide-writer | Language/tool-specific reviews and documentation generation |
