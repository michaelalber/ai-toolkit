# OWASP Top 10 (2025) — React / front-end checklist

Per-category detail behind the SKILL threat table. Each row is a grep/read target, the exploit, and the
fix. JSX escapes by default — most React XSS comes from the handful of escape hatches below.

## A01 — Broken Access Control (Critical)

| Look for | Exploit | Fix |
|----------|---------|-----|
| Route guard that only hides UI (`{isAdmin && <AdminPanel/>}`) with no server check | User calls the API directly | Enforce authz on the server; the client guard is UX only |
| Fetch-all-then-filter (`data.filter(r => r.ownerId === me)`) | All rows already in the browser payload | Scope the query server-side |
| Sequential/guessable IDs in client calls (`/api/orders/1024`) | IDOR | Server checks ownership on every request |

## A02 — Cryptographic Failures (High)

| Look for | Exploit | Fix |
|----------|---------|-----|
| `localStorage.setItem('token', …)` | Any XSS reads the token | httpOnly cookie or in-memory token |
| Custom hashing/encryption in the client | Trivially broken | Don't do crypto client-side; use TLS + server |
| `http://` links / mixed content | MITM | HTTPS everywhere; upgrade-insecure-requests |

## A03 — Injection / XSS (Critical)

| Look for | Exploit | Fix |
|----------|---------|-----|
| Raw-HTML escape hatch (`dangerously…InnerHTML={{ __html: userData }}`) | Stored/reflected XSS | Sanitize with DOMPurify, or render as text; never feed it raw user data |
| `<a href={userUrl}>` / `<iframe src={userUrl}>` | `javascript:` URL runs script | Validate the protocol against an allow-list (`https:`/`mailto:`) |
| Dynamic code eval (`eval`, the `Function` constructor, injected `<script>`) on input | RCE-in-browser | Remove; there is almost never a legitimate need |
| `ref` callback assigning raw markup to a DOM node's HTML sink | Bypasses JSX escaping | Render via React/text nodes instead of writing markup imperatively |

```bash
grep -rn "dangerously" src/
grep -rn "href={[^\"]" src/                # dynamic hrefs to review for protocol
grep -rniE "\beval\b|\bFunction\b" src/    # dynamic code evaluation sinks
```

## A04 — Insecure Design (High)

| Look for | Exploit | Fix |
|----------|---------|-----|
| `target="_blank"` without `rel="noopener noreferrer"` | Reverse-tabnabbing | Add `rel`; modern browsers help but don't rely on it |
| `window.addEventListener('message', …)` with no `event.origin` check | Any site postMessages in | Verify `event.origin` against an allow-list |

## A05 — Security Misconfiguration (High)

| Look for | Exploit | Fix |
|----------|---------|-----|
| No Content-Security-Policy header | XSS payloads run freely | Ship a CSP (nonce/hash-based; avoid `unsafe-inline`) |
| Source maps deployed to prod public | Source + comments exposed | Strip or access-control `.map` files |
| Dev build / React DevTools in prod | Info leak, slower, less safe | Build with production mode |

## A06 — Vulnerable & Outdated Components (High)

```bash
npm audit --omit=dev
npx npm-check-updates       # surface stale majors
```

Lockfile committed; no `latest`/`*` ranges; remove abandoned UI deps. The transitive npm tree is the
biggest surface — review `npm audit` chains, not just direct deps.

## A07 — Authentication / Session Failures (High)

| Look for | Exploit | Fix |
|----------|---------|-----|
| Token not cleared on logout | Session persists | Clear token + invalidate server-side |
| Long-lived token in storage | Replay after theft | Short-lived access token + refresh; httpOnly |

## A08 — Software & Data Integrity Failures (High)

| Look for | Exploit | Fix |
|----------|---------|-----|
| `<script src="cdn…">` without `integrity` | Compromised CDN ships malware | Add SRI `integrity` + `crossorigin` |
| `import(userControlledUrl)` | Loads attacker code | Never import attacker-controlled URLs |

## A09 — Logging & Monitoring Failures (Medium)

| Look for | Exploit | Fix |
|----------|---------|-----|
| Token/PII in `console.log` or sent to Sentry/GA | Leak via logs/telemetry | Scrub before sending; configure error-tracker PII filters |

## A10 — SSRF / Open Redirect (High)

| Look for | Exploit | Fix |
|----------|---------|-----|
| `location.href = params.get('next')` | Open redirect → phishing | Allow-list redirect targets; only relative paths |
| Image/iframe `src` from user input proxied | SSRF via a proxy endpoint | Validate + allow-list on the server |

## Framework notes

- **Next.js**: check `headers()` config for CSP/HSTS; Server Actions and route handlers are *server* code — review them with the matching backend security review too. `NEXT_PUBLIC_` vars are shipped to the browser by design — confirm none are secrets.
- **Vite**: only `import.meta.env.VITE_*` is exposed to the client; anything else stays server-side. Confirm secrets aren't prefixed `VITE_`.
- **CRA**: `REACT_APP_*` vars are embedded in the bundle — same rule.
