---
name: dotnet-security-review
description: Conducts OWASP-based security reviews of .NET and .NET Framework applications with Telerik UI specialization. Identifies vulnerabilities, insecure patterns, and compliance gaps across all OWASP Top 10 categories. Generates manager-friendly reports with risk explanations and remediation priorities. Use when asked to review security, audit code for vulnerabilities, check OWASP compliance, assess security risks, find security issues, scan for CVEs, review Telerik security, or evaluate application security posture. Triggers on phrases like "security review", "OWASP audit", "vulnerability assessment", "security scan", "check for vulnerabilities", "security compliance", "Telerik security", "security posture", "penetration test prep".
---

# .NET Security Review (OWASP Baseline)

> "Security is not a product, but a process."
> -- Bruce Schneier, *Secrets and Lies*

> "The only truly secure system is one that is powered off, cast in a block of concrete, and sealed in a lead-lined room with armed guards."
> -- Gene Spafford

## Core Philosophy

Security is a first-class concern in every .NET application, not an afterthought bolted on before deployment. The OWASP Top 10 provides a proven baseline, but it is a floor, not a ceiling -- mature applications must go beyond the Top 10 to address domain-specific risks like Telerik component CVEs, logging hygiene, and stored procedure injection.

Telerik UI components deserve special attention because of their prevalence in enterprise .NET applications and their documented CVE history. The ASP.NET AJAX product line (RadAsyncUpload, RadEditor) has had multiple critical remote code execution vulnerabilities that were actively exploited in the wild. Failing to check Telerik versions and configuration is not an oversight -- it is a gap that adversaries specifically probe for.

At the same time, security reviews must balance thoroughness with developer productivity. Reporting dozens of low-severity findings without prioritization creates noise that obscures real risk. Every finding must be classified by severity with evidence, and every report must include positive findings that acknowledge good practices already in place.

Manager-friendly reporting is not optional. If a security review cannot be understood by the people who authorize remediation budgets and timelines, it will not result in action. Technical detail matters for developers; executive summaries matter for decision-makers. Both audiences must be served in every report. See `references/executive-summary-templates.md` for the language patterns that bridge technical findings and business impact.

## Domain Principles

| # | Principle | Description |
|---|-----------|-------------|
| 1 | **Defense in Depth** | Never rely on a single security control. Layer authentication, authorization, input validation, output encoding, and encryption so that failure of one layer does not compromise the system. |
| 2 | **Least Privilege** | Every component -- database accounts, service identities, API keys, user roles -- should operate with the minimum permissions required. An sa database connection or an admin-by-default role is a finding, not a convenience. |
| 3 | **Input Validation** | All external input is untrusted. Validate type, length, range, and format on the server side. Client-side validation is UX; server-side validation is security. See `references/owasp-top-10.md` for injection patterns. |
| 4 | **Output Encoding** | Encode all output based on its context (HTML, JavaScript, URL, SQL). Razor provides automatic encoding; `@Html.Raw()` and `MarkupString` bypass it and must be justified. |
| 5 | **Secure Defaults** | Applications should be secure out of the box. Debug mode off, HTTPS required, CORS restricted, authentication mandatory. Insecurity should require explicit opt-in, not the reverse. |
| 6 | **Fail Securely** | When errors occur, fail closed. Do not expose stack traces, connection strings, or internal paths. Catch exceptions, log them securely (see `references/dotnet-security-checklist.md`), and return safe error responses. |
| 7 | **Separation of Concerns** | Security logic should not be scattered across controllers and views. Centralize authorization policies, validation pipelines, and sanitization services. FluentValidation pipeline behaviors and ASP.NET Core policy-based authorization are the patterns to look for. |
| 8 | **Audit Trail** | Security-relevant events (logins, failures, privilege changes, data access) must be logged. But logs must never contain passwords, tokens, PII, or connection strings. The boundary between "enough logging" and "too much logging" is the most common misconfiguration. |
| 9 | **Dependency Awareness** | Every NuGet package, npm module, and JavaScript library is attack surface. Outdated components with known CVEs are the easiest entry point for adversaries. Defer to the `supply-chain-audit` skill for comprehensive dependency analysis. |
| 10 | **Telerik Component Security** | Telerik products span three distinct security profiles: Blazor (low CVE risk), ASP.NET MVC/Kendo (medium), and ASP.NET AJAX/RadControls (high -- multiple critical RCE CVEs). Always identify which product line is in use before assessing risk. See `references/telerik-security.md` for version-specific guidance. |

