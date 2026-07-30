# Compliance Scoring Reference

## Scoring Methodology

### Overview

The TDD Compliance Score evaluates five categories, each scored 1-5:

| Score | Meaning |
|-------|---------|
| 5 | Exemplary — Best practices followed consistently |
| 4 | Good — Minor deviations, overall solid |
| 3 | Acceptable — Noticeable issues, but TDD was attempted |
| 2 | Poor — Significant deviations from TDD |
| 1 | Minimal — TDD not effectively practiced |

### Category 1: Test-First Development (1-5)

**What it measures**: Evidence that tests were written before implementation.

**Scoring Criteria**:

| Score | Criteria |
|-------|----------|
| 5 | All features have test commits preceding implementation commits |
| 4 | 80%+ features show test-first, minor exceptions explained |
| 3 | 50-80% test-first, some simultaneous commits |
| 2 | Less than 50% test-first, many simultaneous commits |
| 1 | Tests appear after implementation or no clear order |

**Evidence to Examine**:
- Git commit history chronology
- Commit messages mentioning tests
- Separate commits for test vs implementation
- RED phase evidence in commit messages

**Example Analysis**:
```
Commit History Analysis:
abc123 "Add test for login validation" (test file only)
def456 "Implement login validation" (impl file only)
ghi789 "Add user registration" (test AND impl together)

Result: 2/3 features show test-first = 4/5
```

### Category 2: Behavioral Testing (1-5)

**What it measures**: Tests verify behavior, not implementation details.

**Scoring Criteria**:

| Score | Criteria |
|-------|----------|
| 5 | All tests verify observable behavior from user/caller perspective |
| 4 | Rare implementation coupling, mostly behavioral |
| 3 | Mixed — some behavioral, some implementation-coupled |
| 2 | Many tests verify internal state or method calls |
| 1 | Most tests are implementation-coupled or mock-heavy |

**Evidence to Examine**:
- Test assertions (behavior vs implementation)
- Mock usage patterns
- Private method testing
- Refactoring resilience

**Behavioral Test Indicators**:
```python
# BEHAVIORAL (Good)
def test_user_can_purchase_item():
    user = User(balance=100)
    item = Item(price=50)

    result = user.purchase(item)

    assert result.success == True
    assert user.balance == 50
    assert item in user.inventory

# IMPLEMENTATION-COUPLED (Bad)
def test_purchase_calls_payment_processor():
    mock_processor = Mock()
    user = User(payment_processor=mock_processor)

    user.purchase(item)

    mock_processor.process.assert_called_once()
```

### Category 3: Minimal Implementation (1-5)

**What it measures**: Implementation contains only what tests require.

**Scoring Criteria**:

| Score | Criteria |
|-------|----------|
| 5 | All code is covered by tests, no speculative features |
| 4 | Minor untested helpers or utilities, core is tested |
| 3 | Some untested features, but main paths covered |
| 2 | Significant untested code, over-engineering visible |
| 1 | Much code without corresponding tests |

**Evidence to Examine**:
- Coverage gaps
- Code complexity vs test complexity
- Speculative generality
- Unused parameters or branches

**Over-Engineering Signs**:
```python
# MINIMAL (Good - tests require basic greeting)
def greet(name):
    return f"Hello, {name}!"

# OVER-ENGINEERED (Bad - no tests require this)
def greet(name, greeting="Hello", punctuation="!",
          language="en", formal=False):
    if language == "es":
        greeting = "Hola" if not formal else "Buenos días"
    elif formal:
        greeting = "Good day"
    title = "Mr./Ms. " if formal else ""
    return f"{greeting}, {title}{name}{punctuation}"
```

### Category 4: Refactoring Discipline (1-5)

**What it measures**: Refactoring maintains green tests.

**Scoring Criteria**:

| Score | Criteria |
|-------|----------|
| 5 | All refactorings maintain passing tests, clean commits |
| 4 | Refactorings mostly maintain green, rare breaks quickly fixed |
| 3 | Some refactorings break tests temporarily |
| 2 | Frequent test breakage during refactoring |
| 1 | Refactoring and behavior changes mixed |

**Evidence to Examine**:
- Commits that change only structure (no behavior)
- Test stability during refactoring
- Separate refactoring commits from feature commits

