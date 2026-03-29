---
name: rpi-implement
description: >
  RPI Implement phase -- executes a phased implementation plan mechanically with verification
  after each phase and checkpoint-based context management. Use for "/rpi-implement path/to/plan.md",
  "execute the plan", "implement the changes from the plan", "run the implementation".
---

# RPI Implement

> "The plan is the spec. If the plan is right, implementation is mechanical. If you're inventing, you're planning, not implementing."

> "A good plan executed today is better than a perfect plan executed at some indefinite point in the future."
> -- George S. Patton

## Core Philosophy

The Implement phase is deliberately mechanical. The research and planning phases exist so that the implementer never has to think creatively. Every file to change, every change to make, every verification to run -- it is all in the plan. The implementer's job is to execute the plan faithfully and stop when something doesn't work.

This is not a limitation -- it is the goal. Mechanical execution is fast, predictable, and recoverable. Creative implementation is slow, unpredictable, and prone to scope drift.

**Non-Negotiable Constraints:**
1. Read the ENTIRE plan before making any changes -- understand all phases and their dependencies
2. Execute phases IN ORDER -- never reorder, skip, or parallelize phases
3. Run verification steps after EVERY phase -- a failed verification stops everything
4. Update checkboxes in the plan file after completing each item -- this is the resumption protocol
5. If something is not in the plan, STOP and tell the user -- do not invent solutions
6. Write progress notes before context fills -- proactive checkpoint management
7. The plan is the spec -- if the plan is wrong, fix the plan (via /rpi-iterate), not the implementation

## Domain Principles Table

| # | Principle | Description | Applied As |
|---|-----------|-------------|------------|
| 1 | **Read Before Acting** | An implementer who starts executing before reading the full plan may complete Phase 1 correctly but set up Phase 2 to fail. Dependencies are only visible from the full plan view. | Read the entire plan -- all phases, success criteria, and notes -- before making any file edits. |
| 2 | **Sequential Phase Execution** | Phases have dependencies. Executing Phase 3 before Phase 2 may produce code that conflicts with Phase 2's changes or depends on types Phase 2 has not yet created. | Announce each phase, complete it fully, verify it, then move to the next. Never jump ahead. |
| 3 | **Verify Before Proceeding** | A passing build at the end of Phase 1 confirms Phase 2 starts from a known-good state. A failing build at Phase 1 means Phase 2's changes may compound the failure. | Run the verification commands listed in each phase's Success Criteria section. Report failures immediately; do not continue. |
| 4 | **Checkboxes Are the Contract** | The plan file's checkboxes are the source of truth for implementation progress. When context resets and the implementer re-runs the command, checked boxes tell it where to resume. Unchecked boxes may be re-executed. | Update every checkbox in the plan file as soon as that item is confirmed complete. Never batch checkbox updates. |
| 5 | **Invention = Stop Signal** | If the implementer finds itself needing to create a type, choose between two approaches, or add a file not mentioned in the plan, the plan is incomplete. Continuing means diverging from the reviewed and approved plan. | When you would invent something not in the plan, STOP. Report: "The plan does not cover [X]. Please update the plan via /rpi-iterate or clarify." |
| 6 | **Context Management Is Proactive** | Waiting until context is full before writing a progress note means losing track of current state. Writing the note when context is 70-80% full ensures a clean handoff. | Check context usage before each phase. If more than 70% full, write a progress note and tell the user to restart with the same plan path. |
| 7 | **Failures Are Findings** | A build failure during implementation is new information -- either the plan was wrong, or the codebase has changed since research. Either way, it should surface to the human rather than be silently worked around. | When verification fails, show the error, analyze the root cause, and report it. Fix simple in-scope issues; escalate out-of-scope issues to /rpi-iterate. |
| 8 | **Commit-Ready Phases** | Each phase should produce a commit-ready increment. This keeps the git history clean, makes rollback easy, and provides natural checkpoints for code review. | After each phase verification passes, note in the progress summary that this phase is commit-ready. |
| 9 | **The Rollback Plan Is Real** | The plan includes a rollback section. If implementation goes badly wrong, the rollback procedure should work. The implementer must understand it -- not just execute forward. | Read the rollback plan during the initial full-read step. Know how to undo before you start doing. |
| 10 | **Progress Notes Enable Resumption** | An implementation that fills the context window halfway through and dies without a progress note forces the user to re-examine the codebase manually. A progress note makes resumption instant. | Before context fills, write to `thoughts/shared/progress/YYYY-MM-DD-[plan-slug].md` with: phases complete, current state, issues, what remains. |

## Workflow

