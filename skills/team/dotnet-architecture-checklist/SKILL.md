---
name: dotnet-architecture-checklist
audience: team
description: >
  Grades an existing .NET solution against the style it actually uses — controller-based
  layered/N-tier Web API OR vertical-slice CQRS (FreeMediator/Mapster)/Blazor — detecting
  framework, hosting model, and style FIRST (a layered API is not penalized for not being
  vertical-slice), then checking architectural coherence, controller/handler discipline, EF Core
  lifetimes, framework health, and config/secrets hygiene with file:line evidence. Use to review
  or grade a .NET solution. Not for Socratic critique (architecture-review), security audits
  (dotnet-security-review), or new test-first code (tdd).
---

# .NET / Blazor Architecture Checklist

> "A checklist cannot fly a plane, but a pilot cannot fly safely without one."
> — Atul Gawande

## Core Architectural Values

Shared across the `dotnet` / `python` / `php` / `rust` architecture checklists — same values, language-specific checks.

| # | Value | What it means |
|---|-------|---------------|
| 1 | **Detect before judge** | Determine version/framework/structure before applying any item; context decides what is idiomatic. |
| 2 | **Evidence over opinion** | Every finding cites `file:line` and the offending pattern. "Handlers are coupled" is not a finding; "`OrderHandler.cs:12` inherits `BaseCrudHandler<T>`" is. |
| 3 | **Feature cohesion** | Organized by business capability (feature folders), not technical layer. Cross-feature imports are a violation. |
| 4 | **Dependencies point inward** | Domain logic does not depend on infrastructure; entities do not leak across API boundaries (anti-corruption layers). |
| 5 | **Explicit error handling** | Failures handled at the right layer (pipeline behaviors); no silent swallowing; errors carry diagnostic context. |
| 6 | **Config & secrets hygiene** | No hardcoded secrets; configuration via `IOptions<T>`; no secrets in WASM bundles. |
| 7 | **Version awareness** | Recommendations are gated to the detected `<TargetFramework>`; never suggest an API absent from that version. |
| 8 | **Tests gate change** | Untested code is a finding; high-risk handlers without tests are prioritized. |
| 9 | **Graded, actionable output** | A letter grade (A–F) from counted findings, plus prioritized, version-correct recommendations. |

## Workflow

Shared skeleton: `DETECT → SCAN → REPORT → RECOMMEND`.

```
DETECT     Target framework (grep <TargetFramework> in all .csproj; global.json/Directory.Build.props),
           hosting model (Program.cs render modes: Server/WASM/Auto; or controller Web API), and —
           CRITICAL — the ARCHITECTURE STYLE: layered/N-tier controllers vs. vertical-slice CQRS vs.
           mixed (see references/layered-ntier.md for the style-detection grep). Then CQRS library
           (FreeMediator vs MediatR), Mapster, and Telerik usage. The detected style selects which
           checklist branch is authoritative. If the framework or style is unclear, ask — never assume
           .NET 10 or vertical-slice.

SCAN       Run the checklist branch for the DETECTED style — the Vertical-Slice/CQRS branch (table below)
           OR the Layered/N-tier Controller branch (references/layered-ntier.md) — section by section,
           cross-referencing references/red-flags.md. Gather evidence with grep and dotnet build/analyzers.
           Every violation becomes a finding with file:line and a severity (critical/high/medium/low).

REPORT     Emit the graded report (Output Template). Grade = function of counted findings.

RECOMMEND  Prioritize: critical → quick wins → modernization. Version-gate every recommendation; provide
           upgrade paths for EOL frameworks (references/framework-detection.md).
```

## .NET Checklist (language-specific)

**Branch by detected style.** Items 1–2 are style-specific — apply the row matching the
project. Items 3–9 apply to both styles (item 3 only when a mediator is present).

| # | Check | Severity |
|---|-------|----------|
| 1 | **Architectural coherence** — the project follows its OWN chosen style consistently: *vertical-slice* → features by capability, no cross-feature imports; *layered/N-tier* → clean layer boundaries (Controllers → Services → Data), dependencies point inward, no layer-skipping. The finding is **incoherence or a leaky boundary, never the choice of style.** | Critical |
| 2 | **Controller / handler discipline** — *vertical-slice* → each handler is a `sealed` standalone `IRequestHandler<TReq,TRes>`, no base handlers, thin endpoints that only `mediator.Send()`. *layered* → thin controllers (`[ApiController]`/`ControllerBase`), no business logic or EF queries in actions, delegate to a service layer; DTOs at the boundary, no entity leakage. (Full layered branch: references/layered-ntier.md) | Critical |
| 3 | **Mediator pipeline (CQRS projects only)** — FreeMediator preferred (MediatR flagged for migration); validation/logging/exception/transaction behaviors registered in order. *Skip for layered projects — do not flag the absence of a mediator.* | Critical |
| 4 | **EF Core lifetime** — DbContext scoped to the hosting model (singleton = Critical in Blazor Server); async all the way; no N+1 | Critical |
| 5 | **Framework health** — EOL frameworks (.NET Core 3.1, 5, 7) flagged Critical; .NET Framework 4.x gets an upgrade-path assessment | Critical |
| 6 | **Mapster discipline (when detected)** — `TypeAdapterConfig` configured at startup; queries use `ProjectToType<>()` not `ToList().Adapt()` | High |
| 7 | **Shared kernel** — official shared packages, version consistency, no duplicate entity definitions | High |
| 8 | **Config & secrets** — `IOptions<T>`/`IOptionsSnapshot<T>`; no hardcoded secrets; WASM bundles secret-free | High |
| 9 | **Telerik (when detected)** — Grid `Data` on large datasets paged/virtualized; component version alignment | High |

