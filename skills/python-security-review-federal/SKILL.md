---
name: python-security-review-federal
description: Conducts security reviews of Python applications for federal/DOE/DOD environments. Extends python-security-review with NIST SP 800-53 control mapping, DOE Order 205.1B compliance, FIPS 140-2/3 cryptographic requirements, and CUI handling. Generates federal-compliant reports with impact levels and POA&M-ready findings. Trigger phrases: "federal python security", "NIST python", "FISMA python", "DOE python security", "python ATO review", "python FIPS compliance", "CUI python", "python federal compliance", "python NIST 800-53".
---

# Python Security Review — Federal Edition

> "In God we trust. All others we monitor."
> -- NSA motto (attributed)

> "The question is not whether you will be attacked, but whether you will know when it happens."
> -- NIST SP 800-137

## Core Philosophy

Federal Python applications face the same OWASP Top 10 risks as commercial applications — plus a layer of compliance obligations that are legally binding and auditable. NIST SP 800-53, FIPS 140-2/3, DOE Order 205.1B, and FISMA requirements are not optional enhancements; they are conditions of operation.

**Base review first, always.** This skill extends `python-security-review` — it does not replace it. Run the base OWASP review first, then apply the federal overlay. A federal review that skips the OWASP baseline is incomplete.

The federal overlay adds three dimensions that the base review does not cover:

1. **NIST SP 800-53 control mapping** — every finding must be mapped to the control family it violates (AC, IA, SC, AU, etc.)
2. **FIPS 140-2/3 cryptographic compliance** — Python's `cryptography` library must be used in FIPS mode; `hashlib` algorithms must be from the approved list; no MD5 or SHA1 for security purposes
3. **POA&M output** — findings must be formatted as Plan of Action and Milestones entries, not just a findings table

CUI (Controlled Unclassified Information) handling is a special concern in Python applications. CUI must not appear in logs, must be encrypted at rest and in transit, and must not be stored in development or test environments without authorization.

## Domain Principles

| # | Principle | Description |
|---|-----------|-------------|
| 1 | **Base Review First** | The OWASP baseline from `python-security-review` is a prerequisite. Federal overlay findings are additive, not a replacement. Never skip the base review. |
| 2 | **NIST Control Mapping** | Every finding must map to a NIST SP 800-53 control family. A SQL injection finding maps to SI-10 (Information Input Validation). A missing audit log maps to AU-2 (Event Logging). Unmapped findings cannot be tracked in a POA&M. |
| 3 | **FIPS 140-2/3 Cryptography** | Only FIPS-approved algorithms are permitted: AES-128/256, SHA-256/384/512, RSA-2048+, ECDSA P-256/P-384. Python's `cryptography` library supports FIPS mode via OpenSSL FIPS provider. `hashlib` uses the system OpenSSL — verify FIPS mode is active. |
| 4 | **CUI Protection** | CUI must be identified, labeled, encrypted at rest (AES-256), encrypted in transit (TLS 1.2+), and access-controlled. CUI must not appear in logs, error messages, or debug output. |
| 5 | **Audit Trail Completeness** | AU-2 requires logging of defined auditable events. AU-3 requires log content (timestamp, user, event type, outcome, source IP). AU-9 requires log protection. Python logging must meet all three. |
| 6 | **Least Privilege (AC-6)** | Service accounts, database connections, and API keys must operate with minimum required permissions. Privilege escalation paths must be documented and controlled. |
| 7 | **Configuration Management (CM-6)** | Security configuration baselines must be documented and enforced. `DEBUG=False`, `ALLOWED_HOSTS`, CORS restrictions, and TLS configuration are CM-6 items. |
| 8 | **Identification and Authentication (IA)** | Multi-factor authentication required for privileged access (IA-2). Password complexity enforced (IA-5). Session management compliant with IA-11 (re-authentication). |
| 9 | **Incident Response Readiness (IR)** | The application must support incident response: structured logs, correlation IDs, and the ability to revoke sessions and API keys without downtime. |
| 10 | **Supply Chain Risk (SR-3)** | All Python dependencies must be from trusted sources with integrity verification. `pip install --require-hashes` in production. No packages from unofficial indexes without approval. |

