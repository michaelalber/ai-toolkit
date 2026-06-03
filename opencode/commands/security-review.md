---
description: OWASP security review. Pass a path or leave empty for full project.
agent: plan
subtask: true
---

Use the security-review skill matching the project's stack (dotnet / python / php / rust / react).
For federal / gov / DOE / NIST / FIPS / CUI contexts, run the shared `security-review-federal` overlay after the base review.
Scope: $ARGUMENTS (defaults to full project if empty).
Output a manager-friendly summary with: critical findings, medium findings, recommendation table.
