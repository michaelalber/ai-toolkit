# Verification Failure Guide

How to diagnose and respond to build/test failures during implementation.

## Decision tree: what to do when verification fails

```
Verification fails during Phase N
            |
            v
    Is the failure caused by Phase N's changes?
            |
    YES ----+---- NO
    |               |
    v               v
Is the fix     Report to user:
described      "This may be a pre-existing
in the plan?   failure. Please verify and
    |          advise how to proceed."
YES -+- NO     Stop -- do not continue.
|       |
v       v
Apply   Is the fix
fix,    a simple
re-     mechanical
verify  correction?
    |
YES -+- NO
|       |
v       v
Apply   STOP. Report:
and     "Plan gap found.
verify  Use /rpi-iterate."
```

## Failure type classification

### Type 1: Simple compilation error from plan change

**Symptoms:** Build fails with CS error pointing to a file you just modified.

**Common causes:**
- Missing `using` statement for new type
- Method signature mismatch (plan described slightly different parameters)
- Null reference in constructor (new dependency not initialized)

**Response:**
1. Check if adding a `using` or adjusting the signature matches what the plan intended
2. If yes: apply the minimal fix, re-verify, note the correction in the progress summary
3. If the fix requires understanding something not in the plan: STOP, report as plan gap

### Type 2: Test failure from changed behavior

**Symptoms:** Tests that previously passed now fail because behavior changed.

**Common causes:**
- New dependency injection requirement breaks test setup
- Changed method signature breaks existing test calls
- New validation rejects previously-valid test data

**Response:**
1. Read the failing test to understand what it is verifying
2. Is the test verifying behavior that the plan intentionally changed?
   - YES: Update the test to match the new behavior (this is expected)
   - NO: The plan may have unintended side effects — STOP and report
3. Is the test setup missing the new dependency?
   - YES: Add the mock/fake (if the test pattern in the research artifact supports it)
   - NO: STOP and report

### Type 3: Pre-existing test failure

**Symptoms:** Tests fail that are completely unrelated to the current phase's files.

**Response:**
1. Verify by checking: does the failing test file appear anywhere in the plan?
2. If NO: This is a pre-existing failure. Report to user:
   > "The following test failures appear to be pre-existing and unrelated to Phase N:
   > [list of tests]
   > Please confirm these were failing before implementation started. I will stop until confirmed."
3. Do NOT assume failures are pre-existing without checking the plan

### Type 4: Migration failure

**Symptoms:** `dotnet ef database update` or `dotnet ef migrations add` fails.

**Common causes:**
- Conflicting migration names
- Model snapshot out of sync
- Database connection not available in test environment

**Response:**
1. Show the full EF Core error output
2. Check if the plan specified the exact migration command — compare with what you ran
3. For model snapshot issues: this is a plan gap — the plan should have included snapshot repair steps
4. For connection issues: report to user, do not continue
5. STOP if the fix requires anything not described in the plan

### Type 5: Format/lint failure

**Symptoms:** `dotnet format --verify-no-changes` or `ruff check` fails.

**Response:**
1. Run the auto-format command to see what needs fixing: `dotnet format` or `ruff format .`
2. If the changes are purely stylistic (whitespace, import ordering): apply and re-verify
3. If the formatter requires substantive changes that affect logic: STOP and report
4. Note: format fixes are always safe to apply as they are deterministic

## Reporting a plan gap

When a failure requires plan changes, use this format:

```
Phase N verification FAILED with a plan gap.

Error:
[exact error output]

Root cause:
[Analysis — what the error means]

Gap identified:
The plan does not address [specific missing step]. To fix this, the plan needs to:
[Description of what Phase N or an earlier phase should have included]

Please run:
/rpi-iterate "Phase N verification failed because [gap]. Plan needs to [fix]."
```

## What you are allowed to fix without stopping

| Fix | Allowed | Notes |
|-----|---------|-------|
| Add missing `using` statement | YES | Mechanical, always required when adding new types |
| Fix typo in a string literal | YES | If the plan describes the string content |
| Add mock for new injected dependency in tests | YES | If the test pattern (NSubstitute/Moq) is in research |
| Run `dotnet format` auto-fix | YES | Deterministic, no logic changes |
| Change from `var` to explicit type | YES | If linter/format demands it |
| Change method visibility from `private` to `internal` | NO | Logic decision; stop and report |
| Add error handling not in the plan | NO | Plan gap; stop and report |
| Change algorithm or logic | NO | Stop and report |
| Add new files not in the plan | NO | Stop and report |
