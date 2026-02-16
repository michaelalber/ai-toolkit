---
name: dotnet-security-review-federal
description: >
  Conducts security reviews of .NET applications for LANL/DOE/DOD environments.
  Extends the base dotnet-security-review with NIST SP 800-53 control mapping,
  DOE Order 205.1B compliance, FIPS 140-2/3 cryptographic requirements, and CUI
  handling. Generates federal-compliant reports with impact levels and POA&M-ready
  findings. Trigger phrases: "federal security review", "NIST compliance",
  "DOE security", "FISMA", "CUI", "FIPS audit", "federal compliance",
  "LANL security", "ATO review", "POA&M generation".
---

# .NET Security Review -- Federal/LANL Edition

> "Security is not a product, but a process. It is not a technology problem --
> it is a people and management problem."
> -- Bruce Schneier

> "Compliance is the floor, not the ceiling. Meeting the minimum control
> requirements is where security begins, not where it ends."
> -- NIST Cybersecurity Framework guidance

---

## Core Philosophy

This skill provides a **federal compliance overlay** on top of the base
`dotnet-security-review` skill. It does not replace the base review -- it
extends it with the regulatory, policy, and procedural requirements specific to
U.S. federal systems, particularly those within the Department of Energy (DOE)
and national laboratory environments.

**Foundational principles:**

1. **Base review first, always.** Every federal review begins by executing
   the full `dotnet-security-review` skill. OWASP Top 10 coverage is a
   prerequisite, not an option. Federal overlays are meaningless without a
   solid technical foundation.

2. **NIST SP 800-53 Rev 5 is the framework.** All findings, controls, and
   recommendations map back to NIST control families. The framework provides
   the shared vocabulary between developers, assessors, and authorizing
   officials.

3. **Compliance is not optional.** Federal systems operate under legal
   mandates (FISMA, FIPS, EO 14028). Gaps are not "nice to fix" -- they are
   conditions that can revoke an Authorization to Operate (ATO) and halt
   mission-critical work.

4. **DOE-specific requirements exceed baselines.** DOE Order 205.1B and
   NNSA NAP 70.4 impose parameters that exceed standard NIST baselines.
   Password lengths, lockout thresholds, session timeouts, and audit
   retention all have DOE-specific values. Reference `references/doe-cybersecurity.md`.

5. **POA&M-driven remediation.** Every finding produces a Plan of Action and
   Milestones entry. Findings without POA&M entries are invisible to the
   authorization process. Every gap gets a tracking artifact.

6. **Defense-in-depth for government systems.** Federal systems face
   nation-state adversaries. A single control failure must not lead to
   compromise. Overlapping controls, boundary protections, and continuous
   monitoring are expected, not aspirational.

---

## Domain Principles

| # | Principle | Rationale |
|---|-----------|-----------|
| 1 | **Continuous Monitoring** | Federal systems require ongoing assessment per NIST SP 800-137, not point-in-time reviews. Every scan contributes to the continuous monitoring program. |
| 2 | **Least Privilege Enforcement** | AC-6 demands minimum necessary access. Broad "Admin" roles, sa database accounts, and blanket AllowAnonymous attributes are federal compliance failures. |
| 3 | **FIPS-Validated Cryptography** | SC-13 requires FIPS 140-2/3 validated modules. MD5, SHA-1, DES, 3DES, RC4, and System.Random are never acceptable in federal systems. See `references/fips-crypto-requirements.md`. |
| 4 | **CUI Marking and Handling** | 32 CFR Part 2002 and NIST SP 800-171 mandate that CUI is marked, encrypted at rest and in transit, access-controlled, and audit-logged. See `references/cui-handling.md`. |
| 5 | **Audit Completeness** | AU-2 through AU-12 require that every security-relevant event is captured with who, what, when, where, and outcome. Catch blocks without logging are federal audit failures. |
| 6 | **Boundary Protection** | SC-7 requires monitoring and controlling communications at system boundaries. Network zone awareness and segmentation must be enforced in code. |
| 7 | **Incident Response Readiness** | DOE incident categories (CAT 1-4) have reporting deadlines from 1 hour to 1 week. Applications must support detection, categorization, and notification. See `references/doe-cybersecurity.md`. |
| 8 | **Configuration Management** | CM-6 and CM-7 require approved baselines. No developer overrides in production, no debug endpoints, no default credentials. |
| 9 | **Access Control Granularity** | AC-3 demands resource-level authorization checks, not just endpoint-level. IDOR prevention is a federal requirement, not just a best practice. |
| 10 | **Supply Chain Risk Management** | EO 14028 and RA-5 require SBOM capability, approved package sources, and dependency vulnerability scanning. Every NuGet package is a supply chain decision. |

