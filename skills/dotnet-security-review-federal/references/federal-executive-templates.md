# Federal Executive Summary Templates

Manager-friendly language for federal security review reports. Tailored for DOE/LANL leadership, program managers, and federal stakeholders.

---

## Overall Posture Statements

### Compliant Posture
> "This [Moderate/High]-impact system demonstrates strong alignment with NIST SP 800-53 security controls. Our assessment identified [X] findings requiring attention, with no critical or high-priority issues that would impact the system's Authorization to Operate (ATO). The development team has implemented security controls consistent with federal requirements. We recommend addressing the [Y] medium-priority items as part of continuous monitoring activities."

### Minor Gaps
> "This [Moderate/High]-impact system has a solid security foundation with minor gaps in NIST control implementation. We identified [X] findings: [Y] medium-priority and [Z] low-priority. No issues were found that would jeopardize the system's ATO, but remediation of medium-priority items should be tracked in the POA&M and addressed within 90 days to maintain compliance."

### Significant Gaps
> "This [Moderate/High]-impact system has significant security gaps requiring prompt remediation. We identified [X] findings including [Y] high-priority items affecting NIST controls [list key controls]. These gaps could impact the system's ATO status if not addressed. We recommend immediate POA&M updates with 30-day remediation targets for high-priority items and executive sponsorship to ensure timely resolution."

### Critical Gaps
> "**ATTENTION REQUIRED**: This [Moderate/High]-impact system has critical security vulnerabilities that pose immediate risk to [data type: CUI/PII/mission data]. We identified [X] findings including [Y] critical items requiring immediate action. These issues could result in [data breach/unauthorized access/system compromise] and jeopardize the system's Authorization to Operate. Recommend limiting system exposure and beginning remediation within 24-48 hours. Escalation to the Authorizing Official and CISO is advised."

---

## Impact Level Explanations

Use these to explain system categorization to non-technical leadership:

### Low Impact
> "A Low-impact system is one where the loss of confidentiality, integrity, or availability would have a limited adverse effect on organizational operations, assets, or individuals. This typically applies to systems with public information or limited internal functions."

### Moderate Impact
> "A Moderate-impact system is one where security compromise would have a serious adverse effect on operations, assets, or individuals. This includes most systems handling Controlled Unclassified Information (CUI), personally identifiable information (PII), or important business functions. Most LANL business systems fall into this category."

### High Impact
> "A High-impact system is one where security compromise would have a severe or catastrophic effect on operations, national security, or individuals. This includes systems handling highly sensitive data, critical infrastructure controls, or information that could cause exceptionally grave damage if compromised."

---

## Finding Priority Explanations

### P1 - Critical (Immediate Action)

**For Federal Leadership:**
> "P1 findings represent vulnerabilities that could be actively exploited to compromise system security, potentially resulting in unauthorized access to sensitive data, system takeover, or service disruption. These require immediate attention—ideally within 24-48 hours—and may warrant temporary system access restrictions until resolved. P1 issues typically represent failures in fundamental security controls and could trigger incident response procedures if exploited."

**Example P1 findings:**
- Authentication bypass allowing unauthorized system access
- Unpatched critical vulnerability with known exploit
- Hardcoded credentials for production databases
- Missing encryption on CUI/PII data at rest
- Remote code execution vulnerability

### P2 - High (30-Day Remediation)

**For Federal Leadership:**
> "P2 findings represent significant security weaknesses that, while not immediately exploitable, could lead to unauthorized access or data exposure under certain conditions. These should be tracked in the Plan of Action and Milestones (POA&M) with 30-day remediation targets. P2 issues may be flagged during ATO reviews and could affect authorization decisions if not addressed."

**Example P2 findings:**
- Authorization gaps allowing access to other users' data
- Missing multi-factor authentication for privileged access
- Weak encryption algorithms (non-FIPS compliant)
- Insufficient audit logging for security events
- Session management weaknesses

### P3 - Medium (90-Day Remediation)

**For Federal Leadership:**
> "P3 findings represent security concerns that should be addressed as part of ongoing continuous monitoring activities. While these don't pose immediate risk, they represent deviations from security best practices or NIST control requirements. Track these in the POA&M with 90-day targets and address during normal development cycles."

