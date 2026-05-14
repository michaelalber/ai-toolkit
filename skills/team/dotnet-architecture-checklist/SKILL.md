---
name: dotnet-architecture-checklist
description: Checklist executor for .NET Blazor architecture reviews using CQRS patterns (FreeMediator/Mapster). Use when asked to review architecture, audit code quality, assess technical debt, evaluate Blazor projects, check for anti-patterns, review .NET solutions, validate FreeMediator/Mapster usage, run architecture checklist, or grade a .NET project. Triggers on phrases like "review this project", "architecture checklist", "audit this code", "check for issues", "evaluate this solution", "review CQRS patterns", "check handlers", "check framework version", "shared kernel review", "run checklist", "grade this architecture".
---

# .NET Blazor Architecture Checklist

> "Architecture is the decisions you wish you could get right early in a project, but that you are not necessarily more likely to get right than any other."
> -- Ralph Johnson

> "A checklist cannot fly a plane, but a pilot cannot fly safely without one."
> -- Atul Gawande

## Core Philosophy

This skill is a **checklist executor**, not a Socratic coach. Where `architecture-review` asks open-ended questions, this skill validates specific .NET patterns against a concrete, enumerated checklist and produces a graded report with prioritized findings.

The distinction matters: `architecture-review` builds architectural judgment. This skill applies it mechanically and reproducibly across .NET Blazor projects with CQRS patterns using FreeMediator and Mapster. It detects the framework version and hosting model first, then runs every checklist item in `references/review-checklist.md`, flags violations from `references/red-flags.md`, validates CQRS patterns from `references/cqrs-patterns.md`, and assesses framework health from `references/framework-detection.md`.

**Non-negotiable constraints:**
1. **Detect before you judge** -- always determine the target framework, hosting model, and pattern choices before applying any checklist item.
2. **Checklist completeness** -- every section of `references/review-checklist.md` is executed; skipping requires explicit justification.
3. **Evidence-based findings** -- every finding must reference a specific file, line, or pattern match.
4. **Grade reflects reality** -- the grading scale is objective: count of critical, high, and medium findings determines the grade.
5. **Recommendations match the stack** -- never recommend patterns or APIs that do not exist in the detected framework version.

## Domain Principles Table

| # | Principle | Description | Priority |
|---|-----------|-------------|----------|
| 1 | **Vertical Slice Compliance** | Features organized by business capability, not technical layer. Each feature folder contains commands, queries, handlers, validators, and DTOs. Cross-feature imports are violations. | Critical |
| 2 | **CQRS Handler Isolation** | Each handler is a standalone class implementing `IRequestHandler<TRequest, TResponse>`. No shared base handlers, no handler-to-handler calls, no business logic in controllers. | Critical |
| 3 | **FreeMediator Pipeline** | FreeMediator (Apache 2.0) is preferred. Pipeline behaviors for validation, logging, exception handling, and transactions registered in order. MediatR usage flagged for migration. | Critical |
| 4 | **Mapster Mapping Discipline** | `TypeAdapterConfig.GlobalSettings` configured at startup. Queries use `ProjectToType<>()` instead of `ToList().Adapt()`. Mapping profiles centralized in dedicated config classes. | High |
| 5 | **Blazor Hosting Model Detection** | Server, WASM, and Interactive Auto each require different checklist sections. Server requires SignalR circuit and backplane checks. WASM requires IL trimming and bundle security review. | Critical |
| 6 | **Shared Kernel Usage** | Projects must use official shared packages, maintain version consistency, and avoid duplicate entity definitions. | High |
| 7 | **EF Core Patterns** | DbContext must be scoped correctly for the hosting model. Async all the way down. N+1 query patterns caught. Singleton DbContext is a critical finding. | Critical |
| 8 | **Framework Version Awareness** | EOL frameworks (.NET Core 3.1, .NET 5, .NET 7) are flagged as critical. .NET Framework 4.x requires upgrade path assessment. | Critical |
| 9 | **Anti-Corruption Layers** | Boundaries between the application and external systems must be explicit. No domain entities leak across API boundaries. | High |
| 10 | **Configuration Patterns** | No hardcoded secrets. Configuration uses `IOptions<T>` or `IOptionsSnapshot<T>`. WASM bundles must not contain secrets. | High |

