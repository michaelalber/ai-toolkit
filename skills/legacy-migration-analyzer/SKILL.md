---
name: legacy-migration-analyzer
description: Analyze .NET Framework to .NET 10 migration paths. Use when assessing legacy codebases for modernization, identifying breaking changes, and planning incremental migration strategies. Also triggers on "upgrade framework", "migrate to .net 10", "framework to core", "legacy .net", ".net framework upgrade", "modernize .net", "upgrade .net framework project", "convert csproj to sdk-style".
---

# Legacy Migration Analyzer

> "The best migrations are the ones you don't notice. Incremental, tested, and invisible to the end user."
> -- Immo Landwerth, .NET Platform Compatibility Lead

## Core Philosophy

This skill analyzes legacy .NET Framework codebases and produces actionable migration plans to .NET 10. It does NOT perform the migration itself — it assesses, quantifies risk, and creates a phased plan that humans and other skills execute.

**Non-negotiable constraints:**
1. **Assess before acting** — Scan the codebase, catalog dependencies, and score risk before recommending any approach.
2. **Incremental migration over big-bang rewrites** — The strangler fig pattern and project-by-project migration succeed. Full rewrites fail.
3. **Preserve business logic unchanged** — Migration changes infrastructure, not behavior.
4. **Dependencies are the real blockers** — Third-party NuGet packages, COM interop, and Windows-specific APIs are where migrations stall. Identify these first.
5. **Every recommendation must cite evidence** — Reference specific files, namespaces, NuGet packages, or API calls. Vague guidance is not actionable.

## Domain Principles Table

| # | Principle | Description | Priority |
|---|-----------|-------------|----------|
| 1 | **Risk Assessment First** | Scan the codebase to quantify breaking changes, unsupported APIs, and incompatible dependencies before planning. Risk drives the plan. | Critical |
| 2 | **Incremental Migration** | Migrate one project, one layer, or one feature at a time. Each increment must be independently deployable and testable. | Critical |
| 3 | **API Compatibility Analysis** | Use .NET Upgrade Assistant and API compatibility analyzers for machine-readable reports. Manual inspection misses edge cases. | Critical |
| 4 | **Dependency Audit** | Catalog every NuGet package, COM reference, and P/Invoke call. For each: compatible version exists, replacement exists, or is a hard blocker. | Critical |
| 5 | **Business Logic Isolation** | Separate business logic from framework-dependent infrastructure before migrating. Pure C# libraries migrate trivially; framework-coupled code does not. | High |
| 6 | **Test Coverage Gate** | Do not migrate any project that lacks adequate test coverage. Write characterization tests against the legacy system first. | High |
| 7 | **Configuration Migration** | Map every `web.config`/`app.config` key to `appsettings.json` and the Options pattern before migrating. | High |
| 8 | **Authentication and Identity** | ASP.NET Membership, Forms Auth, and WIF require complete replacement. Plan these early — they are high-effort and high-risk. | High |
| 9 | **Database Access Layer** | EF6 → EF Core is non-trivial. Lazy loading behavior, query translation differences, and migration history require careful planning. | Medium |
| 10 | **Deployment Pipeline** | Legacy deployment (MSBuild scripts, IIS, manual) must be modernized alongside code migration. | Medium |

## Knowledge Base Lookups

| Query | When to Call |
|-------|--------------|
| `search_knowledge(".NET Framework to .NET 8 10 migration breaking changes")` | At SCAN phase — load authoritative breaking changes catalog |
| `search_knowledge(".NET Upgrade Assistant compatibility analyzer tool")` | During ASSESS phase — confirms tooling commands and output |
| `search_knowledge("Entity Framework 6 EF Core migration differences lazy loading")` | When assessing data access layer |
| `search_knowledge("ASP.NET MVC to ASP.NET Core migration web.config appsettings")` | When analyzing web projects |
| `search_knowledge("NuGet package compatibility .NET Standard target framework")` | During dependency audit |
| `search_knowledge("strangler fig pattern incremental migration legacy modernization")` | During PLAN phase |

Search at the start of SCAN and ASSESS phases. Every risk finding must cite its authoritative source.

## Workflow

Analysis proceeds through four phases: **SCAN** (codebase inventory) → **ASSESS** (risk scoring) → **PLAN** (migration roadmap) → **VALIDATE** (feasibility confirmation). Do not skip phases or reorder them.

**Approach selection:** Hard blockers (WCF duplex, COM-heavy, undocumented protocols) that can be isolated → strangler fig; that cannot be isolated → hybrid (keep blocked components on .NET Framework behind API gateway). Single monolith under 50K LOC → in-place upgrade. All NuGet dependencies compatible → project-by-project in-place. Incompatible packages with replacements → replace packages first, then upgrade. No clean path → strangler fig for affected projects.

### Phase 1: SCAN — Codebase Inventory

