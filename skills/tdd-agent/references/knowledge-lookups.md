# Knowledge-Base Lookups & Test Desiderata

## Knowledge Base Lookups

Use `search_knowledge` (grounded-code-mcp) to ground decisions in authoritative references.

| Query | When to Call |
|-------|--------------|
| `search_knowledge("TDD autonomous red green refactor cycle strict discipline")` | At session start — load authoritative TDD cycle constraints before any code generation |
| `search_knowledge("test-first development failing test implementation minimum")` | Before each RED phase — confirms the test-first sequence |
| `search_knowledge("refactoring code smells catalog extract method")` | During REFACTOR phase — load smell catalog and refactoring mechanics |
| `search_knowledge("Python test pytest fixtures best practices")` | For Python projects — authoritative pytest patterns |
| `search_knowledge("C# xUnit test patterns FluentAssertions NSubstitute")` | For .NET projects — authoritative xUnit/FluentAssertions patterns |
| `search_knowledge("unit test naming conventions behavior specification")` | When naming tests — confirms behavioral naming standards |

**Protocol:** Search before each phase transition (RED→GREEN→REFACTOR). Cite the source path in phase logs.

## Kent Beck's 12 Test Desiderata (Agent Focus)

| Property | Agent Responsibility |
|----------|---------------------|
| **Isolated** | Tests don't share state; verify no side effects |
| **Deterministic** | Same results every run; no flaky tests |
| **Specific** | Failures point to exact cause |
| **Automated** | No manual intervention required |
| **Predictive** | Passing tests = working code |
| **Fast** | Maintain quick feedback loop |
