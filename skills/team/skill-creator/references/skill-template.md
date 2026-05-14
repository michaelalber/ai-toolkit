# Skill Template — Blank Scaffold

This file is the canonical blank template for a new SKILL.md. All 10 sections are
present as labeled stubs. Replace placeholder content with real content before
marking the skill complete.

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

1. <Constraint 1 — a hard rule the agent must never violate.>
2. <Constraint 2>
3. <Constraint 3>

## Domain Principles Table

| # | Principle | Description | Applied As |
|---|-----------|-------------|------------|
| 1 | **<Principle Name>** | <Why this principle matters in this domain.> | <How the agent applies it concretely.> |
| 2 | **<Principle Name>** | <Description> | <Applied As> |
| 3 | **<Principle Name>** | <Description> | <Applied As> |
| 4 | **<Principle Name>** | <Description> | <Applied As> |
| 5 | **<Principle Name>** | <Description> | <Applied As> |
| 6 | **<Principle Name>** | <Description> | <Applied As> |
| 7 | **<Principle Name>** | <Description> | <Applied As> |
| 8 | **<Principle Name>** | <Description> | <Applied As> |
| 9 | **<Principle Name>** | <Description> | <Applied As> |
| 10 | **<Principle Name>** | <Description> | <Applied As> |

## Workflow

<For single-mode skills, use a flat step list. For multi-mode, label each mode.>

### Mode: <MODE NAME> — <Brief Description>

\`\`\`
STEP 1: <action>
STEP 2: If <condition>, then <action>. Otherwise, <action>.
STEP 3: <action>

Verification:
[ ] <check 1>
[ ] <check 2>
\`\`\`

## State Block

\`\`\`
<<skill-name>-state>
phase: <phase1> | <phase2> | <phase3>
<field1>: <description>
<field2>: <description>
last_action: [what was just completed]
next_action: [what happens next]
</<skill-name>-state>
\`\`\`

## Output Templates

### <Template 1 Name>

\`\`\`markdown
## <Output Section Title>

<Template content with [PLACEHOLDER] markers for variable content>
\`\`\`

### <Template 2 Name>

\`\`\`markdown
<Template 2 content>
\`\`\`

## AI Discipline Rules

### CRITICAL: <Rule Name>

<One sentence describing the rule.>

\`\`\`
WRONG: <Description of the incorrect behavior. Specific, not generic.>

RIGHT: <Description of the correct behavior. Specific, not generic.>
\`\`\`

### CRITICAL: <Rule 2 Name>

\`\`\`
WRONG: <wrong>

RIGHT: <right>
\`\`\`

### CRITICAL: <Rule 3 Name>

\`\`\`
WRONG: <wrong>

RIGHT: <right>
\`\`\`

## Anti-Patterns Table

| # | Anti-Pattern | Why It Fails | Correct Approach |
|---|-------------|-------------|-----------------|
| 1 | **<Name>** | <Why this fails.> | <What to do instead.> |
| 2 | **<Name>** | <Why> | <Correct> |
| 3 | **<Name>** | <Why> | <Correct> |
| 4 | **<Name>** | <Why> | <Correct> |
| 5 | **<Name>** | <Why> | <Correct> |
| 6 | **<Name>** | <Why> | <Correct> |
| 7 | **<Name>** | <Why> | <Correct> |
| 8 | **<Name>** | <Why> | <Correct> |

## Error Recovery

### <Scenario 1 Name>

\`\`\`
Symptom: <What the agent observes that indicates this error.>

Recovery:
1. <First recovery action>
2. <Second recovery action>
3. <Third recovery action>
\`\`\`

### <Scenario 2 Name>

\`\`\`
Symptom: <description>

Recovery:
1. <action>
2. <action>
\`\`\`

## Integration with Other Skills

- **\`<skill-name>\`** — <How this skill relates to or hands off to the named skill.>
- **\`<skill-name>\`** — <Relationship description.>
```
