---
name: legacy-migration-analyzer
description: Analyze .NET Framework to .NET 10 migration paths. Use when assessing legacy codebases for modernization, identifying breaking changes, and planning incremental migration strategies. Also triggers on "upgrade framework", "migrate to .net 10", "framework to core", "legacy .net", ".net framework upgrade", "modernize .net", "upgrade .net framework project", "convert csproj to sdk-style".
---

# Legacy Migration Analyzer

> "The best migrations are the ones you don't notice. Incremental, tested, and invisible to the end user."
> -- Immo Landwerth, .NET Platform Compatibility Lead

## Core Philosophy

This skill analyzes legacy .NET Framework codebases and produces actionable migration plans to .NET 10. It does NOT perform the migration itself -- it assesses, quantifies risk, and creates a phased plan that humans and other skills execute.

**Non-negotiable constraints:**

1. **Assess before acting** -- Never recommend a migration approach without first scanning the codebase, cataloging dependencies, and scoring risk. Gut feelings are not migration plans.
2. **Incremental migration over big-bang rewrites** -- The strangler fig pattern and project-by-project migration succeed. Full rewrites fail. Default to incremental unless the data overwhelmingly says otherwise.
3. **Preserve business logic unchanged** -- Migration changes infrastructure, not behavior. If a business rule works correctly on .NET Framework, it must work identically on .NET 10. Behavior changes are bugs, not features.
4. **Dependencies are the real blockers** -- The framework migration is predictable. Third-party NuGet packages, COM interop, and Windows-specific APIs are where migrations stall. Identify these first.
5. **Every recommendation must cite evidence** -- Reference specific files, namespaces, NuGet packages, or API calls. Vague guidance like "modernize the data layer" is not actionable.

## Domain Principles Table

| # | Principle | Description | Priority |
|---|-----------|-------------|----------|
| 1 | **Risk Assessment First** | Before any migration planning, scan the codebase to quantify breaking changes, unsupported APIs, and incompatible dependencies. Risk drives the plan, not the other way around. | Critical |
| 2 | **Incremental Migration** | Migrate one project, one layer, or one feature at a time. Each increment must be independently deployable and testable. Never migrate the entire solution in a single pass. | Critical |
| 3 | **API Compatibility Analysis** | Use the .NET Upgrade Assistant and API compatibility analyzers to produce machine-readable reports. Manual inspection misses edge cases; tooling catches them. | Critical |
| 4 | **Dependency Audit** | Catalog every NuGet package, COM reference, and P/Invoke call. For each, determine: has a .NET 10 compatible version, has a replacement, or is a hard blocker. | Critical |
| 5 | **Business Logic Isolation** | Separate business logic from framework-dependent infrastructure code before migrating. Business logic in pure C# libraries migrates trivially; framework-coupled code does not. | High |
| 6 | **Test Coverage Gate** | Do not migrate any project that lacks adequate test coverage. If tests do not exist, write characterization tests against the legacy system first. Migration without tests is migration without a safety net. | High |
| 7 | **Configuration Migration** | `web.config` and `app.config` XML configuration must be mapped to `appsettings.json` and the Options pattern. Document every configuration key and its target location. | High |
| 8 | **Authentication and Identity** | ASP.NET Membership, Forms Authentication, and Windows Identity Foundation require complete replacement. These are high-effort, high-risk items that must be planned early. | High |
| 9 | **Database Access Layer** | Entity Framework 6 to EF Core migration is non-trivial. Lazy loading behavior, query translation differences, and migration history all require careful planning. Coordinate with `ef-migration-manager`. | Medium |
| 10 | **Deployment Pipeline** | Legacy projects often deploy via MSBuild scripts, IIS configurations, or manual processes. The migration plan must include CI/CD modernization alongside code migration. | Medium |

## Workflow

### Analysis Phase Machine

