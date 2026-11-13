# rust-security-review — operating guide

Depth relocated from SKILL.md; load it when the Workflow points here.

## Rust Threat Checklist (language-specific)

| OWASP (2025) | Rust check | Severity signal |
|---|---|---|
| A01 Broken Access Control | Auth extractor/middleware on every protected route; object-level checks (no IDOR); deny by default | Critical |
| A02 Cryptographic Failures | `ring`/`rustls`/RustCrypto — no hand-rolled crypto; `getrandom` for tokens; Argon2/bcrypt for passwords; no MD5/SHA1 for security | High |
| A03 Injection | `sqlx`/`diesel` bound params (no `format!` into SQL); `std::process::Command` with explicit args, never a shell string from input | Critical |
| **A04 Memory Safety (`unsafe` audit)** | Every `unsafe` block has a correct `// SAFETY:` comment; no `transmute` of untrusted data; raw-pointer and FFI buffer bounds checked; no out-of-bounds / use-after-free | Critical |
| A04 Denial of Service | No `.unwrap()`/`.expect()`/`panic!` on user input (thread crash/DoS); bounded allocations; `checked_`/`saturating_` math on security-sensitive arithmetic | High |
| A06 Vulnerable Components | `cargo audit` clean (RustSec); `cargo deny` advisories/bans enforced | High |
| A08 Integrity / Deserialization | serde on untrusted input bounded and validated; untagged/`deny_unknown_fields` considered; no unbounded recursion | High |
| A09 Logging Failures | Secrets not exposed via `Debug`/`Display`; no tokens/PII in logs | Medium |
| A10 SSRF | Outbound URLs from user input validated/allow-listed | High |

Full per-category checklist + grounding query map: [owasp rust checklist](references/owasp-rust-checklist.md) · `unsafe` audit method: [unsafe audit guide](references/unsafe-audit-guide.md).

## AI Discipline Rules

- **Evidence or it is not a finding.** Run cargo-audit/cargo-deny; cite `file:line` and the OWASP category. No speculative findings.
- **`unsafe` is the security surface.** Memory safety holds only outside `unsafe`; audit every block for a correct `// SAFETY:` invariant — a missing or wrong one is Critical.
- **`panic` on input is a DoS finding**, not just a robustness nit, in a service that must stay up.
- **Architecture, not here.** Ownership/trait/structure issues belong to `rust-architecture-checklist` — note and route.
- **Federal/gov context → escalate.** If NIST/FIPS/CUI/DOE applies, run `security-review-federal` after this base review.
