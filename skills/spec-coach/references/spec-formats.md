# Spec Format Templates

Complete templates for all five target formats. Use these during the GENERATE phase of `spec-coach`.

---

## Format 1: SKILL.md (ai-toolkit Skill)

Path: `skills/<name>/SKILL.md`

```markdown
---
name: [skill-name]
description: >
  [What the skill does. Include trigger phrases like "keyword1", "keyword2".]
---

# [Skill Title] ([Subtitle — e.g., "Interactive Coach" or "Autonomous Analyzer"])

> "[Relevant quote about the domain]"
> — [Attribution]

> "[Second quote, optional]"
> — [Attribution]

## Core Philosophy

[3-5 paragraphs. What problem does this skill solve? What is the core design insight?
What is this skill IS and IS NOT? What are the non-negotiable constraints?]

## Domain Principles Table

| # | Principle | Description | Applied As |
|---|-----------|-------------|------------|
| 1 | **[Name]** | [Description] | [How to apply] |
| 2 | **[Name]** | [Description] | [How to apply] |
| 3 | **[Name]** | [Description] | [How to apply] |
| 4 | **[Name]** | [Description] | [How to apply] |
| 5 | **[Name]** | [Description] | [How to apply] |
| 6 | **[Name]** | [Description] | [How to apply] |
| 7 | **[Name]** | [Description] | [How to apply] |
| 8 | **[Name]** | [Description] | [How to apply] |
| 9 | **[Name]** | [Description] | [How to apply] |
| 10 | **[Name]** | [Description] | [How to apply] |

## Workflow: [The Workflow Name]

[Introduction to the workflow — what phases does it have? What is the core interaction loop?]

### Phase 1: [PHASE NAME] — [Phase Subtitle]

**Entry question:** "[Question that opens this phase]"

**Actions:**
1. [Action]
2. [Action]
3. [Action]

**Exit criterion:** [What must be true before moving to the next phase]

[Repeat for each phase]

## State Block

Maintain state across conversation turns:

```
<[skill-name]-state>
[field]: [description]
[field]: [description]
last_action: [what was just done]
next_action: [what should happen next]
</[skill-name]-state>
```

## Output Templates

### Session Opening

```markdown
[How the skill introduces itself and starts the session]
```

### [Other template names as needed]

## AI Discipline Rules

### CRITICAL: [Rule Name]

[Rule description]

```
WRONG: [Example of what not to do]
RIGHT: [Example of correct behavior]
```

[Repeat for each critical rule — minimum 4]

## Anti-Patterns Table

| Anti-Pattern | Description | Why It Fails | Correct Approach |
|---|---|---|---|
| **[Name]** | [Description] | [Why it fails] | [Correct approach] |
[10 rows minimum]

## Error Recovery

### Problem: [Problem Name]

[Description of the problem]

**Indicators:**
- [Symptom]
- [Symptom]

**Recovery Actions:**
1. [Step]
2. [Step]
3. [Step]

[3-4 problems minimum]

## Integration with Other Skills

- **`[skill-name]`** — [When and why to use this skill in conjunction]
- **`[skill-name]`** — [When and why to use this skill in conjunction]
```

**Required references directory:** `skills/<name>/references/` with at least 2 supporting files.

---

## Format 2: Claude Code Agent (`claude/agents/<name>.md`)

Path: `claude/agents/<name>.md`

```markdown
---
name: [agent-name]
description: [What the agent does. Include trigger phrases for slash-command discovery.]
tools: Read, Edit, Write, Bash, Glob, Grep
model: inherit
skills:
  - [skill-name-1]
  - [skill-name-2]
---

# [Agent Title] (Autonomous Mode)

> "[Relevant quote]"
> — [Attribution]

## Core Philosophy

You are an autonomous [domain] agent. You [primary function] independently.
**Stricter guardrails apply** because there is no human catching mistakes in real-time.

**Non-Negotiable Constraints:**
1. [Constraint]
2. [Constraint]
3. [Constraint]

## The [N] Guardrails

### Guardrail 1: [Name]

[Description]

```
GATE CHECK:
1. [Check]
2. [Check]

