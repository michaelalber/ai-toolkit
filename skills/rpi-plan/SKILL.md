---
name: rpi-plan
description: >
  RPI Plan phase -- converts a research artifact into a phased implementation plan with exact
  file paths, change descriptions, and per-phase verification steps. Use for "/rpi-plan feature",
  "create implementation plan", "plan the changes for X", "design the implementation".
---

# RPI Plan

> "Plans are worthless, but planning is everything."
> -- Dwight D. Eisenhower

> "A plan precise enough to execute mechanically is the goal. If the implementer has to invent anything, the plan failed."

## Core Philosophy

The Plan phase converts the research artifact into an implementation contract. The implementing agent must be able to execute the plan mechanically -- without judgment, invention, or discovery. If the plan requires the implementer to figure out what to do, the plan is incomplete.

The plan is not the implementation. It contains change descriptions, not code. It describes what to change and where, with enough precision that an experienced developer (or an AI agent) can execute each phase without ambiguity.

**Non-Negotiable Constraints:**
1. ALWAYS read the research artifact first -- never plan from memory or assumptions
2. ALWAYS ask clarifying questions before writing -- wait for answers
3. EVERY phase must have automated verification steps (build, test, lint)
4. EVERY changed file must have an exact path -- not "the service layer" or "the controller"
5. The plan must include "What we're NOT doing" -- explicit scope boundaries prevent scope creep
6. The plan must include a rollback procedure -- every change must be reversible
7. NO source code in the plan -- change descriptions only (code snippets for illustration are fine)
8. TESTS FIRST -- any phase that introduces new production behavior must have a test-writing step BEFORE the implementation step (RED before GREEN)
9. YAGNI -- if a phase exists only because "we might need it later," remove it

## Domain Principles Table

| # | Principle | Description | Applied As |
|---|-----------|-------------|------------|
| 1 | **Research First, Always** | Planning from memory or assumptions produces plans that don't match the codebase. The research artifact is the only source of truth. | If no research artifact exists, stop and tell the user to run /rpi-research first. |
| 2 | **Clarifying Questions Prevent Churn** | A plan built on the wrong scope assumption requires /rpi-iterate, which is a second planning session. 5 minutes of questions prevents 30 minutes of rework. | Always ask before writing. Identify scope decisions, approach preferences, testing requirements, and constraints. |
| 3 | **Mechanical Execution Is the Standard** | The implementing agent should not need to think creatively. Every phase should feel mechanical -- read file, make described change, run verification, update checkbox. | If a phase description contains words like "appropriately", "as needed", or "implement X", it is not precise enough. |
| 4 | **Every Phase Must Be Verifiable** | An unverifiable phase is a black box. If the implementation phase can't confirm it worked, it can't stop at the right time or diagnose failures. | Every phase includes at minimum: `dotnet build` (or equivalent) + relevant test command. |
| 5 | **Scope Boundaries Prevent Drift** | "What we're NOT doing" is as important as "What we're doing." Without explicit exclusions, implementation scope expands to include every tangentially related improvement. | Write the exclusion list during planning, before anyone has started implementing. |
| 6 | **Exact Paths, Not Directions** | "Update the authentication service" requires the implementer to find the file. "Update `Features/Auth/Services/TokenValidator.cs:88`" does not. | Every change description includes the file path with optional line number for context. |
| 7 | **Code Snippets Illustrate, Don't Implement** | A plan that shows the exact code to write has become the implementation. A plan that shows REMOVE/ADD markers to illustrate the change gives the implementer precise guidance without doing the work for them. | Use before/after markers in code blocks, not complete method implementations. |
| 8 | **Phase Ordering Respects Dependencies** | Phase 2 may depend on Phase 1's output. Phase ordering must reflect those dependencies. If two phases are truly independent, note that explicitly so the implementer doesn't waste time sequencing. | Add "Implementation note" to each phase describing sequencing requirements. |
| 9 | **Rollback Is Mandatory** | Every implementation must be reversible. A plan without a rollback procedure implicitly assumes the implementation will succeed. This is optimistic engineering. | Document how to revert each phase: git reset path, migration rollback command, feature flag toggle. |
| 10 | **One Bad Plan Line = 100 Bad Code Lines** | The leverage at plan review is the highest in the entire RPI workflow. A wrong file path, a missed integration point, a scope decision resolved incorrectly -- each of these costs 10x more to fix during implementation. | Treat plan review as the most important review in the workflow. |

