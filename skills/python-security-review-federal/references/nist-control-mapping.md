# NIST SP 800-53 Control Mapping — Python Implementation

Reference for the `python-security-review-federal` skill. Maps NIST SP 800-53 control families to Python-specific implementation patterns and common violations.

---

## AC — Access Control

| Control | Requirement | Python Implementation | Common Violation |
|---------|------------|----------------------|-----------------|
| AC-2 | Account management | User model with `is_active`, `is_staff`, `last_login` fields; account lifecycle events logged | No account deactivation mechanism; no login history |
| AC-3 | Access enforcement | FastAPI: `Depends(require_role("admin"))`; Django: `@permission_required`; DRF: `IsAuthenticated` + custom permissions | Missing authorization on internal endpoints |
| AC-6 | Least privilege | Database user with minimal grants; service accounts with scoped API keys; no root DB connections | `root` or `sa` database connections; admin API keys used for read-only operations |
| AC-17 | Remote access | TLS 1.2+ enforced; no plaintext HTTP in production; VPN/bastion for admin access | `allow_http=True` in production; admin endpoints on public internet |

---

## AU — Audit and Accountability

| Control | Requirement | Python Implementation | Common Violation |
|---------|------------|----------------------|-----------------|
| AU-2 | Event logging | Log: authentication (success/fail), authorization failures, data access, privilege changes, system errors | Missing authentication event logging; no authorization failure logging |
| AU-3 | Log content | Each log record must include: timestamp (UTC), user ID, event type, outcome (success/fail), source IP, resource accessed | Logs missing user ID or source IP; no UTC timestamps |
| AU-9 | Log protection | Log files owned by dedicated log user; no write access for application user; ship to SIEM | Application writes to its own log files; no log shipping |
| AU-12 | Audit record generation | All AU-2 events generate log records; no silent failures | Exception handlers that swallow errors without logging |

### Python Logging Pattern (AU-3 Compliant)

```python
import structlog
import logging
from datetime import datetime, timezone

logger = structlog.get_logger()

# AU-3 compliant log record
logger.info(
    "authentication_success",
    timestamp=datetime.now(timezone.utc).isoformat(),
    user_id=user.id,
    event_type="login",
    outcome="success",
    source_ip=request.client.host,
    resource="/api/v1/auth/login"
)
```

---

## IA — Identification and Authentication

| Control | Requirement | Python Implementation | Common Violation |
|---------|------------|----------------------|-----------------|
| IA-2 | User identification | Unique user IDs; no shared accounts; MFA for privileged access (IA-2(1)) | Shared service accounts; no MFA for admin users |
| IA-5 | Authenticator management | Password complexity enforced; bcrypt/argon2 hashing; password history; expiration for privileged accounts | Weak password policy; MD5/SHA1 password hashing |
| IA-8 | Non-organizational users | External users authenticated via federated identity (SAML, OIDC) or separate credential store | External users in same user table as internal users without differentiation |
| IA-11 | Re-authentication | Session timeout after inactivity; re-authentication for sensitive operations | No session timeout; no re-auth for privilege escalation |

### FIPS-Compliant Password Hashing

```python
# FIPS-compliant: use passlib with argon2 or bcrypt
from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["argon2"],  # FIPS-approved via Argon2id
    deprecated="auto"
)

# NOT FIPS-compliant:
# import hashlib
# hashlib.md5(password.encode()).hexdigest()  # MD5 not approved
# hashlib.sha1(password.encode()).hexdigest()  # SHA1 not approved for passwords
```

---

## SC — System and Communications Protection

| Control | Requirement | Python Implementation | Common Violation |
|---------|------------|----------------------|-----------------|
| SC-8 | Transmission confidentiality | TLS 1.2+ for all external communication; `requests` with `verify=True` (default) | `verify=False` in requests; HTTP endpoints in production |
| SC-12 | Cryptographic key management | Keys in environment variables or secrets manager; rotation policy; no hardcoded keys | Hardcoded API keys; no key rotation |
| SC-13 | Cryptographic protection | FIPS 140-2/3 validated modules; approved algorithms only | MD5/SHA1 for security; non-FIPS OpenSSL |
| SC-28 | Protection at rest | CUI encrypted at rest with AES-256; database encryption enabled | Plaintext CUI in database; unencrypted backups |

### FIPS-Approved Algorithms (Python)

| Algorithm | FIPS Status | Python Usage |
|-----------|------------|-------------|
| AES-128/256 | ✓ Approved | `cryptography.hazmat.primitives.ciphers.algorithms.AES` |
| SHA-256/384/512 | ✓ Approved | `hashlib.sha256()`, `hashlib.sha384()`, `hashlib.sha512()` |
| RSA-2048+ | ✓ Approved | `cryptography.hazmat.primitives.asymmetric.rsa` |
| ECDSA P-256/P-384 | ✓ Approved | `cryptography.hazmat.primitives.asymmetric.ec` |
| HMAC-SHA256 | ✓ Approved | `hmac.new(key, msg, hashlib.sha256)` |
| MD5 | ✗ Not approved for security | Do not use for security purposes |
| SHA-1 | ✗ Not approved for security | Do not use for security purposes |
| DES/3DES | ✗ Not approved | Do not use |
| RC4 | ✗ Not approved | Do not use |

---

## SI — System and Information Integrity

| Control | Requirement | Python Implementation | Common Violation |
|---------|------------|----------------------|-----------------|
| SI-2 | Flaw remediation | `pip-audit` in CI/CD; patching SLA (Critical: 30 days, High: 90 days) | No automated dependency scanning; no patching SLA |
| SI-3 | Malicious code protection | bandit in CI/CD; no `eval()`/`exec()` with user input; no `pickle.loads()` on untrusted data | No SAST in pipeline; pickle deserialization of external data |
| SI-10 | Information input validation | Pydantic v2 models for all external input; parameterized queries; no string formatting in SQL | Missing input validation; SQL string formatting |

---

## CM — Configuration Management

| Control | Requirement | Python Implementation | Common Violation |
|---------|------------|----------------------|-----------------|
| CM-6 | Configuration settings | `DEBUG=False`; `ALLOWED_HOSTS` set; CORS restricted; security headers configured | `DEBUG=True` in production; `ALLOWED_HOSTS=["*"]` |
| CM-7 | Least functionality | No debug endpoints in production; no unused routes; no development dependencies in production image | `/debug`, `/admin` endpoints accessible without auth; dev dependencies in production |

---

## SR — Supply Chain Risk Management

| Control | Requirement | Python Implementation | Common Violation |
|---------|------------|----------------------|-----------------|
| SR-3 | Supply chain controls | `pip install --require-hashes`; dependencies from PyPI only (no unofficial indexes without approval); `pip-audit` in CI | No hash verification; packages from unofficial indexes |
| SR-11 | Component authenticity | Verify package signatures where available; use trusted publishing for internal packages | No integrity verification of installed packages |