If ANY check fails → [Action]
```

[Repeat for each guardrail]

## Autonomous Protocol

### Phase 1: [PHASE NAME] — [Description]

```
1. [Step]
2. [Step]
3. [Step]
4. Log with evidence
5. Only then → [NEXT PHASE]
```

**Mandatory Logging:**
```markdown
### [Phase] Phase

**[Field]**: [description]
**[Field]**: [description]

Proceeding to [next phase].
```

[Repeat for each phase]

## Self-Check Loops

### [Phase] Phase Self-Check
- [ ] [Check]
- [ ] [Check]
- [ ] [Check]

[Repeat for each phase]

## Error Recovery

### [Problem Name]
```
1. [Step]
2. [Step]
3. [Step]
```

[3-4 problems]

## AI Discipline Rules

### [Rule Name]
- [Rule]
- [Rule]

[4 rules minimum]

## Session Template

```markdown
## [Agent] Session: [Feature/Target]

Mode: Autonomous ([agent-name])
[Context fields]

---

### [Phase] Phase

[Phase logging template]

<[agent]-state>
phase: [phase]
[fields]
</[agent]-state>

---
```

## State Block

Always maintain explicit state:

```markdown
<[agent-name]-state>
phase: [PHASE1] | [PHASE2] | [PHASE3]
[field]: [description]
[field]: [description]
last_action: [what was just completed]
next_action: [what should happen next]
</[agent-name]-state>
```

## Completion Criteria

Session is complete when:
- [Criterion]
- [Criterion]
- [Criterion]
- User's original request is satisfied
```

**Key notes for Claude agents:**
- `model: inherit` — do not specify a model; inherit from the calling context
- `skills:` array lists skill names (not paths) that load automatically
- All 10 sections required
- State block XML tag must be unique across the entire toolkit

---

## Format 3: OpenCode Agent (`opencode/agents/<name>.md`)

Path: `opencode/agents/<name>.md`

```markdown
---
description: [What the agent does. Include trigger phrases for discovery.]
mode: subagent
tools:
  read: true
  edit: true
  write: true
  bash: true
  glob: true
  grep: true
---

# [Agent Title] (Autonomous Mode)

> "[Relevant quote]"
> — [Attribution]

## Core Philosophy

[Same content as Claude agent version]

## Available Skills

Load these skills on-demand for detailed guidance. Use the `skill` tool when you need deeper reference material:

| Skill | When to Load |
|-------|--------------|
| `skill({ name: "[skill-name-1]" })` | [When to load this skill] |
| `skill({ name: "[skill-name-2]" })` | [When to load this skill] |

**Skill Loading Protocol:**
1. [When to load first skill]
2. [When to load subsequent skills]

**Note:** Skills are located in `~/.config/opencode/skills/`.

## The [N] Guardrails

[Same content as Claude agent version]

## Autonomous Protocol

[Same content as Claude agent version]

## Self-Check Loops

[Same content as Claude agent version]

## Error Recovery

[Same content as Claude agent version]

## AI Discipline Rules

[Same content as Claude agent version]

## Session Template

[Same content as Claude agent version]

## State Block

[Same content as Claude agent version]

## Completion Criteria

[Same content as Claude agent version]
```

**Key differences from Claude agent format:**
- No `name:` in frontmatter (OpenCode uses the filename)
- No `model:` field (OpenCode inherits from settings)
- `tools:` is a boolean map, not a comma-separated list
- `skills:` are NOT in frontmatter — use `skill({ name: "..." })` table in the body
- Add "Available Skills" section with skill loading protocol after Core Philosophy
- Include note: "Skills are located in `~/.config/opencode/skills/`."

---

## Format 4: Generic PRD (O'Reilly Framework)

Standalone spec not tied to any specific toolkit. Use when defining agent behavior for any platform.

