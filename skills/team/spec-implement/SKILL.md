---
name: spec-implement
description: >
  Spec-driven TDD implementation for greenfield features and well-understood changes.
  Takes an existing spec (PRD, user stories, requirements doc, or acceptance criteria)
  and drives test-first implementation to verified completion. The unique step is
  translating the spec into binary, verifiable acceptance criteria before any code
  starts. Use when implementing a greenfield feature from a spec, PRD, or acceptance criteria. Trigger phrases: "/spec-implement path/to/spec.md", "implement this spec", "implement
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

This skill bridges the gap between a written spec and working, verified code. The unique contribution is the **Parse phase**: converting human-written requirements into binary, independently-verifiable acceptance criteria before a single line of production code is written. Once the criteria are confirmed, implementation becomes mechanical -- each criterion maps to a test cycle, each test cycle maps to a RED-GREEN-REFACTOR iteration.

The skill exists because most spec-to-code failures happen before implementation begins. Requirements that say "the system should handle errors gracefully" cannot be tested. Requirements that say "when the API returns 500, the retry count increments and the error is logged with the request ID" can be.

**What this skill IS:** A structured workflow from spec → verifiable criteria → TDD-first implementation → verified done. The greenfield counterpart to RPI: use this when you have a spec, use RPI when you have a codebase to research.

**What this skill is NOT:** A spec writer (use `spec-coach`); a planning tool for brownfield changes (use `/rpi-research`); a code generator that skips tests.

## Domain Principles Table

| # | Principle | Description | Applied As |
|---|-----------|-------------|------------|
| 1 | **Criteria Before Code** | A criterion is the contract that defines done. "Handle errors gracefully" is not a criterion. "When input exceeds 255 characters, return HTTP 400 with 'Input too long'" is. | Never begin implementation until every requirement has a binary pass/fail criterion. |
| 2 | **Binary Verifiability** | An observer with no context should be able to run the tests and determine unambiguously whether each criterion passes. No partial credit, no "mostly works." | Every criterion: "Could an independent observer determine pass/fail from test output alone?" |
| 3 | **Smallest Testable Increment** | Decompose features into the smallest testable behaviors, then implement in dependency order. An increment taking more than 30 minutes to reach GREEN is too large. | Ask: "What is the smallest increment of this that could be tested independently?" |
| 4 | **Spec Ambiguity Is a Stop Signal** | Ambiguity is a missing specification that will produce the wrong behavior. Surface it before implementing. Guessing is cheap in the short term and catastrophically expensive after delivery. | When a criterion cannot be made binary because the spec is ambiguous, STOP and surface the question. |
| 5 | **Test Sequencing Encodes Dependencies** | Tests are written in dependency order, not spec order. Foundational behaviors first, higher-order behaviors last. | Produce a sequenced test plan before the first test is written. |
| 6 | **No Scope Drift** | The spec defines what to build. New observations, "obvious improvements," and "related things to clean up" go in the deferred items register. | When a scope drift impulse appears, log it and return to the current criterion. |
| 7 | **Green Baseline First** | Before writing the first failing test, run the existing test suite. A dirty baseline makes failures invisible. | Always run the baseline before writing the first test. Report the result; stop if the baseline is dirty. |
| 8 | **Each Criterion Gets One Commit** | Commit after each criterion is GREEN and REFACTORED. The message references the criterion. | Never mega-commit. One criterion = one commit. |
| 9 | **Deferred ≠ Forgotten** | Observations and spec gaps that arise during implementation are logged in the deferred items register and reviewed with the user at the end. | Maintain a deferred items register; review it at VERIFY. |
| 10 | **Done Means Criteria + Confirmed** | Implementation is done when all criteria pass AND the user confirms. Not when the last test goes green. | Present the final verification report and explicitly ask for user confirmation before closing. |

## Knowledge Base Lookups

| Query | When to Call |
|-------|--------------|
| `search_knowledge("acceptance criteria BDD given when then format")` | During PARSE phase -- ground criteria format in authoritative BDD practices |
| `search_knowledge("TDD red green refactor cycle phases")` | Before IMPLEMENT phase -- confirm canonical phase definitions |
| `search_knowledge("Kent Beck test desiderata properties")` | When evaluating test quality in RED phase |
| `search_knowledge("test-first development discipline XP")` | When enforcing TDD discipline |
| `search_knowledge("unit test naming conventions AAA arrange act assert")` | When structuring test bodies |
| `search_knowledge("simple design four rules Beck")` | During REFACTOR phase |

Local reference: `references/bdd-given-when-then.md` -- binary verifiability rules, conversion examples, dependency sequencing, and the Criteria Manifest format.

## Workflow