**Good Refactoring Commit Pattern**:
```
abc123 "Refactor: Extract payment calculation"
  - Modified: src/order.py
  - No test changes needed
  - Tests still pass: 45/45
```

### Category 5: Coverage Quality (1-5)

**What it measures**: Tests actually verify behavior, not just execute code.

**Scoring Criteria**:

| Score | Criteria |
|-------|----------|
| 5 | High coverage with meaningful assertions, edge cases covered |
| 4 | Good coverage, most assertions verify behavior |
| 3 | Moderate coverage, some coverage theater |
| 2 | Low coverage or many assert-free tests |
| 1 | Coverage theater — tests don't catch regressions |

**Evidence to Examine**:
- Assertion count and quality
- Edge case coverage
- Error path testing
- Mutation testing results (if available)

**Coverage Quality Indicators**:
```python
# HIGH QUALITY (Good)
def test_divide_by_zero():
    with pytest.raises(ZeroDivisionError):
        divide(10, 0)

def test_divide_negative_numbers():
    assert divide(-10, 2) == -5

def test_divide_results_in_float():
    assert divide(5, 2) == 2.5

# LOW QUALITY (Bad)
def test_divide():
    divide(10, 2)  # No assertion!

def test_divide_works():
    result = divide(10, 2)
    assert result  # Just checks truthy!
```

## Calculating Overall Score

### Formula

```
Overall Score = (Cat1 + Cat2 + Cat3 + Cat4 + Cat5) / 25 * 100

Rating Scale:
90-100%: Excellent
75-89%: Good
60-74%: Acceptable
40-59%: Needs Improvement
0-39%: Poor
```

### Weighting (Optional)

For projects prioritizing certain aspects:

```
Weighted Score = (Cat1 * W1 + Cat2 * W2 + ... + Cat5 * W5) / (5 * Sum(W))

Example Weights:
- New Project: Test-First (1.5), Behavioral (1.2), others (1.0)
- Legacy Project: Coverage Quality (1.5), Minimal Impl (1.2), others (1.0)
```

## Score Interpretation

### Score: 90-100% (Excellent)

**Interpretation**: TDD is well-practiced.

**Characteristics**:
- Tests consistently drive development
- Behavioral focus in testing
- Minimal waste in implementation
- Clean refactoring discipline
- High-quality coverage

**Recommendation**: Document and share practices with team.

### Score: 75-89% (Good)

**Interpretation**: TDD is practiced with minor gaps.

**Characteristics**:
- Most features show test-first
- Occasional implementation coupling
- Some over-engineering
- Mostly clean refactoring

**Recommendation**: Address specific weak categories.

### Score: 60-74% (Acceptable)

**Interpretation**: TDD attempt visible but inconsistent.

**Characteristics**:
- Mixed test-first and test-after
- Noticeable implementation coupling
- Some coverage theater
- Occasional discipline lapses

**Recommendation**: Training on weak areas, pair programming.

### Score: 40-59% (Needs Improvement)

**Interpretation**: TDD not effectively practiced.

**Characteristics**:
- Mostly test-after
- Implementation-focused tests
- Low coverage quality
- Refactoring breaks tests

**Recommendation**: TDD coaching, start with kata exercises.

### Score: 0-39% (Poor)

**Interpretation**: TDD not meaningfully practiced.

**Characteristics**:
- Tests as afterthought
- Mock-heavy, implementation-coupled
- Extensive coverage theater
- No refactoring discipline

**Recommendation**: Fundamental TDD education needed.

## Reporting Template

```markdown
## TDD Compliance Score

**Project**: [name]
**Date**: [date]
**Period**: [date range]

### Scores

| Category | Score | Status |
|----------|-------|--------|
| Test-First Development | X/5 | [emoji] |
| Behavioral Testing | X/5 | [emoji] |
| Minimal Implementation | X/5 | [emoji] |
| Refactoring Discipline | X/5 | [emoji] |
| Coverage Quality | X/5 | [emoji] |

**Overall**: X/25 (XX%) — [Rating]

### Key Findings

**Strongest Area**: [category] — [why]
**Weakest Area**: [category] — [why]

### Improvement Priority

1. [First priority action]
2. [Second priority action]
3. [Third priority action]

### Detailed Notes

[Category-by-category analysis with specific examples]
```
