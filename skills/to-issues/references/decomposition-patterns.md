# Issue Decomposition Patterns

Strategies for slicing a feature into independently-deliverable GitHub Issues.

## Pattern 1: Vertical slice (preferred)

Each issue delivers an end-to-end slice of user value — thin but complete.

```
Issue 1: User can create an account (no email verification)
Issue 2: User receives email verification after signup
Issue 3: User can reset password via email
```

Good for: feature development, user-facing work
Risk: each slice must be independently shippable without depending on the next

## Pattern 2: Horizontal layer (use sparingly)

Split by technical layer: data model → API → UI.

```
Issue 1: Add Order table and migrations
Issue 2: Implement POST /orders endpoint
Issue 3: Build order creation form
```

Good for: infrastructure-heavy work, when API must be stable before UI starts
Risk: each layer has no user value until the stack is complete

## Pattern 3: Risk-first

Lead with the highest-risk, most uncertain work.

```
Issue 1: Spike — validate payment provider integration (timebox: 1 day)
Issue 2: Implement payment flow (depends on #1)
Issue 3: Add receipt email (depends on #2)
```

Good for: features with technical unknowns, new external integrations
Risk: spike may invalidate the plan; keep it short and timebox it

## Pattern 4: Happy path first, then edge cases

```
Issue 1: User can upload a single file (happy path)
Issue 2: Handle upload errors (network failure, invalid type, size limit)
Issue 3: Support bulk upload (multiple files)
```

Good for: complex features with many error modes
Risk: error handling issues can be large — split them if needed

## Issue size guidance

| Size | Duration | When to use |
|------|----------|------------|
| S | < 4 hours | Focused change, one file, clear outcome |
| M | 1–2 days | Multiple files, one workflow, clear scope |
| L | 3–5 days | Larger scope — split if possible |
| XL | > 5 days | Always split — scope is not clear enough |

## Anti-patterns

- **"Implement authentication"** — too large; split into create-account, login, logout, password-reset, session-management
- **"Fix all bugs"** — not a valid issue; create one issue per bug with reproduction steps
- **"Refactor X"** — split by: extract module, rename types, update callers, update tests