```
+-------------------------------------------------------------------+
|                Legacy Migration Analysis Phases                     |
|                                                                     |
|  +------+    +--------+    +------+    +----------+                 |
|  | SCAN |---}| ASSESS |---}| PLAN |---}| VALIDATE |                |
|  +------+    +--------+    +------+    +----------+                 |
|      |            |            |            |                        |
|      |            |            |            |                        |
|      v            v            v            v                        |
|  Inventory    Risk Score   Migration    Feasibility                  |
|  Report       Report       Roadmap     Confirmation                  |
+-------------------------------------------------------------------+
```

### Pre-Flight Checklist

Before beginning analysis, verify:

```
+-------------------------------------------------------------+
| Migration Analysis Pre-Flight                                |
+-------------------------------------------------------------+
| [ ] Access to full source code (all projects in solution)    |
| [ ] Solution builds successfully on .NET Framework           |
| [ ] List of all deployed environments obtained               |
| [ ] Current .NET Framework version(s) confirmed              |
| [ ] Target .NET version confirmed (.NET 10)                  |
| [ ] Stakeholder expectations documented                      |
| [ ] Team skill assessment completed                          |
| [ ] Timeline constraints identified                          |
| [ ] Budget constraints identified                            |
| [ ] Existing test suite status known                         |
+-------------------------------------------------------------+
```

### Phase 1: SCAN -- Codebase Inventory

**Objective**: Produce a complete inventory of the codebase, its dependencies, and its framework-specific API usage.

**Actions:**

1. Run the .NET Upgrade Assistant analysis:
   ```bash
   upgrade-assistant analyze <SolutionPath> --target-tfm net10.0
   ```
2. Catalog all projects in the solution with their types:
   - Class Library (.dll)
   - ASP.NET Web Application / MVC / Web API
   - WCF Service
   - Windows Service
   - Console Application
   - WinForms / WPF
3. Enumerate all NuGet package references and their versions
4. Identify all `System.Web` namespace usages
5. Identify all COM interop and P/Invoke declarations
6. Identify all `web.config` / `app.config` sections with custom configuration
7. Catalog authentication mechanisms in use
8. Document IIS-specific features (HTTP modules, HTTP handlers, ISAPI filters)
9. Identify all Windows-specific APIs (Registry, WMI, Event Log, Performance Counters)
10. Map project-to-project references and dependency graph

**Output**: Inventory Report (see Output Templates)

### Phase 2: ASSESS -- Risk Scoring

**Objective**: Assign a risk score to each project and to the overall solution based on scan findings.

**Actions:**

1. Cross-reference each NuGet package against [Breaking Changes Catalog](references/breaking-changes-catalog.md) and [Breaking Changes 4.x to 10](references/breaking-changes-4x-to-10.md)
2. Score each project using the [Migration Decision Matrix](references/migration-decision-matrix.md)
3. Consult [Package Replacement Map](references/package-replacement-map.md) for NuGet package migration paths
4. Consult [API Replacement Patterns](references/api-replacement-patterns.md) for code-level migration patterns
5. For web applications, consult [ASP.NET to Blazor Patterns](references/aspnet-to-blazor-patterns.md)
6. Classify each breaking change by severity: Blocker, High, Medium, Low
7. Identify hard blockers (no known migration path)
8. Calculate effort estimates per project
9. Aggregate into overall solution risk score

**Decision Tree -- Migration Approach Selection:**

```
Solution scanned and scored
        |
        v
Are there hard blockers (WCF server, COM-heavy, undocumented protocols)?
    YES --> Can blockers be isolated to specific projects?
                YES --> Strangler Fig: Migrate non-blocked projects first,
                        wrap blocked components behind abstractions
                NO  --> Hybrid: Keep blocked components on .NET Framework,
                        communicate via API gateway or message bus
    NO
        |
        v
Is the solution a single monolithic project?
    YES --> Is it under 50K lines of code?
                YES --> In-place upgrade (with Upgrade Assistant)
                NO  --> Decompose first, then migrate project by project
    NO
        |
        v
Are all NuGet dependencies .NET 10 compatible?
    YES --> Project-by-project in-place upgrade
                (start with leaf nodes in dependency graph)
    NO  --> Can incompatible packages be replaced?
                YES --> Replace packages first, verify on .NET Framework,
                        then proceed with in-place upgrade
                NO  --> Strangler Fig for affected projects
```

