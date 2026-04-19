# POA&M Entry Template — Python Federal Security Review

Reference for the `python-security-review-federal` skill. Use during Phase 4 (POA&M GENERATION) to format findings as Plan of Action and Milestones entries for ATO package submission.

---

## POA&M Entry Format

Each finding from the federal security review must be formatted as a POA&M entry. The format below is compatible with the standard federal POA&M template used by most agencies.

```markdown
## POA&M Entry [ID]

| Field | Value |
|-------|-------|
| **POA&M ID** | POAM-YYYY-NNN |
| **System Name** | [Application name] |
| **System Owner** | [Name / Organization] |
| **Finding ID** | FF-NNN (from federal findings table) |
| **Weakness Description** | [Plain-language description of the vulnerability] |
| **NIST SP 800-53 Control** | [Control ID, e.g., SC-13] |
| **OWASP Category** | [e.g., A02 Cryptographic Failures] |
| **Severity** | Critical / High / Medium / Low |
| **Impact Level** | [Low / Moderate / High — from FIPS 199] |
| **Detection Method** | [bandit / pip-audit / manual code review / grep] |
| **Detection Date** | YYYY-MM-DD |
| **Responsible Party** | [Name / Team] |
| **Scheduled Completion Date** | YYYY-MM-DD |
| **Milestones** | See below |
| **Resources Required** | [Estimated hours / tools / approvals needed] |
| **Status** | Open / In Progress / Completed / Risk Accepted |
| **Comments** | [Additional context, compensating controls, risk acceptance rationale] |

### Milestones

| Milestone | Description | Target Date | Status |
|-----------|-------------|-------------|--------|
| M1 | [First action step, e.g., "Identify all affected files"] | YYYY-MM-DD | Open |
| M2 | [Second action step, e.g., "Implement fix in development"] | YYYY-MM-DD | Open |
| M3 | [Third action step, e.g., "Test fix and verify with bandit"] | YYYY-MM-DD | Open |
| M4 | [Final step, e.g., "Deploy to production and verify"] | YYYY-MM-DD | Open |
```

---

## Scheduled Completion Date Guidelines

| Severity | Maximum Time to Remediate |
|----------|--------------------------|
| Critical | 30 days from detection |
| High | 90 days from detection |
| Medium | 180 days from detection |
| Low | 365 days from detection (or next major release) |

These are maximum timelines. Agency-specific requirements (DOE Order 205.1B, CMMC, FedRAMP) may impose stricter deadlines.

---

## Example POA&M Entries

### Example 1: FIPS Cryptography Violation (Critical)

```markdown
## POA&M Entry POAM-2024-001

| Field | Value |
|-------|-------|
| **POA&M ID** | POAM-2024-001 |
| **System Name** | Data Processing API |
| **System Owner** | Jane Smith, IT Security |
| **Finding ID** | FF-001 |
| **Weakness Description** | MD5 algorithm used for password hashing in auth/utils.py. MD5 is not FIPS-approved for security purposes and is cryptographically broken. |
| **NIST SP 800-53 Control** | SC-13 (Cryptographic Protection) |
| **OWASP Category** | A02 Cryptographic Failures |
| **Severity** | Critical |
| **Impact Level** | Moderate |
| **Detection Method** | bandit (B303) + manual code review |
| **Detection Date** | 2024-01-15 |
| **Responsible Party** | Backend Development Team |
| **Scheduled Completion Date** | 2024-02-14 |
| **Resources Required** | 4 hours development, 2 hours testing |
| **Status** | Open |
| **Comments** | Compensating control: passwords are also salted, reducing (but not eliminating) risk. Interim risk acceptance not recommended given Critical severity. |

### Milestones

| Milestone | Description | Target Date | Status |
|-----------|-------------|-------------|--------|
| M1 | Replace hashlib.md5 with passlib argon2 in auth/utils.py | 2024-01-22 | Open |
| M2 | Add migration to re-hash existing passwords on next login | 2024-01-29 | Open |
| M3 | Run bandit to confirm B303 finding resolved | 2024-02-05 | Open |
| M4 | Deploy to production; verify no MD5 usage remains | 2024-02-14 | Open |
```

### Example 2: Missing Audit Logging (High)

```markdown
## POA&M Entry POAM-2024-002

| Field | Value |
|-------|-------|
| **POA&M ID** | POAM-2024-002 |
| **System Name** | Data Processing API |
| **System Owner** | Jane Smith, IT Security |
| **Finding ID** | FF-002 |
| **Weakness Description** | Authentication events are not logged. Failed login attempts, successful logins, and session terminations are not recorded. AU-2 requires these events to be logged. |
| **NIST SP 800-53 Control** | AU-2 (Event Logging), AU-3 (Content of Audit Records) |
| **OWASP Category** | A09 Security Logging and Monitoring Failures |
| **Severity** | High |
| **Impact Level** | Moderate |
| **Detection Method** | Manual code review |
| **Detection Date** | 2024-01-15 |
| **Responsible Party** | Backend Development Team |
| **Scheduled Completion Date** | 2024-04-15 |
| **Resources Required** | 8 hours development, 4 hours testing, SIEM configuration |
| **Status** | Open |
| **Comments** | No compensating controls in place. Incident response capability is impaired until this is resolved. |

### Milestones

| Milestone | Description | Target Date | Status |
|-----------|-------------|-------------|--------|
| M1 | Add structlog to project dependencies | 2024-02-01 | Open |
| M2 | Implement AU-3 compliant log records for auth events | 2024-02-15 | Open |
| M3 | Configure log shipping to SIEM | 2024-03-01 | Open |
| M4 | Verify log records contain all AU-3 required fields | 2024-04-01 | Open |
| M5 | Deploy to production and confirm SIEM receiving events | 2024-04-15 | Open |
```

---

## Risk Acceptance Template

When a finding cannot be remediated within the scheduled timeline, a risk acceptance must be documented.

```markdown
## Risk Acceptance — [Finding ID]

| Field | Value |
|-------|-------|
| **Finding ID** | FF-NNN |
| **Risk Description** | [What risk is being accepted] |
| **Justification** | [Why remediation is not feasible within the standard timeline] |
| **Compensating Controls** | [What mitigations are in place to reduce risk] |
| **Residual Risk Level** | Critical / High / Medium / Low |
| **Acceptance Authority** | [Name and title of authorizing official] |
| **Acceptance Date** | YYYY-MM-DD |
| **Expiration Date** | YYYY-MM-DD (maximum 1 year for High; 6 months for Critical) |
| **Review Date** | YYYY-MM-DD (quarterly review required for Critical/High) |
```
