---
description: Reviews staged or branch changes for correctness, security, performance, and style, injecting live git diff before analysis. Use when reviewing changes before commit, auditing a branch before merging, or asked to review pending code changes.
allowed-tools: Bash(git diff:*), Bash(git log:*), Read
---

<changes>
!`git diff --stat HEAD~1 2>/dev/null || git diff --staged --stat`
!`git diff HEAD~1 2>/dev/null || git diff --staged`
</changes>

Use the code-review-agent on the changes above.
Focus on: correctness, security, patterns (vertical slice / CQRS conformance), test coverage gaps.
Output: blocking issues first, then suggestions, then nits.
