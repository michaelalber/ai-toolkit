---
name: python-security-review
description: Conducts OWASP-based security reviews of Python applications (FastAPI, Django, Flask) with bandit/pip-audit tooling. Identifies vulnerabilities, insecure patterns, and compliance gaps across all OWASP Top 10 categories. Generates manager-friendly reports with risk explanations and remediation priorities. Use when asked to review security, audit python code, check python vulnerabilities, OWASP python, bandit scan, pip-audit, or evaluate python application security posture. Triggers on phrases like "python security review", "audit python code", "check python vulnerabilities", "OWASP python", "bandit scan", "pip-audit", "python security posture", "fastapi security", "django security", "flask security".
---

# Python Security Review (OWASP Baseline)

> "Security is not a product, but a process."
> -- Bruce Schneier, *Secrets and Lies*

> "The only truly secure system is one that is powered off, cast in a block of concrete, and sealed in a lead-lined room with armed guards."
> -- Gene Spafford

## Core Philosophy

Security is a first-class concern in every Python application, not an afterthought bolted on before deployment. The OWASP Top 10 provides a proven baseline, but it is a floor, not a ceiling — mature Python applications must go beyond the Top 10 to address framework-specific risks like Django ORM raw query injection, Flask Jinja2 SSTI, FastAPI dependency chain bypasses, and deserialization vulnerabilities in pickle-based caching.

Python's dynamic nature makes security review both more important and more subtle than in statically typed languages. Type hints are optional, `eval()` and `exec()` are first-class builtins, and the standard library includes `pickle` — a deserialization vector that has caused critical vulnerabilities in production systems. These are not theoretical risks; they are patterns that appear in real codebases and are actively exploited.

At the same time, security reviews must balance thoroughness with developer productivity. Reporting dozens of low-severity findings without prioritization creates noise that obscures real risk. Every finding must be classified by severity with evidence, and every report must include positive findings that acknowledge good practices already in place.

Manager-friendly reporting is not optional. If a security review cannot be understood by the people who authorize remediation budgets and timelines, it will not result in action. Technical detail matters for developers; executive summaries matter for decision-makers. Both audiences must be served in every report. See `references/executive-summary-template.md` for the language patterns that bridge technical findings and business impact.

## Domain Principles

| # | Principle | Description |
|---|-----------|-------------|
| 1 | **Defense in Depth** | Never rely on a single security control. Layer authentication, authorization, input validation, output encoding, and encryption so that failure of one layer does not compromise the system. |
| 2 | **Least Privilege** | Every component — database accounts, service identities, API keys, user roles — should operate with the minimum permissions required. A root database connection or an admin-by-default role is a finding, not a convenience. |
| 3 | **Input Validation** | All external input is untrusted. Validate type, length, range, and format on the server side. Pydantic v2 models in FastAPI provide structural validation; Django Form validators and DRF serializers serve the same role. Client-side validation is UX; server-side validation is security. |
| 4 | **Output Encoding** | Encode all output based on its context (HTML, JavaScript, URL, SQL). Django templates auto-escape; `mark_safe()` and `|safe` bypass it and must be justified. Jinja2 auto-escaping must be explicitly enabled. |
| 5 | **Secure Defaults** | Applications should be secure out of the box. `DEBUG=False` in production, HTTPS required, CORS restricted, authentication mandatory. Insecurity should require explicit opt-in, not the reverse. |
| 6 | **Fail Securely** | When errors occur, fail closed. Do not expose stack traces, internal paths, or database errors. Catch exceptions, log them securely, and return safe error responses. FastAPI exception handlers and Django's `DEBUG=False` are the first line of defense. |
| 7 | **Separation of Concerns** | Security logic should not be scattered across views and routes. Centralize authorization policies, validation pipelines, and sanitization services. FastAPI `Depends()` chains and Django middleware are the patterns to look for. |
| 8 | **Audit Trail** | Security-relevant events (logins, failures, privilege changes, data access) must be logged. But logs must never contain passwords, tokens, PII, or connection strings. The boundary between "enough logging" and "too much logging" is the most common misconfiguration. |
| 9 | **Dependency Awareness** | Every pip package is attack surface. Outdated packages with known CVEs are the easiest entry point for adversaries. Defer to the `supply-chain-audit` skill for comprehensive dependency analysis; use `pip-audit` and `safety check` as the first-pass tools. |
| 10 | **Framework-Specific Injection Patterns** | Each Python web framework has unique injection surfaces: Django ORM `raw()` and `extra()` queries, Flask/Jinja2 SSTI via `render_template_string()`, FastAPI query parameter injection when passed to shell commands, and `pickle.loads()` on untrusted data. Always identify the framework before scanning. |

