---
name: evaluate-tests
audience: team
description: >
  Evaluates an existing test file or suite against Beck's behavioral and
  structure-insensitive criteria. Flags implementation-coupled tests, horizontal
  slice patterns, and tests that would not survive a refactor. Produces a
  prioritized rewrite list with the reason for each. Use when auditing inherited
  test suites, preparing code for safe refactoring, checking AI-generated tests
  before merge, or after a TDD compliance scorecard flags behavioral or coupling issues.
  Triggers on "evaluate tests", "audit test quality", "test coupling", "are these tests
  behavioral", "check my tests". Do NOT use to write new tests — use tdd for that.
  Do NOT use when the codebase has no tests yet.
---

# Evaluate Tests

> "If tests break when you rename a private method, your tests are describing the solution,
> not the problem."
> — Adapted from Kent Beck

## What This Skill Evaluates

For each test, assess two properties and one pattern:

### 1. Behavioral (does the test specify behavior?)

A behavioral test fails when the observable outcome breaks.
An implementation-coupled test fails when internals change even if behavior is identical.

| Signal | Behavioral | Implementation-coupled |
|--------|-----------|----------------------|
| Assertion target | Return value, state visible through public API, side effect via public interface | Mock call count (`assert_called_with`), private field access (`_total`), internal call order |
| Refactor sensitivity | Survives extract-method, rename, move-class | Breaks on rename even when behavior is unchanged |
| Failure message | "Expected 42, got 0" — points to the what | "Expected save() to be called once" — points to the how |

### 2. Structure-insensitive (does the test survive internal refactors?)

Run this mental test: *if I renamed every private method and field in this class, would
this test break?* If yes, it is structure-coupled.

### 3. Horizontal slice pattern (were tests written without matching implementation?)

Signs in git history: a commit with 3+ test stubs followed by a commit with all implementations.
Signs in test file: test methods that assert on code that clearly pre-existed the test
(no trace of incremental growth in the test file).

## Per-Test Classification

For each test, classify as one of:

| Class | Definition | Action |
|-------|-----------|--------|
| **PASS** | Behavioral + structure-insensitive | Keep |
| **COUPLED** | Asserts on implementation detail (call counts, private state, internal call order) | Rewrite: assert on observable outcome instead |
| **FRAGILE** | Survives behavior changes but breaks on structural refactors | Rewrite: remove internal references |
| **THEATER** | Passes trivially; no assertion or assertion always passes | Strengthen or delete |

## Output Format

```markdown
## Test Evaluation: [file or suite name]

### Summary
Tests evaluated: N | PASS: N | COUPLED: N | FRAGILE: N | THEATER: N

### Prioritized Rewrite List

| Priority | Test | Class | Reason | Suggested Fix |
|----------|------|-------|--------|---------------|
| 1 | `test_name` | COUPLED | Asserts `repo.save.called` — tests the how, not the what | Assert `repo.find(id) is not None` instead |
| 2 | `test_name` | FRAGILE | Reads `user._email` directly | Assert via `user.get_profile()["email"]` |
| 3 | `test_name` | THEATER | No assertion — only calls the method | Add assertion on return value or observable state |

### Horizontal Slice Signals
[commit evidence or "not detectable from test file alone — check git history with tdd-verify"]
```

## Scope

Pass a single file: evaluate all tests in it.
Pass a directory: evaluate the most-changed test files first; ask before evaluating more
than 20 tests in one turn.

For a full TDD compliance scorecard including commit history analysis: pair with `tdd-verify`.
For concrete rewrite examples by language: see [Coupling Patterns](references/coupling-patterns.md).
