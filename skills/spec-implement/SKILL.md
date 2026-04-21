---
name: spec-implement
description: >
  Spec-driven TDD implementation for greenfield features and well-understood changes.
  Takes an existing spec (PRD, user stories, requirements doc, or acceptance criteria)
  and drives test-first implementation to verified completion. The unique step is
  translating the spec into binary, verifiable acceptance criteria before any code
  starts. Use for "/spec-implement path/to/spec.md", "implement this spec", "implement
  from requirements", "turn this PRD into code", "greenfield feature from spec",
  "acceptance criteria to implementation". Do NOT use when the codebase is complex,
  unfamiliar, or requires research before planning — use /rpi-research instead.
---

# Spec Implement

> "The spec is the budget. Implementation spends it. You cannot spend what isn't defined."
> — Adapted from Frederick P. Brooks Jr., "The Mythical Man-Month"

> "First, write the test that would prove the spec is satisfied. Everything else follows."
> — Adapted from Kent Beck

## Core Philosophy

This skill bridges the gap between a written spec and working, verified code. The unique contribution is the **Parse phase**: converting human-written requirements into binary, independently-verifiable acceptance criteria before a single line of production code is written. Once the criteria are confirmed, implementation becomes mechanical — each criterion maps to a test cycle, each test cycle maps to a RED-GREEN-REFACTOR iteration.

The skill exists because most spec-to-code failures happen before implementation begins. Requirements that say "the system should handle errors gracefully" cannot be tested. Requirements that say "when the API returns 500, the retry count increments and the error is logged with the request ID" can be. The Parse and Scope phases exist to eliminate the first kind and enforce the second.

**What this skill IS:**

- A structured workflow from spec → verifiable criteria → TDD-first implementation → verified done
- A discipline for making "done" mean something specific and observable before work starts
- A session management tool that tracks criteria, test status, and implementation progress across turns
- The greenfield counterpart to RPI: use this when you have a spec, use RPI when you have a codebase to research

**What this skill is NOT:**

- A spec writer — it reads and parses specs, it does not produce them (use `spec-coach` for that)
- A planning tool for brownfield changes — if you need to understand existing code first, use `/rpi-research`
- A substitute for `tdd-cycle` — this skill *orchestrates* TDD; `tdd-cycle` manages the phase transitions within each RED-GREEN-REFACTOR iteration
- A code generator that skips tests — tests come first, always, every time

---

## Domain Principles Table

| # | Principle | Description | Applied As |
|---|-----------|-------------|------------|
| 1 | **Criteria Before Code** | You cannot test what you have not defined. Acceptance criteria are not documentation added after the fact — they are the contract that defines when implementation is done. Writing criteria before code forces clarity. "Handle errors gracefully" is not a criterion. "When input exceeds 255 characters, return HTTP 400 with the message 'Input too long'" is. | Never begin implementation until every requirement has been converted to a binary pass/fail criterion. |
| 2 | **Binary Verifiability** | A criterion is either satisfied or it isn't — there is no partial credit, no "mostly works," no "close enough." This is not pedantry; it is the only way to know when you are done. An observer with no context should be able to run the tests and determine unambiguously whether each criterion passes. | Every criterion must pass this test: "Could an independent observer, given only the test output, determine whether this criterion is satisfied without asking anyone?" |
| 3 | **Smallest Testable Increment** | The spec names features. Features are built from behaviors. Behaviors are exercised by tests. The skill's job is to decompose features into the smallest testable behaviors, then implement those behaviors in dependency order. An increment that takes more than 30 minutes to reach GREEN is too large. | Decompose each spec feature into behaviors before implementing. Ask: "What is the smallest increment of this that could be tested independently?" |
| 4 | **Spec Ambiguity Is a Stop Signal** | Ambiguity in requirements is not a creative opportunity — it is a missing specification that will produce the wrong behavior. When the spec is silent on a behavior that matters, surface it to the human before implementing. Guessing is cheaper in the short term and catastrophically expensive after delivery. | When a criterion cannot be made binary because the spec is ambiguous, STOP and surface the question. Do not assume. |
| 5 | **Test Sequencing Encodes Dependencies** | Tests are not written in the order they appear in the spec. They are written in dependency order: foundational behaviors first, higher-order behaviors last. Implementing a validation rule before the entity it validates produces unreliable test results. | Before the first test is written, produce a sequenced test plan. Tests that depend on other tests come later, regardless of spec order. |
| 6 | **No Scope Drift** | The spec defines what to build. Implementation executes the spec. During the Implement phase, it is common to notice "obvious improvements," "related things to clean up," or "things the spec missed." None of these belong in this session. The criteria are fixed. New observations go in the deferred items register. | When a scope drift impulse appears, log it in the deferred items register and return to the current criterion. Do not implement unspecified behavior. |
| 7 | **Green Baseline First** | Before writing the first failing test, run the existing test suite. A clean baseline means any subsequent failure was caused by this session. A dirty baseline means failures are invisible. On greenfield projects where no tests exist, confirm the project compiles and the test runner works. | Always run the test suite before writing the first test. Report the baseline result; stop if the baseline is dirty and the cause is unclear. |
| 8 | **Each Criterion Gets One Commit** | Granular commits make bisect, rollback, and review fast. After each criterion's test passes and refactoring is complete, commit. The commit message references the criterion. This is the implementation's audit trail against the spec. | Commit after each criterion is verified GREEN and REFACTORED. Never mega-commit. |
| 9 | **Deferred ≠ Forgotten** | Observations, scope questions, and spec gaps that arise during implementation are not lost — they are logged in the session's deferred items register and reviewed with the user at the end. "I noticed X but did not implement it" is better than either ignoring X or implementing X without specification. | Maintain a deferred items register throughout the session. Review it with the user at the final verification step. |
| 10 | **Done Means Criteria + Confirmed** | Implementation is done when all criteria pass AND the user confirms. Not when the last test goes green. Not when the code compiles. The user must review the final verification report and acknowledge it. The skill does not declare done unilaterally. | Present the final verification report and explicitly ask for user confirmation before closing the session. |

