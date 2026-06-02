---
description: Start the QRASPI Questions phase -- surface open questions for a brand-NEW system across the six greenfield categories before any research or architecture. Use for "/qraspi-questions <project>". Writes questions.md to a per-project folder and STOPS for human answers. For an existing codebase use /qrspi-questions instead.
allowed-tools: Bash(ls:*), Bash(date:*), Read
---

<live_state>
Today: !`date +%Y-%m-%d`
Existing QRASPI project folders:
!`ls -1 thoughts/shared/qraspi/ 2>/dev/null || echo "(none yet)"`
</live_state>

Run the QRASPI **Questions** phase for the new system: $ARGUMENTS

Use the `qraspi-orchestrator` agent (it loads the `qraspi-questions` skill). Surface every unknown
across all SIX greenfield categories — functional scope · quality attributes (the -ilities) ·
integration / external systems · compliance / regulatory · deployment / runtime target · data &
domain model — as targeted, answerable questions; enumerate a question for every category whether
or not I named it. Write `thoughts/shared/qraspi/<today>-<project-slug>/questions.md` with status
`awaiting-answers`; then STOP and tell me to answer the questions inline before running
`/qraspi-research`.

Do not research, do not pick a stack, and do not architect anything in this phase — only ask. This
is for a NEW system; for adding a feature to an existing codebase, use `/qrspi-questions` instead.