```markdown
# Agent Spec: [Agent Name]

**Version**: 1.0
**Date**: [YYYY-MM-DD]
**Author**: [name]
**Status**: [Draft | Review | Approved]

---

## Objective

[1-3 sentences. What does this agent do, for whom, and how will you know it succeeded?]

**Goal statement**: [One sentence — the result of the VISION phase three-test review]

---

## Tech Stack

[Specific versions and dependencies the agent operates within]

- **Language**: [e.g., Python 3.12]
- **Framework**: [e.g., FastAPI 0.111]
- **Package manager**: [e.g., uv]
- **Test framework**: [e.g., pytest]
- **Linter**: [e.g., ruff]

---

## Commands

All commands are copy-paste executable. `[NEEDS INPUT]` markers indicate values to be filled in before deployment.

| Operation | Command |
|-----------|---------|
| Build | `[exact build command]` |
| Test | `[exact test command]` |
| Lint | `[exact lint command]` |
| Format | `[exact format command]` |
| Install | `[exact install command]` |

---

## Testing

- **Test directory**: `[path]`
- **Coverage requirement**: [N]%
- **Test procedure**: [exact steps to run tests and interpret results]
- **CI verification**: [link to CI config or describe the pipeline]

---

## Project Structure

```
[repo-root]/
├── [dir]/          # [purpose]
├── [dir]/          # [purpose]
│   ├── [subdir]/   # [purpose]
│   └── [file]      # [purpose]
└── [file]          # [purpose]
```

---

## Code Style

[Include actual code examples demonstrating preferred patterns — not prose rules.]

```[language]
# Preferred: [description]
[example code]

