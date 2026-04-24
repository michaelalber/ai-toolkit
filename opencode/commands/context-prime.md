---
description: Prime session context from git state and recent work.
agent: plan
subtask: true
---

<repo_state>
!`git log --oneline -10`
!`git status --short`
!`git diff --stat HEAD~1 2>/dev/null`
</repo_state>

Use the context-builder-agent.
Summarize: recent changes, current branch state, any ADRs relevant to active work.
Output a session brief — what was done, what's in progress, what's next.
