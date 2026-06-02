---
description: Start the QRSPI Implement phase (execute an approved plan.md slice-by-slice with strict Red-Green-Refactor per slice). Requires plan.md status: approved; writes per-slice proof logs. Usage: /qrspi-implement <feature>
agent: qrspi-implement
subtask: false
---

Run the QRSPI **Implement** phase for: $ARGUMENTS

Load the `qrspi-implement` and `tdd` skills. Locate the feature folder under
`thoughts/shared/qrspi/` and read its `plan.md`. If no `plan.md` exists, STOP and tell me to run
`/qrspi-plan` first -- do not implement from memory. If `plan.md` status is only
`ready-for-review`, STOP and ask me to approve the plan before implementing.

Run the baseline test suite first; if it is red, STOP and report -- do not fix the baseline. Then
execute the plan's vertical slices **in order, one at a time**. For each slice run strict
Red-Green-Refactor: write the failing test and RUN it (must FAIL), write minimal code and RUN
build+tests (must PASS), refactor and RUN again (stays GREEN). Record the actual RED and GREEN
command output to `thoughts/shared/qrspi/<feature-folder>/implementation/slice-NN-{name}.md`, then
suggest a one-slice commit.

Test-first or STOP: production code before a failing test is a stop condition. Invention is a STOP:
anything not in the plan means re-run `/qrspi-plan`, do not improvise. Honor the per-slice context
budget -- at ~40% (or slice end) checkpoint to the slice log and tell me to start a fresh session for
the next slice.
