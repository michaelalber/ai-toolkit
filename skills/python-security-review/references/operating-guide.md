# python-security-review — operating guide

Depth relocated from SKILL.md; load it when the Workflow points here.

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

Full per-category checklist + grounding query map: [owasp python checklist](references/owasp-python-checklist.md).

## AI Discipline Rules

- **Evidence or it is not a finding.** Run bandit/pip-audit; cite `file:line` and the OWASP category. No speculative findings.
- **Detect the framework first.** Django escapes templates and ships CSRF; FastAPI validates via Pydantic — confirm these are used, not bypassed, before flagging.
- **Severity reflects exploitability + impact**, not how unusual the pattern looks.
- **Architecture, not here.** Structural/maintainability issues belong to `python-architecture-checklist` — note and route.
- **Federal/gov context → escalate.** If NIST/FIPS/CUI/DOE applies, run `security-review-federal` after this base review.
