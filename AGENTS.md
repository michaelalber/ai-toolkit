# AGENTS.md

Project instructions for AI coding agents (Claude Code, OpenCode, GitHub Copilot, Cursor, Windsurf, etc.).

## Project Overview

AI Toolkit -- a collection of 47 skills and 13 autonomous agents for AI-assisted software development. Supports Claude Code and OpenCode.

## Repository Structure

```
ai-toolkit/
├── skills/                     # 47 shareable skills
│   └── <skill-name>/
│       ├── SKILL.md            # Skill definition (frontmatter + 10 sections)
│       └── references/         # Supporting docs, code examples, checklists
├── claude/agents/              # 13 Claude Code agent definitions
│   └── <agent-name>.md
├── opencode/agents/            # 13 OpenCode agent definitions
│   └── <agent-name>.md
├── AGENTS.md                   # This file (universal agent instructions)
├── CLAUDE.md                   # Claude Code-specific pointer
└── README.md
```

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

### 10 Mandatory Agent Sections

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

## Editing Guidelines

- Follow the 10-section template when creating or modifying skills.
- Keep both `claude/agents/` and `opencode/agents/` versions in sync.
- Every skill must have a `references/` directory with at least 2 supporting files.
- State block XML tags must be unique across all skills and agents.
- Frontmatter `description` fields must include trigger phrases for slash-command discovery.
- In Python code examples, avoid PyTorch evaluation mode calls that trigger security hooks. Use `model.train(False)` instead.

## Skill Suites

| Suite | Skills | Focus |
|-------|--------|-------|
| TDD | tdd-cycle, tdd-implementer, tdd-refactor, tdd-agent, tdd-pair, tdd-verify | Test-Driven Development lifecycle |
| Enterprise .NET | dotnet-vertical-slice, ef-migration-manager, nuget-package-scaffold, legacy-migration-analyzer, dotnet-architecture-checklist, dotnet-security-review, dotnet-security-review-federal, minimal-api-scaffolder, shared-kernel-generator, 4d-schema-migration | .NET patterns, migrations, security |
| Edge/IoT | edge-cv-pipeline, jetson-deploy, sensor-integration, picar-x-behavior | Edge computing, CV, robotics |
| AI/ML | rag-pipeline-python, rag-pipeline-dotnet, mcp-server-scaffold, ollama-model-workflow | RAG, MCP servers, local LLMs |
| Coaching | architecture-review, pattern-tradeoff-analyzer, system-design-kata, dependency-mapper, code-review-coach, refactor-challenger, security-review-trainer, pr-feedback-writer, technical-debt-assessor, architecture-journal | Engineering judgment |
| Agent Support | automated-code-review, test-scaffold, doc-sync, supply-chain-audit, environment-health, model-optimization, anomaly-detection, fleet-management, research-synthesis, session-context, task-decomposition | Domain knowledge for agents |