---

## Workflow

This skill follows a six-phase workflow. Each phase builds on the previous one.
Do not skip phases or reorder them.

### Phase 1: BASE-REVIEW

Execute the full `dotnet-security-review` skill process before applying any
federal overlays.

**Actions:**
- Run reconnaissance (framework version, application type, solution structure)
- Execute the complete OWASP Top 10 scan (A01 through A10)
- Run Telerik UI components scan if applicable
- Run jQuery/JavaScript XSS scan
- Run SQL Server stored procedure scan
- Run FluentValidation scan
- Run logging security scan (Serilog/NLog)

**Reference:** `../dotnet-security-review/SKILL.md` and its `references/` directory.

**Exit criteria:** All OWASP findings documented with severity and location.

### Phase 2: NIST-MAP

Map all base findings to NIST SP 800-53 Rev 5 controls and assess additional
NIST control families.

**Actions:**
- Determine system impact level (Low / Moderate / High) based on data types
- Map each OWASP finding to its primary NIST control (see `references/nist-800-53-mapping.md`)
- Assess Access Control (AC) family: AC-2, AC-3, AC-6, AC-7, AC-11, AC-17
- Assess Audit and Accountability (AU) family: AU-2, AU-3, AU-6, AU-9, AU-12
- Assess Identification and Authentication (IA) family: IA-2, IA-2(1), IA-5, IA-5(1), IA-8
- Assess System and Communications Protection (SC) family: SC-8, SC-12, SC-13, SC-28

**Search patterns for impact level determination:**
```bash
# Check for indicators of data classification
grep -rn "CUI\|FOUO\|Controlled\|Classified\|UCNI\|OUO" --include="*.md" --include="*.txt" --include="*.cs"

# Check for PII/PHI handling
grep -rn "SSN\|SocialSecurity\|DateOfBirth\|HealthRecord\|HIPAA" --include="*.cs"

# Check for financial data
grep -rn "CreditCard\|BankAccount\|RoutingNumber" --include="*.cs"
```

**Impact level table:**

| Data Types Present | Likely Impact Level |
|-------------------|---------------------|
| Public data only | Low |
| PII, business sensitive | Moderate |
| CUI, UCNI, mission-critical | High |

**NIST control search patterns:** See `references/nist-800-53-mapping.md` for
complete search patterns and .NET implementation examples for each control.
Key patterns for quick reference:

```bash
# Access Control family (AC-2 through AC-17)
grep -rn "\[Authorize\]\|\[AllowAnonymous\]" --include="*.cs"
grep -rn "Lockout\|MaxFailedAccessAttempts\|ExpireTimeSpan" --include="*.cs"

# Audit family (AU-2 through AU-12)
grep -rn "ILogger\|AuditLog\|SecurityEvent" --include="*.cs"

# Identification and Authentication family (IA-2 through IA-8)
grep -rn "AddAuthentication\|TwoFactor\|MFA\|PasswordOptions" --include="*.cs"

# System and Communications Protection family (SC-8 through SC-28)
grep -rn "UseHttps\|UseHsts\|Encrypt\|DataProtection" --include="*.cs"
grep -rn "MD5\|SHA1\|DES\|3DES\|RC4" --include="*.cs"
```

**Exit criteria:** Every base finding has a NIST control mapping. NIST control families assessed with status for each control.

### Phase 3: FIPS-AUDIT

Audit all cryptographic usage against FIPS 140-2/3 requirements.

