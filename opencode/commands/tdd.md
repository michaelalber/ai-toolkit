---
description: Run a TDD cycle. Injects live test output before implementing.
agent: build
subtask: true
---

<current_test_state>
!`out=$(timeout 90 dotnet test --no-build -m:1 $ARGUMENTS 2>&1); rc=$?; printf '%s\n' "$out" | tail -50; [ "$rc" = 124 ] && echo "(TIMED OUT after 90s — snapshot is INCOMPLETE. Treat it as no data, not as a result. Re-run scoped: dotnet test --no-build -m:1 --filter <expr>)"; true`
</current_test_state>

Use the tdd skill. The test output above is the current state.
Make failing tests pass. Do not modify test files. Run tests after each change.
Stop when all tests pass and no regressions are introduced.

Always pass `-m:1` to `dotnet test`, and prefer a project path or `--filter`.
`-m:1` runs one test project at a time. Without it, a whole-solution run starts a
test host per project in parallel; on a large solution that can exhaust the
per-user process limit (`ulimit -u`), and `fork` then fails with "Resource
temporarily unavailable".

If you see that error, or a test command dies on a signal, the tests did not run.
That is neither a red baseline nor a green one — it is no data. Re-run scoped.
Never infer a cause from the word `Killed` alone: it names the signal, not the
sender. Check `journalctl -k | grep -i oom` before claiming an out-of-memory kill,
and read the `available` column of `free`, never `free`.
