# Checkpoint Protocol

How to write progress notes and resume interrupted implementations.

## When to write a checkpoint

Write a progress note when:
- Context usage exceeds ~70% of the context window
- Stopping mid-implementation for any reason (user request, end of session)
- A phase verification fails and implementation is paused for plan review
- The session will end before all phases are complete

**Do not wait until context is full.** Waiting until the last moment leaves no room to write a coherent note.

## Progress note location

```
thoughts/shared/progress/YYYY-MM-DD-[plan-slug].md
```

Derive the slug from the plan file name. Example:
- Plan: `thoughts/shared/plans/2026-03-29-review-notifications.md`
- Progress note: `thoughts/shared/progress/2026-03-29-review-notifications.md`

## Progress note template

```markdown
# Implementation Progress: [Plan Title]

**Plan**: thoughts/shared/plans/YYYY-MM-DD-description.md
**Date**: YYYY-MM-DD HH:MM
**Session ended**: [reason — context limit | user request | verification failure | other]

## Status

**Phases complete** (do not re-execute):
- [x] Phase 1: [title] — verified ✓
- [x] Phase 2: [title] — verified ✓

**Phases remaining**:
- [ ] Phase 3: [title]
- [ ] Phase 4: [title]

**Current phase** (if stopped mid-phase):
- Phase 3 was started; [specific items] completed, [specific items] not yet done.

## Codebase state

[Brief description of what has been changed so far. Enough for the next session to orient itself.]

Example:
- `Features/Review/Handlers/ReviewHandler.cs` — constructor updated to inject IEmailService
- `Features/Review/Handlers/ReviewHandler.cs` — notification dispatch added after save (line 45-52)
- `tests/Unit/Features/Review/ReviewHandlerTests.cs` — 3 new tests added

## Issues encountered

[Any deviations from the plan, workarounds applied, or surprising discoveries.
If empty, write "None."]

## Verification status

- Phase 1: ✓ build pass, ✓ tests pass
- Phase 2: ✓ build pass, ✓ tests pass
- Phase 3: NOT YET VERIFIED (stopped before verification)

## Resume instructions

Start a new session and run:
```
/rpi-implement thoughts/shared/plans/YYYY-MM-DD-description.md
```

The checked boxes in the plan file indicate completed phases. The implement agent will automatically start from the first unchecked phase.

[If stopped mid-phase]: Phase 3 was partially started. The new session should:
1. Review the current state of `[file]` to understand what was already done
2. Complete the remaining items in Phase 3 before running verification
```

## The checkbox-based resumption protocol

The plan file's checkboxes are the authoritative source of progress. The progress note is supplementary context.

When the implement agent starts a new session with a plan that has checked boxes:

1. It reads the full plan to understand all phases
2. It identifies the first unchecked phase
3. It announces: "Resuming from Phase N: [title]. Phases 1-[N-1] are marked complete."
4. It executes from Phase N forward

**Important:** The progress note describes codebase state; the plan checkboxes determine where to resume. Both matter.

## Maintaining checkbox accuracy

Update checkboxes in the plan file as items complete -- not as a batch at the end of a phase.

**Pattern:**
```
1. Complete item ①  →  update checkbox ①  in plan file
2. Complete item ②  →  update checkbox ②  in plan file
3. Run verification  →  all items in phase show ✓ in plan file
4. Announce phase complete
```

**Anti-pattern:**
```
1. Complete items ①②③
2. Batch-update all three checkboxes
```

The anti-pattern fails if context resets between step 1 and step 2.

## Final completion note

After all phases complete, write a brief completion note:

```markdown
# Implementation Complete: [Plan Title]

**Plan**: thoughts/shared/plans/YYYY-MM-DD-description.md
**Completed**: YYYY-MM-DD HH:MM
**All phases verified**: YES

## Files changed

**Modified:**
- `Features/Review/Handlers/ReviewHandler.cs`
- `Features/Review/Handlers/ReviewHandler.cs` (constructor)

**Added:**
- `tests/Unit/Features/Review/ReviewHandlerNotificationTests.cs`

**Deleted:** None

## Final verification

- ✓ `dotnet build` — 0 errors
- ✓ `dotnet test` — all 47 tests pass (3 new)
- ✓ `dotnet format --verify-no-changes` — clean
```