## Workflow

### Phase 1: RECONNAISSANCE

**Objective:** Determine the technology stack, hosting model, and attack surface before scanning.

**Steps:**

1. Find all project files and determine target framework (.NET 6+, .NET Framework 4.x, or mixed)
2. Identify application type: Web API, MVC, Blazor Server, Blazor WASM, WinForms, WPF, Console
3. Locate configuration files (appsettings.json, web.config, app.config)
4. Identify authentication mechanism (ASP.NET Core Identity, JWT, Windows Auth, custom)
5. Identify Telerik product line and version (Blazor, MVC/Kendo, or AJAX/RadControls)
6. Identify logging framework (Serilog, NLog, built-in ILogger)
7. Identify validation framework (DataAnnotations, FluentValidation, custom)

```bash
# Find all project files and determine framework
find . -name "*.csproj" -exec grep -l "TargetFramework" {} \;

# Check for web projects
find . -name "Startup.cs" -o -name "Program.cs" | head -10

# Find configuration files
find . -name "appsettings*.json" -o -name "web.config" -o -name "app.config"

# Identify authentication setup
grep -r "AddAuthentication\|AddAuthorization\|UseAuthentication" --include="*.cs" | head -20

# Identify Telerik product line
grep -rn "Telerik.UI.for.Blazor\|Kendo.Mvc\|Telerik.Web.UI" --include="*.csproj" --include="packages.config" --include="*.cs"
```

### Phase 2: SCAN

**Objective:** Run grep patterns for each OWASP Top 10 category plus domain-specific checks.

Use `references/owasp-top-10.md` for detailed patterns and code examples per category.

**OWASP Top 10 Quick Scan:**

```bash
# A01: Broken Access Control
grep -rn "AllowAnonymous\|\[Authorize\]\|Claims\|Policy" --include="*.cs"
grep -rn "User\.Identity\|User\.IsInRole" --include="*.cs"

# A02: Cryptographic Failures
grep -rn "MD5\|SHA1\|DES\|TripleDES\|RC2" --include="*.cs"
grep -rn "password.*=\|connectionString\|apiKey\|secret" --include="*.cs" --include="*.json" --include="*.config"

# A03: Injection
grep -rn "FromSqlRaw\|ExecuteSqlRaw\|SqlCommand\|OleDbCommand" --include="*.cs"
grep -rn "Process\.Start\|ProcessStartInfo" --include="*.cs"
grep -rn "innerHTML\|@Html\.Raw" --include="*.cs" --include="*.cshtml" --include="*.razor"

# A04: Insecure Design
grep -rn "TODO\|FIXME\|HACK\|BUG" --include="*.cs" | grep -i "security\|auth\|password\|token"

# A05: Security Misconfiguration
grep -rn "CORS\|AllowAnyOrigin\|AllowCredentials" --include="*.cs"
grep -rn "Debug.*true\|<compilation debug=\"true\"" --include="*.cs" --include="*.config" --include="*.json"

# A06: Vulnerable Components
# See supply-chain-audit skill (NuGet-specific review section)

# A07: Authentication Failures
grep -rn "PasswordSignInAsync\|SignInAsync\|ValidateCredentials" --include="*.cs"
grep -rn "lockout\|MaxFailedAccessAttempts" --include="*.cs"

# A08: Data Integrity Failures
grep -rn "Deserialize\|BinaryFormatter\|XmlSerializer\|JsonConvert" --include="*.cs"
grep -rn "TypeNameHandling" --include="*.cs"

# A09: Logging Failures
grep -rn "ILogger\|Log\.\|_logger\." --include="*.cs" | head -30
grep -rn "catch.*Exception" --include="*.cs" | head -20

# A09: Sensitive Data in Logs (Serilog/NLog)
grep -rn "Log.*password\|Log.*token\|Log.*apiKey\|Log.*connectionString" -i --include="*.cs"
grep -rn "_logger.*password\|_logger.*secret" -i --include="*.cs"

# A10: SSRF
grep -rn "HttpClient\|WebClient\|WebRequest\|HttpWebRequest" --include="*.cs"
grep -rn "new Uri\(.*\+\|Uri\.Parse" --include="*.cs"
```

