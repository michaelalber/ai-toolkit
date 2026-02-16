---
name: dotnet-security-review-federal
description: Conducts security reviews of .NET applications for LANL/DOE/DOD environments. Extends the base dotnet-security-review with NIST SP 800-53 control mapping, DOE Order 205.1B compliance, FIPS 140-2/3 cryptographic requirements, and CUI handling. Generates federal-compliant reports with impact levels and POA&M-ready findings. Use for federal systems, LANL projects, DOE applications, or when FISMA/FedRAMP compliance is required.
---

# .NET Security Review - Federal/LANL Edition

Conducts comprehensive security reviews of .NET applications in LANL/DOE/DOD environments. **This skill extends the base `dotnet-security-review` skill** with federal compliance overlays.

## Quick Start

When triggered:
1. **First**: Execute all steps from the base `dotnet-security-review` skill (OWASP Top 10 scan)
2. **Then**: Apply federal compliance overlays from this skill
3. **Finally**: Generate the federal-format security report with NIST control mappings

## Base Skill Reference

This skill builds upon `dotnet-security-review`. Execute that skill's full process first:
- Reconnaissance (framework, application type)
- OWASP Top 10 scan (A01-A10)
- Telerik UI components scan
- jQuery/JavaScript XSS scan
- SQL Server stored procedure scan
- FluentValidation scan
- Logging security scan (Serilog/NLog)

**Reference**: `../dotnet-security-review/SKILL.md` and its `references/` directory.

---

## Federal Compliance Overlays

After completing the base OWASP scan, apply these federal-specific checks.

### Step 1: Determine System Impact Level

```bash
# Check for indicators of system classification
grep -rn "CUI\|FOUO\|Controlled\|Classified\|UCNI\|OUO" --include="*.md" --include="*.txt" --include="*.cs"

# Check for PII/PHI handling
grep -rn "SSN\|SocialSecurity\|DateOfBirth\|HealthRecord\|HIPAA" --include="*.cs"

# Check for financial data
grep -rn "CreditCard\|BankAccount\|RoutingNumber" --include="*.cs"
```

**Impact Level Determination:**
| Data Types Present | Likely Impact Level |
|-------------------|---------------------|
| Public data only | Low |
| PII, business sensitive | Moderate |
| CUI, UCNI, mission-critical | High |

### Step 2: NIST SP 800-53 Control Verification

Use `references/nist-800-53-mapping.md` for detailed control mapping.

**Access Control (AC) Family:**
```bash
# AC-2: Account Management
grep -rn "CreateUser\|DeleteUser\|DisableUser\|UserManager" --include="*.cs"
grep -rn "account.*expir\|password.*expir" -i --include="*.cs"

# AC-3: Access Enforcement
grep -rn "\[Authorize\]\|\[AllowAnonymous\]" --include="*.cs"
grep -rn "Policy\|Claim\|Role" --include="*.cs" | grep -i "auth"

# AC-6: Least Privilege
grep -rn "Admin\|SuperUser\|Root\|Elevated" --include="*.cs"

# AC-7: Unsuccessful Logon Attempts
grep -rn "Lockout\|MaxFailedAccessAttempts\|LockoutEnd" --include="*.cs"

# AC-11: Session Lock
grep -rn "SessionTimeout\|IdleTimeout\|ExpireTimeSpan" --include="*.cs"

# AC-17: Remote Access
grep -rn "VPN\|RemoteDesktop\|SSH\|TwoFactor\|MFA" --include="*.cs"
```

**Audit and Accountability (AU) Family:**
```bash
# AU-2: Audit Events
grep -rn "ILogger\|Log\.\|_logger\." --include="*.cs" | head -30

# AU-3: Content of Audit Records
grep -rn "LogInformation\|LogWarning\|LogError" --include="*.cs" | head -20

# AU-6: Audit Review, Analysis, and Reporting
grep -rn "Serilog\|NLog\|log4net\|ApplicationInsights" --include="*.cs" --include="*.csproj"

# AU-9: Protection of Audit Information
grep -rn "LogPath\|LogFile\|WriteTo" --include="*.cs" --include="*.json" --include="*.config"

# AU-12: Audit Generation
grep -rn "AuditLog\|SecurityEvent\|AuditTrail" --include="*.cs"
```