## Knowledge Base Lookups

Use `search_knowledge` (grounded-code-mcp) to ground decisions in authoritative references.

| Query | When to Call |
|-------|--------------|
| `search_knowledge("OWASP python security bandit injection")` | At RECONNAISSANCE phase — load authoritative OWASP categories before scanning |
| `search_knowledge("pip-audit safety dependency vulnerability python")` | During dependency scan — confirms pip-audit and safety usage patterns |
| `search_knowledge("FastAPI Django Flask authentication JWT python")` | During authentication/authorization scan — confirms secure patterns |
| `search_knowledge("SQL injection parameterized queries SQLAlchemy Django ORM")` | When reviewing data access layer — authoritative injection prevention patterns |
| `search_knowledge("logging sensitive data PII credentials security python")` | During logging hygiene review — confirms what must not appear in logs |
| `search_knowledge("NIST input validation output encoding secure defaults python")` | When scoring findings against compliance baselines |

**Protocol:** Search at RECONNAISSANCE phase and before scoring any finding category. Cite the source path in the executive summary and technical findings.

## Workflow

### Phase 1: RECONNAISSANCE

**Objective:** Determine the technology stack, hosting model, and attack surface before scanning.

**Steps:**

1. Find all Python files and determine framework (FastAPI, Django, Flask, or bare WSGI/ASGI)
2. Identify application type: REST API, web app, background worker, CLI tool
3. Locate configuration files (`settings.py`, `.env`, `config.py`, `pyproject.toml`)
4. Identify authentication mechanism (JWT, session-based, OAuth2, API key, custom)
5. Identify ORM/database access layer (SQLAlchemy, Django ORM, raw `psycopg2`, etc.)
6. Identify logging framework (`logging`, `structlog`, `loguru`)
7. Identify validation framework (Pydantic v2, Django Forms, DRF serializers, marshmallow)

```bash
# Find all Python files
find . -name "*.py" | head -30

# Identify framework
grep -r "from fastapi\|import fastapi\|from flask\|import flask\|from django\|import django" --include="*.py" | head -10

# Find configuration files
find . -name "settings.py" -o -name ".env" -o -name "config.py" | head -10

# Identify authentication setup
grep -r "jwt\|JWT\|OAuth2\|APIKeyHeader\|login_required\|Depends.*current_user" --include="*.py" | head -20

# Identify ORM usage
grep -r "from sqlalchemy\|from django.db\|import psycopg2\|import sqlite3" --include="*.py" | head -10
```

### Phase 2: SCAN

**Objective:** Run bandit and grep patterns for each OWASP Top 10 category plus Python-specific checks.

Use `references/owasp-python-checklist.md` for detailed patterns and code examples per category.

**Automated SAST scan:**

```bash
# Run bandit (SAST for Python)
bandit -r . -f json -o bandit-report.json
bandit -r . --severity-level medium  # human-readable summary

# Dependency vulnerability scan
pip-audit --format json > pip-audit-report.json
pip-audit  # human-readable summary

# Safety check (alternative/complement to pip-audit)
safety check --full-report
```

**OWASP Top 10 Quick Scan:**

