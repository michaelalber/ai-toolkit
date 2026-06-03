---
name: evaluate-tests
audience: team
description: >
  Audits existing tests in two modes: (1) test-file quality — evaluates tests against Beck's
  behavioral and structure-insensitive criteria, flagging implementation-coupled, fragile, and
  theater tests with a prioritized rewrite list; (2) TDD compliance — analyzes git commit history
  for test-first discipline and produces a 0–25 compliance scorecard with AI anti-pattern findings.
  Use when auditing inherited test suites, checking AI-generated tests before merge, preparing code
  for safe refactoring, or verifying that TDD discipline was actually followed. Triggers on
  "evaluate tests", "audit test quality", "test coupling", "are these tests behavioral", "check my
  tests", "tdd compliance", "did we follow tdd", "tdd scorecard", "audit commits for tdd",
  "tdd anti-patterns". Do NOT use to write new tests — use tdd for that. Do NOT use when the
  codebase has no tests yet.
---

# Evaluate Tests

> "If tests break when you rename a private method, your tests are describing the solution,
> not the problem."
> — Adapted from Kent Beck

## Two Modes

| Mode | Input | Output | Use when |
|------|-------|--------|----------|
| **1 · Test-file quality** | a test file or directory | per-test classification + prioritized rewrite list | auditing whether existing tests are behavioral and refactor-safe |
| **2 · TDD compliance** | git commit history (+ test/impl files) | 0–25 compliance scorecard + anti-pattern findings | verifying test-first discipline was actually followed |

Pick the mode from the request. Run both for a full audit — Mode 1's findings feed the Behavioral
and Coverage categories of Mode 2's scorecard.

---

# Mode 1 — Test-File Quality

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
[commit evidence or "not detectable from test file alone — run Mode 2 (commit history)"]
```

## Scope (Mode 1)

Pass a single file: evaluate all tests in it.
Pass a directory: evaluate the most-changed test files first; ask before evaluating more
than 20 tests in one turn.

For concrete rewrite examples by language: see [Coupling Patterns](references/coupling-patterns.md).

---

# Mode 2 — TDD Compliance (commit-history audit)

Verifies the *discipline* was followed, not just that tests exist. Tests written after
implementation feel different, test different things, and provide different value than tests
written first. This mode detects that from git history and scores it.

## Workflow

1. **Gather evidence** — chronological `git log`, test + implementation file contents, coverage
   report (if available), test-run results.
2. **Analyze commit order** — did a failing-test commit precede each implementation commit? Flag
   commits containing both test and impl ("should be separate") and impl commits with no preceding
   test.

   | Commit | Type | TDD compliant? |
   |--------|------|----------------|
   | abc123 | Test | N/A (first) |
   | def456 | Impl | Yes (test first) |
   | ghi789 | Both | No (should be separate) |
   | jkl012 | Impl | No (no preceding test) |

3. **Analyze test quality** — run Mode 1's classification on the changed tests.
4. **Check coverage quality** — distinguish real coverage (tests fail when behavior breaks; edge
   and error paths covered) from theater (passes even with broken behavior; no assertions; happy
   path only).
5. **Generate the scorecard.**

## AI Anti-Patterns to Detect

| Anti-Pattern | Detection Signal |
|---|---|
| **Test-After Implementation** | Both test and impl in one commit; no failing-test commit before the impl commit |
| **Over-Mocking** | `assert_called_with(...)` on implementation-internal methods |
| **Happy Path Only** | Test inventory missing zero / overflow / invalid-input cases |
| **Assert-Free Tests** | Zero assertion statements in the test body |
| **Implementation Coupling** | `_private_method` / `_internal_state` references in test assertions |
| **Copy-Paste Tests** | Test names like `test_X_1`, `test_X_2` with only value differences |

## Compliance Scorecard

```markdown
## TDD Compliance Scorecard: [repo/branch]
**Period**: [date range] | **Commits analyzed**: N

| Category | Score | Status |
|----------|-------|--------|
| Test-First Development | X/5 | GREEN/YELLOW/RED |
| Behavioral Testing | X/5 | GREEN/YELLOW/RED |
| Minimal Implementation | X/5 | GREEN/YELLOW/RED |
| Refactoring Discipline | X/5 | GREEN/YELLOW/RED |
| Coverage Quality | X/5 | GREEN/YELLOW/RED |
**Overall**: X/25 ([percentage]%)

Anti-patterns: [list or "none"]
Recommendations: Immediate: [...] | Short-term: [...] | Ongoing: [...]
```

Full scoring methodology: [Compliance Scoring](references/compliance-scoring.md).
AI-specific anti-pattern catalog: [AI Anti-Patterns](references/ai-antipatterns.md).

**Discipline rules:** evidence-based only — never claim compliance without commit-history proof;
be constructive (findings drive improvement, not punishment); account for context (legacy code,
time pressure, learning curves) before scoring.
