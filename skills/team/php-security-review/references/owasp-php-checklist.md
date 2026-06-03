# OWASP Top 10 (2025) — PHP / Laravel Checklist

Per-category checklist for the PHP security review. Run alongside `composer audit` and
`phpstan` / `psalm --taint-analysis`.

---

## A01 — Broken Access Control
- [ ] Every protected route enforces a Gate/Policy (`authorize()`, `can:` middleware)
- [ ] Object ownership checked before access (no IDOR via route model binding)
- [ ] Mass-assignment guarded: `$fillable` or `$guarded` on every model; no `Model::unguard()`
- [ ] No reliance on hidden form fields or client-side checks for authorization

```bash
grep -rn "unguard\|->forceFill\|create(\$request->all" app/
```

## A02 — Cryptographic Failures
- [ ] Passwords hashed with `Hash::make` (Bcrypt/Argon2) — never `md5`/`sha1`/`crypt`
- [ ] Encryption via `openssl`/`sodium` or Laravel `Crypt`; keys from `.env`
- [ ] Tokens from `random_bytes`/`Str::random` — never `rand`/`mt_rand`/`uniqid`
- [ ] TLS enforced; `Secure`/`HttpOnly`/`SameSite` cookie flags set

## A03 — Injection
- [ ] All queries use Eloquent or bound parameters; no `DB::raw`/`whereRaw`/`selectRaw` on user input
- [ ] No dynamic code execution or shell calls on user input (`escapeshellarg`/`escapeshellcmd`)
- [ ] Blade output auto-escaped; `{!! !!}` used only on explicitly sanitized HTML
- [ ] No dynamic class/method instantiation from user input

```bash
grep -rn "DB::raw\|whereRaw\|selectRaw\|{!! \|shell_exec\|\bsystem(" app/ resources/
```

## A05 — Security Misconfiguration
- [ ] `APP_DEBUG=false` and `APP_ENV=production` in production
- [ ] `.env`, `storage/`, `vendor/` not web-served; public root is `public/`
- [ ] Security headers (CSP, X-Frame-Options, HSTS) set
- [ ] Default/sample credentials removed

## A06 — Vulnerable & Outdated Components
- [ ] `composer audit` clean (no known CVEs)
- [ ] `composer.lock` committed; no abandoned packages
- [ ] Framework on a supported version

## A07 — Identification & Authentication Failures
- [ ] Login throttled/rate-limited (`throttle` middleware)
- [ ] Session regenerated on login (`$request->session()->regenerate()`) — fixation defense
- [ ] CSRF protection on all state-changing routes (`VerifyCsrfToken`)
- [ ] Password reset tokens single-use and time-limited

## A08 — Software & Data Integrity Failures
- [ ] No `unserialize()` on user-controlled input (PHP object injection) — use JSON
- [ ] Package sources signed/verified; no untrusted Composer repositories

## A09 — Security Logging & Monitoring Failures
- [ ] Auth and access-control failures logged
- [ ] No passwords, tokens, or PII written to logs

## A10 — SSRF
- [ ] Outbound requests from user input validated against an allow-list
- [ ] No raw `file_get_contents($userUrl)` / Guzzle to user-controlled hosts

---

## Tooling

```bash
composer audit                       # dependency CVEs
phpstan analyse                      # static analysis
psalm --taint-analysis               # taint tracking (source -> sink)
grep -rn "DB::raw\|{!! \|unserialize\|->all()" app/   # high-signal patterns
```