---

## Knowledge Base Lookups

Use `search_knowledge` (grounded-code-mcp) to ground decisions in authoritative references.

| Query | When to Call |
|-------|--------------|
| `search_knowledge("acceptance criteria BDD given when then format")` | During PARSE phase — ground criteria format in authoritative BDD practices |
| `search_knowledge("TDD red green refactor cycle phases")` | Before IMPLEMENT phase — confirm canonical phase definitions |
| `search_knowledge("Kent Beck test desiderata properties")` | When evaluating test quality in RED phase — authoritative test properties |
| `search_knowledge("test-first development discipline XP")` | When enforcing TDD discipline — ground in XP practices |
| `search_knowledge("unit test naming conventions AAA arrange act assert")` | When structuring test bodies — naming and organization patterns |
| `search_knowledge("simple design four rules Beck")` | During REFACTOR phase — ground refactoring decisions in Simple Design |

**Protocol:** Search at phase transitions where grounding matters. Cite the source path in your response.

**Local reference:** `references/bdd-given-when-then.md` — binary verifiability rules, conversion examples, dependency sequencing, and the Criteria Manifest format. Read this during PARSE when formalizing criteria.

---

## Workflow

```
PARSE
    Read the full spec (or user-supplied requirements).

    If the spec is a GitHub Spec Kit `spec.md`, look for companion files in the same directory:
      → `plan.md`      — read for architecture approach and technical decisions (shapes test structure)
      → `data-model.md`— read for entity definitions (informs entity test setup and field assertions)
      → `contracts/`   — read for API contracts (maps directly to endpoint criteria)
      → `research.md`  — read for technical background (surfaces implementation constraints)
    Log which companion files were found and what criteria they contribute.

    Extract every requirement, user story, or acceptance criterion.
    For each, convert to binary form: GIVEN [context] WHEN [action] THEN [observable outcome].
    Flag anything that cannot be made binary as an ambiguity.
    Produce the Criteria Manifest.

        |
        v

SCOPE
    Present the Criteria Manifest to the user.
    Review each criterion together:
      → Confirm: criterion is clear, binary, in scope
      → Revise: criterion needs adjustment
      → Reject: out of scope or misread
    Resolve every flagged ambiguity — ask, do not assume.
    Agree on the sequenced test plan: dependency order for all criteria.
    Agree on the baseline check command (test runner invocation).
    User signs off on the Criteria Manifest before any code is written.
    STATUS: waiting for user approval of Criteria Manifest before proceeding.

        |
        v

BASELINE
    Run the existing test suite (or verify the project compiles, for greenfield).
    → CLEAN: all tests pass (or "no tests yet, project compiles")
      Continue to IMPLEMENT.
    → DIRTY: failures exist before any changes.
      STOP. Report failures. Do not proceed until the user resolves them.

        |
        v

IMPLEMENT (loop per criterion, in sequenced order)

    ANNOUNCE
        "Implementing Criterion [N]: [title]"
        "[GIVEN / WHEN / THEN statement]"

    RED
        Write the smallest test that would fail because this criterion is not yet met.
        Run the test suite. Confirm: new test fails for the RIGHT reason (not syntax/import).
        If the test passes immediately (false green): the test is wrong — revise it.

    GREEN
        Write minimal production code to make the test pass.
        No additional functionality. "Fake it till you make it" is acceptable.
        Run the test suite. Confirm: all tests pass.

    REFACTOR
        Apply Simple Design: remove duplication, improve names, simplify structure.
        Run tests after each change. Tests must stay green.
        Stop when the code reveals its intent without comment.

    COMMIT
        Commit with message: "feat: [criterion title]"
        One commit per criterion.

    ADVANCE
        Mark criterion [N] complete in the Criteria Manifest.
        → More criteria remain: announce next criterion, repeat IMPLEMENT loop.
        → All criteria complete: proceed to VERIFY.

        |
        v

VERIFY
    Run the full test suite.
    Map each passing test to its criterion.
    Produce the Verification Report.
    Review the deferred items register with the user.
    Ask for user confirmation: "All criteria verified. Do you confirm this implementation complete?"
    → Confirmed: session complete.
    → Issues raised: address them or log them as follow-up items.
```

