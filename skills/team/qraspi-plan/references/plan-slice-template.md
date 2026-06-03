# `plan-{slice}.md` Template

The Plan phase writes one of these per backlog slice to the project folder
`thoughts/shared/qraspi/YYYY-MM-DD-{slug}/plan-{slice}.md`. It converts **one slice from the
skeleton's backlog** (`skeleton.md`) into a mechanically executable plan. Greenfield grows
slice-by-slice on the green walking skeleton, so Plan runs **once per slice** -- default: the next
unbuilt backlog item. The phases inside the plan come from decomposing that one slice end-to-end;
Plan makes each phase exact, it never re-designs the architecture.

```markdown
---
date: YYYY-MM-DDTHH:MM:SS
repository: [repo name]
topic: "[the backlog slice, one line]"
tags: [qraspi, plan, relevant-tag]
git_commit: [short hash]
phase: Plan (P)
qraspi_project: [project-slug]
slice: [slice-slug]
skeleton_artifact: thoughts/shared/qraspi/YYYY-MM-DD-{slug}/skeleton.md
status: ready-for-review        # draft -> ready-for-review -> approved (human gate before /qraspi-implement)
---

# Plan: [slice] (on the [project] walking skeleton)

## Overview
[2-3 sentences: the increment this slice delivers and how it extends the skeleton.]

## Skeleton baseline  (from skeleton.md)
[What the walking skeleton already exercises end-to-end; the layers this slice touches.]
[The live fitness gates this slice's verification must keep green (name them + their ADR ids).]

## Desired end state
[Observable behavior once every phase of this slice is complete.]

## What we're NOT doing
- [Explicit scope boundary — other backlog slices are out of scope for this plan.]
- [Adjacent improvement deliberately deferred.]

## Implementation approach
[Why the phases are ordered this way; how the slice threads every layer the ADRs name.]

---

## Phase 1 — [sub-step name]  (contract / thinnest end-to-end thread)
**Goal:** [the end-to-end increment this phase delivers — testable on its own.]

**Changes:**
- `path/to/file.ext` — [REMOVE/ADD change description, no full implementation]

**Step 1 (RED):** Write failing test
- `path/to/test_file.ext` — add `[test name]` asserting [behavior]
- Verify: `[test command]` → FAIL expected

**Step 2 (GREEN):** Implement to pass
- `path/to/file.ext` — [change description]
- Verify: `[test command]` → PASS required

**Success criteria:** `[build/test command]` passes AND the skeleton's fitness gates stay green
  (`[fitness gate command]`); [manual check if any].
**Rollback:** `git restore path/to/file.ext` / [migration downgrade / flag toggle].

## Phase 2 — [sub-step name]
[Same shape: changes · RED step · GREEN step · success criteria (incl. fitness gates) · rollback.]

---

## Testing strategy
[Unit / integration / e2e split; what each phase's verification proves; which fitness gates apply.]

## Rollback plan
[How to revert the whole slice: phase-by-phase git restore, migration downgrades, flags.]

## Notes
[Sequencing notes, follow-ups, the remaining backlog items this plan does NOT cover.]
```

## Authoring rules
- **Skeleton-grounded:** the slice comes from `skeleton.md`'s backlog; do not invent new scope or
  re-open the ADRs here. A design change routes back to `/qraspi-architecture`.
- **One slice per file:** `plan-{slice}.md` covers exactly one backlog item. The next backlog item is
  a separate `/qraspi-plan` run and a separate file.
- **Exact paths, not directions:** every change names a file path. "Update the service layer" is
  wrong; "Add `recipient` to `send()` in `src/notify/service.py:34`" is right.
- **Tests first:** any phase adding behavior opens with a RED test step before the GREEN code step.
- **Fitness gates are part of "done":** every phase's success criteria include keeping the skeleton's
  fitness gates green -- a plan that would trip a gate is invalid, not merely risky.
- **No source code:** REMOVE/ADD change descriptions and illustrative snippets only -- never a full
  method body. The plan describes the change; the Implement phase writes the code.
- **Lifecycle:** `ready-for-review` (written) -> `approved` (the human's gate before
  `/qraspi-implement` consumes it).

## The vertical-not-horizontal gate (worked example)

A horizontal plan completes whole layers in sequence and is REJECTED:

```
WRONG (horizontal — refuse and re-slice):
  Phase 1: all data models      Phase 2: all services      Phase 3: all UI
  → nothing is end-to-end testable until Phase 3; a wrong assumption surfaces last.
```

A vertical plan slices end-to-end and is ACCEPTED:

```
RIGHT (vertical — each phase ships a testable increment through every layer):
  Phase 1: thinnest contract for the slice (request → stubbed response, test + gates pass)
  Phase 2: real behavior behind the contract (observable, test + gates pass)
  Phase 3: persistence / integration behind the same contract (integration test + gates pass)
  → each phase is a checkpoint and maps to one fresh implementation session.
```

If the intended phases look like the WRONG block, STOP at the RE-SLICE GATE and rebuild them as the
RIGHT block before writing `plan-{slice}.md`.
