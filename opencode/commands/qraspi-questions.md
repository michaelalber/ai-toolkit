---
description: Start the QRASPI Questions phase for a brand-NEW system. Usage: /qraspi-questions <project>
agent: qraspi-orchestrator
subtask: true
---

Run the QRASPI **Questions** phase for the new system: $ARGUMENTS

Load the `qraspi-questions` skill. Surface every unknown across all SIX greenfield categories —
functional scope · quality attributes (the -ilities) · integration / external systems · compliance
/ regulatory · deployment / runtime target · data & domain model — as targeted, answerable
questions; enumerate a question for every category whether or not I named it. Write
`thoughts/shared/qraspi/<today>-<project-slug>/questions.md` with status `awaiting-answers`; then
STOP and tell me to answer the questions inline before running `/qraspi-research`.

Do not research, do not pick a stack, and do not architect anything in this phase — only ask. This
is for a NEW system; for adding a feature to an existing codebase, use `/qrspi-questions` instead.
