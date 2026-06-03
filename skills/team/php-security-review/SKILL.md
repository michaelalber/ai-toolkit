---
name: php-security-review
audience: team
description: >
  OWASP-based security review of PHP / Laravel applications. Detects the framework and entry points,
  scans against the OWASP Top 10 (2025) mapped to PHP/Laravel patterns (mass-assignment, query injection,
  Blade XSS, auth/session, file uploads, secrets), and produces a manager-friendly executive summary plus
  a graded technical findings table. Use to audit PHP code for vulnerabilities.
  Triggers on "php security review", "laravel security audit", "audit php for vulnerabilities", "owasp php",
  "php security posture", "check php vulnerabilities", "composer audit".
  For federal / gov / DOE / NIST / FIPS / CUI context, run security-review-federal after this base review.
  Do NOT use to grade architecture/structure — use php-architecture-checklist.
---

# PHP Security Review

> "Security is not a product, but a process."
> — Bruce Schneier

## Core Security Values

Shared across the `dotnet` / `python` / `php` / `rust` security reviews — same values, language-specific threats.

| # | Value | What it means |
|---|-------|---------------|
| 1 | **Validate at boundaries** | Every external input validated and typed at the edge; never trust client data. |
| 2 | **Parameterized queries only** | No string-concatenated SQL; bound parameters everywhere. |
| 3 | **Secrets out of code** | No hardcoded secrets; env / secret-manager; never logged. |
| 4 | **Authn/authz at every boundary** | Authentication and authorization enforced server-side at each trust boundary; deny by default. |
| 5 | **Least privilege & safe defaults** | Minimal permissions; secure defaults; fail closed. |
| 6 | **Protect data in transit & at rest** | No sensitive data (passwords, tokens, PII) in logs; TLS; encryption at rest. |
| 7 | **Dependencies pinned & audited** | Versions pinned; CVE scan in CI; supply chain reviewed. |
| 8 | **Evidence-based, graded findings** | Every finding cites `file:line` + OWASP category + severity; report is graded and manager-readable. |

## Workflow

Shared skeleton: `DETECT → SCAN → EXECUTIVE SUMMARY → GRADED FINDINGS`.

```
DETECT     Framework (Laravel/Symfony/plain + version), entry points (routes, controllers, jobs,
           console commands), and the data stores / external calls in scope.

SCAN       Walk the PHP Threat Checklist below, one OWASP category at a time. Gather evidence:
             composer audit                       # known CVEs in dependencies
             phpstan analyse / psalm --taint-analysis   # taint + static analysis
             grep -rn "DB::raw\|{!! \|unserialize\|env(" app/   # high-signal patterns
           Every issue becomes a finding with file:line, OWASP category, and severity.

EXEC SUMMARY  Manager-friendly: risk grade, count by severity, top 3 risks in plain language.

FINDINGS      Technical table: severity · location · OWASP · finding · remediation.
```

## PHP Threat Checklist (language-specific)

| OWASP (2025) | PHP / Laravel check | Severity signal |
|---|---|---|
| A01 Broken Access Control | Gates/Policies enforced; no IDOR (object ownership checked); **mass-assignment** guarded (`$fillable`/`$guarded`, never `Model::unguard()`) | Critical |
| A02 Cryptographic Failures | `password_hash`/Bcrypt/Argon2 (never MD5/SHA1 for passwords); `openssl`/`sodium` for encryption; no `mt_rand` for tokens (`random_bytes`) | High |
| A03 Injection | Eloquent / bound params; no `DB::raw`/`whereRaw` on input; no `eval`/`shell_exec` on input (`escapeshellarg`); Blade auto-escapes — `{!! !!}` only on sanitized HTML | Critical |
| A05 Misconfiguration | `APP_DEBUG=false` in prod; `.env` not web-served; no directory listing; security headers set | High |
| A06 Vulnerable Components | `composer audit` clean; no abandoned packages; `composer.lock` committed | High |
| A07 Auth/Session Failures | Login rate-limited/throttled; session regenerated on login (fixation); secure+httpOnly cookies; CSRF tokens on state-changing routes | High |
| A08 Integrity Failures | No `unserialize()` on user input (object injection); signed/verified package sources | Critical |
| A09 Logging Failures | No passwords/tokens/PII in logs; auth and access failures logged | Medium |
| A10 SSRF | Outbound URLs from user input validated/allow-listed; no raw `file_get_contents($userUrl)` | High |

Full per-category checklist: [owasp php checklist](references/owasp-php-checklist.md).

## State Block

```
<security-review-state>
language: php
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
## Security Review: [project] (PHP)
**Framework**: [Laravel x/Symfony/plain] | **Scope**: [paths] | **Risk grade**: [A–F]

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

- **Evidence or it is not a finding.** Run the tools; cite `file:line` and the OWASP category. No speculative findings.
- **Detect the framework first.** Laravel ships CSRF, hashing, and Blade escaping — confirm they are used, not bypassed, before flagging.
- **Severity reflects exploitability + impact**, not how unusual the pattern looks.
- **Architecture, not here.** Structural/maintainability issues belong to `php-architecture-checklist` — note and route.
- **Federal/gov context → escalate.** If NIST/FIPS/CUI/DOE applies, run `security-review-federal` after this base review.

## Integration with Other Skills

- **`security-review-federal`** — Federal/gov overlay (NIST 800-53, FIPS, CUI, POA&M) applied on top of this base review.
- **`php-architecture-checklist`** — Companion for structure/maintainability; run first for context.
- **`supply-chain-audit`** — Deeper dependency/CVE and license analysis beyond `composer audit`.
- **`dotnet` / `python` / `rust`-security-review** — Sibling skills sharing this exact Core Values + workflow + output.
