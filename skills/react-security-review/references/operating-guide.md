# react-security-review — operating guide

Depth relocated from SKILL.md; load it when the Workflow points here.

## React Threat Checklist (language-specific)

| OWASP (2025) | React / front-end check | Severity signal |
|---|---|---|
| A01 Broken Access Control | Authorization enforced by the API, not just hidden routes/buttons; no sensitive data fetched then client-side filtered; no IDOR via predictable IDs in client calls | Critical |
| A02 Cryptographic Failures | Tokens not in `localStorage` (XSS-readable) — prefer httpOnly cookies or memory; no home-rolled crypto in the client; HTTPS-only links | High |
| A03 Injection (XSS) | JSX auto-escaping intact; the raw-HTML escape hatch (`dangerously…InnerHTML`) only on sanitized HTML (DOMPurify); no `href={userUrl}`/`src=` allowing `javascript:`; no dynamic code evaluation (`eval`, the `Function` constructor, injected `<script>`) on input | Critical |
| A04 Insecure Design | `target="_blank"` paired with `rel="noopener noreferrer"`; `postMessage` handlers check `event.origin`; no trust of `window.name`/referrer | High |
| A05 Misconfiguration | Content-Security-Policy present; source maps not shipped to prod (or access-controlled); no `*` CORS reliance; React dev build not served in prod | High |
| A06 Vulnerable Components | `npm audit` clean; lockfile committed; no abandoned/unmaintained UI deps; no `latest` ranges | High |
| A07 Auth/Session Failures | Login flows rate-limited server-side; tokens cleared on logout; no long-lived tokens in storage; refresh handled securely | High |
| A08 Integrity Failures | Third-party `<script>`/CDN tags use SRI (`integrity`); no untrusted dynamic import of attacker-controlled URLs | High |
| A09 Logging Failures | No tokens/PII sent to client analytics/error trackers (scrub before Sentry/GA); no secrets in `console.log` | Medium |
| A10 SSRF / Open Redirect | Redirect targets from query params allow-listed (no `location.href = params.get('next')`); image/iframe `src` from user input validated | High |

Full per-category checklist + grounding query map: [owasp react checklist](references/owasp-react-checklist.md).

## AI Discipline Rules

- **Evidence or it is not a finding.** Run the tools; cite `file:line` and the OWASP category. No speculative findings.
- **Detect the framework first.** React escapes JSX by default and Next.js adds headers/CSP options — confirm the safe defaults are used, not bypassed, before flagging.
- **Client guards are UX, not security.** A hidden admin route is never a control; the finding is the *missing server-side check*, not the visible button.
- **Severity reflects exploitability + impact**, not how unusual the pattern looks. XSS that reads a `localStorage` token is Critical; a missing `rel="noopener"` is Low/Medium.
- **Architecture, not here.** Structural/maintainability issues belong to `react-architecture-checklist` — note and route.
- **Federal/gov context → escalate.** If NIST/FIPS/CUI/DOE applies, run `security-review-federal` after this base review.