## Workflow

```
READ
    Load the research artifact from thoughts/shared/research/
    → If no artifact exists: STOP. Tell user to run /rpi-research first.
    Identify key findings: affected files, patterns to follow, open questions answered?

        |
        v

QUESTION
    Ask the user about:
    - Scope decisions (full feature vs. incremental? breaking changes acceptable?)
    - Approach (if research reveals multiple valid paths, present options with tradeoffs)
    - Testing requirements (unit, integration, end-to-end, manual verification?)
    - Constraints (deadlines, deployment windows, dependencies on other work)
    WAIT for answers before proceeding.

        |
        v

DESIGN
    Write a brief Design Discussion (~10-15 lines) covering:
    - Chosen approach and why (what alternatives exist from research, why this one)
    - Phase breakdown rationale (how many phases, what each accomplishes)
    - Key risks or dependencies the plan must accommodate
    Present the Design Discussion to the user BEFORE writing the full plan.
    Wait for feedback or approval before proceeding to WRITE.
    (Catching an approach disagreement here costs 2 minutes; catching it during implementation costs hours.)

    Then decompose into phases:
    - Each phase accomplishes one logical unit (schema change, handler, UI, tests)
    - Each phase is independently verifiable
    - Order phases by dependency (infrastructure before features, features before UI)
    - Identify the "What we're NOT doing" scope boundary
    - For phases introducing new behavior: the first step must be "Write failing tests" (RED)
      followed by "Implement to make tests pass" (GREEN) — never implement before tests exist
    - Apply YAGNI: for each phase, ask "Does this solve a real requirement in scope?"
      If the answer is "we might need it later" — remove the phase

    YAGNI CHECK (before finalizing phase list):
    1. Does every phase correspond to a stated requirement or acceptance criterion?
    2. Are there any "nice to have" phases that don't directly deliver the feature?
    3. Is there any infrastructure being added "just in case"?
    If YES to 2 or 3: remove those phases and add them to "What we're NOT doing".

        |
        v

WRITE
    Write to: thoughts/shared/plans/YYYY-MM-DD-description-slug.md
    Use the plan artifact template (see references/plan-artifact-template.md)
    Include verification commands from references/phase-verification-patterns.md

        |
        v

REPORT
    Tell the user:
    - Artifact path
    - Phase count and brief description of each phase
    - Key decision points they should review
    - Reminder: "Review before running /rpi-implement"
    - "Use /rpi-iterate if adjustments are needed"
```

**Exit criteria:** Plan artifact written with all phases containing exact file paths and verification steps; user reminded to review.

## State Block

```
<rpi-plan-state>
phase: READ | QUESTION | DESIGN | WRITE | REPORT | COMPLETE
topic: [feature being planned]
research_artifact: thoughts/shared/research/YYYY-MM-DD-slug.md
plan_artifact: thoughts/shared/plans/YYYY-MM-DD-description-slug.md
design_discussion_presented: true | false
design_discussion_approved: true | false
clarifying_questions_asked: true | false
clarifying_questions_answered: true | false
phases_designed: [count]
yagni_check_passed: true | false
tdd_phases_identified: [count of phases with test-first steps]
status: in_progress | complete
</rpi-plan-state>
```

## Output Templates

### Plan Artifact

See `references/plan-artifact-template.md` for the complete template.

