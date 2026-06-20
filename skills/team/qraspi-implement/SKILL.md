---
name: qraspi-implement
audience: team
description: >
  QRASPI Implement phase — grows the green walking skeleton ONE approved slice at a time with
  strict Red-Green-Refactor per phase, keeping fitness gates green, and writes a per-slice proof
  log. Use for '/qraspi-implement <project>', 'implement the slice on the skeleton', 'build the
  approved plan-{slice} with RGR'. Requires plan-{slice}.md status: approved and a green
  skeleton. Not for a feature in an EXISTING codebase (qrspi-implement), the deprecated RPI
  workflow, or a bare TDD cycle with no plan (tdd).
---

# QRASPI Implement

> "Amateurs practice until they get it right. Professionals practice until they can't get it wrong."

## Core Philosophy

The Implement phase grows the walking skeleton **one approved slice at a time**. Architecture locked
the decisions, Plan made the slice mechanical -- you execute `plan-{slice}.md` without re-opening
either. Each phase inside the slice plan runs a full **Red-Green-Refactor** loop: a failing test
first, minimal code to pass, then refactor -- with the RED and GREEN command output captured to the
slice's log. The skeleton's **fitness gates are live**, so GREEN means the tests pass *and* the gates
stay green; a change that trips a gate is not done. One slice is ideally one fresh session -- the
per-slice log is the resumption point, so context never spans the whole system. You stop the instant
the plan does not cover something.

**Non-Negotiable Constraints:**
1. APPROVED-GATED -- never start without `plan-{slice}.md` status: approved; never implement from memory
2. SKELETON GREEN FIRST -- pre-flight requires `skeleton.md` `ci_green: true` AND a green baseline run
   (tests + the skeleton's fitness gates); a red baseline is a STOP, not yours to fix
3. ONE SLICE, PHASES IN ORDER -- execute the phases inside `plan-{slice}.md` in order; never reorder,
   parallelize, or skip; other backlog slices are out of scope for this run
4. TEST FIRST OR STOP -- production code written before a failing test is a STOP condition
5. RGR PER PHASE -- RED (test fails) -> GREEN (minimal code, build+test+fitness gates pass) -> REFACTOR (stays green)
6. GATES STAY GREEN -- a change that trips a fitness gate is NOT green; fix the change, never disable the gate
7. RECORD THE PROOF -- write RED and GREEN command output to `implementation-log-{slice}.md`
8. INVENTION = STOP -- anything not in the plan stops the slice (re-run /qraspi-plan); a design change
   routes to /qraspi-architecture. Never improvise.
9. CONTEXT BUDGET: keep utilization under 40%. At 60% (or end of the slice), checkpoint to the slice
   log and tell the user to start a fresh session.

## Workflow

```
PRE-FLIGHT
    [ ] Locate the project folder thoughts/shared/qraspi/YYYY-MM-DD-{slug}/
    [ ] Read skeleton.md: status: complete AND ci_green: true. If not green -> STOP; route to /qraspi-skeleton
    [ ] Read plan-{slice}.md for the target slice. If absent -> STOP; route the user to /qraspi-plan
    [ ] Confirm plan-{slice}.md status: approved. If only ready-for-review -> STOP; ask the human to approve
    [ ] Run the baseline suite (tests + the skeleton's fitness gates). If red -> STOP; report; do not fix it
    [ ] Read the ENTIRE plan-{slice}.md; identify the next unfinished phase from implementation-log-{slice}.md

PHASE LOOP  (one phase = one vertical increment inside the slice; inner loop delegated to tdd)
    1. RED   — write the phase's failing test; RUN it; it MUST FAIL.
               If it passes, the test is wrong -> fix the test, not the code.
    2. GREEN — write the minimal production code; RUN build + tests + the skeleton's fitness gates;
               ALL MUST PASS.
    3. REFACTOR — clean up; RUN again; it MUST stay GREEN (tests AND gates).
    4. RECORD — append to implementation-log-{slice}.md: RED output, GREEN output, the gate result, files changed.
    5. CHECKPOINT — suggest a commit; if context > 40% or the slice is done, hand off a fresh session.

REPORT
    Phases complete / total for this slice · fitness gates green · last verification · the next backlog
    slice (run /qraspi-plan for it) or "all backlog slices built -> /qraspi-graduate".
```

**Exit criteria:** every phase in `plan-{slice}.md` executed in order with RED + GREEN proof in
`implementation-log-{slice}.md`; build/tests AND the skeleton's fitness gates are GREEN; a per-slice
commit suggested; the user knows the next backlog slice or that the system is ready to graduate.

## State Block

```
<qraspi-implement-state>
phase: PRE-FLIGHT | RED | GREEN | REFACTOR | RECORD | CHECKPOINT | COMPLETE
project_folder: thoughts/shared/qraspi/YYYY-MM-DD-{slug}/
skeleton_ci_green: true | false      # MUST be true to proceed
plan_present: true | false           # plan-{slice}.md -- MUST be true to proceed
plan_approved: true | false          # MUST be true to proceed
baseline_green: true | false         # tests + fitness gates -- MUST be true before any change
slice_name: [the slice being built]
current_phase: [NN]
phases_total: [count]
phases_complete: [count]
fitness_gates_green: true | false    # MUST stay true -- it is part of GREEN
last_verification: red | green | pending   # RED step expects red; GREEN/REFACTOR expect green
context_budget: under-40 | approaching-60 | checkpoint-now
</qraspi-implement-state>
```

## Output Template

See `references/implementation-log-template.md` for the per-slice `implementation-log-{slice}.md`
structure -- the per-phase RED proof, GREEN proof, the fitness-gate result, the files-changed list,
and the resume note.

## Integration with Other Skills

| Skill | Relationship |
|-------|-------------|
| `qraspi-plan` | Prior phase. Its approved `plan-{slice}.md` is the contract this phase executes; refuses to run without `status: approved`. |
| `qraspi-skeleton` | Supplies the green skeleton this phase grows on and the live fitness gates GREEN must keep passing. |
| `tdd` | The inner loop. Each phase IS a RED-GREEN-REFACTOR cycle; load `tdd` for the test-first mechanics this skill enforces per phase. |
| `qraspi-graduate` | Terminal next step once every backlog slice is built -- hands the repo to QRSPI for ongoing features. |
| `dotnet-vertical-slice` / `python-feature-slice` / `rust-feature-slice` | Stack scaffolders for the slice's phases. |
| `qrspi-implement` | Brownfield sibling. Same per-slice RGR discipline; QRASPI grows a fresh green skeleton slice-by-slice and keeps fitness gates green, instead of executing a multi-slice `plan.md` over an existing codebase. |