**Telerik UI Components Scan (Critical):**

Telerik components have significant CVE history. Always check. See `references/telerik-security.md` for full guidance.

```bash
# Find Telerik references
grep -rn "Telerik\|RadAsyncUpload\|RadEditor\|RadGrid" --include="*.cs" --include="*.aspx" --include="*.ascx" --include="*.config"

# Check Telerik version in packages
grep -rn "Telerik" --include="*.csproj" --include="packages.config"

# RadAsyncUpload configuration (Critical CVEs)
grep -rn "RadAsyncUpload\|AsyncUpload" --include="*.aspx" --include="*.ascx" --include="*.cs"

# Telerik encryption keys (must be custom, not defaults)
grep -rn "ConfigurationEncryptionKey\|ConfigurationHashKey\|DialogParametersEncryptionKey" --include="*.config"

# Machine keys (required for Telerik security)
grep -rn "machineKey\|validationKey\|decryptionKey" --include="*.config"

# RadEditor dialogs (path traversal risk)
grep -rn "DialogHandler\|RadEditor" --include="*.config" --include="*.aspx"
```

**Known Critical CVEs:**
- CVE-2019-18935: RadAsyncUpload RCE (before 2020.1.114)
- CVE-2017-11317: RadAsyncUpload RCE (before 2017.2.621)
- CVE-2017-9248: Telerik.Web.UI crypto weakness (before 2017.2.621)
- CVE-2014-2217: RadEditor DialogHandler path traversal

**jQuery/JavaScript XSS Scan:**

```bash
# Dangerous jQuery patterns
grep -rn "\.html(\|\.append(\|\.prepend(" --include="*.js" --include="*.ts"

# Safe alternatives should use .text()
grep -rn "\.text(" --include="*.js" --include="*.ts"

# Dangerous dynamic code patterns
grep -rn "setTimeout.*\"" --include="*.js" --include="*.ts"

# URL parameter usage (potential DOM XSS)
grep -rn "location\.search\|location\.hash\|URLSearchParams" --include="*.js" --include="*.ts"

# AJAX without CSRF tokens
grep -rn "\$\.ajax\|\$\.post\|\$\.get" --include="*.js" --include="*.ts"

# innerHTML usage
grep -rn "innerHTML\|outerHTML" --include="*.js" --include="*.ts"
```

**SQL Server Stored Procedure Scan:**

```bash
# Find stored procedures with dynamic SQL
grep -rn "EXEC(\|EXECUTE(" --include="*.sql"

# Safe dynamic SQL should use sp_executesql
grep -rn "sp_executesql" --include="*.sql"

# QUOTENAME for dynamic object names
grep -rn "QUOTENAME" --include="*.sql"

# Connection strings - check for sa or elevated accounts
grep -rn "User Id=sa\|User=sa\|uid=sa" --include="*.config" --include="*.json" --include="*.cs"
```

**FluentValidation Scan:**

```bash
# Find validators
grep -rn "AbstractValidator\|IValidator" --include="*.cs"

# Check for string length validation
grep -rn "MaximumLength\|MinimumLength" --include="*.cs"

# Check for pattern validation (injection prevention)
grep -rn "Matches\|Must(" --include="*.cs"

# Commands/Requests without validators (potential gap)
grep -rn "class.*Command\s*:\|class.*Request\s*:" --include="*.cs" | grep -v "Validator"

# Check validator registration
grep -rn "AddValidatorsFromAssembly\|services\.AddScoped.*IValidator" --include="*.cs"
```

**Logging Security Scan (Serilog/NLog):**

```bash
# Serilog - Check for PII in logs
grep -rn "Log.*password\|Log.*Password\|Log.*ssn\|Log.*creditcard" -i --include="*.cs"
grep -rn "LogInformation.*\$\"\|LogDebug.*\$\"" --include="*.cs"

# NLog - Check for PII in logs
grep -rn "_logger.*password\|_logger.*Password\|\.Info.*password" -i --include="*.cs"
grep -rn "Logger\..*\$\"\|_logger\..*\$\"" --include="*.cs"

# Check for token/secret logging
grep -rn "Log.*apiKey\|Log.*token\|Log.*secret\|Log.*connectionString" -i --include="*.cs"

# Check for full object serialization in logs (risky)
grep -rn "Log.*JsonConvert\|Log.*Serialize" --include="*.cs"

# Check log configuration files
grep -rn "internalLogLevel\|MinimumLevel" --include="*.config" --include="*.json" --include="*.cs"
```