**Example P3 findings:**
- Verbose error messages exposing technical details
- Missing input validation on some endpoints
- Incomplete security headers
- Password policy below NIST recommendations
- Minor CORS configuration issues

### P4 - Low (Backlog/Continuous Improvement)

**For Federal Leadership:**
> "P4 findings represent opportunities for security hardening and defense-in-depth improvements. These are minor issues or deviations from best practices that don't represent significant risk. Address these as capacity allows and during system upgrades. They do not typically affect ATO status."

**Example P4 findings:**
- Additional security headers recommended
- Code quality improvements for security
- Documentation updates
- Defense-in-depth enhancements

---

## NIST Control Finding Templates

### Access Control (AC) Findings

**AC-2 (Account Management) Gap:**
> "The system lacks automated account management controls required by AC-2. Specifically, [dormant account identification/periodic access review/account provisioning workflow] is not implemented. This could result in unauthorized access through stale accounts or excessive privileges. **Business Impact**: Former employees or contractors may retain access longer than appropriate, increasing insider threat risk."

**AC-3 (Access Enforcement) Gap:**
> "Access enforcement controls (AC-3) are incomplete. We identified [X] API endpoints/pages that lack proper authorization checks, potentially allowing users to access data outside their authorization. **Business Impact**: Users could view or modify information they shouldn't have access to, potentially exposing [CUI/PII/sensitive data] to unauthorized parties."

**AC-6 (Least Privilege) Gap:**
> "The system does not fully implement least privilege (AC-6). [Describe specific issue: broad admin roles, database access with elevated accounts, etc.]. **Business Impact**: If an account is compromised, attackers would have broader access than necessary, increasing the potential damage from a security incident."

### Audit (AU) Findings

**AU-2 (Audit Events) Gap:**
> "Audit logging does not capture all security-relevant events required by AU-2. Missing events include: [authentication failures/authorization decisions/privileged actions/data access]. **Business Impact**: Security incidents may go undetected, and forensic investigation capabilities are limited. This could delay incident response and affect our ability to demonstrate compliance during audits."

**AU-9 (Protection of Audit Information) Gap:**
> "Audit logs are not adequately protected per AU-9. [Logs accessible to application administrators/logs stored on same server as application/no log integrity verification]. **Business Impact**: An attacker or malicious insider could modify or delete logs to cover their tracks, undermining our ability to detect and investigate security incidents."

### Identification and Authentication (IA) Findings

**IA-2 (MFA) Gap:**
> "Multi-factor authentication is not implemented for [privileged access/remote access/CUI access] as required by IA-2(1). **Business Impact**: Compromised passwords alone could grant unauthorized system access. Given the prevalence of credential theft attacks, MFA is essential for protecting sensitive systems."

**IA-5 (Authenticator Management) Gap:**
> "Password policies do not meet federal requirements per IA-5. Current settings: [describe]. Required: [describe federal requirement]. **Business Impact**: Weak passwords are more susceptible to brute-force attacks and credential stuffing, increasing the risk of account compromise."

### System and Communications Protection (SC) Findings

**SC-13 (Cryptographic Protection/FIPS) Gap:**
> "The system uses non-FIPS validated cryptographic algorithms. Specifically, [MD5/SHA-1/DES/3DES] was found in [locations]. Federal systems processing [CUI/PII] must use FIPS 140-2/3 validated cryptography. **Business Impact**: This represents a compliance gap that could be flagged during ATO reviews. Additionally, deprecated algorithms provide weaker security protection for sensitive data."

**SC-28 (Protection at Rest) Gap:**
> "Sensitive data ([CUI/PII/credentials]) is not encrypted at rest as required by SC-28. Data found unencrypted in [database tables/configuration files/logs]. **Business Impact**: If the storage media is accessed by unauthorized parties (through breach, improper disposal, or insider threat), sensitive data would be exposed in readable form."

---

## Risk Communication Templates

### Data Breach Risk

