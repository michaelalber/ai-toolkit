# Research Artifact Template

Use this template when writing research artifacts to `thoughts/shared/research/YYYY-MM-DD-topic-slug.md`.

**Target length:** 150-250 lines. Shorter is better. Every line should contain information the plan phase needs.

---

```markdown
---
date: YYYY-MM-DDTHH:MM:SS
repository: [repo-name]
topic: "[exact topic string from /rpi-research command]"
branch: [git branch at time of research, e.g., main]
git_commit: [short commit hash, e.g., a1b2c3d]
tags: [research, tag-1, tag-2]
status: complete
---

# Research: [Topic]

## Research question
[What we investigated — 1-2 sentences. Be specific: "How does the annual review workflow
create notification records, and what infrastructure already exists for email delivery?"]

## Summary
[2-3 paragraphs. This is the most important section — the planner may read only this.
Cover: what exists, where it lives, what patterns govern it, what is missing or unclear.
No opinions. No suggestions. Only what is true about the current codebase.]

## Detailed findings

### 1. [Component/Area Name]
[2-4 sentences describing what this component does and its role in the topic.]

**Key files:**
- `path/to/core-file.cs` (142 lines) — [what it contains, key types]
- `path/to/interface.cs` (28 lines) — [what interface it defines]

**Key types:**
- `TypeName` (`path/to/file.cs:42`) — [what it represents]
- `MethodSignature(param: Type): ReturnType` (`path/to/file.cs:67`) — [what it does]

**Flow:**
1. Entry at `Controller.Action` (`file.cs:15`)
2. Dispatched to `Handler.Handle` via MediatR (`handler.cs:28`)
3. Persists via `DbContext.EntitySet.Add()` (`handler.cs:44`)

### 2. [Next Component/Area]
[Same structure as above]

### 3. [Tests]
**Location:** `tests/Unit/Features/[Feature]/` and `tests/Integration/Features/[Feature]/`
**Naming:** `MethodName_Scenario_ExpectedBehavior`
**Mocking:** NSubstitute (`Substitute.For<IInterface>()`)
**Coverage:** [what is tested vs. what is not tested]

## Code references

### Core implementation
- `Features/[Feature]/Commands/[Command].cs` — [description]
- `Features/[Feature]/Handlers/[Handler].cs` — [description]

### Integration points
- `Infrastructure/[Service].cs` — [what external system it connects to]
- `appsettings.json:[ConfigKey]` — [what configuration it reads]

### Tests
- `tests/Unit/Features/[Feature]/[Test].cs` — [what it covers]
- `tests/Integration/[Feature]/[Test].cs` — [what it covers]

## Key design patterns
1. [Pattern name]: [where it appears, e.g., "CQRS: all writes via MediatR commands in Features/*/Commands/"]
2. [Pattern name]: [where it appears]
3. [Convention: e.g., "Vertical slice: each feature folder contains handler, validator, DTO, and tests"]

## Open questions
[List every unverified assumption and human-judgment item. These must be resolved before planning.]

1. [Question requiring human judgment — e.g., "Should the plan consolidate the duplicated validation logic, or is the duplication intentional?"]
2. [Unverified assumption — e.g., "Could not locate the IEmailSender registration — may not exist yet or may use different naming"]
3. [Scope decision needed — e.g., "Does this change need to be backwards-compatible with the legacy workflow or can it break it?"]

## Dependencies & Risks
[Things outside this feature's control that could affect planning or implementation.]

- **External dependency**: [e.g., "Feature requires a third-party API that may have rate limits — not investigated"]
- **Migration risk**: [e.g., "Three tables affected — rollback requires coordinated migration reversal"]
- **Test gap**: [e.g., "No integration tests exist for this area — plan should include adding them"]
- **Unknown**: [e.g., "Could not determine if the legacy workflow is still in use — requires human confirmation"]
```

---

## Naming conventions for artifact files

```
YYYY-MM-DD-topic-slug.md

Examples:
2026-03-29-annual-review-notification-workflow.md
2026-03-29-auth-middleware-token-validation.md
2026-03-29-ef-core-migration-strategy.md
```

Use lowercase kebab-case for the slug. Derive it from the research topic string.

## What NOT to include

- Opinions about code quality ("this is poorly designed")
- Suggestions for improvement ("should be refactored")
- Implementation proposals ("we could add a service")
- Comparisons to other approaches ("unlike the standard pattern")
- Speculation about intent ("they probably did this because")

All of these belong in open questions if they represent genuine uncertainties, or in the plan if they represent decisions.
