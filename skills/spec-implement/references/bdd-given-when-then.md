# BDD Given-When-Then — Reference

Source: Behavior-Driven Development (Dan North, 2003); *Specification by Example* (Gojko Adzic)

## The Format

```
GIVEN  [context — the world state before the action]
WHEN   [action — the event or trigger]
THEN   [observable outcome — what must be verifiably true afterward]
```

Every criterion in a Criteria Manifest maps to exactly one GIVEN/WHEN/THEN triple.

---

## Rules for Binary Verifiability

A criterion is binary when an independent observer can determine pass or fail from test output alone, without asking anyone.

| Test | Question to ask |
|---|---|
| **Observation** | Can the outcome be verified by reading test output, not by human judgment? |
| **Specificity** | Does THEN name exact values, formats, status codes, or messages — not "appropriate" or "reasonable"? |
| **Atomicity** | Does the criterion describe one behavior, not two behaviors joined by "and"? |

**Fail indicators** — any of these disqualify a criterion:

- THEN contains "should", "appropriate", "reasonable", "graceful", "fast", "user-friendly"
- THEN requires a human to decide if it passed
- THEN describes two different outcomes (split into two criteria)
- GIVEN is so broad it admits unrelated failures (narrow it)

---

## Conversion Examples

| Vague requirement | Binary GIVEN/WHEN/THEN |
|---|---|
| "Validate user input" | GIVEN a registration form / WHEN username contains '!' / THEN HTTP 400 `{error: "Username may only contain letters, numbers, and underscores"}` |
| "Handle API errors gracefully" | GIVEN the upstream API is unavailable / WHEN a user submits a request / THEN HTTP 503 `{error: "Service temporarily unavailable", retryAfter: 30}` |
| "Show a confirmation" | GIVEN a valid order is submitted / WHEN the submit button is clicked / THEN a banner appears: "Order #[id] confirmed" and persists for 3 seconds |
| "Rate limit the endpoint" | GIVEN a user has made 100 requests in the current minute / WHEN the 101st request arrives / THEN HTTP 429 `{error: "Rate limit exceeded", retryAfter: 60}` |
| "The search should be fast" | GIVEN an index of 10,000 items / WHEN a full-text search is submitted / THEN results are returned within 200ms at p95 |

---

## Decomposition Rules

### One behavior per criterion

If the THEN clause contains "and", split:

```
BAD:  THEN the user is created AND a welcome email is sent
GOOD: THEN the user record exists in the database with status "active"
GOOD: THEN a welcome email is dispatched to the registered address
```

### Context narrows, not expands

GIVEN should be the minimal context that makes the behavior deterministic:

```
BAD:  GIVEN the system is running
GOOD: GIVEN a user with email "test@example.com" exists and is active
```

### Observable outcomes only

THEN must describe something the test framework can assert — not internal state:

```
BAD:  THEN the validation logic runs
GOOD: THEN the response body contains {field: "username", message: "..."}
```

---

## Dependency Sequencing

Tests are implemented in dependency order, not spec order.

1. **Foundational entities first** — you cannot test duplicate email rejection before you can create a user
2. **Happy path before edge cases** — the error path test assumes the happy path works
3. **Unit before integration** — lower-level behaviors before behaviors that compose them

Produce a dependency graph before writing the first test:

```
C-01: User can be created (no dependencies)
C-02: Duplicate email rejected (depends on C-01 — needs a user to exist)
C-03: Welcome email sent on creation (depends on C-01)
C-04: Duplicate email check is case-insensitive (depends on C-02)
```

Implementation order: C-01 → C-02 → C-03 → C-04

---

## The False Green Test

A test that passes immediately in RED phase is wrong — the behavior is either already implemented or the assertion is too weak.

**Diagnose false green:**
1. Is the behavior already implemented? → Mark criterion satisfied by existing code; skip to COMMIT
2. Is the assertion too permissive? → `assert response is not None` will always pass
3. Is the test hitting the wrong code path? → Check the route/handler the test is actually calling

A valid RED phase test fails with a **semantic failure** (wrong status code, wrong body, wrong state) — not a structural failure (import error, syntax error, wrong type).

---

## Criteria Manifest Format

Used in the `spec-implement` SCOPE phase:

```markdown
| # | Title | GIVEN | WHEN | THEN | Status |
|---|-------|-------|------|------|--------|
| C-01 | User created | a valid registration payload | POST /users | HTTP 201 + {id, email, status: "active"} | confirmed |
| C-02 | Duplicate email rejected | a user with email X exists | POST /users with same email | HTTP 409 + {error: "Email already registered"} | confirmed |
| C-03 | Invalid email format | any context | POST /users with email "not-an-email" | HTTP 400 + {error: "Invalid email format"} | ambiguous |
```

Ambiguous criteria are resolved before any code is written. An ambiguous criterion is a missing specification.