**Exit criteria:** All criteria in the Criteria Manifest are marked complete, the full test suite passes, and the user has confirmed.

---

## State Block

Maintain state across conversation turns:

```
<spec-implement-state>
phase: PARSE | SCOPE | BASELINE | IMPLEMENT | VERIFY | COMPLETE
spec_source: [path or description of the spec]
criteria_total: [N]
criteria_confirmed: [N]
criteria_complete: [N]
current_criterion: [N — title]
tdd_phase: RED | GREEN | REFACTOR | none
baseline_status: clean | dirty | not-run
deferred_items: [count]
last_action: [what was just done]
next_action: [what should happen next]
blockers: none | [description]
</spec-implement-state>
```

### State Progression Example

```
<spec-implement-state>
phase: PARSE
spec_source: docs/requirements/user-registration.md
criteria_total: pending
criteria_confirmed: 0
criteria_complete: 0
current_criterion: none
tdd_phase: none
baseline_status: not-run
deferred_items: 0
last_action: Session opened — reading spec
next_action: Extract and formalize acceptance criteria
blockers: none
</spec-implement-state>
```

```
<spec-implement-state>
phase: SCOPE
spec_source: docs/requirements/user-registration.md
criteria_total: 8
criteria_confirmed: 0
criteria_complete: 0
current_criterion: none
tdd_phase: none
baseline_status: not-run
deferred_items: 2
last_action: Criteria Manifest produced — 8 criteria extracted, 2 ambiguities flagged
next_action: Review Criteria Manifest with user; resolve ambiguities; get sign-off
blockers: none
</spec-implement-state>
```

```
<spec-implement-state>
phase: IMPLEMENT
spec_source: docs/requirements/user-registration.md
criteria_total: 8
criteria_confirmed: 8
criteria_complete: 3
current_criterion: 4 — Duplicate email rejected with 409
tdd_phase: GREEN
baseline_status: clean
deferred_items: 1
last_action: RED phase complete — failing test for duplicate email check
next_action: Write minimal code to make the duplicate email test pass
blockers: none
</spec-implement-state>
```

---

## Output Templates

### Session Opening

```markdown
## Spec Implement Session

I will translate this spec into verified, test-first implementation.

**How this works:**
1. I read the spec and convert every requirement into a binary, verifiable criterion
2. We review the criteria together and resolve ambiguities before any code is written
3. You sign off on the Criteria Manifest
4. I run the baseline test suite to confirm a clean starting state
5. I implement each criterion in sequence: RED → GREEN → REFACTOR → commit
6. I present a Verification Report at the end and ask you to confirm done

**Important:** Implementation does not begin until the Criteria Manifest is confirmed.
If I cannot make a requirement binary, I will ask — not assume.

To begin, please provide the spec (file path, paste, or description).

<spec-implement-state>
phase: PARSE
spec_source: awaiting input
criteria_total: pending
criteria_confirmed: 0
criteria_complete: 0
current_criterion: none
tdd_phase: none
baseline_status: not-run
deferred_items: 0
last_action: Session opened
next_action: Awaiting spec from user
blockers: none
</spec-implement-state>
```

