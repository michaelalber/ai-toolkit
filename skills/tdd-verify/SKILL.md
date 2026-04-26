---
name: tdd-verify
description: >
  Verify AI-generated code follows TDD discipline. Use when auditing commits for TDD discipline,
  checking test coverage quality, detecting TDD anti-patterns, or generating compliance scorecards.
  Do NOT use when reviewing legacy code written before TDD was applied without
  first establishing a baseline; Do NOT use when you have not reviewed project history.
---

# TDD Verify (Gatekeeper)

> "Any fool can write code that a computer can understand. Good programmers write code that humans can understand."
> — Martin Fowler

## Core Philosophy

TDD verification ensures that the discipline was followed, not just that tests exist. Tests written after implementation feel different, test different things, and provide different value than tests written first.

**The Gatekeeper's Role:** Detect when TDD wasn't followed. Identify coverage theater (tests that don't test). Score TDD compliance. Guide improvement.

## Knowledge Base Lookups

| Query | When to Call |
|-------|--------------|
| `search_knowledge("TDD anti-patterns test after implementation coverage theater")` | During verification — authoritative anti-pattern catalog to check against |
| `search_knowledge("test quality desiderata behavioral isolated deterministic")` | When scoring test quality — confirms the 12 properties and their verification questions |
| `search_knowledge("code coverage mutation testing quality metrics")` | When assessing coverage quality vs. coverage theater |
| `search_knowledge("TDD discipline red green refactor commit order")` | When auditing commit history — confirms expected TDD commit sequence |

Search at verification start to load authoritative compliance criteria. Cite the source path in the scorecard.

## Kent Beck's 12 Test Desiderata (Verification Focus)

| Property | Verification Question |
|----------|----------------------|
| **Isolated** | Can each test run independently? |
| **Composable** | Can tests be run in any subset? |
| **Deterministic** | Do tests always give the same result? |
| **Specific** | Do failures point to the exact cause? |
| **Behavioral** | Do tests verify behavior, not implementation? |
| **Structure-insensitive** | Would refactoring break these tests? |
| **Fast** | Is feedback loop quick enough? |
| **Writable** | Are tests easy to create? |
| **Readable** | Can you understand intent quickly? |
| **Automated** | Do tests run without intervention? |
| **Predictive** | Does passing mean it works? |
| **Inspiring** | Do tests give confidence to change? |

## Verification Modes

**Commit History Analysis** — verify test-first development by examining git history:

```bash
# Check if tests were committed before implementation
git log --oneline --name-only | less
# Expected: test file commit precedes implementation file commit
```

**Coverage Quality Analysis** — look beyond percentage to quality. Coverage theater signs: 100% coverage with no assertions, tests that only call methods, happy path only, implementation details tested.

**Test Quality Audit** — checklist per test: test name describes behavior, Arrange-Act-Assert structure clear, single concept per test, assertions are specific, no implementation details exposed, failure message would be helpful.

**Compliance Scorecard** — five categories scored 0–5: Test-First Evidence, Behavioral Tests, Minimal Implementation, Refactoring Discipline, Coverage Quality. Total out of 25.

## Workflow

### Step 1: Gather Evidence

Collect: git commit history (chronological), test file contents, implementation file contents, coverage report (if available), test execution results.

### Step 2: Analyze Commit Order

Check if tests preceded implementation. Flag any commit that contains both test and implementation files in a single commit ("should be separate"), and any implementation commit without a preceding test commit.

| Commit | Type | TDD Compliant? |
|--------|------|----------------|
| abc123 | Test | N/A (first) |
| def456 | Impl | Yes (test first) |
| ghi789 | Both | No (should be separate) |
| jkl012 | Impl | No (no preceding test) |

### Step 3: Analyze Test Quality

For each test, evaluate against the 12 Desiderata. Note: Behavioral (tests outcome, not internal call), Specific (precise assertion), Isolated (no shared state), Structure-insensitive (not verifying private methods or internal structure).

### Step 4: Check Coverage Quality

High-quality indicators: tests fail when behavior breaks, edge cases covered, error paths tested, assertions verify outcomes. Theater indicators: tests pass even with broken behavior, no assertions, only exercises code paths, happy path only.

### Step 5: Generate Scorecard

Compile findings into a report with: Overall assessment, Strengths, Improvement Areas, Recommendations (immediate, short-term, long-term), and per-category scores.

## AI Anti-Patterns to Detect

| Anti-Pattern | Signs | Detection Signal |
|---|---|---|
| **Test-After Implementation** | Tests mirror impl structure; same variable names as impl; test "documents" rather than "specifies" | Both test and impl in same commit; no failing-test commit before impl commit |
| **Over-Mocking** | More mocks than real objects; tests verify method calls; mocks returning mocks | `assert_called_with(...)` on implementation-internal methods |
| **Happy Path Only** | No error, edge, or boundary tests | Test inventory missing: zero cases, overflow cases, invalid input cases |
| **Assert-Free Tests** | Tests only call methods; tests print output; tests "verify" nothing | Zero assertion statements in test body |
| **Implementation Coupling** | Tests break on refactoring; tests verify private methods; tests depend on specific structure | `_private_method` or `_internal_state` references in test assertions |
| **Copy-Paste Tests** | Tests differ only in values; no parameterization; duplicated setup code | Test names following pattern `test_X_1`, `test_X_2`, `test_X_3` |

## Output Templates

```markdown
## TDD Compliance Scorecard: [Repo/Branch]
**Period**: [date range] | **Commits Analyzed**: N

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

Full templates (Detailed Verification Report with per-category analysis and Appendix): `references/compliance-scoring.md`

## State Block

```
<tdd-verify-state>
scope: [repo path | branch | commit range | "pending"]
commits_analyzed: [N | "none yet"]
current_category: [test-first | behavioral | minimal-impl | refactor | coverage | "complete"]
score_so_far: [e.g., "12/20 — 3 categories complete"]
anti_patterns_found: [comma-separated list or "none"]
findings_pending_review: [N items]
last_action: [what was just done]
next_action: [what should happen next]
</tdd-verify-state>
```

## AI Discipline Rules

**Evidence-based verification only.** Never claim TDD compliance without evidence. Commit history must show test-first ordering. Coverage must show meaningful assertions. Tests must exercise behavior, not internal structure.

**Be constructive — verification is for improvement, not punishment.** Frame findings as opportunities. Provide specific, actionable recommendations. Acknowledge what was done well.

**Context matters.** Legacy code may not follow TDD. Time pressure affects discipline. Learning curves are real. Consider the situation before scoring.

**Distinguish intent from mistakes.** Some code may intentionally skip tests. Some tests may be exploratory. Ask before assuming violations when the situation is ambiguous.

## Integration with Other Skills

- **`tdd-cycle`** — Audit a session orchestrated by tdd-cycle; full-cycle commit history provides the richest evidence
- **`tdd-agent`** — Run tdd-verify after an autonomous tdd-agent session to confirm discipline was followed
- **`tdd-pair`** — Run tdd-verify at the end of a pair session to score compliance and surface improvement areas
- **`tdd-refactor`** — If tdd-verify finds implementation-coupled tests, invoke tdd-refactor to decouple them safely
- **`tdd-implementer`** — If tdd-verify finds over-engineering or over-mocking, trace findings back to the GREEN phase for root-cause

Reference files: `references/compliance-scoring.md` (detailed scoring methodology) | `references/ai-antipatterns.md` (patterns specific to AI-generated code)
