# [YOUR APP NAME] — Claude Instructions

<!-- Drop this file at the root of your project (same folder as .git/).
     Fill in the Project Overview section. Leave everything else as-is. -->

---

## Project Overview

- **Name:** [Your app name]
- **Purpose:** [One sentence: what does this do and for whom?]
- **Stack:** [e.g., Python + Flask, Node + React, etc.]
- **Phase:** [Building / Fixing / Maintaining]

---

## Core Rules

**Correctness first.** A slower, obviously correct fix beats a clever one that might break something else.

**Explicit over clever.** Readable code is easier to fix later. No tricks.

**Leave it no worse.** Don't clean up unrelated code while fixing a bug — that's how new bugs get introduced.

---

## The #1 Rule: Fix Only What Was Asked

When fixing a bug or adding a feature, **touch only the code required for that change**.

- Do NOT refactor nearby code "while you're in there"
- Do NOT rename variables, reorganize functions, or restructure files unless asked
- Do NOT add error handling, logging, or validation beyond what the task requires
- If you notice something that *should* be fixed but is out of scope, **say so in a comment** — don't just fix it

If the fix requires touching more than expected, **stop and ask** before proceeding.

---

## Before Writing Any Code

1. **Read the relevant files first.** Understand what's already there before changing anything.
2. **State what you're about to change and why.** One sentence is enough.
3. **Identify what could break.** Name any other code that calls or depends on what you're touching.

If you can't clearly answer "what does this code currently do?", say so — don't guess and write.

---

## One Change at a Time

- One logical fix per response. No bundling unrelated changes.
- Show the before/after diff clearly. Don't rewrite whole files when a small edit will do.
- After a fix, point out anything that might need manual testing.

---

## Red-Green-Refactor

This is the most reliable way to add or fix code without introducing new bugs. Follow the three phases in order — **never mix them**.

### RED — write a failing test first
Before writing any implementation, write a test that describes the behavior you want. Run it. It must fail.

- One test at a time. Don't write five tests then implement them all.
- The test should assert an **observable outcome** ("the response status is 200", "the saved name equals 'Alice'") — not internal details ("the method was called").
- If the test passes immediately without any code change, the test is wrong — make it stronger.

### GREEN — write the minimum code to pass
Write only enough code to make the failing test pass. Nothing more.

- No extra error handling "just in case"
- No extra features "while you're here"
- No cleanup or reorganization yet
- Fake it if needed (hardcode a return value) — you'll generalize it later
- Run the full test suite. The new test must pass. All existing tests must still pass.

**If an existing test breaks: stop. Fix that before anything else.**

### REFACTOR — clean up, with tests green
Only after all tests are passing: clean up the code you just wrote.

- One change at a time. Run tests after each change.
- If tests go red during refactor: revert the last change, don't pile on more edits.
- No new behavior during refactor. Bug fixes and new features start a new RED phase.

### Why this prevents bugs
The discipline of keeping the phases separate means:
- You always have a safety net before changing code
- "While I'm here" changes happen in REFACTOR (where tests catch regressions), not GREEN (where the code is still unstabilized)
- A breaking change is caught immediately — at the one step that caused it — instead of buried in a larger diff

### Self-check before moving to the next phase
- [ ] The test was red before I wrote any implementation
- [ ] The test asserts behavior, not internal state
- [ ] My implementation passes this test — and all tests that existed before
- [ ] I am not cleaning up or reorganizing during GREEN
- [ ] I am not adding new behavior during REFACTOR

---

## When to Stop and Ask

Always check with the user before:

- Deleting any file or function
- Changing how data is stored (database schema, file format, data structure)
- Adding a new dependency / package
- Changing any code that wasn't directly related to the stated task
- When you're not sure the fix is correct — say `[UNSURE]: <what you're not sure about]` and explain

---

## Accuracy

- Never invent function names, library APIs, or syntax. If you're not sure, say so.
- Prefer a shorter correct answer over a longer guess.
- Mark anything uncertain with `# VERIFY: [what to check]` rather than presenting it as fact.

---

## Security Basics

Even for personal apps:

- Never hardcode passwords, API keys, or tokens — use environment variables
- Never build SQL queries by concatenating strings — use parameterized queries
- Never log passwords or tokens

---

## Session Start

At the start of each session, briefly confirm:
1. What the current task is
2. Which files are relevant
3. Whether anything from the last session is still in progress

Don't begin work until this is confirmed.

---

## Open Questions / Known Issues

<!-- Keep a running list here so nothing falls through the cracks -->

- [ ] [e.g., Login flow not tested with invalid credentials]
- [ ] [Known issue or unresolved question]