## Knowledge Base Lookups

Use `search_knowledge` (grounded-code-mcp) to ground decisions in authoritative references.

| Query | When to Call |
|-------|--------------|
| `search_knowledge("NIST SP 800-53 control families python")` | At RECONNAISSANCE phase — load control family mapping |
| `search_knowledge("FIPS 140-2 cryptography python hashlib")` | During cryptographic review — confirm FIPS-approved algorithms |
| `search_knowledge("DOE cybersecurity order 205.1B")` | When reviewing DOE-specific requirements |
| `search_knowledge("CUI controlled unclassified information handling python")` | When CUI data flows are identified |
| `search_knowledge("FISMA ATO authorization to operate requirements")` | When preparing ATO documentation |
| `search_knowledge("POA&M plan of action milestones federal security")` | During REPORT phase — confirm POA&M format requirements |

**Protocol:** Search at RECONNAISSANCE phase and before each control family assessment. Cite NIST control IDs in every finding.

## Workflow

### Phase 0: Prerequisites

**Before starting this review:**
- [ ] `python-security-review` base review has been completed
- [ ] Base review findings are available for reference
- [ ] System categorization (Low/Moderate/High) is known or can be determined

### Phase 1: RECONNAISSANCE (Federal Extension)

**Objective:** Extend base reconnaissance with federal-specific context.

**Steps:**

1. Determine system categorization: Low, Moderate, or High impact (FIPS 199)
2. Identify CUI data flows: where is CUI received, processed, stored, transmitted?
3. Identify the authorization boundary
4. Determine applicable overlays: DOE Order 205.1B, CMMC, FedRAMP, etc.
5. Identify cryptographic implementations

```bash
# Find cryptographic usage
grep -rn "import hashlib\|from cryptography\|import ssl\|import hmac" --include="*.py"

# Find CUI-adjacent data handling (keywords vary by agency)
grep -rn "CUI\|FOUO\|sensitive\|classified\|pii\|ssn\|ein" --include="*.py" -i | head -20

# Find logging configuration
grep -rn "logging\.basicConfig\|structlog\|loguru\|getLogger" --include="*.py" | head -10

# Find TLS/SSL configuration
grep -rn "ssl\.create_default_context\|verify=False\|CERT_NONE\|TLSv1\b" --include="*.py"
```

### Phase 2: FEDERAL SCAN

**Objective:** Assess compliance with NIST SP 800-53 control families relevant to the system categorization.

**Priority control families for Python web applications:**

| Control Family | Key Controls | Python-Specific Checks |
|---------------|-------------|----------------------|
| AC (Access Control) | AC-2, AC-3, AC-6, AC-17 | Authentication decorators, RBAC implementation, least privilege |
| AU (Audit and Accountability) | AU-2, AU-3, AU-9, AU-12 | Structured logging, log content, log protection |
| IA (Identification and Authentication) | IA-2, IA-5, IA-8, IA-11 | MFA, password policy, session management |
| SC (System and Communications Protection) | SC-8, SC-12, SC-13, SC-28 | TLS, key management, FIPS crypto, encryption at rest |
| SI (System and Information Integrity) | SI-2, SI-3, SI-10 | Patching, SAST (bandit), input validation |
| CM (Configuration Management) | CM-6, CM-7 | Secure defaults, least functionality |
| SR (Supply Chain Risk Management) | SR-3, SR-11 | Dependency integrity, pip-audit |

**FIPS Cryptography Check:**

