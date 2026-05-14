---
name: rpi-implement
description: >
  RPI Implement phase -- executes a phased implementation plan mechanically with verification
  after each phase and checkpoint-based context management. Use when executing an approved implementation plan. Trigger phrases: "/rpi-implement path/to/plan.md",
  "execute the plan", "implement the changes from the plan", "run the implementation".
---

# RPI Implement

> "The plan is the spec. If the plan is right, implementation is mechanical. If you're inventing, you're planning, not implementing."

> "A good plan executed today is better than a perfect plan executed at some indefinite point in the future."
> -- George S. Patton

## Core Philosophy

The Implement phase is deliberately mechanical. The research and planning phases exist so that the implementer never has to think creatively. Every file to change, every change to make, every verification to run -- it is all in the plan. The implementer's job is to execute the plan faithfully and stop when something doesn't work.

**Non-Negotiable Constraints:**
1. The plan MUST have status `approved` before any changes are made -- stop and tell the user if it does not
2. Run the baseline test suite BEFORE any changes -- a failing baseline means you cannot distinguish pre-existing failures from yours
3. Read the ENTIRE plan before making any changes -- understand all phases and their dependencies
4. Execute phases IN ORDER -- never reorder, skip, or parallelize phases
5. Run verification steps after EVERY phase -- a failed verification stops everything
6. Update checkboxes in the plan file after completing each item -- this is the resumption protocol
7. If something is not in the plan, STOP and tell the user -- do not invent solutions
8. Write progress notes before context fills -- proactive checkpoint management
9. The plan is the spec -- if the plan is wrong, fix the plan (via /rpi-iterate), not the implementation
10. ONE commit per phase -- never mega-commit all phases at the end

## Domain Principles Table

| # | Principle | Applied As |
|---|-----------|------------|
| 1 | **Read Before Acting** | Read the entire plan -- all phases, success criteria, and notes -- before making any file edits. Dependencies are only visible from the full plan view. |
| 2 | **Sequential Phase Execution** | Announce each phase, complete it fully, verify it, then move to the next. Never jump ahead. |
| 3 | **Verify Before Proceeding** | Run the verification commands listed in each phase's Success Criteria. Report failures immediately; do not continue. |
| 4 | **Checkboxes Are the Contract** | Update every checkbox as soon as that item is confirmed complete. Never batch checkbox updates. Checked boxes are how a restarted session knows where to resume. |
| 5 | **Invention = Stop Signal** | When you would create something not in the plan, STOP. Report: "The plan does not cover [X]. Please update the plan via /rpi-iterate or clarify." |
| 6 | **Context Management Is Proactive** | Check context usage before each phase. If more than 70% full, write a progress note and tell the user to restart with the same plan path. |
| 7 | **Failures Are Findings** | When verification fails, show the error, analyze the root cause, and report it. Fix simple in-scope issues; escalate out-of-scope issues to /rpi-iterate. |
| 8 | **Commit-Ready Phases** | After each phase verification passes, note that this phase is commit-ready. Keep the git history clean with one commit per phase. |
| 9 | **The Rollback Plan Is Real** | Read the rollback plan during the initial full-read step. Know how to undo before you start doing. |
| 10 | **Progress Notes Enable Resumption** | Write to `thoughts/shared/progress/YYYY-MM-DD-[plan-slug].md` before context fills: phases complete, current state, issues, what remains. |

## Workflow

**PRE-IMPLEMENTATION CHECKS** (before making any changes):
- [ ] Plan status is `approved` — check the plan file's Status field. If not approved, stop and tell the user.
- [ ] Run the baseline test suite. If tests fail before any changes, stop and report — you cannot distinguish your failures from pre-existing ones.

**READ:** Read the entire plan file. Note all phases, their order, dependencies, and the rollback plan. Note which phases already have checked boxes (resuming from previous session).

**RESUME CHECK:** Are any phases already checked? If YES, start from the first unchecked phase and announce "Resuming from Phase N." If NO, start from Phase 1.

**PHASE LOOP** (for each unchecked phase):

