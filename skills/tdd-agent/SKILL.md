---
name: tdd-agent
description: Fully autonomous TDD with strict guardrails. Use when you want the AI to drive the entire RED-GREEN-REFACTOR cycle independently while maintaining TDD discipline.
---

# TDD Agent (Autonomous Mode)

> "Make it work, make it right, make it fast — in that order."
> — Kent Beck

## Core Philosophy

The TDD Agent operates autonomously through the complete TDD cycle. Unlike pair programming, the AI drives all phases. **Stricter guardrails apply** because there's no human catching mistakes in real-time.

**Non-Negotiable Constraints:**
1. Every implementation MUST have a failing test first
2. Every test MUST be verified to fail before implementation
3. Every refactoring MUST maintain green tests
4. Every phase transition MUST be explicitly logged

## Kent Beck's 12 Test Desiderata (Agent Focus)

The agent must ensure tests have these properties:

| Property | Agent Responsibility |
|----------|---------------------|
| **Isolated** | Tests don't share state; verify no side effects |
| **Deterministic** | Same results every run; no flaky tests |
| **Specific** | Failures point to exact cause |
| **Automated** | No manual intervention required |
| **Predictive** | Passing tests = working code |
| **Fast** | Maintain quick feedback loop |

## Autonomous Protocol

### Phase 1: RED — Write Failing Test

```
RED Protocol:
1. Identify smallest testable behavior
2. Write test for that behavior
3. RUN the test suite
4. VERIFY the new test fails
5. VERIFY failure is for the expected reason
6. Only then, proceed to GREEN
```

**Mandatory Logging:**
```markdown
### RED Phase — Iteration N

**Behavior to test**: [description]
**Test written**: `test_name` in `file`

**Verification**:
```
[actual test output showing failure]
```

**Failure reason**: [e.g., "NameError: Calculator not defined"]
**Expected**: Yes, test fails because Calculator class doesn't exist yet

Proceeding to GREEN phase.
```

### Phase 2: GREEN — Minimal Implementation

```
GREEN Protocol:
1. Review the failing test
2. Identify minimal code to pass
3. Implement ONLY what's needed
4. RUN the test suite
5. VERIFY all tests pass
6. Only then, proceed to REFACTOR
```

**Mandatory Logging:**
```markdown
### GREEN Phase — Iteration N

**Test to satisfy**: `test_name`
**Implementation strategy**: [Fake It | Obvious | Triangulation]

**Code written**:
```[language]
[implementation code]
```

**Verification**:
```
[actual test output showing all pass]
```

All tests passing. Proceeding to REFACTOR phase.
```

### Phase 3: REFACTOR — Improve Structure

```
REFACTOR Protocol:
1. Confirm all tests pass
2. Identify ONE improvement
3. Make the change
4. RUN the test suite
5. VERIFY all tests still pass
6. If red, REVERT immediately
7. Repeat or proceed to next RED
```

**Mandatory Logging:**
```markdown
### REFACTOR Phase — Iteration N

**Starting state**: All tests passing (N tests)
**Improvement identified**: [e.g., "Extract duplicate calculation"]

**Change made**:
[brief description]

**Verification**:
```
[actual test output]
```

Refactoring complete. [Continue refactoring | Ready for next feature]
```

## Self-Check Loops

At each phase, the agent must run verification:

### RED Phase Self-Check

```
┌─────────────────────────────────────────────┐
│ RED Self-Check                              │
├─────────────────────────────────────────────┤
│ □ Test file exists                          │
│ □ Test is syntactically valid               │
│ □ Test suite runs without error             │
│ □ New test fails                            │
│ □ Failure is for expected reason            │
│ □ Only ONE new failing test                 │
│ □ Existing tests still pass                 │
└─────────────────────────────────────────────┘
```

If any check fails, stop and correct before proceeding.

### GREEN Phase Self-Check

```
┌─────────────────────────────────────────────┐
│ GREEN Self-Check                            │
├─────────────────────────────────────────────┤
│ □ Implementation is minimal                 │
│ □ No features beyond test requirements      │
│ □ Test suite runs without error             │
│ □ All tests pass                            │
│ □ New test passes                           │
│ □ No other tests broke                      │
└─────────────────────────────────────────────┘
```

### REFACTOR Phase Self-Check

```
┌─────────────────────────────────────────────┐
│ REFACTOR Self-Check                         │
├─────────────────────────────────────────────┤
│ □ Started with all tests passing            │
│ □ Made ONE small change                     │
│ □ Test suite runs without error             │
│ □ All tests still pass                      │
│ □ No behavior was changed                   │
│ □ Code is cleaner than before               │
└─────────────────────────────────────────────┘
```

## Guardrails

### Guardrail 1: No Implementation Without Failure Proof

Before writing ANY implementation code:

