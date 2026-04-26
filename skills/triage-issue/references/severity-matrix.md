# Severity and Priority Matrix

## Severity (impact of the issue)

| Severity | Criteria | Examples |
|----------|----------|---------|
| **Critical** | Data loss, security vulnerability, system unavailable, no workaround | PII exposed, database corruption, payment double-charge, service down |
| **High** | Core feature broken, workaround exists but painful | Login broken (can reset password to workaround), file upload fails for PDFs |
| **Medium** | Non-critical feature broken, reasonable workaround | Report export fails (can copy-paste instead), sort order wrong |
| **Low** | Polish issue, minor inconvenience, cosmetic | Tooltip typo, button misaligned by 2px, non-critical email not sent |

## Priority (urgency — when to fix it)

| Priority | Label | Criteria |
|----------|-------|----------|
| P0 | Hotfix now | Critical severity in production; cannot wait for next release |
| P1 | This sprint | High severity; blocks significant user workflows |
| P2 | Next sprint | Medium severity; annoying but not blocking |
| P3 | Backlog | Low severity; fix when passing by or in a cleanup sprint |

## Severity ≠ Priority

A high-severity issue in a deprecated feature may be P3 (no users).
A low-severity issue that affects every user's first experience may be P1.

Always state the priority reason explicitly: "P1 because this affects 100% of users on checkout."

## Type definitions

| Type | Criteria |
|------|----------|
| Bug | Behavior differs from spec or documented behavior |
| Regression | Was working; broke after a recent change (cite commit or release if known) |
| Performance | Correct behavior, unacceptable speed or resource use |
| UX | Correct behavior, poor usability or confusing experience |
| Security | Any exposure of data, permissions, or attack surface |
| Docs | Documentation wrong or missing |
