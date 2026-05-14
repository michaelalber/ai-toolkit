---
name: skill-creator
description: >
  Create, modify, and audit AI agent skills in this toolkit. Use when scaffolding
  a new SKILL.md from the 10-section template, revising an existing skill to fix
  structural defects, or scoring a skill against the 10-dimension rubric. Trigger
  phrases: "create skill", "new skill", "scaffold skill", "write skill", "revise
  skill", "update skill", "score skill", "audit skill quality".
  Do NOT use when the goal is to run a skill (invoke the skill directly); do NOT
  use when the goal is to create an agent definition (use AGENTS.md conventions).
---

# Skill Creator

> "Precision in instructions is not pedantry — it is the difference between a
>  tool that does what you intend and one that does what you said."
> -- Adapted from Fred Brooks, "The Mythical Man-Month"

## Core Philosophy

A skill is a reusable, invocable instruction set for an AI agent. Its quality is
measured by one criterion: does it cause the agent to behave correctly, reliably,
and without ambiguity? Beautiful prose, thorough explanations, and clever
abstractions are worthless if the skill triggers on the wrong prompts, fails to
stop when it should, or produces inconsistent outputs.

**Non-Negotiable Constraints:**

1. A skill that does not trigger reliably is worthless regardless of its internal quality. The trigger description is the most important line in the file.
2. Every new skill must have a `references/` directory with ≥ 2 supporting files before it is considered complete.
3. Revisions must not change state block XML tags — this is a breaking change for any in-flight sessions using the skill.
4. The 10-section template is the contract. Sections may be extended but never removed or reordered.

## Domain Principles Table

| # | Principle | Description | Applied As |
|---|-----------|-------------|------------|
| 1 | **Trigger-First Design** | The description field is the skill's contract with the dispatch layer. A poorly scoped description causes false positives (triggering when another skill is better) or false negatives (not triggering when it should). Trigger precision is the most valuable property a skill can have. | Write the description last, after the full skill body is written. Read the description in isolation — if it triggers on scenarios the skill cannot handle, narrow it. |
| 2 | **Negative Example Mandate** | An AI agent without WRONG/RIGHT examples will drift toward plausible-but-incorrect behavior under ambiguous inputs. Concrete counterexamples anchor the agent to correct behavior even when inputs are unusual. | Every AI Discipline Rule must include at least one WRONG and one RIGHT code or prose block. Rules stated without examples are incomplete. |
| 3 | **Scope Discipline** | A skill that tries to do three things does none of them reliably. Single responsibility in skills means one user goal, one workflow, one state machine. When a skill requires three separate workflows, it should be three skills. | If the workflow section has more than three distinct modes that cannot share the same state block, flag for decomposition. |
| 4 | **AI-First Phrasing** | Skills are read by AI agents, not humans. Instructions written for human judgment ("use your best judgment", "adapt as needed") produce inconsistent agent behavior. Instructions written as deterministic decision trees produce consistent behavior. | Every conditional in a workflow must have an explicit branch: "If X, then Y. If not X, then Z." No open-ended conditionals. |
| 5 | **Token Budget Discipline** | A skill that grows without bound will eventually overflow the context window of the agents that load it. Every line must earn its place. Repeated content, redundant explanations, and narrative padding are liabilities. | Target ≤ 300 lines for a single-mode skill; ≤ 400 lines for a multi-mode skill. Audit line count before finalizing. |
| 6 | **State Block Uniqueness** | State blocks use XML-style tags. If two skills share a tag name, an agent running both simultaneously cannot distinguish their state. Tag collisions are silent bugs. | Before finalizing any state block, grep the entire skills/ directory for the tag name. If it exists, rename it. |
| 7 | **References Directory Hygiene** | Reference files keep the SKILL.md lean by externalizing reusable tables, templates, and catalogs. A skill without a references/ directory forces all content inline, bloating the file and making updates harder. | Every skill gets a references/ directory with ≥ 2 files. Reference files named descriptively: `scoring-rubric.md`, `question-catalog.md`, not `refs.md`. |
| 8 | **WRONG/RIGHT Evidence Pattern** | The WRONG/RIGHT pattern is the most effective format for anchoring AI behavior. It shows the failure mode concretely, names it, and immediately follows with the correct behavior. Agents learn by contrast, not by rules alone. | Use fenced code blocks or prose blocks with explicit `WRONG:` and `RIGHT:` labels. Never embed WRONG/RIGHT examples in narrative paragraphs. |
| 9 | **Interop Declaration** | Skills do not exist in isolation. Agents combine skills, and skills reference each other. Undeclared interop creates invisible dependencies that break when skill names change. | The Integration section must name every skill this skill references, depends on, or hands off to. No implicit dependencies. |
| 10 | **Currency Maintenance** | A skill written for one version of a framework, API, or tool will silently degrade as those evolve. Stale skills are worse than no skills because they produce confident wrong answers. | Note version-sensitive content explicitly. Add a `# VERIFY:` comment on any API call, library function, or framework behavior that may change. |

