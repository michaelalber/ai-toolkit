---
description: Conducts an OWASP Top 10 security review of the current codebase or a specified path, identifying vulnerabilities and generating a prioritized findings report. Use when asked for a security review, security audit, or "check this for vulnerabilities".
allowed-tools: Read, Glob, Grep
---

Use the dotnet-security-review skill (or dotnet-security-review-federal for federal/LANL contexts).
Scope: $ARGUMENTS (defaults to full project if empty).
Output a manager-friendly summary with: critical findings, medium findings, recommendation table.
