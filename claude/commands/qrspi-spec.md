---
description: Start the QRSPI Spec phase -- a Design Brain-Dump the human redirects ("brain surgery"), then a vertically-sliced Structure Outline. Use for "/qrspi-spec <feature>". Reads research.md and writes spec.md. Distinct from the deprecated /rpi-plan.
allowed-tools: Bash(ls:*), Bash(date:*), Read
---

<live_state>
Today: !`date +%Y-%m-%d`
QRSPI feature folders and their artifacts:
!`for d in thoughts/shared/qrspi/*/; do echo "$d"; ls -1 "$d" 2>/dev/null | sed 's/^/  - /'; done 2>/dev/null || echo "(none yet)"`
</live_state>

Run the QRSPI **Spec** phase for: $ARGUMENTS

Use the `qrspi-orchestrator` agent (it loads the `qrspi-spec` skill). Locate the feature folder
above and read its `research.md` (status `complete`) plus the answered `questions.md`. If no
`research.md` exists, STOP and tell me to run `/qrspi-research` first -- do not design from memory.

Write the ~200-line **Design Brain-Dump** (current state / desired end state / design decisions) to
`thoughts/shared/qrspi/<feature-folder>/spec.md` with `status: draft`, `design_approved: false`,
then **STOP and present it**. Do NOT write the Structure Outline yet. When I redirect the
architecture, revise the Brain-Dump and re-present; loop until I approve (`design_approved: true`).

Only then add the **Structure Outline**: type/function signatures and VERTICAL slices (mock-API ->
front-end -> database, one checkpoint per slice -- never horizontal layers). Set
`status: ready-for-review` and tell me to review/approve before `/qrspi-plan`.
