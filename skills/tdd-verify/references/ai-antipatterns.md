# AI Anti-Patterns Reference

## Overview

AI code assistants can generate TDD-violating patterns that look correct but undermine test-driven development. This reference catalogs patterns specific to AI-generated code.

## AI-Specific Anti-Patterns

### Anti-Pattern 1: Simultaneous Test and Implementation

**Description**: AI generates both test and implementation in a single response.

**Why It Happens**:
- AI optimizes for efficiency
- AI wants to be "helpful" by completing the task
- AI doesn't naturally pause for verification

**Example**:
```markdown
AI Response:
"Here's the test and implementation for the feature:

# test_calculator.py
def test_add():
    assert add(2, 3) == 5

# calculator.py
def add(a, b):
    return a + b

Both files are ready to use!"
```

**Why It's Wrong**:
- Test never failed — can't know if it would catch regressions
- Implementation might not satisfy a failing test
- Skips RED phase entirely

**Detection**:
- Single commit with test AND implementation
- No evidence of test failure before implementation
- AI response includes both files together

**Remediation**:
- Separate commits: test first, then implementation
- Require verification of test failure before implementing
- Use tdd-agent guardrails to enforce RED phase

### Anti-Pattern 2: Implementation-Derived Tests

**Description**: AI writes tests based on existing implementation rather than desired behavior.

**Why It Happens**:
- AI reads implementation first
- AI "tests" what the code does, not what it should do
- Tests match implementation structure

**Example**:
```python
# Implementation (written first or read by AI)
def process_order(order):
    if order.total > 100:
        order.apply_discount(0.1)
    order.calculate_tax()
    return order.finalize()

# AI-generated test (mirrors implementation)
def test_process_order():
    order = Mock()
    order.total = 150

    result = process_order(order)

    order.apply_discount.assert_called_with(0.1)
    order.calculate_tax.assert_called_once()
    order.finalize.assert_called_once()
```

**Why It's Wrong**:
- Tests implementation details, not behavior
- Tests break if implementation changes
- Doesn't specify what "processed" means

**Detection**:
- Test structure mirrors implementation structure
- Mock verification of internal calls
- Test and implementation have same control flow

**Remediation**:
```python
# Behavioral test (specifies outcomes)
def test_large_order_gets_discount():
    order = Order(items=[Item(price=150)])

    processed = process_order(order)

    assert processed.final_total == 135  # 10% off
    assert processed.status == "ready"
```

### Anti-Pattern 3: Over-Complete Test Coverage

**Description**: AI generates exhaustive tests that test every code path mechanically.

**Why It Happens**:
- AI aims for high coverage metrics
- AI treats all paths equally
- AI doesn't understand risk-based testing

**Example**:
```python
# AI generates tests for every getter/setter
def test_user_get_name():
    user = User(name="Alice")
    assert user.name == "Alice"

def test_user_set_name():
    user = User(name="Alice")
    user.name = "Bob"
    assert user.name == "Bob"

def test_user_name_is_string():
    user = User(name="Alice")
    assert isinstance(user.name, str)

# ...50 more trivial tests
```

**Why It's Wrong**:
- Tests obvious, low-risk code
- Doesn't focus on behavior
- Creates maintenance burden
- Coverage theater

**Detection**:
- Many tests for simple getters/setters
- Tests that verify type correctness only
- High test count with low behavioral value

**Remediation**:
- Focus on behavior, not structure
- Test interesting interactions
- Skip testing language/framework guarantees

### Anti-Pattern 4: Mock-Everything Testing

**Description**: AI mocks all dependencies, even when real ones are preferable.

**Why It Happens**:
- Mocking is a clear pattern AI can apply
- AI prefers predictable test setups
- AI doesn't know which dependencies are safe

**Example**:
```python
def test_user_full_name():
    mock_first = Mock(return_value="John")
    mock_last = Mock(return_value="Doe")

    user = User()
    user.first_name = mock_first
    user.last_name = mock_last

    assert user.full_name == "John Doe"
```

**Why It's Wrong**:
- Mocking simple value objects
- Tests mock behavior, not real code
- Brittle and confusing

**Detection**:
- Mocks for simple data objects
- Mocks for pure functions
- More mocks than real objects in test

**Remediation**:
```python
def test_user_full_name():
    user = User(first_name="John", last_name="Doe")
    assert user.full_name == "John Doe"
```

### Anti-Pattern 5: Assert-What-Changed Testing

**Description**: AI writes assertions based on what implementation changed, not what should be verified.

**Why It Happens**:
- AI observes implementation effects
- AI generates assertions for visible changes
- AI doesn't understand invariants

