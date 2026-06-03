---
name: dotnet-security-review
audience: team
description: >
  OWASP-based security review of .NET / .NET Framework applications with Telerik UI specialization.
  Detects the framework and entry points, scans against the OWASP Top 10 (2025) mapped to .NET patterns
  (deserialization, injection, auth, Telerik, crypto, secrets), and produces a manager-friendly executive
  summary plus a graded technical findings table. Use to audit .NET code for vulnerabilities. Triggers on
  "dotnet security review", "OWASP audit", "check for vulnerabilities", "Telerik security", ".net security
  posture", "security scan", "vulnerability assessment". For federal / gov / DOE / NIST / FIPS / CUI context,
  run security-review-federal after this base review.
  Do NOT use to grade architecture/structure — use dotnet-architecture-checklist.
---

# .NET Security Review

> "Security is not a product, but a process."
> — Bruce Schneier

## Core Security Values

Shared across the `dotnet` / `python` / `php` / `rust` security reviews — same values, language-specific threats.

| # | Value | What it means |
|---|-------|---------------|
| 1 | **Validate at boundaries** | Every external input validated and typed at the edge (model validation/FluentValidation); never trust client data. |
| 2 | **Parameterized queries only** | No string-concatenated SQL; EF Core / parameterized ADO.NET everywhere. |
| 3 | **Secrets out of code** | No hardcoded secrets; user-secrets / Key Vault / env; never logged. |
| 4 | **Authn/authz at every boundary** | `[Authorize]` / policy checks server-side at each trust boundary; deny by default. |
| 5 | **Least privilege & safe defaults** | Minimal permissions; secure defaults; fail closed. |
| 6 | **Protect data in transit & at rest** | No sensitive data (passwords, tokens, PII) in logs; HTTPS/HSTS; encryption at rest. |
| 7 | **Dependencies pinned & audited** | Versions pinned; `dotnet list package --vulnerable` in CI; supply chain reviewed. |
| 8 | **Evidence-based, graded findings** | Every finding cites `file:line` + OWASP category + severity; report is graded and manager-readable. |

## Workflow

Shared skeleton: `DETECT → SCAN → EXECUTIVE SUMMARY → GRADED FINDINGS`.

```
DETECT     Framework (.NET version / .NET Framework 4.x), app model (MVC/Razor/Blazor/API/WebForms),
           Telerik usage, and the data stores / external calls in scope.

SCAN       Walk the .NET Threat Checklist below, one OWASP category at a time. Gather evidence:
             dotnet list package --vulnerable --include-transitive   # known CVEs
             grep -rn "BinaryFormatter\|new SqlCommand(\"\|FromSqlRaw\|Html.Raw\|ValidateAntiForgeryToken"
           Every issue becomes a finding with file:line, OWASP category, and severity.

EXEC SUMMARY  Manager-friendly: risk grade, count by severity, top 3 risks in plain language.

FINDINGS      Technical table: severity · location · OWASP · finding · remediation.
```

## .NET Threat Checklist (language-specific)

| OWASP (2025) | .NET check | Severity signal |
|---|---|---|
| A01 Broken Access Control | `[Authorize]`/policies on every protected endpoint; object-level checks (no IDOR); anti-forgery on state changes | Critical |
| A02 Cryptographic Failures | `Aes`/`SHA256+` via `System.Security.Cryptography`; `RandomNumberGenerator` for tokens; no MD5/SHA1/DES for security; ASP.NET Identity for passwords | High |
| A03 Injection | EF Core / parameterized queries; no string-concatenated SQL, no `FromSqlRaw` on input; encoded Razor output, no untrusted `Html.Raw` | Critical |
| A04 Insecure Design / Deserialization | No `BinaryFormatter`/`LosFormatter`/insecure `JSON.NET TypeNameHandling`; ViewState MAC enabled (WebForms) | Critical |
| A05 Misconfiguration | Custom errors on; debug off in prod; HSTS; secure cookie flags; CORS locked down | High |
| A06 Vulnerable Components | `dotnet list package --vulnerable` clean; EOL framework flagged; no abandoned packages | High |
| A07 Auth Failures | Anti-forgery tokens; lockout/throttling on login; secure session/JWT handling | High |
| A09 Logging Failures | No passwords/tokens/PII in logs; auth and access failures logged | Medium |
| **Telerik (when detected)** | Patched Telerik version (CVE-2019-18935 RadAsyncUpload etc.); upload handlers locked down; encryption keys rotated | Critical |

Full per-category checklist: [dotnet security checklist](references/dotnet-security-checklist.md) · OWASP detail: [owasp top 10](references/owasp-top-10.md) · Telerik specifics: [telerik security](references/telerik-security.md).

## State Block

```
<security-review-state>
language: dotnet
mode: DETECT | SCAN | EXEC-SUMMARY | FINDINGS | COMPLETE
detected: [framework | app model | telerik:y/n | data stores]
owasp_covered: [A01..A10 progress]
findings: [critical:N high:N medium:N low:N]
last_action: [what was just done]
next_action: [what should happen next]
</security-review-state>
```

## Output Template

Shared across all four security reviews. Executive summary templates: [executive summary](references/executive-summary-templates.md).

```markdown
## Security Review: [project] (.NET)
**Framework**: [version] | **App model**: [MVC/Blazor/API/WebForms] | **Risk grade**: [A–F]

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

- **Evidence or it is not a finding.** Run the vulnerable-package scan; cite `file:line` and the OWASP category. No speculative findings.
- **Detect the framework first.** WebForms (ViewState, `LosFormatter`) and modern ASP.NET Core have different threat surfaces; .NET Framework 4.x is also an EOL-risk finding.
- **Always run the Telerik section when Telerik is detected.** Unpatched RadAsyncUpload is a remote code execution risk.
- **Architecture, not here.** Structural/maintainability issues belong to `dotnet-architecture-checklist` — note and route.
- **Federal/gov context → escalate.** If NIST/FIPS/CUI/DOE applies, run `security-review-federal` after this base review.

## Integration with Other Skills

- **`security-review-federal`** — Federal/gov overlay (NIST 800-53, FIPS, CUI, POA&M) applied on top of this base review.
- **`dotnet-architecture-checklist`** — Companion for structure/maintainability; run first for context.
- **`supply-chain-audit`** — Deeper dependency/CVE and license analysis.
- **`python` / `php` / `rust`-security-review** — Sibling skills sharing this exact Core Values + workflow + output.
