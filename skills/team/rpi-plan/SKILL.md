---
name: rpi-plan
description: >
  RPI Plan phase -- converts a research artifact into a phased implementation plan with exact
  file paths, change descriptions, and per-phase verification steps. Use when converting a research artifact into a phased implementation plan. Trigger phrases: "/rpi-plan feature",
  "create implementation plan", "plan the changes for X", "design the implementation".
---

# RPI Plan

> "Plans are worthless, but planning is everything."
> -- Dwight D. Eisenhower

> "A plan precise enough to execute mechanically is the goal. If the implementer has to invent anything, the plan failed."

## Core Philosophy

The Plan phase converts the research artifact into an implementation contract. The implementing agent must be able to execute the plan mechanically -- without judgment, invention, or discovery. If the plan requires the implementer to figure out what to do, the plan is incomplete.

**Non-Negotiable Constraints:**
1. ALWAYS read the research artifact first -- never plan from memory or assumptions
2. ALWAYS ask clarifying questions before writing -- wait for answers
3. EVERY phase must have automated verification steps (build, test, lint)
4. EVERY changed file must have an exact path -- not "the service layer" or "the controller"
5. The plan must include "What we're NOT doing" -- explicit scope boundaries prevent scope creep
6. The plan must include a rollback procedure -- every change must be reversible
7. NO source code in the plan -- change descriptions only (code snippets for illustration are fine)
8. TESTS FIRST -- any phase introducing new production behavior must have a test-writing step BEFORE the implementation step (RED before GREEN)
9. YAGNI -- if a phase exists only because "we might need it later," remove it

## Domain Principles Table

| # | Principle | Applied As |
|---|-----------|------------|
| 1 | **Research First, Always** | If no research artifact exists, stop and tell the user to run /rpi-research first. |
| 2 | **Clarifying Questions Prevent Churn** | Always ask before writing. Identify scope decisions, approach preferences, testing requirements, and constraints. |
| 3 | **Mechanical Execution Is the Standard** | If a phase description contains "appropriately", "as needed", or "implement X", it is not precise enough. |
| 4 | **Every Phase Must Be Verifiable** | Every phase includes at minimum: `dotnet build` (or equivalent) + relevant test command. |
| 5 | **Scope Boundaries Prevent Drift** | Write the "What we're NOT doing" exclusion list during planning, before implementation starts. |
| 6 | **Exact Paths, Not Directions** | Every change description includes the file path with optional line number for context. |
| 7 | **Code Snippets Illustrate, Don't Implement** | Use REMOVE/ADD markers to illustrate the change — not complete method implementations. |
| 8 | **Phase Ordering Respects Dependencies** | Add "Implementation note" to each phase describing sequencing requirements. |
| 9 | **Rollback Is Mandatory** | Document how to revert each phase: git reset path, migration rollback command, feature flag toggle. |
| 10 | **One Bad Plan Line = 100 Bad Code Lines** | Treat plan review as the most important review in the RPI workflow. |

## Workflow

### READ
Load the research artifact from `thoughts/shared/research/`. If none exists, stop — tell the user to run /rpi-research first. Identify key findings: affected files, patterns to follow, open questions answered.

### QUESTION
Ask the user about: scope decisions (full feature vs. incremental? breaking changes acceptable?), approach (present options with tradeoffs if research reveals multiple valid paths), testing requirements (unit, integration, end-to-end?), constraints (deadlines, deployment windows, dependencies). **Wait for answers before proceeding.**

### DESIGN
Write a brief Design Discussion (~10–15 lines) covering: chosen approach and why, phase breakdown rationale, key risks or dependencies. **Present the Design Discussion before writing the full plan. Wait for feedback or approval.** Catching an approach disagreement here costs 2 minutes; catching it during implementation costs hours.

Decompose into phases — each accomplishes one logical unit (schema change, handler, UI, tests), is independently verifiable, and is ordered by dependency (infrastructure before features, features before UI). For phases introducing new behavior, the first step must be "Write failing tests" (RED) followed by "Implement to make tests pass" (GREEN).