### Phase 3: PLAN -- Migration Roadmap

**Objective**: Produce a phased migration plan with specific ordering, effort estimates, and risk mitigations.

**Actions:**

1. Order projects by dependency graph (leaf nodes first)
2. Group into migration phases (2-4 week sprints)
3. Assign each phase a risk level and rollback strategy
4. Identify prerequisite work (test coverage, package updates, abstractions)
5. Define validation criteria for each phase (what "done" means)
6. Create timeline with milestones and decision gates

**Migration Order Strategy:**

```
Phase 0: Prerequisites
   - Add characterization tests for untested code
   - Update NuGet packages to latest .NET Framework compatible versions
   - Abstract away framework-specific code behind interfaces
   - Replace incompatible packages with alternatives

Phase 1: Shared Libraries
   - Migrate class libraries with no framework dependencies
   - Multi-target if consumers are not yet migrated:
     <TargetFrameworks>net48;net10.0</TargetFrameworks>

Phase 2: Data Access Layer
   - Migrate EF6 to EF Core (coordinate with ef-migration-manager)
   - Update repository patterns for EF Core differences
   - Verify query translation parity

Phase 3: Business Logic Layer
   - Migrate services and domain logic
   - These should be mostly framework-agnostic if Phase 0 was thorough

Phase 4: Presentation / API Layer
   - ASP.NET MVC/Web API to ASP.NET Core
   - WCF services to gRPC or minimal APIs
   - This is the highest-risk phase; plan extra buffer

Phase 5: Infrastructure
   - Windows Services to Worker Services
   - IIS configurations to Kestrel/YARP
   - Deployment pipeline updates
```

### Phase 4: VALIDATE -- Feasibility Confirmation

**Objective**: Confirm the plan is realistic and surface any issues that were missed.

**Actions:**

1. Walk through the plan with the development team
2. Verify effort estimates against team capacity
3. Confirm all hard blockers have mitigation strategies
4. Validate that rollback is possible at each phase boundary
5. Check that the plan respects deployment constraints
6. Get stakeholder sign-off on timeline and risk acceptance

## State Block Format

Maintain state across conversation turns using this block:

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

### Example State Progression

```
<migration-analysis-state>
step: SCAN
source_framework: .NET Framework 4.8
target_framework: .NET 10
breaking_changes_found: 0
risk_level: unknown
last_action: Solution loaded, beginning dependency inventory
next_action: Run Upgrade Assistant analysis on solution
blockers: none
</migration-analysis-state>
```

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

```
<migration-analysis-state>
step: PLAN
source_framework: .NET Framework 4.8
target_framework: .NET 10
breaking_changes_found: 47
risk_level: high
last_action: Decided on strangler fig approach for WCF components
next_action: Build phased migration roadmap with ordering
blockers: none -- WCF blocker mitigated with gRPC replacement plan
</migration-analysis-state>
```

## Output Templates

### Inventory Report

