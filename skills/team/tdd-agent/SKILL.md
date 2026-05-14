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

## Knowledge Base Lookups

Use `search_knowledge` (grounded-code-mcp) to ground decisions in authoritative references.

| Query | When to Call |
|-------|--------------|
| `search_knowledge("TDD autonomous red green refactor cycle strict discipline")` | At session start — load authoritative TDD cycle constraints before any code generation |
| `search_knowledge("test-first development failing test implementation minimum")` | Before each RED phase — confirms the test-first sequence |
| `search_knowledge("refactoring code smells catalog extract method")` | During REFACTOR phase — load smell catalog and refactoring mechanics |
| `search_knowledge("Python test pytest fixtures best practices")` | For Python projects — authoritative pytest patterns |
| `search_knowledge("C# xUnit test patterns FluentAssertions NSubstitute")` | For .NET projects — authoritative xUnit/FluentAssertions patterns |
| `search_knowledge("unit test naming conventions behavior specification")` | When naming tests — confirms behavioral naming standards |

**Protocol:** Search before each phase transition (RED→GREEN→REFACTOR). Cite the source path in phase logs.

## Kent Beck's 12 Test Desiderata (Agent Focus)

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

**Verification**: [actual test output showing failure]
**Failure reason**: [e.g., "NameError: Calculator not defined"]

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
**Code written**: [implementation code]

**Verification**: [actual test output showing all pass]

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
**Change made**: [brief description]

**Verification**: [actual test output]

Refactoring complete. [Continue refactoring | Ready for next feature]
```

## Self-Check Loops

Run these checklists at each phase transition. Stop and correct if any item fails.

**RED Self-Check:**
- [ ] Test file exists and is syntactically valid
- [ ] Test suite runs without error
- [ ] New test fails for the expected reason
- [ ] Only ONE new failing test
- [ ] Existing tests still pass

**GREEN Self-Check:**
- [ ] Implementation is minimal — no features beyond test requirements
- [ ] All tests pass
- [ ] No other tests broke

**REFACTOR Self-Check:**
- [ ] Started with all tests passing
- [ ] Made ONE small change
- [ ] All tests still pass
- [ ] No behavior was changed — only structure

## Guardrails

**Guardrail 1 — No Implementation Without Failure Proof:** Before writing any implementation code, verify a test exists for the behavior, it was just run, output shows failure, and the failure is logged. If any item is missing, stop.

**Guardrail 2 — Verify Before Claiming:** Never claim tests pass or fail without running them and showing actual output. Show `[actual test output] All 15 tests pass` — not "the test should now pass."

**Guardrail 3 — Minimal Means Minimal:** During GREEN, ask: can I make this simpler? Am I adding anything the test doesn't require? Would a hardcoded value pass? If yes to any, simplify.

**Guardrail 4 — Rollback on Red:** If tests fail during REFACTOR, stop, revert the change immediately, verify tests pass again, then try a smaller step. Never fix a broken refactor forward.

## State Block

```
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

At each decision point, log options, reasoning, and choice before acting:

```markdown
**Decision Point**: How to implement Calculator.add(2, 3)?

**Options**:
1. Return hardcoded 5 (Fake It)
2. Return a + b (Obvious Implementation)

**Reasoning**: Single test for addition. Obvious implementation is safe — trivial algorithm, no edge cases.

**Choice**: Obvious Implementation
```

## Workflow Example

RED → GREEN → REFACTOR for `Calculator.add()` (Python):

**RED**: Write `test_add_two_numbers`, run pytest — `NameError: Calculator not defined`. Log failure. Update state: `phase: GREEN, iteration: 1`.

**GREEN**: Implement `class Calculator: def add(self, a, b): return a + b`. Run pytest — 1 passed. Update state: `phase: REFACTOR`.

**REFACTOR**: No smells detected. Code is minimal. No refactoring needed. Update state: `phase: RED, iteration: 2`.

Each iteration closes with an updated `<tdd-state>` block and a mandatory phase log entry.

## Output Templates

See [Guardrails Reference](references/guardrails.md) for detailed phase log templates.
See [Autonomous Protocol](references/autonomous-protocol.md) for extended workflow examples.

## AI Discipline Rules

**CRITICAL: Trust Nothing Without Verification** — Don't assume tests pass, don't assume tests fail, don't assume code works. Run and verify everything.

**CRITICAL: Be Boringly Predictable** — Follow the protocol exactly. Log everything explicitly. Never skip steps. Never combine steps.

**CRITICAL: Fail Loudly** — If something unexpected happens: stop immediately, report the anomaly, ask for guidance. Do not work around it.

**CRITICAL: Prefer Smaller Steps** — When in doubt: smaller test, simpler implementation, one refactoring at a time, more iterations over fewer.

## Integration with Other Skills

- **`tdd-cycle`** — Orchestrates the phase state machine; invoke at session start to configure mode (autonomous vs. pair) and manage transitions
- **`tdd-implementer`** — Called during GREEN phase for implementation strategy selection (Fake It / Obvious / Triangulation)
- **`tdd-refactor`** — Called during REFACTOR phase for smell identification and safe step-by-step improvement
- **`tdd-verify`** — Run after the session to audit TDD compliance, score commit history, and identify anti-patterns
- **`tdd-pair`** — Alternative to this skill; use when a human partner drives and the AI navigates

## Error Recovery

**Tests Won't Run:** Check syntax and imports in the test file. Fix infrastructure issues first. Do not write any implementation until the test suite runs cleanly.

**Wrong Test Failure:** Examine the actual error message — not the expected one. Fix the test if it has bugs. Proceed only when the failure is the expected one.

**Can't Make Test Pass:** Re-read the test carefully. Check for typos in expectations. Verify setup and assertions. Ask for help if stuck — do not guess at the implementation.

**State Confusion:** Run the full test suite. If all pass: begin REFACTOR or new RED. If one fails: you are in GREEN. Reconstruct the state block from observed evidence.
