# Skill Quality Scoring Rubric (5-Section Lean Layout)

Use this rubric when running `/skill-creator` in SCORE mode. Apply each dimension independently.
Assign an integer 1–5 based on the evidence criteria below. The rubric scores a full-template skill
against the 5-section lean layout: lean SKILL.md, depth in `references/`.

**Score thresholds:**

| Total | Verdict | Action |
|-------|---------|--------|
| 45–50 | EXEMPLARY | No action required. |
| 35–44 | PASS | Minor improvements welcome but not blocking. |
| 25–34 | REVISE | List specific defects. Schedule revision. |
| < 25 | DEPRECATE | Draft a replacement spec before revising. |

---

## Dimension 1 — Trigger Precision

Does the `description:` field trigger correctly and only in the right scenarios?

| Score | Criteria |
|-------|----------|
| 5 | Domain-specific nouns and action verbs. Would not trigger on adjacent skills. Includes "Do NOT use when..." with ≥ 2 specific negative scenarios and named alternatives. |
| 4 | Strong positive trigger. Negative clause present but only 1 scenario named, or alternative not specified. |
| 3 | Moderately specific positive trigger. Negative clause present but vague. |
| 2 | Generic positive trigger (e.g., "use for .NET development"). No negative clause. |
| 1 | Missing, one sentence only, or only hedging language. No negative trigger. |

## Dimension 2 — Core Philosophy + Non-Negotiable Constraints

Does Core Philosophy set hard boundaries and absorb the Critical/High principles as constraints?

| Score | Criteria |
|-------|----------|
| 5 | 3–5 numbered Non-Negotiable Constraints as imperatives; each testable. The skill's Critical/High principles are represented here (full table lives in references). |
| 4 | Constraints present but ≤ 2, or some stated as preferences rather than hard rules. |
| 3 | Philosophy present but no explicit constraints list; rules embedded in narrative. |
| 2 | Purely narrative, no actionable constraints. |
| 1 | Missing, or one-sentence description only. |

## Dimension 3 — Lean Layout Discipline

Does SKILL.md follow the 5-section layout and stay within budget?

| Score | Criteria |
|-------|----------|
| 5 | Exactly the 5 sections (Core Philosophy, Workflow, State Block, Output Template, Integration) + title/epigraph. SKILL.md ≤ 200 lines. No inline principle/anti-pattern/error-recovery tables. |
| 4 | 5-section layout; ≤ 250 lines; at most one heavy table still inline. |
| 3 | Mostly lean but 1–2 extra sections, or 250–320 lines, or some depth not yet moved to references. |
| 2 | Still on the legacy 10-section shape, or 320–400 lines. |
| 1 | > 400 lines, or depth fully inline with no references offload. |

## Dimension 4 — Workflow Completeness

Is the Workflow a deterministic decision tree an agent can execute?

| Score | Criteria |
|-------|----------|
| 5 | Every step is an imperative; all conditionals have explicit branches; exit criteria stated. Long decision trees/step prose are offloaded to references with a pointer. |
| 4 | Most steps imperative; one or two open-ended; exit criteria present. |
| 3 | Mixes imperatives and narrative; no exit criteria. |
| 2 | Numbered list of phases with minimal detail; no branching. |
| 1 | Missing, or describes what the skill does rather than how to execute it. |

## Dimension 5 — State Block Presence and Uniqueness

Is the state block present, well-formed, and non-conflicting?

| Score | Criteria |
|-------|----------|
| 5 | XML tag unique across the suite (grep-verified), derives from the skill name, covers all phases; `last_action`/`next_action` present. |
| 4 | Tag present and unique; missing `last_action`/`next_action` or one phase unrepresented. |
| 3 | Present but tag doesn't derive from the name, or < 4 fields. |
| 2 | Tag conflicts with another skill (potential collision). |
| 1 | Missing (and the skill has multi-step state worth tracking). |

## Dimension 6 — Output Template as Pointers

Does the Output Template section point to the report/code templates in `references/`?

| Score | Criteria |
|-------|----------|
| 5 | Every emitted template/pattern catalog is named with a relative `references/...` pointer; no full templates inline. |
| 4 | Pointers present; one small template still inline. |
| 3 | Mix of pointers and inline templates. |
| 2 | Templates inline in SKILL.md rather than referenced. |
| 1 | No output guidance at all. |

## Dimension 7 — Integration Declaration

Does the Integration section name every related skill?

| Score | Criteria |
|-------|----------|
| 5 | Table naming every skill this one references, depends on, or hands off to, each with a relationship. No implicit dependencies. |
| 4 | Most relationships named; one handoff implied but not stated. |
| 3 | Some integrations listed; relationships terse. |
| 2 | Section present but lists names without relationships. |
| 1 | Missing. |

## Dimension 8 — References Depth

Do `references/` hold the relocated depth — principle table, discipline rules, anti-patterns, error recovery?

| Score | Criteria |
|-------|----------|
| 5 | `conventions.md` (or equivalents) contains a 10-row principle table, ≥ 3 WRONG/RIGHT discipline rules, ≥ 8-row anti-patterns table, and ≥ 3 error-recovery scenarios (Symptom + numbered steps). |
| 4 | All four present; one is thin (e.g., 6-row anti-patterns or 2 recovery scenarios). |
| 3 | Two or three of the four present. |
| 2 | Only one present, or all are stubs. |
| 1 | Depth missing entirely (neither inline nor in references). |

## Dimension 9 — Reference Hygiene

Is the `references/` directory well-formed and wired to SKILL.md?

| Score | Criteria |
|-------|----------|
| 5 | ≥ 2 descriptively named files; every file is named by a pointer in SKILL.md's Output Template section. |
| 4 | ≥ 2 files; not all are explicitly pointed to but all are relevant. |
| 3 | 1 file only, or files present but not referenced. |
| 2 | Directory exists but empty. |
| 1 | `references/` missing. |

## Dimension 10 — AI-First Phrasing

Is the prose written for an AI agent — imperatives, no hedging, concrete anchors?

| Score | Criteria |
|-------|----------|
| 5 | Imperatives throughout; no hedging ("you might", "consider"); WRONG/RIGHT anchors present in `references/conventions.md`. |
| 4 | Mostly imperative; occasional hedging. |
| 3 | Mix of imperative and narrative; few concrete anchors. |
| 2 | Largely narrative; open-ended conditionals ("use your judgment"). |
| 1 | Narrative throughout; no actionable phrasing. |
