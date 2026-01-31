# Phase Transitions Reference

## Detailed Transition Logic

### RED → GREEN Transition

```
Precondition Check:
├── Test file exists?
│   └── NO → Cannot transition, need test first
│   └── YES → Continue
├── Test suite runs without errors?
│   └── NO → Fix syntax/import issues first
│   └── YES → Continue
├── Exactly one NEW failing test?
│   └── NO → Adjust (too many or none failing)
│   └── YES → Continue
├── Failure is for expected reason?
│   └── NO → Test may be wrong, review
│   └── YES → Transition approved
```

**Verification Commands by Stack:**

```bash
# .NET
dotnet test --filter "FullyQualifiedName~TestName" --no-build

# Python (pytest)
pytest -x -v tests/test_file.py::test_name

# TypeScript (Jest)
npm test -- --testNamePattern="test name" --bail
```

### GREEN → REFACTOR Transition

```
Precondition Check:
├── All tests passing?
│   └── NO → Still in GREEN, fix implementation
│   └── YES → Continue
├── Implementation exists for the test?
│   └── NO → Still in GREEN, implement
│   └── YES → Continue
├── Code committed/saved?
│   └── NO → Save working state first
│   └── YES → Transition approved
```

### REFACTOR → RED Transition

```
Precondition Check:
├── All tests still passing?
│   └── NO → Stay in REFACTOR, fix or revert
│   └── YES → Continue
├── Refactoring complete?
│   └── NO → Continue refactoring
│   └── YES → Continue
├── More features needed?
│   └── NO → Cycle complete, exit or wait
│   └── YES → Transition to RED
```

## Transition Verification Protocol

Before ANY transition, execute this checklist:

1. **Run test suite**: Execute all tests, not just the new one
2. **Capture output**: Record test results for state block
3. **Verify expectations**: Match results to phase requirements
4. **Update state**: Modify state block with new phase
5. **Announce transition**: Clearly communicate phase change

## Edge Cases

### Multiple Failing Tests

**Situation**: More than one test fails after writing a new test.

**Diagnosis**:
- Did you break existing functionality?
- Are tests properly isolated?
- Is there a shared state issue?

**Resolution**:
1. Revert new test temporarily
2. Verify existing tests pass
3. If they don't, fix that first
4. If they do, examine test isolation

### Flaky Tests

**Situation**: Tests sometimes pass, sometimes fail.

**Diagnosis**:
- Time-dependent code?
- External service dependency?
- Race condition?
- Shared mutable state?

**Resolution**:
1. Identify the source of non-determinism
2. Mock external dependencies
3. Control time in tests
4. Ensure test isolation

### Test Passes Immediately

**Situation**: New test passes without writing any code.

**Diagnosis**:
- Feature already implemented?
- Test is too weak?
- Test has a bug (always passes)?

**Resolution**:
1. Verify test actually exercises new behavior
2. Add stronger assertions
3. Comment out implementation, verify failure
4. If truly implemented, pick different behavior to test

## Phase Duration Guidelines

| Phase | Typical Duration | Warning Signs |
|-------|------------------|---------------|
| RED | 1-5 minutes | Spending too long means test is too big |
| GREEN | 1-10 minutes | Long GREEN means implementation is too complex |
| REFACTOR | 0-15 minutes | Can be skipped if code is clean |

**If stuck in any phase for too long**:
- Consider breaking down the current behavior
- The test may be testing too much at once
- Step back and reassess