```markdown
## Migration Inventory Report: [SolutionName]

**Source Framework**: [.NET Framework version]
**Target Framework**: .NET 10
**Analysis Date**: [date]
**Analyzed By**: legacy-migration-analyzer

### Solution Overview
| Metric | Count |
|--------|-------|
| Total Projects | [N] |
| Class Libraries | [N] |
| Web Applications (ASP.NET) | [N] |
| WCF Services | [N] |
| Windows Services | [N] |
| Console Applications | [N] |
| WinForms/WPF | [N] |
| Total NuGet Packages | [N] |
| Unique NuGet Packages | [N] |

### Project Inventory
| Project | Type | Framework | Dependencies | LOC (approx) |
|---------|------|-----------|-------------|---------------|
| [name] | [type] | [framework] | [count] | [lines] |

### NuGet Package Compatibility
| Package | Current Version | .NET 10 Compatible | Replacement | Effort |
|---------|----------------|-------------------|-------------|--------|
| [name] | [version] | [Yes/No/Partial] | [replacement or N/A] | [Low/Med/High] |

### Breaking Change Summary
| Category | Count | Blockers | High | Medium | Low |
|----------|-------|----------|------|--------|-----|
| ASP.NET to ASP.NET Core | [N] | [N] | [N] | [N] | [N] |
| WCF to gRPC/REST | [N] | [N] | [N] | [N] | [N] |
| EF6 to EF Core | [N] | [N] | [N] | [N] | [N] |
| Windows-specific APIs | [N] | [N] | [N] | [N] | [N] |
| NuGet Incompatibilities | [N] | [N] | [N] | [N] | [N] |
| Configuration (web.config) | [N] | [N] | [N] | [N] | [N] |
| Authentication | [N] | [N] | [N] | [N] | [N] |

### Hard Blockers
| # | Description | Affected Projects | Mitigation Options |
|---|-------------|-------------------|-------------------|
| 1 | [description] | [projects] | [options] |

<migration-analysis-state>
step: SCAN
source_framework: [version]
target_framework: .NET 10
breaking_changes_found: [total count]
risk_level: [level based on findings]
last_action: Inventory scan complete
next_action: Begin risk assessment scoring
blockers: [any hard blockers found]
</migration-analysis-state>
```

### Risk Assessment Report

```markdown
## Risk Assessment: [SolutionName]

**Overall Risk Level**: [LOW | MEDIUM | HIGH | CRITICAL]
**Recommended Approach**: [In-Place Upgrade | Strangler Fig | Hybrid | Phased Decomposition]

### Risk Score by Project
| Project | Risk Score | Blockers | Incompatible Deps | Framework APIs | Effort (days) |
|---------|-----------|----------|-------------------|----------------|---------------|
| [name] | [1-10] | [count] | [count] | [count] | [estimate] |

### Risk Score Breakdown
| Factor | Weight | Score | Weighted |
|--------|--------|-------|----------|
| Hard Blockers | 30% | [0-10] | [calculated] |
| NuGet Incompatibility | 25% | [0-10] | [calculated] |
| Framework API Usage | 20% | [0-10] | [calculated] |
| Test Coverage Gap | 15% | [0-10] | [calculated] |
| Solution Complexity | 10% | [0-10] | [calculated] |
| **Total** | **100%** | | **[total]** |

### Risk Interpretation
| Total Score | Risk Level | Recommendation |
|-------------|-----------|----------------|
| 0-2.0 | Low | Straightforward in-place upgrade |
| 2.1-4.0 | Medium | In-place with targeted remediation |
| 4.1-6.0 | High | Strangler fig or phased approach |
| 6.1-10.0 | Critical | Major architectural work required |

<migration-analysis-state>
step: ASSESS
source_framework: [version]
target_framework: .NET 10
breaking_changes_found: [count]
risk_level: [calculated level]
last_action: Risk assessment complete
next_action: Build migration roadmap
blockers: [any unresolved blockers]
</migration-analysis-state>
```

### Migration Roadmap

