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
- **Purpose:** A collection of 86+ shareable skills and autonomous agents for AI-assisted software development. Supports Claude Code and OpenCode.
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

---

## Open Loops

- [ ] Skill count (currently 86) — update this file and README when skills are added or removed. QRSPI added 5 phase skills 2026-06-02 (was 81); the 4 deprecated `rpi-*` skills remain on disk until sunset ~2026-09-01 (Slice 7 → 82).
- [x] Agent count parity — Claude Code (37) vs. OpenCode (37) — QRSPI added `qrspi-orchestrator` + `qrspi-implement` 2026-06-02 (was 35/35, resolved 2026-05-19); sunset removes `rpi-planner`/`rpi-implement` ~2026-09-01 → 35/35
- [x] Commands layer — `claude/commands/` (15 commands) and `opencode/commands/` (15 commands) — QRSPI added 5 (`/qrspi-questions`…`/qrspi-implement`) 2026-06-02 (was 10/10; added 2026-04-24; tdd-cycle → tdd rename + evaluate-tests 2026-05-19)

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
| TDD | tdd, tdd-implementer, tdd-refactor, tdd-agent, tdd-pair, tdd-verify, evaluate-tests | Test-Driven Development lifecycle |
| Enterprise .NET | dotnet-vertical-slice, ef-migration-manager, nuget-package-scaffold, legacy-migration-analyzer, dotnet-architecture-checklist, dotnet-security-review, dotnet-security-review-federal, minimal-api-scaffolder, 4d-schema-migration | .NET patterns, migrations, security |
| Edge/IoT | edge-cv-pipeline, jetson-deploy, sensor-integration, picar-x-behavior | Edge computing, CV, robotics |
| AI/ML | rag-pipeline-python, rag-pipeline-dotnet, mcp-server-scaffold, ollama-model-workflow | RAG, MCP servers, local LLMs |
| Coaching | architecture-review, pattern-tradeoff-analyzer, system-design-kata, dependency-mapper, code-review-coach, refactor-challenger, security-review-trainer, pr-feedback-writer, technical-debt-assessor, architecture-journal, grill-me, zoom-out, caveman, improve-codebase-architecture | Engineering judgment and communication modes |
| DDD | domain-model | Domain-Driven Design vocabulary and modeling |
| Product & GitHub | to-prd, to-issues, triage-issue | PRD creation, issue decomposition, bug triage |
| Agent Support | automated-code-review, test-scaffold, doc-sync, supply-chain-audit, environment-health, model-optimization, anomaly-detection, fleet-management, research-synthesis, session-context, task-decomposition | Domain knowledge for agents |
| Agent Design | spec-coach | Interactive spec design coach — skills, agents, PRDs, and GitHub Spec Kit |
| QRSPI Workflow | qrspi-questions, qrspi-research, qrspi-spec, qrspi-plan, qrspi-implement | Questions-Research-Spec-Plan-Implement: instruction-budget-disciplined replacement for RPI. No-magic-words artifact gates, ticket-hidden research, Design Brain-Dump → Structure Outline, vertical-slice plans, per-slice Red-Green-Refactor. Driven by the `qrspi-orchestrator` (alignment) + `qrspi-implement` (execution) agents and the renamed `research-*` read-only subagents. |
| RPI Workflow _(DEPRECATED — use QRSPI)_ | rpi-research, rpi-plan, rpi-implement, rpi-iterate | **Deprecated 2026-06-02; superseded by the QRSPI Workflow.** Research-Plan-Implement with session isolation and parallel subagents. Skills carry `disable-model-invocation: true`; scheduled for removal at sunset ~2026-09-01 (Slice 7). |
| Python | python-security-review, python-security-review-federal, python-feature-slice, alembic-migration-manager, python-modernization-analyzer, fastapi-scaffolder, pypi-package-scaffold | Python patterns, migrations, security, packaging |
| Rust | rust-architecture-checklist, rust-security-review, rust-feature-slice, sqlx-migration-manager, rust-migration-analyzer, axum-scaffolder, cargo-package-scaffold | Rust architecture, security, migrations, API scaffolding, packaging |
| Other | python-arch-review, jira-review, jira-comment-writer, confluence-guide-writer | Language/tool-specific reviews and documentation generation |
