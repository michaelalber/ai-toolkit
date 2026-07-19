---
name: vue-security-review
audience: team
description: >
  OWASP-based security review of Vue/TypeScript front-ends. Detects framework (Vite/Vue
  CLI/Nuxt), entry points, and data flows; scans the OWASP Top 10 (2025) mapped to Vue
  client-side risks (raw-HTML XSS via v-html, URL/protocol injection, bundled secrets,
  insecure token storage, dependency CVEs, missing CSP, open redirects, router guard
  bypass); emits an exec summary plus graded findings. Use to audit Vue for
  vulnerabilities. Not for architecture grading (vue-architecture-checklist).
---

# Vue Security Review

> "Security is not a product, but a process."
> — Bruce Schneier

## Core Philosophy

Shared across the `dotnet` / `python` / `php` / `rust` / `react` / `vue` security reviews — same values, language-specific threats.

> **Grounding note:** the knowledge base has a Vue 2/3 corpus under `collection="javascript"`. Use
> `collection="internal"` for OWASP and `collection="ui_ux"` for safe-by-default UI; cite **vuejs.org**
> and the OWASP cheat sheets as the Vue authority. Never invent a `vue` collection.

| # | Value | What it means |
|---|-------|---------------|
| 1 | **Validate at boundaries** | Every external input (route params, `postMessage`, API responses) validated/typed before use; never trust client-controlled data — even your own API's response shapes. |
| 2 | **No raw HTML from untrusted data** | Output is escaped by default (Vue's mustache interpolation and `:text` do this); `v-html` is sanitized or never fed user data. |
| 3 | **Secrets out of the bundle** | No API keys/tokens in client code; only intentionally-public `VITE_`/`VUE_APP_` values shipped; everything else stays server-side. |
| 4 | **Authn/authz is server-enforced** | The client never *decides* authorization — it only reflects it. Vue Router navigation guards are UX, not security; the API enforces. |
| 5 | **Least privilege & safe defaults** | Minimal scopes; safe link/target defaults; fail closed on missing data. |
| 6 | **Protect data in transit & at rest** | TLS only; tokens in memory or httpOnly cookies, not `localStorage`; no PII/tokens in logs or analytics. |
| 7 | **Dependencies pinned & audited** | Lockfile committed; `npm audit` / Snyk in CI; transitive CVEs reviewed (the npm tree is deep). |
| 8 | **Evidence-based, graded findings** | Every finding cites `file:line` + OWASP category + severity; report is graded and manager-readable. |

## Workflow

Shared skeleton: `DETECT → SCAN → EXECUTIVE SUMMARY → GRADED FINDINGS`.

```
DETECT     Framework (Vite/Vue CLI/Nuxt + Vue version), entry points (routes, forms, `postMessage`/
           `iframe`, external script tags), and the APIs / storage the app talks to.

SCAN       Walk the Vue Threat Checklist below, one OWASP category at a time. Gather evidence:
             npm audit --omit=dev                       # known CVEs in the dependency tree
             npx eslint . --plugin security               # eslint-plugin-security + vuejs-accessibility
             grep -rn "v-html" src/                        # raw-HTML escape hatch usage
             grep -rn "localStorage\|sessionStorage" src/ # token storage
             grep -rn "VITE_\|VUE_APP_\|process.env" src/ # secrets exposed to the bundle
           Every issue becomes a finding with file:line, OWASP category, and severity.

EXEC SUMMARY  Manager-friendly: risk grade, count by severity, top 3 risks in plain language.

FINDINGS      Technical table: severity · location · OWASP · finding · remediation.
```

## Vue Threat Checklist (language-specific)

| OWASP (2025) | Vue / front-end check | Severity signal |
|---|---|---|
| A01 Broken Access Control | Authorization enforced by the API, not just hidden routes/buttons or a `beforeEnter` guard; no sensitive data fetched then client-side filtered; no IDOR via predictable IDs in client calls | Critical |
| A02 Cryptographic Failures | Tokens not in `localStorage` (XSS-readable) — prefer httpOnly cookies or memory (a Pinia store held in memory only); no home-rolled crypto in the client; HTTPS-only links | High |
| A03 Injection (XSS) | Mustache/`:text` escaping intact; `v-html` only on sanitized HTML (DOMPurify); no `:href={userUrl}`/`:src=` allowing `javascript:`; no dynamic code evaluation (`eval`, the `Function` constructor, injected `<script>`) on input | Critical |
| A04 Insecure Design | `target="_blank"` paired with `rel="noopener noreferrer"`; `postMessage` handlers check `event.origin`; router navigation guards check `event.origin`/referrer where relevant; no trust of `window.name` | High |
| A05 Misconfiguration | Content-Security-Policy present; source maps not shipped to prod (or access-controlled); no `*` CORS reliance; Vue dev build (`__VUE_PROD_DEVTOOLS__` etc.) not served in prod | High |
| A06 Vulnerable Components | `npm audit` clean; lockfile committed; no abandoned/unmaintained UI deps; no `latest` ranges | High |
| A07 Auth/Session Failures | Login flows rate-limited server-side; tokens cleared on logout; no long-lived tokens in storage; refresh handled securely; router `beforeEach` global guard reflects auth state, does not enforce it | High |
| A08 Integrity Failures | Third-party `<script>`/CDN tags use SRI (`integrity`); no untrusted dynamic `import()` of attacker-controlled URLs | High |
| A09 Logging Failures | No tokens/PII sent to client analytics/error trackers (scrub before Sentry/GA); no secrets in `console.log` | Medium |
| A10 SSRF / Open Redirect | Redirect targets from query params allow-listed (no `router.push(route.query.next)` unvalidated); image/iframe `src` from user input validated | High |

Full per-category checklist: [owasp vue checklist](references/owasp-vue-checklist.md).

## State Block

```
<security-review-state>
language: vue
mode: DETECT | SCAN | EXEC-SUMMARY | FINDINGS | COMPLETE
detected: [framework+version | entry points | apis/storage]
owasp_covered: [A01..A10 progress]
findings: [critical:N high:N medium:N low:N]
last_action: [what was just done]
next_action: [what should happen next]
</security-review-state>
```

## Output Template

Shared across all security reviews. Executive summary template: [executive summary](references/executive-summary-template.md).

```markdown
## Security Review: [project] (Vue)
**Framework**: [Vite/Vue CLI/Nuxt + Vue x] | **Scope**: [paths] | **Risk grade**: [A–F]

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
**D** 1+ critical · **F** systemic (unsanitized `v-html` + secrets in bundle + client-only authz).

## AI Discipline Rules

- **Evidence or it is not a finding.** Run the tools; cite `file:line` and the OWASP category. No speculative findings.
- **Detect the framework first.** Vue escapes interpolation by default and Nuxt adds headers/CSP options — confirm the safe defaults are used, not bypassed, before flagging.
- **Client guards are UX, not security.** A `beforeEnter`/`beforeEach` route guard is never a control; the finding is the *missing server-side check*, not the visible redirect.
- **Severity reflects exploitability + impact**, not how unusual the pattern looks. XSS via `v-html` that reads a `localStorage` token is Critical; a missing `rel="noopener"` is Low/Medium.
- **Architecture, not here.** Structural/maintainability issues belong to `vue-architecture-checklist` — note and route.
- **Federal/gov context → escalate.** If NIST/FIPS/CUI/DOE applies, run `security-review-federal` after this base review.

## Integration with Other Skills

- **`security-review-federal`** — Federal/gov overlay (NIST 800-53, FIPS, CUI, POA&M) applied on top of this base review.
- **`vue-architecture-checklist`** — Companion for structure/maintainability; run first for context.
- **`supply-chain-audit`** — Deeper dependency/CVE and license analysis beyond `npm audit` (the npm tree is the largest attack surface here).
- **`dotnet` / `python` / `php` / `rust` / `react`-security-review** — Sibling skills sharing this exact Core Values + workflow + output.
