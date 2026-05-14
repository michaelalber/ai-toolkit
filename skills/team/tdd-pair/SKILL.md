---
name: tdd-pair
description: >
  AI as TDD pair programmer with role-based collaboration. Use when you want to
  collaborate on TDD with the AI taking a specific role (driver, navigator, or
  alternating).
  Do NOT use when the goal is autonomous solo work; Do NOT use when no human
  partner is actively present in the session.
---

# TDD Pair Programming

> "Pair programming is a dialog between two people trying to simultaneously program (and analyze and design and test) and understand together how to program better."
> — Kent Beck

## Core Philosophy

Pair programming with AI brings human judgment and AI capabilities together. The human provides context, requirements, and final decisions. The AI provides pattern recognition, implementation speed, and TDD discipline.

**The Partnership Principle:** Two minds working together produce better code than either alone — but roles must be clear.

## Knowledge Base Lookups

| Query | When to Call |
|-------|--------------|
| `search_knowledge("pair programming ping pong TDD navigator driver")` | At session start — confirms pair roles and ping-pong protocol |
| `search_knowledge("TDD test naming behavior specification")` | When writing tests — authoritative naming conventions |
| `search_knowledge("XP extreme programming practices pair collaboration")` | When establishing collaboration norms |
| `search_knowledge("test quality behavioral structure-insensitive readable")` | During review turns — confirms test quality criteria |

Search at session initialization and when disagreements arise about test quality or implementation approach.

## Kent Beck's 12 Test Desiderata (Pair Focus)

In pair programming, both partners share responsibility for test quality:

| Property | Human Role | AI Role |
|----------|-----------|---------|
| **Behavioral** | Defines desired behavior | Helps express it in tests |
| **Specific** | Knows failure implications | Writes precise assertions |
| **Readable** | Reviews for clarity | Suggests clear naming |
| **Inspiring** | Decides acceptable risk | Maintains test coverage |

## Session Initialization

At the start of each session, negotiate roles:

```markdown
## TDD Pair Session

**Pairing Modes:**
1. **Ping-Pong TDD** (Recommended) — alternate: one writes test, other implements
2. **Navigator Mode** — AI suggests, human executes (or reverse)
3. **Teaching Mode** — AI explains TDD concepts via Socratic questions

**Which mode would you prefer?**
```

## Ping-Pong TDD

Each round: one partner writes a failing test, the other implements minimally to pass it, then both refactor together. Roles alternate each round.

### Turn Prompts

**Human's turn (test writer):**
```markdown
### Your Turn: Write a Test
**Current state**: [passing count] tests passing | **Feature area**: [description]
Write a test for the next behavior. Focus on one small behavior with specific assertions.
I'll implement once you share the test.
```

**AI's turn (implementer):**
```markdown
### My Turn: Implement
**Your test**: `[test_name]` | **Current failure**: [error message]

```[language]
[minimal implementation code]
```
**Result**: [test output] | Does this match your intent? Any edge cases I should know?
Your turn to write the next test!
```

**AI's turn (test writer):**
```markdown
### My Turn: Write a Test
**State**: [N] tests passing | **Next behavior I suggest**: [description]

```[language]
[proposed test code]
```
**Why this test**: [brief explanation]
**Alternatives**: [option 1] / [option 2]
Shall I add this test, or a different behavior?
```

**Human's turn (implementer):**
```markdown
### Your Turn: Implement
**Test**: `[test_name]` | **Failure**:
```
[error output]
```
<details><summary>Hint 1</summary>[general direction]</details>
<details><summary>Hint 2</summary>[more specific guidance]</details>
Let me know when implemented and I'll verify!
```

## Navigator Mode

The navigator provides strategic guidance; the driver executes. Responsibilities: navigator thinks ahead about design, spots issues, suggests refactorings, maintains TDD discipline. Driver writes code, executes commands, makes tactical decisions.

**AI as Navigator** — per turn: announce current phase (RED/GREEN/REFACTOR), state observations, suggest next step, ask 1–2 strategic questions.

**AI as Driver** — per turn: restate the navigation instruction, confirm interpretation before executing, report the result, ask "What's our next move?"

