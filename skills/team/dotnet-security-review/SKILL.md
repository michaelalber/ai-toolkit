---
name: dotnet-security-review
description: Conducts OWASP-based security reviews of .NET and .NET Framework applications with Telerik UI specialization. Identifies vulnerabilities, insecure patterns, and compliance gaps across all OWASP Top 10 categories. Generates manager-friendly reports with risk explanations and remediation priorities. Use when asked to review security, audit code for vulnerabilities, check OWASP compliance, assess security risks, find security issues, scan for CVEs, review Telerik security, or evaluate application security posture. Triggers on phrases like "security review", "OWASP audit", "vulnerability assessment", "security scan", "check for vulnerabilities", "security compliance", "Telerik security", "security posture", "penetration test prep".
---

# .NET Security Review (OWASP Baseline)

> "Security is not a product, but a process."
> -- Bruce Schneier, *Secrets and Lies*

## Core Philosophy

Security is a first-class concern in every .NET application, not an afterthought bolted on before deployment. The OWASP Top 10 provides a proven baseline, but it is a floor, not a ceiling -- mature applications must go beyond the Top 10 to address domain-specific risks like Telerik component CVEs, logging hygiene, and stored procedure injection.

Telerik UI components deserve special attention because of their prevalence in enterprise .NET applications and their documented CVE history. The ASP.NET AJAX product line (RadAsyncUpload, RadEditor) has had multiple critical remote code execution vulnerabilities that were actively exploited. Failing to check Telerik versions and configuration is a gap that adversaries specifically probe for.

Manager-friendly reporting is not optional. If a security review cannot be understood by the people who authorize remediation budgets, it will not result in action. Both audiences must be served in every report. See `references/executive-summary-templates.md` for the language patterns that bridge technical findings and business impact.

## Domain Principles

| # | Principle | Description |
|---|-----------|-------------|
| 1 | **Defense in Depth** | Never rely on a single security control. Layer authentication, authorization, input validation, output encoding, and encryption. |
| 2 | **Least Privilege** | Every component -- database accounts, service identities, user roles -- should operate with the minimum permissions required. An `sa` database connection is a finding, not a convenience. |
| 3 | **Input Validation** | All external input is untrusted. Validate type, length, range, and format on the server side. Client-side validation is UX; server-side validation is security. |
| 4 | **Output Encoding** | Encode all output based on context (HTML, JavaScript, URL, SQL). Razor provides automatic encoding; `@Html.Raw()` and `MarkupString` bypass it and must be justified. |
| 5 | **Secure Defaults** | Applications should be secure out of the box. Debug mode off, HTTPS required, CORS restricted, authentication mandatory. |
| 6 | **Fail Securely** | When errors occur, fail closed. Do not expose stack traces, connection strings, or internal paths. Return safe error responses. |
| 7 | **Separation of Concerns** | Centralize authorization policies, validation pipelines, and sanitization services. FluentValidation pipeline behaviors and policy-based authorization are the patterns to look for. |
| 8 | **Audit Trail** | Security-relevant events must be logged. Logs must never contain passwords, tokens, PII, or connection strings. |
| 9 | **Dependency Awareness** | Every NuGet package and JavaScript library is attack surface. Defer to `supply-chain-audit` for comprehensive dependency analysis. |
| 10 | **Telerik Component Security** | Telerik products span three distinct security profiles: Blazor (low CVE risk), MVC/Kendo (medium), ASP.NET AJAX/RadControls (high -- multiple critical RCE CVEs). Always identify the product line first. |

## Knowledge Base Lookups

| Query | When to Call |
|-------|--------------|
| `search_knowledge("OWASP Top 10 injection XSS broken access control")` | At RECONNAISSANCE phase -- load authoritative OWASP categories before scanning |
| `search_knowledge("ASP.NET Core authentication authorization policy JWT")` | During authentication/authorization scan |
| `search_knowledge("SQL injection parameterized queries Entity Framework")` | When reviewing data access layer |
| `search_knowledge("Telerik RadAsyncUpload CVE ASP.NET AJAX security")` | When Telerik AJAX/RadControls is detected |
| `search_knowledge("logging sensitive data PII credentials security")` | During logging hygiene review |

