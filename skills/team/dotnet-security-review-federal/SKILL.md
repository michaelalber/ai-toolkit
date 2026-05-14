---
name: dotnet-security-review-federal
description: >
  Conducts security reviews of .NET applications for federal/DOE/DOD environments.
  Extends the base dotnet-security-review with NIST SP 800-53 control mapping,
  DOE Order 205.1B compliance, FIPS 140-2/3 cryptographic requirements, and CUI
  handling. Generates federal-compliant reports with impact levels and POA&M-ready
  findings. Trigger phrases: "federal security review", "NIST compliance",
  "DOE security", "FISMA", "CUI", "FIPS audit", "federal compliance",
  "federal agency security", "ATO review", "POA&M generation".
---

# .NET Security Review -- Federal Edition

> "Security is not a product, but a process."
> -- Bruce Schneier

> "Compliance is the floor, not the ceiling."
> -- NIST Cybersecurity Framework guidance

## Core Philosophy

This skill provides a **federal compliance overlay** on top of the base `dotnet-security-review` skill. It extends it with the regulatory, policy, and procedural requirements specific to U.S. federal systems, particularly DOE and national laboratory environments.

**Foundational principles:**

1. **Base review first, always.** Execute the full `dotnet-security-review` skill before applying any federal overlays. OWASP Top 10 coverage is a prerequisite.
2. **NIST SP 800-53 Rev 5 is the framework.** All findings, controls, and recommendations map back to NIST control families.
3. **Compliance is not optional.** Federal systems operate under legal mandates (FISMA, FIPS, EO 14028). Gaps can revoke an ATO.
4. **DOE-specific requirements exceed baselines.** DOE Order 205.1B and NNSA NAP 70.4 impose thresholds that exceed NIST minimums — password lengths, lockout, session timeouts, audit retention. Reference `references/doe-cybersecurity.md`.
5. **POA&M-driven remediation.** Every finding produces a Plan of Action and Milestones entry. Findings without POA&M entries are invisible to the authorization process.
6. **Defense-in-depth for government systems.** Federal systems face nation-state adversaries. A single control failure must not lead to compromise.

## Domain Principles

| # | Principle | Rationale |
|---|-----------|-----------|
| 1 | **Continuous Monitoring** | Federal systems require ongoing assessment per NIST SP 800-137, not point-in-time reviews. |
| 2 | **Least Privilege Enforcement** | AC-6 demands minimum necessary access. Broad "Admin" roles, sa database accounts, and blanket AllowAnonymous are federal compliance failures. |
| 3 | **FIPS-Validated Cryptography** | SC-13 requires FIPS 140-2/3 validated modules. MD5, SHA-1, DES, 3DES, RC4, and System.Random are never acceptable. See `references/fips-crypto-requirements.md`. |
| 4 | **CUI Marking and Handling** | 32 CFR Part 2002 and NIST SP 800-171 mandate CUI is marked, encrypted at rest and in transit, access-controlled, and audit-logged. See `references/cui-handling.md`. |
| 5 | **Audit Completeness** | AU-2 through AU-12 require every security-relevant event is captured with who, what, when, where, and outcome. Catch blocks without logging are federal audit failures. |
| 6 | **Boundary Protection** | SC-7 requires monitoring communications at system boundaries. Network zone awareness must be enforced in code. |
| 7 | **Incident Response Readiness** | DOE incident categories (CAT 1-4) have reporting deadlines from 1 hour to 1 week. Applications must support detection, categorization, and notification. See `references/doe-cybersecurity.md`. |
| 8 | **Configuration Management** | CM-6 and CM-7 require approved baselines. No developer overrides in production, no debug endpoints, no default credentials. |
| 9 | **Access Control Granularity** | AC-3 demands resource-level authorization checks, not just endpoint-level. IDOR prevention is a federal requirement. |
| 10 | **Supply Chain Risk Management** | EO 14028 and RA-5 require SBOM capability, approved package sources, and dependency vulnerability scanning. |