**.NET-Specific Checks:**

Use the following reference files for detailed patterns and checklists:
- `references/dotnet-security-checklist.md` -- Full .NET security checklist
- `references/telerik-security.md` -- Telerik-specific security guidance
- `references/owasp-top-10.md` -- OWASP patterns and code examples

### Phase 3: ANALYZE

**Objective:** Classify every finding by severity with evidence. Eliminate false positives.

**Steps:**

1. For each grep match, read surrounding context (10-20 lines) to determine if it is a true finding or a false positive
2. Classify severity using the classification guide below
3. Map each finding to its OWASP Top 10 category
4. Identify positive findings -- security controls that are properly implemented
5. Count findings by severity for the executive summary

**Severity Classification:**

**Critical** -- Active exploitation possible:
- Authentication bypass, Remote code execution, SQL injection with data access
- Hardcoded production credentials
- Telerik CVE-affected versions (ASP.NET AJAX only)
- Default/missing Telerik encryption keys (ASP.NET AJAX)
- Missing ASP.NET machine keys with Telerik
- Passwords/secrets logged (Serilog/NLog), Connection strings in logs

**High** -- Significant security weakness:
- Authorization flaws, Sensitive data exposure, Weak cryptography on sensitive data
- Missing security headers, Insecure deserialization
- jQuery `.html()` with user input, AJAX calls without CSRF tokens
- SQL Server `EXEC` with string concatenation, Database connection using sa/dbo accounts
- TelerikUpload without server-side validation, TelerikEditor content not sanitized
- TelerikGrid without server-side authorization
- Missing FluentValidation for commands/requests, API keys/tokens logged

**Medium** -- Notable concern requiring attention:
- Verbose error messages, Missing input validation, Insufficient logging
- CORS misconfiguration, Session management weaknesses
- Kendo Editor without content sanitization
- Missing `QUOTENAME` for dynamic SQL object names
- FluentValidation missing `MaximumLength()`
- String interpolation in log statements, PII (SSN, DOB) in logs
- Debug logging enabled in production

**Low** -- Minor issue or hardening opportunity:
- Missing security hardening, Informational findings, Best practice deviations
- Defense-in-depth opportunities, Missing Content Security Policy nonces
- NLog internal logging enabled

### Phase 4: REPORT

**Objective:** Generate a report that serves both managers (executive summary) and developers (technical details).

See `references/executive-summary-templates.md` for manager-friendly language templates.

Generate the report in this format:

```markdown
# Security Review: [Solution Name]

**Review Date**: [Date]
**Framework**: [.NET 8 / .NET Framework 4.8 / etc.]
**Application Type**: [Web API / MVC / Blazor / etc.]

---

## Executive Summary

[Write 3-4 sentences for managers explaining:
- Overall security posture (Strong/Adequate/Weak/Critical)
- Number and severity of findings
- Key risk areas
- Recommended action timeline]

**Example**: "This application has an adequate security posture with room for improvement. We identified 12 security findings: 2 high severity, 5 medium, and 5 low. The high-severity issues involve authentication weaknesses that could allow unauthorized access. We recommend addressing high-severity items within one week and medium items within one month."

### Risk Rating: [Critical/High/Medium/Low]

| Severity | Count | Description |
|----------|-------|-------------|
| Critical | X | Immediate exploitation risk |
| High | X | Significant security weakness |
| Medium | X | Notable concern requiring attention |
| Low | X | Minor issue or hardening opportunity |

---

## OWASP Top 10 Assessment

| Category | Status | Findings |
|----------|--------|----------|
| A01: Broken Access Control | Pass/Fail/Partial | [Brief summary] |
| A02: Cryptographic Failures | Pass/Fail/Partial | [Brief summary] |
| A03: Injection | Pass/Fail/Partial | [Brief summary] |
| A04: Insecure Design | Pass/Fail/Partial | [Brief summary] |
| A05: Security Misconfiguration | Pass/Fail/Partial | [Brief summary] |
| A06: Vulnerable Components | Pass/Fail/Partial | [Brief summary] |
| A07: Authentication Failures | Pass/Fail/Partial | [Brief summary] |
| A08: Data Integrity Failures | Pass/Fail/Partial | [Brief summary] |
| A09: Logging Failures | Pass/Fail/Partial | [Brief summary] |
| A10: SSRF | Pass/Fail/Partial | [Brief summary] |

## Additional Security Assessments

| Category | Status | Findings |
|----------|--------|----------|
| Telerik UI for Blazor | Pass/Fail/Partial/N/A | [Upload validation, Editor sanitization, Grid auth] |
| Telerik UI for MVC | Pass/Fail/Partial/N/A | [Kendo Upload, Editor, Grid security] |
| jQuery/JavaScript XSS | Pass/Fail/Partial/N/A | [DOM XSS, AJAX security] |
| SQL Server Stored Procs | Pass/Fail/Partial/N/A | [Dynamic SQL, privileges] |
| FluentValidation | Pass/Fail/Partial/N/A | [Validators coverage, injection prevention] |
| Logging Security (Serilog) | Pass/Fail/Partial/N/A | [PII in logs, structured logging] |
| Logging Security (NLog) | Pass/Fail/Partial/N/A | [PII in logs, config security] |
| Machine Keys (.NET Fx) | Pass/Fail/Partial/N/A | [Custom keys configured] |

---

## Detailed Findings

### Critical Severity

#### [Finding Title]
- **OWASP Category**: [A01-A10]
- **Location**: [File:Line or general area]
- **Risk Explanation**: [2-3 sentences in plain language explaining what could go wrong and business impact]
- **Technical Detail**: [Brief technical description]
- **Remediation**: [Specific fix with code example if applicable]

### High Severity
[Same format]

### Medium Severity
[Same format]

### Low Severity
[Same format]

---

## Remediation Roadmap

### Immediate (24-48 hours)
1. [Critical items]

### Short-term (1 week)
1. [High severity items]

### Medium-term (1 month)
1. [Medium severity items]

### Backlog
1. [Low severity items]

---

## Positive Findings

[List security controls that are properly implemented - this provides balance and acknowledges good practices]

1. [Good practice found]
2. [Good practice found]
```

## State Block

Maintain this state throughout the review session:

```xml
<dotnet-security-state>
  <mode>RECONNAISSANCE|SCAN|ANALYZE|REPORT</mode>
  <target_framework>unknown</target_framework>
  <telerik_version>unknown</telerik_version>
  <telerik_product>unknown|blazor|mvc-kendo|ajax-radcontrols|none</telerik_product>
  <owasp_categories_scanned>0/10</owasp_categories_scanned>
  <findings_critical>0</findings_critical>
  <findings_high>0</findings_high>
  <findings_medium>0</findings_medium>
  <findings_low>0</findings_low>
  <positive_findings>0</positive_findings>
  <last_action>none</last_action>
  <next_action>begin reconnaissance</next_action>
</dotnet-security-state>
```

Update the state block after each significant action. The mode field tracks which phase is active. The findings counters accumulate as the scan progresses. The `next_action` field ensures forward momentum -- never leave it blank.

## Output Templates

### Executive Summary (for managers)

Use the posture statements from `references/executive-summary-templates.md`:

- **Strong**: Few low-severity findings, good practices in place
- **Adequate**: Some high/medium findings, fundamentals present
- **Weak**: Multiple high-severity issues, gaps in basic controls
- **Critical**: Critical findings requiring immediate action

**Instead of**: "SQL injection vulnerability in UserRepository.cs via unsanitized input to FromSqlRaw"

**Write**: "An attacker could manipulate database queries to access or modify data they shouldn't have access to, potentially exposing customer information or corrupting records."

### Technical Findings Table

| # | Severity | OWASP | Location | Finding | Remediation |
|---|----------|-------|----------|---------|-------------|
| 1 | Critical | A03 | UserRepo.cs:45 | Raw SQL with concatenation | Use parameterized query or LINQ |
| 2 | High | A01 | OrderController.cs:22 | Missing [Authorize] attribute | Add authorization check |