## Workflow

### Mode: CREATE — Scaffold a New Skill

```
LOAD gold standard:
  Read skills/architecture-review/SKILL.md
  Note: section structure, description format, WRONG/RIGHT pattern, state block tag

INTAKE:
  Ask: What is the skill's one-sentence purpose?
  Ask: What are the trigger phrases?
  Ask: What are the negative trigger scenarios (Do NOT use when)?
  Ask: What workflow modes does it need? (1 = simple, 2-3 = multi-mode)

DRAFT:
  Write all 10 sections following the gold standard
  Section order: Title+Epigraph, Core Philosophy, Domain Principles,
    Workflow, State Block, Output Templates, AI Discipline Rules,
    Anti-Patterns, Error Recovery, Integration
  Leave stubs for any section where content is not yet known

DESCRIPTION QUALITY:
  The description is the only thing the model sees when deciding which skill to load.
  Write it last, after the full skill body is written.

  Rules:
  - Max 1024 chars
  - Third person: "Scaffolds...", "Audits...", "Extracts..."
  - First sentence: what the skill does
  - Second sentence: "Use when [specific trigger scenarios]"
  - Include "Do NOT use when..." to prevent false positives

  WRONG:
    description: >
      A powerful tool for NuGet package management.
      Very useful for .NET developers.

  RIGHT:
    description: >
      Scaffolds NuGet package metadata, CI/CD pipeline, and test harness.
      Use when publishing a new library to NuGet.org. Do NOT use for
      internal workspace-only libraries; use dotnet-vertical-slice instead.

VERIFY:
  [ ] All 10 sections present
  [ ] description field includes "Do NOT use when..." clause
  [ ] State block XML tag is unique (grep skills/ directory)
  [ ] ≥ 3 WRONG/RIGHT examples in AI Discipline Rules
  [ ] Anti-Patterns table has ≥ 8 rows
  [ ] Line count ≤ 400
  [ ] references/ directory created with ≥ 2 files

REPORT:
  State: skill path, sections complete, line count, references count, issues found
```

### Mode: REVISE — Fix an Existing Skill

```
LOAD:
  Read the target skill completely
  Read skills/architecture-review/SKILL.md (gold standard)
  Identify defects by comparing to 10-dimension rubric

PATCH:
  Address defects minimally — do not rewrite sections that are not broken
  Never change state block XML tag names
  Never remove sections; only add or correct content

VERIFY:
  Run the same checklist as CREATE mode
  Confirm: all sections present, no regressions in non-patched sections
  Confirm: state block XML tag unchanged from pre-revision

REPORT:
  State: what changed, why, line count before/after, issues remaining
```

### Mode: SCORE — Audit a Skill Against the Rubric

```
LOAD:
  Read the target skill completely
  Load references/scoring-rubric.md

SCORE:
  Apply each of the 10 rubric dimensions
  Assign 1–5 per dimension with evidence from the skill text

CLASSIFY:
  Total ≥ 45: EXEMPLARY
  Total 35–44: PASS
  Total 25–34: REVISE (flag specific defects)
  Total < 25: DEPRECATE (flag for replacement)

REPORT:
  Emit full scorecard table
  List issues by severity: CRITICAL (blocks correct behavior) → HIGH → MEDIUM
```

## State Block

```
<skill-creator-state>
mode: create | revise | score
target_skill: [skills/<name>/SKILL.md or "new"]
sections_complete: [N]/10
references_count: [N]
last_action: [what was just done]
next_action: [what should happen next]
</skill-creator-state>
```

## Output Templates

### New Skill Scaffold

