# Archetype: .NET 10 / Blazor Server enterprise app (EF Core + vertical slice + CQRS)

A new multi-project .NET solution. This is the archetype the full six-phase workflow fits best -- the
Architecture phase carried real weight (DB choice, auth model, CQRS/mediator, migration strategy), and
the fitness functions are richest here. Per-stack templates matter most for this archetype.

## Stack it instantiates (from the ADRs)
.NET 10, Blazor Server, EF Core, FreeMediator (CQRS), xUnit. Confirm transport/auth/DB against the
accepted ADRs -- these are the path-dependent picks Architecture locked.

## Repo layer (the recipe)
- Layout: feature-folder vertical slices (NOT n-tier layers): `src/<App>/Features/<Feature>/`,
  `src/<App>/Infrastructure/`, `tests/<App>.Tests/`, a `.sln`.
- Entrypoint: one Blazor page -> command/query handler -> EF Core -> DB, end-to-end (the walking
  slice). One slice only.
- Health/smoke: an ASP.NET health check endpoint + an integration test hitting the slice through the
  handler against an in-memory or TestContainers DB.
- Observability hook: structured logging + the built-in health checks middleware.
- Secure-by-default: nullable reference types on, warnings as errors; no secrets in source (user
  secrets / env); parameterized EF queries only; auth per the ADR.

## Slice layer (delegate)
Invoke `dotnet-vertical-slice` (CQRS + FreeMediator, optional Telerik Blazor UI) for the one slice.
Use `ef-migration-manager` if the ADRs require an initial migration.

## Fitness gates typical here (wire via `fitness-functions`)
Richest set: NetArchTest layer-direction rules (UI never imports persistence directly), coverage
threshold, `dotnet format`/analyzer gate, dependency policy. The global `dotnet build` PostToolUse
hook is the local precedent. See `fitness-functions/references/dotnet.md`.

## CI-green command
`.github/workflows/ci.yml` running `dotnet build -warnaserror && dotnet test` (incl. the NetArchTest
fitness tests) -> exit 0. No hardware gate. `ci_green` is the captured exit status.