## Knowledge Base Lookups

| Query | When to Call |
|-------|--------------|
| `search_knowledge("NIST SP 800-53 controls access control audit accountability")` | At NIST-MAP phase — load authoritative control families (AC, AU, IA, SC) |
| `search_knowledge("FIPS 140-2 validated cryptography .NET AES SHA-256")` | During FIPS-CRYPTO phase — confirms compliant vs. non-compliant algorithm use in .NET |
| `search_knowledge("CUI handling marking encryption access control federal")` | During CUI-CHECK phase |
| `search_knowledge("FISMA FedRAMP ATO authorization operate federal system")` | When producing POA&M entries |
| `search_knowledge("DOE cybersecurity order 205.1B NNSA incident response")` | During DOE-OVERLAY phase |
| `search_knowledge("OWASP injection broken access control .NET ASP.NET Core")` | At BASE-REVIEW phase |

Search at the start of each phase. Federal findings MUST cite the NIST control and DOE policy source.

## Workflow

Six-phase workflow. Do not skip phases or reorder them.

### Phase 1: BASE-REVIEW

Execute the full `dotnet-security-review` skill first.

**Actions:** Reconnaissance (framework version, app type, solution structure) → OWASP Top 10 scan (A01–A10) → Telerik UI component scan → jQuery/JavaScript XSS → SQL Server stored procedure scan → FluentValidation scan → logging security scan.

**Reference:** `../dotnet-security-review/SKILL.md`

**Exit criteria:** All OWASP findings documented with severity and location.

### Phase 2: NIST-MAP

Map all base findings to NIST SP 800-53 Rev 5 controls. Determine system impact level.

**Impact level:**

| Data Types Present | Likely Impact Level |
|-------------------|---------------------|
| Public data only | Low |
| PII, business sensitive | Moderate |
| CUI, UCNI, mission-critical | High |

```bash
# Impact level detection
grep -rn "CUI\|FOUO\|Controlled\|Classified\|UCNI" --include="*.md" --include="*.cs"
grep -rn "SSN\|SocialSecurity\|DateOfBirth\|HealthRecord" --include="*.cs"
grep -rn "CreditCard\|BankAccount\|RoutingNumber" --include="*.cs"

# Access Control (AC-2 through AC-17)
grep -rn "\[Authorize\]\|\[AllowAnonymous\]" --include="*.cs"
grep -rn "Lockout\|MaxFailedAccessAttempts\|ExpireTimeSpan" --include="*.cs"

# Audit (AU-2 through AU-12)
grep -rn "ILogger\|AuditLog\|SecurityEvent" --include="*.cs"

# Identification and Authentication (IA-2 through IA-8)
grep -rn "AddAuthentication\|TwoFactor\|MFA\|PasswordOptions" --include="*.cs"

# Communications Protection (SC-8 through SC-28)
grep -rn "UseHttps\|UseHsts\|Encrypt\|DataProtection" --include="*.cs"
grep -rn "MD5\|SHA1\|DES\|3DES\|RC4" --include="*.cs"
```

**Reference:** `references/nist-800-53-mapping.md` for complete control search patterns.

**Exit criteria:** Every base finding has a NIST control mapping. All AC/AU/IA/SC controls assessed.

### Phase 3: FIPS-AUDIT

Audit all cryptographic usage against FIPS 140-2/3 requirements.

```bash
# FIPS-compliant
grep -rn "Aes\|RSACryptoServiceProvider\|ECDsa\|SHA256\|SHA384\|SHA512" --include="*.cs"

# NON-compliant (findings)
grep -rn "MD5\|SHA1\|DES\|TripleDES\|RC2\|RC4\|Rijndael" --include="*.cs"

# Random number generation (System.Random is non-compliant)
grep -rn "new Random\|Random()\|RandomNumberGenerator" --include="*.cs"
```