**YAGNI Check (before finalizing phase list):**
1. Does every phase correspond to a stated requirement or acceptance criterion?
2. Are there any "nice to have" phases that don't directly deliver the feature?
3. Is there any infrastructure being added "just in case"?

If YES to 2 or 3: remove those phases and add them to "What we're NOT doing."

### WRITE
Write to: `thoughts/shared/plans/YYYY-MM-DD-description-slug.md`. Use the plan artifact template (see `references/plan-artifact-template.md`). Include verification commands from `references/phase-verification-patterns.md`.

### REPORT
Tell the user: artifact path, phase count and brief description of each phase, key decision points to review, reminder to review before running /rpi-implement.

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

**Plan artifact structure:** Title, Created date, Research path, Status, Ticket, Branch, Git commit → Overview (2–3 sentences) → Current state analysis (from research) → Desired end state (bullet list) → What we're NOT doing (bullet list) → Implementation approach (rationale) → Phase N sections (Overview, Changes required with exact file paths and REMOVE/ADD markers, Success criteria with automated verification commands and manual checks, Implementation note on sequencing) → Testing strategy → Rollback plan → Notes.

**Clarifying Questions format:** Number each question. Identify: (1) scope decision from research, (2) approach options with tradeoffs if multiple valid paths exist, (3) testing requirement, (4) constraints not captured in research.

Full templates: `references/plan-artifact-template.md` | Phase verification commands: `references/phase-verification-patterns.md`

## AI Discipline Rules

**No Planning Without Research:** If no research artifact is found for the topic, stop immediately. Tell the user to run /rpi-research first. Do not plan from memory, assumptions, or general knowledge. Do not offer to "quickly research" in the same session — that defeats phase isolation.

**Ask Before Writing:** After reading the research artifact, identify the key scope decisions, ask 2–4 clarifying questions, wait for answers. Writing a plan immediately without asking is the fastest path to /rpi-iterate.

**Exact Paths, Not Directions:** Every change description includes the file path. "Update the notification service" is wrong. "Add `recipientEmail` parameter to `SendNotificationAsync` in `Features/Notifications/Services/NotificationService.cs:34`" is correct.

## Anti-Patterns Table

| # | Anti-Pattern | Why It Fails | Correct Approach |
|---|-------------|-------------|-----------------|
| 1 | **Planning without research** | Plan doesn't match codebase; implementer discovers problems during execution | Always read research artifact first; stop if none exists |
| 2 | **Skipping clarifying questions** | Plan makes wrong scope assumption; requires /rpi-iterate to fix | Ask 2–4 questions before writing; wait for answers |
| 3 | **Phases without verification** | Implementation has no way to confirm progress; failures go undetected | Every phase includes build + relevant test command at minimum |
| 4 | **Vague file descriptions** | Implementer must discover the file; adds judgment to "mechanical" execution | Exact file paths in every change description |
| 5 | **No "What we're NOT doing"** | Scope creeps during implementation; adjacent improvements get added | Write exclusion list during planning, before implementation starts |
| 6 | **No rollback plan** | An implementation failure has no recovery path | Document git reset paths, migration rollback commands, feature flags |
| 7 | **Writing code in the plan** | Plan becomes the implementation; misses the point of phase separation | Change descriptions and illustrative snippets only |
| 8 | **Single monolithic phase** | All-or-nothing execution; one failure blocks everything | Break into independently verifiable phases |
| 9 | **500+ line plans per phase** | Implementer can't hold the phase in working memory | Each phase should be ≤ 100 lines; split large phases |
| 10 | **Ordering phases arbitrarily** | Phase N may depend on types created in Phase N+1 | Respect dependencies: infrastructure → domain → application → UI → tests |

## Error Recovery

**No research artifact exists:** Tell the user clearly that no research artifact was found. Instruct them to run /rpi-research first. Do not proceed to plan from memory, assumptions, or general knowledge.

**Research artifact has unresolved open questions:** Surface open questions in the clarifying questions step. Do not write the plan until the user answers them. If the user says "just pick one," document the choice in the plan's Implementation Approach section.

