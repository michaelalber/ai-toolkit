---
name: tdd-verify
description: Verify AI-generated code follows TDD discipline. Use to audit commits, check coverage quality, detect TDD anti-patterns, and generate compliance scorecards.
---

# TDD Verify (Gatekeeper)

> "Any fool can write code that a computer can understand. Good programmers write code that humans can understand."
> — Martin Fowler

## Core Philosophy

TDD verification ensures that the discipline was followed, not just that tests exist. Tests written after implementation feel different, test different things, and provide different value than tests written first.

**The Gatekeeper's Role:**
- Detect when TDD wasn't followed
- Identify coverage theater (tests that don't test)
- Score TDD compliance
- Guide improvement

## Kent Beck's 12 Test Desiderata (Verification Focus)

Use these properties to evaluate test quality:

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

### 1. Commit History Analysis

Examine git history to verify test-first development:

```bash
# Check if tests were committed before implementation
git log --oneline --name-only | less

# Expected pattern:
# abc1234 Add test for user login
#   tests/test_auth.py
# def5678 Implement user login
#   src/auth.py
```

### 2. Coverage Quality Analysis

Look beyond coverage percentage to coverage quality:

```markdown
Coverage Theater Signs:
- 100% coverage with no assertions
- Tests that only call methods
- Happy path only, no edge cases
- Implementation details tested
```

### 3. Test Quality Audit

Examine individual tests for TDD characteristics:

```markdown
Test Quality Checklist:
□ Test name describes behavior
□ Arrange-Act-Assert structure clear
□ Single concept per test
□ Assertions are specific
□ No implementation details exposed
□ Failure message would be helpful
```

### 4. Compliance Scorecard

Generate a TDD compliance score:

```markdown
## TDD Compliance Scorecard

| Category | Score | Notes |
|----------|-------|-------|
| Test-First Evidence | 3/5 | Some tests added with impl |
| Behavioral Tests | 4/5 | Minor impl coupling |
| Minimal Implementation | 5/5 | No over-engineering |
| Refactoring Discipline | 4/5 | Most refactors preserved green |
| Coverage Quality | 3/5 | Some coverage theater |

**Overall Score**: 19/25 (76%)
**Rating**: Good (with improvement areas)
```

## Workflow

### Step 1: Gather Evidence

Collect information for verification:

```markdown
Evidence Collection:
1. Git commit history (chronological)
2. Test file contents
3. Implementation file contents
4. Coverage report (if available)
5. Test execution results
```

### Step 2: Analyze Commit Order

Check if tests preceded implementation:

```markdown
Commit Order Analysis:

| Commit | Type | TDD Compliant? |
|--------|------|----------------|
| abc123 | Test | N/A (first) |
| def456 | Impl | Yes (test first) |
| ghi789 | Both | No (should be separate) |
| jkl012 | Impl | No (no preceding test) |
```

### Step 3: Analyze Test Quality

Evaluate each test against quality criteria:

```markdown
Test Quality Analysis:

**test_user_can_login**
- Behavioral: Yes (tests login outcome)
- Specific: Yes (checks user object)
- Isolated: Yes (no shared state)
- Implementation-coupled: No
- Quality: Good

**test_database_insert_called**
- Behavioral: No (tests internal call)
- Specific: Yes
- Isolated: Yes
- Implementation-coupled: Yes (mock verification)
- Quality: Poor (should test outcome)
```

### Step 4: Check Coverage Quality

Look beyond the percentage:

```markdown
Coverage Quality Check:

**High-quality coverage indicators:**
- Tests fail when behavior breaks
- Edge cases are covered
- Error paths are tested
- Assertions verify outcomes

**Coverage theater indicators:**
- Tests pass even with broken behavior
- No assertions (just coverage)
- Only exercises code paths
- Happy path only
```

### Step 5: Generate Scorecard

Compile findings into actionable report:

```markdown
## TDD Verification Report

### Summary
[Overall assessment]

### Strengths
- [What was done well]

### Improvement Areas
- [What could be better]

### Recommendations
1. [Specific action item]
2. [Specific action item]

### Detailed Findings
[Section for each category]
```

## AI Anti-Patterns to Detect

### Anti-Pattern 1: Test-After Implementation

**Signs:**
- Tests mirror implementation structure
- Tests use same variable names as implementation
- Test written to match existing behavior

**Detection:**
```
Look for:
- Commit with both test and impl
- Test that seems to "document" rather than "specify"
- No failing test commit before implementation
```

### Anti-Pattern 2: Over-Mocking

**Signs:**
- More mocks than real objects
- Tests that verify method calls
- Mocks returning mocks

**Detection:**
```python
# Suspicious: Testing internal calls
def test_save_user(self):
    mock_db = Mock()
    service = UserService(mock_db)
    service.save(user)
    mock_db.execute.assert_called_with(
        "INSERT INTO users ...",
        (user.id, user.name)
    )
```

### Anti-Pattern 3: Happy Path Only

**Signs:**
- No error case tests
- No edge case tests
- No boundary tests

**Detection:**
```markdown
Test inventory check:
- test_add_positive_numbers ✓
- test_add_zero ✗ missing
- test_add_negative ✗ missing
- test_add_overflow ✗ missing
```

### Anti-Pattern 4: Assert-Free Tests

**Signs:**
- Tests that only call methods
- Tests that print output
- Tests that "verify" nothing

**Detection:**
```python
# Suspicious: No assertions
def test_process_data(self):
    processor = DataProcessor()
    processor.process(data)
    # No assertion!
```

### Anti-Pattern 5: Implementation Coupling

**Signs:**
- Tests break on refactoring
- Tests verify private methods
- Tests depend on specific structure

**Detection:**
```python
# Suspicious: Testing internal structure
def test_user_has_internal_state(self):
    user = User("alice")
    assert user._internal_cache is not None
    assert user._validate_called == True
```

### Anti-Pattern 6: Copy-Paste Tests

**Signs:**
- Tests differ only in values
- No parameterization
- Duplicated setup code

**Detection:**
```python
# Suspicious: Copy-paste tests
def test_add_1_and_2(self):
    assert add(1, 2) == 3

def test_add_3_and_4(self):
    assert add(3, 4) == 7

def test_add_5_and_6(self):
    assert add(5, 6) == 11
```

## Output Templates

### Quick Verification Summary

```markdown
## TDD Quick Check

**Repository/Branch**: [info]
**Period**: [date range]
**Commits Analyzed**: N

### Traffic Light Summary
- Test-First: [GREEN | YELLOW | RED]
- Test Quality: [GREEN | YELLOW | RED]
- Coverage Quality: [GREEN | YELLOW | RED]

### Key Findings
1. [Most important finding]
2. [Second finding]
3. [Third finding]

### Recommended Actions
- [Immediate action]
- [Short-term improvement]
```

### Detailed Verification Report

```markdown
## TDD Verification Report

**Date**: [date]
**Scope**: [what was analyzed]
**Auditor**: Claude Code (tdd-verify)

---

### Executive Summary

[1-2 paragraph overall assessment]

---

### Scoring

| Category | Score | Status |
|----------|-------|--------|
| Test-First Development | X/5 | [status] |
| Behavioral Testing | X/5 | [status] |
| Minimal Implementation | X/5 | [status] |
| Refactoring Discipline | X/5 | [status] |
| Coverage Quality | X/5 | [status] |

**Overall**: X/25 ([percentage]%)

---

### Category Details

#### Test-First Development

[Analysis and evidence]

#### Behavioral Testing

[Analysis and evidence]

[... etc for each category ...]

---

### Anti-Patterns Detected

| Anti-Pattern | Occurrences | Severity | Examples |
|--------------|-------------|----------|----------|
| [pattern] | N | [H/M/L] | [file:line] |

---

### Recommendations

**Immediate (This Sprint)**
1. [Action item]

**Short-term (This Month)**
1. [Action item]

**Long-term (Ongoing)**
1. [Action item]

---

### Appendix: Detailed Findings

[Supporting details, code snippets, etc.]
```

## AI Discipline Rules

### CRITICAL: Evidence-Based Verification

Never claim TDD compliance without evidence:
- Commit history must show test-first
- Coverage must show meaningful assertions
- Tests must exercise behavior

### CRITICAL: Be Constructive

Verification is for improvement, not punishment:
- Frame findings as opportunities
- Provide specific, actionable recommendations
- Acknowledge what was done well

### CRITICAL: Context Matters

Consider the situation:
- Legacy code may not follow TDD
- Time pressure affects discipline
- Learning curves are real

### CRITICAL: Distinguish Intent

Separate intentional choices from mistakes:
- Some code may intentionally skip tests
- Some tests may be exploratory
- Ask before assuming violations

## Stack-Specific Guidance

See reference files for verification tools:
- [Compliance Scoring](references/compliance-scoring.md) - Detailed scoring methodology
- [AI Anti-patterns](references/ai-antipatterns.md) - Patterns specific to AI-generated code