**Identification and Authentication (IA) Family:**
```bash
# IA-2: Identification and Authentication
grep -rn "AddAuthentication\|UseAuthentication\|SignInManager" --include="*.cs"

# IA-2(1): Multi-factor Authentication
grep -rn "TwoFactor\|MFA\|Authenticator\|TOTP" --include="*.cs"

# IA-5: Authenticator Management
grep -rn "PasswordOptions\|RequiredLength\|RequireDigit" --include="*.cs"

# IA-5(1): Password-based Authentication
grep -rn "PBKDF2\|Argon2\|bcrypt\|PasswordHasher" --include="*.cs"

# IA-8: Identification and Authentication (Non-Organizational Users)
grep -rn "ExternalLogin\|OAuth\|SAML\|OpenId" --include="*.cs"
```

**System and Communications Protection (SC) Family:**
```bash
# SC-8: Transmission Confidentiality and Integrity
grep -rn "UseHttps\|RequireHttps\|UseHsts" --include="*.cs"
grep -rn "TLS\|SSL\|Certificate" --include="*.cs" --include="*.config"

# SC-12: Cryptographic Key Establishment
grep -rn "KeyVault\|DataProtection\|CertificateStore" --include="*.cs"

# SC-13: Cryptographic Protection (FIPS 140-2)
grep -rn "AES\|RSA\|SHA256\|SHA384\|SHA512" --include="*.cs"
grep -rn "MD5\|SHA1\|DES\|3DES\|RC4" --include="*.cs"  # Non-compliant

# SC-28: Protection of Information at Rest
grep -rn "Encrypt\|DataProtection\|TDE\|AlwaysEncrypted" --include="*.cs"
```

### Step 3: DOE-Specific Requirements

Use `references/doe-cybersecurity.md` for detailed DOE requirements.

```bash
# Check for DOE-specific patterns
grep -rn "NNSA\|DOE\|LANL\|Laboratory" --include="*.cs" --include="*.config" --include="*.md"

# Privileged access management
grep -rn "ServiceAccount\|SystemAccount\|Impersonate" --include="*.cs"

# Network segmentation indicators
grep -rn "DMZ\|Firewall\|NetworkZone\|Enclave" --include="*.cs" --include="*.config"
```

### Step 4: FIPS 140-2/3 Cryptographic Compliance

Use `references/fips-crypto-requirements.md` for detailed requirements.

```bash
# FIPS-compliant algorithms
grep -rn "Aes\|RSACryptoServiceProvider\|ECDsa\|SHA256\|SHA384\|SHA512" --include="*.cs"

# NON-compliant algorithms (findings)
grep -rn "MD5\|SHA1\|DES\|TripleDES\|RC2\|RC4\|Rijndael" --include="*.cs"

# Check for FIPS mode
grep -rn "UseFipsAlgorithms\|CryptoConfig\|FIPSAlgorithmPolicy" --include="*.cs" --include="*.config"

# Random number generation
grep -rn "Random\(\)\|new Random\|RandomNumberGenerator" --include="*.cs"

# Key sizes
grep -rn "KeySize\|keysize" --include="*.cs"
```

### Step 5: CUI Handling Requirements

Use `references/cui-handling.md` for detailed CUI requirements.

```bash
# CUI markers in code/comments
grep -rn "CUI\|Controlled Unclassified\|FOUO\|SBU\|LES" --include="*.cs" --include="*.md"

# Data classification patterns
grep -rn "Classification\|DataCategory\|SensitivityLevel" --include="*.cs"

# Export/download functionality (potential CUI exfiltration)
grep -rn "Download\|Export\|FileResult\|File(" --include="*.cs"

# Print functionality
grep -rn "Print\|Report\|PDF" --include="*.cs"

# Email functionality (CUI transmission)
grep -rn "SmtpClient\|SendGrid\|MailMessage\|EmailService" --include="*.cs"
```

### Step 6: Supply Chain Security (EO 14028)

```bash
# Check for SBOM capability
ls -la **/sbom* **/bom* 2>/dev/null
grep -rn "CycloneDX\|SPDX\|SBOM" --include="*.csproj" --include="*.json"

# Package sources (should be approved)
grep -rn "packageSources\|nuget.org\|artifactory\|nexus" --include="*.config" --include="*.json"

# Dependency pinning
grep -rn "Version=" --include="*.csproj" | grep -v "\*"
```

