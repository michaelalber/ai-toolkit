---
description: Conducts an OWASP Top 10 security review of the current codebase or a specified path, identifying vulnerabilities and generating a prioritized findings report. Use when asked for a security review, security audit, or "check this for vulnerabilities".
allowed-tools: Read, Glob, Grep
---

Use the security-review skill matching the project's stack (dotnet / python / php / rust).
For federal / gov / DOE / NIST / FIPS / CUI / national-laboratory contexts, run the shared `security-review-federal` overlay after the base review.
Scope: $ARGUMENTS (defaults to full project if empty).
Output a manager-friendly summary with: critical findings, medium findings, recommendation table.
