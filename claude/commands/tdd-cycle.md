---
description: Runs a RED-GREEN-REFACTOR TDD cycle with live test output injected before each phase transition. Use when starting TDD, implementing a feature test-first, or asked to "run a TDD cycle" or "do TDD".
allowed-tools: Bash(dotnet test:*), Bash(dotnet build:*), Read, Edit, Write
---

<current_test_state>
!`dotnet test --no-build 2>&1 | tail -50`
</current_test_state>

Use the tdd-cycle skill. The test output above is the current state.
Make failing tests pass. Do not modify test files. Run tests after each change.
Stop when all tests pass and no regressions are introduced.
