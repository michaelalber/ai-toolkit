---
description: Audits existing tests in two modes — test-file quality (flags implementation-coupled, fragile, and theater tests against Beck's criteria, with a prioritized rewrite list) and TDD compliance (analyzes git commit history for test-first discipline, produces a 0–25 scorecard + anti-pattern findings). Use when auditing inherited tests, checking AI-generated tests before merge, preparing code for safe refactoring, or verifying TDD discipline. Pass a file or directory path as the argument.
allowed-tools: Read, Glob, Bash(git log:*)
---

Use the evaluate-tests skill.
Target: $ARGUMENTS