```markdown
---
name: <skill-name>
description: >
  <one sentence purpose>. Use when <trigger scenarios>. Trigger phrases: "<phrase1>",
  "<phrase2>". Do NOT use when <negative scenario>; use <alternative> instead.
---

# <Skill Title>

> "<epigraph quote>"
> -- <attribution>

## Core Philosophy

<Non-negotiable constraints, 3–5 items>

## Domain Principles Table

| # | Principle | Description | Applied As |
|---|-----------|-------------|------------|
| 1 | **[Name]** | [Description] | [Applied As] |
...

## Workflow

<Decision-tree style steps>

## State Block

\`\`\`
<<skill-name>-state>
field: value
</<skill-name>-state>
\`\`\`

## Output Templates

<Structured templates for skill outputs>

## AI Discipline Rules

### CRITICAL: <Rule Name>

\`\`\`
WRONG: <wrong behavior>
RIGHT: <correct behavior>
\`\`\`

## Anti-Patterns Table

| # | Anti-Pattern | Why It Fails | Correct Approach |
|---|-------------|-------------|-----------------|

## Error Recovery

### <Scenario Name>

<Recovery steps>

## Integration with Other Skills

- **`<skill-name>`** — <relationship description>
```

### Revision Diff Summary

```markdown
## Skill Revision: <skill-name>

**Date**: <date>
**Mode**: REVISE
**Defects found**: <N>

### Changes Made

| Section | Change | Reason |
|---------|--------|--------|
| [section] | [what changed] | [why] |

### Line Count
Before: <N> lines
After: <N> lines

### State Block Tag
Unchanged: `<<skill-name>-state>` ✓

### Issues Remaining
- [ ] <any unresolved issues>
```

### Scorecard

```markdown
## Skill Quality Scorecard: <skill-name>

| # | Dimension | Score (1–5) | Evidence |
|---|-----------|-------------|---------|
| 1 | Trigger precision | [N] | [evidence from description field] |
| 2 | Negative trigger present | [N] | [evidence] |
| 3 | Domain Principles Table (10 rows) | [N] | [evidence] |
| 4 | Workflow completeness | [N] | [evidence] |
| 5 | State block present and unique | [N] | [evidence] |
| 6 | Output templates present | [N] | [evidence] |
| 7 | AI Discipline Rules with WRONG/RIGHT | [N] | [evidence] |
| 8 | Anti-Patterns table (≥ 8 rows) | [N] | [evidence] |
| 9 | Error Recovery scenarios | [N] | [evidence] |
| 10 | References directory (≥ 2 files) | [N] | [evidence] |
| — | **Total** | **[N]/50** | |

**Verdict**: EXEMPLARY / PASS / REVISE / DEPRECATE

**Critical issues** (blocks correct behavior):
- [issue]

**High issues** (degrades reliability):
- [issue]
```

## AI Discipline Rules

### CRITICAL: Always Load the Gold Standard Before Scaffolding

Creating a new skill from memory produces inconsistent structure. The gold standard (`skills/architecture-review/SKILL.md`) is the reference implementation. Every scaffold must start by reading it.

```
WRONG: Writing a new SKILL.md from scratch without reading the gold standard first.
       Result: missing sections, inconsistent state block format, weak trigger description.

RIGHT: Read skills/architecture-review/SKILL.md completely.
       Note: frontmatter format, section headers, WRONG/RIGHT block syntax, state block XML tag.
       Then scaffold following that exact structure.
```

### CRITICAL: Never Change a State Block XML Tag During Revision

State block tags are session identifiers. An agent mid-session with a `<jira-review-state>` block will lose its state if the skill is revised to use `<jira-state>`. This is a silent breaking change.

```
WRONG: Renaming <old-skill-state> to <new-skill-state> because the new name
       is "cleaner" or "more consistent".

RIGHT: Keep the existing XML tag. If fields need to change:
       - Add new fields with default values
       - Mark deprecated fields with a comment
       - Never rename the tag itself
```

### CRITICAL: Every Description Must Have a Negative Trigger

A description that only says what the skill does will trigger in every adjacent scenario. The negative trigger clause (`Do NOT use when...`) is what prevents the skill from being invoked inappropriately.

```
WRONG: description: >
         Creates NuGet packages with CI/CD pipeline setup and test harness.
         Use when publishing a library to NuGet.

RIGHT: description: >
         Creates NuGet packages with CI/CD pipeline setup and test harness.
         Use when publishing a library to NuGet. Do NOT use for internal
         workspace-only libraries not intended for publication; do NOT use
         for application projects — use dotnet-vertical-slice instead.
```

## Anti-Patterns Table