> "This vulnerability could enable unauthorized access to [X records of CUI/PII/sensitive data]. Based on the data types involved, a breach could trigger [DOE incident reporting requirements/Privacy Act notification obligations/potential regulatory penalties]. The reputational impact to the Laboratory could be significant, particularly given [describe context if relevant]."

### Compliance Risk

> "This finding represents a gap in NIST SP 800-53 control [control ID]. Unresolved, this could affect the system's Authorization to Operate (ATO) and would likely be identified during security assessments. Recommend adding to POA&M with [priority level] and [timeline] remediation target."

### Operational Risk

> "This vulnerability could be exploited to [disrupt system availability/corrupt data integrity/gain unauthorized system control]. For a [mission-critical/business-essential] system, extended downtime or data corruption could impact [describe operational impact]."

---

## Positive Finding Templates

Always include positive findings to provide balance:

> "The security assessment identified several well-implemented controls demonstrating the team's security awareness:"

**Authentication:**
> "Strong authentication controls are in place, including [MFA/robust password policies/account lockout], aligning with NIST IA family requirements."

**Encryption:**
> "FIPS-validated encryption is properly implemented for [data at rest/data in transit], meeting SC-13 and SC-28 requirements."

**Audit Logging:**
> "Comprehensive audit logging captures security-relevant events with sufficient detail for incident investigation, satisfying AU-2 and AU-3 requirements."

**Access Control:**
> "Role-based access control is well-implemented with appropriate separation of duties, demonstrating strong AC-3 and AC-6 compliance."

**Secure Development:**
> "The codebase shows evidence of secure development practices including [parameterized queries/input validation/output encoding], reducing OWASP Top 10 risks."

---

## Remediation Timeline Language

| Priority | Federal Language |
|----------|------------------|
| P1 | "requires immediate attention and should be addressed before end of business; consider limiting system exposure until resolved" |
| P2 | "should be added to POA&M with 30-day remediation milestone; track progress weekly" |
| P3 | "should be added to POA&M with 90-day remediation milestone; address in next development cycle" |
| P4 | "can be addressed during normal maintenance activities or system upgrades; track as continuous improvement item" |

---

## POA&M Entry Template

```markdown
## POA&M Entry

**Weakness ID**: [Unique ID]
**Finding**: [Brief title]
**NIST Control**: [Control ID - Control Name]
**Priority**: [P1/P2/P3/P4]
**Status**: Open

**Description**:
[Detailed description of the finding]

**Risk Statement**:
[Impact if not remediated]

**Recommended Remediation**:
[Specific steps to resolve]

**Milestone Schedule**:
| Milestone | Target Date | Status |
|-----------|-------------|--------|
| Initial assessment | [Date] | Complete |
| Remediation plan approved | [Date] | |
| Implementation complete | [Date] | |
| Verification testing | [Date] | |

**Resources Required**:
- [Developer hours]
- [Security review]
- [Testing]

**Point of Contact**: [Name]
**Last Updated**: [Date]
```

---

## Closing Recommendations

### For Critical/High Findings
> "Given the [critical/high] priority findings identified, we recommend establishing a focused remediation effort with dedicated resources. Weekly progress reviews with the project lead and security team should continue until P1 items are resolved. Consider engaging the Authorizing Official if remediation timelines cannot be met, as these findings may affect ATO status."

### For Moderate Findings
> "The findings identified should be incorporated into the POA&M and tracked through standard continuous monitoring processes. Monthly progress reviews are appropriate. No immediate escalation is required, but timely remediation will ensure continued compliance and reduce risk exposure."

### For Low/Compliant
> "This system demonstrates strong security practices. Continue current continuous monitoring activities and address low-priority items during normal maintenance. Consider this assessment as a baseline for future reviews."

---

## Acronym Reference

| Acronym | Definition |
|---------|------------|
| ATO | Authorization to Operate |
| CUI | Controlled Unclassified Information |
| FIPS | Federal Information Processing Standard |
| NIST | National Institute of Standards and Technology |
| PII | Personally Identifiable Information |
| POA&M | Plan of Action and Milestones |
| SP | Special Publication |
| UCNI | Unclassified Controlled Nuclear Information |