```
STOP! Verify:
1. A test exists for this behavior
2. The test was just run
3. The test output shows failure
4. The failure is logged in conversation

If any are missing, DO NOT PROCEED.
```

### Guardrail 2: Verify Before Claiming

Never claim tests pass/fail without evidence:

```
WRONG: "The test should now pass."
WRONG: "I believe all tests are passing."
RIGHT: "Running tests... [actual output] All 15 tests pass."
```

### Guardrail 3: Minimal Means Minimal

During GREEN, ask:
- Can I make this simpler?
- Am I adding anything the test doesn't require?
- Would a hardcoded value work?

If yes to any, simplify.

### Guardrail 4: Rollback on Red

If tests fail during REFACTOR:

```
IMMEDIATE ACTIONS:
1. Stop refactoring
2. Revert the change (git checkout or undo)
3. Verify tests pass again
4. Analyze what went wrong
5. Try smaller step
```

Do NOT try to "fix" the refactoring. Revert first.

### Guardrail 5: State Persistence

Always maintain explicit state:

```markdown
<tdd-state>
phase: [RED | GREEN | REFACTOR]
iteration: N
feature: [description]
current_test: [test name or none]
tests_passing: [true | false]
test_count: N
failing_count: N
last_verified: [timestamp or "just now"]
</tdd-state>
```

## Explicit Reasoning

The agent must explain decisions at each step:

```markdown
**Decision Point**: How to implement Calculator.add(2, 3)?

**Options**:
1. Return hardcoded 5 (Fake It)
2. Return a + b (Obvious Implementation)

**Reasoning**: This is the only test for addition. Obvious implementation
is safe because the algorithm is trivial (single expression, no edge cases).

**Choice**: Obvious Implementation
```

## Workflow Example

```markdown
## TDD Session: Calculator

Mode: Autonomous (tdd-agent)
Stack: Python

---

### RED Phase — Iteration 1

**Behavior**: Calculator can add two numbers

**Test**:
```python
# tests/test_calculator.py
def test_add_two_numbers():
    calc = Calculator()
    assert calc.add(2, 3) == 5
```

**Verification**:
```
$ pytest tests/test_calculator.py -v
E   NameError: name 'Calculator' is not defined
```

**Analysis**: Test fails as expected — Calculator class doesn't exist.

<tdd-state>
phase: GREEN
iteration: 1
feature: Addition
current_test: test_add_two_numbers
tests_passing: false
</tdd-state>

---

### GREEN Phase — Iteration 1

**Strategy**: Obvious Implementation (addition is trivial)

**Implementation**:
```python
# calculator.py
class Calculator:
    def add(self, a, b):
        return a + b
```

**Verification**:
```
$ pytest tests/test_calculator.py -v
test_calculator.py::test_add_two_numbers PASSED
```

All tests pass.

<tdd-state>
phase: REFACTOR
iteration: 1
tests_passing: true
</tdd-state>

---

### REFACTOR Phase — Iteration 1

**Check**: Code is simple, no smells detected.

**Decision**: No refactoring needed. Ready for next feature.

<tdd-state>
phase: RED
iteration: 2
</tdd-state>
```

## Output Templates

See [Guardrails Reference](references/guardrails.md) for detailed templates.
See [Autonomous Protocol](references/autonomous-protocol.md) for extended workflow examples.

## AI Discipline Rules

### CRITICAL: Trust Nothing Without Verification

- Don't assume tests pass
- Don't assume tests fail
- Don't assume code works
- Run and verify everything

### CRITICAL: Be Boringly Predictable

- Follow the protocol exactly
- Log everything explicitly
- Never skip steps
- Never combine steps

### CRITICAL: Fail Loudly

If something unexpected happens:
- Stop immediately
- Report the anomaly
- Ask for guidance if unclear
- Don't try to work around it

### CRITICAL: Prefer Smaller Steps

When in doubt:
- Smaller test
- Simpler implementation
- One refactoring at a time
- More iterations over fewer

## Error Recovery

### Tests Won't Run

```
Problem: Test suite errors out
Actions:
1. Check syntax of test file
2. Check imports and dependencies
3. Fix infrastructure issues
4. Do NOT write implementation until tests run
```

### Wrong Test Failure

```
Problem: Test fails but not for expected reason
Actions:
1. Examine the actual error
2. Fix the test if it has bugs
3. Ensure test setup is correct
4. Only proceed when failure is expected
```

### Can't Make Test Pass

```
Problem: Implementation seems correct but test fails
Actions:
1. Re-read the test carefully
2. Check for typos in test expectations
3. Verify test setup and assertions
4. Ask for help if stuck
```

### State Confusion

```
Problem: Unsure what phase we're in
Actions:
1. Run full test suite
2. If all pass: REFACTOR or new RED
3. If one fails: GREEN
4. Reconstruct state block from evidence
```
