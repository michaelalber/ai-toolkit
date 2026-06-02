---
date: 2026-06-02T00:00:00
repository: ai-toolkit
topic: "QRSPI Slice 4 — qrspi-plan (vertical-not-horizontal planning)"
tags: [qrspi, implement, slice-4, plan, vertical-slice, re-slice-gate]
git_commit: 1e1c31f
plan_artifact: thoughts/qrspi-plan.md
phase: Implement (I)
slice: 4
branch: qrspi-slice-3-spec
status: complete
note: Backfilled after the fact (Slice 4 was built without a log in a prior session); reconstructed from commit a9ac8d3.
---

# QRSPI Implementation Log — Slice 4: `qrspi-plan`

Implements Slice 4 from `thoughts/qrspi-plan.md` §6. Adds the Plan phase: converts an approved
`spec.md` into a mechanically executable, vertically sliced `plan.md` with exact file paths and
per-phase verification — so the full **Q→R→S→P** alignment chain works end-to-end.

> **Backfill note:** this log was written after Slice 5, reconstructed from commit `a9ac8d3`
> (`feat: QRSPI Slice 4 — qrspi-plan`). Slice 4 was originally built in a prior session that did not
> emit a log; the deliverables themselves are unchanged.

## What this slice is (per plan §6, Slice 4, re-read in full)

> - Write SKILL.md (+ plan-template), extend orchestrator `skills:`. Implements the
>   horizontal-layer refusal gate (§4.3), sets `status: ready-for-review`.
> - Checkpoint: `/qrspi-plan` consumes `spec.md`, produces a vertically-sliced `plan.md` and
>   refuses a horizontal plan. Q→R→S→P works.

## What was done

### 1. `qrspi-plan` skill (minimal tier)
- `skills/team/qrspi-plan/SKILL.md` — **97 lines**, ≤ ~40 directives, self-sufficient when invoked
  directly. Frontmatter matches the `qrspi-*` shape (`name`, `audience: team`, `description: >` with
  `/qrspi-plan` usage + natural triggers + negatives for the deprecated `rpi-plan` and planning
  without a spec — plan §5 disambiguation).
- **Vertical-not-horizontal refusal gate (plan §4.3)** as the `RE-SLICE GATE` workflow step +
  constraint 2 ("VERTICAL OR REFUSE"): if any phase completes a whole horizontal layer (all models,
  then all services, then all UI), STOP and re-slice before WRITE. Mirrors `rpi-plan`'s YAGNI gate
  that blocks WRITE.
- **Spec-gated** (constraint 1 + PRE-FLIGHT): refuses to plan without `spec.md` `status: approved`
  AND `design_approved: true`; a `ready-for-review` spec STOPs and asks for design approval.
- **Mechanical-execution** discipline: exact file paths, a RED test step before the GREEN code step,
  an automated verification command, and a rollback line per phase; sets `plan.md` `status:
  ready-for-review`.
- 40/60 context-budget rule + `context_budget` state field (plan §4.5).
- Unique state tag `<qrspi-plan-state>` (appears only in this file).

### 2. ONE reference file (minimal-tier rule)
- `references/plan-template.md` — the full `plan.md` structure + frontmatter (incl. `status:
  ready-for-review → approved` lifecycle), the per-phase shape (exact paths, RED/GREEN steps,
  verification command, rollback), and the worked horizontal-vs-vertical example showing the WRONG
  (refuse) and RIGHT (accept) phase decompositions.

### 3. Extended `qrspi-orchestrator` (both platforms, parity preserved)
- Claude: added `qrspi-plan` to the `skills:` array; OpenCode: added the `skill({ name: "qrspi-plan"
  })` row to the Available Skills table (OpenCode has no `skills:` frontmatter).
- Both: added a **PLAN Phase** to the Autonomous Protocol (spec-approved gate → RE-SLICE GATE →
  WRITE with exact paths/RED-before-GREEN/verification/rollback → report); added a "Before writing
  plan.md" self-check; added a PLAN Completion Criterion; added `PLAN` to the phase/Mode enums.
  (Same in-place extension pattern Slice 3 used for SPEC.)

### 4. Command pair (flat, paired)
- `claude/commands/qrspi-plan.md` — `!`-injected `<live_state>` (today + `ls` of feature folders and
  their artifacts), routes to `qrspi-orchestrator`, encodes the spec-approval and RE-SLICE gates.
- `opencode/commands/qrspi-plan.md` — `agent: qrspi-orchestrator`, `subtask: true` (read-heavy
  alignment phase; same classification as questions/research/spec, plan §3).

## Verification (all green at slice close)

