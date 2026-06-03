---
name: python-security-review
audience: team
description: >
  OWASP-based security review of Python applications (FastAPI, Django, Flask). Detects the framework and
  entry points, scans against the OWASP Top 10 (2025) mapped to Python patterns (injection, insecure
  deserialization, SSTI, secrets, auth), runs bandit and pip-audit for evidence, and produces a
  manager-friendly executive summary plus a graded technical findings table. Use to audit Python code for
  vulnerabilities. Triggers on "python security review", "audit python code", "check python vulnerabilities",
  "OWASP python", "bandit scan", "pip-audit", "fastapi security", "django security", "flask security".
  For federal / gov / DOE / NIST / FIPS / CUI context, run security-review-federal after this base review.
  Do NOT use to grade architecture/structure — use python-architecture-checklist.
---

# Python Security Review

> "Security is not a product, but a process."
> — Bruce Schneier

## Core Security Values

Shared across the `dotnet` / `python` / `php` / `rust` security reviews — same values, language-specific threats.

| # | Value | What it means |
|---|-------|---------------|
| 1 | **Validate at boundaries** | Every external input validated and typed at the edge (Pydantic/serializers); never trust client data. |
| 2 | **Parameterized queries only** | No f-string / `%`-formatted SQL; bound parameters or the ORM everywhere. |
| 3 | **Secrets out of code** | No hardcoded secrets; env / secret-manager; never logged. |
| 4 | **Authn/authz at every boundary** | Authentication and authorization enforced server-side at each trust boundary; deny by default. |
| 5 | **Least privilege & safe defaults** | Minimal permissions; secure defaults; fail closed. |
| 6 | **Protect data in transit & at rest** | No sensitive data (passwords, tokens, PII) in logs; TLS; encryption at rest. |
| 7 | **Dependencies pinned & audited** | Versions pinned; `pip-audit` in CI; supply chain reviewed. |
| 8 | **Evidence-based, graded findings** | Every finding cites `file:line` + OWASP category + severity; report is graded and manager-readable. |

## Workflow

Shared skeleton: `DETECT → SCAN → EXECUTIVE SUMMARY → GRADED FINDINGS`.

```
DETECT     Framework (FastAPI/Django/Flask + version), entry points (routes, views, tasks, CLIs),
           and the data stores / external calls in scope.

SCAN       Walk the Python Threat Checklist below, one OWASP category at a time. Gather evidence:
             bandit -r <pkg>            # static security analysis
             pip-audit                  # known CVEs in dependencies
             grep -rn "yaml.load(\|shell=True\|format(.*SELECT" <pkg>
           Every issue becomes a finding with file:line, OWASP category, and severity.

EXEC SUMMARY  Manager-friendly: risk grade, count by severity, top 3 risks in plain language.

FINDINGS      Technical table: severity · location · OWASP · finding · remediation.
```

## Python Threat Checklist (language-specific)

| OWASP (2025) | Python check | Severity signal |
|---|---|---|
| A01 Broken Access Control | Auth dependencies/decorators on every protected route; object-level checks (no IDOR); deny by default | Critical |
| A02 Cryptographic Failures | `hashlib` SHA-256+ (never MD5/SHA1 for security); `secrets`/`os.urandom` for tokens (not `random`); `passlib`/bcrypt for passwords | High |
| A03 Injection | ORM or bound params (no f-string/`%` SQL); no shell-command execution on input (`subprocess(..., shell=True)`, shell helpers); no dynamic `eval`/`exec` on input | Critical |
| A04 Insecure Design | Server-Side Template Injection (Jinja2 rendering user input); open redirects | High |
| A05 Misconfiguration | `DEBUG=False` in prod; `ALLOWED_HOSTS`/CORS locked down; secure cookie flags; `SECRET_KEY` from env | High |
| A06 Vulnerable Components | `pip-audit` clean; versions pinned in `pyproject.toml`; no abandoned packages | High |
| A08 Integrity Failures | No insecure deserialization of untrusted input (native object deserialization, `yaml.load` without `SafeLoader`) | Critical |
| A09 Logging Failures | No passwords/tokens/PII in logs; auth and access failures logged | Medium |
| A10 SSRF | Outbound URLs from user input validated/allow-listed; no raw `requests.get(user_url)` | High |

Full per-category checklist: [owasp python checklist](references/owasp-python-checklist.md).

## State Block

```
<security-review-state>
language: python
mode: DETECT | SCAN | EXEC-SUMMARY | FINDINGS | COMPLETE
detected: [framework+version | entry points | data stores]
owasp_covered: [A01..A10 progress]
findings: [critical:N high:N medium:N low:N]
last_action: [what was just done]
next_action: [what should happen next]
</security-review-state>
```

## Output Template

Shared across all four security reviews. Executive summary template: [executive summary](references/executive-summary-template.md).

```markdown
## Security Review: [project] (Python)
**Framework**: [FastAPI/Django/Flask] | **Scope**: [paths] | **Risk grade**: [A–F]

### Executive Summary (manager-friendly)
[2–3 sentences: overall posture, the most serious risk in plain language, recommended next step.]
Findings: Critical [N] · High [N] · Medium [N] · Low [N]

### Technical Findings
| Severity | Location | OWASP | Finding | Remediation |
|----------|----------|-------|---------|-------------|
| CRITICAL | file:line | A03 | [pattern] | [fix] |

**Top 3 priorities**: 1. … 2. … 3. …
```

Risk grade: **A** no critical/high · **B** no critical, ≤2 high · **C** no critical, multiple high ·
**D** 1+ critical · **F** systemic (injection + secrets in code + broken access control).

## AI Discipline Rules

- **Evidence or it is not a finding.** Run bandit/pip-audit; cite `file:line` and the OWASP category. No speculative findings.
- **Detect the framework first.** Django escapes templates and ships CSRF; FastAPI validates via Pydantic — confirm these are used, not bypassed, before flagging.
- **Severity reflects exploitability + impact**, not how unusual the pattern looks.
- **Architecture, not here.** Structural/maintainability issues belong to `python-architecture-checklist` — note and route.
- **Federal/gov context → escalate.** If NIST/FIPS/CUI/DOE applies, run `security-review-federal` after this base review.

## Integration with Other Skills

- **`security-review-federal`** — Federal/gov overlay (NIST 800-53, FIPS, CUI, POA&M) applied on top of this base review.
- **`python-architecture-checklist`** — Companion for structure/maintainability; run first for context.
- **`supply-chain-audit`** — Deeper dependency/CVE and license analysis beyond `pip-audit`.
- **`dotnet` / `php` / `rust`-security-review** — Sibling skills sharing this exact Core Values + workflow + output.