### Criteria Manifest

```markdown
## Criteria Manifest

**Spec**: [source]
**Extracted**: [N] criteria, [N] ambiguities

### Criteria

| # | Title | Given / When / Then | Status |
|---|-------|---------------------|--------|
| C-01 | [title] | GIVEN [context] WHEN [action] THEN [observable outcome] | confirmed |
| C-02 | [title] | GIVEN [context] WHEN [action] THEN [observable outcome] | confirmed |
| C-03 | [title] | GIVEN [context] WHEN [action] THEN [observable outcome] | **ambiguous** |

### Ambiguities Requiring Resolution

#### [A-01] [description of ambiguity]
**From spec**: "[exact quote]"
**What is unclear**: [explanation]
**Options**:
1. [interpretation A]
2. [interpretation B]
**Question for you**: [specific question]

### Proposed Test Sequence

Dependency-ordered implementation sequence:
1. C-02 — [title] (foundational, no dependencies)
2. C-01 — [title] (depends on C-02 entity)
3. C-03 — [title] (depends on C-01 behavior)
...

**Please review, revise, and confirm this manifest before I proceed.**

<spec-implement-state>
phase: SCOPE
...
</spec-implement-state>
```

### Criterion Announcement

```markdown
---

### Criterion [N] of [total]: [Title]

**GIVEN** [context]
**WHEN** [action]
**THEN** [observable outcome]

Starting RED phase — writing the failing test.
```

### RED Phase Complete

```markdown
**RED ✓** — Failing test written.

Test: `[test name]`
Failure: `[exact failure message]`
Failure reason: correct — [criterion] is not yet implemented

Starting GREEN phase.
```

### GREEN Phase Complete

```markdown
**GREEN ✓** — All tests pass.

Production code added:
- `[file path]` — [brief description of change]

Starting REFACTOR phase.
```

### REFACTOR Phase Complete

```markdown
**REFACTOR ✓** — Code cleaned.

Changes: [brief description, or "none required"]
Tests: all passing

Committing: `feat: [criterion title]`

Criterion [N] complete. [N remaining / proceeding to VERIFY]
```

### Verification Report

```markdown
## Verification Report

**Spec**: [source]
**Date**: [date]
**Test suite**: [command]

### Criteria Status

| # | Criterion | Test | Status |
|---|-----------|------|--------|
| C-01 | [title] | `[test name]` | ✓ PASS |
| C-02 | [title] | `[test name]` | ✓ PASS |

**All [N] criteria: PASS**

Test suite: [N] passed, 0 failed, 0 skipped

### Deferred Items

Items observed during implementation but not in scope:

| # | Item | Recommendation |
|---|------|----------------|
| D-01 | [description] | [add to backlog / address in follow-up spec] |

### Confirmation

All [N] criteria have been implemented and verified by the test suite.

**Do you confirm this implementation complete?**

<spec-implement-state>
phase: VERIFY
...
</spec-implement-state>
```

---

## AI Discipline Rules

### CRITICAL: Parse Before Implementing

The most common failure is jumping from "I understand the spec" to writing code. Understanding a spec is not the same as having binary, verifiable criteria. Before any code is written, the Criteria Manifest must exist and be confirmed.

```
WRONG: User pastes a PRD. Agent reads it and starts writing tests.

RIGHT: User pastes a PRD. Agent produces the Criteria Manifest.
       Agent presents it and asks for confirmation.
       User confirms or revises.
       Agent runs baseline check.
       THEN agent writes the first test.
```

### CRITICAL: Never Assume Ambiguous Requirements

When a requirement cannot be made binary — because it uses vague qualifiers ("should be fast," "handle errors gracefully," "validate input"), is silent on an edge case, or contradicts another requirement — the correct action is to stop and ask.

```
WRONG: Spec says "validate user input." Agent implements:
       - max length 255
       - no special characters
       - email format check
       None of these were specified.

RIGHT: Spec says "validate user input." Agent flags: "The spec mentions
       validation but does not specify the rules. Before I can write a
       test, I need to know: [list specific questions]."
```

### CRITICAL: Test Must Fail for the RIGHT Reason

A test that fails because of a missing import or syntax error is not a RED phase test — it is a broken test. The failure must be semantic: the behavior is not yet implemented, not: the code does not compile.

