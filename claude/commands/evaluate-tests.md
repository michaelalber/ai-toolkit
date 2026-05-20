---
description: Evaluates an existing test file or suite against Beck's behavioral and structure-insensitive criteria. Flags implementation-coupled, fragile, and theater tests and produces a prioritized rewrite list. Use when auditing inherited tests, checking AI-generated tests before merge, or preparing code for safe refactoring. Pass a file or directory path as the argument.
allowed-tools: Read, Glob, Bash(git log:*)
---

Use the evaluate-tests skill.
Target: $ARGUMENTS