---

## Federal Output Format

Generate the report in this federal-compliant format:

```markdown
# Security Assessment Report: [Solution Name]

**Classification**: [UNCLASSIFIED / CUI / etc.]
**Assessment Date**: [Date]
**System Impact Level**: [Low / Moderate / High]
**Framework**: [.NET 8 / .NET Framework 4.8 / etc.]
**Application Type**: [Web API / MVC / Blazor / etc.]
**Assessor**: Claude AI Security Review

---

## Executive Summary

[Write 3-4 sentences for federal program managers explaining:
- Overall security posture relative to NIST baseline
- Number and severity of findings by impact level
- Key compliance gaps (NIST, FIPS, CUI)
- Recommended POA&M timeline]

**Example**: "This Moderate-impact system has an adequate security posture with identified gaps in NIST SP 800-53 controls. We identified 15 findings: 1 High (P1), 4 Moderate (P2), and 10 Low (P3). Critical gaps exist in SC-13 (FIPS cryptography) and AU-2 (audit events). Recommend immediate POA&M entry for P1 items with 30-day remediation target."

### Security Posture: [Critical Gap / Significant Gaps / Minor Gaps / Compliant]

| Priority | Count | NIST Impact | Remediation Window |
|----------|-------|-------------|-------------------|
| P1 (Critical) | X | High | Immediate (24-48 hrs) |
| P2 (High) | X | Moderate | 30 days |
| P3 (Medium) | X | Low | 90 days |
| P4 (Low) | X | Minimal | 180 days / Backlog |

---

## NIST SP 800-53 Control Assessment

### Access Control (AC)

| Control | Status | Finding | Priority |
|---------|--------|---------|----------|
| AC-2 Account Management | Implemented/Partial/Not Implemented | [Summary] | P1-P4 |
| AC-3 Access Enforcement | | | |
| AC-6 Least Privilege | | | |
| AC-7 Unsuccessful Logon Attempts | | | |
| AC-11 Session Lock | | | |
| AC-17 Remote Access | | | |

### Audit and Accountability (AU)

| Control | Status | Finding | Priority |
|---------|--------|---------|----------|
| AU-2 Audit Events | | | |
| AU-3 Content of Audit Records | | | |
| AU-6 Audit Review | | | |
| AU-9 Protection of Audit Info | | | |
| AU-12 Audit Generation | | | |

### Identification and Authentication (IA)

| Control | Status | Finding | Priority |
|---------|--------|---------|----------|
| IA-2 I&A (Organizational Users) | | | |
| IA-2(1) MFA | | | |
| IA-5 Authenticator Management | | | |
| IA-5(1) Password-based Auth | | | |

### System and Communications Protection (SC)

| Control | Status | Finding | Priority |
|---------|--------|---------|----------|
| SC-8 Transmission Confidentiality | | | |
| SC-12 Crypto Key Establishment | | | |
| SC-13 Cryptographic Protection | | | |
| SC-28 Protection at Rest | | | |

---

## OWASP Top 10 Assessment

[Include standard OWASP table from base skill]

| Category | Status | NIST Mapping | Findings |
|----------|--------|--------------|----------|
| A01: Broken Access Control | Pass/Fail/Partial | AC-3, AC-6 | [Summary] |
| A02: Cryptographic Failures | | SC-12, SC-13, SC-28 | |
| A03: Injection | | SI-10 | |
| A04: Insecure Design | | SA-8 | |
| A05: Security Misconfiguration | | CM-6, CM-7 | |
| A06: Vulnerable Components | | SI-2, RA-5 | |
| A07: Authentication Failures | | IA-2, IA-5 | |
| A08: Data Integrity Failures | | SI-7 | |
| A09: Logging Failures | | AU-2, AU-3, AU-12 | |
| A10: SSRF | | SC-7 | |

---

## FIPS 140-2/3 Cryptographic Compliance

| Requirement | Status | Finding |
|-------------|--------|---------|
| FIPS-approved algorithms only | Compliant/Non-compliant | [List non-compliant: MD5, SHA1, etc.] |
| Minimum key sizes (AES-128+, RSA-2048+) | | |
| Approved RNG (RNGCryptoServiceProvider) | | |
| TLS 1.2+ for transmission | | |

---

## CUI Handling Assessment

| Requirement | Status | Finding |
|-------------|--------|---------|
| CUI marking capability | | |
| Access controls for CUI | | |
| Audit logging for CUI access | | |
| Encryption at rest | | |
| Encryption in transit | | |
| Export controls | | |

---

## Detailed Findings

### P1 - Critical (Immediate Action Required)

#### [Finding ID]: [Finding Title]
- **NIST Control**: [Control ID and Name]
- **OWASP Category**: [A01-A10 if applicable]
- **Location**: [File:Line or general area]
- **Impact Statement**: [Federal impact language - what could happen to mission/data]
- **Technical Detail**: [Brief technical description]
- **Remediation**: [Specific fix with code example if applicable]
- **POA&M Recommendation**: [Milestone, resource estimate]

### P2 - High (30-Day Remediation)
[Same format]

### P3 - Medium (90-Day Remediation)
[Same format]

### P4 - Low (Backlog)
[Same format]

---

## POA&M Summary

| ID | Finding | Control | Priority | Target Date | Status |
|----|---------|---------|----------|-------------|--------|
| 1 | [Title] | [NIST] | P1 | [Date] | Open |
| 2 | | | | | |

---

## Compliance Summary

| Framework | Status | Notes |
|-----------|--------|-------|
| NIST SP 800-53 Rev 5 | Partial | [X of Y controls assessed] |
| FIPS 140-2/3 | Compliant/Non-compliant | [Summary] |
| DOE Order 205.1B | [Status] | [Notes] |
| OWASP Top 10 2021 | [X/10 Pass] | [Summary] |

---

## Positive Findings

[List security controls properly implemented - provides balance and acknowledges good practices]

1. [Good practice found]
2. [Good practice found]

---

## Recommendations

### Immediate Actions
1. [P1 items]

### 30-Day Actions
1. [P2 items]

### 90-Day Actions
1. [P3 items]

### Continuous Improvement
1. [P4 items and ongoing recommendations]

---

## Appendix A: References

- NIST SP 800-53 Rev 5: https://csrc.nist.gov/publications/detail/sp/800-53/rev-5/final
- FIPS 140-3: https://csrc.nist.gov/publications/detail/fips/140/3/final
- DOE Order 205.1B: https://www.directives.doe.gov/directives-documents/200-series/0205.1-BOrder-b
- OWASP Top 10 2021: https://owasp.org/Top10/
- 32 CFR Part 2002 (CUI): https://www.ecfr.gov/current/title-32/subtitle-B/chapter-XX/part-2002
```

