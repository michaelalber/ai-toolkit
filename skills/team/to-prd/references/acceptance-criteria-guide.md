# Acceptance Criteria — Writing Guide

Acceptance criteria are the contract between product and engineering. Good ACs can be
verified by an independent observer without asking clarifying questions.

## Rules

1. **Binary** — each criterion is either fully met or not. "Mostly works" is not pass.
2. **Specific** — name the exact behavior, not the general goal.
3. **Observable** — verifiable by reading output, checking a state, or running a test.
4. **Independent** — each criterion can be checked without the others.

## Pattern

> Given [starting state], when [action], then [observable outcome].

## Examples

**Bad — too vague:**
- [ ] The form works correctly
- [ ] Performance is good
- [ ] The user can log in

**Good — specific and binary:**
- [ ] Given an unauthenticated user, when they visit `/dashboard`, they are redirected to `/login` with status 302.
- [ ] Given valid credentials, when the user submits the login form, a session cookie is set and the user is redirected to `/dashboard` within 2 seconds.
- [ ] Given an invalid email format, when the user submits the registration form, an inline error "Please enter a valid email address" appears without a page reload.
- [ ] The `/api/health` endpoint returns `{"status": "ok"}` with HTTP 200 within 100ms under normal load.

## Anti-patterns

| Anti-pattern | Why it fails | Fix |
|-------------|-------------|-----|
| "The system should handle errors gracefully" | Not verifiable — what is graceful? | Specify the exact error response: status code, body, log entry |
| "Performance should be acceptable" | Not binary — no threshold defined | "P95 latency < 200ms under 100 concurrent users" |
| "The UI should look good" | Subjective | Cite a specific design spec or visual diff |
| "Users can do X" | Ambiguous — which users, what inputs, what constraints? | "Given [user type] with [state], when [action], then [result]" |