### Remediation Roadmap

| Timeline | Severity | Count | Action |
|----------|----------|-------|--------|
| Immediate (24-48h) | Critical | X | [List items] |
| Short-term (1 week) | High | X | [List items] |
| Medium-term (1 month) | Medium | X | [List items] |
| Backlog | Low | X | [List items] |

### Positive Findings Section

Always include at least 3 positive observations. Examples:
- "Parameterized queries used consistently for database access"
- "ASP.NET Core Identity properly configured with strong password requirements"
- "HTTPS enforced throughout the application"
- "Input validation present on all user-facing forms"
- "Proper error handling that does not expose internal details"
- "Authentication logging captures security-relevant events"
- "Role-based authorization properly implemented"

## AI Discipline Rules

**CRITICAL -- these rules must never be violated:**

1. **Always check Telerik version for known CVEs.** If Telerik is present and the version cannot be determined, report the version as unknown and flag it as a finding. Do not assume the version is safe. Cross-reference against the CVE table in `references/telerik-security.md`.

2. **Never report severity without evidence.** Every finding must include the file path, line number (or general area), and the specific code pattern that triggered the finding. A severity label without supporting evidence is an opinion, not a finding.

3. **Always include positive findings.** A report with only negative findings is incomplete and demoralizing. Identify at least 3 security controls that are properly implemented. If the codebase is genuinely poor, acknowledge any attempt at security (e.g., "The application uses HTTPS" or "Authentication is present, though misconfigured").

4. **Use manager-friendly language in executive summaries.** The executive summary must be readable by someone who does not write code. No method names, no file paths, no technical jargon. Use the templates in `references/executive-summary-templates.md`. Technical detail belongs in the Detailed Findings section.

5. **Verify grep pattern matches before reporting.** A grep match is not a finding -- it is a lead. Read the surrounding code context before classifying severity. `FromSqlRaw` with parameterized arguments is safe. `[AllowAnonymous]` on a public health-check endpoint is correct. Context determines whether a pattern is a vulnerability or an appropriate design decision.

6. **Distinguish Telerik product lines.** CVE-2019-18935 applies to ASP.NET AJAX RadAsyncUpload, not to Telerik UI for Blazor or Kendo MVC. Reporting a Blazor application as vulnerable to RadAsyncUpload RCE is a false positive. Always identify the product line first. See `references/telerik-security.md` Part 1 vs Part 2 vs Part 3.

7. **Never skip the Remediation Roadmap.** Findings without remediation timelines do not get fixed. Every report must include Immediate / Short-term / Medium-term / Backlog categories with specific items assigned to each.

8. **Scan all 10 OWASP categories.** Do not stop after finding critical issues in A03 (Injection). Every category must be scanned and reported, even if the result is "Pass" with no findings. A complete OWASP assessment is the minimum deliverable.

## Anti-Patterns

| # | Anti-Pattern | Why It Is Wrong | Correct Approach |
|---|-------------|-----------------|------------------|
| 1 | **Reporting false positives without verification** | Erodes trust in the review and wastes developer time on non-issues | Read 10-20 lines of context around every grep match; verify the pattern is actually vulnerable |
| 2 | **Ignoring Telerik-specific CVEs** | Telerik CVEs are among the most exploited in enterprise .NET; adversaries scan for them specifically | Always identify the Telerik product line and version; check against known CVE list |
| 3 | **Only scanning for injection (A03)** | Injection is one of ten categories; stopping there misses access control, crypto, config, and logging issues | Complete all 10 OWASP categories plus domain-specific scans |
| 4 | **Skipping configuration review** | Debug mode, permissive CORS, and missing security headers are among the easiest vulnerabilities to exploit | Always scan appsettings.json, web.config, and middleware configuration |
| 5 | **Reporting everything as Critical** | When everything is critical, nothing is critical; managers cannot prioritize remediation | Use the severity classification guide; Critical means active exploitation is possible |
| 6 | **Missing positive findings** | Reports without positive findings appear adversarial and are less likely to result in remediation action | Include at least 3 positive observations that acknowledge good security practices |
| 7 | **Writing executive summaries in technical language** | Decision-makers who cannot understand the summary will not authorize remediation resources | Use `references/executive-summary-templates.md` language; save technical detail for the findings section |
| 8 | **Treating all Telerik products as equally risky** | Blazor and MVC/Kendo have very different security profiles than ASP.NET AJAX RadControls | Identify the specific product line before assessing Telerik risk; see `references/telerik-security.md` |
| 9 | **Skipping the logging security scan** | Sensitive data in logs is a compliance violation (GDPR, HIPAA, PCI) and an attacker resource | Always scan for passwords, tokens, PII, and connection strings in log statements |
| 10 | **Not scanning FluentValidation coverage** | Commands and requests without validators are injection surface; missing MaximumLength enables buffer-style attacks | Check that every Command/Request DTO has a corresponding validator with length limits |

