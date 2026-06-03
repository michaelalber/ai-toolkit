---
name: dotnet-architecture-checklist
audience: team
description: >
  Checklist executor for .NET / Blazor architecture reviews using CQRS (FreeMediator/Mapster). Detects
  the target framework, hosting model, and pattern choices, then runs a systematic checklist covering
  vertical-slice compliance, handler isolation, EF Core lifetime, framework health, and config/secrets
  hygiene — producing a graded report with file:line evidence. Use to review or grade an existing .NET solution.
  Triggers on "review this .net project", "architecture checklist", "audit this solution", "evaluate blazor
  project", "review cqrs patterns", "check handlers", "grade this architecture", "shared kernel review".
  Do NOT use for a Socratic design critique — use architecture-review. Do NOT use for a security audit —
  use dotnet-security-review. Do NOT use to write new code test-first — use tdd.
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
           hosting model (Program.cs render modes: Server/WASM/Auto), CQRS library (FreeMediator vs
           MediatR), Mapster, and Telerik usage. If the framework is unknown, ask — never assume .NET 10.

SCAN       Run the .NET Checklist below section by section, cross-referencing references/red-flags.md.
           Gather evidence with grep and dotnet build/analyzers. Every violation becomes a finding with
           file:line and a severity (critical/high/medium/low).

REPORT     Emit the graded report (Output Template). Grade = function of counted findings.

RECOMMEND  Prioritize: critical → quick wins → modernization. Version-gate every recommendation; provide
           upgrade paths for EOL frameworks (references/framework-detection.md).
```

## .NET Checklist (language-specific)

| # | Check | Severity |
|---|-------|----------|
| 1 | **Vertical slice compliance** — features by capability; each folder holds command/query/handler/validator/DTO; no cross-feature imports | Critical |
| 2 | **Handler isolation** — each handler is a `sealed` standalone `IRequestHandler<TReq,TRes>`; no base handlers, no handler-to-handler calls, thin endpoints that only `mediator.Send()` | Critical |
| 3 | **FreeMediator pipeline** — FreeMediator preferred (MediatR flagged for migration); validation/logging/exception/transaction behaviors registered in order | Critical |
| 4 | **EF Core lifetime** — DbContext scoped to the hosting model (singleton = Critical in Blazor Server); async all the way; no N+1 | Critical |
| 5 | **Framework health** — EOL frameworks (.NET Core 3.1, 5, 7) flagged Critical; .NET Framework 4.x gets an upgrade-path assessment | Critical |
| 6 | **Mapster discipline** — `TypeAdapterConfig` configured at startup; queries use `ProjectToType<>()` not `ToList().Adapt()` | High |
| 7 | **Shared kernel** — official shared packages, version consistency, no duplicate entity definitions | High |
| 8 | **Config & secrets** — `IOptions<T>`/`IOptionsSnapshot<T>`; no hardcoded secrets; WASM bundles secret-free | High |
| 9 | **Telerik (when detected)** — Grid `Data` on large datasets paged/virtualized; component version alignment | High |

CQRS patterns: [cqrs patterns](references/cqrs-patterns.md) · framework upgrade paths: [framework detection](references/framework-detection.md) · anti-patterns: [red flags](references/red-flags.md). Full section-by-section list: [review checklist](references/review-checklist.md).

## State Block

```
<arch-checklist-state>
language: dotnet
mode: DETECT | SCAN | REPORT | RECOMMEND | COMPLETE
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
**Framework**: [version] | **Hosting**: [Server/WASM/Auto] | **CQRS**: [FreeMediator/MediatR/None] | **Tests**: [yes/no]

| Section | Pass | Fail | Warn |
|---------|------|------|------|
| Slice / Handlers / Pipeline / EF / Framework / Config / Telerik | … | … | … |

### Grade: [A–F]
Grading: **A** 0 crit/0 high/≤3 med · **B** 0 crit/≤2 high · **C** 0 crit, gaps in one area ·
**D** 1+ crit · **F** fundamental problems (EOL framework, singleton DbContext, base handlers, missing auth).

| Severity | Location | Finding | Recommendation |
|----------|----------|---------|----------------|
| CRITICAL | file:line | [pattern] | [version-gated fix] |

**Quick wins**: [low-effort, high-impact] · **Modernization**: [larger items with effort estimate]
```

## AI Discipline Rules

- **Detect framework and hosting model first.** Recommending Interactive Auto to a .NET 6 project, or Server patterns to a WASM app, produces invalid findings.
- **Check handler isolation before naming/structure.** A base-handler hierarchy (`grep -r "class.*Handler.*:.*Base"`) is a critical structural problem to report first.
- **Never mix architectural styles in recommendations.** If the codebase is vertical-slice CQRS, do not recommend repository/layered patterns; flag a style change as a separate migration with an effort estimate.
- **Architecture, not security.** Vulnerability findings belong to `dotnet-security-review` — note them and route there.

## Integration with Other Skills

- **`architecture-review`** — When the grade is D/F, escalate to the Socratic critic: this checklist finds _what_ is wrong; `architecture-review` builds _why_.
- **`dotnet-security-review`** — Companion for the security dimension (OWASP, Telerik, deserialization).
- **`dotnet-vertical-slice`** — Correct-pattern reference when the checklist flags structural violations.
- **`ef-migration-manager`** — For EF Core lifetime/migration findings.
- **`legacy-migration-analyzer`** — When EOL/.NET Framework is detected, for a phased upgrade plan.
- **`tdd`** — Methodology for adding tests the checklist flags as missing.
- **`python` / `php` / `rust`-architecture-checklist** — Sibling skills sharing this exact Core Values + workflow + output.