**Actions:** Flag every non-FIPS algorithm. Verify key sizes (AES-128+, RSA-2048+, ECDSA P-256+). Confirm TLS 1.2+ enforcement. Check FIPS mode awareness.

**Reference:** `references/fips-crypto-requirements.md` for approved/non-approved algorithm tables.

**Exit criteria:** Complete cryptographic inventory with FIPS compliance status for each instance.

### Phase 4: CUI-CHECK

Assess Controlled Unclassified Information handling throughout the application.

```bash
grep -rn "CUI\|Controlled Unclassified\|FOUO\|SBU\|LES" --include="*.cs" --include="*.md"
grep -rn "Classification\|DataCategory\|SensitivityLevel" --include="*.cs"
grep -rn "Download\|Export\|FileResult\|File(" --include="*.cs"
grep -rn "SmtpClient\|SendGrid\|MailMessage\|EmailService" --include="*.cs"
```

**Actions:** Verify CUI encrypted at rest and in transit. Check CUI behind authorization policies. Verify CUI access audit-logged. Assess export/download/print/email for CUI controls.

**Reference:** `references/cui-handling.md`

**Exit criteria:** CUI presence determined. If present, all handling requirements assessed.

### Phase 5: DOE-OVERLAY

Apply DOE-specific requirements that exceed standard NIST baselines.

**DOE-specific thresholds (DOE Order 205.1B):**
- Passwords: 15+ characters minimum
- Account lockout: 3 failed attempts
- Session timeout: 15 min (Moderate), 10 min (High)
- Audit retention: 3 years minimum

```bash
grep -rn "RequiredLength\|MaxFailedAccessAttempts" --include="*.cs"
grep -rn "ExpireTimeSpan\|SessionTimeout" --include="*.cs"
grep -rn "ServiceAccount\|SystemAccount\|Impersonate" --include="*.cs"
grep -rn "SelfApproval\|SeparationOfDuties" --include="*.cs"
```

**Reference:** `references/doe-cybersecurity.md`

**Exit criteria:** All DOE-specific parameters verified against DOE Order 205.1B thresholds.

### Phase 6: POA&M-GENERATE

Generate the complete federal security assessment report.

**Actions:** Federal executive summary → NIST SP 800-53 control assessment matrix → FIPS audit results → CUI handling assessment → OWASP-to-NIST cross-reference → detailed findings (P1/P2/P3/P4 order) → POA&M entries for every finding → compliance summary → positive findings → recommendations by timeline (immediate / 30-day / 90-day / continuous).

**Reference:** `references/federal-executive-templates.md` for posture statements, finding templates, and POA&M entry format.

**Exit criteria:** Complete federal security assessment report ready for authorizing official review.

## State Block

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

**Fields:** `mode` — current phase; `nist_controls_checked` — progress through 23 assessed controls (AC: 6, AU: 5, IA: 5, SC: 4, plus SI/CM/RA); `poam_items` — running count of POA&M entries.

## Output Templates

```markdown
# Security Assessment Report: [Solution Name]
**Classification**: [UNCLASSIFIED / CUI] | **Impact Level**: [Low / Moderate / High]
**Framework**: [.NET version] | **App Type**: [Web API / MVC / Blazor]

## Executive Summary
[3-4 sentences: overall posture vs NIST baseline, finding counts by severity, key compliance gaps, recommended POA&M timeline]

| Priority | Count | Remediation Window |
|----------|-------|--------------------|
| P1 Critical | X | Immediate (24-48 hrs) |
| P2 High | X | 30 days |
| P3 Medium | X | 90 days |
| P4 Low | X | Backlog |
```

Full templates for NIST control matrix, FIPS audit table, CUI assessment, and POA&M entries: `references/federal-executive-templates.md`.

## Priority Classification