```bash
# A01: Broken Access Control
grep -rn "login_required\|permission_required\|Depends.*current_user\|@require_permission" --include="*.py"
grep -rn "AllowAny\|IsAuthenticated\|IsAdminUser" --include="*.py"

# A02: Cryptographic Failures
grep -rn "import hashlib\|import md5\|import sha\|random\." --include="*.py"
grep -rn "SECRET_KEY\|password\s*=\s*['\"]" --include="*.py"

# A03: Injection
grep -rn "\.raw(\|\.extra(\|execute.*%\|execute.*format\|execute.*f\"" --include="*.py"
grep -rn "eval(\|exec(\|subprocess.*shell=True" --include="*.py"
grep -rn "render_template_string\|Markup(" --include="*.py"

# A04: Insecure Design
grep -rn "pickle\.loads\|pickle\.load\|yaml\.load(" --include="*.py"

# A05: Security Misconfiguration
grep -rn "DEBUG\s*=\s*True\|ALLOWED_HOSTS\s*=\s*\[\s*['\"]?\*" --include="*.py"
grep -rn "allow_origins.*\*\|CORSMiddleware" --include="*.py"

# A06: Vulnerable Components — handled by pip-audit above

# A07: Auth Failures
grep -rn "check_password\|verify_password\|bcrypt\|argon2\|pbkdf2" --include="*.py"
grep -rn "session\[.*\]\s*=\|request\.session\[" --include="*.py"

# A08: Software Integrity
grep -rn "requests\.get.*verify=False\|urllib.*verify=False" --include="*.py"

# A09: Logging Failures
grep -rn "logging\..*password\|log\..*token\|logger\..*secret" --include="*.py"
grep -rn "print.*password\|print.*token\|print.*secret" --include="*.py"

# A10: SSRF
grep -rn "requests\.get.*request\.\|requests\.post.*request\.\|httpx.*request\." --include="*.py"
```

### Phase 3: REPORT

**Objective:** Classify findings by severity, produce technical findings table, and generate executive summary.

**Severity classification:**

| Severity | CVSS Range | Examples |
|----------|-----------|---------|
| Critical | 9.0–10.0 | SQL injection, RCE via `eval()`/`pickle`, hardcoded secrets |
| High | 7.0–8.9 | Broken auth, SSRF, insecure deserialization, missing HTTPS |
| Medium | 4.0–6.9 | CORS misconfiguration, weak crypto, verbose error messages |
| Low | 0.1–3.9 | Missing security headers, overly broad logging, debug endpoints |
| Informational | N/A | Positive findings, best practices already in place |

Use `references/executive-summary-template.md` for the manager-friendly report format.

### Phase 4: RECOMMEND

**Objective:** Provide prioritized, actionable remediation steps for each finding.

**Prioritization order:**
1. Critical findings — remediate before next deployment
2. High findings — remediate within current sprint
3. Medium findings — remediate within current quarter
4. Low findings — add to technical debt backlog
5. Informational — acknowledge and document

## State Block

```xml
<python-security-state>
  phase: RECONNAISSANCE | SCAN | REPORT | RECOMMEND | COMPLETE
  framework_detected: fastapi | django | flask | unknown
  auth_mechanism: jwt | session | oauth2 | apikey | custom | none
  findings_count: 0
  critical_count: 0
  high_count: 0
  medium_count: 0
  low_count: 0
  bandit_clean: true | false | not_run
  pip_audit_clean: true | false | not_run
  last_action: [description]
  next_action: [description]
</python-security-state>
```

## Output Templates

### Executive Summary (Manager-Friendly)