Search at RECONNAISSANCE phase and before scoring any finding category. Cite the source in the executive summary.

## Workflow

### Phase 1: RECONNAISSANCE

Determine the technology stack, hosting model, and attack surface before scanning.

```bash
# Find all project files and determine framework
find . -name "*.csproj" -exec grep -l "TargetFramework" {} \;

# Find configuration files
find . -name "appsettings*.json" -o -name "web.config" -o -name "app.config"

# Identify authentication setup
grep -r "AddAuthentication\|AddAuthorization\|UseAuthentication" --include="*.cs" | head -20

# Identify Telerik product line
grep -rn "Telerik.UI.for.Blazor\|Kendo.Mvc\|Telerik.Web.UI" --include="*.csproj" --include="packages.config" --include="*.cs"
```

### Phase 2: SCAN

Run grep patterns for each OWASP Top 10 category plus domain-specific checks.

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

# A05: Security Misconfiguration
grep -rn "CORS\|AllowAnyOrigin\|AllowCredentials" --include="*.cs"
grep -rn "Debug.*true\|<compilation debug=\"true\"" --include="*.cs" --include="*.config" --include="*.json"

# A07: Authentication Failures
grep -rn "PasswordSignInAsync\|SignInAsync\|ValidateCredentials" --include="*.cs"
grep -rn "lockout\|MaxFailedAccessAttempts" --include="*.cs"

# A08: Data Integrity Failures
grep -rn "Deserialize\|BinaryFormatter\|XmlSerializer\|JsonConvert" --include="*.cs"
grep -rn "TypeNameHandling" --include="*.cs"

# A09: Logging Failures -- Sensitive Data
grep -rn "Log.*password\|Log.*token\|Log.*apiKey\|Log.*connectionString" -i --include="*.cs"
grep -rn "_logger.*password\|_logger.*secret" -i --include="*.cs"

# A10: SSRF
grep -rn "HttpClient\|WebClient\|WebRequest\|HttpWebRequest" --include="*.cs"
grep -rn "new Uri\(.*\+\|Uri\.Parse" --include="*.cs"
```

**Telerik UI Components Scan (Critical):**

```bash
# Find Telerik references
grep -rn "Telerik\|RadAsyncUpload\|RadEditor\|RadGrid" --include="*.cs" --include="*.aspx" --include="*.ascx" --include="*.config"

# RadAsyncUpload configuration (Critical CVEs)
grep -rn "RadAsyncUpload\|AsyncUpload" --include="*.aspx" --include="*.ascx" --include="*.cs"

# Telerik encryption keys (must be custom, not defaults)
grep -rn "ConfigurationEncryptionKey\|ConfigurationHashKey\|DialogParametersEncryptionKey" --include="*.config"

# Machine keys (required for Telerik security)
grep -rn "machineKey\|validationKey\|decryptionKey" --include="*.config"
```

**Known Critical CVEs:** CVE-2019-18935 (RadAsyncUpload RCE, before 2020.1.114), CVE-2017-11317 (RadAsyncUpload RCE, before 2017.2.621), CVE-2017-9248 (Telerik.Web.UI crypto weakness), CVE-2014-2217 (RadEditor DialogHandler path traversal).

```bash
# jQuery/JavaScript XSS
grep -rn "\.html(\|\.append(\|\.prepend(\|innerHTML\|outerHTML" --include="*.js" --include="*.ts"
grep -rn "setTimeout.*\"" --include="*.js" --include="*.ts"
grep -rn "location\.search\|location\.hash\|URLSearchParams" --include="*.js" --include="*.ts"

# SQL Server Stored Procedures
grep -rn "EXEC(\|EXECUTE(" --include="*.sql"
grep -rn "sp_executesql\|QUOTENAME" --include="*.sql"
grep -rn "User Id=sa\|uid=sa" --include="*.config" --include="*.json" --include="*.cs"

