---
description: Start the QRSPI Questions phase for a feature. Usage: /qrspi-questions <feature>
agent: qrspi-orchestrator
subtask: true
---

Run the QRSPI **Questions** phase for: $ARGUMENTS

Load the `qrspi-questions` skill. Surface every unknown across all relevant areas as targeted,
answerable questions; write `thoughts/shared/qrspi/<today>-<feature-slug>/questions.md` with
status `awaiting-answers`; then STOP and tell me to answer the questions inline before running
`/qrspi-research`.

Do not research the codebase and do not design anything in this phase — only ask.
