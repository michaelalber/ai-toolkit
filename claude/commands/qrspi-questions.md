---
description: Start the QRSPI Questions phase -- surface open technical questions for a feature before any research or design. Use for "/qrspi-questions <feature>". Writes questions.md to a per-feature folder and STOPS for human answers.
allowed-tools: Bash(ls:*), Bash(date:*), Read
---

<live_state>
Today: !`date +%Y-%m-%d`
Existing QRSPI feature folders:
!`ls -1 thoughts/shared/qrspi/ 2>/dev/null || echo "(none yet)"`
</live_state>

Run the QRSPI **Questions** phase for: $ARGUMENTS

Use the `qrspi-orchestrator` agent (it loads the `qrspi-questions` skill). Surface every unknown
across all relevant areas as targeted, answerable questions; write
`thoughts/shared/qrspi/<today>-<feature-slug>/questions.md` with status `awaiting-answers`; then
STOP and tell me to answer the questions inline before running `/qrspi-research`.

Do not research the codebase and do not design anything in this phase — only ask.