1. **ANNOUNCE** — "Starting Phase N: [title]"
2. **EXECUTE** — Make all changes described in the phase, following exact file paths and change descriptions from the plan. If anything is ambiguous or missing: STOP and report to user.
3. **VERIFY** — Run all automated verification commands from the phase's Success Criteria. Show command output. On PASS: continue. On FAIL: show error, analyze root cause, attempt fix only if within plan scope; if fix requires plan changes: STOP and tell user to run /rpi-iterate.
4. **UPDATE CHECKBOXES** — Update all checked items in the plan file: `- [ ]` → `- [x]`
5. **MANUAL VERIFICATION** — If required, ask user to perform manual steps. Wait for confirmation before proceeding.
6. **CONTEXT CHECK** — If context > 70% full, write progress note, tell user to restart with same plan path.
7. **ANNOUNCE COMPLETION** — "Phase N complete. Moving to Phase N+1."

**FINAL REPORT:** Confirm all checkboxes are checked. Run the final verification suite. Write brief summary to `thoughts/shared/progress/YYYY-MM-DD-[plan-slug]-complete.md`. Report files modified/added/deleted, phases completed, verification status.

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

| Template | Required Content |
|----------|-----------------|
| Phase Announcement | "Starting Phase N: [title]" + numbered list of changes to make + "Running verification after completion." |
| Verification Pass | Phase N, ✓ per command with result, "Checkboxes updated. Phase N complete." |
| Verification Fail | "Phase N verification FAILED:", command + output, root cause analysis, in/out-of-scope determination, /rpi-iterate instruction if out of scope |
| Progress Note | Plan path, date, session-ended reason, phases-complete (checked list), phases-remaining (unchecked list), current codebase state, issues encountered, resume instruction |
| Final Report | Plan path, "All N phases verified," files modified/added/deleted, final verification results, progress note path |

Full templates: `references/implementation-templates.md`

## AI Discipline Rules

**Stop When Inventing:** If the plan says to add a method but the required interface does not exist in the codebase, stop immediately. Report: "The plan references [X] but it does not exist. Please update the plan via /rpi-iterate." Do not create things the plan did not describe.

**Update Checkboxes Immediately, Never in Batches:** Complete item 1, update its checkbox. Complete item 2, update its checkbox. Never batch checkbox updates at the end of a phase — a context reset between the batch and the update leaves inaccurate progress state.

**Verification Failures Stop Execution:** If Phase 2 produces test failures that may be pre-existing, do not proceed to Phase 3. Stop, show the failure, report to the user. Never assume a failure is pre-existing without checking. Never mark tests as "expected" to keep moving.

## Anti-Patterns Table

| # | Anti-Pattern | Why It Fails | Correct Approach |
|---|-------------|-------------|-----------------|
| 1 | **Starting without approved plan** | Executing unvalidated decisions | Check plan status field; stop if not `approved` |
| 2 | **Skipping baseline test run** | Cannot distinguish pre-existing failures from new ones | Always run tests before the first change |
| 3 | **Starting without reading full plan** | Phase dependencies are invisible | Read all phases, notes, and rollback plan before any changes |
| 4 | **Skipping verification steps** | Failures accumulate silently across phases | Run every verification command in every phase |
| 5 | **Continuing after verification failure** | Subsequent phases compound the failure | Stop immediately on failure; report to user |
| 6 | **Inventing what's not in the plan** | Diverges from the reviewed spec | Stop and report; use /rpi-iterate to update |
| 7 | **Batching checkbox updates** | A context reset leaves inaccurate progress state | Update each checkbox as the item completes |
| 8 | **Waiting until context is full** | No time to write a proper progress note | Write progress note when context is 70–80% full |
| 9 | **Fixing test failures without stopping** | The fix may compensate for a real plan gap | Show the failure to the user; fix only if clearly within plan scope |
| 10 | **Reordering phases "for efficiency"** | Phase ordering reflects dependencies | Execute phases exactly as numbered |
| 11 | **Not writing final report** | User has no summary of what changed | Always write final report with files changed and verification status |
| 12 | **Mega-commits (all phases in one commit)** | Loses phase-by-phase recovery points | Commit after each phase's verification passes |

## Error Recovery

**Verification failure: build error:** Show the full build error output. Identify the error location (file:line). Check if it is caused by the current phase's changes. If YES and fix is described in the plan: apply it and re-verify. If YES and fix requires plan changes: STOP — tell user to run /rpi-iterate. If NO (pre-existing or unrelated): document it and ask user how to proceed. Never assume a build failure is pre-existing without checking.

**Verification failure: test failure:** Show which tests failed and the error messages. Determine if they test the current phase's functionality. If YES and it is a gap in the plan: STOP — tell user to use /rpi-iterate. If tests appear to test unrelated functionality: report to user; do not continue. Never silently skip failing tests or mark them as "expected."