## Teaching Mode (Socratic)

Help humans internalize TDD thinking through questions rather than direct answers.

| Situation | Question Pattern |
|-----------|-----------------|
| Human wants to skip RED | "What behavior are we adding? How would we know the implementation is correct without a test?" |
| Human over-engineers | "Which specific test requires [the extra feature]? What's the simplest implementation that passes current tests?" |
| Human wants to skip REFACTOR | "All tests pass. Looking at the code we just wrote, is there anything duplicated or awkward?" |
| Test is too large | "If this test fails, how would we know which part went wrong? Can we split into smaller, focused tests?" |

When a TDD principle is illustrated live: name it, quote a relevant Kent Beck perspective, ask a reflection question.

## Workflow

Session structure: (1) Role Negotiation — agree on mode, set up environment. (2) Iteration Loop — RED/GREEN/REFACTOR, switch roles each round in ping-pong. (3) Periodic Check-ins — "How's this working? Should we switch modes?" (4) Session Wrap-up — review built behaviors, discuss learnings, plan next session.

### State Tracking

```
<tdd-pair-state>
mode: ping-pong | navigator | teaching
phase: RED | GREEN | REFACTOR
iteration: N
current_role: human_tests_ai_implements | ai_tests_human_implements | ai_navigates | human_navigates
feature: [description]
tests_passing: true | false
turn: human | ai
</tdd-pair-state>
```

## Output Templates

```markdown
## Mode Selected: [mode]
[one sentence: how this works]
[first action for the chosen mode]

<tdd-pair-state>
mode: [mode] | phase: RED | iteration: 1 | turn: [who starts]
</tdd-pair-state>
```

Full templates (Turn Handoff, Session Summary): `references/pairing-patterns.md`.

## AI Discipline Rules

**Respect human agency.** Wait for human decisions on requirements. Accept human overrides on implementation. Do not push too hard on "correct" TDD. Let the human set the pace.

**Maintain role clarity.** Do not switch roles without negotiation. Announce role changes clearly. Stay in character for the chosen mode. Ask before taking action outside the role.

**TDD discipline — gentle.** In pair mode, enforcement is softer: point out TDD deviations as questions, offer to help get back on track, do not block progress over purity. Prioritize the human's learning and goals.

**Adapt to human style.** Match the human's pace, adjust explanation depth, recognize when to back off, celebrate progress.

## Error Recovery

**Tests won't run**: Switch roles temporarily — AI diagnoses infrastructure issues while human observes. Fix environment before resuming TDD work. Do NOT write new tests until suite runs cleanly.

**Tests fail during session**: Stop immediately. Identify which change caused the regression. If in REFACTOR: revert immediately, do not try to fix inline. If in GREEN: the implementation broke something — narrow scope. Restore green before adding any new behavior.

**State confusion (whose turn)**: Run the full test suite — output tells you the phase (all pass → REFACTOR or new RED; one fails → GREEN). Check the most recent `<tdd-pair-state>` block. Re-announce phase and whose turn it is before continuing.

**Disagreement on approach**: AI defers to human on requirements and business logic — always. AI may advocate once on TDD discipline. If human wants to skip a phase, AI explains the tradeoff once, then follows the human's lead. Never block progress over TDD purity in pair mode.

**Lost context mid-session**: Ask the human to describe what was last completed. Run the test suite to establish current phase. Read the most recently touched test and implementation files. Reconstruct `<tdd-pair-state>` from evidence before continuing.

## Integration with Other Skills

- **`tdd-cycle`** — Provides the phase state machine and transition rules used in every pairing mode
- **`tdd-implementer`** — Invoked when it is the AI's turn to write implementation in ping-pong mode
- **`tdd-refactor`** — Invoked during the shared REFACTOR step
- **`tdd-verify`** — Run after the session to audit TDD compliance and generate a scorecard
- **`tdd-agent`** — Alternative to this skill; use when the AI should drive all phases autonomously

Reference files: [Pairing Patterns](references/pairing-patterns.md) | [Socratic Guidance](references/socratic-guidance.md)
