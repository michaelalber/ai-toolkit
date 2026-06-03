# Layered / N-Tier Controller Branch

> Use this branch when DETECT classifies the project as **controller-based layered/N-tier**
> (the dominant production .NET Web API style) rather than vertical-slice CQRS. The goal is
> to grade the project against the style it actually uses. A coherent layered API with clean
> boundaries earns an A — "it isn't vertical slice" is **not** a finding.

## Style detection

Run from the solution root. The result picks the authoritative checklist branch.

```bash
# Controllers present?
grep -rlE "class \w+Controller\s*:\s*(ControllerBase|Controller|\w*ControllerBase)" --include="*.cs" . | wc -l

# Mediator in controllers? (signals vertical-slice/CQRS)
grep -rlE "_mediator\.Send|ISender|IMediator" --include="*Controller.cs" . | wc -l

# Service-layer injection in controllers? (signals layered/N-tier)
grep -rlE "I\w+Service\b" --include="*Controller.cs" . | wc -l

# Feature folders vs. layer folders
find . -type d \( -name Controllers -o -name Services -o -name Repositories -o -name Models -o -name DTOs \) | wc -l   # layer folders
find . -type d -name Features | wc -l                                                                                  # feature folders
```

Classify:

| Signal | Style |
|--------|-------|
| Controllers inject services / repositories; layer folders dominate | **layered-controllers** → this branch |
| Controllers only `mediator.Send()`; feature folders; handlers per feature | **vertical-slice-cqrs** → SKILL.md table |
| Both patterns present in similar measure | **mixed** → report the split, grade each area in its own style, recommend convergence as an optional migration |

## Layered checklist

| # | Check | Severity | Evidence grep |
|---|-------|----------|---------------|
| 1 | **Layer boundaries respected** — Controllers → Services → Data; UI/API never reaches the DbContext directly; no layer-skipping | Critical | `grep -rE "DbContext|_context\." --include="*Controller.cs"` (hits = controllers hitting data directly) |
| 2 | **Thin controllers** — actions bind/validate/delegate/map only; no business rules, loops of EF queries, or transaction orchestration in actions | Critical | `grep -rA12 "ActionResult\|IActionResult" --include="*Controller.cs"` then read for logic |
| 3 | **DTOs at the boundary** — requests/responses are DTOs; entities are not bound from the request body or returned | Critical | `grep -rE "Task<.*Entity>\|public.*Entity .*\(\[FromBody\]" --include="*Controller.cs"` |
| 4 | **`[ApiController]` + `ControllerBase`** — API controllers use `[ApiController]` and derive from `ControllerBase`, not `Controller` | High | `grep -rE "class \w+Controller\s*:\s*Controller\b" --include="*.cs"` (hits = MVC base on an API) |
| 5 | **Service layer is cohesive** — services own business logic, are interface-backed, registered with correct DI lifetime; no god-services | High | `grep -rE "AddScoped<I\w+Service" Program.cs Startup.cs` |
| 6 | **Consistent validation** — one approach (DataAnnotations OR FluentValidation) applied uniformly; no unvalidated input reaching services | High | `grep -rE "\[Required\]\|AbstractValidator<" --include="*.cs"` |
| 7 | **Consistent error handling** — global exception handler / `ProblemDetails`; not ad-hoc `try/catch` returning raw 500s per action | High | `grep -rc "catch" --include="*Controller.cs"` (many = per-action handling) |
| 8 | **Consistent response shape** — all actions return the same contract (raw DTO+`ActionResult<T>` OR a single envelope type), not a mix | Medium | compare `return Ok(` vs `ApiResponse<` usage |
| 9 | **Async + CancellationToken** — actions and service calls are async; `CancellationToken` propagated; no `.Result`/`.Wait()` | High | `grep -rE "\.Result\b\|\.Wait\(\)" --include="*.cs"` |
| 10 | **Repository discipline (when present)** — if a repository/UoW layer exists, it is consistent and not leaking `IQueryable` of entities to controllers | Medium | `grep -rE "IQueryable<" --include="*Controller.cs"` |

Items 4–9 of the SKILL.md table (EF lifetime, framework health, Mapster, shared kernel,
config/secrets, Telerik) apply to layered projects unchanged. **Skip** the mediator-pipeline
item — do not flag the absence of a mediator in a layered project.

## What is NOT a finding in a layered project

- Absence of CQRS, FreeMediator, or a vertical-slice folder structure
- Controllers calling a service layer instead of `mediator.Send()`
- Layer folders (`Controllers/`, `Services/`, `Models/`) instead of feature folders
- A repository pattern, when used consistently

Flag a move to vertical-slice/CQRS only as an **optional** modernization with an effort
estimate — never as a graded violation.

## Layered red flags (in addition to references/red-flags.md)

```bash
# Business logic in controllers (the #1 layered smell)
grep -rA15 "public.*ActionResult" --include="*Controller.cs" . | grep -iE "_context|SaveChanges|\.Where\(|foreach|new .*Entity"

# Entities bound directly from the request (over-posting risk)
grep -rE "\(\[FromBody\] \w+Entity|\(\[FromBody\] \w+Model" --include="*Controller.cs"

# Fat controller (too many dependencies => doing too much)
grep -rE "public \w+Controller\(" --include="*Controller.cs"   # inspect constructor arity

# Synchronous data access
grep -rE "\.ToList\(\)\b\|\.First\(\)\b\|\.Single\(\)\b" --include="*Controller.cs"

# Mixed response shapes (envelope in some actions, raw in others)
grep -rE "return Ok\(|ApiResponse<" --include="*Controller.cs" | sort | uniq -c
```