```markdown
## Migration Roadmap: [SolutionName]

**Approach**: [In-Place Upgrade | Strangler Fig | Hybrid]
**Estimated Total Duration**: [weeks/months]
**Team Size Assumption**: [N developers]

### Phase Summary
| Phase | Scope | Duration | Risk | Rollback Strategy |
|-------|-------|----------|------|-------------------|
| Phase 0 | Prerequisites | [duration] | Low | N/A (no migration yet) |
| Phase 1 | [scope] | [duration] | [level] | [strategy] |
| Phase 2 | [scope] | [duration] | [level] | [strategy] |
| Phase N | [scope] | [duration] | [level] | [strategy] |

### Detailed Phase Plan

#### Phase 0: Prerequisites (Duration: [estimate])
**Objective**: Prepare the codebase for migration without changing the target framework.

| Task | Description | Effort | Owner |
|------|-------------|--------|-------|
| [task] | [description] | [days] | [role] |

**Exit Criteria**:
- [ ] [criterion]

**Decision Gate**: Proceed to Phase 1 only when all exit criteria are met.

[Repeat for each phase]

### Dependencies and Ordering
[Dependency graph or ordered list showing which projects must migrate first]

### Risk Mitigations
| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| [risk] | [H/M/L] | [H/M/L] | [mitigation] |

<migration-analysis-state>
step: PLAN
source_framework: [version]
target_framework: .NET 10
breaking_changes_found: [count]
risk_level: [level]
last_action: Migration roadmap created
next_action: Validate plan with team
blockers: [any remaining concerns]
</migration-analysis-state>
```

## AI Discipline Rules

### CRITICAL: Never Recommend Full Rewrite Without Data

Before suggesting a rewrite of any component:

1. Scan the component with the .NET Upgrade Assistant
2. Catalog every breaking change and incompatible dependency
3. Estimate the effort for incremental migration versus rewrite
4. Only recommend rewrite if incremental effort exceeds 3x the rewrite effort AND the component has adequate test coverage to validate the rewrite

```
WRONG: "This WCF service is old, you should rewrite it as a gRPC service."
RIGHT: "This WCF service uses 3 duplex contracts and 14 service operations.
        The duplex contracts have no direct gRPC equivalent and require
        architectural changes. Estimated effort: 12 days incremental vs
        8 days rewrite. Rewrite is justified IF the existing integration
        tests (found: 47 tests covering 82% of operations) can validate
        the replacement."
```

### CRITICAL: Always Scan Dependencies First

Before making any migration recommendation:

1. Run `dotnet list package` on every project
2. Check each package against nuget.org for .NET 10 compatibility
3. Identify transitive dependencies that may be incompatible
4. Document the full dependency chain, not just direct references

```
WRONG: "The project uses Newtonsoft.Json, which works on .NET 10."
RIGHT: "The project uses Newtonsoft.Json 13.0.3 (compatible), but also
        references Castle.Windsor 5.1.1 which depends on
        System.Configuration.ConfigurationManager. Windsor 6.0+ supports
        .NET 10. Migration requires updating from 5.1.1 to 6.0+, which
        includes breaking changes in container registration syntax.
        See: [specific breaking changes]."
```

### CRITICAL: Preserve Business Logic Unchanged

During migration planning:

1. Identify all business rules implemented in the codebase
2. Ensure the migration plan does NOT modify business logic
3. Flag any case where framework differences could change behavior (e.g., different floating-point handling, string comparison, culture defaults)
4. Require characterization tests for any business logic near framework-sensitive code

```
WRONG: "While migrating the order calculator, we can also clean up
        the discount logic."
RIGHT: "The order calculator uses Thread.CurrentThread.CurrentCulture
        for currency formatting. .NET 10 has different default culture
        handling. A characterization test must verify that discount
        calculations produce identical results before and after migration.
        Business logic changes, if desired, should be a separate work item
        after migration is complete and validated."
```

### CRITICAL: Risk Assessment Before Migration Plan

Never produce a migration plan without first completing the SCAN and ASSESS phases:

1. SCAN must produce a complete inventory report
2. ASSESS must produce a risk score for every project
3. Only then can PLAN produce a credible roadmap