**Example**:
```python
# Implementation sets multiple fields
def process_payment(order, amount):
    order.payment_status = "processed"
    order.payment_amount = amount
    order.payment_date = datetime.now()
    order.last_modified = datetime.now()
    order.modified_by = "payment_processor"
    return order

# AI tests all changed fields
def test_process_payment():
    order = Order()
    result = process_payment(order, 100)

    assert result.payment_status == "processed"
    assert result.payment_amount == 100
    assert result.payment_date is not None
    assert result.last_modified is not None
    assert result.modified_by == "payment_processor"
```

**Why It's Wrong**:
- Tests internal bookkeeping (last_modified)
- Implementation-coupled assertions
- Missing what actually matters to users

**Detection**:
- Assertions for every changed field
- Audit field testing (modified_by, timestamps)
- No focus on business-relevant outcomes

**Remediation**:
```python
def test_process_payment():
    order = Order()
    result = process_payment(order, 100)

    assert result.payment_status == "processed"
    assert result.payment_amount == 100
    # Don't test internal audit fields
```

### Anti-Pattern 6: Specification-Matching Tests

**Description**: AI writes tests that exactly match a specification or requirement document.

**Why It Happens**:
- AI follows instructions literally
- AI doesn't add creative edge cases
- AI doesn't think about what could go wrong

**Example**:
```markdown
Requirement: "User can log in with email and password"

AI Test:
def test_user_can_log_in_with_email_and_password():
    result = login("user@example.com", "password123")
    assert result.success == True
```

**Why It's Wrong**:
- Only tests happy path from spec
- Missing: wrong password, wrong email, SQL injection, etc.
- Test is too literal

**Detection**:
- Test names match requirement text exactly
- Only happy paths tested
- No edge cases or error cases

**Remediation**:
```python
def test_login_with_valid_credentials():
    result = login("user@example.com", "correct_password")
    assert result.success == True

def test_login_with_wrong_password():
    result = login("user@example.com", "wrong_password")
    assert result.success == False
    assert "invalid credentials" in result.error

def test_login_with_nonexistent_email():
    result = login("nobody@example.com", "password")
    assert result.success == False

def test_login_prevents_sql_injection():
    result = login("'; DROP TABLE users; --", "password")
    assert result.success == False
```

### Anti-Pattern 7: Confidence Without Verification

**Description**: AI claims tests pass without actually running them.

**Why It Happens**:
- AI generates syntactically correct code
- AI assumes logic is correct
- AI can't actually execute code

**Example**:
```markdown
AI: "I've written the test and implementation. The tests will pass."

[No test output shown]
[No verification performed]
```

**Why It's Wrong**:
- Tests might have syntax errors
- Logic might be wrong
- Dependencies might not exist

**Detection**:
- No test execution output in conversation
- Phrases like "should pass" or "will work"
- Missing verification step

**Remediation**:
- Always run tests before claiming success
- Show actual test output
- Verify both failure and success

## AI-Assisted TDD Guardrails

### Guardrail: Forced Verification

```markdown
Before claiming GREEN:
1. Run test suite
2. Capture output
3. Show pass/fail count
4. Only then proceed
```

### Guardrail: Separate Responses

```markdown
RED Response: Write test only
[Wait for verification]
GREEN Response: Write implementation only
[Wait for verification]
```

### Guardrail: Behavioral Focus Prompt

```markdown
When writing tests, ask:
- What does the user/caller observe?
- What outcome matters?
- NOT: What methods get called internally?
```

### Guardrail: Edge Case Expansion

```markdown
After happy path test, ask:
- What if input is empty/null?
- What if input is very large?
- What if operation fails?
- What if called twice?
```

## Detection Checklist

Use this checklist when reviewing AI-generated tests:

```
AI Anti-Pattern Detection:
□ Were test and implementation generated together?
□ Do tests mirror implementation structure?
□ Are there trivial getter/setter tests?
□ Are simple objects mocked?
□ Do assertions test all changed fields?
□ Are only happy paths tested?
□ Were tests verified by actual execution?
```

If any checkbox is marked, investigate further.

## Remediation Strategies

### For Developers

1. Review AI-generated tests critically
2. Ask AI to write test first, wait for failure
3. Request edge cases explicitly
4. Run tests before accepting

### For AI Tools

1. Enforce RED-GREEN-REFACTOR sequence
2. Require test failure verification
3. Separate test and implementation responses
4. Include edge case prompts automatically

### For Teams

1. Include AI anti-patterns in code review
2. Measure TDD compliance, not just coverage
3. Use mutation testing to verify test quality
4. Train on behavioral test writing
