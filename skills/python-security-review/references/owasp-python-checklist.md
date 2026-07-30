# OWASP Top 10 — Python Security Checklist

Reference for the `python-security-review` skill. Use during Phase 2 (SCAN) to verify coverage of each OWASP category with Python-specific patterns.

---

## A01: Broken Access Control

**Risk:** Attackers access resources or perform actions they are not authorized for.

### FastAPI
- [ ] All routers use `Depends(get_current_user)` or equivalent — no unauthenticated endpoints without explicit justification
- [ ] Role/permission checks are in `Depends()` chains, not scattered in handler bodies
- [ ] Path parameters are validated against the authenticated user's scope (e.g., user can only access their own resources)
- [ ] No `response_model` bypass via `response_model_exclude_unset` that leaks sensitive fields

### Django
- [ ] Views use `@login_required` or `LoginRequiredMixin`
- [ ] Object-level permissions use `has_object_permission()` in DRF or `django-guardian`
- [ ] Admin views are not accessible to non-staff users (`@staff_member_required`)
- [ ] `MEDIA_ROOT` files are not served directly without authorization checks

### Flask
- [ ] Routes use `@login_required` (Flask-Login) or equivalent decorator
- [ ] Blueprint-level `before_request` hooks enforce authentication
- [ ] No direct file serving from user-controlled paths

---

## A02: Cryptographic Failures

**Risk:** Sensitive data exposed due to weak or missing encryption.

### Password Hashing
- [ ] Passwords hashed with `bcrypt`, `argon2-cffi`, or `passlib` — never `hashlib.md5()` or `hashlib.sha1()`
- [ ] Django: `AUTH_PASSWORD_VALIDATORS` configured; default hasher is PBKDF2 (acceptable) or argon2 (preferred)
- [ ] No plaintext passwords stored or logged

### Secrets Management
- [ ] `SECRET_KEY` / `JWT_SECRET` loaded from environment variables, not hardcoded
- [ ] No secrets in `settings.py`, `config.py`, or any committed file
- [ ] `.env` files are in `.gitignore`

### Cryptographic Primitives
- [ ] `secrets` module used for token generation, not `random`
- [ ] `hashlib` used with salt for any security-relevant hashing
- [ ] TLS 1.2+ enforced; no `verify=False` in `requests`/`httpx` calls
- [ ] No use of deprecated algorithms: MD5, SHA1, DES, RC4 for security purposes

---

## A03: Injection

**Risk:** Attacker-controlled data interpreted as commands or queries.

### SQL Injection
- [ ] SQLAlchemy: parameterized queries only — `session.execute(text("SELECT * FROM t WHERE id = :id"), {"id": user_id})`
- [ ] Django ORM: no `raw()` or `extra()` with string formatting — use `raw("... WHERE id = %s", [user_id])`
- [ ] No `cursor.execute(f"...")` or `cursor.execute("..." % ...)` patterns
- [ ] No `cursor.execute("..." + user_input)` patterns

### OS Command Injection
- [ ] `subprocess.run()` uses list form: `["cmd", arg1, arg2]` — never `shell=True` with user input
- [ ] `os.system()` not used with user-controlled data
- [ ] `shlex.quote()` used if shell=True is unavoidable

### Template Injection (SSTI)
- [ ] Flask: `render_template_string()` never called with user input
- [ ] Jinja2: auto-escaping enabled (`autoescape=True`)
- [ ] Django: `mark_safe()` and `|safe` filter usage reviewed and justified

### Deserialization
- [ ] `pickle.loads()` / `pickle.load()` never called on untrusted data
- [ ] `yaml.safe_load()` used instead of `yaml.load()`
- [ ] `eval()` / `exec()` not called with user-controlled input

---

## A04: Insecure Design

**Risk:** Fundamental design flaws that cannot be patched — only redesigned.

