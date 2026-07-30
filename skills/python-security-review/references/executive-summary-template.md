# Executive Summary Templates — Python Security Review

Reference for the `python-security-review` skill. Use during Phase 3 (REPORT) to produce manager-friendly output that bridges technical findings and business impact.

---

## Template 1: Full Executive Summary

Use for comprehensive security reviews delivered to management or clients.

```markdown
# Security Review: [Application Name]

**Date:** YYYY-MM-DD
**Reviewer:** [Name / Team]
**Framework:** [FastAPI / Django / Flask / Other]
**Python Version:** [3.x]
**Scope:** [Brief description — e.g., "REST API endpoints and authentication layer"]
**Tools Used:** bandit [version], pip-audit [version], manual code review

---

## Risk Summary

| Severity | Count | Status |
|----------|-------|--------|
| 🔴 Critical | N | Requires immediate action before next deployment |
| 🟠 High | N | Requires remediation within current sprint |
| 🟡 Medium | N | Requires remediation within current quarter |
| 🟢 Low | N | Add to technical debt backlog |
| ℹ️ Informational | N | Positive findings and observations |

**Overall Risk Rating:** [Critical / High / Medium / Low]

---

## What This Means for the Business

[2-3 sentences in plain language. Example:]

The application has [N] critical findings that could allow an attacker to [specific impact — e.g., "access any user's data without authentication" or "execute arbitrary code on the server"]. These findings require immediate attention before the next production deployment. The remaining [N] high-severity findings represent significant risk that should be addressed within the current development sprint.

---

## Top 3 Findings (Plain Language)

### 1. [Finding Name] — Critical

**What it is:** [One sentence describing the vulnerability in plain language]
**What an attacker could do:** [One sentence describing the business impact]
**How to fix it:** [One sentence describing the remediation]
**Estimated fix time:** [Hours / Days]

### 2. [Finding Name] — High

**What it is:** [One sentence]
**What an attacker could do:** [One sentence]
**How to fix it:** [One sentence]
**Estimated fix time:** [Hours / Days]

### 3. [Finding Name] — Medium

**What it is:** [One sentence]
**What an attacker could do:** [One sentence]
**How to fix it:** [One sentence]
**Estimated fix time:** [Hours / Days]

---

## What Is Working Well

The following security practices were observed and should be maintained:

- [Positive finding 1 — e.g., "Passwords are hashed with bcrypt — correct algorithm and work factor"]
- [Positive finding 2 — e.g., "All database queries use parameterized statements — no SQL injection surface found"]
- [Positive finding 3 — e.g., "Dependencies are pinned with exact versions in requirements.txt"]

---

## Remediation Priority Matrix

| Priority | Finding | Effort | Risk Reduction |
|----------|---------|--------|---------------|
| 1 (Immediate) | [Finding name] | [S/M/L] | Critical → Resolved |
| 2 (This Sprint) | [Finding name] | [S/M/L] | High → Resolved |
| 3 (This Quarter) | [Finding name] | [S/M/L] | Medium → Resolved |

---

## Recommended Next Steps

1. **Immediate (before next deployment):** [Specific action for Critical findings]
2. **This sprint:** [Specific action for High findings]
3. **This quarter:** [Specific action for Medium findings]
4. **Ongoing:** Run `pip-audit` in CI/CD pipeline to catch new dependency vulnerabilities automatically
```

---

## Template 2: Technical Findings Table

Use for the developer-facing section of the report.

```markdown
## Technical Findings

| ID | Severity | OWASP | File | Line | Description | Bandit Code | Remediation |
|----|----------|-------|------|------|-------------|-------------|-------------|
| F-001 | Critical | A03 | app/db.py | 42 | SQL injection via string formatting in execute() | B608 | Use parameterized queries |
| F-002 | High | A02 | config/settings.py | 8 | Hardcoded SECRET_KEY | B105 | Load from os.environ |
| F-003 | High | A01 | api/users.py | 87 | Missing authentication on /admin endpoint | — | Add Depends(require_admin) |
| F-004 | Medium | A05 | main.py | 12 | DEBUG=True detected | B501 | Set DEBUG=False in production |
| F-005 | Low | A09 | auth/views.py | 34 | Password logged on failed login | — | Remove password from log statement |
```

---

## Template 3: Dependency Vulnerability Summary

Use when pip-audit finds CVEs.

```markdown
## Dependency Vulnerabilities (pip-audit)

| Package | Installed Version | CVE | Severity | Fixed In | Action |
|---------|-----------------|-----|----------|----------|--------|
| requests | 2.28.0 | CVE-YYYY-XXXXX | High | 2.31.0 | Upgrade immediately |
| cryptography | 38.0.0 | CVE-YYYY-XXXXX | Critical | 41.0.0 | Upgrade immediately |
| Pillow | 9.0.0 | CVE-YYYY-XXXXX | Medium | 9.3.0 | Upgrade this sprint |

**Action:** Run `pip install --upgrade [package]` for each finding. Re-run `pip-audit` after upgrading to confirm resolution.
```

---

## Plain-Language Translations for Common Findings

Use these translations when writing the executive summary for non-technical stakeholders.

| Technical Finding | Plain-Language Translation |
|------------------|--------------------------|
| SQL injection | "An attacker could read, modify, or delete any data in the database by sending specially crafted input to the application." |
| Hardcoded secret key | "The application's master password is stored in the source code. Anyone with access to the code repository can impersonate the application or decrypt user sessions." |
| Missing authentication | "Certain parts of the application can be accessed without logging in, including areas intended only for administrators." |
| Outdated dependency with CVE | "The application uses a third-party library with a known security flaw. Attackers actively scan for applications using this library." |
| DEBUG=True in production | "The application is configured to show detailed error messages to users, including internal code paths and database queries that attackers can use to plan an attack." |
| CORS misconfiguration | "The application's cross-origin policy allows any website to make authenticated requests on behalf of logged-in users, enabling cross-site request forgery attacks." |
| Insecure deserialization (pickle) | "The application processes data in a format that can execute arbitrary code when loaded. An attacker who can control this data can run any command on the server." |
| SSRF | "The application can be tricked into making requests to internal systems (databases, cloud metadata services) that should not be accessible from the internet." |
