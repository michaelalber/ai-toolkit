---
name: nuget-security-review
description: Reviews NuGet packages for security vulnerabilities and available updates. Generates manager-friendly executive summaries explaining risks and update priorities. Use when asked to review dependencies, audit packages, check for vulnerabilities, review NuGet packages, assess security risks, or check for outdated packages. Triggers on phrases like "review nuget", "package security", "dependency audit", "outdated packages", "vulnerability scan", "check dependencies".
---

# NuGet Package Security & Update Review

Conducts comprehensive NuGet package reviews with executive summaries suitable for management reporting.

## Quick Start

When triggered:
1. Locate all `.csproj` files in the solution
2. Run `dotnet list package --outdated` for update analysis
3. Run `dotnet list package --vulnerable` for security analysis
4. Generate the two-part report with executive summaries

## Review Commands

```bash
# Find all project files
find . -name "*.csproj" | head -20

# Check for outdated packages (all projects)
dotnet list package --outdated

# Check for vulnerable packages
dotnet list package --vulnerable

# For specific project
dotnet list [project.csproj] package --outdated
dotnet list [project.csproj] package --vulnerable

# Include transitive dependencies
dotnet list package --vulnerable --include-transitive
```

## Output Format

Generate the report in this exact format:

```markdown
# NuGet Package Review: [Solution Name]

**Review Date**: [Date]
**Projects Scanned**: [Count]

---

## Part 1: Packages Requiring Updates

### Executive Summary

[Write 2-3 sentences for managers explaining:
- How many packages need updates
- Overall risk level of not updating (Low/Medium/High)
- Recommended action timeline (immediate/soon/scheduled maintenance)]

**Example**: "This solution has 8 packages requiring updates. Most updates are routine maintenance with low risk, but 2 packages have significant version gaps that could cause compatibility issues if delayed further. We recommend scheduling these updates within the next sprint cycle."

### Update Details

| Package | Current | Latest | Priority | Business Impact |
|---------|---------|--------|----------|-----------------|
| [Name] | [Ver] | [Ver] | High/Med/Low | [One sentence] |

#### Package-by-Package Summary

**[Package.Name]** (Current: X.X.X → Latest: Y.Y.Y)
- **Priority**: [High/Medium/Low]
- **Why Update**: [1-2 sentences explaining in non-technical terms why this update matters. Focus on stability, performance, or compatibility benefits.]

---

## Part 2: Security Vulnerabilities

### Executive Summary

[Write 2-3 sentences for managers explaining:
- Total vulnerability count and severity breakdown
- Potential business impact if not addressed
- Required action urgency]

**Example**: "We identified 3 security vulnerabilities in project dependencies: 1 critical and 2 moderate. The critical vulnerability could allow unauthorized access to user data if exploited. Immediate remediation is required for the critical issue; moderate issues should be addressed within 2 weeks."

### Vulnerability Details

| Package | Severity | CVE | Affected Versions | Fixed In |
|---------|----------|-----|-------------------|----------|
| [Name] | Critical/High/Moderate/Low | [CVE-ID] | [Range] | [Ver] |

#### Vulnerability-by-Vulnerability Summary

**[Package.Name]** - [CVE-ID or Advisory ID]
- **Severity**: [Critical/High/Moderate/Low]
- **Risk Explanation**: [2-3 sentences explaining what could go wrong in plain language. Avoid jargon. Focus on business impact: data exposure, service disruption, compliance risk, etc.]
- **Recommended Action**: [Specific version to update to or mitigation steps]

---

## Summary & Recommendations

### Immediate Actions Required
1. [List critical/high severity items]

### Scheduled Maintenance
1. [List medium priority items]

### Monitor/Low Priority
1. [List low priority items]
```

## Priority Guidelines

See `references/severity-guidelines.md` for detailed prioritization rules.

### Quick Reference

**Critical Priority** (Fix within 24-48 hours):
- Known exploited vulnerabilities (KEV listed)
- Critical severity (CVSS 9.0+)
- Authentication/authorization bypasses
- Remote code execution

**High Priority** (Fix within 1 week):
- High severity (CVSS 7.0-8.9)
- Data exposure risks
- Major version gaps (2+ major versions behind)

**Medium Priority** (Fix within 1 month):
- Moderate severity (CVSS 4.0-6.9)
- One major version behind
- Deprecated packages

**Low Priority** (Scheduled maintenance):
- Low severity (CVSS < 4.0)
- Minor/patch updates only
- No security implications

## Writing Executive Summaries

See `references/executive-summary-templates.md` for guidance on writing manager-friendly summaries.

### Key Principles

1. **Avoid technical jargon**: Say "unauthorized access" not "authentication bypass vulnerability"
2. **Focus on business impact**: Data loss, service downtime, compliance violations, reputation risk
3. **Be specific about urgency**: "within 24 hours" not "ASAP"
4. **Provide context**: "1 of 3 vulnerabilities is critical" not just "3 vulnerabilities found"
5. **Recommend actions**: Always end with clear next steps

## Example Vulnerability Explanations

**Instead of**: "CVE-2024-12345: Deserialization of untrusted data vulnerability in Newtonsoft.Json allowing RCE"

**Write**: "This vulnerability could allow an attacker to run malicious code on our servers by sending specially crafted data. If exploited, an attacker could gain full control of the affected system. This directly impacts our ability to protect customer data and maintain service availability."

## No Issues Found

If no vulnerabilities or updates are found:

```markdown
# NuGet Package Review: [Solution Name]

**Review Date**: [Date]
**Projects Scanned**: [Count]

## Summary

All NuGet packages are up-to-date and no known security vulnerabilities were detected.

**Recommendations**:
- Continue regular dependency monitoring
- Consider enabling GitHub Dependabot or similar automated scanning
- Schedule quarterly dependency reviews
```