| Priority | Timeframe | Examples |
|----------|-----------|---------|
| **P1 Critical** | 24-48 hrs | Authentication bypass, RCE, SQL injection with data access, non-compliant crypto on CUI/PII, missing MFA on privileged accounts, audit logging disabled |
| **P2 High** | 30 days | IDOR, sensitive data exposure, missing encryption at rest for PII, session management weaknesses, non-FIPS algorithms on non-sensitive data |
| **P3 Medium** | 90 days | Verbose error messages, missing input validation, CORS misconfiguration, weak password policy, missing security headers |
| **P4 Low** | Backlog | Defense-in-depth opportunities, best practice deviations, documentation gaps, minor hardening items |

## OWASP to NIST Cross-Reference

| OWASP Category | Primary NIST Controls | Federal Implication |
|---------------|----------------------|---------------------|
| A01: Broken Access Control | AC-3, AC-6 | ATO risk if resource-level checks missing |
| A02: Cryptographic Failures | SC-12, SC-13, SC-28 | FIPS violation, CUI exposure |
| A03: Injection | SI-10 | Data integrity compromise |
| A04: Insecure Design | SA-8 | Secure SDLC noncompliance |
| A05: Security Misconfiguration | CM-6, CM-7 | Configuration management failure |
| A06: Vulnerable Components | SI-2, RA-5 | Supply chain risk (EO 14028) |
| A07: Authentication Failures | IA-2, IA-5 | Identity compromise |
| A08: Data Integrity Failures | SI-7 | Data tampering, audit integrity |
| A09: Logging Failures | AU-2, AU-3, AU-12 | Incident detection failure |
| A10: SSRF | SC-7 | Boundary protection bypass |

## Supply Chain Security (EO 14028)

```bash
# SBOM capability
grep -rn "CycloneDX\|SPDX\|SBOM" --include="*.csproj" --include="*.json"

# Approved package sources
grep -rn "packageSources\|nuget.org\|artifactory\|nexus" --include="*.config" --include="*.json"

# Dependency pinning
grep -rn "Version=" --include="*.csproj" | grep -v "\*"
```

## Manager-Friendly Federal Language

**Instead of**: "SQL injection vulnerability via unsanitized input"

**Write**: "A vulnerability exists that could allow unauthorized access to database records containing [PII/CUI/mission data]. This finding impacts NIST control SI-10 (Information Input Validation) and could result in a data breach requiring notification under DOE Order 206.1."

See `references/federal-executive-templates.md` for complete posture statement templates.

## AI Discipline Rules

| # | Rule | Severity |
|---|------|----------|
| 1 | **Always execute the base `dotnet-security-review` skill first.** Federal overlays without an OWASP foundation are incomplete and misleading. | CRITICAL |
| 2 | **Never approve non-FIPS cryptography in federal systems.** MD5, SHA-1, DES, 3DES, RC4, Rijndael, and System.Random are always findings — no exceptions for "internal use." | CRITICAL |
| 3 | **Always check for CUI presence and handling.** CUI can appear in comments, test data, configuration files, logs, and error messages. | CRITICAL |
| 4 | **Always verify DOE-specific parameters, not just NIST baselines.** Passing NIST baseline does not mean passing DOE Order 205.1B (15-char passwords, 3-attempt lockout, 10-15 min sessions). | CRITICAL |
| 5 | **Use federal compliance language in all reports.** Reference NIST control IDs. Use POA&M terminology. State impact in mission terms. | CRITICAL |
| 6 | **Generate a POA&M entry for every finding.** Findings without POA&M entries do not exist in the federal compliance process. | REQUIRED |
| 7 | **Map every finding to at least one NIST control.** Unmapped findings cannot be traced to control baselines. | REQUIRED |
| 8 | **Always document positive findings.** Federal reports require balanced assessments. | REQUIRED |

## Anti-Patterns