Layered/N-tier controller branch: [layered & n-tier](references/layered-ntier.md) · CQRS patterns: [cqrs patterns](references/cqrs-patterns.md) · framework upgrade paths: [framework detection](references/framework-detection.md) · anti-patterns: [red flags](references/red-flags.md). Full section-by-section list: [review checklist](references/review-checklist.md).

## State Block

```
<arch-checklist-state>
language: dotnet
mode: DETECT | SCAN | REPORT | RECOMMEND | COMPLETE
architecture_style: layered-controllers | vertical-slice-cqrs | mixed
detected: [target_framework | hosting_model | cqrs_lib | mapster:y/n | telerik:y/n | tests:y/n]
issues_found: [critical:N high:N medium:N low:N]
last_action: [what was just done]
next_action: [what should happen next]
</arch-checklist-state>
```

## Output Template

Shared across all four architecture checklists.

```markdown
## Architecture Checklist: [solution] (.NET)
**Framework**: [version] | **Style**: [Layered-Controllers/Vertical-Slice-CQRS/Mixed] | **Hosting**: [Server/WASM/Auto/Web API] | **CQRS**: [FreeMediator/MediatR/None] | **Tests**: [yes/no]

| Section | Pass | Fail | Warn |
|---------|------|------|------|
| Coherence / Controllers-Handlers / Pipeline / EF / Framework / Config / Telerik | … | … | … |

### Grade: [A–F]
Grading: **A** 0 crit/0 high/≤3 med · **B** 0 crit/≤2 high · **C** 0 crit, gaps in one area ·
**D** 1+ crit · **F** fundamental problems (EOL framework, singleton DbContext, missing auth; *vertical-slice:*
base-handler hierarchy; *layered:* business logic + EF queries in controllers). Grade against the detected
style — a coherent layered controller API with clean boundaries is an A.

| Severity | Location | Finding | Recommendation |
|----------|----------|---------|----------------|
| CRITICAL | file:line | [pattern] | [version-gated fix] |

**Quick wins**: [low-effort, high-impact] · **Modernization**: [larger items with effort estimate]
```

## AI Discipline Rules

- **Detect framework, hosting model, AND architecture style first.** Recommending Interactive Auto to a .NET 6 project, Server patterns to a WASM app, or vertical-slice/CQRS to a layered controller API produces invalid findings. The style decides which branch is authoritative.
- **Grade against the project's own style — never penalize the choice of style.** A coherent layered controller API is an A, not a C "because it isn't vertical slice." The violations are incoherence and leaky boundaries (business logic in controllers, layer-skipping, entity leakage), not the absence of a mediator.
- **Apply the right discipline check per style.** Vertical-slice: a base-handler hierarchy (`grep -r "class.*Handler.*:.*Base"`) is the critical structural problem to report first. Layered: business logic or EF queries inside controller actions (`grep -rA10 "ActionResult" --include="*Controller.cs"`) is the equivalent critical finding.
- **Never recommend a cross-style rewrite as a checklist finding.** Do not tell a layered project to adopt CQRS, or a vertical-slice project to adopt repositories/layers. Flag any style change as a separate, optional migration with an effort estimate.
- **Architecture, not security.** Vulnerability findings belong to `dotnet-security-review` — note them and route there.

## Integration with Other Skills

- **`architecture-review`** — When the grade is D/F, escalate to the Socratic critic: this checklist finds _what_ is wrong; `architecture-review` builds _why_.
- **`dotnet-security-review`** — Companion for the security dimension (OWASP, Telerik, deserialization).
- **`dotnet-vertical-slice`** — Correct-pattern reference when a vertical-slice/CQRS project flags structural violations.
- **`dotnet-controller-api-scaffolder`** — Correct-pattern reference when a layered controller API flags structural violations (fat controllers, entity leakage, inconsistent conventions).
- **`ef-migration-manager`** — For EF Core lifetime/migration findings.
- **`legacy-migration-analyzer`** — When EOL/.NET Framework is detected, for a phased upgrade plan.
- **`tdd`** — Methodology for adding tests the checklist flags as missing.
- **`python` / `php` / `rust`-architecture-checklist** — Sibling skills sharing this exact Core Values + workflow + output.