**Context window nearly full mid-implementation:** Complete the current phase's changes and verification. Update all checkboxes for the completed phase. Write progress note to `thoughts/shared/progress/YYYY-MM-DD-[slug].md`. Tell user: "Context limit approaching. Progress saved. Please start a new session and re-run: /rpi-implement [plan path]. Checked phases will not be re-executed." Stop after writing the note.

## Integration with Other Skills

| Skill | Relationship |
|-------|-------------|
| `rpi-plan` | Produces the plan artifact this skill consumes. The plan must be reviewed before implementation. |
| `rpi-iterate` | Updates the plan when this skill encounters gaps, ambiguities, or out-of-scope issues during execution. |
| `rpi-research` | If implementation reveals something the research missed: stop → rpi-iterate the plan → rpi-implement resumes. |
| `ef-migration-manager` | When phases involve EF Core migrations — migration execution safety, dry-run verification, rollback commands. |
| `tdd-cycle` | If the plan includes writing tests before implementation, use tdd-cycle to manage RED-GREEN-REFACTOR within each phase. |
| `session-context` | Before resuming an interrupted implementation, load session-context to understand what changed in git since the last session. |

## .NET/Blazor Adapter Notes

**EF Core Migrations — always in a dedicated phase:**

```bash
dotnet ef migrations add [MigrationName] --project [DataProject] --startup-project [ApiProject]
dotnet ef migrations script --idempotent   # review before applying
dotnet ef database update --dry-run         # verify connection and SQL
dotnet ef database update                   # apply
```

Never apply a migration in the same phase as the model change that requires it. Rollback: `dotnet ef database update [PreviousMigration]` then `dotnet ef migrations remove`.

**Blazor Component Changes — verify render after each phase:**
- [ ] Component renders without `@rendermode` errors (Server vs. WebAssembly mismatch)
- [ ] No `NullReferenceException` on `OnInitializedAsync` (check `@if (model is null)` guard)
- [ ] `EventCallback` parameters fire correctly (check parent → child wiring)

**Telerik Components — check before and after:**
- [ ] Telerik license referenced in the project (`Telerik.UI.for.Blazor` package present)
- [ ] Telerik CSS/JS included in `_Host.cshtml` or `App.razor`
- [ ] For `TelerikGrid`: verify `Data`, `TItem`, and `OnRead` are consistent with data type changes
- [ ] For `TelerikForm`: verify `Model` type and `FormItems` match updated DTO/command fields

**FreeMediator / CQRS Pipeline:** When adding a new command or query, verify it is handled before wiring up the UI. DI registration for new handlers is automatic with assembly scanning — verify the scan includes the new feature folder.

## Python Adapter Notes

**Alembic Migrations — always in a dedicated phase:**

```bash
alembic revision --autogenerate -m "[MigrationName]"
# STOP: review the generated script in alembic/versions/ before proceeding
alembic check                    # verify no spurious changes were detected
alembic upgrade head             # apply
alembic current                  # confirm new revision is HEAD
```

Never apply a migration in the same phase as the SQLAlchemy model change that requires it. Rollback: `alembic downgrade -1` then delete the revision file from `alembic/versions/` if abandoning the revision.

**FastAPI Routes — verify after each phase:**
- [ ] `uvicorn app.main:app --reload` starts without import errors
- [ ] `curl http://localhost:8000/docs` renders the OpenAPI UI without errors
- [ ] Affected endpoint returns expected status code (not 422 Unprocessable from Pydantic, not 500 from unresolved `Depends()`)
- [ ] No `RuntimeWarning: coroutine was never awaited` in server output

**pytest Quality Checklist — run after every implementation phase:**
- [ ] `pytest tests/ -v` — all pass
- [ ] `pytest tests/ --cov=src --cov-report=term-missing` — coverage ≥ 80% for changed modules
- [ ] `ruff check .` — 0 lint errors
- [ ] `mypy src/` — 0 type errors
- [ ] `pytest --co -q` — confirm new async tests appear in collection (not silently skipped)

**SQLAlchemy / Session Scope — verify per phase:**
- [ ] No `Session` created outside a request context (use `Depends(get_db)` in FastAPI)
- [ ] No `AsyncSession` used in a sync context or vice versa
- [ ] If adding a new model: `Base.metadata.create_all()` is NOT used in production paths — Alembic owns schema management