## Knowledge Base Lookups

| Query | When to Call |
|-------|--------------|
| `search_knowledge("Blazor CQRS FreeMediator vertical slice architecture .NET")` | At DETECT phase — confirms architectural patterns and checklist applicability |
| `search_knowledge("EF Core DbContext scoped singleton Blazor circuit")` | During EF Core section — authoritative DbContext lifetime patterns for Blazor |
| `search_knowledge("ASP.NET Core dependency injection IOptions configuration")` | When reviewing configuration patterns |
| `search_knowledge("Mapster ProjectTo query projection EF Core")` | During Mapster section — confirms ProjectTo vs Adapt patterns |
| `search_knowledge(".NET target framework EOL SDK style csproj")` | During framework detection — EOL status and SDK-style migration guidance |

Search at the start of each checklist section (DETECT, SCAN). Cite the source path in every finding.

## Workflow

The checklist lifecycle flows: **DETECT → SCAN → REPORT → RECOMMEND**; unknown framework or blocked items pause for user clarification.

### Phase 1: DETECT

Determine the full project context before running any checklist items.

1. **Target framework**: Scan all `.csproj` for `<TargetFramework>`. Categorize by EOL status.
2. **Hosting model**: Identify Blazor Server, WASM, Interactive Auto, or non-Blazor ASP.NET Core.
3. **CQRS library**: Detect FreeMediator or MediatR. Flag MediatR for migration consideration.
4. **Mapping library**: Detect Mapster, AutoMapper, or manual mapping.
5. **UI framework**: Detect Telerik, MudBlazor, Radzen, or vanilla Blazor.
6. **Shared kernel**: Check for shared NuGet package references.
7. **Project style**: Verify SDK-style projects. Flag legacy project files.

```bash
grep -r "<TargetFramework" --include="*.csproj" | grep -oE "net[0-9]+\.[0-9]+|netcoreapp[0-9]+\.[0-9]+|net4[0-9]+" | sort -u
grep -r "FreeMediator\|MediatR\|Mapster\|AutoMapper" --include="*.csproj"
grep -r "TelerikRootComponent\|MudThemeProvider\|RadzenLayout" --include="*.razor" | head -5
grep -rE "YourOrg\.SharedKernel\." --include="*.csproj"
find . -name "*.csproj" -exec grep -L "Sdk=" {} \;
```

### Phase 2: SCAN

Execute every section of `references/review-checklist.md` and every pattern in `references/red-flags.md`. For each item: run the detection command, record PASS/FAIL/WARN/SKIP, capture file and line reference, cross-reference CQRS items with `references/cqrs-patterns.md`.

**Checklist execution order:**
- Section 0: Framework & Dependencies Pre-Check
- Section 1: Solution Structure & Patterns (1a: CQRS, 1b: Mapster)
- Section 2: Blazor Hosting & Reliability
- Section 3: State Management
- Section 4: Data Access
- Section 5: Security
- Section 6: API Design
- Section 7: Observability
- Section 8: Dependency Injection
- Section 9: Testability
- Section 10: Performance
- Section 11: Telerik UI for Blazor (if applicable)

### Phase 3: REPORT

Count findings by severity. Calculate grade. Identify top 3 critical failure points. Generate the anti-patterns table, quick wins list, and technical debt register.

**Grading Formula:**
- **A**: 0 critical, 0 high, ≤ 3 medium findings
- **B**: 0 critical, ≤ 2 high findings
- **C**: 0 critical, significant gaps in one area
- **D**: 1+ critical findings or gaps in multiple areas
- **F**: Fundamental architectural problems (EOL framework, singleton DbContext, missing auth)

### Phase 4: RECOMMEND

Filter all recommendations against the detected target framework version. Prioritize: Critical findings → quick wins → modernization. Group by effort level (small/medium/large). Provide migration paths for framework upgrades.