```bash
# Check for non-FIPS algorithms used for security purposes
grep -rn "md5\|sha1\b\|des\b\|rc4\|blowfish" --include="*.py" -i

# Check for FIPS-approved usage
grep -rn "AES\|SHA256\|SHA384\|SHA512\|RSA\|ECDSA" --include="*.py"

# Check for random vs secrets module
grep -rn "import random\b\|random\.random\|random\.choice\|random\.randint" --include="*.py"

# Check TLS version
grep -rn "TLSv1\b\|TLSv1_1\|SSLv2\|SSLv3" --include="*.py"
```

### Phase 3: FEDERAL REPORT

**Objective:** Produce NIST-mapped findings and POA&M entries.

Use `references/nist-control-mapping.md` for control family → Python implementation mapping.
Use `references/poam-template.md` for POA&M entry format.

**Impact Level Determination:**

| Impact Level | System Categorization | Control Baseline |
|-------------|----------------------|-----------------|
| Low | FIPS 199 Low | NIST 800-53 Low baseline |
| Moderate | FIPS 199 Moderate | NIST 800-53 Moderate baseline |
| High | FIPS 199 High | NIST 800-53 High baseline |

### Phase 4: POA&M GENERATION

**Objective:** Format all findings as POA&M entries for ATO package submission.

See `references/poam-template.md` for the required format.

## State Block

```xml
<python-federal-security-state>
  phase: PREREQUISITES | RECONNAISSANCE | FEDERAL_SCAN | FEDERAL_REPORT | POAM | COMPLETE
  base_review_complete: true | false
  system_categorization: low | moderate | high | unknown
  applicable_overlays: [doe | cmmc | fedramp | none]
  cui_data_flows_identified: true | false
  fips_compliant: true | false | partial | not_assessed
  findings_count: 0
  poam_entries_generated: 0
  last_action: [description]
  next_action: [description]
</python-federal-security-state>
```

## Output Templates

### Federal Findings Table

```markdown
## Federal Security Findings

| ID | Severity | NIST Control | OWASP | File | Line | Description | Remediation | POA&M Priority |
|----|----------|-------------|-------|------|------|-------------|-------------|---------------|
| FF-001 | High | SC-13 | A02 | crypto/utils.py | 15 | MD5 used for password hashing | Replace with argon2 | P1 |
| FF-002 | High | AU-3 | A09 | logging/config.py | 8 | Log records missing required AU-3 fields | Add user ID, event type, outcome | P2 |
```

### Impact Level Summary

```markdown
## Federal Compliance Summary

**System Categorization:** [Low / Moderate / High]
**Applicable Overlays:** [DOE 205.1B / CMMC Level N / FedRAMP / None]

| Control Family | Status | Findings |
|---------------|--------|---------|
| AC (Access Control) | ✓ Compliant / ⚠ Partial / ✗ Non-Compliant | N findings |
| AU (Audit) | ✓ / ⚠ / ✗ | N findings |
| IA (Authentication) | ✓ / ⚠ / ✗ | N findings |
| SC (Communications) | ✓ / ⚠ / ✗ | N findings |
| SI (Integrity) | ✓ / ⚠ / ✗ | N findings |
| CM (Configuration) | ✓ / ⚠ / ✗ | N findings |
| SR (Supply Chain) | ✓ / ⚠ / ✗ | N findings |
```

## AI Discipline Rules

### CRITICAL: Base Review Is a Prerequisite

**WRONG:** Start the federal review without completing the OWASP base review.

**RIGHT:** Confirm `python-security-review` has been completed. Reference its findings in the federal overlay. Do not re-run the base scan — extend it.

### REQUIRED: Every Finding Maps to a NIST Control

**WRONG:** Report a finding without a NIST control ID.

**RIGHT:** Every finding in the federal report includes the NIST SP 800-53 control ID (e.g., SC-13, AU-2, IA-5). If you cannot map a finding to a control, it belongs in the base review, not the federal overlay.

### CRITICAL: FIPS Compliance Is Binary

