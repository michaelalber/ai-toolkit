---
description: Start the QRSPI Spec phase (Design Brain-Dump + vertically-sliced Structure Outline, with a human "brain surgery" gate). Usage: /qrspi-spec <feature>
agent: qrspi-orchestrator
subtask: true
---

Run the QRSPI **Spec** phase for: $ARGUMENTS

Load the `qrspi-spec` skill. Locate the feature folder under `thoughts/shared/qrspi/` and read its
`research.md` (status `complete`) plus the answered `questions.md`. If no `research.md` exists, STOP
and tell me to run `/qrspi-research` first -- do not design from memory.

Write the ~200-line **Design Brain-Dump** (current state / desired end state / design decisions) to
`thoughts/shared/qrspi/<feature-folder>/spec.md` with `status: draft`, `design_approved: false`,
then **STOP and present it**. Do NOT write the Structure Outline yet. When I redirect the
architecture, revise the Brain-Dump and re-present; loop until I approve (`design_approved: true`).

Only then add the **Structure Outline**: type/function signatures and VERTICAL slices (mock-API ->
front-end -> database, one checkpoint per slice -- never horizontal layers). Set
`status: ready-for-review` and tell me to review/approve before `/qrspi-plan`.