```markdown
## Security Review: [Application Name]
**Date:** YYYY-MM-DD  
**Reviewer:** AI Security Review (python-security-review skill)  
**Framework:** [FastAPI / Django / Flask]  
**Scope:** [Brief description of what was reviewed]

### Risk Summary

| Severity | Count | Business Impact |
|----------|-------|----------------|
| Critical | N | Immediate exploitation risk; data breach or system compromise possible |
| High | N | Significant risk; exploitation likely without remediation |
| Medium | N | Moderate risk; exploitation requires specific conditions |
| Low | N | Minor risk; defense-in-depth improvement |

### Top 3 Findings (Plain Language)

1. **[Finding Name]** — [One sentence explaining the risk in business terms, not technical jargon]
2. **[Finding Name]** — [One sentence explaining the risk in business terms]
3. **[Finding Name]** — [One sentence explaining the risk in business terms]

### What Is Working Well

- [Positive finding 1]
- [Positive finding 2]

### Recommended Next Steps

1. [Immediate action — Critical findings]
2. [Short-term action — High findings]
3. [Medium-term action — Medium findings]
```

### Technical Findings Table

```markdown
## Technical Findings

| ID | Severity | Category | File | Line | Description | Remediation |
|----|----------|----------|------|------|-------------|-------------|
| F-001 | Critical | A03 Injection | app/db.py | 42 | Raw SQL with string formatting | Use parameterized queries |
| F-002 | High | A02 Crypto | config/settings.py | 8 | Hardcoded SECRET_KEY | Load from environment variable |
```

## AI Discipline Rules

### CRITICAL: Never Assert a Vulnerability Without Reading the Code

