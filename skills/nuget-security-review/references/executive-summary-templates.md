# Executive Summary Templates

Guidelines for writing manager-friendly summaries that communicate technical package issues in business terms.

## Core Principles

1. **Lead with impact, not technical details**
2. **Quantify the risk** (number of issues, severity breakdown)
3. **Recommend specific timelines**
4. **Avoid acronyms and jargon**

## Updates Section Templates

### All Packages Current
> "All project dependencies are up-to-date. No action is required at this time. We recommend continuing regular quarterly dependency reviews to maintain this status."

### Minor Updates Only (Low Risk)
> "This solution has [X] packages with available updates, all of which are minor improvements or bug fixes. These updates pose minimal risk and can be included in regular maintenance cycles. No urgent action is required."

### Mixed Updates (Medium Risk)
> "We identified [X] packages requiring updates. While most are routine maintenance, [Y] packages are significantly behind current versions, which could cause compatibility issues with newer tools and libraries. We recommend scheduling these updates within the next [timeframe] to prevent accumulating technical debt."

### Major Updates Needed (Higher Risk)
> "This solution has [X] packages that are [Y] or more major versions behind current releases. Delaying these updates increases the risk of compatibility problems, makes future updates more difficult, and may leave the application without access to important improvements. We recommend prioritizing these updates in the upcoming development cycle."

### End-of-Life/Deprecated Packages
> "We found [X] packages that are no longer maintained or have been deprecated by their authors. Continuing to use unsupported packages creates long-term risk as security issues will not be patched. We recommend planning replacements for these packages within [timeframe]."

## Security Section Templates

### No Vulnerabilities
> "No known security vulnerabilities were detected in the project dependencies. We recommend maintaining regular security scanning to preserve this status."

### Low Severity Only
> "We identified [X] low-severity security advisories affecting project dependencies. These represent minimal risk under normal operating conditions and can be addressed during scheduled maintenance. No immediate action is required."

### Moderate Severity Present
> "This review identified [X] security vulnerabilities, including [Y] moderate-severity issues. Moderate vulnerabilities typically require specific conditions to exploit but should be addressed promptly to maintain security compliance. We recommend remediating these within [2 weeks/next sprint]."

### High Severity Present
> "We found [X] security vulnerabilities, including [Y] high-severity issues that could result in [data exposure/service disruption/unauthorized access]. These vulnerabilities should be addressed as a priority within the next [1 week]. Specific remediation steps are provided below."

### Critical Severity Present
> "**URGENT**: This review identified [X] critical security vulnerabilities requiring immediate attention. Critical vulnerabilities can be exploited remotely and may result in complete system compromise, data breach, or service outage. Remediation should begin within 24-48 hours. The development team should treat this as a priority incident."

## Per-Package Explanation Templates

### Update Explanations

**Performance improvement**:
> "This update includes optimizations that improve application speed and reduce resource usage. Updating ensures the application performs efficiently."

**Bug fixes**:
> "This version fixes known issues that could cause unexpected behavior. Updating improves application stability and reliability."

**Compatibility update**:
> "This update maintains compatibility with other tools and libraries the application depends on. Delaying could cause integration issues."

**New features**:
> "This version adds new capabilities that may benefit future development. While not urgent, updating keeps the codebase modern."

**Deprecated version**:
> "The current version is no longer supported. Continuing to use it means no bug fixes or security patches will be available."

### Vulnerability Explanations

**Data exposure risk**:
> "This vulnerability could allow unauthorized parties to access sensitive information stored or processed by the application. If exploited, it may result in a data breach affecting customer or business data."

**Service disruption risk**:
> "This vulnerability could allow an attacker to crash the application or make it unavailable to users. This directly impacts business operations and user experience."

**Unauthorized access risk**:
> "This vulnerability could allow attackers to bypass security controls and access features or data they shouldn't have access to. This compromises the integrity of access controls."

**Remote code execution risk**:
> "This vulnerability could allow an attacker to run malicious programs on our systems. This represents the highest risk level as it could lead to complete system compromise."

**Denial of service risk**:
> "This vulnerability could be exploited to overwhelm the application with requests, making it unavailable to legitimate users."

## Severity Language Guide

| Technical Term | Manager-Friendly Alternative |
|----------------|------------------------------|
| RCE (Remote Code Execution) | "allows attackers to run malicious code on our systems" |
| SQL Injection | "allows attackers to access or modify database information" |
| XSS (Cross-Site Scripting) | "allows attackers to inject malicious content that users see" |
| Authentication Bypass | "allows unauthorized access without proper credentials" |
| Privilege Escalation | "allows attackers to gain additional access rights" |
| DoS (Denial of Service) | "allows attackers to make the application unavailable" |
| Information Disclosure | "exposes sensitive information to unauthorized parties" |
| Deserialization | "allows attackers to manipulate data the application processes" |
| SSRF | "allows attackers to make the server access internal resources" |
| Path Traversal | "allows attackers to access files outside intended directories" |

## Timeline Recommendations

| Severity | Recommended Timeline | Wording |
|----------|---------------------|---------|
| Critical | 24-48 hours | "requires immediate attention" |
| High | 1 week | "should be addressed this week" |
| Moderate | 2 weeks | "should be addressed within two weeks" |
| Low | Next maintenance cycle | "can be addressed during scheduled maintenance" |
| Updates (major) | 1-2 sprints | "recommend scheduling in upcoming development cycle" |
| Updates (minor) | Maintenance window | "can be included in regular maintenance" |
