---
date: 2026-04-19T00:00:00
repository: ai-toolkit
topic: "Existing skills and agents — inventory, structure, and parity"
tags: [research, skills, agents, opencode, claude, parity]
git_commit: 58b7d32726c82fe201404fdd6fde04211892241d
status: complete
---

# Research: Skills and Agents — Inventory, Structure, and Parity

## Research question
What skills and agents exist in the AI Toolkit, what is their structural compliance against the 10-section template, and where are the parity gaps between Claude Code and OpenCode?

## Summary

The repository contains **53 skills** and **39 agents** (20 Claude Code, 19 OpenCode). All counts match the values stated in `AGENTS.md`. The gold-standard skill template is `skills/architecture-review/SKILL.md` (610 lines, 10 sections). The majority of skills comply with sections 1–6; compliance drops significantly for sections 7–10 (`AI Discipline Rules`, `Anti-Patterns Table`, `Error Recovery`, `Integration with Other Skills`).

The single confirmed parity gap is `confluence-guide-writer`: the Claude agent exists at `claude/agents/confluence-guide-writer.md` (416 lines, full 10-section agent structure) but has no counterpart in `opencode/agents/`. The Claude version references skills `confluence-guide-writer`, `doc-sync`, and `jira-comment-writer`. One additional structural gap: `skills/jira-comment-writer/references/` contains only 1 file (`comment-templates.md`); the convention requires ≥ 2.

Two convention violations require attention: (1) `<tdd-state>` XML tag is shared across 4 skills (`tdd-cycle`, `tdd-agent`, `tdd-refactor`, `tdd-implementer`) — `AGENTS.md` requires unique tags; (2) a stale skill reference `rag-pipeline` in `claude/agents/research-agent.md` should be `rag-pipeline-python`.

## Detailed findings

### 1. Skill inventory (53 skills)

All skills reside in `skills/<name>/SKILL.md` with a `references/` subdirectory.

**Suites and counts:**
- Enterprise .NET: 9 (`4d-schema-migration`, `dotnet-architecture-checklist`, `dotnet-security-review`, `dotnet-security-review-federal`, `dotnet-vertical-slice`, `ef-migration-manager`, `legacy-migration-analyzer`, `minimal-api-scaffolder`, `nuget-package-scaffold`)
- TDD: 6 (`tdd-agent`, `tdd-cycle`, `tdd-implementer`, `tdd-pair`, `tdd-refactor`, `tdd-verify`)
- Edge/IoT: 5 (`edge-cv-pipeline`, `fleet-management`, `jetson-deploy`, `picar-x-behavior`, `sensor-integration`)
- AI/ML: 5 (`mcp-server-scaffold`, `model-optimization`, `ollama-model-workflow`, `rag-pipeline-dotnet`, `rag-pipeline-python`)
- Coaching: 10 (`architecture-journal`, `architecture-review`, `code-review-coach`, `dependency-mapper`, `pattern-tradeoff-analyzer`, `pr-feedback-writer`, `refactor-challenger`, `security-review-trainer`, `system-design-kata`, `technical-debt-assessor`)
- Agent Support: 10 (`anomaly-detection`, `automated-code-review`, `doc-sync`, `environment-health`, `research-synthesis`, `session-context`, `supply-chain-audit`, `task-decomposition`, `test-scaffold`)
- RPI Workflow: 4 (`rpi-implement`, `rpi-iterate`, `rpi-plan`, `rpi-research`)
- Other: 5 (`agent-spec-writer`, `confluence-guide-writer`, `jira-comment-writer`, `jira-review`, `python-arch-review`)

### 2. Agent inventory (39 agents)

**Claude Code agents** (`claude/agents/`, 20 files): code-review-agent, confluence-guide-writer, context-builder-agent, dependency-audit-agent, documentation-agent, environment-health-agent, fleet-deployment-agent, migration-orchestrator, model-optimization-agent, research-agent, rpi-code-analyzer, rpi-file-locator, rpi-implement, rpi-pattern-finder, rpi-planner, sensor-anomaly-agent, spec-extractor-agent, task-decomposition-agent, tdd-agent, test-generation-agent

**OpenCode agents** (`opencode/agents/`, 19 files): same list minus `confluence-guide-writer`

### 3. Skill template compliance

Sections 1–6 present in all 53 skills. Gaps in sections 7–10:

| Section | Present in | Missing from |
|---|---|---|
| 7. AI Discipline Rules | 51/53 | `tdd-refactor`, `tdd-implementer` |
| 8. Anti-Patterns Table | 51/53 | `tdd-refactor`, `tdd-implementer` |
| 9. Error Recovery | 47/53 | `tdd-refactor`, `tdd-implementer`, `jira-review`, `doc-sync`, `session-context`, `automated-code-review` |
| 10. Integration with Other Skills | 40/53 | `pr-feedback-writer`, `jira-comment-writer`, `tdd-verify`, `tdd-refactor`, `tdd-agent`, `tdd-implementer`, `supply-chain-audit`, `nuget-package-scaffold`, `architecture-journal`, `doc-sync`, `task-decomposition`, `session-context`, `automated-code-review` |

