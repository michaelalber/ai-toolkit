---
description: Code review of staged or branch changes. Injects git diff before reviewing.
agent: plan
subtask: true
---

<changes>
!`git diff --stat HEAD~1 2>/dev/null || git diff --staged --stat`
!`git diff HEAD~1 2>/dev/null || git diff --staged`
</changes>

Use the code-review-agent on the changes above.
Focus on: correctness, security, patterns (vertical slice / CQRS conformance), test coverage gaps.
Output: blocking issues first, then suggestions, then nits.
