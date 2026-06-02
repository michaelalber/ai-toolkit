---
description: Start the QRSPI Plan phase (convert an approved spec.md into a mechanically executable, vertically sliced plan.md). Usage: /qrspi-plan <feature>
agent: qrspi-orchestrator
subtask: true
---

Run the QRSPI **Plan** phase for: $ARGUMENTS

Load the `qrspi-plan` skill. Locate the feature folder under `thoughts/shared/qrspi/` and read its
`spec.md`. If no `spec.md` exists, STOP and tell me to run `/qrspi-spec` first -- do not plan from
memory. If `spec.md` exists but its status is only `ready-for-review`, STOP and ask me to approve
the design before planning.

Carry the spec's vertical slices forward as the phase skeleton. **RE-SLICE GATE:** if any phase
would complete a whole horizontal layer (all models, then all services, then all UI), STOP and
re-slice into end-to-end increments before writing -- never write a horizontal plan.

Write `plan.md` to `thoughts/shared/qrspi/<feature-folder>/plan.md` with `status: ready-for-review`.
Each phase must have exact file paths, a failing-test step (RED) before the code step (GREEN), an
automated verification command, and a rollback line; include a "What we're NOT doing" list and a
rollback plan. Then tell me to review/approve before `/qrspi-implement`.
