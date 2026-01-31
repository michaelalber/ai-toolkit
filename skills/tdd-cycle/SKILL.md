---
name: tdd-cycle
description: Orchestrate RED-GREEN-REFACTOR TDD phases. Use when starting TDD, managing phase transitions, or maintaining TDD discipline across a development session.
---

# TDD Cycle Orchestrator

> "The goal is clean code that works. First we make it work, then we make it clean."
> — Ron Jeffries

## Core Philosophy

This skill coordinates the canonical TDD cycle: **RED → GREEN → REFACTOR**. It maintains phase state, enforces transitions, and prevents the AI from "helping" by skipping phases.

**The cycle is non-negotiable:**
1. **RED**: Write a failing test that defines desired behavior
2. **GREEN**: Write minimal code to make the test pass
3. **REFACTOR**: Improve code structure while keeping tests green

## Kent Beck's 12 Test Desiderata

Use this framework to evaluate test quality at every phase:

| Property | Description | Priority |
|----------|-------------|----------|
| **Isolated** | Tests don't affect each other | Critical |
| **Composable** | Can run any subset of tests | High |
| **Deterministic** | Same result every time | Critical |
| **Specific** | Failure points to cause | High |
| **Behavioral** | Tests behavior, not implementation | High |
| **Structure-insensitive** | Refactoring doesn't break tests | High |
| **Fast** | Quick feedback loop | Medium |
| **Writable** | Easy to create new tests | Medium |
| **Readable** | Easy to understand intent | High |
| **Automated** | No manual intervention | Critical |
| **Predictive** | Passing tests = working code | High |
| **Inspiring** | Confidence to make changes | Medium |

## Workflow

### Phase State Machine

```
┌─────────────────────────────────────────────────────┐
│                                                     │
│    ┌─────┐      ┌───────┐      ┌──────────┐        │
│ ──►│ RED │─────►│ GREEN │─────►│ REFACTOR │────┐   │
│    └─────┘      └───────┘      └──────────┘    │   │
│        ▲                                       │   │
│        └───────────────────────────────────────┘   │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### State Block Format

Maintain state across conversation turns using this block:

```
<tdd-state>
phase: RED | GREEN | REFACTOR
iteration: [number]
feature: [brief description]
current_test: [test name or "none"]
tests_passing: [true | false | unknown]
last_action: [what was just done]
next_action: [what should happen next]
blockers: [any issues preventing progress]
</tdd-state>
```

### Phase Transitions

#### RED Phase Entry
**Preconditions:**
- Previous cycle complete OR starting new feature
- Clear understanding of desired behavior

**Actions:**
1. Identify the smallest testable behavior increment
2. Write ONE failing test
3. Run test suite, verify new test fails
4. Document expected vs actual behavior

**Exit Criteria:**
- Exactly one new failing test
- Test failure is for the RIGHT reason (not syntax/import errors)
- Test clearly expresses intended behavior

#### GREEN Phase Entry
**Preconditions:**
- RED phase complete
- Exactly one failing test exists
- Failure reason is verified

**Actions:**
1. Write MINIMAL code to pass the test
2. No additional functionality
3. "Fake it till you make it" is acceptable
4. Run tests, verify all pass

**Exit Criteria:**
- All tests pass (including the new one)
- No more code than necessary was written

#### REFACTOR Phase Entry
**Preconditions:**
- GREEN phase complete
- All tests passing
- Code works but may not be clean

**Actions:**
1. Identify code smells or duplication
2. Make ONE small improvement
3. Run tests after EACH change
4. Repeat until satisfied

**Exit Criteria:**
- All tests still pass
- Code is cleaner/clearer
- No behavior changes

### Mode Selection

At session start, determine the mode:

**Autonomous Mode** (`tdd-agent`):
- AI drives all phases
- Stricter verification requirements
- Explicit reasoning at each step

**Pair Mode** (`tdd-pair`):
- Human and AI collaborate
- Role negotiation (driver/navigator, ping-pong)
- More conversational flow

## Output Templates

### Session Start
```markdown
## TDD Session: [Feature Name]

**Mode**: [Autonomous | Pair]
**Stack**: [Language/Framework]

<tdd-state>
phase: RED
iteration: 1
feature: [description]
current_test: none
tests_passing: unknown
last_action: Session initialized
next_action: Write first failing test
blockers: none
</tdd-state>

### RED Phase - Iteration 1

I'll write a test for: [specific behavior]
```

### Phase Transition
```markdown
### Phase Complete: [PHASE]

**What was accomplished:**
- [bullet points]

**Verification:**
- Tests run: [yes/no]
- Result: [pass/fail with count]

<tdd-state>
phase: [NEXT_PHASE]
...
</tdd-state>

### [NEXT_PHASE] Phase - Iteration [N]

Next step: [action]
```

## AI Discipline Rules

### CRITICAL: Never Skip RED

Before writing ANY implementation code, verify:
1. A failing test exists for the feature
2. The test actually fails when run
3. The failure is for the expected reason

If no failing test exists, STOP and write one first.

### CRITICAL: Minimal GREEN

During GREEN phase:
- Write the LEAST code possible to pass the test
- "Obvious implementation" is fine for trivial cases
- Prefer "fake it" over "build it" when uncertain
- Adding features not covered by tests is FORBIDDEN

### CRITICAL: Green-to-Green Refactoring

During REFACTOR phase:
- Run tests before AND after each change
- If tests fail, immediately revert
- One refactoring at a time
- No new functionality during refactoring

### CRITICAL: State Verification

Before any phase transition:
1. Run the test suite
2. Verify expected results
3. Update state block
4. Only then proceed

### CRITICAL: Resist "Helpfulness"

The AI must NOT:
- Write tests AND implementation together
- Add "while I'm here" improvements during GREEN
- Skip refactoring because "the code is simple"
- Assume tests pass without running them

## Stack-Specific Guidance

See reference files for stack-specific patterns:
- [Phase Transitions](references/phase-transitions.md) - Detailed transition logic
- [State Management](references/state-management.md) - Persisting state across turns

## Integration with Other Skills

- **RED phase** → Use domain knowledge to write meaningful tests
- **GREEN phase** → Invoke `tdd-implementer` for implementation
- **REFACTOR phase** → Invoke `tdd-refactor` for safe improvements
- **Autonomous mode** → Delegate to `tdd-agent`
- **Pair mode** → Delegate to `tdd-pair`
- **Verification** → Invoke `tdd-verify` for compliance check

## Common Anti-Patterns to Avoid

| Anti-Pattern | Why It's Wrong | Correct Approach |
|--------------|----------------|------------------|
| Test after code | Tests become verification, not specification | Always RED first |
| Multiple features per cycle | Loses precision, harder to debug | One behavior at a time |
| Skipping refactor | Technical debt accumulates | Always evaluate for cleanup |
| Gold-plating in GREEN | Violates minimal implementation | Save improvements for REFACTOR |
| Tests that test implementation | Brittle, break on refactor | Test behavior only |

## Recovery Procedures

### If Tests Pass Unexpectedly in RED
The test is likely:
1. Testing existing behavior (duplicate)
2. Not testing what you think
3. Has a bug in the test itself

**Action**: Examine the test, strengthen assertions, or find the actual gap.

### If Tests Fail in REFACTOR
1. Immediately revert the last change
2. Analyze why the refactoring broke behavior
3. Consider smaller steps or different approach

### If State is Lost
1. Run the full test suite
2. Examine recent changes
3. Reconstruct state block from evidence
4. Resume at appropriate phase
