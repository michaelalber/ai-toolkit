---
description: Prime session context from git state, ADRs, and open work.
allowed-tools: Bash(git log:*), Bash(git diff:*), Bash(git status:*), Read
---

<repo_state>
!`git log --oneline -10`
!`git status --short`
!`git diff --stat HEAD~1 2>/dev/null`
</repo_state>

Use the context-builder-agent.
Summarize: recent changes, current branch state, any ADRs relevant to active work.
Output a session brief — what was done, what's in progress, what's next.