```
WRONG: "Here's a migration plan for your solution: start with the
        shared libraries, then migrate the web project."

RIGHT: "Scan results show 14 projects, 87 NuGet packages (12 incompatible),
        and 23 System.Web usages. Risk assessment scores the solution at
        5.8 (High). The web project has the highest individual risk (7.2)
        due to heavy HttpContext.Current usage across 34 files. The
        recommended approach is strangler fig, starting with the 6 class
        libraries that have zero framework dependencies (risk: 1.1 each),
        then proceeding to the data access layer (risk: 3.4), and
        finally the web project with a parallel ASP.NET Core implementation."
```

## .NET Framework Upgrade Specifics

This section provides detailed guidance for .NET Framework 4.x to .NET 10 upgrade execution, complementing the analysis workflow above with concrete strategies, project file conversion patterns, and complexity classification criteria.

### Target Framework Recommendations

| Scenario | Target |
|----------|--------|
| New projects | .NET 10 (latest LTS) |
| Production upgrades | .NET 10 or .NET 8 (current LTS) |
| Shared libraries | Multi-target if needed |

### Upgrade Strategies

#### Strategy 1: In-Place Upgrade (Recommended for most projects)
1. Convert `.csproj` to SDK-style
2. Update target framework to `net10.0`
3. Replace incompatible packages (see [Package Replacement Map](references/package-replacement-map.md))
4. Fix breaking API changes (see [API Replacement Patterns](references/api-replacement-patterns.md))
5. Update configuration to `appsettings.json`

#### Strategy 2: Parallel Migration (For complex apps)
1. Create new .NET 10 project alongside legacy
2. Copy/migrate code file by file
3. Share database via EF Core
4. Run both in parallel during transition

#### Strategy 3: Strangler Fig (For monoliths)
1. Extract features as new .NET 10 microservices
2. Route requests to new services
3. Gradually replace legacy components
4. Decommission old app when empty

### Project File Conversion

#### Legacy `.csproj` Format
```xml
<?xml version="1.0" encoding="utf-8"?>
<Project ToolsVersion="15.0" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">
  <Import Project="$(MSBuildExtensionsPath)\..." />
  <PropertyGroup>
    <TargetFrameworkVersion>v4.8</TargetFrameworkVersion>
    ...
  </PropertyGroup>
  <ItemGroup>
    <Reference Include="System" />
    <Reference Include="System.Core" />
    ...
  </ItemGroup>
  <ItemGroup>
    <Compile Include="Class1.cs" />
    ...
  </ItemGroup>
  <Import Project="$(MSBuildToolsPath)\Microsoft.CSharp.targets" />
</Project>
```

#### SDK-Style `.csproj` Format (Target)
```xml
<Project Sdk="Microsoft.NET.Sdk">

  <PropertyGroup>
    <TargetFramework>net10.0</TargetFramework>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="PackageName" Version="X.Y.Z" />
  </ItemGroup>

</Project>
```

#### Web Project SDK-Style
```xml
<Project Sdk="Microsoft.NET.Sdk.Web">

  <PropertyGroup>
    <TargetFramework>net10.0</TargetFramework>
  </PropertyGroup>

</Project>
```

### Complexity Classification

#### Low Complexity (1-2 weeks)
- Class libraries with no web dependencies
- Console applications
- Already uses SDK-style project
- Standard NuGet packages only

#### Medium Complexity (2-4 weeks)
- Web API (non-MVC)
- Entity Framework 6 to EF Core migration
- Some configuration changes
- Limited System.Web usage

#### High Complexity (4-8+ weeks)
- Full ASP.NET MVC application
- Heavy System.Web dependencies
- WCF services
- Windows-specific features
- Custom MSBuild tasks
- Binary serialization

### Upgrade Analysis Commands

