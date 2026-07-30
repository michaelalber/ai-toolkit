# Fitness Functions — .NET (NetArchTest)

Tool: **NetArchTest.Rules** — express layer/namespace/dependency rules as xUnit tests so they run
under `dotnet test` and fail the build like any other test. For coupling *metrics* (Ca/Ce/I/A/D),
defer to `dependency-mapper`; NetArchTest gates *rules* (allowed/forbidden dependencies).

## 1. Minimal check

A test that asserts the Domain layer never depends on Infrastructure (enforces a Clean
Architecture ADR):

```csharp
using NetArchTest.Rules;
using Xunit;

public class ArchitectureFitnessTests
{
    // Gates ADR-0003: domain must not depend on infrastructure.
    [Fact]
    public void Domain_does_not_depend_on_Infrastructure()
    {
        var result = Types.InAssembly(typeof(Domain.Marker).Assembly)
            .That().ResideInNamespace("MyApp.Domain")
            .ShouldNot().HaveDependencyOn("MyApp.Infrastructure")
            .GetResult();

        Assert.True(result.IsSuccessful,
            "Domain depends on Infrastructure: " +
            string.Join(", ", result.FailingTypeNames ?? Array.Empty<string>()));
    }
}
```

Add the package to the test project: `dotnet add package NetArchTest.Rules`.

## 2. CI wiring (GitHub Actions)

The gate is just the existing test step — no separate runner needed. Keep architecture tests in
their own project (`tests/Architecture.Tests`) so they can be required independently if desired.

```yaml
# .github/workflows/ci.yml
  - name: Architecture fitness functions (gates ADR-0003)
    run: dotnet test tests/Architecture.Tests --no-build --configuration Release
```

A failing assertion exits non-zero → the job fails → merge is blocked by branch protection.

## 3. Prove it gates

1. Run `dotnet test tests/Architecture.Tests` → must PASS today.
2. Add a deliberate violation: in any `MyApp.Domain` type, add `using MyApp.Infrastructure;` and
   reference an infrastructure type. Re-run → the test must FAIL with the offending type listed.
3. Revert the violation. Commit only the green state.

## Other ready-made .NET fitness functions

- **Coverage threshold:** `coverlet` + `--threshold 80 --threshold-type line` fails under target.
- **No `*.Result`/`.Wait()` on async:** a Roslyn analyzer rule or a NetArchTest predicate over
  method bodies (see project conventions on async-all-the-way).
