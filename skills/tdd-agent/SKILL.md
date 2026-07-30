---
name: tdd-agent
audience: team
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

Kent Beck's 12 Test Desiderata (agent responsibilities) and the per-phase knowledge-base lookup protocol live in `references/knowledge-lookups.md` — consult it at session start and before each phase transition.

## Knowledge Base Lookups

Use `search_knowledge` (grounded-code-mcp) to ground decisions in authoritative references. Search before each phase transition (RED→GREEN→REFACTOR) and cite the source path in phase logs. The full query→trigger table and the Kent Beck desiderata are in `references/knowledge-lookups.md`.

## Workflow

Drive each behavior through three phases. Run and verify after every step — never assume.

```
RED — Write Failing Test
1. Identify smallest testable behavior
2. Write test for that behavior
3. RUN the test suite
4. VERIFY the new test fails
5. VERIFY failure is for the expected reason
6. Only then, proceed to GREEN
```

```
GREEN — Minimal Implementation
1. Review the failing test
2. Identify minimal code to pass
3. Implement ONLY what's needed
4. RUN the test suite
5. VERIFY all tests pass
6. Only then, proceed to REFACTOR
```

```
REFACTOR — Improve Structure
1. Confirm all tests pass
2. Identify ONE improvement
3. Make the change
4. RUN the test suite
5. VERIFY all tests still pass
6. If red, REVERT immediately
7. Repeat or proceed to next RED
```

Run the RED/GREEN/REFACTOR self-check at each transition; stop and correct if any item fails. The full self-check lists, the mandatory phase-log templates, and the explicit-reasoning template are in `references/guardrails.md`. A complete multi-iteration worked example (user-service feature) and a minimal Calculator walkthrough are in `references/autonomous-protocol.md`.

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

Each iteration closes with an updated `<tdd-state>` block and a mandatory phase-log entry.

## Output Template

- **Phase logs** (RED / GREEN / REFACTOR markdown templates) — `references/guardrails.md`.
- **Explicit reasoning** (options → reasoning → choice at each decision point) — `references/guardrails.md`.
- **Session init, worked iteration example, completion summary** — `references/autonomous-protocol.md`.

## Guardrails

Four hard gates — see `references/guardrails.md` for implementation detail, violation responses, and the severity table.

1. **No Implementation Without Failure Proof** — verify a test exists, was just run, output shows failure, and the failure is logged. If any is missing, stop.
2. **Verify Before Claiming** — never claim a test passes or fails without running it and showing actual output.
3. **Minimal Means Minimal** — during GREEN, if a simpler or hardcoded solution would pass, simplify.
4. **Rollback on Red** — if tests fail during REFACTOR, revert immediately; never fix a broken refactor forward.

The AI discipline rules (Trust Nothing, Be Boringly Predictable, Fail Loudly, Prefer Smaller Steps) are in `references/guardrails.md`.

## Integration with Other Skills

This skill is an *operating mode* of the canonical `tdd` loop, not a replacement for it.

- **`tdd`** — The canonical inner loop this mode drives. Defines the two critical test properties (behavioral, structure-insensitive), the per-cycle self-check, the GREEN strategies (Fake It / Obvious / Triangulation, with per-language idioms in its `references/`), and the REFACTOR smell catalog (the `tdd` skill's `references/code-smells.md` and `references/refactoring-catalog.md`). Load those on demand during GREEN/REFACTOR.
- **`evaluate-tests`** — Run after the session to audit test quality and TDD compliance (commit-history scorecard, anti-pattern detection).

## Error Recovery

Common recovery cases (tests won't run, wrong test failure, can't make test pass, state confusion) and their step-by-step protocols are in `references/autonomous-protocol.md`. In every case: fix infrastructure before writing implementation, examine the actual error not the expected one, and reconstruct the state block from a full test-suite run when state is unclear.