```bash
# Find all project files
find . -name "*.csproj" -o -name "*.vbproj" -o -name "*.fsproj"

# Check target frameworks
grep -r "<TargetFramework" --include="*.csproj" | sort -u

# Identify SDK-style vs legacy projects
find . -name "*.csproj" -exec grep -L "Sdk=" {} \;  # Legacy format

# Check for packages.config (needs migration)
find . -name "packages.config"

# System.Web dependencies (major blocker)
grep -r "using System\.Web" --include="*.cs" | wc -l

# WCF usage (needs alternative)
grep -r "using System\.ServiceModel" --include="*.cs"

# ConfigurationManager (needs replacement)
grep -r "ConfigurationManager" --include="*.cs"

# BinaryFormatter (security concern)
grep -r "BinaryFormatter" --include="*.cs"
```

### Upgrade Tools

#### .NET Upgrade Assistant
```bash
# Install
dotnet tool install -g upgrade-assistant

# Analyze solution
upgrade-assistant analyze <solution.sln>

# Upgrade project
upgrade-assistant upgrade <project.csproj>
```

#### try-convert (Project File Conversion)
```bash
# Install
dotnet tool install -g try-convert

# Convert project
try-convert -p <project.csproj>

# Convert solution
try-convert -w <solution.sln>
```

### Reference Files

For detailed migration patterns, consult these references:

- [Breaking Changes: .NET Framework 4.x to .NET 10](references/breaking-changes-4x-to-10.md) -- Critical and medium-impact breaking changes by version with code migration examples
- [Package Replacement Map](references/package-replacement-map.md) -- Comprehensive NuGet package replacement guide organized by category (web, EF, logging, DI, auth, caching, etc.)
- [API Replacement Patterns](references/api-replacement-patterns.md) -- Code-level API migration patterns for HttpContext, configuration, logging, caching, session, EF, controllers, DI, and more
- [ASP.NET to Blazor Patterns](references/aspnet-to-blazor-patterns.md) -- Web Forms/MVC to Blazor migration including component conversion, form handling, authentication, and incremental strategy

## Anti-Patterns Table

| Anti-Pattern | Why It's Wrong | Correct Approach |
|--------------|----------------|------------------|
| Big-bang rewrite | 60-80% of large rewrites fail or exceed budget by 2x+. Business continuity is lost during rewrite. No incremental value delivery. | Strangler fig or project-by-project migration with continuous deployment at each phase. |
| Migrating without tests | No way to verify that behavior is preserved. Bugs introduced during migration are indistinguishable from existing bugs. | Write characterization tests against the legacy system before touching any code. Minimum 80% coverage on business logic. |
| Starting with the hardest project | High risk of early failure demoralizes the team and stalls the entire migration. Lessons learned come too late. | Start with the simplest leaf-node projects. Build team confidence and migration patterns before tackling high-risk components. |
| Ignoring transitive dependencies | A direct dependency may be compatible, but its transitive dependencies may not. The build breaks at the worst possible time. | Use `dotnet list package --include-transitive` and verify the full dependency tree. Resolve transitive incompatibilities before migrating. |
| Changing business logic during migration | Conflates two concerns: infrastructure modernization and feature changes. If something breaks, you cannot tell if it was the migration or the logic change. | Migration is infrastructure only. Business logic changes go in separate PRs after migration is validated. |
| Skipping the Upgrade Assistant | Manual analysis misses edge cases. The Upgrade Assistant has rules for hundreds of breaking changes that no human remembers. | Always run `upgrade-assistant analyze` as the first step. Use its output as the foundation for the analysis, then augment with manual review. |
| Migrating the database and application simultaneously | Two high-risk changes at once. If either fails, rollback is ambiguous. | Migrate the database layer first (coordinate with `ef-migration-manager`), verify, then migrate the application layer. |
| Assuming .NET Standard means compatible | A library targeting .NET Standard 2.0 may compile but behave differently due to API shims that throw at runtime (e.g., `System.Drawing`). | Test .NET Standard libraries on .NET 10 runtime. Check for `PlatformNotSupportedException` and behavioral differences in shimmed APIs. |

## Error Recovery

### Problem: Upgrade Assistant Fails to Analyze Solution

The .NET Upgrade Assistant cannot parse the solution or crashes during analysis.

