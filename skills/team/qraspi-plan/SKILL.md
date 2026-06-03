---
name: qraspi-plan
audience: team
description: >
  QRASPI Plan phase -- converts the next slice from the skeleton's backlog into a mechanically
  executable, vertically-sliced plan-{slice}.md with exact file paths and per-phase verification,
  grown on top of the green walking skeleton. Use for "/qraspi-plan <project>", "plan the first
  slice of new X", "plan the next increment on the skeleton". Do NOT use to plan a feature in an
  EXISTING codebase (use qrspi-plan). Do NOT use for the deprecated RPI workflow. This phase consumes
  skeleton.md and REFUSES horizontal-layer plans.
---

# QRASPI Plan

> "A plan precise enough to execute mechanically is the goal. If the implementer has to invent anything, the plan failed."
> -- Adapted from Dwight D. Eisenhower

## Core Philosophy

Greenfield grows **one vertical slice at a time on top of the green walking skeleton**. The Skeleton
phase already stood the architecture up, landed the fitness gates, and enumerated a slice backlog;
Plan takes the **next unbuilt backlog slice** and makes it mechanically executable -- exact file
paths, a test-first step per phase, an automated verification command -- without re-opening the
architecture (the ADRs are locked, the fitness gates are live). Its one hard gate is **vertical, not
horizontal**: a slice plan organized by technical layer (all models, then all services, then all UI)
is rejected before it is written. Each phase must deliver an end-to-end testable increment that the
skeleton's CI -- including its fitness functions -- still passes.

**Non-Negotiable Constraints:**
1. SKELETON-GATED -- never plan without `skeleton.md` (status: complete, `ci_green: true`) on disk;
   never plan from memory. The slice comes from the skeleton's backlog.
2. ONE BACKLOG SLICE -- plan the next unbuilt slice from `skeleton.md`'s backlog (default), producing
   `plan-{slice}.md`; never re-plan a built slice or invent scope the backlog does not name
3. VERTICAL OR REFUSE -- if the slice's phases organize by horizontal layer, STOP and re-slice before writing
4. MECHANICAL EXECUTION -- every change names an exact file path; "the service layer" is not a path
5. TESTS FIRST -- any phase adding behavior opens with a failing-test step (RED) before the code step
6. ARCHITECTURE-RESPECTING -- honor the accepted ADRs and the skeleton's fitness gates; a plan whose
   verification would fail a fitness gate is invalid. Do NOT re-open the ADRs -- that is /qraspi-architecture.
7. NO SOURCE CODE -- change descriptions and illustrative snippets only, never full implementations
8. CONTEXT BUDGET: keep utilization under 40%. At 60%, write `plan-{slice}.md` with progress and tell
   the user to start a fresh session.

## Workflow

```
PRE-FLIGHT
    [ ] Locate the project folder thoughts/shared/qraspi/YYYY-MM-DD-{slug}/
    [ ] Read skeleton.md. If absent -> STOP; route the user to /qraspi-skeleton
    [ ] Confirm skeleton.md status: complete AND ci_green: true.
        If the skeleton is not green -> STOP; it must stand up green before any slice is planned
    [ ] Read the SLICE BACKLOG; pick the next unbuilt slice (default) or the one the user named
    [ ] Skim the accepted docs/adr/ + the fitness gates this slice's verification must keep green

RE-SLICE GATE  (the vertical-not-horizontal refusal)
    Inspect the intended phases for this slice. If any phase completes a whole layer (all models,
    then all services, then all UI), STOP and re-slice so each phase is an end-to-end increment.
    Do NOT proceed to WRITE until every phase is a vertical slice.

WRITE  (only after the gate passes)
    For the chosen backlog slice: exact file paths · REMOVE/ADD change descriptions · a RED test step
    before the code step · an automated verification command (the test suite AND the fitness gates) ·
    a rollback line. Add "What we're NOT doing" (scope boundaries) and a rollback plan.
    Write plan-{slice}.md, status: ready-for-review.

REPORT
    Artifact path · the slice planned · phase list (one line each) · remaining backlog count ·
    "Review/approve, then start a NEW session and run /qraspi-implement"
```

**Exit criteria:** `plan-{slice}.md` holds vertically-sliced phases for ONE backlog slice, each with
exact paths, a test-first step, an automated verification command that keeps the skeleton's fitness
gates green, and a rollback; a "What we're NOT doing" list is present; `status: ready-for-review`;
user told to review/approve before `/qraspi-implement`.

## State Block

```
<qraspi-plan-state>
phase: PRE-FLIGHT | RE-SLICE-GATE | WRITE | REPORT | COMPLETE
project_folder: thoughts/shared/qraspi/YYYY-MM-DD-{slug}/
skeleton_present: true | false        # MUST be true to proceed
skeleton_ci_green: true | false       # MUST be true to proceed
slice_name: [the backlog slice being planned]
slice_from_backlog: true | false      # MUST be true -- no invented scope
phases_planned: [count]
vertical_check: pass | re-slice-needed   # MUST be pass before WRITE
fitness_gates_respected: true | false    # the plan's verification keeps the skeleton's gates green
rollback_documented: true | false
backlog_remaining: [count]
context_budget: under-40 | approaching-60 | checkpoint-now
status: draft | ready-for-review | approved
</qraspi-plan-state>
```

## Output Template

See `references/plan-slice-template.md` for the full `plan-{slice}.md` structure, frontmatter,
per-phase shape (exact paths, RED/GREEN test steps, verification commands incl. the fitness gates,
rollback), and the horizontal-vs-vertical worked example.

## Integration with Other Skills

| Skill | Relationship |
|-------|-------------|
| `qraspi-skeleton` | Prior phase. Its `skeleton.md` slice backlog is the source of the slice this phase plans; its CI fitness gates constrain the plan's verification. |
| `qraspi-implement` | Next phase. Consumes the approved `plan-{slice}.md`; refuses to execute without `status: approved`. |
| `qraspi-architecture` | The accepted ADRs the plan must respect. Plan does NOT re-open them -- a design change routes back to `/qraspi-architecture`. |
| `tdd` | The inner loop the Implement phase runs per phase; Plan's test-first steps map onto RED-GREEN-REFACTOR. |
| `dotnet-vertical-slice` / `python-feature-slice` / `rust-feature-slice` | Stack scaffolders for the vertical slice this phase plans. |
| `qrspi-plan` | Brownfield sibling. Same horizontal-refusal gate; QRASPI plans one backlog slice at a time on a fresh green skeleton, not a single `plan.md` over an existing codebase. |
