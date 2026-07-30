# State Management Reference

## State Block Specification

The state block persists TDD context across conversation turns.

### Full State Block Schema

```
<tdd-state>
phase: RED | GREEN | REFACTOR
iteration: [positive integer]
feature: [string, brief description of feature being developed]
current_test: [string, test name or file:testname format]
tests_passing: true | false | unknown
test_count: [integer, total tests in suite]
failing_count: [integer, number of failing tests]
last_action: [string, what was just completed]
next_action: [string, what should happen next]
blockers: [string, "none" or description of issues]
stack: [string, e.g., "dotnet", "python", "typescript"]
mode: autonomous | pair
last_run: [ISO timestamp of last test run]
</tdd-state>
```

### Minimal State Block

For simpler sessions, use the minimal version:

```
<tdd-state>
phase: RED
iteration: 1
feature: User authentication
current_test: none
tests_passing: unknown
last_action: Session start
next_action: Write first failing test
blockers: none
</tdd-state>
```

## State Transitions

### Initializing State

When starting a new TDD session:

```
<tdd-state>
phase: RED
iteration: 1
feature: [from user request]
current_test: none
tests_passing: unknown
last_action: Session initialized
next_action: Identify smallest testable behavior
blockers: none
</tdd-state>
```

### After Writing a Test (RED)

```
<tdd-state>
phase: RED
iteration: 1
feature: User authentication
current_test: test_login_with_valid_credentials
tests_passing: false
test_count: 15
failing_count: 1
last_action: Wrote test for valid login
next_action: Verify test fails for right reason, then implement
blockers: none
</tdd-state>
```

### After Test Verification (RED → GREEN)

```
<tdd-state>
phase: GREEN
iteration: 1
feature: User authentication
current_test: test_login_with_valid_credentials
tests_passing: false
test_count: 15
failing_count: 1
last_action: Verified test fails with "LoginService not implemented"
next_action: Implement minimal code to pass test
blockers: none
</tdd-state>
```

### After Implementation (GREEN → REFACTOR)

```
<tdd-state>
phase: REFACTOR
iteration: 1
feature: User authentication
current_test: test_login_with_valid_credentials
tests_passing: true
test_count: 15
failing_count: 0
last_action: Implemented LoginService.login() method
next_action: Look for refactoring opportunities
blockers: none
</tdd-state>
```

### After Refactoring (REFACTOR → RED)

```
<tdd-state>
phase: RED
iteration: 2
feature: User authentication
current_test: none
tests_passing: true
test_count: 15
failing_count: 0
last_action: Extracted password hashing to separate method
next_action: Write test for next behavior (invalid credentials)
blockers: none
</tdd-state>
```

## State Recovery

### When State is Missing

If the state block is not found in recent messages:

1. **Check test suite**:
   ```bash
   # Run tests to determine current state
   dotnet test  # or pytest, npm test
   ```

2. **Examine recent files**:
   - Look at most recently modified test files
   - Look at most recently modified source files
   - Check git status for uncommitted changes

3. **Reconstruct state**:
   - If tests pass: likely in REFACTOR or between cycles
   - If exactly one test fails: likely in GREEN
   - If no new tests: likely in RED (test not written yet)

### State Validation

Before acting on state, validate:

```
Validation Checklist:
├── phase is valid enum value?
├── iteration is positive integer?
├── If phase=GREEN, current_test is set?
├── If phase=GREEN, tests_passing=false?
├── If phase=REFACTOR, tests_passing=true?
├── feature matches current work?
```

## Multi-Feature Sessions

When working on multiple features or taking breaks:

### Suspending Work

```
<tdd-state>
phase: GREEN
iteration: 2
feature: User authentication
current_test: test_login_with_invalid_password
tests_passing: false
last_action: Wrote test for invalid password case
next_action: [SUSPENDED] Resume by implementing rejection logic
blockers: Taking break, will resume later
</tdd-state>
```

### Resuming Work

1. Locate the last state block
2. Verify current codebase matches state
3. Run tests to confirm test_passing status
4. Continue from next_action

## State in Pair Programming

During pair programming, state helps handoff between human and AI:

```
<tdd-state>
phase: RED
iteration: 3
feature: Shopping cart
current_test: none
tests_passing: true
last_action: Human completed refactoring
next_action: AI writes next test (human's turn to implement)
mode: pair
pair_role: AI=test_writer, Human=implementer
blockers: none
</tdd-state>
```

## Common State Errors

| Error | Cause | Fix |
|-------|-------|-----|
| phase=GREEN but tests_passing=true | Forgot to update after running tests | Re-run tests, update state |
| iteration stays at 1 | Forgot to increment on new cycle | Increment when entering RED |
| current_test is stale | Didn't clear after cycle complete | Set to "none" in new RED |
| blockers not cleared | Didn't update after resolving | Clear when no longer blocked |