```
READ
    Read the entire plan file completely.
    Note: which phases exist, their order, their dependencies, the rollback plan.
    Note: which phases already have checked boxes (resuming from previous session).

        |
        v

RESUME CHECK
    Are any phases already checked (prior session)?
    → YES: Start from the first unchecked phase; announce "Resuming from Phase N"
    → NO: Start from Phase 1

        |
        v

PHASE LOOP (for each unchecked phase):

    ANNOUNCE
        "Starting Phase N: [title]"

    EXECUTE
        Make all changes described in the phase
        Follow exact file paths and change descriptions from the plan
        If anything is ambiguous or missing: STOP and report to user

    VERIFY
        Run all automated verification commands from the phase's Success Criteria
        Show command output
        → PASS: Continue to checkbox update
        → FAIL: Show error, analyze root cause, attempt fix only if within plan scope
                 If fix requires plan changes: STOP and tell user to run /rpi-iterate

    UPDATE CHECKBOXES
        Update all checked items in the plan file: `- [ ]` → `- [x]`

    MANUAL VERIFICATION (if required)
        Ask user to perform any manual verification steps
        Wait for confirmation before proceeding

    ANNOUNCE COMPLETION
        "Phase N complete. Moving to Phase N+1."

        |
        v

CONTEXT CHECK (before each phase)
    Context > 70% full?
    → YES: Write progress note, tell user to restart with same plan path
    → NO: Continue to next phase

        |
        v

FINAL REPORT
    Confirm all checkboxes are checked
    Run the final verification suite from the last phase
    Write brief summary to thoughts/shared/progress/YYYY-MM-DD-[plan-slug]-complete.md
    Report: files modified/added/deleted, phases completed, final verification status
```

**Exit criteria:** All phases verified and checkboxes checked; final report delivered.

## State Block

```
<rpi-implement-state>
phase: READ | EXECUTE | VERIFY | CHECKPOINT | COMPLETE
plan_path: thoughts/shared/plans/YYYY-MM-DD-description-slug.md
current_phase_number: [N]
current_phase_title: [title]
phases_total: [count]
phases_complete: [count]
last_verification: pass | fail | pending
context_usage: low | medium | high
progress_note_written: true | false
blockers: none | [description]
</rpi-implement-state>
```

## Output Templates

### Phase Announcement

```
Starting Phase N: [Phase Title]

Changes to make:
1. [File path] — [brief description of change]
2. [File path] — [brief description of change]

Running verification after completion.
```

### Verification Report (Pass)

```
Phase N verification:
✓ dotnet build --no-restore — 0 errors, 0 warnings
✓ dotnet test --filter "Feature=X" — 12 passed
✓ dotnet format --verify-no-changes — clean

Checkboxes updated. Phase N complete.
```

### Verification Report (Fail)

```
Phase N verification FAILED:

Command: dotnet test --filter "Feature=X"
Output:
  [error output here]

Root cause analysis:
[Analysis of what went wrong]

This failure is:
□ Within plan scope — attempting fix
■ Outside plan scope — stopping

[If outside scope]: Please update the plan via /rpi-iterate with this feedback:
"[Description of what needs to change in the plan]"
```

### Progress Note (Context Management)

```markdown
# Implementation Progress: [Plan Title]

**Plan**: thoughts/shared/plans/YYYY-MM-DD-description-slug.md
**Date**: YYYY-MM-DD
**Session ended**: context window limit approaching

## Phases complete
- [x] Phase 1: [title] — verified
- [x] Phase 2: [title] — verified

## Phases remaining
- [ ] Phase 3: [title]
- [ ] Phase 4: [title]

## Current codebase state
[Brief description of what has been changed so far]

## Issues encountered
[Any deviations from the plan, workarounds applied]

## Resume instruction
Start a new session and run: /rpi-implement thoughts/shared/plans/YYYY-MM-DD-description-slug.md
The checked boxes will indicate where to resume.
```

### Final Report

```
Implementation complete.

Plan: thoughts/shared/plans/YYYY-MM-DD-description-slug.md
All N phases verified.

Changes made:
- Modified: [list of modified files]
- Added: [list of new files]
- Deleted: [list of deleted files]

Final verification:
✓ [build command]
✓ [test command]
✓ [lint command]

Progress note: thoughts/shared/progress/YYYY-MM-DD-plan-slug-complete.md
```

## AI Discipline Rules

### CRITICAL: Stop When Inventing

**WRONG:**
```
The plan says to add a `SendAsync` method. The existing interface doesn't have one,
so I'll also add `IEmailSender` to the codebase to support it.
```

**RIGHT:**
```
The plan describes adding `SendAsync` to the email handler, but I cannot find
`IEmailSender` in the codebase. The research artifact referenced it but it
may not exist yet, or may use a different name.

Stopping here. Please update the plan via /rpi-iterate with:
"The IEmailSender interface needs to be created first, or the plan needs to
reference the actual interface name."
```

