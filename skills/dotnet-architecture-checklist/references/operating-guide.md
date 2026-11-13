# dotnet-architecture-checklist — operating guide

Depth relocated from SKILL.md; load it when the Workflow points here.

## .NET Checklist (language-specific)

**Branch by detected style.** Items 1–2 are style-specific — apply the row matching the
project. Items 3–9 apply to both styles (item 3 only when a mediator is present).

| # | Check | Severity |
|---|-------|----------|
| 1 | **Architectural coherence** — the project follows its OWN chosen style consistently: *vertical-slice* → features by capability, no cross-feature imports; *layered/N-tier* → clean layer boundaries (Controllers → Services → Data), dependencies point inward, no layer-skipping. The finding is **incoherence or a leaky boundary, never the choice of style.** | Critical |
| 2 | **Controller / handler discipline** — *vertical-slice* → each handler is a `sealed` standalone `IRequestHandler<TReq,TRes>`, no base handlers, thin endpoints that only `mediator.Send()`. *layered* → thin controllers (`[ApiController]`/`ControllerBase`), no business logic or EF queries in actions, delegate to a service layer; DTOs at the boundary, no entity leakage. (Full layered branch: references/layered-ntier.md) | Critical |
| 3 | **Mediator pipeline (CQRS projects only)** — FreeMediator preferred (MediatR flagged for migration); validation/logging/exception/transaction behaviors registered in order. *Skip for layered projects — do not flag the absence of a mediator.* | Critical |
| 4 | **EF Core lifetime** — DbContext scoped to the hosting model (singleton = Critical in Blazor Server); async all the way; no N+1 | Critical |
| 5 | **Framework health** — EOL frameworks (.NET Core 3.1, 5, 7, 9) flagged Critical; .NET Framework 4.x gets an upgrade-path assessment | Critical |
| 6 | **Mapster discipline (when detected)** — `TypeAdapterConfig` configured at startup; queries use `ProjectToType<>()` not `ToList().Adapt()` | High |
| 7 | **Shared kernel** — official shared packages, version consistency, no duplicate entity definitions | High |
| 8 | **Config & secrets** — `IOptions<T>`/`IOptionsSnapshot<T>`; no hardcoded secrets; WASM bundles secret-free | High |
| 9 | **Telerik (when detected)** — Grid `Data` on large datasets paged/virtualized; component version alignment | High |

Layered/N-tier controller branch: [layered & n-tier](references/layered-ntier.md) · CQRS patterns: [cqrs patterns](references/cqrs-patterns.md) · framework upgrade paths: [framework detection](references/framework-detection.md) · anti-patterns: [red flags](references/red-flags.md). Full section-by-section list + grounding query map: [review checklist](references/review-checklist.md).

## AI Discipline Rules

- **Detect framework, hosting model, AND architecture style first.** Recommending Interactive Auto to a .NET 6 project, Server patterns to a WASM app, or vertical-slice/CQRS to a layered controller API produces invalid findings. The style decides which branch is authoritative.
- **Grade against the project's own style — never penalize the choice of style.** A coherent layered controller API is an A, not a C "because it isn't vertical slice." The violations are incoherence and leaky boundaries (business logic in controllers, layer-skipping, entity leakage), not the absence of a mediator.
- **Apply the right discipline check per style.** Vertical-slice: a base-handler hierarchy (`grep -r "class.*Handler.*:.*Base"`) is the critical structural problem to report first. Layered: business logic or EF queries inside controller actions (`grep -rA10 "ActionResult" --include="*Controller.cs"`) is the equivalent critical finding.
- **Never recommend a cross-style rewrite as a checklist finding.** Do not tell a layered project to adopt CQRS, or a vertical-slice project to adopt repositories/layers. Flag any style change as a separate, optional migration with an effort estimate.
- **Architecture, not security.** Vulnerability findings belong to `dotnet-security-review` — note them and route there.