- [ ] Business logic is in service/domain layer, not in HTTP handlers
- [ ] Rate limiting applied to authentication endpoints (login, password reset, OTP)
- [ ] Account enumeration prevented (same response for "user not found" and "wrong password")
- [ ] Password reset tokens are single-use and time-limited
- [ ] File upload endpoints validate MIME type server-side (not just extension)

---

## A05: Security Misconfiguration

**Risk:** Default or insecure configuration exposes the application.

### Django
- [ ] `DEBUG = False` in production
- [ ] `ALLOWED_HOSTS` set to specific domains — not `["*"]`
- [ ] `SECRET_KEY` is long, random, and from environment
- [ ] `SECURE_SSL_REDIRECT = True` in production
- [ ] `SESSION_COOKIE_SECURE = True` and `CSRF_COOKIE_SECURE = True`
- [ ] `X_FRAME_OPTIONS = "DENY"` or `"SAMEORIGIN"`

### FastAPI
- [ ] `debug=False` in `FastAPI()` constructor for production
- [ ] `CORSMiddleware` configured with specific origins — not `allow_origins=["*"]` with credentials
- [ ] OpenAPI docs (`/docs`, `/redoc`) disabled in production if not needed: `docs_url=None`
- [ ] Exception handlers do not expose stack traces to clients

### Flask
- [ ] `app.debug = False` in production
- [ ] `SECRET_KEY` set and loaded from environment
- [ ] `SESSION_COOKIE_HTTPONLY = True` and `SESSION_COOKIE_SECURE = True`

---

## A06: Vulnerable and Outdated Components

**Risk:** Known vulnerabilities in dependencies exploited by attackers.

- [ ] `pip-audit` run and output reviewed — no unpatched Critical/High CVEs
- [ ] `safety check` run as secondary scan
- [ ] `pip list --outdated` reviewed for packages with security-relevant updates
- [ ] Dependencies pinned in `requirements.txt` or `pyproject.toml` with exact versions
- [ ] No abandoned packages (last release > 2 years, no security response policy)

---

## A07: Identification and Authentication Failures

**Risk:** Broken authentication allows account takeover or session hijacking.

- [ ] JWT tokens validated for signature, expiry, and issuer — not just decoded
- [ ] JWT `alg` field validated — reject `"none"` algorithm
- [ ] Session IDs regenerated after login (session fixation prevention)
- [ ] Passwords meet minimum complexity requirements
- [ ] Failed login attempts rate-limited and logged
- [ ] Password reset flow uses time-limited, single-use tokens
- [ ] Multi-factor authentication available for privileged accounts

---

## A08: Software and Data Integrity Failures

**Risk:** Untrusted code or data executed without integrity verification.

- [ ] Dependencies installed from trusted sources (PyPI with hash verification)
- [ ] `pip install --require-hashes` used in production deployments
- [ ] No `requests.get(url, verify=False)` — TLS verification always enabled
- [ ] Webhook payloads verified with HMAC signature before processing
- [ ] No dynamic `import` of user-controlled module names

---

## A09: Security Logging and Monitoring Failures

**Risk:** Attacks go undetected; forensic investigation is impossible.

- [ ] Authentication events logged (success and failure) with timestamp and IP
- [ ] Authorization failures logged
- [ ] Logs do NOT contain: passwords, tokens, API keys, PII, connection strings
- [ ] Structured logging used (`structlog` or `python-json-logger`) for machine-parseable output
- [ ] Log level is appropriate — `DEBUG` not enabled in production
- [ ] Logs shipped to a centralized system (not only local files)

---

## A10: Server-Side Request Forgery (SSRF)

**Risk:** Attacker causes server to make requests to internal resources.

- [ ] URLs from user input are validated against an allowlist before fetching
- [ ] Internal IP ranges (10.x, 172.16.x, 192.168.x, 169.254.x, 127.x) blocked in URL validation
- [ ] `requests.get(user_url)` never called without URL validation
- [ ] Cloud metadata endpoints (169.254.169.254) explicitly blocked
- [ ] DNS rebinding mitigated by resolving and validating IP after DNS lookup
