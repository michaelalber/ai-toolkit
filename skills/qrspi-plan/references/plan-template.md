# `plan.md` Template

The Plan phase writes this to the feature folder
`thoughts/shared/qrspi/YYYY-MM-DD-{feature-slug}/plan.md`. It converts the approved `spec.md`
(Design Brain-Dump + Structure Outline) into a mechanically executable plan. The phases come
**from the spec's vertical slices** -- the Plan phase makes each one exact, never re-designs it.

```markdown
---
date: YYYY-MM-DDTHH:MM:SS
repository: [repo name]
topic: "[feature, one line]"
tags: [qrspi, plan, relevant-tag]
git_commit: [short hash]
phase: Plan (P)
qrspi_feature: [feature-slug]
spec_artifact: thoughts/shared/qrspi/YYYY-MM-DD-{slug}/spec.md
status: ready-for-review        # draft -> ready-for-review -> approved (human gate before /qrspi-implement)
---

# Plan: [feature]

## Overview
[2-3 sentences: what this plan delivers and how it maps to the spec's slices.]

## Current state  (from spec.md / research.md)
[What exists today, with file:line citations carried from the spec.]

## Desired end state
[Observable behavior once every phase is complete.]

## What we're NOT doing
- [Explicit scope boundary — prevents drift during implementation.]
- [Adjacent improvement deliberately deferred.]

## Implementation approach
[Why the phases are ordered this way; dependencies between slices.]

---

## Phase 1 — [vertical slice name]  (mock API / contract)
**Goal:** [the end-to-end increment this phase delivers — testable on its own.]

**Changes:**
- `path/to/file.ext` — [REMOVE/ADD change description, no full implementation]

**Step 1 (RED):** Write failing test
- `path/to/test_file.ext` — add `[test name]` asserting [behavior]
- Verify: `[test command]` → FAIL expected

**Step 2 (GREEN):** Implement to pass
- `path/to/file.ext` — [change description]
- Verify: `[test command]` → PASS required

**Success criteria:** `[build/test/lint command]` passes; [manual check if any].
**Rollback:** `git restore path/to/file.ext` / [migration downgrade / flag toggle].

## Phase 2 — [vertical slice name]  (front-end against the contract)
[Same shape: changes · RED step · GREEN step · success criteria · rollback.]

## Phase 3 — [vertical slice name]  (real persistence / integration)
[Same shape.]

---

## Testing strategy
[Unit / integration / e2e split; what each phase's verification proves.]

## Rollback plan
[How to revert the whole feature: phase-by-phase git restore, migration downgrades, flags.]

## Notes
[Sequencing notes, follow-ups, anything the implementer needs but that isn't a phase.]
```

## Authoring rules
- **Spec-grounded:** phases come from the spec's vertical slices; do not invent new design here.
- **Exact paths, not directions:** every change names a file path. "Update the service layer" is
  wrong; "Add `recipient` to `send()` in `src/notify/service.py:34`" is right.
- **Tests first:** any phase adding behavior opens with a RED test step before the GREEN code step.
- **Every phase verifiable:** each phase carries an automated command and a rollback line.
- **No source code:** REMOVE/ADD change descriptions and illustrative snippets only — never a full
  method body. The plan describes the change; the Implement phase writes the code.
- **Lifecycle:** `ready-for-review` (written) -> `approved` (the human's gate before
  `/qrspi-implement` consumes it).

## The vertical-not-horizontal gate (worked example)

A horizontal plan completes whole layers in sequence and is REJECTED:

```
WRONG (horizontal — refuse and re-slice):
  Phase 1: all data models      Phase 2: all services      Phase 3: all UI
  → nothing is end-to-end testable until Phase 3; a wrong assumption surfaces last.
```

A vertical plan slices end-to-end and is ACCEPTED:

```
RIGHT (vertical — each phase ships a testable increment):
  Phase 1: mock-API contract for feature X (request → stubbed response, test passes)
  Phase 2: front-end calls the contract (observable behavior, test passes)
  Phase 3: real persistence behind the same contract (integration test passes)
  → each phase is a checkpoint and maps to one fresh implementation session.
```

If the intended phases look like the WRONG block, STOP at the RE-SLICE GATE and rebuild them as
the RIGHT block before writing `plan.md`.