## Error Recovery

### Scenario 1: No vulnerabilities found but uncertain

**Situation:** The scan completes with zero findings across all categories. This is possible but rare for any non-trivial application.

**Recovery:**
1. Re-verify that the grep patterns matched the correct file types (`.cs`, `.cshtml`, `.razor`, `.config`, `.json`, `.js`)
2. Check that the working directory is correct and contains source files (not a build output directory)
3. Look for custom frameworks or unconventional patterns that the standard grep patterns would miss
4. If the application is genuinely clean, report it as such with high confidence. Document what was scanned and what was found. A clean report is valuable information.
5. Recommend periodic re-review since new CVEs are published daily

### Scenario 2: Telerik version unknown

**Situation:** Telerik components are present in the codebase (grep matches on component names) but the version cannot be determined from `.csproj` or `packages.config` files.

**Recovery:**
1. Check for `Telerik.Web.UI.dll` or similar binaries in `bin/` or `lib/` directories and inspect file properties
2. Search for version strings in `.config` files: `grep -rn "Telerik.*version\|Telerik.*Version" --include="*.config"`
3. Check for NuGet package cache references
4. If version remains unknown, **report it as a finding** (High severity): "Telerik components detected but version cannot be verified against known CVE list. Manual version verification required."
5. Include the specific CVEs that should be checked once the version is determined

### Scenario 3: Mixed .NET Framework and .NET Core in same solution

**Situation:** The solution contains both .NET Framework 4.x projects and .NET 6+ projects, which have different security models, configuration patterns, and Telerik product lines.

**Recovery:**
1. Inventory all projects with their target frameworks: `grep -rn "TargetFramework" --include="*.csproj"`
2. Run the scan twice -- once with .NET Framework patterns (web.config, machine keys, RadControls) and once with .NET Core patterns (appsettings.json, middleware pipeline, Blazor/Kendo)
3. Keep findings separated by framework in the report
4. Pay special attention to shared libraries that are referenced by both framework versions
5. Note any shared database connections or authentication systems that bridge the two frameworks

### Scenario 4: Large solution with hundreds of projects

**Situation:** The solution is too large for manual grep review of every match.

**Recovery:**
1. Prioritize web-facing projects (API, MVC, Blazor) over internal libraries and console apps
2. Focus scan on projects that handle user input, authentication, and data access
3. Use `--include` patterns to narrow file scope
4. Report scope limitations in the executive summary: "This review focused on the X web-facing projects. Internal libraries were assessed for shared security concerns only."

## Integration with Other Skills

- **`supply-chain-audit`**: Defer to this skill for NuGet package vulnerability scanning (OWASP A06: Vulnerable Components). It provides comprehensive CVE correlation, license compliance, and maintenance health analysis across NuGet, npm, and pip ecosystems.

- **`dotnet-security-review-federal`**: When the application operates in LANL/DOE/DOD environments, apply this compliance overlay after completing the base OWASP scan. It adds NIST SP 800-53 control mapping, FIPS 140-2/3 cryptographic requirements, and CUI handling verification.

- **`architecture-review`**: For system-level security concerns that go beyond code-level scanning -- network segmentation, service boundaries, trust zones, and infrastructure security. The architecture review provides the "big picture" context that individual code findings fit into.

- **`dotnet-architecture-checklist`**: Cross-reference security findings with architecture patterns. A missing `[Authorize]` attribute may indicate a broader pattern of missing authorization middleware. An insecure deserialization finding may point to architectural decisions about data serialization formats.