| # | Anti-Pattern | Why It Fails | Correct Approach |
|---|-------------|-------------|-----------------|
| 1 | **Skipping references/ creation** | Inline content bloats the skill and must be maintained in-place. Reference files can be updated without changing the SKILL.md token footprint. | Create the references/ directory before marking the skill complete. Minimum 2 files. |
| 2 | **Copying sections verbatim from another skill** | Copied sections carry the original skill's context, examples, and domain assumptions. They produce confusing behavior when adapted to a different domain. | Read the gold standard for structure only. Write every sentence from scratch for the target domain. |
| 3 | **Using "helpful/useful/powerful/comprehensive" in description** | These words are fillers that add no trigger signal. An agent uses the description for routing decisions, not evaluation. | Use domain-specific nouns and action verbs: "scaffolds", "audits", "generates", "validates". |
| 4 | **Writing narrative instead of imperatives** | Narrative ("The skill helps you think about...") is ambiguous to an AI agent. Imperatives ("Read the source file. Identify missing sections. Patch each.") are unambiguous decision points. | Write every workflow step as an imperative: "Read X. If Y, do Z. Otherwise, do W." |
| 5 | **Omitting WRONG/RIGHT examples** | Without counterexamples, an AI agent defaults to plausible behavior. Plausible is not the same as correct. | Every AI Discipline Rule must have at least one WRONG/RIGHT block. Rules without examples are placeholders, not instructions. |
| 6 | **Exceeding 300 lines without justification** | Long skills load slowly, consume disproportionate context, and often contain redundancy that degrades reliability. | Audit every section for repetition. Extract tables and templates to references/. Target ≤ 300 lines for single-mode skills. |
| 7 | **Bundling multiple responsibilities** | A skill that creates NuGet packages AND manages release pipelines AND audits security will produce inconsistent results across all three. Single responsibility produces reliable results for one thing. | If a skill has more than three workflow modes or more than one state machine, split it into separate skills. |
| 8 | **Writing a description that triggers on everything** | A description that says "use when working with .NET code" will outcompete every other .NET skill. It wins every race and fails every task. | Narrow the description to the specific output the skill produces. "Scaffolds NuGet package metadata and CI/CD pipeline" is specific. ".NET code help" is not. |
| 9 | **Using hedging language** | "You could consider...", "It may be helpful to...", "You might want to..." gives the agent permission to skip the instruction. | Use declarative language: "Do X", "Run Y", "If Z, stop and report." Hedging language is treated as optional. |
| 10 | **Missing Knowledge Base Lookups when grounded-code-mcp is available** | Skills that generate code without searching authoritative references produce answers based on training data alone, which may be outdated or incorrect. | Any skill generating code in a domain covered by grounded-code-mcp must include a Knowledge Base Lookups section. |

## Error Recovery

### Existing skill has no state block

```
Symptom: A SKILL.md has no <name-state> XML block.

Recovery:
1. Derive the tag name from the skill's name field: skills/<name>/SKILL.md → <<name>-state>
2. Check that no other skill uses this tag (grep skills/ for the proposed tag)
3. Add the state block section after the Output Templates section
4. Populate fields based on the workflow phases described in the skill
5. Note in the revision summary that this was added (not changed)
```

### Revision breaks a reference path

```
Symptom: A SKILL.md references a file in references/ that was renamed or removed.

Recovery:
1. Do not delete the original file — restore the original reference path
2. If the file was moved, add a redirect note at the top of the new file:
   "# Redirected from references/old-name.md"
3. Update the SKILL.md reference to point to the new path
4. Verify: test -f skills/<name>/references/<new-file>.md && echo "PASS"
```

### Score reveals score < 25/50 (DEPRECATE threshold)

```
Symptom: Scorecard total is below 25. Multiple CRITICAL issues found.

Recovery:
1. Flag the skill as DEPRECATE — do not attempt in-place revision
2. Draft a replacement spec documenting what the skill should do and what the
   current version fails to do
3. Present the spec to the user before writing a single line of the new skill
4. Keep the old skill in place (with a DEPRECATED header) until the replacement
   passes a score of ≥ 40
```

## Integration with Other Skills

- **`spec-coach`** — For creating agent definitions, PRDs, or GitHub Spec Kit files. When the user wants a new agent (a `.md` file in `claude/agents/` or `opencode/agents/`) or any interactive spec design session, use `spec-coach` instead of this skill.
- **`architecture-review`** — The gold standard for skill structure. Always load and read before scaffolding or revising. See `skills/architecture-review/SKILL.md`.
- **`automated-code-review`** — Use after creating or revising a skill to perform a quality check on the new content against project conventions.
- **`session-context`** — Use at the start of a revision session to understand what has changed in the skills suite since the last session before making any modifications.