### REQUIRED: Update Checkboxes Immediately

**WRONG:** Complete 3 items in a phase, then update all three checkboxes at the end.

**RIGHT:** Complete item 1, update its checkbox, complete item 2, update its checkbox. Checkboxes are updated as each item completes, not as a batch.

### CRITICAL: Verification Failures Stop Execution

**WRONG:**
```
Phase 2 verification failed with 2 test errors. These look like pre-existing failures
unrelated to my changes. Proceeding to Phase 3.
```

**RIGHT:**
```
Phase 2 verification failed with 2 test errors.
[Show error output]

I cannot determine if these failures are pre-existing or caused by my Phase 2 changes.
Stopping here. Please investigate and let me know how to proceed.
```

## Anti-Patterns Table

| # | Anti-Pattern | Why It Fails | Correct Approach |
|---|-------------|-------------|-----------------|
| 1 | **Starting without reading full plan** | Phase dependencies are invisible; Phase 1 may create a conflict with Phase 3 | Read all phases, notes, and rollback plan before making any changes |
| 2 | **Skipping verification steps** | Failures accumulate silently across phases; debugging becomes a multi-phase archaeology project | Run every verification command in every phase's success criteria |
| 3 | **Continuing after verification failure** | Subsequent phases may compound the failure; rollback becomes harder | Stop immediately on failure; show error; report to user |
| 4 | **Inventing what's not in the plan** | Diverges from the reviewed spec; introduces unreviewed logic | Stop and report: "The plan doesn't cover X" -- use /rpi-iterate to update |
| 5 | **Batching checkbox updates** | A context reset between batch and update leaves an inaccurate progress state | Update each checkbox as the item completes, not as a group |
| 6 | **Waiting until context is full** | No time to write a proper progress note; resumption is manual | Write progress note when context is 70-80% full; proactive, not reactive |
| 7 | **Fixing test failures without stopping** | The fix may be wrong or may compensate for an actual plan gap | Show the failure to the user; fix only if clearly within plan scope |
| 8 | **Reordering phases "for efficiency"** | Phase ordering in the plan reflects dependencies; reordering breaks them | Execute phases exactly as numbered |
| 9 | **Not writing final report** | User has no summary of what changed; makes PR description and rollback harder | Always write final report with files changed and verification status |
| 10 | **Treating progress notes as optional** | Without notes, a context reset means the user manually re-determines completion state | Progress notes are mandatory before context resets and at completion |

## Error Recovery

### Verification failure: build error

```
Symptoms: `dotnet build` (or equivalent) fails during phase verification

Recovery:
1. Show the full build error output
2. Identify the error location (file:line)
3. Check if it is caused by the current phase's changes
4. If YES and fix is described in the plan: apply it and re-verify
5. If YES and fix requires plan changes: STOP. Tell user to run /rpi-iterate
6. If NO (pre-existing or unrelated): document it and ask user how to proceed
7. NEVER assume a build failure is pre-existing without checking
```

### Verification failure: test failure

```
Symptoms: Test suite fails during phase verification

Recovery:
1. Show which tests failed and the error messages
2. Determine if the tests are testing the current phase's functionality
3. If YES and it is a gap in the plan: STOP. Tell user to use /rpi-iterate
4. If the tests appear to test unrelated functionality: report to user; do not continue
5. NEVER silently skip failing tests or mark them as "expected"
```

### Context window nearly full mid-implementation

```
Symptoms: Multiple phases complete but context usage > 70%

Recovery:
1. Complete the current phase's changes and verification
2. Update all checkboxes for the completed phase
3. Write progress note to thoughts/shared/progress/YYYY-MM-DD-[slug].md
4. Tell user: "Context limit approaching. Progress saved. Please start a new session
   and re-run: /rpi-implement [plan path]
   Checked phases will not be re-executed."
5. Stop after writing the note -- do not attempt more phases
```

## Integration with Other Skills

| Skill | Relationship |
|-------|-------------|
| `rpi-plan` | Produces the plan artifact this skill consumes. The plan must be reviewed before implementation. |
| `rpi-iterate` | Updates the plan when this skill encounters gaps, ambiguities, or out-of-scope issues during execution. |
| `rpi-research` | If implementation reveals something the research missed, the fix path is: stop → rpi-iterate the plan → rpi-implement resumes. |
| `ef-migration-manager` | When phases involve EF Core migrations, load this skill for migration execution safety, dry-run verification, and rollback commands. |
| `tdd-cycle` | If the plan includes writing tests before implementation, use tdd-cycle to manage the RED-GREEN-REFACTOR sequence within each phase. |
| `session-context` | Before resuming an interrupted implementation, load session-context to understand what changed in git since the last session. |