---

## Priority Classification (Federal)

### P1 - Critical (Immediate)
- Active exploitation possible
- Authentication bypass
- Remote code execution
- SQL injection with data access
- Non-compliant crypto on CUI/PII (FIPS violation)
- Missing MFA on privileged accounts
- Hardcoded credentials for federal systems
- Audit logging disabled

### P2 - High (30 Days)
- Authorization flaws (IDOR)
- Sensitive data exposure
- Missing encryption at rest for PII
- Session management weaknesses
- Insufficient audit logging
- Non-FIPS algorithms on non-sensitive data
- Missing account lockout

### P3 - Medium (90 Days)
- Verbose error messages
- Missing input validation
- CORS misconfiguration
- Weak password policy (below NIST guidelines)
- Incomplete audit trails
- Missing security headers

### P4 - Low (Backlog)
- Defense-in-depth opportunities
- Best practice deviations
- Documentation gaps
- Minor hardening items

---

## Manager-Friendly Federal Language

See `references/federal-executive-templates.md` for templates.

**Instead of**: "SQL injection vulnerability via unsanitized input"

**Write**: "A vulnerability exists that could allow unauthorized access to database records containing [PII/CUI/mission data]. This finding impacts NIST control SI-10 (Information Input Validation) and could result in a data breach requiring notification under DOE Order 206.1."

---

## References

- `references/nist-800-53-mapping.md` - NIST control to OWASP mapping
- `references/doe-cybersecurity.md` - DOE Order 205.1B requirements
- `references/fips-crypto-requirements.md` - FIPS 140-2/3 compliance
- `references/cui-handling.md` - CUI handling in .NET applications
- `references/federal-executive-templates.md` - Federal report language
- `../dotnet-security-review/references/` - Base OWASP and .NET references