## State Block

```
<dotnet-checklist-state>
mode: [DETECT | SCAN | REPORT | RECOMMEND | COMPLETE]
target_framework: [net48 | net6.0 | net8.0 | net10.0 | mixed | unknown]
hosting_model: [server | wasm | auto | non-blazor | unknown]
cqrs_compliant: [true | false | partial | not-applicable]
freemediator_version: [version | mediatr-detected | none]
issues_found: [critical:N high:N medium:N low:N]
last_action: [what was just done]
next_action: [what should happen next]
</dotnet-checklist-state>
```

**Example:**

```
<dotnet-checklist-state>
mode: SCAN
target_framework: net8.0
hosting_model: server
cqrs_compliant: partial
freemediator_version: mediatr-detected
issues_found: critical:1 high:3 medium:5 low:2
last_action: Completed sections 0-6 of review checklist
next_action: Execute sections 7-11, cross-reference red-flags
</dotnet-checklist-state>
```

## Output Templates

```markdown
## Architecture Checklist: [Solution Name]
**Framework**: [version] | **Hosting**: [Server/WASM/Auto] | **CQRS**: [FreeMediator/MediatR/None]
**Mapster**: [yes/no] | **Telerik**: [yes/no] | **Projects**: [count]

| Section | Items | Pass | Fail | Warn |
|---------|-------|------|------|------|
| 0 Framework | 8 | 6 | 1 | 1 |
| 1 Structure / 1a CQRS / 1b Mapster | ... | ... | ... | ... |

### Grade: [A-F]
**Critical failure points**: 1. [scenario] 2. [scenario] 3. [scenario]

| Severity | Location | Finding | Recommendation |
|----------|----------|---------|----------------|
| CRITICAL | file:line | [pattern] | [fix] |

**Quick Wins**: [low-effort high-impact fixes]
**Technical Debt**: [item | priority | effort | impact]
```

Full templates (Session Opening, Checklist Results Table, Finding Details, Session Closing with Roadmap): `references/review-checklist.md`.

## AI Discipline Rules

**Always detect framework first.** Recommending `InteractiveAutoRenderMode` to a .NET 6 project produces invalid findings. Run framework detection (grep `<TargetFramework>` in all `.csproj`) before any checklist item. If framework cannot be determined, ask the user — never assume .NET 10.

**Never assume the hosting model.** Server, WASM, and Interactive Auto have fundamentally different architectural concerns. Detect from `Program.cs`, project configuration, and component render modes before applying hosting-specific checklist items. Running the wrong section produces false positives.

**Check handler isolation before patterns.** Verify no base handler classes and no cross-handler calls (`grep -r "class.*Handler.*:.*Base" --include="*.cs"`) before assessing naming conventions or folder structure. A codebase with well-named handlers that all inherit from `BaseCrudHandler<T>` has a critical structural problem that must be reported first.

**Validate Mapster configs exist.** If the project uses Mapster, verify `TypeAdapterConfig` is configured at startup (`grep -r "TypeAdapterConfig\|IRegister" --include="*.cs"`). Relying on convention-based mapping silently produces incomplete DTOs when entity shapes change — this is a high-severity finding.

**Never mix architectural styles in recommendations.** If the codebase uses vertical slices with CQRS, never recommend repository pattern or layered architecture improvements. If recommending a style change, flag it as a separate migration initiative with an effort estimate.

**Handlers must be isolated and sealed.** Shared base handlers with injected fields create hidden coupling between unrelated features. Each handler must be a standalone `sealed class` implementing `IRequestHandler<TRequest, TResponse>` directly, with its own private dependencies. Flag any shared base handler as critical.

**Endpoints must be thin.** An endpoint that contains validation logic, business rules, or persistence calls is untestable and defeats the CQRS pipeline. Endpoints call only `mediator.Send()`. All business logic lives in handlers. Flag fat endpoints as a high-severity finding.

**Version-gate all recommendations.** Before suggesting any API, pattern, or feature, verify it exists in the detected .NET version. If it requires a newer version, note the minimum required version and frame it as a post-upgrade opportunity.

