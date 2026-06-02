# `slice-NN-{name}.md` Template

The Implement phase writes one of these per executed slice to the feature folder's implementation
subdirectory: `thoughts/shared/qrspi/YYYY-MM-DD-{feature-slug}/implementation/slice-NN-{name}.md`.
It is the **resumption point** for the next fresh session -- a later session reads the latest slice
log, not the transcript. Its job is to PROVE the slice ran Red-Green-Refactor, by capturing the
actual command output at the RED and GREEN gates.

```markdown
---
date: YYYY-MM-DDTHH:MM:SS
repository: [repo name]
topic: "[feature, one line]"
tags: [qrspi, implement, slice-NN]
git_commit: [short hash at slice start]
phase: Implement (I)
qrspi_feature: [feature-slug]
plan_artifact: thoughts/shared/qrspi/YYYY-MM-DD-{slug}/plan.md
slice: NN
slice_name: [vertical-slice-name from plan Phase NN]
status: complete        # in-progress while running; complete when GREEN + recorded
---

# Slice NN — [vertical slice name]

Implements **Phase NN** of `plan.md`. [One sentence: the end-to-end increment this slice delivers.]

## RED — failing test first
**Test added:** `path/to/test_file.ext` :: `[test name]`
**Command:** `[test command]`
**Result:** FAIL (expected) — paste the failing assertion / error:
```
[actual RED command output — the proof the test fails before the code exists]
```

## GREEN — minimal code to pass
**Production changes:**
- `path/to/file.ext` — [what changed, briefly]
**Command:** `[build + test command]`
**Result:** PASS (required) — paste the passing summary:
```
[actual GREEN command output — the proof build + tests pass]
```

## REFACTOR — cleanup, stays green
- [What was tidied, or "none — code already clean."]
**Command:** `[test command]` **Result:** still GREEN.

## Files changed
- `path/to/file.ext` (production)
- `path/to/test_file.ext` (test)

## Checkpoint / resume note
- Suggested commit: `git add [files] && git commit -m 'feat: [slice NN description]'`
- Next slice: **Phase NN+1 — [name]** (or "feature complete").
- Context at handoff: [under-40 | checkpoint-now]. Start a fresh session for the next slice.
```

## Authoring rules
- **Proof, not prose:** paste the real RED and GREEN command output. A slice with no captured RED
  output did not prove test-first and is not done.
- **RED must actually be red:** if the first run of the new test passes, the test is wrong — fix the
  test and re-run before writing any production code.
- **One slice per file:** never combine two plan phases into one log; the per-slice file is what
  makes a fresh session cheap.
- **`status: complete` only after GREEN:** while a slice is mid-flight, leave `status: in-progress`
  so a resuming session knows where it stopped.
- **No invention:** if the slice needs something the plan does not describe, STOP and re-run
  `/qrspi-plan`; do not record an improvised change as if it were planned.