**Action:**
1. Verify the solution builds on .NET Framework first
2. Check for unsupported project types (e.g., SSDT, Fabric, native C++)
3. Analyze projects individually if the solution-level analysis fails
4. Fall back to manual analysis using the [Breaking Changes Catalog](references/breaking-changes-catalog.md) and [Breaking Changes 4.x to 10](references/breaking-changes-4x-to-10.md)
5. Report the issue to the Upgrade Assistant GitHub repository

### Problem: NuGet Package Has No .NET 10 Version

A required NuGet package does not support .NET 10 and has no replacement.

**Action:**
1. Check if the package is open source -- fork and compile for .NET 10
2. Look for the functionality in the .NET 10 BCL (many old packages were absorbed)
3. Search for community-maintained alternatives
4. If the package wraps a native library, check if P/Invoke works directly
5. As a last resort, isolate the dependency behind an interface and keep it in a .NET Framework process, communicating via HTTP or gRPC

### Problem: WCF Service Cannot Be Migrated

A WCF service uses features with no ASP.NET Core equivalent (duplex channels, MSMQ transport, federated security).

**Action:**
1. Evaluate CoreWCF as a compatibility bridge (supports many WCF server scenarios)
2. For duplex contracts, consider SignalR or gRPC bidirectional streaming
3. For MSMQ, consider Azure Service Bus, RabbitMQ, or a dedicated message broker
4. If none work, keep the WCF service on .NET Framework and expose it via an API gateway to the migrated application

### Problem: Extensive System.Web Usage

The codebase uses `HttpContext.Current`, `HttpRuntime`, `HttpApplication`, and other `System.Web` types pervasively.

**Action:**
1. Count and categorize all `System.Web` usages
2. Group by pattern: session access, cache, request/response manipulation, static context access
3. Create an abstraction layer on .NET Framework first (e.g., `IHttpContextAccessor` equivalent)
4. Migrate all consumers to use the abstraction
5. Then swap the implementation to ASP.NET Core equivalents
6. This is Phase 0 prerequisite work, not migration work

### Problem: Risk Assessment Disagrees with Stakeholder Expectations

Stakeholders expect a 3-month migration but the assessment says 9-12 months.

**Action:**
1. Present the data: specific breaking changes, dependency counts, effort estimates
2. Show the risk score calculation transparently
3. Offer scope reduction options: migrate critical path first, defer low-value components
4. Identify what could be parallelized with more team members
5. Never compress the timeline by removing validation steps -- that trades schedule risk for production risk

## Integration with Other Skills

- **`ef-migration-manager`** -- When the migration analysis identifies Entity Framework 6 usage, coordinate with this skill to plan the EF6-to-EF-Core migration. The database schema migration is often the riskiest part of the overall migration and should be planned and tested independently. Use `ef-migration-manager` to handle the actual migration creation, SQL review, and rollback testing for the data access layer.

- **`dotnet-vertical-slice`** -- When the migration plan calls for decomposing a monolithic application, use this skill to structure the new .NET 10 projects as vertical slices. This is especially relevant in strangler fig migrations where new features are built in .NET 10 while legacy features remain on .NET Framework. Each new slice should follow the vertical slice architecture from the start.

- **`nuget-package-scaffold`** -- When the migration analysis identifies shared libraries that need to be extracted or multi-targeted, use this skill to scaffold proper NuGet package projects. Multi-targeting (`net48;net10.0`) during the transition period requires correct package metadata, conditional compilation, and proper dependency management that this skill handles.

- **`dotnet-vertical-slice`** (Telerik Blazor UI section) -- When the migration plan involves converting ASP.NET Web Forms or MVC views to Blazor, use the Telerik Blazor UI generation section in `dotnet-vertical-slice` for component implementation. The [ASP.NET to Blazor Patterns](references/aspnet-to-blazor-patterns.md) reference provides migration patterns that map legacy controls to Telerik Blazor equivalents.
