---
description: Run a TDD cycle. Injects live test output before implementing.
agent: build
subtask: true
---

<current_test_state>
!`dotnet test --no-build 2>&1 | tail -50`
</current_test_state>

Use the tdd-cycle skill. The test output above is the current state.
Make failing tests pass. Do not modify test files. Run tests after each change.
Stop when all tests pass and no regressions are introduced.