```
PARSE
    Read the full spec. If a GitHub Spec Kit spec.md, look for companion files:
      plan.md (architecture approach), data-model.md (entities), contracts/ (API),
      research.md (technical background). Log which files were found.
    Extract every requirement. Convert each to binary form:
      GIVEN [context] WHEN [action] THEN [observable outcome].
    Flag anything that cannot be made binary as an ambiguity.
    Produce the Criteria Manifest.

        |
        v

SCOPE
    Present the Criteria Manifest to the user. Review each criterion:
      Confirm / Revise / Reject.
    Resolve every flagged ambiguity -- ask, do not assume.
    Agree on the sequenced test plan (dependency order).
    Agree on the baseline check command.
    User signs off. STATUS: waiting for user approval before proceeding.

        |
        v

BASELINE
    Run the existing test suite (or verify the project compiles, for greenfield).
    CLEAN: continue to IMPLEMENT.
    DIRTY: STOP. Report failures. Do not proceed until the user resolves them.

        |
        v

IMPLEMENT (loop per criterion, in sequenced order)

    ANNOUNCE  "Implementing Criterion [N]: [GIVEN / WHEN / THEN]"

    RED       Write the smallest test that fails because this criterion is not yet met.
              Run suite. Confirm: new test fails for the RIGHT reason (not syntax/import).
              If the test passes immediately (false green): the test is wrong -- revise it.

    GREEN     Write minimal production code to make the test pass.
              No additional functionality. Run suite. Confirm: all tests pass.

    REFACTOR  Apply Simple Design: remove duplication, improve names, simplify structure.
              Run tests after each change. Stop when code reveals intent without comment.

    COMMIT    "feat: [criterion title]" -- one commit per criterion.

    ADVANCE   Mark criterion [N] complete.
              More criteria remain → next criterion.
              All complete → VERIFY.

        |
        v

VERIFY
    Run the full test suite. Map each passing test to its criterion.
    Produce the Verification Report. Review the deferred items register.
    Ask: "All criteria verified. Do you confirm this implementation complete?"
```

## State Block

```
<spec-implement-state>
phase: PARSE | SCOPE | BASELINE | IMPLEMENT | VERIFY | COMPLETE
spec_source: [path or description of the spec]
criteria_total: [N]
criteria_confirmed: [N]
criteria_complete: [N]
current_criterion: [N -- title]
tdd_phase: RED | GREEN | REFACTOR | none
baseline_status: clean | dirty | not-run
deferred_items: [count]
last_action: [what was just done]
next_action: [what should happen next]
blockers: none | [description]
</spec-implement-state>
```

**Example:**

```
<spec-implement-state>
phase: IMPLEMENT
spec_source: docs/requirements/user-registration.md
criteria_total: 8
criteria_confirmed: 8
criteria_complete: 3
current_criterion: 4 -- Duplicate email rejected with 409
tdd_phase: GREEN
baseline_status: clean
deferred_items: 1
last_action: RED phase complete -- failing test for duplicate email check
next_action: Write minimal code to make the duplicate email test pass
blockers: none
</spec-implement-state>
```

## Output Templates

```markdown
## Criteria Manifest

**Spec**: [source] | **Extracted**: [N] criteria, [N] ambiguities

| # | Title | Given / When / Then | Status |
|---|-------|---------------------|--------|
| C-01 | [title] | GIVEN [context] WHEN [action] THEN [observable outcome] | confirmed |
| C-02 | [title] | GIVEN [context] WHEN [action] THEN [observable outcome] | **ambiguous** |

**Ambiguity [A-01]**: "[exact quote from spec]" — [what is unclear] — Options: (1) [interpretation A] (2) [interpretation B] — **Question**: [specific question]

**Proposed Test Sequence** (dependency order): C-02 → C-01 → C-03 ...

**Please review, revise, and confirm before I proceed.**
```

Full templates (Session Opening, Criterion Announcement, RED/GREEN/REFACTOR completion, Verification Report): `references/bdd-given-when-then.md`.

## AI Discipline Rules

**Parse before implementing.** Understanding a spec is not the same as having binary, verifiable criteria. The Criteria Manifest must exist and be confirmed before any code is written. User pastes a PRD → produce the Criteria Manifest → get confirmation → run baseline → THEN write the first test.

**Never assume ambiguous requirements.** When a requirement uses vague qualifiers ("should be fast," "handle errors gracefully," "validate input") or is silent on an edge case, stop and ask. Do not implement validation rules that were not specified; flag them as ambiguities requiring clarification.

**Test must fail for the RIGHT reason.** A test that fails because of a missing import is not a RED phase test -- it is a broken test. Fix structural failures (imports, syntax) first. The RED phase test fails with a semantic assertion: "Expected 400, got 200."

