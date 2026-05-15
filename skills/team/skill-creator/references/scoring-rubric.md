# Skill Quality Scoring Rubric

Use this rubric when running `/skill-creator` in SCORE mode. Apply each dimension
independently. Assign an integer 1–5 based on the evidence criteria below.

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
| 5 | Description uses domain-specific nouns and action verbs. Would not trigger on adjacent skills. Includes "Do NOT use when..." clause with ≥ 2 specific negative scenarios and named alternatives. |
| 4 | Strong positive trigger. Negative clause present but only 1 scenario named, or alternative skill not specified. |
| 3 | Positive trigger is moderately specific. Negative clause present but vague ("do not use for unrelated tasks"). |
| 2 | Positive trigger is generic (e.g., "use for .NET development"). No negative clause. |
| 1 | Description is missing, one sentence only, or uses only hedging language. No negative trigger. |

---

## Dimension 2 — Core Philosophy Completeness

Does the Core Philosophy section set hard behavioral boundaries?

| Score | Criteria |
|-------|----------|
| 5 | 3–5 numbered Non-Negotiable Constraints stated as imperatives. Each constraint is specific enough that an agent could be tested against it. |
| 4 | Constraints present but ≤ 2, or some are stated as preferences rather than hard rules. |
| 3 | Philosophy present but no explicit "Non-Negotiable Constraints" list. Rules embedded in narrative. |
| 2 | Section exists but is purely narrative with no actionable constraints. |
| 1 | Section missing or contains only a one-sentence description of the skill. |

---

## Dimension 3 — Domain Principles Table

Is the Domain Principles Table present, complete, and domain-specific?

| Score | Criteria |
|-------|----------|
| 5 | 10 rows. All four columns populated (# / Principle / Description / Applied As). "Applied As" column gives concrete agent instructions, not restatements of the description. |
| 4 | 8–9 rows. All columns present. "Applied As" column is partially generic. |
| 3 | 5–7 rows. Or all 10 rows present but "Applied As" column is missing or all identical. |
| 2 | Table present but fewer than 5 rows, or missing columns. |
| 1 | Table missing. Principles described only in narrative. |

---

## Dimension 4 — Workflow Completeness

Is the Workflow section a deterministic decision tree an agent can execute?

| Score | Criteria |
|-------|----------|
| 5 | Every step is an imperative. All conditionals have explicit branches. Includes verification checklist. Completion exit criteria stated. |
| 4 | Most steps are imperatives. One or two open-ended steps remain. Verification present. |
| 3 | Workflow present but mixes imperatives and narrative. No explicit verification checklist. |
| 2 | Workflow is a numbered list of phases with minimal detail. No branching logic. |
| 1 | Workflow section missing, or describes what the skill does rather than how the agent should execute it. |

---

## Dimension 5 — State Block Presence and Uniqueness

Is the state block present, well-formed, and non-conflicting?

| Score | Criteria |
|-------|----------|
| 5 | XML tag is unique across the skill suite (verified by grep). Tag derives from skill name. Fields cover all workflow phases. `last_action` and `next_action` fields present. |
| 4 | Tag present and unique. Missing `last_action` or `next_action`, or one phase is not represented. |
| 3 | State block present but tag does not derive from skill name, or fields are minimal (< 4). |
| 2 | State block present but tag name conflicts with another skill (potential collision). |
| 1 | State block section missing. |

---

## Dimension 6 — Output Templates

Are structured output templates present for each workflow phase that produces output?

| Score | Criteria |
|-------|----------|
| 5 | ≥ 2 templates. Each template is a complete fenced code block with labeled placeholders. Templates match the workflow phases. |
| 4 | ≥ 2 templates. One template is partially complete or lacks labeled placeholders. |
| 3 | 1 template only, or templates are prose descriptions rather than formatted examples. |
| 2 | Templates mentioned but not provided (e.g., "output a report with these fields"). |
| 1 | Output Templates section missing. |

---

## Dimension 7 — AI Discipline Rules with WRONG/RIGHT Examples

Are the AI Discipline Rules present with concrete behavioral anchors?

| Score | Criteria |
|-------|----------|
| 5 | ≥ 3 CRITICAL rules. Each rule has at least one WRONG/RIGHT fenced code or prose block. WRONG cases are specific failure modes, not generic warnings. |
| 4 | ≥ 3 rules present. 1–2 rules lack WRONG/RIGHT examples. |
| 3 | Rules present but stated as prose only (no WRONG/RIGHT blocks). |
| 2 | Section present but fewer than 3 rules, and no WRONG/RIGHT examples. |
| 1 | AI Discipline Rules section missing. |

---

## Dimension 8 — Anti-Patterns Table

Is the Anti-Patterns table present and sufficiently populated?

| Score | Criteria |
|-------|----------|
| 5 | ≥ 8 rows. Three columns: Anti-Pattern / Why It Fails / Correct Approach. "Why It Fails" explains the failure mechanism, not just "it is bad". "Correct Approach" is actionable. |
| 4 | 6–7 rows. All columns present. Some rows have generic "Why It Fails" entries. |
| 3 | 4–5 rows. Or missing "Why It Fails" column. |
| 2 | Table present but fewer than 4 rows. |
| 1 | Anti-Patterns section missing. |

---

## Dimension 9 — Error Recovery Scenarios

Are concrete error recovery procedures present?

| Score | Criteria |
|-------|----------|
| 5 | ≥ 3 named scenarios. Each has: Symptom (what the agent observes) + numbered Recovery steps. Recovery steps are executable by an agent without human intervention. |
| 4 | ≥ 3 scenarios. 1–2 scenarios have vague symptoms or non-executable recovery steps. |
| 3 | 1–2 scenarios only. Or scenarios are described as prose rather than structured recovery procedures. |
| 2 | Section present but contains only general advice (e.g., "stop and ask the user"). |
| 1 | Error Recovery section missing. |

---

## Dimension 10 — References Directory

Does the skill have a populated references/ directory?

| Score | Criteria |
|-------|----------|
| 5 | ≥ 2 files. Files are named descriptively (e.g., `scoring-rubric.md`, `question-catalog.md`). SKILL.md references these files by relative path in the appropriate sections. |
| 4 | ≥ 2 files present. SKILL.md does not reference them explicitly but they are relevant. |
| 3 | 1 file only. Or files exist but are empty or placeholder-only. |
| 2 | Directory exists but is empty. |
| 1 | references/ directory missing. |