1. Run `upgrade-assistant analyze <SolutionPath> --target-tfm net10.0`
2. Catalog all projects (class libraries, ASP.NET MVC/Web API, WCF, Windows Services, Console, WinForms/WPF)
3. Enumerate all NuGet package references and versions
4. Identify `System.Web` namespace usages, COM interop, and P/Invoke declarations
5. Catalog all `web.config`/`app.config` sections with custom configuration
6. Catalog authentication mechanisms, IIS-specific features, and Windows-specific APIs
7. Map project-to-project references and dependency graph

### Phase 2: ASSESS — Risk Scoring

1. Cross-reference each NuGet package against [Breaking Changes Catalog](references/breaking-changes-catalog.md) and [Breaking Changes 4.x to 10](references/breaking-changes-4x-to-10.md)
2. Score each project using the [Migration Decision Matrix](references/migration-decision-matrix.md)
3. Consult [Package Replacement Map](references/package-replacement-map.md) for NuGet migration paths
4. Consult [API Replacement Patterns](references/api-replacement-patterns.md) for code-level migration patterns
5. For web projects, consult [ASP.NET to Blazor Patterns](references/aspnet-to-blazor-patterns.md)
6. Classify each breaking change: Blocker, High, Medium, Low
7. Calculate effort estimates per project and aggregate into overall risk score

### Phase 3: PLAN — Migration Roadmap

Order projects by dependency graph (leaf nodes first). Group into 2-4 week phases. Assign risk levels and rollback strategies. Define validation criteria per phase.

Standard phase order: Phase 0 (prerequisites: characterization tests, NuGet updates, extract interfaces) → Phase 1 (class libraries with no framework dependencies; multi-target if needed: `net48;net10.0`) → Phase 2 (data access layer; coordinate with `ef-migration-manager`) → Phase 3 (business logic layer) → Phase 4 (presentation/API layer; ASP.NET Core, gRPC) → Phase 5 (infrastructure; Worker Services, Kestrel, CI/CD).

### Phase 4: VALIDATE — Feasibility Confirmation

1. Walk the plan with the development team; verify effort estimates against capacity
2. Confirm all hard blockers have mitigation strategies
3. Validate rollback is possible at each phase boundary
4. Confirm deployment constraints are respected
5. Get stakeholder sign-off on timeline and risk acceptance

## State Block Format

```
<migration-analysis-state>
step: [SCAN | ASSESS | PLAN | VALIDATE]
source_framework: [e.g., ".NET Framework 4.8"]
target_framework: [e.g., ".NET 10"]
breaking_changes_found: [count]
risk_level: [low | medium | high | critical]
last_action: [what was just done]
next_action: [what should happen next]
blockers: [any issues]
</migration-analysis-state>
```

**Example:**
```
<migration-analysis-state>
step: ASSESS
source_framework: .NET Framework 4.8
target_framework: .NET 10
breaking_changes_found: 47
risk_level: high
last_action: Completed NuGet compatibility scan, 12 packages incompatible
next_action: Score each project and determine migration approach
blockers: WCF service project has no clear migration path for duplex contracts
</migration-analysis-state>
```

## Output Templates

```markdown
## Migration Inventory Report: [SolutionName]
**Source**: [.NET Framework version] → **Target**: .NET 10 | **Date**: [date]

| Metric | Count | | Package | .NET 10 Compatible | Replacement |
|--------|-------|-|---------|-------------------|-------------|
| Projects / NuGet Packages | [N] | | [name] | Yes/No/Partial | [replacement] |

**Breaking Changes by Category**: [table of counts per category]
**Hard Blockers**: [list with mitigation options]
**Risk Score**: [0-10] → [Low/Medium/High/Critical] → [recommended approach]
```

## AI Discipline Rules

**Never recommend a full rewrite without data.** Before suggesting a rewrite of any component, scan it, catalog breaking changes, and compare incremental vs. rewrite effort. Only recommend rewrite if incremental effort exceeds 3× the rewrite effort AND adequate test coverage exists to validate the rewrite.

**Always scan dependencies first.** Run `dotnet list package` on every project, check against nuget.org for .NET 10 compatibility, and verify transitive dependencies — not just direct references.

**Preserve business logic unchanged.** Migration is infrastructure only. Flag cases where framework differences could change behavior (culture defaults, floating-point, string comparison). Business logic changes go in separate PRs after migration is validated.

**Never produce a migration plan without completing SCAN and ASSESS first.** SCAN must produce a complete inventory; ASSESS must produce a risk score for every project. Skipping these produces an uncredible roadmap.

## .NET Framework Upgrade Specifics

### Analysis Commands