**Actions:**
- Identify all cryptographic algorithm usage in the codebase
- Flag every non-FIPS algorithm (MD5, SHA-1, DES, 3DES, RC2, RC4, Rijndael)
- Verify key sizes meet minimums (AES-128+, RSA-2048+, ECDSA P-256+)
- Confirm random number generation uses RandomNumberGenerator, not System.Random
- Check TLS configuration for 1.2+ enforcement
- Verify FIPS mode awareness in the application

**Search patterns:**
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

**Reference:** `references/fips-crypto-requirements.md` for approved/non-approved algorithm tables and compliant .NET implementations.

**Exit criteria:** Complete inventory of cryptographic usage with FIPS compliance status for each instance.

### Phase 4: CUI-CHECK

Assess Controlled Unclassified Information handling throughout the application.

**Actions:**
- Search for CUI markers in code, comments, configuration, and documentation
- Verify CUI data is encrypted at rest using FIPS-validated algorithms
- Verify CUI is encrypted in transit (TLS 1.2+)
- Check that CUI access is behind proper authorization policies
- Verify CUI access is audit-logged with complete records
- Assess export, download, print, and email functionality for CUI controls
- Check for CUI marking in UI banners, exports, and printed output

**Search patterns:**
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

**Reference:** `references/cui-handling.md` for CUI categories, marking formats, NIST SP 800-171 requirements, and .NET implementation patterns.

**Exit criteria:** CUI presence determined. If CUI is present, all handling requirements assessed with compliance status.

### Phase 5: DOE-OVERLAY

Apply DOE-specific requirements that exceed standard NIST baselines.

**Actions:**
- Verify DOE-specific authentication parameters (15+ char passwords, 3 attempt lockout)
- Verify DOE session timeout requirements (15 min Moderate, 10 min High)
- Assess DOE audit requirements (3-year retention, comprehensive event coverage)
- Check network zone awareness (Yellow/Green/Turquoise/Red for LANL)
- Verify privileged access management with separation of duties
- Check for DOE incident response integration (CAT 1-4 categorization)
- Assess secure SDLC compliance (threat modeling, SAST/DAST, hardened configs)
- Verify configuration management controls (no dev overrides in production)

**Search patterns:**
```bash
# Check for DOE-specific patterns
grep -rn "NNSA\|DOE\|LANL\|Laboratory" --include="*.cs" --include="*.config" --include="*.md"

# Privileged access management
grep -rn "ServiceAccount\|SystemAccount\|Impersonate" --include="*.cs"

# Network segmentation indicators
grep -rn "DMZ\|Firewall\|NetworkZone\|Enclave" --include="*.cs" --include="*.config"

# Authentication strength
grep -rn "RequiredLength\|MaxFailedAccessAttempts" --include="*.cs"

# Session management
grep -rn "ExpireTimeSpan\|SessionTimeout" --include="*.cs"

# Separation of duties
grep -rn "SelfApproval\|SeparationOfDuties\|Approve.*Own" --include="*.cs"
```

**Reference:** `references/doe-cybersecurity.md` for DOE Order 205.1B, LANL network zones, privileged access, and incident response requirements.

**Exit criteria:** All DOE-specific parameters verified against DOE Order 205.1B thresholds. LANL-specific controls assessed if applicable.

### Phase 6: POA&M-GENERATE

Generate the complete federal security assessment report with POA&M entries.

**Actions:**
- Write the federal executive summary using language from `references/federal-executive-templates.md`
- Compile the NIST SP 800-53 control assessment matrix
- Compile the FIPS audit results table
- Compile the CUI handling assessment table
- Compile the OWASP-to-NIST cross-reference table
- Generate detailed findings in P1/P2/P3/P4 priority order
- Generate POA&M entries for every finding
- Compile the compliance summary across all frameworks
- List positive findings to provide balanced assessment
- Write recommendations by timeline (immediate, 30-day, 90-day, continuous)

**Reference:** `references/federal-executive-templates.md` for posture statements, impact level explanations, finding templates, and POA&M entry format.