**Plan becomes too large:** Split into Plan A (foundation, independently deployable) and Plan B (extension). Note in Plan A's Notes section that Plan B follows. Name descriptively: `2026-04-01-email-notifications-phase-a-infrastructure.md`.

**When to split a plan (self-assessment):** If more than one is YES, split: (1) More than one working session to implement? (2) Touches more than 3 vertical slices or feature areas? (3) Phases that could be deployed independently? (4) 10+ phases? (5) Reviewer needs more than 20 minutes to review?

## Integration with Other Skills

| Skill | Relationship |
|-------|-------------|
| `rpi-research` | Produces the artifact this skill consumes. Must complete before planning. |
| `rpi-implement` | Consumes the plan this skill produces. Executes phases mechanically. |
| `rpi-iterate` | Updates this skill's output when feedback or discovered issues require plan changes. |
| `task-decomposition` | For very large features, break the plan into parallel workstreams for concurrent execution. |
| `ef-migration-manager` | For phases involving EF Core migrations — safety checks, dry-run verification, rollback procedures. |
| `dotnet-vertical-slice` | When planning new vertical slices in .NET — canonical file/folder structure and DI registration pattern. |
| `tdd-cycle` | When planning phases requiring RED-GREEN-REFACTOR discipline — structure test-write → implement → refactor steps. |

## .NET/Blazor Adapter Notes

**Phase boundaries:** One phase per vertical slice — don't mix command handler changes with query handler changes. EF Core migrations get their own phase (never combined with model change). DI registration in a dedicated step — missed DI registration is the #1 "works on my machine" failure. Telerik component changes get their own phase to prevent cascading failures.

**TDD phase structure for .NET:**

```
#### Step 1: Write failing tests
**File**: `tests/Unit/Features/[Feature]/[Handler]Tests.cs`
**Changes**: Add test method `[MethodName]_[Scenario]_[ExpectedBehavior]` asserting new behavior.
Verification: `dotnet test --filter "FullyQualifiedName~[TestName]"` → FAIL expected

#### Step 2: Implement to pass tests
**File**: `Features/[Feature]/[Handler].cs`
**Changes**: [implementation description]
Verification: `dotnet test --filter "FullyQualifiedName~[TestName]"` → PASS required
```

**FreeMediator implications:** When adding a new command handler, include explicit verification step: "confirm handler is discovered by assembly scanning." When adding a pipeline behavior, verify against each handler type it affects. Pipeline behaviors fire on ALL commands/queries — scope changes carefully.

## Python Adapter Notes

**Phase boundaries:** One phase per module or feature area. Pydantic model changes before handler changes — handler phase assumes schema is already correct. Alembic migrations get their own phase (never combined with SQLAlchemy model change). FastAPI `Depends()` wiring in a dedicated step — missing `Depends()` is the #1 "works in unit tests, fails at runtime" failure.

**TDD phase structure for Python:**

```
#### Step 1: Write failing tests
**File**: `tests/[feature]/test_[module].py`
**Changes**: Add test function `test_[scenario]_[expected_behavior]` asserting new behavior.
Verification: `pytest tests/[feature]/test_[module].py::test_[name] -v` → FAIL expected

#### Step 2: Implement to pass tests
**File**: `src/[feature]/[module].py`
**Changes**: [implementation description]
Verification: `pytest tests/[feature]/test_[module].py::test_[name] -v` → PASS required
```

**Alembic migration phase structure:**

```
#### Step 1: Generate migration revision
**Command**: `alembic revision --autogenerate -m "[descriptive-name]"`
**Action**: Review generated script — verify only expected schema changes are present.
Verification: `alembic check` → no pending changes beyond the new revision

#### Step 2: Apply migration
**Command**: `alembic upgrade head`
Verification: `alembic current` shows new revision as current head
Rollback: `alembic downgrade -1`
```

**pytest-asyncio:** When adding async handlers, include a verification step confirming the test is decorated with `@pytest.mark.asyncio` (or `asyncio_mode = "auto"` is configured). Async tests that run synchronously pass silently — add `pytest --co -q` to confirm the test is collected as async.