```bash
find . -name "*.csproj" -o -name "*.vbproj"          # Find all project files
grep -r "<TargetFramework" --include="*.csproj"        # Check target frameworks
find . -name "*.csproj" -exec grep -L "Sdk=" {} \;    # Legacy projects (no SDK attr)
find . -name "packages.config"                         # Needs migration to PackageReference
grep -r "using System\.Web" --include="*.cs" | wc -l  # System.Web usage (major blocker)
grep -r "using System\.ServiceModel" --include="*.cs"  # WCF (needs alternative)
grep -r "ConfigurationManager" --include="*.cs"        # Needs replacement
grep -r "BinaryFormatter" --include="*.cs"             # Security concern, not supported
```

### Upgrade Tools

```bash
# .NET Upgrade Assistant
dotnet tool install -g upgrade-assistant
upgrade-assistant analyze <solution.sln>
upgrade-assistant upgrade <project.csproj>

# try-convert (project file conversion)
dotnet tool install -g try-convert
try-convert -p <project.csproj>
```

### Complexity Classification

| Level | Timeframe | Characteristics |
|-------|-----------|-----------------|
| Low | 1–2 weeks | Class libraries, console apps, SDK-style already, standard NuGet only |
| Medium | 2–4 weeks | Web API (non-MVC), EF6→EF Core, limited System.Web, some config changes |
| High | 4–8+ weeks | Full ASP.NET MVC, heavy System.Web, WCF, Windows-specific features, custom MSBuild |

SDK-style `.csproj` target:
```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net10.0</TargetFramework>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
  </PropertyGroup>
</Project>
```

## Anti-Patterns Table

| Anti-Pattern | Why It's Wrong | Correct Approach |
|--------------|----------------|------------------|
| **Big-bang rewrite** | 60–80% of large rewrites fail or exceed budget 2×. | Strangler fig or project-by-project with continuous deployment. |
| **Migrating without tests** | Cannot verify behavior is preserved. | Write characterization tests first. Minimum 80% coverage on business logic. |
| **Starting with the hardest project** | High risk of early failure demoralizes the team. | Start with the simplest leaf-node projects. Build patterns before high-risk components. |
| **Ignoring transitive dependencies** | A compatible direct dependency may have incompatible transitive deps. | Use `dotnet list package --include-transitive`. Resolve before migrating. |
| **Changing business logic during migration** | Conflates infrastructure modernization and feature changes. | Migration is infrastructure only; logic changes go in separate PRs after validation. |
| **Skipping the Upgrade Assistant** | Manual analysis misses hundreds of breaking-change rules. | Always run `upgrade-assistant analyze` first. |
| **Migrating database and application simultaneously** | Two high-risk changes at once; rollback is ambiguous. | Migrate data layer first (via `ef-migration-manager`), verify, then application layer. |

## Error Recovery

### Upgrade Assistant Fails to Analyze Solution
1. Verify the solution builds on .NET Framework first
2. Check for unsupported project types (SSDT, Fabric, native C++)
3. Analyze projects individually if solution-level fails
4. Fall back to manual analysis using the [Breaking Changes Catalog](references/breaking-changes-catalog.md)

### NuGet Package Has No .NET 10 Version
1. Check if open source — fork and compile for .NET 10
2. Look for the functionality in the .NET 10 BCL
3. Search for community-maintained alternatives
4. As last resort, keep the dependency in a .NET Framework process; communicate via HTTP or gRPC

### WCF Service Cannot Be Migrated
1. Evaluate CoreWCF (supports many WCF server scenarios)
2. For duplex contracts, consider SignalR or gRPC bidirectional streaming
3. For MSMQ, consider Azure Service Bus, RabbitMQ
4. If none work, keep WCF on .NET Framework behind an API gateway

### Extensive System.Web Usage
1. Count and categorize all `System.Web` usages by pattern
2. Create an abstraction layer on .NET Framework first (equivalent of `IHttpContextAccessor`)
3. Migrate all consumers to the abstraction
4. Then swap the implementation to ASP.NET Core equivalents
5. This is Phase 0 prerequisite work, not migration work

## Integration with Other Skills

- **`ef-migration-manager`** — When the analysis identifies EF6 usage, coordinate for the EF6→EF Core migration. The database schema migration is often the riskiest part and should be planned and tested independently.
- **`dotnet-vertical-slice`** — When the plan calls for decomposing a monolithic application, use this skill to structure new .NET 10 projects as vertical slices. Especially relevant in strangler fig migrations.
- **`nuget-package-scaffold`** — When shared libraries need to be extracted or multi-targeted (`net48;net10.0`) during the transition period.

## Reference Files

- [Breaking Changes: .NET Framework 4.x to .NET 10](references/breaking-changes-4x-to-10.md)
- [Package Replacement Map](references/package-replacement-map.md)
- [API Replacement Patterns](references/api-replacement-patterns.md)
- [ASP.NET to Blazor Patterns](references/aspnet-to-blazor-patterns.md)
- [Migration Decision Matrix](references/migration-decision-matrix.md)
- [Breaking Changes Catalog](references/breaking-changes-catalog.md)