| Check | Result |
| --- | --- |
| skills count | 84 → **85** (+qrspi-plan) |
| claude agents | **36** (no new agent — qrspi-plan runs under the orchestrator) |
| opencode agents | **36** |
| agent parity | 36 == 36 ✅ |
| claude commands | 13 → **14** |
| opencode commands | 13 → **14** |
| command parity | 14 == 14 ✅ |
| minimal-tier lines | qrspi-plan 97 (≤100) ✅ |
| ≥1 reference | plan-template.md ✅ |
| frontmatter `name:` == dir | `qrspi-plan` ✅ |
| unique state tag | `<qrspi-plan-state>` appears only in its own skill ✅ |
| orchestrator PLAN wiring | PLAN Phase + self-check + completion criterion present on both platforms ✅ |

## Eval status (TDD / eval discipline)

No executable trigger-eval harness exists in-repo yet (plan §5 defers eval authoring). Eval spec
recorded as a checklist for a later eval-harness session.

### `qrspi-plan` trigger evals (plan §5)
- [ ] MUST activate: "/qrspi-plan X", "qrspi plan X", "turn the spec into an implementation plan"
- [ ] MUST NOT activate: "/rpi-plan X" (→ deprecated `rpi-plan`), "plan the changes" with no QRSPI
      context (→ generic / `rpi-plan`)
- [ ] Disambiguation: highest collision risk is `rpi-plan` — route here for QRSPI's spec-gated,
      refuses-horizontal plan

### Behavior evals (the spec + re-slice gates)
- [ ] Plan requested with no `spec.md` → STOPS and routes to `/qrspi-spec`
- [ ] `spec.md` only `ready-for-review` (not `approved`) → STOPS and asks for design approval
- [ ] A horizontal-layer phase decomposition → re-sliced before `status: ready-for-review`
- [ ] Every written phase has an exact file path, a RED-before-GREEN step, and a verification command

## Deliberate plan-driven choices worth noting at review

1. **No new agent.** `qrspi-plan` runs under the existing `qrspi-orchestrator` (extended in place,
   per the Slice 3 handoff), so agent counts stay 36/36 at slice close. The Implement agent
   (`qrspi-implement`) is the only new agent the suite adds — in Slice 5.
2. **OpenCode `subtask: true` for plan** — consistent with the Slice 2/3 decision that classifies all
   four alignment phases as read-heavy; only `implement` is `subtask: false`.
3. **Planning artifacts left untracked** — `thoughts/qrspi-plan.md` / `qrspi-research.md` remain
   unstaged (meta-artifacts, not slice deliverables), consistent with Slices 2–3.

## Handoff to Slice 5 (`qrspi-implement`)

**What was done:** `qrspi-plan` skill (+ plan-template); orchestrator extended for PLAN on both
platforms; `qrspi-plan` command pair. Counts at slice close: 85 / 36 / 36 / 14 / 14.

**What tests pass:** all structural/parity/minimal-tier checks above; orchestrator PLAN wiring on
both platforms. Trigger/behavior evals written as checklists (no harness).

**What's deferred:** README/AGENTS.md/docs bookkeeping and the RPI DEPRECATED markers → **Slice 6**
(do not interleave). Build-end totals after Slice 5 reconcile to 86 / 37 / 37 / 15 / 15.

**What Slice 5 needs to know:**
1. **Implement is a NEW, separate agent** (`qrspi-implement`, edit access) — NOT an orchestrator
   skill. The orchestrator is read-only (`edit: false`) and cannot run Implement. Agent counts move
   36 → 37 in Slice 5.
2. **`qrspi-implement` is minimal tier** (≤100 lines, ≥1 reference: `slice-log-template.md`);
   `skills: [qrspi-implement, tdd]`.
3. **RGR-per-slice gate (plan §4.4):** RED (test fails) → GREEN (build+test pass) → REFACTOR; record
   RED + GREEN output to `implementation/slice-NN-{name}.md`. Production-code-before-failing-test = STOP.
4. **approved-status guard:** consumes `plan.md`, refuses without `status: approved`.
5. **40/60 per-slice context budget** (plan §4.5) — stricter than `rpi-implement`'s 70%.
6. **Orchestrator touch is minimal in Slice 5** — flip the "Implement comes online later" note and
   complete the SEQUENCE CHECK (PLAN live + add IMPLEMENT row). Do NOT add `qrspi-implement` to the
   orchestrator `skills:` array.

**Branch:** `qrspi-slice-3-spec` (committed as `a9ac8d3`; Slice 4 was built directly on this branch
without a per-slice branch).