```
WRONG: Test written. Running it produces: ImportError: cannot import name 'UserService'
       Agent proceeds to GREEN phase.

RIGHT: Agent fixes the import issue (structural, not behavioral).
       Re-runs. Test now fails with: AssertionError: Expected 400, got 200
       THAT is the RED phase complete.
```

### CRITICAL: Minimal GREEN Code

GREEN phase code is not production code. Its only job is to make the failing test pass. Hardcoding return values, if-statements that match only the test case, and "fake" implementations are all acceptable. The REFACTOR phase and subsequent criteria will force the real implementation.

```
WRONG: During GREEN for "email must be unique," agent implements:
       - full database query
       - case-insensitive comparison
       - trimming whitespace
       - transaction isolation
       None of these were required by the current failing test.

RIGHT: Agent implements the minimum check that makes the test pass.
       Subsequent criteria (case sensitivity, trimming) will require
       and specify those behaviors separately.
```

### CRITICAL: Log Scope Drift, Do Not Act On It

During implementation, it is common to notice things not in the spec. Logging them is correct. Implementing them is not. The spec defines the budget; the session spends it. Work not in the spec goes in the deferred items register.

```
WRONG: While implementing C-03, agent notices the error messages
       could be internationalized. Agent adds i18n support.

RIGHT: Agent adds to deferred register: "D-01: Error messages use
       hardcoded strings — consider i18n in a future spec."
       Agent continues with C-03.
```

---

## Anti-Patterns Table

| Anti-Pattern | Description | Why It Fails | What to Do Instead |
|--------------|-------------|-------------|-------------------|
| **Skipping Parse** | Reading the spec and immediately writing tests or code based on informal understanding | Informal understanding produces informal criteria. The first test is testing the agent's interpretation, not the spec. | Always produce the Criteria Manifest before the first test. |
| **Vague Criteria Acceptance** | Allowing criteria like "the API should respond quickly" or "errors are handled" to survive the Scope phase | Vague criteria cannot be tested. They produce tests that pass trivially or fail inconsistently. | In SCOPE, reject every criterion that fails the binary test: "could an independent observer determine pass/fail from test output alone?" |
| **Assuming Missing Requirements** | Implementing behavior the spec did not specify because it "obviously" should be there | The spec author may have intentionally omitted it. The behavior may be in scope for a different story. The assumption may be wrong. | Flag it as an ambiguity in PARSE; surface it in SCOPE; resolve it before code. |
| **False Green** | Writing a test that passes immediately without production code being added | The test does not test the right thing — it may be too permissive, testing the wrong path, or the behavior already exists. | If a test passes immediately in RED phase, revise the test until it fails for the right reason. |
| **GREEN Overreach** | Writing more production code than needed to pass the current failing test | Adds behavior without a test; the extra behavior is unspecified and may be wrong. | Write the minimum. If more is needed, the next criterion will require and test it. |
| **Batch Commits** | Completing all criteria and committing everything at the end | Loses per-criterion recovery points; makes the commit history useless for bisect and review | Commit after each criterion is GREEN and REFACTORED. One criterion = one commit. |
| **Skipping Baseline** | Writing the first test without running the existing suite | Pre-existing failures become invisible; the agent cannot tell if its changes caused failures | Always run the baseline before writing the first test. A dirty baseline is a stop signal. |
| **Speccing During Implementation** | Adding new requirements or "just one more thing" during the IMPLEMENT phase | Scope creep with no specification. The new behavior may conflict with confirmed criteria. | Log in deferred items register; address in a follow-up spec session. |
| **Declaring Done Unilaterally** | The agent marks implementation complete without explicit user confirmation | The user may have context the agent lacks; verification is a shared act | Present the Verification Report and explicitly ask for user confirmation. |
| **Using This Skill for Brownfield** | Running spec-implement on a complex, unfamiliar codebase without research | Criteria will be written without knowing how the existing system behaves; tests will fight the codebase | If the codebase is complex or unfamiliar, run `/rpi-research` first to produce a research artifact, then return to spec-implement. |

---

## Error Recovery

### Problem: Ambiguity Cannot Be Resolved in Session

The user does not have the answer to an ambiguity question — the product owner, a stakeholder, or a technical design decision is needed.

