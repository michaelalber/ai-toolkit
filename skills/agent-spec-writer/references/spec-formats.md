# Spec Format Templates

Complete templates for all four target formats. Use these during the GENERATE phase of `agent-spec-writer`.

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