**Summary structure:**
```markdown
# [Feature Title] — Implementation Plan

## Overview
[What we're doing and why, 2-3 sentences]

## Current state analysis
[Summary from research: key discoveries that affect the plan]

## Desired end state
- [Concrete outcome 1]
- [Concrete outcome 2]

## What we're NOT doing
- [Explicit exclusion 1]
- [Explicit exclusion 2]

## Implementation approach
[Brief rationale for the chosen approach]

---

## Phase 1: [Phase Title]

### Overview
[What this phase accomplishes in 1-2 sentences]

### Changes required

#### 1. [Specific change title]
**File**: `path/to/file.cs`
**Changes**: [Exact description of what to add, remove, or modify]

```csharp
// REMOVE:
public OldMethod() { ... }

// ADD:
public NewMethod(INewDependency dep) { ... }
```

### Success criteria

#### Automated verification
- [ ] `dotnet build --no-restore` compiles without errors
- [ ] `dotnet test --filter "Category=Unit&Feature=X"` passes
- [ ] `dotnet format --verify-no-changes` passes

#### Manual verification (if needed)
- [ ] [Specific navigation or UI check]

**Implementation note**: Must complete before Phase 2 (Phase 2 depends on new type from Phase 1).

---

## Testing strategy
[Unit, integration, regression approach]

## Rollback plan
[How to revert: git commands, migration rollback, feature flag]

## Notes
[Anything else relevant]
```

### Clarifying Questions Template

```
Before I write the plan, I need to clarify a few things:

1. **Scope**: [Specific scope decision from research — e.g., "Should this handle the legacy path or only new records?"]

2. **Approach**: [If multiple valid approaches exist from research — e.g., "Research shows two patterns: Option A (simpler, requires migration) vs Option B (backwards-compatible, more code). Which do you prefer?"]

3. **Testing**: [Testing requirement — e.g., "Should this include integration tests against the real database, or unit tests with mocks?"]

4. **Constraints**: [Any constraints not in research — e.g., "Is there a deployment window constraint for the migration?"]
```

## AI Discipline Rules

### CRITICAL: No Planning Without Research

**WRONG:**
```
User: /rpi-plan "add email notifications"
Agent: I'll plan the email notification feature now.
Phase 1: Add an EmailService...
```

**RIGHT:**
```
User: /rpi-plan "add email notifications"
Agent: I need to read the research artifact first.
[Reads thoughts/shared/research/]
[If not found]: No research artifact found for this topic.
Please run /rpi-research "email notifications" first, then review the results before planning.
```

### REQUIRED: Ask Before Writing

**WRONG:** Writing a plan immediately after reading the research artifact without asking any questions.

**RIGHT:** Identifying the key scope decisions from the research artifact, asking 2-4 clarifying questions, waiting for answers, then writing the plan.

### CRITICAL: Exact Paths, Not Directions

**WRONG:**
```
#### Change the notification service
Update the service to accept the new parameter.
```

**RIGHT:**
```
#### 1. Add `recipientEmail` parameter to `SendNotificationAsync`
**File**: `Features/Notifications/Services/NotificationService.cs`
**Changes**: Add `string recipientEmail` parameter to `SendNotificationAsync` method at line 34.
Update the private `BuildEmailMessage` call at line 41 to pass `recipientEmail`.
```

## Anti-Patterns Table

