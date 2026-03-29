# Plan Artifact Template

Use this template when writing plan artifacts to `thoughts/shared/plans/YYYY-MM-DD-description-slug.md`.

**Target length:** Each phase ≤ 100 lines. Whole plan ≤ 500 lines. Split features needing more into Plan A + Plan B.

---

```markdown
# [Feature Title] — Implementation Plan

**Created:** YYYY-MM-DD
**Research:** thoughts/shared/research/YYYY-MM-DD-topic-slug.md
**Status:** ready-for-review | in-progress | complete

---

## Overview
[What we're building and why — 2-3 sentences. Reference the research artifact's summary.
Example: "Add automated email notifications to the annual review workflow. Currently the system
creates review records but sends no notifications. This plan adds notification dispatch
after a review is submitted, using the existing IEmailService infrastructure."]

## Current state analysis
[Key discoveries from research that constrain or inform the plan.
Do not reproduce the full research artifact — summarize the decision-relevant findings.
Example: "IEmailService exists and is registered in DI (Infrastructure/ServiceExtensions.cs:44).
ReviewHandler.Handle() already persists the review record (Features/Review/Handlers/ReviewHandler.cs:38).
No notification dispatch exists today. Tests use NSubstitute mocking."]

## Desired end state
- [Concrete outcome 1 — measurable]
- [Concrete outcome 2 — measurable]
- [etc.]

Example:
- Email sent to reviewer and reviewee when a review is submitted
- Email content includes reviewer name, reviewee name, and submission timestamp
- Notification dispatch is tested with unit tests (mocked IEmailService)
- All existing tests continue to pass

## What we're NOT doing
[Explicit exclusions — prevent scope creep during implementation]
- [Exclusion 1]
- [Exclusion 2]

Example:
- NOT adding email preferences or unsubscribe functionality (separate feature)
- NOT changing the existing review persistence logic
- NOT adding email templates or HTML formatting (plain text only in this plan)
- NOT modifying the ReviewController (handler-only change)

## Implementation approach
[1-2 sentences explaining the chosen approach and why, especially if research revealed alternatives.
Example: "Dispatch notifications directly from ReviewHandler.Handle() after the save succeeds,
rather than via domain events, to avoid introducing new infrastructure complexity (research
found no existing event bus)."]

---

## Phase 1: [Phase Title]

### Overview
[1-2 sentences: what this phase accomplishes and why it comes first.]

### Changes required

#### 1. [Specific change title]
**File**: `path/to/file.cs`
**Changes**: [Precise description of what to add, remove, or modify. Include line numbers for context.]

```csharp
// REMOVE (line 34):
public async Task<Result<ReviewDto>> Handle(CreateReviewCommand command, CancellationToken ct)
{

// ADD:
public async Task<Result<ReviewDto>> Handle(
    CreateReviewCommand command,
    CancellationToken ct,
    IEmailService emailService)  // injected via constructor — see change 2
{
```

#### 2. [Next change in this phase]
**File**: `path/to/other-file.cs`
**Changes**: [Description]

### Success criteria

#### Automated verification
- [ ] `dotnet build --no-restore` — 0 errors, 0 warnings
- [ ] `dotnet test --filter "Category=Unit&Feature=Review"` — all pass
- [ ] `dotnet format --verify-no-changes` — clean

#### Manual verification (if needed)
- [ ] [Specific UI check or runtime behavior to confirm]

**Implementation note**: [Sequencing note — e.g., "Must complete before Phase 2; Phase 2 depends on the constructor change in this phase."]

---

## Phase 2: [Phase Title]

### Overview
[What this phase accomplishes]

### Changes required

#### 1. [Change title]
**File**: `path/to/file.cs`
**Changes**: [Description]

### Success criteria

#### Automated verification
- [ ] `dotnet build --no-restore`
- [ ] `dotnet test --filter "Feature=Review"` — including new tests from this phase
- [ ] `dotnet format --verify-no-changes`

**Implementation note**: [Dependencies]

---

## Phase N: Final verification

### Overview
Full integration verification across all phases.

### Changes required

#### 1. Search for remaining TODOs
```bash
grep -rn "TODO\|FIXME\|HACK" Features/Review/
```
Expected: no results from this implementation.

### Success criteria

#### Automated verification
- [ ] `dotnet build` — solution-wide
- [ ] `dotnet test` — all tests pass
- [ ] `dotnet format --verify-no-changes`
- [ ] `dotnet ef database update --dry-run` (if migrations involved)

---

## Testing strategy
[How the feature is tested: what unit tests, what integration tests, what manual checks.
Reference the test pattern from the research artifact.]

Example:
- Unit tests mock `IEmailService` using NSubstitute; verify `SendAsync` called with correct parameters
- Integration tests use `TestEmailService` (in-memory) to verify end-to-end flow
- No new test infrastructure required; follows pattern in `tests/Unit/Features/Review/`

## Rollback plan
[How to revert if the implementation fails or is rejected.]

Example:
- All changes are in `Features/Review/` — `git restore Features/Review/` reverts all
- No database migrations in this plan — no migration rollback needed
- Feature flag: set `Features:ReviewNotifications:Enabled = false` in appsettings to disable without revert

## Notes
[Anything else relevant — external dependencies, deployment instructions, communication needed.]
```

---

## Naming conventions for plan files

```
YYYY-MM-DD-description-slug.md

Examples:
2026-03-29-annual-review-email-notifications.md
2026-03-29-auth-middleware-token-consolidation.md
2026-03-29-phase-a-payment-service-migration.md
```

Use lowercase kebab-case. Be descriptive enough that the file name is self-explanatory.

## Phase sizing guidelines

| Phase size | Guidance |
|-----------|----------|
| ≤ 3 file changes | Good — independently verifiable, easy to review |
| 4-6 file changes | Acceptable — may be worth splitting if the changes are logically distinct |
| 7+ file changes | Too large — split into two phases |

Exception: A single refactor touching many files (e.g., rename, extract interface) may be one large phase if it is truly atomic.

## Verification command reference

See `references/phase-verification-patterns.md` for project-specific verification commands.
