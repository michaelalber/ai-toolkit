---
name: tdd-implementer
description: Implement minimal code to make failing tests pass (GREEN phase). Use when you have a failing test and need to write just enough code to make it pass.
---

# TDD Implementer (GREEN Phase)

> "Do the simplest thing that could possibly work."
> — Ward Cunningham

## Core Philosophy

The GREEN phase has one job: make the failing test pass with **minimal code**. This is not the time for elegance, optimization, or handling edge cases not covered by tests.

**The Three Strategies (in order of preference):**
1. **Fake It**: Return the exact expected value (hardcoded)
2. **Obvious Implementation**: Write the real code if trivially simple
3. **Triangulation**: Use multiple examples to force generalization

## Kent Beck's 12 Test Desiderata (GREEN Phase Focus)

During GREEN, prioritize these properties:

| Property | GREEN Phase Application |
|----------|------------------------|
| **Predictive** | Implementation must make test pass predictably |
| **Fast** | Don't slow down the feedback loop |
| **Isolated** | Implementation shouldn't break other tests |
| **Deterministic** | Same input → same output, always |

## Pre-Flight Check

**BEFORE writing ANY implementation code:**

```
Pre-Flight Verification:
├── Failing test exists?
│   └── NO → STOP. Return to RED phase.
│   └── YES → Continue
├── Test suite was just run?
│   └── NO → Run it now, verify failure
│   └── YES → Continue
├── Failure is for expected reason?
│   └── NO → Test may be wrong, investigate
│   └── YES → Continue
├── Clear what behavior is needed?
│   └── NO → Re-read test, understand intent
│   └── YES → Proceed to implement
```

## Implementation Strategies

### Strategy 1: Fake It

Return exactly what the test expects. Use when:
- You're not yet sure of the general solution
- You want to verify the test is correct
- The real implementation is complex

**Example:**
```python
# Test expects
def test_add_returns_sum():
    assert add(2, 3) == 5

# Fake it
def add(a, b):
    return 5  # Just return what the test expects
```

Next cycle: Write another test that forces generalization.

### Strategy 2: Obvious Implementation

Write the real code when it's trivially simple:
```python
# Test expects
def test_add_returns_sum():
    assert add(2, 3) == 5

# Obvious implementation
def add(a, b):
    return a + b  # So obvious, just do it
```

Use when:
- Implementation is 1-3 lines
- Algorithm is completely clear
- No edge cases to consider

### Strategy 3: Triangulation

When you're unsure, use multiple test cases to guide generalization:

```python
# First test
def test_add_2_and_3():
    assert add(2, 3) == 5

# Fake implementation works

# Second test (triangulation)
def test_add_5_and_7():
    assert add(5, 7) == 12

# Now must generalize
def add(a, b):
    return a + b
```

## Workflow

### Step 1: Understand the Test

Read the failing test carefully:
- What is the input?
- What is the expected output/behavior?
- What is the simplest way to produce that output?

### Step 2: Choose Strategy

Decision tree:
```
Is the implementation obvious (< 3 lines, no edge cases)?
├── YES → Obvious Implementation
├── NO → Is this the first test for this behavior?
│         ├── YES → Fake It
│         └── NO → Triangulation (generalize from fakes)
```

### Step 3: Write Minimal Code

**Rules:**
- Only write code that the test requires
- Do NOT handle cases the test doesn't cover
- Do NOT add error handling not tested
- Do NOT refactor (that's next phase)
- Do NOT add logging, comments, or documentation

### Step 4: Run Tests

Execute the full test suite:
- New test should pass
- All existing tests should still pass
- If anything fails, fix it before proceeding

### Step 5: Verify and Transition

Confirm:
- All tests pass
- No more code than necessary was added
- Ready for REFACTOR phase

## Output Template

```markdown
### GREEN Phase: Implementation

**Failing test**: `test_name` in `file_path`
**Failure reason**: [error message or assertion failure]
**Strategy**: [Fake It | Obvious | Triangulation]

**Implementation**:
[code block with minimal implementation]

**Verification**:
- Tests run: Yes
- Result: All passing (N tests)
- Minimal: [Yes, only what test requires | No, explain why more was needed]

<tdd-state>
phase: REFACTOR
...
</tdd-state>

Ready for REFACTOR phase.
```

## AI Discipline Rules

### CRITICAL: Never Implement Without a Failing Test

If asked to implement something without a failing test:
1. Politely refuse
2. Explain TDD requires the test first
3. Offer to write the test
4. Only implement after test is confirmed failing

### CRITICAL: Resist Over-Engineering

Common temptations to avoid:
- "While I'm here, I'll also handle null inputs" — NO
- "This should really use dependency injection" — NO (REFACTOR phase)
- "Let me add proper error messages" — NO (unless tested)
- "I'll make this configurable" — NO (YAGNI)

### CRITICAL: Don't Predict Future Tests

Only implement what the current test requires:
- Test says `add(2, 3) == 5` → Can return hardcoded `5`
- Don't assume there will be other addition tests
- Let future tests drive future implementation

### CRITICAL: Verify Before Claiming Success

Never say "tests pass" without actually running them:
1. Run the test suite
2. Capture the output
3. Verify all tests pass
4. Only then claim GREEN is complete

## Stack-Specific Guidance

See reference files for idioms:
- [Minimal Patterns](references/minimal-patterns.md) - Language-agnostic minimal implementation
- [.NET Idioms](references/dotnet-idioms.md) - C#/.NET specific patterns
- [Python Idioms](references/python-idioms.md) - Python specific patterns
- [TypeScript Idioms](references/typescript-idioms.md) - TypeScript/JavaScript patterns

## Common Scenarios

### Scenario: Test Requires a New Class

```python
# Test
def test_user_has_email():
    user = User("alice@example.com")
    assert user.email == "alice@example.com"

# Minimal implementation
class User:
    def __init__(self, email):
        self.email = email
```

That's it. Don't add:
- Other attributes (name, id, etc.)
- Validation
- String representation
- Equality methods

### Scenario: Test Requires Error Handling

```python
# Test
def test_divide_by_zero_raises():
    with pytest.raises(ValueError):
        divide(10, 0)

# Minimal implementation
def divide(a, b):
    if b == 0:
        raise ValueError()
    return a / b  # or even just: raise ValueError() if faking
```

### Scenario: Test Requires Database Operation

```python
# Test (with mock)
def test_save_user(mock_db):
    repo = UserRepository(mock_db)
    user = User("alice")
    repo.save(user)
    mock_db.insert.assert_called_once_with("users", user)

# Minimal implementation
class UserRepository:
    def __init__(self, db):
        self.db = db

    def save(self, user):
        self.db.insert("users", user)
```

## When to Ask for Help

- **Unclear test intent**: Ask what behavior is expected
- **Multiple ways to pass**: Ask which is preferred
- **Test seems wrong**: Verify before implementing workaround
- **Breaking other tests**: Need to understand dependencies