# FluentValidation coverage
grep -rn "AbstractValidator\|IValidator" --include="*.cs"
grep -rn "MaximumLength\|MinimumLength\|Matches\|Must(" --include="*.cs"
grep -rn "class.*Command\s*:\|class.*Request\s*:" --include="*.cs" | grep -v "Validator"

# Logging Security (Serilog/NLog)
grep -rn "Log.*password\|Log.*ssn\|Log.*creditcard\|Log.*JsonConvert\|Log.*Serialize" -i --include="*.cs"
grep -rn "LogInformation.*\$\"\|LogDebug.*\$\"" --include="*.cs"
```

See `references/owasp-top-10.md` for detailed patterns per category.

### Phase 3: ANALYZE

For each grep match, read surrounding context (10-20 lines) to determine true finding vs. false positive. Classify severity and map to OWASP category. Identify positive findings.

**Severity Classification:**

| Severity | Examples |
|----------|---------|
| **Critical** | Auth bypass, RCE, SQL injection with data access, hardcoded production credentials, Telerik CVE-affected versions (AJAX only), missing Telerik encryption keys, passwords/secrets logged |
| **High** | Authorization flaws, sensitive data exposure, weak crypto, jQuery `.html()` with user input, AJAX without CSRF, SQL EXEC with concatenation, sa/dbo database connection, missing FluentValidation for commands |
| **Medium** | Verbose error messages, missing input validation, CORS misconfiguration, session weaknesses, FluentValidation missing MaximumLength, string interpolation in logs, PII in logs, debug logging in production |
| **Low** | Missing security hardening, best practice deviations, missing CSP nonces, NLog internal logging enabled |

### Phase 4: REPORT

Generate a report serving both managers (executive summary) and developers (technical details). See `references/executive-summary-templates.md` for full report template and manager-friendly language patterns.

**Report structure:**
1. Executive Summary (3-4 sentences, risk rating, severity count table)
2. OWASP Top 10 Assessment (Pass/Fail/Partial per category)
3. Additional Security Assessments (Telerik, jQuery XSS, SQL procs, FluentValidation, logging)
4. Detailed Findings by severity (OWASP category, location, plain-language risk, remediation)
5. Remediation Roadmap (Immediate / 1 week / 1 month / Backlog)
6. Positive Findings

## State Block

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

## Output Templates

**Executive Summary posture statements** (from `references/executive-summary-templates.md`):
- **Strong**: Few low-severity findings, good practices in place
- **Adequate**: Some high/medium findings, fundamentals present
- **Weak**: Multiple high-severity issues, gaps in basic controls
- **Critical**: Critical findings requiring immediate action

**Instead of**: "SQL injection via unsanitized input to FromSqlRaw in UserRepository.cs"
**Write**: "An attacker could manipulate database queries to access or modify data they shouldn't, potentially exposing customer information or corrupting records."

**Technical Findings Table:**

| # | Severity | OWASP | Location | Finding | Remediation |
|---|----------|-------|----------|---------|-------------|
| 1 | Critical | A03 | UserRepo.cs:45 | Raw SQL with concatenation | Use parameterized query or LINQ |

**Positive Findings:** Always include at least 3 (e.g., "Parameterized queries used consistently", "HTTPS enforced throughout", "Role-based authorization properly implemented").

## AI Discipline Rules

1. **Always check Telerik version for known CVEs.** If version cannot be determined, report it as unknown and flag as a finding. Do not assume safe. Cross-reference against the CVE table in `references/telerik-security.md`.
2. **Never report severity without evidence.** Every finding must include file path, line number, and the specific code pattern. A severity label without supporting evidence is an opinion, not a finding.
3. **Always include positive findings.** At least 3 security controls properly implemented. A report with only negatives is incomplete and demoralizing.
4. **Use manager-friendly language in executive summaries.** No method names, no file paths, no jargon. Technical detail belongs in the Detailed Findings section.
5. **Verify grep pattern matches before reporting.** `FromSqlRaw` with parameterized arguments is safe. `[AllowAnonymous]` on a health-check endpoint is correct. Context determines vulnerability.
6. **Distinguish Telerik product lines.** CVE-2019-18935 applies to ASP.NET AJAX RadAsyncUpload, not Blazor or Kendo MVC. Always identify the product line first. See `references/telerik-security.md`.
7. **Never skip the Remediation Roadmap.** Findings without timelines do not get fixed. Every report needs Immediate/Short-term/Medium-term/Backlog with specific items.
8. **Scan all 10 OWASP categories.** Every category must be scanned and reported, even if the result is "Pass."

## Anti-Patterns

| # | Anti-Pattern | Why It Is Wrong | Correct Approach |
|---|-------------|-----------------|------------------|
| 1 | **Reporting false positives without verification** | Erodes trust, wastes developer time | Read 10-20 lines of context around every grep match |
| 2 | **Ignoring Telerik-specific CVEs** | Adversaries scan specifically for Telerik vulnerabilities | Always identify product line and version; check CVE list |
| 3 | **Only scanning A03 (injection)** | Stops at one of ten categories; misses access control, crypto, config, logging | Complete all 10 OWASP categories plus domain-specific scans |
| 4 | **Skipping configuration review** | Debug mode and permissive CORS are easiest to exploit | Always scan appsettings.json, web.config, and middleware configuration |
| 5 | **Reporting everything as Critical** | When everything is critical, nothing is; managers cannot prioritize | Use severity classification guide; Critical = active exploitation possible |
| 6 | **Missing positive findings** | Reports without positives appear adversarial; less likely to result in action | Include at least 3 positive observations |
| 7 | **Executive summaries in technical language** | Decision-makers cannot authorize resources they cannot understand | Use `references/executive-summary-templates.md`; save technical detail for findings section |
| 8 | **Treating all Telerik products equally** | Blazor and MVC/Kendo have very different security profiles than ASP.NET AJAX | Identify the specific product line before assessing Telerik risk |
| 9 | **Skipping logging security scan** | Sensitive data in logs is a compliance violation (GDPR, HIPAA, PCI) | Always scan for passwords, tokens, PII, and connection strings in log statements |
| 10 | **Not scanning FluentValidation coverage** | Commands/requests without validators are injection surface | Check that every Command/Request DTO has a corresponding validator with length limits |

## Error Recovery

**No vulnerabilities found but uncertain**: Re-verify grep patterns matched correct file types (`.cs`, `.cshtml`, `.razor`, `.config`, `.json`, `.js`). Check working directory contains source files, not build output. Look for unconventional patterns standard greps would miss. If genuinely clean, report with high confidence and document what was scanned.

**Telerik version unknown**: Check `bin/` directories for DLL file properties. Search config files: `grep -rn "Telerik.*version\|Telerik.*Version" --include="*.config"`. If still unknown, report as High finding: "Telerik components detected but version cannot be verified against known CVE list. Manual verification required."

**Mixed .NET Framework and .NET Core**: Inventory all projects with target frameworks. Run the scan twice -- once with .NET Framework patterns (web.config, machine keys, RadControls) and once with .NET Core patterns (appsettings.json, middleware, Blazor/Kendo). Keep findings separated by framework.

**Large solution with hundreds of projects**: Prioritize web-facing projects (API, MVC, Blazor) over internal libraries. Focus on projects handling user input, authentication, and data access. Document scope limitations in the executive summary.

## Integration with Other Skills

- **`supply-chain-audit`**: Defer for NuGet package vulnerability scanning (OWASP A06). Provides comprehensive CVE correlation, license compliance, and maintenance health analysis.
- **`dotnet-security-review-federal`**: Apply this compliance overlay after completing the base OWASP scan when the application operates in federal environments. Adds NIST SP 800-53, FIPS 140-2/3, and CUI handling.
- **`architecture-review`**: For system-level security concerns -- network segmentation, service boundaries, trust zones. The architecture review provides the "big picture" context individual findings fit into.
- **`dotnet-architecture-checklist`**: Cross-reference security findings with architecture patterns. A missing `[Authorize]` may indicate a broader pattern of missing authorization middleware.