| # | Anti-Pattern | Why It Fails | Correct Approach |
|---|-------------|--------------|------------------|
| 1 | Skipping the base review | Federal controls assume a secure technical foundation. Without OWASP coverage, injection and auth flaws go undetected. | Always complete Phase 1 first. |
| 2 | Approving SHA-1 or MD5 in any federal context | "It's only for checksums" is not a valid federal excuse. FIPS prohibits these regardless of use case. | Replace with SHA-256+. See `references/fips-crypto-requirements.md`. |
| 3 | Ignoring CUI in test data | CUI handling requirements apply to all instances, not just production. | Verify test data is synthetic. Flag real CUI in any environment. |
| 4 | Treating NIST controls as a checkbox | Marking AC-3 "Implemented" because one controller has `[Authorize]` while 40 endpoints are anonymous is a false assessment. | Assess each control thoroughly with evidence-based status. Partial is a valid status. |
| 5 | Missing DOE-specific parameters | Reporting passwords as "adequate" when they meet NIST (8-char) but not DOE (15-char) baselines. | Always verify against DOE Order 205.1B from `references/doe-cybersecurity.md`. |
| 6 | Generating findings without POA&M entries | Findings not in the POA&M will not be tracked or resourced. | Every finding gets a POA&M entry with ID, control, priority, and target date. |
| 7 | Writing purely technical reports | "XSS in SearchController.cs line 47" is meaningless to an authorizing official. | Use templates from `references/federal-executive-templates.md`. |
| 8 | Applying federal overlays to non-federal systems | Not every .NET app needs FIPS cryptography and CUI handling. | Confirm the system is federal before applying this skill. Use base `dotnet-security-review` otherwise. |
| 9 | Assuming Moderate impact without evidence | Defaulting to Moderate without assessing data types. | Run impact level determination in Phase 2 with evidence from grep patterns. |
| 10 | Reporting Argon2/bcrypt as compliant | Argon2 and bcrypt are OWASP-recommended but are NOT FIPS-validated. | Flag Argon2/bcrypt as FIPS non-compliant. Recommend PBKDF2-SHA256 with 600K+ iterations. |

## Error Recovery

### Impact Level Unknown

Default to **Moderate** as a conservative assumption. State in the report: "Impact level assumed Moderate pending formal FIPS 199 categorization by the system owner." Flag impact level determination as a P3 POA&M item requiring system owner confirmation.

### Mixed Federal and Non-Federal Components

Identify the boundary between federal and non-federal components. Apply federal overlays only to federal-facing components. Shared libraries that serve both contexts must meet the higher (federal) standard.

### FIPS Non-Compliant Library with No Alternative

Document the specific library, its non-compliant algorithm usage, and the business function. Assess whether it touches CUI/PII. Generate a P2 POA&M entry with short-term risk acceptance justification, medium-term alternative evaluation, and long-term replacement plan. This requires risk acceptance by the Authorizing Official.

### CUI Found in Logs or Error Messages

Immediately classify as a **P1 finding**. Document specific log entries, locations, and data types exposed. Map to AU-9, SC-28, and applicable CUI controls from NIST SP 800-171. Flag for DOE incident review — CUI exposure may trigger incident reporting per DOE Order 205.1B.

## Integration with Other Skills

- **`dotnet-security-review`** (prerequisite) — Provides OWASP Top 10 coverage, Telerik scanning, jQuery XSS, SQL Server procedures, FluentValidation, and logging security. Federal overlays build on these results.
- **`supply-chain-audit`** — For comprehensive EO 14028 compliance. Verifies approved package sources, pinned versions, known vulnerabilities, and SBOM generation. Feeds RA-5 and SI-2 in Phase 2.
- **`architecture-review`** — For High-impact systems with complex boundary requirements. Provides system boundary analysis and data flow mapping for SC-7 and AC-17 control assessments.

## References

- `references/nist-800-53-mapping.md` — NIST control to OWASP mapping
- `references/doe-cybersecurity.md` — DOE Order 205.1B requirements
- `references/fips-crypto-requirements.md` — FIPS 140-2/3 compliance
- `references/cui-handling.md` — CUI handling in .NET applications
- `references/federal-executive-templates.md` — Federal report language
- `../dotnet-security-review/references/` — Base OWASP and .NET references
