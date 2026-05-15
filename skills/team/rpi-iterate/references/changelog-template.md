# Change Log Template

The change log section is added to the bottom of a plan file during every /rpi-iterate session.

## Placement

Add the change log at the very end of the plan file, after the Notes section.

## Template

```markdown
---

## Change log

### [YYYY-MM-DD] — [one-line description of the feedback that triggered this update]

**Feedback received:**
[Exact feedback text or paraphrase]

**Phases updated:**
- Phase [N]: [What changed] — Reason: [why this feedback required this change]
- Phase [M]: [Downstream update required by Phase N change] — Reason: [cascading impact]

**Phases preserved (complete — not touched):**
- Phase 1, Phase 2 — already executed; not modified

**Phases unaffected:**
- Phase [X] — feedback did not impact this phase

**Scope changes:**
- Added to "What we're NOT doing": [if scope was narrowed]
- Removed from "What we're NOT doing": [if scope was expanded, with rationale]

**Research conducted:**
- [If targeted subagent research was done]: Spawned @rpi-code-analyzer for [area]; found [key discovery]
- [If no research needed]: No additional research required
```

## Multiple iterations

If the plan has been iterated multiple times, add each new entry at the top of the change log (newest first):

```markdown
## Change log

### [YYYY-MM-DD] — [second iteration description]

[... second iteration details ...]

---

### [YYYY-MM-DD] — [first iteration description]

[... first iteration details ...]
```

## Example

```markdown
## Change log

### 2026-03-29 — Use existing EmailQueueService instead of direct IEmailService injection

**Feedback received:**
"Don't inject IEmailService directly into the handler. Use EmailQueueService so notifications
go through the queue for retry support."

**Phases updated:**
- Phase 1: Changed constructor injection from `IEmailService` to `IEmailQueueService`
  — Reason: feedback specifies queue-based delivery
- Phase 1: Updated `SendNotificationAsync` call to `EnqueueNotificationAsync`
  — Reason: IEmailQueueService uses async queue method, not direct send
- Phase 2: Updated test mocks from `IEmailService` to `IEmailQueueService`
  — Reason: downstream impact from Phase 1 change

**Phases preserved (complete — not touched):**
None — no phases were complete at time of iteration.

**Phases unaffected:**
- Phase 3 (final verification) — no changes to verification commands

**Scope changes:**
None

**Research conducted:**
Spawned @rpi-file-locator for "EmailQueueService". Found:
- `Infrastructure/Email/EmailQueueService.cs` (88 lines) — implements `IEmailQueueService`
- Registered in `Infrastructure/ServiceExtensions.cs:61`
```

## When to include the change log vs. skip it

**Always include:** When any phase content is modified.

**Skip only if:** The iteration corrected a typo or formatting issue without changing any phase's scope, file paths, or verification steps.

When in doubt, include it. The change log costs very little to write and is valuable for anyone reviewing the plan's evolution.
