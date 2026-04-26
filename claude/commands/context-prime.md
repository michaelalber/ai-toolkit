---
description: Primes session context by summarizing recent git changes, matching ADRs to current work, and surfacing open loops. Use when starting a new coding session, onboarding to a codebase, or asked to "prime context" or "catch me up".
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