**Recovery:**
1. Reject the ambiguous criterion from the current manifest. Mark it as `blocked`.
2. Continue with the remaining confirmed criteria.
3. Log the blocked criterion and the specific question in the deferred items register.
4. At VERIFY, surface the blocked item: "Criterion [N] was not implemented — pending resolution of [question]. Please schedule this as a follow-up."

### Problem: Test Passes Immediately (False Green)

The test written in RED phase passes without any production code being added.

**Recovery:**
1. Do not proceed to GREEN. The test is wrong.
2. Analyze: Is the behavior already implemented? Is the assertion too weak? Is the test hitting the wrong path?
3. If the behavior already exists: mark the criterion as satisfied by existing code; skip to COMMIT.
4. If the test is wrong: revise it until it fails for the right reason before proceeding.

### Problem: GREEN Phase Takes More Than 30 Minutes

Production code to satisfy a criterion is complex enough that implementation is taking too long.

**Recovery:**
1. Stop. The criterion is too large.
2. Decompose it: "This criterion actually requires [sub-behavior A] before [sub-behavior B]."
3. Return to SCOPE, add the sub-criteria to the manifest, and implement them in order.
4. A 30-minute GREEN phase is a sign the criterion was not the smallest testable increment.

### Problem: REFACTOR Breaks Tests

A refactoring change in REFACTOR phase causes tests to fail.

**Recovery:**
1. Immediately revert the refactoring change.
2. Confirm all tests pass again.
3. Analyze: Was the refactoring changing behavior (not allowed) or structure (allowed)?
4. If behavior change: revert and move on — the refactoring was wrong.
5. If structure change that unexpectedly broke tests: the tests may be testing implementation rather than behavior — investigate and fix the tests first, then re-attempt refactoring.

### Problem: Spec Is a Bullet List, Not Formal Requirements

The user provides requirements as informal notes, a bullet list, or conversational description rather than a structured spec.

**Recovery:**
1. Do not reject the input. Treat it as raw material for PARSE.
2. Work through each bullet and ask: "What would a test for this look like?"
3. For each item that can be formalized: convert to GIVEN/WHEN/THEN.
4. For each item that cannot: flag as an ambiguity requiring clarification.
5. Tell the user: "I have converted your notes into [N] criteria. [M] items need clarification before I can write tests for them."

### Problem: Codebase Is More Complex Than Expected

During IMPLEMENT, the agent discovers the codebase has complex existing behavior that affects the criterion — entangled dependencies, existing implementations of the feature, or conflicting tests.

**Recovery:**
1. Stop immediately. Do not try to work around the complexity.
2. Report: "I found [description]. This is more complex than a greenfield implementation. I recommend running `/rpi-research [topic]` to understand the existing code before continuing."
3. The confirmed criteria remain valid. The implementation path needs research first.

---

## Integration with Other Skills

| Skill | Relationship |
|-------|-------------|
| `spec-coach` | Produces specs that this skill consumes. The spec coach designs behavioral boundaries and anchors acceptance criteria with concrete examples (input → action → expected output). Run `spec-coach` first on greenfield features, then hand the output to this skill. Criteria produced with `spec-coach`'s Specification by Example guidance map directly to the GIVEN/WHEN/THEN format needed in PARSE. |
| `tdd-cycle` | Manages the RED-GREEN-REFACTOR phase transitions within each criterion's implementation. Load `tdd-cycle` when the implementation of a single criterion becomes complex enough to need explicit phase tracking. This skill orchestrates *across* criteria; `tdd-cycle` orchestrates *within* each criterion. |
| `rpi-research` | When spec-implement discovers unexpected complexity in the existing codebase, switch to `rpi-research` to understand what exists before continuing. Research produces an artifact; bring that artifact back to spec-implement to resume. |
| `rpi-plan` | When a spec is large enough (10+ criteria with significant dependencies) that a formal phased plan is warranted, produce a plan artifact with `rpi-plan` and execute it with `rpi-implement` instead. Use spec-implement for well-scoped features; use RPI for large multi-phase changes. |
| `architecture-review` | When the spec describes a significant system design rather than a feature, run `architecture-review` on the proposed design before spec-implement begins. Architecture vulnerabilities found after implementation is complete are expensive. |
| `tdd-refactor` | For REFACTOR phases that involve significant structural changes, load `tdd-refactor` to manage the refactoring safely with per-step verification. |
| `automated-code-review` | After VERIFY, before user confirmation, run `automated-code-review` on the diff to catch quality issues before the session closes. |
