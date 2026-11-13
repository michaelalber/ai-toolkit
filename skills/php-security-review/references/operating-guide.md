# php-security-review — operating guide

Depth relocated from SKILL.md; load it when the Workflow points here.

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

Full per-category checklist + grounding query map: [owasp php checklist](references/owasp-php-checklist.md).

## AI Discipline Rules

- **Evidence or it is not a finding.** Run the tools; cite `file:line` and the OWASP category. No speculative findings.
- **Detect the framework first.** Laravel ships CSRF, hashing, and Blade escaping — confirm they are used, not bypassed, before flagging.
- **Severity reflects exploitability + impact**, not how unusual the pattern looks.
- **Architecture, not here.** Structural/maintainability issues belong to `php-architecture-checklist` — note and route.
- **Federal/gov context → escalate.** If NIST/FIPS/CUI/DOE applies, run `security-review-federal` after this base review.