### 4. Agent frontmatter schemas

**Claude Code** (`claude/agents/<name>.md`):
```yaml
---
name: agent-name           # kebab-case, matches filename
description: ...           # one sentence + trigger phrases
tools: Read, Edit, Write, Bash, Grep, Glob   # comma-separated PascalCase
model: inherit
skills:
  - skill-name-1
---
```
Read-only agents (rpi-pattern-finder, rpi-file-locator, rpi-code-analyzer) use `tools: Read, Glob, Grep`.

**OpenCode** (`opencode/agents/<name>.md`):
```yaml
---
description: ...           # same text as Claude counterpart
mode: subagent             # or "primary" for rpi-planner, rpi-implement, spec-extractor-agent
tools:
  read: true
  edit: true | false
  write: true | false
  bash: true | false
  glob: true
  grep: true
---
```
Body contains a `## Available Skills` table with `skill({ name: "..." })` calls. Claude uses `skills:` frontmatter array instead.

### 5. Convention violations

| Violation | Location |
|---|---|
| `<tdd-state>` shared by 4 skills | `tdd-cycle`, `tdd-agent`, `tdd-refactor`, `tdd-implementer` |
| Stale skill ref `rag-pipeline` (should be `rag-pipeline-python`) | `claude/agents/research-agent.md:7` |
| `jira-comment-writer/references/` has only 1 file | `skills/jira-comment-writer/references/comment-templates.md` |

### 6. Section heading inconsistencies (~cosmetic)

| Canonical | Variants observed |
|---|---|
| `## Domain Principles Table` | `## Domain Principles` (~20 skills) |
| `## State Block` | `## State Block Format` (~20 skills) |
| `## Output Templates` | `## Output Template` (3 skills) |
| `## Anti-Patterns Table` | `## Anti-Patterns` (~15 skills) |

## Code references

### Gold standard
- `skills/architecture-review/SKILL.md` — 610 lines, full 10-section template with Knowledge Base Lookups section

### Parity gap
- `claude/agents/confluence-guide-writer.md` — 416 lines; skills: confluence-guide-writer, doc-sync, jira-comment-writer; state tag: `<confluence-guide-state>`
- `opencode/agents/confluence-guide-writer.md` — **does not exist**

### Convention violations
- `claude/agents/research-agent.md:7` — stale `rag-pipeline` reference

### Under-complete skills (most sections missing)
- `skills/tdd-refactor/SKILL.md` — missing sections 7, 8, 9, 10
- `skills/tdd-implementer/SKILL.md` — missing sections 7, 8, 9, 10

### References gap
- `skills/jira-comment-writer/references/` — only `comment-templates.md` (needs ≥ 2 files)

## Key design patterns

1. **Skill frontmatter** — `name:` + `description:` only; no tools or model declared at skill level
2. **Claude agent frontmatter** — `name`, `description`, `tools` (comma-separated), `model: inherit`, `skills:` array
3. **OpenCode agent frontmatter** — `description`, `mode`, `tools:` boolean map; no `name:` field; skills referenced in body via `skill({ name: "..." })` table
4. **State block tags** — `<{abbreviated-name}-state>` pattern; must be unique (currently violated by TDD suite sharing `<tdd-state>`)
5. **References directory** — every skill has `references/` with ≥ 2 supporting `.md` files (1 violation: `jira-comment-writer`)
6. **Read-only subagents** — rpi-file-locator, rpi-code-analyzer, rpi-pattern-finder have `edit/write/bash: false` in OpenCode and `tools: Read, Glob, Grep` in Claude

## Open questions

1. Should the 4 TDD skills sharing `<tdd-state>` each get unique tags (e.g., `<tdd-cycle-state>`, `<tdd-refactor-state>`)? This is a convention violation per `AGENTS.md` but may be intentional to allow cross-skill state sharing.
2. Should `tdd-refactor` and `tdd-implementer` receive the 4 missing sections (AI Discipline Rules, Anti-Patterns, Error Recovery, Integration), or are these intentionally minimal skills?
3. Should `jira-comment-writer/references/` get a second file (e.g., a plain-language checklist or audience guide)?
4. Is the stale `rag-pipeline` reference in `claude/agents/research-agent.md:7` a breaking issue (does it prevent skill loading) or cosmetic?
5. Should the ~20 skills using `## Domain Principles` (without "Table") and `## State Block Format` (with "Format") be normalized to the canonical headings?
