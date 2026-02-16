---
name: dotnet-security-review
description: Conducts security reviews of .NET and .NET Framework applications using OWASP Top 10 as the baseline. Identifies vulnerabilities, insecure patterns, and compliance gaps. Generates manager-friendly reports with risk explanations and remediation priorities. Use when asked to review security, audit code for vulnerabilities, check OWASP compliance, assess security risks, or find security issues. Triggers on phrases like "security review", "OWASP audit", "vulnerability assessment", "security scan", "check for vulnerabilities", "security compliance".
---

# .NET Security Review (OWASP Baseline)

Conducts comprehensive security reviews of .NET and .NET Framework applications using OWASP Top 10 2021 as the primary framework.

## Quick Start

When triggered:
1. Determine framework: .NET 6+ or .NET Framework 4.x
2. Identify application type: Web API, MVC, Blazor, WinForms, WPF, Console
3. Scan for OWASP Top 10 vulnerabilities using the checklist
4. Generate the security report with executive summary

## Review Process

### Step 1: Reconnaissance

```bash
# Find all project files and determine framework
find . -name "*.csproj" -exec grep -l "TargetFramework" {} \;

# Check for web projects
find . -name "Startup.cs" -o -name "Program.cs" | head -10

# Find configuration files
find . -name "appsettings*.json" -o -name "web.config" -o -name "app.config"

# Identify authentication setup
grep -r "AddAuthentication\|AddAuthorization\|UseAuthentication" --include="*.cs" | head -20
```

### Step 2: OWASP Top 10 Scan

Use `references/owasp-top-10.md` for detailed patterns. Quick scan commands:

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
# See nuget-security-review skill

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

### Step 3: Telerik UI Components Scan (Critical)

Telerik components have significant CVE history. Always check:

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

### Step 4: jQuery/JavaScript XSS Scan

```bash
# Dangerous jQuery patterns
grep -rn "\.html(\|\.append(\|\.prepend(" --include="*.js" --include="*.ts"

# Safe alternatives should use .text()
grep -rn "\.text(" --include="*.js" --include="*.ts"

# Dangerous eval patterns
grep -rn "eval(\|new Function(\|setTimeout.*\"" --include="*.js" --include="*.ts"

# URL parameter usage (potential DOM XSS)
grep -rn "location\.search\|location\.hash\|URLSearchParams" --include="*.js" --include="*.ts"

# AJAX without CSRF tokens
grep -rn "\$\.ajax\|\$\.post\|\$\.get" --include="*.js" --include="*.ts"

# innerHTML usage
grep -rn "innerHTML\|outerHTML" --include="*.js" --include="*.ts"
```

### Step 5: SQL Server Stored Procedure Scan

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

### Step 6: FluentValidation Scan

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

### Step 7: Logging Security Scan (Serilog/NLog)

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

### Step 8: .NET-Specific Checks

Use the following reference files:
- `references/dotnet-security-checklist.md` - Full .NET security checklist
- `references/telerik-security.md` - Telerik-specific security guidance
- `references/owasp-top-10.md` - OWASP patterns and code examples

## Output Format

Generate the report in this exact format:

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

## Severity Classification

### Critical
- Active exploitation possible
- Authentication bypass
- Remote code execution
- SQL injection with data access
- Hardcoded production credentials
- Telerik CVE-affected versions (ASP.NET AJAX only)
- Default/missing Telerik encryption keys (ASP.NET AJAX)
- Missing ASP.NET machine keys with Telerik
- Passwords/secrets logged (Serilog/NLog)
- Connection strings in logs

### High
- Authorization flaws
- Sensitive data exposure
- Weak cryptography on sensitive data
- Missing security headers
- Insecure deserialization
- jQuery `.html()` with user input
- AJAX calls without CSRF tokens
- SQL Server `EXEC` with string concatenation
- Database connection using sa/dbo accounts
- TelerikUpload without server-side validation
- TelerikEditor content not sanitized
- TelerikGrid without server-side authorization
- Missing FluentValidation for commands/requests
- API keys/tokens logged

### Medium
- Verbose error messages
- Missing input validation
- Insufficient logging
- CORS misconfiguration
- Session management weaknesses
- Kendo Editor without content sanitization
- `eval()` or `new Function()` usage
- Missing `QUOTENAME` for dynamic SQL object names
- FluentValidation missing `MaximumLength()`
- String interpolation in log statements
- PII (SSN, DOB) in logs
- Debug logging enabled in production

### Low
- Missing security hardening
- Informational findings
- Best practice deviations
- Defense-in-depth opportunities
- Missing Content Security Policy nonces
- NLog internal logging enabled

## Manager-Friendly Language

See `references/executive-summary-templates.md` for templates.

**Instead of**: "SQL injection vulnerability in UserRepository.cs via unsanitized input to FromSqlRaw"

**Write**: "An attacker could manipulate database queries to access or modify data they shouldn't have access to, potentially exposing customer information or corrupting records."