**WRONG:** "The application uses some FIPS-approved algorithms."

**RIGHT:** FIPS compliance requires ALL cryptographic operations to use FIPS-approved algorithms AND the cryptographic module to be FIPS-validated. Partial compliance is non-compliance. Document exactly which operations are compliant and which are not.

## Anti-Patterns Table

| # | Anti-Pattern | Why It Fails | Correct Approach |
|---|-------------|-------------|-----------------|
| 1 | **Skipping the base OWASP review** | Federal overlay assumes OWASP findings are already addressed; skipping creates gaps | Always run `python-security-review` first |
| 2 | **MD5/SHA1 for security purposes** | Not FIPS-approved for security use; violates SC-13 | Use SHA-256 minimum; argon2/bcrypt for passwords |
| 3 | **CUI in log files** | Violates AU-3 (log content) and CUI handling requirements | Mask or omit CUI from all log statements |
| 4 | **No MFA for privileged access** | Violates IA-2(1) for Moderate/High systems | Implement TOTP or PIV/CAC for admin accounts |
| 5 | **`verify=False` in requests** | Violates SC-8 (transmission confidentiality) | Always verify TLS certificates; use system CA bundle |
| 6 | **Unprotected log files** | Violates AU-9 (protection of audit information) | Restrict log file permissions; ship to protected SIEM |
| 7 | **No session re-authentication** | Violates IA-11 for Moderate/High systems | Require re-authentication after inactivity timeout |
| 8 | **Dependencies without hash verification** | Violates SR-3 (supply chain controls) | Use `pip install --require-hashes` in production |
| 9 | **Debug endpoints in production** | Violates CM-7 (least functionality) | Remove or gate all debug/diagnostic endpoints |
| 10 | **POA&M findings without milestones** | POA&M entries without scheduled completion dates are not actionable for ATO | Every POA&M entry must have a scheduled completion date and responsible party |

## Error Recovery

### System categorization is unknown

```
Symptoms: Cannot determine if system is Low, Moderate, or High impact

Recovery:
1. Ask the system owner for the FIPS 199 categorization document
2. If unavailable, default to Moderate baseline (conservative)
3. Document the assumption: "System categorization unknown; Moderate baseline applied"
4. Flag as a finding: "System categorization not documented — required for ATO"
5. Do not proceed with High baseline without explicit confirmation
```

### FIPS mode cannot be verified

```
Symptoms: Cannot determine if Python's OpenSSL is running in FIPS mode

Recovery:
1. Check: python -c "import ssl; print(ssl.OPENSSL_VERSION)"
2. Check: python -c "import hashlib; print(hashlib.algorithms_available)"
3. Check for FIPS-enabled OpenSSL: openssl version -a | grep FIPS
4. If FIPS mode cannot be confirmed, report as: "FIPS compliance unverified — SC-13 finding"
5. Recommend: deploy on a FIPS-validated OS (RHEL with FIPS mode enabled)
```

### POA&M entry has no remediation owner

```
Symptoms: Finding identified but no team or individual can be assigned

Recovery:
1. Assign to the system owner as default responsible party
2. Note in the POA&M: "Responsible party TBD — system owner to assign"
3. Set scheduled completion date to 30 days from review date for Critical/High
4. Flag the unassigned entry in the executive summary
5. Do not omit the entry — an unassigned POA&M item is better than a missing one
```

## Integration with Other Skills

| Skill | Relationship |
|-------|-------------|
| `python-security-review` | **Prerequisite.** Run the base OWASP review before this federal overlay. |
| `supply-chain-audit` | SR-3 compliance requires comprehensive dependency analysis. Use for CVE correlation and license review. |
| `dotnet-security-review-federal` | Cross-reference for mixed Python/.NET federal stacks. NIST controls are language-agnostic; tooling differs. |
| `python-arch-review` | Architecture review provides system boundary context needed for NIST control scoping. |
