# dotnet-security-review — operating guide

Depth relocated from SKILL.md; load it when the Workflow points here.

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

Full per-category checklist: [dotnet security checklist](references/dotnet-security-checklist.md) · OWASP detail + grounding query map: [owasp top 10](references/owasp-top-10.md) · Telerik specifics: [telerik security](references/telerik-security.md).

## AI Discipline Rules

- **Evidence or it is not a finding.** Run the vulnerable-package scan; cite `file:line` and the OWASP category. No speculative findings.
- **Detect the framework first.** WebForms (ViewState, `LosFormatter`) and modern ASP.NET Core have different threat surfaces; .NET Framework 4.x is also an EOL-risk finding.
- **Always run the Telerik section when Telerik is detected.** Unpatched RadAsyncUpload is a remote code execution risk.
- **Architecture, not here.** Structural/maintainability issues belong to `dotnet-architecture-checklist` — note and route.
- **Federal/gov context → escalate.** If NIST/FIPS/CUI/DOE applies, run `security-review-federal` after this base review.