**Minimal GREEN code.** GREEN phase code has one job: make the failing test pass. Hardcoding, if-statements matching only the test case, and "fake" implementations are acceptable. REFACTOR and subsequent criteria will force the real implementation. Over-implementing in GREEN adds unspecified, untested behavior.

**Log scope drift, do not act on it.** When you notice something not in the spec (i18n, an optimization opportunity, a related bug), add it to the deferred items register and continue with the current criterion. Implementing unspecified behavior is scope creep with no test coverage.

## Anti-Patterns Table

| Anti-Pattern | Why It Fails | What to Do Instead |
|--------------|-------------|-------------------|
| **Skipping Parse** | Informal understanding produces informal criteria. The first test is testing the agent's interpretation, not the spec. | Always produce the Criteria Manifest before the first test. |
| **Vague Criteria Acceptance** | "The API should respond quickly" cannot be tested; produces tests that pass trivially. | Reject every criterion that fails the binary test: "could an independent observer determine pass/fail from test output alone?" |
| **Assuming Missing Requirements** | The spec author may have intentionally omitted it; the assumption may be wrong. | Flag as ambiguity in PARSE; surface in SCOPE; resolve before code. |
| **False Green** | A test that passes immediately in RED tests the wrong thing -- too permissive or hitting the wrong path. | Revise the test until it fails for the right semantic reason. |
| **GREEN Overreach** | More production code than needed to pass the current failing test -- adds unspecified, untested behavior. | Write the minimum. If more is needed, the next criterion will require and test it. |
| **Batch Commits** | Loses per-criterion recovery points; makes commit history useless for bisect. | Commit after each criterion is GREEN and REFACTORED. |
| **Skipping Baseline** | Pre-existing failures become invisible; agent cannot tell if its changes caused them. | Always run baseline before writing the first test. Dirty baseline = stop signal. |
| **Speccing During Implementation** | Scope creep with no specification; new behavior may conflict with confirmed criteria. | Log in deferred items register; address in a follow-up spec session. |
| **Declaring Done Unilaterally** | User may have context the agent lacks; verification is a shared act. | Present the Verification Report and explicitly ask for user confirmation. |
| **Using This Skill for Brownfield** | Criteria written without knowing existing behavior; tests fight the codebase. | Run `/rpi-research` first to understand existing code, then return to spec-implement. |

## Error Recovery

**Ambiguity cannot be resolved in session**: Mark the ambiguous criterion as `blocked`. Continue with remaining confirmed criteria. Surface the blocked item at VERIFY with the specific question needed.

**Test passes immediately (false green)**: Do not proceed to GREEN. Analyze: is the behavior already implemented? Is the assertion too weak? If behavior already exists, mark criterion as satisfied by existing code and skip to COMMIT. If the test is wrong, revise until it fails for the right reason.

**GREEN phase takes more than 30 minutes**: Stop. The criterion is too large. Decompose into sub-behaviors, return to SCOPE, add them to the manifest, implement in order. A 30-minute GREEN phase means the criterion was not the smallest testable increment.

**REFACTOR breaks tests**: Immediately revert. Confirm all tests pass. Determine: was the change modifying behavior (not allowed) or structure (allowed)? If tests break on structural changes, they may be testing implementation rather than behavior -- fix tests first, then re-attempt refactoring.

**Spec is a bullet list, not formal requirements**: Treat as raw material for PARSE. Convert each bullet to GIVEN/WHEN/THEN where possible. Flag items that cannot be formalized. Tell the user: "I have converted your notes into [N] criteria. [M] items need clarification before I can write tests for them."

**Codebase is more complex than expected**: Stop immediately. Report: "I found [description]. This is more complex than greenfield. Run `/rpi-research [topic]` to understand existing code before continuing." Confirmed criteria remain valid; the implementation path needs research first.

## Integration with Other Skills

| Skill | Relationship |
|-------|-------------|
| `spec-coach` | Produces specs that this skill consumes. Run `spec-coach` first on greenfield features, then hand the output here. |
| `tdd-cycle` | Manages RED-GREEN-REFACTOR phase transitions within each criterion. Load when a single criterion's implementation becomes complex enough to need explicit phase tracking. |
| `rpi-research` | When spec-implement discovers unexpected complexity, switch to research first. Bring the artifact back to spec-implement to resume. |
| `rpi-plan` | For specs large enough (10+ criteria with significant dependencies) that a formal phased plan is warranted, use rpi-plan + rpi-implement instead. |
| `architecture-review` | When the spec describes a significant system design, run architecture-review before spec-implement begins. Architecture vulnerabilities found after implementation are expensive. |
