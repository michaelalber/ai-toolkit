---
name: jira-review
audience: team
description: >
  Automatically review Jira issues for implementation readiness. Detects complexity
  signals, parses acceptance criteria, and recommends clarification or planning mode
  when needed. Use when asked to review a Jira issue for readiness, check if a ticket has enough detail to implement, assess acceptance criteria completeness, or evaluate a story before sprint planning. Do NOT use when implementation is already complete — this skill
  reviews for readiness, not post-implementation accuracy; Do NOT use when the
  issue tracker is not Jira.
---

# Jira Issue Review

> "Unclear requirements are the root cause of most project failures.
> Questions asked now prevent misunderstandings later."

## Core Philosophy

Before writing a single line of code, we must understand what we're building and why. This skill
systematically reviews Jira issues *before* implementation to prevent wasted effort (catch ambiguity
early), surface hidden complexity (identify technical risk before it blocks), ensure testability
(clear AC enable TDD), and align expectations. Readiness is assessed from measurable signals, not
intuition — complexity is scored, gaps are named, and the recommendation follows deterministically.

**Non-Negotiable Constraints:**
1. TESTABILITY IS A GATE — no issue passes review without ≥ 1 acceptance criterion expressible as a test.
2. AMBIGUITY IS BLOCKING — any requirement admitting two interpretations is flagged as a blocker, not a suggestion.
3. SCORES NEED EVIDENCE — every complexity score lists the signals that produced it; never guess.
4. FLAG GAPS BY NAME — name the missing element and why it blocks, never "this is unclear."
5. CRITICAL-INFO OVERRIDES — missing AC, vague success criteria, or missing reproduction steps force NEEDS CLARIFICATION regardless of complexity.

Full principle table, extraction algorithm, scoring, signal detection, discipline rules, and worked
examples live in `references/conventions.md`.

## Workflow

```
TRIGGER    Auto-activate on jira_get_issue / jira_get_issue_with_docs. Review before any impl work.

EXTRACT    Parse the description for AC, DoD, user story, technical requirements (algorithm + patterns
           in conventions.md / description-patterns.md). Flag unstructured descriptions.

SCORE      Apply the 5-dimension weighted complexity score (conventions.md / complexity-scoring.md).
           Detect RED/YELLOW/GREEN signals. Record the signals behind the score.

RECOMMEND  Decide deterministically:
             complexity < 40% AND ac_complete AND dod_present     → READY TO IMPLEMENT (→ /tdd-cycle)
             complexity > 70% OR critical_info_missing            → NEEDS PLANNING MODE (→ plan mode)
             otherwise                                            → NEEDS CLARIFICATION
                                                                    (≤ 5 questions, clarifying-questions.md)

REPORT     Emit the structured review (output-templates.md) with the recommendation, named gaps,
           and the handoff snippet for the chosen path.
```

**Exit criteria:** AC/DoD extracted (or their absence flagged), complexity scored with named
signals, a single deterministic recommendation issued, and — when NEEDS CLARIFICATION — specific,
prioritized questions provided.

## State Block

```
<jira-review-state>
phase: TRIGGER | EXTRACT | SCORE | RECOMMEND | REPORT | COMPLETE
issue_key: [KEY-123]
issue_type: story | bug | task | epic
ac_found: yes | no | partial
dod_found: yes | no | partial
complexity_pct: [number or "unable to assess"]
critical_info_missing: true | false
recommendation: ready | needs-clarification | needs-planning | pending
open_questions: [count]
last_action: [description]
next_action: [description]
</jira-review-state>
```

## Output Template

- **Structured issue review, handoff snippets** — `references/output-templates.md`.
- **5-dimension scoring system, formula, thresholds** — `references/complexity-scoring.md`.
- **Description parsing patterns (AC/DoD/BDD extraction)** — `references/description-patterns.md`.
- **Clarifying question templates** — `references/clarifying-questions.md`.
- **Principle table, extraction algorithm, signal detection, discipline rules, worked examples** — `references/conventions.md`.

## Integration with Other Skills

| Skill | Relationship |
|-------|-------------|
| `tdd-cycle` | The handoff for READY TO IMPLEMENT — write tests from the AC, implement, refactor. |
| `task-decomposition` | For NEEDS PLANNING MODE on high-complexity issues — break the issue into implementable sub-tasks. |
| `triage-issue` / `to-issues` | Upstream issue intake; this skill assesses readiness once an issue exists. |