**Exit criteria:** Complete federal security assessment report ready for authorizing official review.

---

## State Block

Track review progress using this state block. Update it after each phase
transition.

```xml
<federal-security-state>
  <mode>BASE-REVIEW|NIST-MAP|FIPS-AUDIT|CUI-CHECK|DOE-OVERLAY|POA&M-GENERATE</mode>
  <impact_level>UNKNOWN|LOW|MODERATE|HIGH</impact_level>
  <nist_controls_checked>0/23</nist_controls_checked>
  <fips_compliant>UNKNOWN|YES|NO|PARTIAL</fips_compliant>
  <cui_present>UNKNOWN|YES|NO</cui_present>
  <doe_overlay_applied>false</doe_overlay_applied>
  <poam_items>0</poam_items>
  <last_action>none</last_action>
  <next_action>Execute base dotnet-security-review skill</next_action>
</federal-security-state>
```

**Field definitions:**
- `mode` -- Current workflow phase
- `impact_level` -- FIPS 199 categorization once determined
- `nist_controls_checked` -- Progress through the 23 assessed controls (AC: 6, AU: 5, IA: 5, SC: 4, plus SI, CM, RA)
- `fips_compliant` -- Overall FIPS cryptographic compliance status
- `cui_present` -- Whether CUI was detected in the application
- `doe_overlay_applied` -- Whether DOE-specific parameters have been verified
- `poam_items` -- Running count of POA&M entries generated
- `last_action` / `next_action` -- Breadcrumb trail for review continuity

---

## Output Templates

### Federal Executive Summary

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

**Example**: "This Moderate-impact system has an adequate security posture with
identified gaps in NIST SP 800-53 controls. We identified 15 findings:
1 High (P1), 4 Moderate (P2), and 10 Low (P3). Critical gaps exist in SC-13
(FIPS cryptography) and AU-2 (audit events). Recommend immediate POA&M entry
for P1 items with 30-day remediation target."

### Security Posture: [Critical Gap / Significant Gaps / Minor Gaps / Compliant]

| Priority | Count | NIST Impact | Remediation Window |
|----------|-------|-------------|-------------------|
| P1 (Critical) | X | High | Immediate (24-48 hrs) |
| P2 (High) | X | Moderate | 30 days |
| P3 (Medium) | X | Low | 90 days |
| P4 (Low) | X | Minimal | 180 days / Backlog |
```

Use posture statement templates from `references/federal-executive-templates.md`.

### NIST Control Compliance Matrix

```markdown
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
```

### FIPS Audit Results

```markdown
## FIPS 140-2/3 Cryptographic Compliance

| Requirement | Status | Finding |
|-------------|--------|---------|
| FIPS-approved algorithms only | Compliant/Non-compliant | [List non-compliant: MD5, SHA1, etc.] |
| Minimum key sizes (AES-128+, RSA-2048+) | | |
| Approved RNG (RNGCryptoServiceProvider) | | |
| TLS 1.2+ for transmission | | |
| FIPS mode awareness | | |
| Password hashing (PBKDF2-SHA256) | | |
```

### CUI Handling Assessment

```markdown
## CUI Handling Assessment

| Requirement | Status | Finding |
|-------------|--------|---------|
| CUI marking capability | | |
| Access controls for CUI | | |
| MFA required for CUI access | | |
| Audit logging for CUI access | | |
| Encryption at rest (AES-256) | | |
| Encryption in transit (TLS 1.2+) | | |
| Export controls | | |
| Print controls | | |
| Email controls | | |
| Destruction tracking | | |
```

### POA&M Entries

```markdown
## POA&M Summary

| ID | Finding | Control | Priority | Target Date | Status |
|----|---------|---------|----------|-------------|--------|
| 1 | [Title] | [NIST] | P1 | [Date] | Open |
| 2 | | | | | |

## POA&M Entry Detail

**Weakness ID**: [Unique ID]
**Finding**: [Brief title]
**NIST Control**: [Control ID - Control Name]
**Priority**: [P1/P2/P3/P4]
**Status**: Open

