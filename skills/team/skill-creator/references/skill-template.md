# Skill Template — Blank Scaffold (5-Section Lean Layout)

This is the canonical blank template for a new full-template SKILL.md. The five sections below are
all that belong in SKILL.md. **Depth — the full Domain Principles table, AI Discipline (WRONG/RIGHT)
rules, Anti-Patterns table, Error Recovery scenarios, and code/report templates — goes in
`references/`, not in SKILL.md.** Keep SKILL.md ≤ 200 lines; every always-loaded line is a
per-invocation token tax. Each reference file must be named by a pointer in the Output Template
section so nothing becomes undiscoverable.

---

```markdown
---
name: <skill-name>
description: >
  <One sentence stating the skill's purpose and primary output.> Use when
  <list specific trigger scenarios>. Trigger phrases: "<phrase1>", "<phrase2>",
  "<phrase3>". Do NOT use when <negative scenario 1>; do NOT use when
  <negative scenario 2> — use <alternative skill> instead.
---

# <Skill Title>

> "<Epigraph quote relevant to the skill's domain.>"
> -- <Attribution>

## Core Philosophy

<2–4 sentences describing the skill's guiding philosophy and what makes it distinct.>

**Non-Negotiable Constraints:**
1. <Constraint 1 — a hard rule the agent must never violate. Fold the Critical/High principles here.>
2. <Constraint 2>
3. <Constraint 3>
4. <Constraint 4>
5. <Constraint 5>

The full principle table, discipline rules, anti-patterns, and error recovery live in
`references/conventions.md`.

## Workflow

​```
PHASE 1   <imperative action>. If <condition>, then <action>; otherwise <action>.
PHASE 2   <action>.  (Detail/templates in references/<file>.md.)
PHASE 3   <action>.
...
​```

**Exit criteria:** <the binary, verifiable condition that means the work is done.>

## State Block

​```
<<skill-name>-state>
phase: <phase1> | <phase2> | <phase3> | COMPLETE
<field1>: <description>
<field2>: <description>
last_action: [what was just completed]
next_action: [what happens next]
</<skill-name>-state>
​```

## Output Template

- **<report/code template name>** — `references/<file>.md`.
- **<another template or pattern catalog>** — `references/<file>.md`.
- **Principle table, discipline rules, anti-patterns, error recovery** — `references/conventions.md`.

## Integration with Other Skills

| Skill | Relationship |
|-------|-------------|
| `<skill-name>` | <How this skill relates to or hands off to the named skill.> |
| `<skill-name>` | <Relationship description.> |
```

---

## What goes in `references/` (not SKILL.md)

Create at least two reference files. A common split:

- **`conventions.md`** — the full Domain Principles table (10 rows), the AI Discipline rules with
  WRONG/RIGHT examples, the Anti-Patterns table (≥ 8 rows), and the Error Recovery scenarios
  (≥ 3, each with Symptom + numbered recovery). This is the depth the Core Philosophy constraints summarize.
- **`<domain>-templates.md`** (or `output-templates.md`) — the report/code templates the skill
  emits, as complete fenced blocks with labeled placeholders.

Add more reference files for large pattern catalogs, decision matrices, or language-specific detail.
Every reference file must be named by a pointer in the Output Template section of SKILL.md.