| # | Anti-Pattern | Why It Fails | Correct Approach |
|---|-------------|-------------|-----------------|
| 1 | **Planning without research** | Plan doesn't match codebase; implementer discovers problems during execution | Always read research artifact first; stop if none exists |
| 2 | **Skipping clarifying questions** | Plan makes wrong scope assumption; requires /rpi-iterate to fix | Ask 2-4 questions before writing; wait for answers |
| 3 | **Phases without verification** | Implementation has no way to confirm progress; failures go undetected | Every phase includes build + relevant test command at minimum |
| 4 | **Vague file descriptions** | Implementer must discover the file; adds judgment and exploration to "mechanical" execution | Exact file paths in every change description |
| 5 | **No "What we're NOT doing"** | Scope creeps during implementation; adjacent improvements get added | Write exclusion list during planning, before implementation starts |
| 6 | **No rollback plan** | An implementation failure has no recovery path; forces risky manual cleanup | Document git reset paths, migration rollback commands, feature flags |
| 7 | **Writing code in the plan** | Plan becomes the implementation; misses the point of phase separation | Change descriptions and illustrative snippets only -- no complete implementations |
| 8 | **Single monolithic phase** | All-or-nothing execution; one failure blocks everything | Break into independently verifiable phases; smaller is more recoverable |
| 9 | **500+ line plans per phase** | Implementer can't hold the phase in working memory; errors of omission increase | Each phase should be ≤ 100 lines; split large phases |
| 10 | **Ordering phases arbitrarily** | Phase N may depend on types or data created in Phase N+1 | Respect dependencies: infrastructure → domain → application → UI → tests |

## Error Recovery

### No research artifact exists

```
Symptoms: User runs /rpi-plan but thoughts/shared/research/ is empty or irrelevant

Recovery:
1. Tell the user clearly: "No research artifact found for this topic."
2. Instruct them to run /rpi-research "[topic]" in a new session first
3. Do NOT proceed to plan from memory, assumptions, or general knowledge
4. Do NOT offer to "quickly research" in the same session (defeats phase isolation)
```

### Research artifact exists but open questions are unresolved

```
Symptoms: Research artifact has an "## Open questions" section with unresolved items

Recovery:
1. Surface the open questions in your clarifying questions step
2. Add them to the question list: "The research identified these open questions..."
3. Do not write the plan until the user answers the open questions
4. If the user says "just pick one," document the choice in the plan's Implementation Approach
```

### Plan becomes too large during design

```
Symptoms: Designing the phases and realizing the plan will be 1000+ lines

Recovery:
1. Split into two plans: Plan A (foundation) and Plan B (extension)
2. Plan A should be independently deployable/valuable
3. Note in Plan A's Notes section that Plan B follows
4. Do not try to fit everything into one plan file
```

### When to Split a Plan (self-assessment)

Ask these questions before writing. If more than one is YES, split:
1. Will this plan take more than one working session to implement?
2. Does this plan touch more than 3 vertical slices or feature areas?
3. Are there phases that could be deployed independently and would deliver value on their own?
4. Is the plan approaching 10+ phases? (10+ phases correlates with high implementation failure rate)
5. Would a reviewer need more than 20 minutes to review the full plan?

When splitting: Plan A should be the smallest independently valuable deliverable. Plan B is everything else. Name them descriptively: `2026-04-01-email-notifications-phase-a-infrastructure.md` and `2026-04-01-email-notifications-phase-b-ui.md`.

## Integration with Other Skills

| Skill | Relationship |
|-------|-------------|
| `rpi-research` | Produces the artifact this skill consumes. Must complete before planning. |
| `rpi-implement` | Consumes the plan this skill produces. Executes phases mechanically. |
| `rpi-iterate` | Updates this skill's output when feedback or discovered issues require plan changes. |
| `task-decomposition` | For very large features, use task-decomposition to break the plan into parallel workstreams that multiple implementers can execute concurrently. |
| `ef-migration-manager` | For phases involving EF Core migrations, load this skill for migration safety checks, dry-run verification patterns, and rollback procedures. |
| `dotnet-vertical-slice` | When planning new vertical slices in .NET, load this skill for the canonical file/folder structure and DI registration pattern. |
| `tdd-cycle` | When planning phases that require RED-GREEN-REFACTOR discipline, load this skill to structure the test-write → implement → refactor steps within each phase. |

## .NET/Blazor Adapter Notes

When planning for a .NET/Blazor codebase, apply these structural rules:

### Phase Boundaries for .NET
- **One phase per vertical slice** — don't mix command handler changes with query handler changes in the same phase
- **EF Core migrations get their own phase** — never combine a model change and a migration in the same phase; the migration phase runs after the model phase is verified
- **DI registration in a dedicated step** — include "register new service in DI container" as an explicit step, not an afterthought. Missed DI registration is the #1 cause of "works on my machine" failures.
- **Telerik component changes get their own phase** — Telerik components have many interdependencies; isolate them to prevent cascading failures

### TDD Phase Structure for .NET
Each phase introducing new behavior should follow this pattern:

```
#### Step 1: Write failing tests
**File**: `tests/Unit/Features/[Feature]/[Handler]Tests.cs`
**Changes**: Add test method `[MethodName]_[Scenario]_[ExpectedBehavior]` that
asserts the new behavior. Test should fail (RED) at this point.
Verification: `dotnet test --filter "FullyQualifiedName~[TestName]"` → FAIL expected

#### Step 2: Implement to pass tests
**File**: `Features/[Feature]/[Handler].cs`
**Changes**: [implementation description]
Verification: `dotnet test --filter "FullyQualifiedName~[TestName]"` → PASS required
```

### FreeMediator Pipeline — planning implications
- When adding a new command handler, plan an explicit verification step: "confirm handler is discovered by assembly scanning"
- When a new pipeline behavior is added, plan a verification step for each handler type it affects
- Pipeline behaviors fire on ALL commands/queries — scope changes carefully; add to "What we're NOT doing" if pipeline-wide changes are out of scope

## Python Adapter Notes

When planning for a Python codebase, apply these structural rules:

### Phase Boundaries for Python
- **One phase per module or feature area** — don't mix route handler changes with Pydantic
  schema changes in the same phase; schema changes have downstream ripple effects
- **Pydantic model changes before handler changes** — a handler phase assumes the schema it
  references is already correct; schema phase must verify first
- *If using Alembic:* **Migrations get their own phase** — never combine a SQLAlchemy model
  change and an Alembic revision in the same phase; the migration phase runs after the model
  phase is verified
- **FastAPI dependency registration in a dedicated step** — include "wire new dependency into
  router `Depends()` chain" as an explicit step; missing `Depends()` wiring is the #1 source
  of "works in unit tests, fails at runtime" failures in FastAPI projects
- > **Flask callout:** Include "register Blueprint with `app.register_blueprint()`" as an
  > explicit step in any phase that adds a new Blueprint.

### TDD Phase Structure for Python
Each phase introducing new behavior should follow this pattern:

```
#### Step 1: Write failing tests
**File**: `tests/[feature]/test_[module].py`
**Changes**: Add test function `test_[scenario]_[expected_behavior]` that asserts the
new behavior. Test should fail (RED) at this point.
Verification: `pytest tests/[feature]/test_[module].py::test_[name] -v` → FAIL expected

#### Step 2: Implement to pass tests
**File**: `src/[feature]/[module].py`
**Changes**: [implementation description]
Verification: `pytest tests/[feature]/test_[module].py::test_[name] -v` → PASS required
```

### Alembic Migration Phase Structure (if using Alembic)
```
#### Step 1: Generate migration revision
**Command**: `alembic revision --autogenerate -m "[descriptive-name]"`
**Action**: Review the generated migration script in `alembic/versions/` — verify only
expected schema changes are present; delete any spurious detected changes
Verification: `alembic check` → no pending changes beyond the new revision

#### Step 2: Apply migration
**Command**: `alembic upgrade head`
Verification: `alembic current` shows the new revision as current head
Rollback: `alembic downgrade -1`
```

### pytest-asyncio — planning implications
- When adding async route handlers or async service methods, plan a verification step
  that confirms the test is decorated with `@pytest.mark.asyncio` (or `asyncio_mode = "auto"`
  is set in `pytest.ini` / `pyproject.toml`)
- Async tests that accidentally run synchronously pass silently — add a verification step:
  `pytest --co -q` to confirm the test is collected as an async test
