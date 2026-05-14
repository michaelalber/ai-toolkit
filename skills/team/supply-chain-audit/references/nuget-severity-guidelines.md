# Severity & Priority Guidelines

Rules for categorizing NuGet package issues and determining remediation priority.

## Vulnerability Severity Levels

### Critical (CVSS 9.0-10.0)

**Characteristics**:
- Remotely exploitable without authentication
- No user interaction required
- Complete system compromise possible
- Active exploitation in the wild

**Common Examples**:
- Remote code execution (RCE)
- Authentication bypass with admin access
- SQL injection with data exfiltration
- Deserialization attacks

**Response Time**: 24-48 hours

**Manager Summary**: "This could allow complete unauthorized control of our systems. This is a security emergency."

---

### High (CVSS 7.0-8.9)

**Characteristics**:
- Significant impact but may require some conditions
- Potential data exposure or service disruption
- May require authentication or user interaction

**Common Examples**:
- Authenticated RCE
- Sensitive data exposure
- Privilege escalation
- Server-Side Request Forgery (SSRF)

**Response Time**: Within 1 week

**Manager Summary**: "This could lead to data exposure or service disruption under certain conditions. Should be addressed promptly."

---

### Moderate (CVSS 4.0-6.9)

**Characteristics**:
- Limited impact scope
- Requires specific conditions or configurations
- May only affect availability, not confidentiality/integrity

**Common Examples**:
- Denial of service (crash/resource exhaustion)
- Limited information disclosure
- Cross-site scripting (XSS) in limited contexts
- Open redirects

**Response Time**: Within 2 weeks

**Manager Summary**: "This presents a limited risk that could cause issues under specific circumstances. Should be addressed in the near term."

---

### Low (CVSS 0.1-3.9)

**Characteristics**:
- Minimal real-world impact
- Requires unlikely conditions
- Defense-in-depth only

**Common Examples**:
- Information leaks of non-sensitive data
- Theoretical vulnerabilities with no practical exploit
- Issues mitigated by other controls

**Response Time**: Next maintenance cycle

**Manager Summary**: "This is a minor issue with minimal practical risk. Can be addressed during routine maintenance."

---

## Package Update Priority Levels

### High Priority Updates

**Criteria** (any of these):
- 2+ major versions behind latest
- Package marked as deprecated
- Package has known compatibility issues with current .NET version
- Security fixes included in newer versions (even if not flagged as vulnerable)
- Package maintainer recommends urgent update

**Manager Summary**: "These packages are significantly out of date and should be updated soon to prevent compatibility and stability issues."

---

### Medium Priority Updates

**Criteria**:
- 1 major version behind
- 3+ minor versions behind
- Performance improvements in newer versions
- Bug fixes that may affect application stability

**Manager Summary**: "These packages have meaningful updates available that would improve application quality."

---

### Low Priority Updates

**Criteria**:
- Minor or patch version updates only
- No security implications
- Primarily documentation or minor improvements

**Manager Summary**: "These are routine updates that can be included in regular maintenance."

---

## Special Considerations

### Transitive Dependencies

When vulnerabilities exist in transitive (indirect) dependencies:

1. Check if the direct parent package has an update that resolves it
2. If not, check if the vulnerability is actually reachable in your usage
3. Note in report whether the vulnerability is in a direct or transitive dependency

**Manager language**: "This issue exists in a package that our code uses indirectly. [It can/cannot] be resolved by updating [direct package name]."

### Framework Dependencies

For Microsoft.* and System.* packages tied to .NET framework:

1. These often require .NET framework upgrade, not just package update
2. Note the minimum .NET version required
3. Factor in broader framework upgrade effort

**Manager language**: "This update requires upgrading the .NET framework version, which is a larger undertaking than a typical package update."

### Breaking Changes

When updates include breaking changes:

1. Note the scope of changes needed
2. Reference migration guides if available
3. Factor into priority assessment

**Manager language**: "This update includes changes that will require code modifications. [Minor adjustments/Moderate refactoring/Significant rework] will be needed."

---

## Priority Matrix

| Vulnerability | Update Available | Priority |
|--------------|------------------|----------|
| Critical | Yes | IMMEDIATE - 24-48 hours |
| Critical | No (mitigation only) | IMMEDIATE - implement mitigation |
| High | Yes | URGENT - 1 week |
| High | No | URGENT - implement mitigation + monitor |
| Moderate | Yes | SOON - 2 weeks |
| Low | Yes | SCHEDULED - maintenance cycle |
| None | Major update (2+) | PLANNED - next sprint |
| None | Major update (1) | PLANNED - 1-2 months |
| None | Minor/Patch only | ROUTINE - maintenance |

---

## CISA KEV Catalog Check

For any vulnerability, check if it appears in CISA's Known Exploited Vulnerabilities catalog:
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog

If present, automatically escalate to **Critical** priority regardless of CVSS score.

**Manager language**: "This vulnerability is being actively exploited in real attacks according to U.S. government security agencies."

---

## Compliance Considerations

Certain industries have specific patching requirements:

| Industry | Typical Requirement |
|----------|---------------------|
| Financial (PCI-DSS) | Critical within 1 month, High within 3 months |
| Healthcare (HIPAA) | Risk-based, document all decisions |
| Government (FedRAMP) | Per CISA BOD 22-01 timelines |
| General SOC 2 | Documented patching policy followed |

Include compliance notes when relevant to the organization.