## Anti-Patterns Table

| Anti-Pattern | Why It's Wrong | Correct Approach |
|--------------|----------------|------------------|
| Reviewing without framework detection | Applying .NET 10 patterns to .NET 4.8 produces irrelevant findings | Always run DETECT phase first |
| Applying .NET 10 patterns to .NET Framework | APIs like Minimal APIs and Interactive Auto don't exist in 4.x | Detect version; recommend upgrade path from `references/framework-detection.md` |
| Ignoring shared kernel conventions | Duplicating entities creates drift and maintenance burden | Flag duplicate entity definitions; verify version consistency |
| Mixing CQRS with repository pattern | Repositories between handlers and DbContext add indirection without benefit | Handlers access DbContext directly; extract specifications for reuse |
| Fat controllers with business logic | Cannot be tested without HTTP infrastructure | Controllers call only `mediator.Send()` |
| Grading without evidence | Subjective assessments cannot be verified or acted upon | Every finding includes file path, evidence string, and checklist section |
| Assuming Blazor Server for all Blazor projects | WASM and Auto have completely different architectural concerns | Detect hosting model before applying hosting-specific checklist items |
| Recommending framework upgrade without complexity assessment | "Upgrade to .NET 10" without assessing System.Web deps is irresponsible | Use `references/framework-detection.md` to assess upgrade complexity |
| Skipping Telerik-specific checks for Telerik projects | Grid with `Data` on large datasets causes full-data loading; missing version alignment causes runtime errors | Always run Section 11 when Telerik UI is detected |
| Singleton DbContext in Blazor Server | Long-lived circuits cause connection exhaustion, stale data, thread-safety violations | DbContext must be scoped; use `OwningComponentBase` or `IDbContextFactory<T>` |

## Error Recovery

**Unknown framework version**: Check `global.json` and `Directory.Build.props` for centrally set framework. Inspect NuGet package versions as a proxy (`Microsoft.AspNetCore.Components` version maps to .NET version). If still unknown, ask the user directly. Record "unknown" in the state block and note which checklist items were skipped.

**Mixed CQRS and repository patterns**: Do NOT recommend removing repositories immediately. Report the inconsistency as HIGH. Recommend: new features use CQRS exclusively; existing repository features migrate incrementally. Flag any handlers that inject repositories (double indirection) as a separate finding.

**Legacy code without tests**: Report as HIGH (not critical). Recommend "test-forward" strategy: all new features and bug fixes include tests. Identify highest-risk handlers as priority candidates for retroactive testing. Reference `tdd-cycle` for methodology.

**Blazor Interactive Auto with unclear render mode boundaries**: Flag components without explicit `@rendermode` directives as MEDIUM. Identify components accessing server-only resources (DbContext, file system) — these must be Server-rendered. Recommend explicit `@rendermode InteractiveServer` or `@rendermode InteractiveWebAssembly` on every interactive component.

## Integration with Other Skills

- **`dotnet-vertical-slice`** -- When the checklist identifies structural violations (cross-feature imports, fat controllers, missing pipeline behaviors), reference this skill for correct implementation patterns.
- **`ef-migration-manager`** -- When the checklist identifies EF Core issues (singleton DbContext, N+1 queries, connection pooling), reference this skill for lifecycle management.
- **`architecture-review`** -- When the checklist produces a grade of D or F, recommend a full architecture review. The checklist identifies _what_ is wrong; `architecture-review` helps the team understand _why_.
- **`legacy-migration-analyzer`** -- When the checklist detects .NET Framework 4.x or EOL frameworks, reference this skill for comprehensive migration analysis and phased upgrade plan.
- **`dotnet-security-review`** -- When the checklist identifies security findings, reference this skill for deeper security posture assessment.

Reference files: [Review Checklist](references/review-checklist.md) | [CQRS Patterns](references/cqrs-patterns.md) | [Framework Detection](references/framework-detection.md) | [Red Flags](references/red-flags.md)