# Avoid: [description]
[counter-example code]
```

---

## Git Workflow

- **Branch naming**: `[pattern, e.g., feat/*, fix/*, chore/*]`
- **Commit format**: `[e.g., conventional commits: feat(scope): description]`
- **PR requirements**: [e.g., 1 approval, CI green, no draft PRs]
- **Main branch protection**: [yes/no, rules]

---

## Boundaries

| Tier | Actions |
|------|---------|
| ✅ **Always** (no approval needed) | [action 1], [action 2], [action 3] |
| ⚠️ **Ask First** (require review) | [action 1], [action 2], [action 3] |
| 🚫 **Never** (hard stops) | [action 1], [action 2], [action 3] |

---

## Self-Checks

Before reporting completion, the agent MUST verify:

- [ ] [Check 1 — tied to a specific spec requirement]
- [ ] [Check 2 — tied to a specific spec requirement]
- [ ] [Check 3 — tied to a specific spec requirement]

---

## Success Criteria

| Goal | Success Criterion | How to Verify |
|------|-----------------|---------------|
| [goal] | [specific, measurable outcome] | [third-party verification method] |

---

## Error Recovery

| Problem | Indicators | Recovery |
|---------|-----------|---------|
| [problem] | [symptom] | [steps] |

---

## Revision History

| Version | Date | Changes | Trigger |
|---------|------|---------|---------|
| 1.0 | [date] | Initial spec | [what prompted this] |

---

## Open Gaps

Items marked `[NEEDS INPUT]` that must be resolved before deployment:

- [ ] [Gap 1: what information is needed and where to find it]
- [ ] [Gap 2: what information is needed and where to find it]
```

---

## Format 5: GitHub Spec Kit (`specs/[###-feature-name]/` directory)

> **⚠️ GROUNDED LOOKUP REQUIRED before generating any file in this format.**
>
> Call `search_knowledge(query="...")` with the queries below **before** producing output.
> The KB contains the authoritative templates. Do not generate from training data alone.
>
> ```
> # For spec.md:
> search_knowledge(query="github spec kit spec template feature user stories priority")
>
> # For plan.md:
> search_knowledge(query="spec kit plan template technical context research data model")
>
> # For tasks.md:
> search_knowledge(query="spec kit tasks template user story parallel task format")
>
> # For constitution.md (only if needed):
> search_knowledge(query="spec kit constitution template principles nine articles")
> ```
>
> KB source paths:
> - `internal/github-spec-kit-spec-template.md`
> - `internal/github-spec-kit-plan-template.md`
> - `internal/github-spec-kit-tasks-template.md`
> - `internal/github-spec-kit-constitution-template.md`

The GitHub Spec Kit (`github/spec-kit`) implements a **Specify → Plan → Tasks** gated workflow
supporting Claude Code, GitHub Copilot, Gemini CLI, opencode, Cursor, Windsurf, and more.
Released September 2024, 55k+ stars.

Supported slash commands: `/speckit.specify`, `/speckit.plan`, `/speckit.tasks`
(invoked via each tool's command directory — see agent-directory table below)

### Directory Structure (per feature)

```
specs/[###-feature-name]/
├── spec.md          # Feature spec — output of /speckit.specify
├── plan.md          # Implementation plan — output of /speckit.plan
├── research.md      # Technical research — phase 0 output of /speckit.plan
├── data-model.md    # Entity/schema definitions — phase 1 output of /speckit.plan
├── quickstart.md    # Validation scenarios — phase 1 output of /speckit.plan
├── contracts/       # API contract definitions — phase 1 output of /speckit.plan
└── tasks.md         # Executable task list — output of /speckit.tasks (NOT /speckit.plan)
```

Optional project-level file (not per-feature):

```
memory/constitution.md   # Non-negotiable project principles — maps to GUARDRAILS Never tier
```

### Agent Command File Directories

The Specify CLI generates agent-specific command files when bootstrapping a project:

| Agent | Directory | Format | CLI Tool |
|-------|-----------|--------|----------|
| Claude Code | `.claude/commands/` | Markdown | `claude` |
| GitHub Copilot | `.github/agents/` | Markdown | N/A (IDE) |
| Gemini CLI | `.gemini/commands/` | TOML | `gemini` |
| opencode | `.opencode/command/` | Markdown | `opencode` |
| Cursor | `.cursor/commands/` | Markdown | `cursor-agent` |
| Windsurf | `.windsurf/workflows/` | Markdown | N/A (IDE) |

### Workflow Summary

| Phase | Command | Output |
|-------|---------|--------|
| Specify | `/speckit.specify` | `specs/[###]/spec.md` — feature spec with user stories |
| Plan | `/speckit.plan` | `plan.md` + `research.md` + `data-model.md` + `contracts/` + `quickstart.md` |
| Tasks | `/speckit.tasks` | `tasks.md` — organized by user story, with parallel markers |
| Execute | Agent works from tasks.md | Implementation guided by spec + plan + tasks |

**Gate rule:** `spec.md` must exist before `/speckit.plan` runs. `plan.md` must exist before `/speckit.tasks` runs.

---

### `spec.md` (Feature Specification)

Path: `specs/[###-feature-name]/spec.md`
Produced by: `/speckit.specify` (VISION + STRUCTURE phases)

```markdown
# Feature Specification: [FEATURE NAME]

**Feature Branch**: `[###-feature-name]`
**Created**: [DATE]
**Status**: Draft
**Input**: User description: "[goal statement from VISION phase]"

---

## User Scenarios & Testing *(mandatory)*

<!--
  User stories must be PRIORITIZED as user journeys ordered by importance.
  Each story must be INDEPENDENTLY TESTABLE — implementing just one story
  should produce a viable MVP that delivers value.

  Priority: P1 = most critical, P2 = important, P3 = nice to have.
-->

### User Story 1 — [Brief Title] (Priority: P1)

[Describe this user journey in plain language]

**Why this priority**: [Explain the value and urgency]

**Independent Test**: [How this story can be tested in isolation — e.g., "Can be fully tested
by [specific action] and delivers [specific value] without any other stories being complete"]

#### Acceptance Criteria

- [ ] [Specific, verifiable criterion — written as a testable assertion]
- [ ] [Specific, verifiable criterion]
- [ ] [Specific, verifiable criterion]

---

### User Story 2 — [Brief Title] (Priority: P2)

[Describe this user journey in plain language]

**Why this priority**: [Explain the value and why it is lower than P1]

**Independent Test**: [How this story can be tested in isolation]

#### Acceptance Criteria

- [ ] [Specific, verifiable criterion]
- [ ] [Specific, verifiable criterion]

---

## Out of Scope

<!--
  IMPORTANT: List explicit exclusions to prevent scope creep.
  "Out of Scope" is as important as "In Scope" — it prevents the agent from
  absorbing adjacent work and losing focus.
-->

- [Explicit exclusion 1 — prevents scope creep]
- [Explicit exclusion 2]

---

## Technical Notes

<!--
  Optional but recommended: anything the agent needs to know before starting
  that is not obvious from the user stories.
-->

- [Technical constraint, dependency, or gotcha]
- [NEEDS INPUT: anything unknown at spec time]

---

## Open Questions

- [ ] [Question 1 — what decision is still open, who owns it, when it must be resolved]
- [ ] [Question 2]
```

---

### `plan.md` (Implementation Plan)

Path: `specs/[###-feature-name]/plan.md`
Produced by: `/speckit.plan` (architecture planning pass after `spec.md` is approved)

```markdown
# Implementation Plan: [FEATURE NAME]

**Branch**: `[###-feature-name]` | **Date**: [DATE] | **Spec**: [link to spec.md]
**Input**: Feature specification from `specs/[###-feature-name]/spec.md`

---

## Summary

[Extract from feature spec: primary requirement + technical approach from research]

---

## Technical Context

**Language/Version**: [e.g., Python 3.12, .NET 10, TypeScript 5.x — or NEEDS CLARIFICATION]
**Primary Dependencies**: [e.g., FastAPI, ASP.NET Core, React — or NEEDS CLARIFICATION]
**Storage**: [if applicable, e.g., PostgreSQL, SQLite, files — or N/A]
**Testing**: [e.g., pytest, xUnit, Vitest — or NEEDS CLARIFICATION]
**Target Platform**: [e.g., Linux server, iOS 15+, browser — or NEEDS CLARIFICATION]
**Project Type**: [e.g., library / cli / web-service / mobile-app / desktop-app]
**Performance Goals**: [domain-specific — or NEEDS CLARIFICATION]
**Constraints**: [e.g., <200ms p95, <100MB memory — or NEEDS CLARIFICATION]
**Scale/Scope**: [e.g., 10k users, single-tenant, offline-capable — or NEEDS CLARIFICATION]

---

## Architecture

### System Context

[Who uses the system and what external systems does it interact with?]

### Key Components

| Component | Responsibility | Technology |
|-----------|---------------|------------|
| [name] | [what it does] | [stack] |
| [name] | [what it does] | [stack] |

### Data Flow

[How data moves through the system. Include sequence for the primary use case.]

---

## Requirement Mapping

| User Story | Implementation Approach | Component |
|------------|------------------------|-----------|
| US1: [title] | [How this story is satisfied] | [Which component] |
| US2: [title] | [How this story is satisfied] | [Which component] |

---

## Technical Decisions

| Decision | Choice | Rationale | Alternatives Rejected |
|----------|--------|-----------|----------------------|
| [e.g., Database] | [e.g., PostgreSQL] | [Why] | [What else was considered] |

[Record each significant decision as an ADR. See `architecture-journal` skill.]

---

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| [risk] | High/Med/Low | High/Med/Low | [mitigation] |

---

## Project Structure

```
[repo-root]/
├── [dir]/          # [purpose]
├── [dir]/          # [purpose]
│   ├── [subdir]/   # [purpose]
│   └── [file]      # [purpose]
└── [file]          # [purpose]
```

### Documentation (this feature)

```
specs/[###-feature]/
├── plan.md              # This file
├── research.md          # Phase 0 output — technical background
├── data-model.md        # Phase 1 output — entity/schema definitions
├── quickstart.md        # Phase 1 output — key validation scenarios
├── contracts/           # Phase 1 output — API contract definitions
└── tasks.md             # Phase 2 output (from /speckit.tasks — NOT this command)
```
```

---

### `tasks.md` (Executable Task List)

Path: `specs/[###-feature-name]/tasks.md`
Produced by: `/speckit.tasks` after `plan.md`, `data-model.md`, `contracts/`, and `research.md` exist

**Format:** `[ID] [P?] [Story] Description`
- `[P]` — task can run in parallel (different files, no conflicting dependencies)
- `[Story]` — which user story this task belongs to (US1, US2, US3...)
- Tasks are organized by user story to enable independent implementation and testing of each story

```markdown
# Tasks: [FEATURE NAME]

**Input**: Design documents from `specs/[###-feature-name]/`
**Prerequisites**: `plan.md` (required), `spec.md` (required for user stories),
                  `research.md`, `data-model.md`, `contracts/`

**Organization**: Tasks are grouped by user story to enable independent implementation
and testing. Each story can be implemented, tested, and demonstrated independently.

---

## User Story 1 — [Brief Title] (P1)

- [ ] T001 Create [specific thing] in `[exact/file/path]`
- [ ] T002 [P] [US1] Add [specific thing] in `[exact/file/path]`
- [ ] T003 [P] [US1] Implement [specific thing] — `[exact/file/path]`
- [ ] T004 [US1] Write tests for [specific thing] — `[exact/test/path]`
- [ ] T005 [US1] Verify acceptance criteria: [criterion from spec.md]

---

## User Story 2 — [Brief Title] (P2)

- [ ] T006 [US2] Add [specific thing] in `[exact/file/path]`
- [ ] T007 [P] [US2] Implement [specific thing] — `[exact/file/path]`
- [ ] T008 [US2] Write tests for [specific thing] — `[exact/test/path]`

---

## Integration

- [ ] T009 Run full test suite: `[exact test command from plan.md]`
- [ ] T010 Verify all acceptance criteria across all user stories are met

---

## Out of Scope

- [Explicit exclusion — prevents task from absorbing adjacent work from other features]
```

---

### `constitution.md` (Non-Negotiable Principles) — Optional

Path: `memory/constitution.md` (project root, not per-feature)
Only produce this file if the project has non-negotiable agent behavior constraints.
Maps directly to the GUARDRAILS phase Never tier. Omit if no hard constraints exist.

```markdown
# [PROJECT NAME] Constitution

**Version**: [N]
**Date**: [YYYY-MM-DD]

> These principles are non-negotiable. They apply in every session, to every agent
> working in this repository, regardless of other instructions.

---

## Core Principles

### I. [Principle Name — e.g., Library-First]

[Principle description — e.g., "Every feature begins as a standalone library.
Libraries must be self-contained, independently testable, and documented."]

### II. [Principle Name — e.g., Test-First (NON-NEGOTIABLE)]

[Principle description — e.g., "TDD mandatory: tests written → user approved →
tests fail → then implement. Red-Green-Refactor cycle strictly enforced."]

### III. [Principle Name — e.g., CLI Interface]

[Principle description — e.g., "Every library exposes functionality via CLI.
Text in/out protocol: stdin/args → stdout, errors → stderr."]

### IV. [Principle Name — e.g., Integration Testing]

[Principle description]

[Add principles until the spec's Never tier is fully covered]

---

## Always (No Approval Needed)

- [Safe, routine action the agent performs automatically]
- [Safe, routine action the agent performs automatically]

---

## Ask First (Require Human Approval)

- [High-impact or irreversible action requiring confirmation]
- [High-impact or irreversible action requiring confirmation]

---

## Never (Hard Stops)

- 🚫 [Forbidden action — specific and verifiable]
- 🚫 Never commit secrets, credentials, or API keys
- 🚫 Never push directly to the main/production branch
- 🚫 Never modify production data without explicit approval
- 🚫 [Domain-specific hard stop]

---

## Revision History

| Version | Date | Change |
|---------|------|--------|
| 1.0 | [date] | Initial constitution |
```

**Key notes for GitHub Spec Kit:**
- Files live under `specs/[###-feature-name]/` per feature — not `.specify/`
- `constitution.md` lives at `memory/constitution.md` in the project root — not per-feature
- `spec.md` is approved before `plan.md` is written; `plan.md` approved before `tasks.md` is generated
- `tasks.md` is produced by `/speckit.tasks` only — **not** by `/speckit.plan`
- Each task must reference an exact file path and exactly one user story
- `[P]` markers enable safe parallel execution by agents
- Use `architecture-journal` skill to record technical decisions from `plan.md` as ADRs
- **Always call `search_knowledge(query="...")` before generating any of these files**