**Description**: [Detailed description]
**Risk Statement**: [Impact if not remediated]
**Recommended Remediation**: [Specific steps]
**Milestone Schedule**: [Implementation timeline]
**Resources Required**: [Developer hours, security review, testing]
```

---

## Priority Classification (Federal)

### P1 -- Critical (Immediate, 24-48 hours)
- Active exploitation possible
- Authentication bypass
- Remote code execution
- SQL injection with data access
- Non-compliant crypto on CUI/PII (FIPS violation)
- Missing MFA on privileged accounts
- Hardcoded credentials for federal systems
- Audit logging disabled

### P2 -- High (30 Days)
- Authorization flaws (IDOR)
- Sensitive data exposure
- Missing encryption at rest for PII
- Session management weaknesses
- Insufficient audit logging
- Non-FIPS algorithms on non-sensitive data
- Missing account lockout

### P3 -- Medium (90 Days)
- Verbose error messages
- Missing input validation
- CORS misconfiguration
- Weak password policy (below NIST guidelines)
- Incomplete audit trails
- Missing security headers

### P4 -- Low (Backlog)
- Defense-in-depth opportunities
- Best practice deviations
- Documentation gaps
- Minor hardening items

---

## OWASP to NIST Cross-Reference

| OWASP Category | Primary NIST Controls | Federal Implication |
|---------------|----------------------|---------------------|
| A01: Broken Access Control | AC-3, AC-6 | ATO risk if resource-level checks missing |
| A02: Cryptographic Failures | SC-12, SC-13, SC-28 | FIPS violation, CUI exposure |
| A03: Injection | SI-10 | Data integrity compromise |
| A04: Insecure Design | SA-8 | Secure SDLC noncompliance |
| A05: Security Misconfiguration | CM-6, CM-7 | Configuration management failure |
| A06: Vulnerable Components | SI-2, RA-5 | Supply chain risk (EO 14028) |
| A07: Authentication Failures | IA-2, IA-5 | Identity compromise, unauthorized access |
| A08: Data Integrity Failures | SI-7 | Data tampering, audit integrity |
| A09: Logging Failures | AU-2, AU-3, AU-12 | Incident detection failure |
| A10: SSRF | SC-7 | Boundary protection bypass |

---

## Supply Chain Security (EO 14028)

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

## Manager-Friendly Federal Language

See `references/federal-executive-templates.md` for complete templates.

**Instead of**: "SQL injection vulnerability via unsanitized input"

**Write**: "A vulnerability exists that could allow unauthorized access to
database records containing [PII/CUI/mission data]. This finding impacts NIST
control SI-10 (Information Input Validation) and could result in a data breach
requiring notification under DOE Order 206.1."

---

## AI Discipline Rules

These rules are non-negotiable. Violating any CRITICAL rule invalidates the
entire review.

| # | Rule | Severity |
|---|------|----------|
| 1 | **Always execute the base `dotnet-security-review` skill first.** Federal overlays without an OWASP foundation are incomplete and misleading. Never skip the base review to save time. | CRITICAL |
| 2 | **Never approve non-FIPS cryptography in federal systems.** MD5, SHA-1, DES, 3DES, RC4, Rijndael, and System.Random are always findings. There are no exceptions for "internal use" or "non-sensitive data" in federal environments. | CRITICAL |
| 3 | **Always check for CUI presence and handling.** Even if the application appears to handle only public data, verify. CUI can appear in comments, test data, configuration files, logs, and error messages. | CRITICAL |
| 4 | **Always verify DOE-specific parameters, not just NIST baselines.** DOE Order 205.1B sets thresholds that exceed NIST minimums (15-char passwords, 3-attempt lockout, 10-15 min sessions). Passing NIST baseline does not mean passing DOE. | CRITICAL |
| 5 | **Use federal compliance language in all reports.** Findings must reference NIST control IDs, use POA&M terminology, state business impact in mission terms, and be comprehensible to authorizing officials. Never write raw technical jargon without federal context. | CRITICAL |
| 6 | **Generate a POA&M entry for every finding.** Findings without POA&M entries do not exist in the federal compliance process. Every gap, regardless of severity, gets a tracking artifact. | REQUIRED |
| 7 | **Map every finding to at least one NIST control.** Unmapped findings cannot be traced to control baselines and are invisible to the authorization process. | REQUIRED |
| 8 | **Always document positive findings.** Federal reports require balanced assessments. List security controls properly implemented to acknowledge good practices and provide context for gaps. | REQUIRED |

---

## Anti-Patterns

| # | Anti-Pattern | Why It Fails | Correct Approach |
|---|-------------|--------------|------------------|
| 1 | Skipping the base review and jumping to federal overlays | Federal controls assume a secure technical foundation. Without OWASP coverage, critical injection, XSS, and auth flaws go undetected. | Always complete Phase 1 (BASE-REVIEW) first. |
| 2 | Approving SHA-1 or MD5 in any federal context | "It's only used for checksums" is not a valid federal excuse. FIPS 140-2/3 prohibits these algorithms. Auditors will flag them regardless of use case. | Replace with SHA-256+ in all cases. See `references/fips-crypto-requirements.md`. |
| 3 | Ignoring CUI in test data or seed files | Test databases with real CUI/PII are compliance violations. CUI handling requirements apply to all instances, not just production. | Verify test data is synthetic. Flag real CUI in any environment. |
| 4 | Treating NIST controls as a checkbox exercise | Marking AC-3 "Implemented" because `[Authorize]` exists on one controller, while 40 other endpoints are anonymous, is a false assessment. | Assess each control thoroughly with evidence-based status. Partial is a valid status. |
| 5 | Missing DOE-specific parameters | Reporting password requirements as "adequate" when they meet NIST (8-char) but not DOE (15-char) baselines. | Always verify against DOE Order 205.1B thresholds from `references/doe-cybersecurity.md`. |
| 6 | Generating findings without POA&M entries | Findings that do not appear in the POA&M are invisible to the authorization process and will not be tracked or resourced. | Every finding gets a POA&M entry with ID, control, priority, and target date. |
| 7 | Writing purely technical reports | "XSS in SearchController.cs line 47" is meaningless to an authorizing official. Federal reports must communicate risk in mission terms. | Use templates from `references/federal-executive-templates.md`. |
| 8 | Applying federal overlays to non-federal systems | Not every .NET application needs FIPS cryptography and CUI handling. Applying federal overlays where they do not apply wastes effort and creates confusion. | Confirm the system is federal (DOE/DOD/LANL) before applying this skill. Use the base `dotnet-security-review` for non-federal systems. |
| 9 | Assuming Moderate impact without evidence | Defaulting to Moderate because "most LANL systems are Moderate" without actually assessing data types and mission impact. | Run the impact level determination in Phase 2 with evidence from grep patterns. |
| 10 | Reporting Argon2/bcrypt as compliant password hashing | Argon2 and bcrypt are OWASP-recommended but are NOT FIPS-validated. Federal systems must use PBKDF2 with HMAC-SHA256. | Flag Argon2/bcrypt as FIPS non-compliant. Recommend PBKDF2-SHA256 with 600K+ iterations. |

---

## Error Recovery

### Scenario 1: Impact Level Unknown

**Situation:** The application handles ambiguous data types. You cannot
definitively determine whether the system is Low, Moderate, or High impact.

**Recovery steps:**
1. Document what data types were identified and what remains unclear
2. Default to **Moderate** as a conservative assumption (most DOE internal systems are Moderate)
3. Explicitly state in the report: "Impact level assumed Moderate pending formal FIPS 199 categorization by the system owner"
4. Flag impact level determination as a P3 POA&M item requiring system owner confirmation
5. Apply Moderate-baseline controls throughout the review

### Scenario 2: Mixed Federal and Non-Federal Components

**Situation:** The solution contains both federal-facing components (e.g., an
internal DOE portal) and non-federal components (e.g., a public informational
website) in the same codebase.

**Recovery steps:**
1. Identify the boundary between federal and non-federal components
2. Apply federal overlays only to federal-facing components
3. Apply the base `dotnet-security-review` to non-federal components
4. Document the boundary clearly: which projects, namespaces, or modules are in scope for federal review
5. Flag shared libraries that serve both contexts -- these must meet the higher (federal) standard
6. Note that shared authentication, logging, and data access layers must comply with the strictest requirements

### Scenario 3: FIPS Non-Compliant Library with No Alternative

**Situation:** The application depends on a third-party library that uses
non-FIPS algorithms internally (e.g., a legacy reporting library using MD5 for
internal checksums), and no FIPS-compliant alternative exists.

**Recovery steps:**
1. Document the specific library, its non-compliant algorithm usage, and the business function it serves
2. Assess whether the non-compliant usage touches CUI/PII or security-critical paths
3. Generate a P2 POA&M entry with the following mitigation plan:
   - Short-term: Document the risk acceptance with justification
   - Medium-term: Evaluate alternative libraries or wrapper approaches
   - Long-term: Replace the library when a compliant alternative becomes available
4. Note in the report that this requires risk acceptance by the Authorizing Official
5. Recommend compensating controls (e.g., additional boundary protections, monitoring)

### Scenario 4: CUI Found in Logs or Error Messages

**Situation:** During the review, you discover CUI markers, PII, or sensitive
data appearing in application logs, error messages, or diagnostic output.

**Recovery steps:**
1. Immediately classify this as a **P1 finding** -- CUI exposure in logs is an active compliance violation
2. Document the specific log entries, locations, and data types exposed
3. Map to NIST controls: AU-9 (Protection of Audit Information), SC-28 (Protection at Rest), and applicable CUI controls from NIST SP 800-171
4. Recommend immediate remediation: implement structured logging that excludes sensitive fields, add PII/CUI scrubbing to log pipelines
5. Flag for DOE incident review -- CUI exposure may trigger incident reporting requirements per DOE Order 205.1B

---

## Integration with Other Skills

### Prerequisite: dotnet-security-review

This skill **requires** the base `dotnet-security-review` as a prerequisite.
The base skill provides OWASP Top 10 coverage, Telerik component scanning,
jQuery XSS analysis, SQL Server stored procedure review, FluentValidation
assessment, and logging security scanning. Federal overlays build upon these
results.

**Reference:** `../dotnet-security-review/SKILL.md`

### Recommended: supply-chain-audit

For comprehensive EO 14028 compliance, run a supply chain audit on all NuGet
dependencies. This verifies that package sources are approved, dependencies are
pinned to specific versions, known vulnerabilities are patched, and SBOM
generation capability exists. Supply chain findings feed into the RA-5 and SI-2
control assessments in Phase 2.

### Recommended: architecture-review

For High-impact systems or systems with complex boundary requirements, an
architecture review provides system boundary analysis, data flow mapping, and
network zone verification. This feeds into SC-7 (Boundary Protection) and
AC-17 (Remote Access) control assessments and helps identify where federal
controls must be enforced versus where they are inherited from infrastructure.

---

## References

- `references/nist-800-53-mapping.md` -- NIST control to OWASP mapping
- `references/doe-cybersecurity.md` -- DOE Order 205.1B requirements
- `references/fips-crypto-requirements.md` -- FIPS 140-2/3 compliance
- `references/cui-handling.md` -- CUI handling in .NET applications
- `references/federal-executive-templates.md` -- Federal report language
- `../dotnet-security-review/references/` -- Base OWASP and .NET references
- NIST SP 800-53 Rev 5: https://csrc.nist.gov/publications/detail/sp/800-53/rev-5/final
- FIPS 140-3: https://csrc.nist.gov/publications/detail/fips/140/3/final
- DOE Order 205.1B: https://www.directives.doe.gov/directives-documents/200-series/0205.1-BOrder-b
- OWASP Top 10 2021: https://owasp.org/Top10/
- 32 CFR Part 2002 (CUI): https://www.ecfr.gov/current/title-32/subtitle-B/chapter-XX/part-2002
- NIST SP 800-171 Rev 2: https://csrc.nist.gov/publications/detail/sp/800-171/rev-2/final
