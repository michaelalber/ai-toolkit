# `implementation-log-{slice}.md` Template

The Implement phase writes one of these per backlog slice to the project folder
`thoughts/shared/qraspi/YYYY-MM-DD-{slug}/implementation-log-{slice}.md`. It is the **resumption
point** for the next fresh session -- a later session reads the latest slice log, not the transcript.
Its job is to PROVE the slice ran Red-Green-Refactor *and kept the skeleton's fitness gates green*, by
capturing the actual command output at the RED, GREEN, and gate checks for each phase in
`plan-{slice}.md`.

```markdown
---
date: YYYY-MM-DDTHH:MM:SS
repository: [repo name]
topic: "[the slice, one line]"
tags: [qraspi, implement, slice]
git_commit: [short hash at slice start]
phase: Implement (I)
qraspi_project: [project-slug]
slice: [slice-slug]
plan_artifact: thoughts/shared/qraspi/YYYY-MM-DD-{slug}/plan-{slice}.md
status: complete        # in-progress while running; complete when every phase is GREEN + recorded
---

# Implementation log — [slice] (on the [project] skeleton)

Executes `plan-{slice}.md` on the green walking skeleton. [One sentence: the increment this slice
delivers.] One section per plan phase; each proves RED -> GREEN -> REFACTOR with the fitness gates green.

## Phase 1 — [phase name]

### RED — failing test first
**Test added:** `path/to/test_file.ext` :: `[test name]`
**Command:** `[test command]`
**Result:** FAIL (expected) — paste the failing assertion / error:
```
[actual RED command output — the proof the test fails before the code exists]
```

### GREEN — minimal code to pass (tests + fitness gates)
**Production changes:**
- `path/to/file.ext` — [what changed, briefly]
**Command:** `[build + test command]`  →  PASS
**Fitness gates:** `[fitness gate command]`  →  GREEN (the skeleton's gates still pass)
```
[actual GREEN command output — the proof build + tests AND the gates pass]
```

### REFACTOR — cleanup, stays green
- [What was tidied, or "none — code already clean."]
**Command:** `[test + gate command]` **Result:** still GREEN.

## Phase 2 — [phase name]
[Same shape: RED · GREEN (tests + gates) · REFACTOR.]

## Files changed
- `path/to/file.ext` (production)
- `path/to/test_file.ext` (test)

## Checkpoint / resume note
- Suggested commit: `git add [files] && git commit -m 'feat: [slice] — [phase]'`
- Next: **Phase N+1** in this slice, or the next backlog slice via `/qraspi-plan`, or
  "all backlog slices built → /qraspi-graduate".
- Context at handoff: [under-40 | checkpoint-now]. Start a fresh session for the next phase/slice.
```

## Authoring rules
- **Proof, not prose:** paste the real RED and GREEN command output. A phase with no captured RED
  output did not prove test-first and is not done.
- **Gates are part of GREEN:** capture the fitness-gate result alongside each GREEN run. A phase whose
  code passes the tests but trips a skeleton fitness gate is RED, not done — fix it, never disable the gate.
- **RED must actually be red:** if the first run of the new test passes, the test is wrong — fix the
  test and re-run before writing any production code.
- **One slice per file:** the log covers one `plan-{slice}.md`; the next backlog slice is a separate
  log. The per-slice file is what makes a fresh session cheap.
- **`status: complete` only after every phase is GREEN:** while mid-flight, leave `status: in-progress`
  so a resuming session knows where it stopped.
- **No invention:** if a phase needs something the plan does not describe, STOP and re-run
  `/qraspi-plan` (or `/qraspi-architecture` for a design change); never record an improvised change as planned.