**WRONG:**
```
The grep output shows `execute(` — this is a SQL injection vulnerability.
```

**RIGHT:**
```
The grep output shows `execute(` at db.py:42. Reading the code:
  cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
This is parameterized incorrectly — user_id is interpolated directly.
This is a confirmed SQL injection vulnerability (F-001, Critical).
```

### REQUIRED: Run bandit Before Reporting SAST Findings

**WRONG:** Report injection findings based solely on grep patterns without running bandit.

**RIGHT:** Run `bandit -r . --severity-level medium` first. Use grep patterns to supplement bandit, not replace it. Bandit's B-codes (B608 for SQL injection, B301 for pickle, B102 for exec) are authoritative.

### CRITICAL: Distinguish False Positives

**WRONG:** Report every `eval(` as a vulnerability.

**RIGHT:** Read the context. `eval(ast.literal_eval(user_input))` is still dangerous. `eval("2 + 2")` with a hardcoded string is not. Bandit will flag both — the reviewer must distinguish them.

### REQUIRED: Always Check pip-audit Before Reporting Dependency Findings

**WRONG:** Report a dependency as vulnerable based on a known CVE without running pip-audit.

**RIGHT:** Run `pip-audit` first. If pip-audit finds no issue, the package may be patched. If pip-audit confirms the CVE, cite the CVE number and the patched version.

### CRITICAL: Severity Must Match Evidence

**WRONG:** Mark a finding as Critical because it "looks bad."

**RIGHT:** Map every finding to an OWASP category and a CVSS score range. Critical = 9.0+, which requires a realistic attack path to data breach or system compromise. If you cannot describe the attack path, the finding is not Critical.

## Anti-Patterns Table

| # | Anti-Pattern | Why It Fails | Correct Approach |
|---|-------------|-------------|-----------------|
| 1 | **Django ORM `raw()` without parameterization** | `Model.objects.raw(f"SELECT * FROM table WHERE id = {user_id}")` is SQL injection | Use `Model.objects.raw("SELECT * FROM table WHERE id = %s", [user_id])` |
| 2 | **Hardcoded secrets in `settings.py`** | `SECRET_KEY = "my-secret-key"` committed to git exposes credentials permanently | Load from environment: `SECRET_KEY = os.environ["SECRET_KEY"]` |
| 3 | **`DEBUG=True` in production** | Exposes stack traces, local variables, and SQL queries to any user who triggers an error | Set `DEBUG=False`; use a proper error tracking service (Sentry) |
| 4 | **CORS allow-all in FastAPI** | `allow_origins=["*"]` with `allow_credentials=True` is a CORS misconfiguration that enables CSRF | Specify exact origins; never combine `allow_origins=["*"]` with `allow_credentials=True` |
| 5 | **`pickle.loads()` on untrusted data** | Pickle deserialization executes arbitrary Python code — any attacker-controlled pickle payload achieves RCE | Use JSON, msgpack, or protobuf for untrusted data; never unpickle from external sources |
| 6 | **`subprocess(shell=True)` with user input** | `subprocess.run(f"ls {user_path}", shell=True)` is OS command injection | Use `subprocess.run(["ls", user_path], shell=False)` with a list of arguments |
| 7 | **`yaml.load()` without `Loader`** | `yaml.load(user_input)` executes arbitrary Python via YAML tags | Use `yaml.safe_load(user_input)` always |
| 8 | **Logging passwords or tokens** | `logger.info(f"Login attempt: {username} / {password}")` stores credentials in log files | Log only non-sensitive identifiers: `logger.info(f"Login attempt: {username}")` |
| 9 | **`requests.get(url, verify=False)`** | Disabling TLS verification enables MITM attacks | Remove `verify=False`; if using a private CA, pass `verify="/path/to/ca-bundle.crt"` |
| 10 | **`render_template_string()` with user input** | Flask's `render_template_string(user_input)` enables Server-Side Template Injection (SSTI) | Never pass user input to `render_template_string()`; use `render_template()` with static template names |

## Error Recovery

### bandit false positives obscure real findings

```
Symptoms: bandit reports dozens of B-code findings; real vulnerabilities are buried in noise

Recovery:
1. Filter by severity: `bandit -r . --severity-level high` to see only high/critical first
2. For each B-code, read the actual code at the reported line
3. Mark confirmed false positives with `# nosec B<code>` and a justification comment
4. Re-run bandit to confirm the noise is reduced
5. Document all `# nosec` suppressions in the findings report as "Reviewed and Suppressed"
6. Never suppress without reading the code — suppression without review is a security gap
```

### pip-audit finds a vulnerability with no available patch

```
Symptoms: pip-audit reports a CVE in a dependency; no patched version exists

Recovery:
1. Check the CVE details: is the vulnerable code path actually used by this application?
2. If the vulnerable function is not called: document as "CVE present, not exploitable in this context" with evidence
3. If the vulnerable function is called: assess exploitability — is the input attacker-controlled?
4. Check for a fork or alternative package that has patched the issue
5. Add a compensating control (input validation, WAF rule) if no patch exists
6. Add to the POA&M with a target remediation date and monitoring plan
7. Never mark as "not a finding" without documented evidence of non-exploitability
```

### Legacy code with no type hints obscures injection surface

```
Symptoms: Codebase has no type hints; grep patterns produce too many false positives to triage

Recovery:
1. Focus bandit output first — it performs AST analysis, not string matching
2. Narrow grep patterns to the most dangerous sinks: eval(, exec(, .raw(, pickle.loads(, shell=True
3. Trace data flow from entry points (request handlers) to dangerous sinks manually for top 3 findings
4. Note in the report: "Type hint coverage is low; injection surface analysis is incomplete. Recommend adding mypy and re-running review."
5. Do not mark the review as complete if critical sinks cannot be traced — flag as "Partial Review"
```

## Integration with Other Skills

| Skill | Relationship |
|-------|-------------|
| `python-security-review-federal` | Federal overlay on this base review — NIST SP 800-53, FIPS 140-2/3, DOE Order 205.1B. Always run this review first. |
| `supply-chain-audit` | Comprehensive dependency vulnerability analysis. Use when pip-audit findings require deeper CVE correlation or license compliance review. |
| `python-arch-review` | Architecture quality gate. Run before security review to understand the codebase structure; security review findings are more actionable with architecture context. |
| `dotnet-security-review` | Cross-reference for teams with mixed Python/.NET stacks. OWASP categories are identical; tooling and patterns differ. |
| `fastapi-scaffolder` | When remediation requires adding authentication, authorization, or input validation to FastAPI endpoints, use this skill for correct scaffold patterns. |
