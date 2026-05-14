# Guardrails Reference

## Guardrail Implementation Details

### Guardrail 1: Failure Verification Gate

**Purpose**: Prevent the most common AI TDD violation — implementing without a failing test.

**Implementation**:

```
Before ANY implementation code:

GATE CHECK:
┌─────────────────────────────────────────────────────────┐
│ 1. Test file path: ____________________                 │
│ 2. Test function name: ____________________             │
│ 3. Test output captured: □ Yes  □ No                    │
│ 4. Test shows failure: □ Yes  □ No                      │
│ 5. Failure reason matches expected: □ Yes  □ No         │
└─────────────────────────────────────────────────────────┘

If ANY checkbox is "No" → STOP. Do not implement.
```

**Violation Response**:

If the AI attempts to write implementation without completing the gate:

```markdown
⚠️ TDD VIOLATION DETECTED

Attempted to write implementation without verified failing test.

**Required Actions**:
1. Delete/revert the implementation code
2. Write the test first
3. Run the test and capture output
4. Verify failure before proceeding

**Reason**: TDD requires RED before GREEN. No exceptions.
```

### Guardrail 2: Evidence-Based Claims

**Purpose**: Prevent hallucinated test results.

**Implementation**:

Every claim about test status must include evidence:

```markdown
# WRONG (no evidence)
"I've implemented the feature and tests pass."

# WRONG (assumed result)
"The test should pass now."

# RIGHT (with evidence)
"Running tests:
```
$ pytest tests/test_feature.py -v
tests/test_feature.py::test_new_feature PASSED
1 passed in 0.03s
```
All tests pass."
```

**Verification Pattern**:

```
Claim: [statement about test result]
Evidence: [actual command output]
Conclusion: [interpretation based on evidence]
```

### Guardrail 3: Minimality Checker

**Purpose**: Prevent over-engineering during GREEN phase.

**Checklist Before Completing GREEN**:

```
Minimality Self-Check:
┌────────────────────────────────────────────────────────────────┐
│ □ Does the implementation use only what the test checks?       │
│ □ Would a simpler/hardcoded solution work for current tests?   │
│ □ Did I add error handling not required by tests?              │
│ □ Did I add validation not required by tests?                  │
│ □ Did I add logging/comments not required by tests?            │
│ □ Did I handle edge cases not covered by tests?                │
│ □ Did I add parameters/configuration not required?             │
│ □ Did I create abstractions not required?                      │
└────────────────────────────────────────────────────────────────┘

If ANY box is checked → SIMPLIFY before proceeding.
```

**Violation Examples**:

```python
# Test
def test_greet_returns_hello():
    assert greet("Alice") == "Hello, Alice!"

# VIOLATION: Over-engineered
def greet(name, greeting="Hello", punctuation="!"):
    if not name:
        raise ValueError("Name required")
    if not isinstance(name, str):
        raise TypeError("Name must be string")
    return f"{greeting}, {name}{punctuation}"

# CORRECT: Minimal
def greet(name):
    return f"Hello, {name}!"
```

### Guardrail 4: Rollback Protocol

**Purpose**: Ensure refactoring failures are handled correctly.

**When Tests Fail During Refactor**:

```
ROLLBACK PROTOCOL - EXECUTE IMMEDIATELY

Step 1: STOP
   └─ Do not attempt to fix the refactoring
   └─ Do not add more code

Step 2: REVERT
   Option A (Git): git checkout -- <file>
   Option B (IDE): Undo (Ctrl+Z / Cmd+Z) until green
   Option C (Manual): Restore from backup/previous version

Step 3: VERIFY
   └─ Run tests
   └─ Confirm all pass
   └─ Capture evidence

Step 4: ANALYZE
   └─ Why did the refactoring break tests?
   └─ Was the change too large?
   └─ Did it actually change behavior?

Step 5: RETRY (smaller)
   └─ Break refactoring into smaller steps
   └─ Execute each step with test verification
```

**Anti-Pattern to Avoid**:

```
# WRONG
1. Refactor code
2. Tests fail
3. "Fix" the refactoring
4. Tests still fail
5. Modify more code
6. Eventually tests pass but behavior changed

# RIGHT
1. Refactor code
2. Tests fail
3. IMMEDIATELY revert
4. Analyze
5. Try smaller refactoring
```

### Guardrail 5: State Integrity

**Purpose**: Maintain clear context across conversation turns.

**State Block Requirements**:

```markdown
<tdd-state>
# Required fields (always present)
phase: RED | GREEN | REFACTOR
iteration: [positive integer]
feature: [string describing current feature]
tests_passing: true | false | unknown

# Conditional fields
current_test: [test name when in GREEN, "none" otherwise]
test_count: [integer, from last run]
failing_count: [integer, from last run]
last_verified: [description of last verification]

# Error state (when applicable)
error: [description of current blocker]
recovery_action: [what needs to happen]
</tdd-state>
```

**State Validation Rules**:

| Phase | tests_passing | current_test | Valid? |
|-------|--------------|--------------|--------|
| RED | false | test name | Yes |
| RED | true | none | Yes (writing test) |
| RED | true | test name | No (should be GREEN) |
| GREEN | false | test name | Yes |
| GREEN | true | test name | No (should be REFACTOR) |
| REFACTOR | true | any | Yes |
| REFACTOR | false | any | No (should revert) |

**State Corruption Recovery**:

```
If state seems wrong:
1. Run full test suite
2. Count passing/failing
3. Identify current test (if any failing)
4. Reconstruct state from evidence
5. Log the recovery
```

## Guardrail Enforcement

### Self-Monitoring

The agent should check guardrails at these points:

| Checkpoint | Guardrails to Check |
|------------|---------------------|
| Before writing test | State integrity |
| After writing test | Failure verification |
| Before implementation | Failure verification |
| After implementation | Evidence-based claims, Minimality |
| Before refactoring | Evidence-based claims, State integrity |
| After refactoring | Rollback readiness, Evidence-based claims |

### Violation Severity

| Level | Examples | Response |
|-------|----------|----------|
| Critical | Implementing without failing test | Full stop, revert, explain |
| High | Claiming tests pass without evidence | Stop, run tests, log evidence |
| Medium | Over-engineering in GREEN | Note violation, simplify |
| Low | Missing state update | Update state, continue |

### Escalation

If guardrails cannot be maintained:

```markdown
⚠️ GUARDRAIL BREACH - ESCALATING

**Issue**: [description]
**Guardrail**: [which one]
**Attempted Resolution**: [what was tried]

**Requesting Human Guidance**:
[specific question or decision needed]

Session paused until guidance received.
```
