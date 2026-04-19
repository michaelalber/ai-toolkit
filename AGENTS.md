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
- **Purpose:** A collection of 61+ shareable skills and autonomous agents for AI-assisted software development. Supports Claude Code and OpenCode.
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
  - `claude/global/CLAUDE.md` + `opencode/global/AGENTS.md` — universal standards, installed once globally
  - `CLAUDE.md` (root) + `AGENTS.md` (root) — this repo's context only
- **Key directories:**
  - `skills/<name>/` — skill definition (`SKILL.md`) + supporting docs (`references/`)
  - `claude/agents/` — Claude Code agent definitions (`.md` with `skills:` frontmatter array)
  - `opencode/agents/` — OpenCode agent definitions (`.md` with boolean tool flags + `skill()` body calls)
  - `claude/global/` — global Claude Code files installed to `~/.claude/`
  - `opencode/global/` — global OpenCode files installed to `~/.config/opencode/`
  - `project-templates/` — context file templates users copy into their own project roots
- **Non-obvious constraints:** `claude/global/` and `opencode/global/` files affect every project on the user's machine — changes require explicit human approval before committing

---

## Key Files

| File | Why It Matters |
|---|---|
| `skills/architecture-review/SKILL.md` | Gold standard for the 10-section skill template |
| `project-templates/AGENTS.md` | Template pattern this file follows |
| `claude/global/CLAUDE.md` | Global Claude Code standards — do not duplicate here |
| `opencode/global/AGENTS.md` | Global OpenCode standards — do not duplicate here |
| `intent.md` | Goals, values, tradeoff hierarchy, and persistent decisions for this repo |
| `constraints.md` | Contribution constraints — read before any task |

---

## Persistent Decisions

| Date | Decision | Rationale |
|---|---|---|
| 2026-03-01 | 10-section template for skills and agents | Enforces completeness; gold standard is `skills/architecture-review/SKILL.md` |
| 2026-03-01 | Claude Code uses `skills:` frontmatter array; OpenCode uses `skill()` body calls | Platform format requirements differ; behavior must be identical |
| 2026-04-18 | Specs live in Jira / Confluence, not local `spec.md` | Professional dev workflow; `spec.md` creates stale duplicates |
| 2026-04-18 | `project-templates/` renamed from `templates/` | "project-templates" makes the scope explicit — these are not global files |
| 2026-04-18 | Global files live in `claude/global/` and `opencode/global/` | Separates global standards from project-level context; aligns with install script targets |

---

## Open Loops

- [ ] Skill count (currently 61) — update this file and README when skills are added or removed
- [ ] Agent count parity — Claude Code (28) vs. OpenCode (27); identify and add the missing OpenCode agent

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

Each skill lives in `skills/<name>/` with a `SKILL.md` and a `references/` directory.

### SKILL.md Frontmatter

```yaml
---
name: skill-name
description: >
  What the skill does. Trigger phrases like "keyword1", "keyword2".
---
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

Gold standard template: `skills/architecture-review/SKILL.md`

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

---

## Skill Suites

| Suite | Skills | Focus |
|-------|--------|-------|
| TDD | tdd-cycle, tdd-implementer, tdd-refactor, tdd-agent, tdd-pair, tdd-verify | Test-Driven Development lifecycle |
| Enterprise .NET | dotnet-vertical-slice, ef-migration-manager, nuget-package-scaffold, legacy-migration-analyzer, dotnet-architecture-checklist, dotnet-security-review, dotnet-security-review-federal, minimal-api-scaffolder, 4d-schema-migration | .NET patterns, migrations, security |
| Edge/IoT | edge-cv-pipeline, jetson-deploy, sensor-integration, picar-x-behavior | Edge computing, CV, robotics |
| AI/ML | rag-pipeline-python, rag-pipeline-dotnet, mcp-server-scaffold, ollama-model-workflow | RAG, MCP servers, local LLMs |
| Coaching | architecture-review, pattern-tradeoff-analyzer, system-design-kata, dependency-mapper, code-review-coach, refactor-challenger, security-review-trainer, pr-feedback-writer, technical-debt-assessor, architecture-journal | Engineering judgment |
| Agent Support | automated-code-review, test-scaffold, doc-sync, supply-chain-audit, environment-health, model-optimization, anomaly-detection, fleet-management, research-synthesis, session-context, task-decomposition | Domain knowledge for agents |
| Agent Design | agent-spec-writer | Spec design and extraction for AI agents |
| RPI Workflow | rpi-research, rpi-plan, rpi-implement, rpi-iterate | Research-Plan-Implement with session isolation and parallel subagents |
| Python | python-security-review, python-security-review-federal, python-feature-slice, alembic-migration-manager, python-modernization-analyzer, fastapi-scaffolder, pypi-package-scaffold | Python patterns, migrations, security, packaging |
| Other | python-arch-review, jira-review, jira-comment-writer, confluence-guide-writer | Language/tool-specific reviews and documentation generation |
