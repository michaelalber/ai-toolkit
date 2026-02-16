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

This skill is a **checklist executor**, not a Socratic coach. Where `architecture-review` asks open-ended questions and guides engineers through tradeoff exploration, this skill validates specific .NET patterns against a concrete, enumerated checklist and produces a graded report with prioritized findings.

The distinction matters: `architecture-review` builds architectural judgment. This skill applies it mechanically and reproducibly across .NET Blazor projects that follow CQRS patterns with FreeMediator and Mapster. It detects the framework version, hosting model, and dependency landscape first, then runs every checklist item in `references/review-checklist.md`, flags violations from `references/red-flags.md`, validates CQRS patterns from `references/cqrs-patterns.md`, and assesses framework health from `references/framework-detection.md`.

**Non-negotiable constraints:**

1. **Detect before you judge** -- Always determine the target framework, hosting model, and pattern choices before applying any checklist item. A rule that applies to Blazor Server may be irrelevant to WASM, and a .NET Framework 4.x project cannot be graded against .NET 10 patterns.
2. **Checklist completeness** -- Every section of `references/review-checklist.md` is executed. Skipping a section requires explicit justification in the report.
3. **Evidence-based findings** -- Every finding must reference a specific file, line, or pattern match. Vague observations like "could be better" are not findings.
4. **Grade reflects reality** -- The grading scale is objective: count of critical, high, and medium findings determines the grade, not subjective impression.
5. **Recommendations match the stack** -- Never recommend patterns or APIs that do not exist in the detected target framework version. A .NET 6 project cannot use .NET 10 features.

## Domain Principles Table

| # | Principle | Description | Priority |
|---|-----------|-------------|----------|
| 1 | **Vertical Slice Compliance** | Features are organized by business capability, not technical layer. Each feature folder contains its commands, queries, handlers, validators, and DTOs. Cross-feature imports are violations. See `references/cqrs-patterns.md` Vertical Slice Validation section. | Critical |
| 2 | **CQRS Handler Isolation** | Each handler is a standalone class implementing `IRequestHandler<TRequest, TResponse>`. No shared base handlers, no handler-to-handler calls, no business logic in controllers. Commands mutate state; queries read it. Never both. See `references/cqrs-patterns.md` Handler Patterns section. | Critical |
| 3 | **FreeMediator Pipeline** | FreeMediator is the preferred CQRS library (Apache 2.0). Pipeline behaviors for validation, logging, exception handling, and transactions are registered in order. MediatR usage is flagged for migration. See `references/cqrs-patterns.md` Pipeline Behaviors section. | Critical |
| 4 | **Mapster Mapping Discipline** | `TypeAdapterConfig.GlobalSettings` is configured at startup, not per-request. Queries use `ProjectToType<>()` instead of `ToList().Adapt()`. Mapping profiles are organized by feature and centralized in dedicated config classes. See `references/cqrs-patterns.md` Mapster Checks section. | High |
| 5 | **Blazor Hosting Model Detection** | The hosting model (Server, WASM, Interactive Auto) determines which checklist items apply. Server requires SignalR circuit management and distributed backplane checks. WASM requires IL trimming and bundle security review. Auto requires render mode boundary validation. See `references/review-checklist.md` section 2. | Critical |
| 6 | **Shared Kernel Usage** | Projects consuming `Denali.LANL.*` shared NuGet packages must use official packages (not local copies), maintain version consistency, avoid duplicate entity definitions, and properly integrate EF Core configurations from the shared kernel. | High |
| 7 | **EF Core Patterns** | DbContext must be scoped correctly for the hosting model. Connection pooling must be sized for long-lived circuits. Async must be used all the way down. N+1 query patterns must be caught. Singleton DbContext is a critical finding. See `references/review-checklist.md` section 4. | Critical |
| 8 | **Framework Version Awareness** | The target framework version gates all recommendations. EOL frameworks (.NET Core 3.1, .NET 5, .NET 7) are flagged as critical. .NET Framework 4.x requires upgrade path assessment. Legacy project file format is flagged for SDK-style conversion. See `references/framework-detection.md`. | Critical |
| 9 | **Anti-Corruption Layers** | Boundaries between the application and external systems (APIs, legacy databases, third-party services) must be explicit. No domain entities should leak across API boundaries. DTOs and mapping exist at every boundary. | High |
| 10 | **Configuration Patterns** | No hardcoded secrets or connection strings. Configuration uses `IOptions<T>` or `IOptionsSnapshot<T>`. Environment-specific settings use proper configuration providers. WASM bundles must not contain secrets. See `references/red-flags.md` Security section. | High |

## Workflow

### Architecture Checklist Lifecycle

```
+----------------------------------------------------------------------+
|                Architecture Checklist Lifecycle                        |
|                                                                        |
|  +--------+    +------+    +--------+    +-----------+                 |
|  | DETECT  |--->| SCAN  |--->| REPORT  |--->| RECOMMEND |                |
|  | Context |    | Items |    | Findings|    | Fixes     |                |
|  +--------+    +------+    +--------+    +-----------+                 |
|      |             |            |              |                        |
|      |  If unknown |  If items  |              |                        |
|      |  framework  |  blocked   |              |                        |
|      v             v            |              |                        |
|  +----------+  +---------+     |              |                        |
|  | ASK USER |  | SKIP +  |     |              |                        |
|  | for info |  | JUSTIFY |     |              |                        |
|  +----------+  +---------+     |              |                        |
+----------------------------------------------------------------------+
```

### Phase 1: DETECT

Determine the full project context before running any checklist items.

1. **Target framework**: Scan all `.csproj` files for `<TargetFramework>` values. Categorize by EOL status. See `references/framework-detection.md`.
2. **Hosting model**: Identify Blazor Server, WASM, Interactive Auto, or non-Blazor ASP.NET Core.
3. **CQRS library**: Detect FreeMediator or MediatR usage. Flag MediatR for migration consideration.
4. **Mapping library**: Detect Mapster, AutoMapper, or manual mapping.
5. **UI framework**: Detect Telerik, MudBlazor, Radzen, or vanilla Blazor.
6. **Shared kernel**: Check for `Denali.LANL.*` package references.
7. **Infrastructure**: Identify Azure, GCP, on-prem, or hybrid hosting.
8. **Project style**: Verify SDK-style projects. Flag legacy project files.

```bash
# Comprehensive detection script
grep -r "<TargetFramework" --include="*.csproj" | grep -oE "net[0-9]+\.[0-9]+|netcoreapp[0-9]+\.[0-9]+|net4[0-9]+" | sort -u
grep -r "FreeMediator\|MediatR\|Mapster\|AutoMapper" --include="*.csproj"
grep -r "TelerikRootComponent\|MudThemeProvider\|RadzenLayout" --include="*.razor" | head -5
grep -rE "Denali\.LANL\." --include="*.csproj"
find . -name "*.csproj" -exec grep -L "Sdk=" {} \;
```

### Phase 2: SCAN

Execute every section of `references/review-checklist.md` and every pattern in `references/red-flags.md`. For each checklist item:

1. Run the associated detection command (grep, find, or code inspection)
2. Record the result as PASS, FAIL, WARN, or SKIP (with justification)
3. Capture the file path and line reference for any finding
4. Cross-reference CQRS-specific items with `references/cqrs-patterns.md`

**Checklist execution order** (from `references/review-checklist.md`):

- Section 0: Framework & Dependencies Pre-Check
- Section 1: Solution Structure & Patterns (including 1a: CQRS, 1b: Mapster)
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

Compile all findings into a structured report with grades.

1. Count findings by severity (Critical, High, Medium, Low)
2. Calculate grade using the grading formula
3. Identify the top 3 critical failure points
4. Generate the anti-patterns table
5. Compile the quick wins list
6. Build the technical debt register

**Grading Formula:**

- **A**: 0 critical, 0 high, <= 3 medium findings
- **B**: 0 critical, <= 2 high findings
- **C**: 0 critical, significant gaps in one area
- **D**: 1+ critical findings or gaps in multiple areas
- **F**: Fundamental architectural problems (EOL framework, singleton DbContext, missing auth)

### Phase 4: RECOMMEND

Generate prioritized recommendations that match the detected stack.

1. Filter all recommendations against the detected target framework version
2. Prioritize: Critical findings first, then quick wins, then modernization
3. Group recommendations by effort level (small, medium, large)
4. Reference specific skills for implementation guidance
5. Provide migration paths for framework upgrades when applicable

## State Block Format

Maintain state across conversation turns using this block:

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

### Example State Progression

```
<dotnet-checklist-state>
mode: DETECT
target_framework: unknown
hosting_model: unknown
cqrs_compliant: not-applicable
freemediator_version: none
issues_found: critical:0 high:0 medium:0 low:0
last_action: Session initialized, scanning .csproj files
next_action: Determine target framework and hosting model
</dotnet-checklist-state>
```

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

```
<dotnet-checklist-state>
mode: RECOMMEND
target_framework: net8.0
hosting_model: server
cqrs_compliant: partial
freemediator_version: mediatr-detected
issues_found: critical:1 high:4 medium:7 low:3
last_action: Report generated with grade C
next_action: Prioritize recommendations by effort and impact
</dotnet-checklist-state>
```

## Output Templates

### Session Opening (with Context Detection)

```markdown
## Architecture Checklist: [Solution Name]

**Date**: [Review Date]

### Detected Context
| Property | Value |
|----------|-------|
| Target Framework | [net8.0 / net10.0 / mixed] |
| Hosting Model | [Blazor Server / WASM / Auto / Non-Blazor] |
| CQRS Library | [FreeMediator / MediatR / None] |
| Mapping Library | [Mapster / AutoMapper / Manual / None] |
| UI Framework | [Telerik / MudBlazor / Vanilla] |
| Shared Kernel | [Denali.LANL.* / None] |
| Project Style | [SDK-style / Legacy] |
| Projects Scanned | [count] |

<dotnet-checklist-state>
mode: DETECT
target_framework: [detected]
hosting_model: [detected]
...
</dotnet-checklist-state>

Proceeding to SCAN phase with [N] checklist sections applicable.
```

### Checklist Results Table

```markdown
### Checklist Results

| # | Section | Items | Pass | Fail | Warn | Skip |
|---|---------|-------|------|------|------|------|
| 0 | Framework & Dependencies | 8 | 6 | 1 | 1 | 0 |
| 1 | Solution Structure | 12 | 10 | 2 | 0 | 0 |
| 1a | CQRS / FreeMediator | 10 | 7 | 2 | 1 | 0 |
| 1b | Mapster | 6 | 4 | 1 | 1 | 0 |
| 2 | Blazor Hosting | 6 | 5 | 0 | 1 | 0 |
| ... | ... | ... | ... | ... | ... | ... |
| **Total** | | **[N]** | **[N]** | **[N]** | **[N]** | **[N]** |
```

### Finding Details

```markdown
### Findings

#### CRITICAL: [Finding Title]
- **Section**: [Checklist section]
- **Location**: `[file path]:[line number]`
- **Evidence**: `[code snippet or grep output]`
- **Impact**: [What breaks, what risk exists]
- **Recommendation**: [Specific fix with code example]
- **Reference**: See `references/[relevant-file].md`

#### HIGH: [Finding Title]
- **Section**: [Checklist section]
- **Location**: `[file path]`
- **Evidence**: `[pattern match]`
- **Impact**: [Performance, maintainability, or security concern]
- **Recommendation**: [Specific fix]
```

### Session Closing (with Prioritized Recommendations)

```markdown
## Architecture Review: [Solution Name]

**Context**: [Blazor Server|WASM|Auto] on [Azure|GCP|On-Prem]
**Date**: [Review Date]

### Grade: [A-F]
[One sentence rationale based on finding counts]

### Critical Failure Points
Where this fails first under load:
1. [Most critical failure scenario]
2. [Second most critical]
3. [Third most critical]

### Anti-Patterns Detected
| Issue | Location | Severity |
|-------|----------|----------|
| [pattern name] | [file/path] | Critical/High/Medium |

### Quick Wins
Low-effort, high-impact fixes:
1. [Fix with highest ROI]
2. [Second highest]
3. [Third highest]

### Modernization Opportunities
Framework-appropriate improvements:
1. [Opportunity matched to detected framework version]

### Technical Debt Register
| Item | Priority | Effort | Impact |
|------|----------|--------|--------|
| [debt item] | P1/P2/P3 | S/M/L | S/M/L |

<dotnet-checklist-state>
mode: COMPLETE
target_framework: [detected]
hosting_model: [detected]
cqrs_compliant: [final assessment]
freemediator_version: [detected]
issues_found: critical:N high:N medium:N low:N
last_action: Recommendations delivered
next_action: Session complete
</dotnet-checklist-state>
```

## AI Discipline Rules

### CRITICAL: Always Detect Framework First

Before running any checklist item, determine the target framework version. A checklist item that references `IAsyncEnumerable` is irrelevant to a .NET Framework 4.8 project. A recommendation to use `InteractiveAutoRenderMode` is invalid for .NET 6.

1. Scan all `.csproj` files for `<TargetFramework>` and `<TargetFrameworks>`
2. Record the framework version in the state block
3. Gate all subsequent checklist items against the detected version
4. If mixed frameworks are detected, note which items apply to which projects

If the framework cannot be determined, ASK the user. Never assume .NET 10.

### CRITICAL: Never Assume Hosting Model

Blazor Server, WASM, and Interactive Auto have fundamentally different architectural concerns:

- **Server**: Circuit management, SignalR backplane, connection pooling for persistent circuits
- **WASM**: Bundle size, secret exposure, IL trimming, client-side performance
- **Auto**: Render mode boundaries, prerendering state persistence, dual-mode component design

Running the wrong section of the checklist produces false positives. Detect the hosting model from project configuration, `Program.cs`, and component render modes before proceeding.

```bash
# Detect hosting model
grep -r "AddServerSideBlazor\|MapBlazorHub\|AddInteractiveServerRenderMode" --include="*.cs"
grep -r "AddInteractiveWebAssemblyRenderMode\|WebAssemblyHostBuilder" --include="*.cs"
grep -r "RenderMode\.\|@rendermode" --include="*.razor" --include="*.cs" | head -10
```

### CRITICAL: Check Handler Isolation Before Patterns

When reviewing CQRS implementations, verify handler isolation (no base classes, no cross-handler calls) before assessing pattern quality (naming, folder structure, pipeline behaviors). A codebase with well-named handlers that all inherit from `BaseCrudHandler<T>` has a critical structural problem that must be reported before pattern refinements.

1. Check for handler inheritance: `grep -r "class.*Handler.*:.*Base\|abstract.*Handler" --include="*.cs"`
2. Check for handler-to-handler calls: `grep -r "IMediator\|ISender" --include="*Handler.cs"`
3. Only after isolation is confirmed, assess naming conventions and folder structure

### CRITICAL: Validate Mapster Configs Exist

If the project uses Mapster, verify that `TypeAdapterConfig` is configured at startup. Projects that use `.Adapt<T>()` without explicit configuration rely on Mapster's convention-based mapping, which silently produces incomplete DTOs when entity shapes change. This is a high-severity finding.

```bash
# Must find startup config
grep -r "TypeAdapterConfig\|IRegister\|MapsterConfig" --include="*.cs"

# Flag inline config in handlers or controllers
grep -r "\.NewConfig()\|\.ForType<" --include="*Handler.cs" --include="*Controller.cs"
```

### CRITICAL: Do Not Mix Architectural Styles in Recommendations

If the codebase uses vertical slices with CQRS, never recommend repository pattern, service layer, or traditional layered architecture improvements. If the codebase uses layered architecture, never recommend vertical slice refactoring without flagging it as a major migration effort. Recommendations must be consistent with the detected architectural style.

1. Detect the predominant pattern: vertical slices (`Features/` folders) vs layers (`Controllers/`, `Services/`, `Repositories/`)
2. Tailor all recommendations to the detected style
3. If recommending a style change, flag it as a separate migration initiative with effort estimate

### HIGH: Version-Gate All Recommendations

Every recommendation must be valid for the detected target framework version. Before suggesting any API, pattern, or feature:

1. Verify it exists in the detected .NET version
2. If it requires a newer version, note the minimum required version
3. Never recommend .NET 10 features to a .NET 6 project without framing it as a post-upgrade opportunity

## Anti-Patterns Table

| Anti-Pattern | Why It's Wrong | Correct Approach |
|--------------|----------------|------------------|
| **Reviewing without framework detection** | Applying .NET 10 best practices to a .NET Framework 4.8 project produces irrelevant findings. Grading against the wrong standard erodes trust in the review. | Always run DETECT phase first. Gate every checklist item against the detected framework version. |
| **Applying .NET 10 patterns to .NET Framework** | APIs like `IAsyncEnumerable`, Minimal APIs, `InteractiveAutoRenderMode`, and record types do not exist in .NET Framework 4.x. Recommending them without an upgrade path is unhelpful. | Detect framework version. Recommend upgrade path via `references/framework-detection.md`. Only suggest patterns available in the current version. |
| **Ignoring shared kernel conventions** | Duplicating entities (Person, Organization, Location) that exist in `Denali.LANL.*` packages creates drift, inconsistency, and maintenance burden across the enterprise. | Check for `Denali.LANL.*` package references. Flag duplicate entity definitions. Verify version consistency across all shared packages. |
| **Mixing CQRS with repository pattern** | Adding a repository layer on top of CQRS handlers creates unnecessary abstraction. Handlers already encapsulate data access. A repository between the handler and DbContext adds indirection without benefit. | Handlers access DbContext directly. If data access logic is reused, extract it to a specification or query object, not a repository. |
| **Fat controllers with business logic** | Business logic in controllers cannot be tested without HTTP infrastructure. It violates the thin-endpoint principle and makes the CQRS pipeline irrelevant. | Controllers call only `mediator.Send()`. All business logic lives in handlers. Validation lives in pipeline behaviors. |
| **Grading without evidence** | Subjective assessments ("the code looks messy") are not findings. Without file paths, line numbers, or pattern matches, findings cannot be verified or acted upon. | Every finding must include a specific file location, evidence string, and checklist section reference. |
| **Assuming Blazor Server for all Blazor projects** | WASM and Interactive Auto have completely different architectural concerns. Server-specific recommendations (circuit management, SignalR backplane) are noise for WASM projects. | Detect hosting model from project configuration before applying hosting-specific checklist items. |
| **Recommending framework upgrade without complexity assessment** | Telling a team to "upgrade to .NET 10" without assessing System.Web dependencies, WCF usage, binary serialization, and legacy project files is irresponsible. | Use `references/framework-detection.md` to assess upgrade complexity (Low/Medium/High). Provide a phased upgrade plan. |
| **Skipping Telerik-specific checks for Telerik projects** | Telerik Grid with `Data` parameter on large datasets causes full-data loading. Missing `TelerikRootComponent` causes silent failures. Version mismatches cause runtime errors. These are common and impactful. | Always run Section 11 of the checklist when Telerik UI is detected. Check grid binding, theming, licensing, and version alignment. See `references/red-flags.md` Telerik-Specific section. |
| **Singleton DbContext in Blazor Server** | Blazor Server circuits are long-lived. A singleton DbContext causes connection exhaustion, stale data, and thread-safety violations. This is a critical production risk. | DbContext must be scoped. Use `OwningComponentBase` or `IDbContextFactory<T>` for proper lifetime management in Blazor Server. |

## Error Recovery

### Problem: Unknown Framework Version

The `.csproj` files are missing, inaccessible, or use non-standard `<TargetFramework>` values.

**Action:**
1. Check if the solution file (`.sln`) exists and lists project paths
2. Search for `global.json` which may specify the SDK version
3. Look for `Directory.Build.props` which may set `<TargetFramework>` centrally
4. Inspect NuGet package versions as a proxy (e.g., `Microsoft.AspNetCore.Components` version indicates .NET version)
5. If framework cannot be determined, ask the user directly. Record "unknown" in the state block and note which checklist items were skipped due to framework uncertainty

```bash
# Fallback detection strategies
cat global.json 2>/dev/null
grep -r "<TargetFramework" Directory.Build.props 2>/dev/null
grep -r "Microsoft.AspNetCore" --include="*.csproj" | grep -oE "[0-9]+\.[0-9]+\.[0-9]+" | sort -u
```

### Problem: Mixed CQRS and Repository Patterns

The codebase uses FreeMediator handlers in some features but also has a `Repositories/` folder with `IRepository<T>` interfaces consumed by other features.

**Action:**
1. Identify which features use CQRS handlers and which use repositories
2. Do NOT recommend ripping out repositories immediately -- this is a migration path
3. Report the architectural inconsistency as a HIGH finding
4. Recommend a migration plan: new features use CQRS exclusively, existing repository features migrate incrementally
5. Flag any handlers that inject repositories (double indirection) as a separate finding
6. Reference `dotnet-vertical-slice` for the target CQRS architecture

### Problem: Legacy Code Without Tests

The project has no test projects, no test frameworks referenced, and no `*Tests.cs` files.

**Action:**
1. Report missing tests as a HIGH finding (not critical -- the code may still function correctly)
2. Do NOT recommend retroactively unit-testing the entire codebase -- this is impractical
3. Recommend a "test-forward" strategy: all new features and bug fixes include tests
4. Identify the highest-risk handlers (those with complex business logic, data access, or external calls) as priority candidates for retroactive testing
5. Reference `tdd-cycle` for the testing methodology
6. Suggest adding a test project scaffold as a quick win

### Problem: Blazor Interactive Auto with Unclear Render Mode Boundaries

The project uses `.NET 8+` Interactive Auto but components do not explicitly declare render modes, leading to unpredictable server/client execution.

**Action:**
1. Check for explicit `@rendermode` directives on components
2. Flag components without explicit render modes as MEDIUM findings
3. Identify components that access server-only resources (DbContext, file system) -- these must be Server-rendered
4. Identify components with heavy client interaction -- these benefit from WASM rendering
5. Recommend explicit `@rendermode InteractiveServer` or `@rendermode InteractiveWebAssembly` on every interactive component
6. Flag any component that works in both modes but assumes server-side resource access

## Integration with Other Skills

- **`dotnet-vertical-slice`** -- When the checklist identifies structural violations in CQRS/vertical slice organization (cross-feature imports, fat controllers, missing pipeline behaviors), reference this skill for the correct implementation patterns. The vertical slice skill defines the target architecture that this checklist validates against.

- **`ef-migration-manager`** -- When the checklist identifies EF Core issues (singleton DbContext, missing async patterns, N+1 queries, connection pooling problems), reference this skill for migration and data access lifecycle management. DbContext lifetime issues in Blazor Server are particularly critical and may require `IDbContextFactory<T>` patterns documented in this skill.

- **`architecture-review`** -- When the checklist produces a grade of D or F, recommend a full architecture review using this Socratic coaching skill. The checklist identifies _what_ is wrong; `architecture-review` helps the team understand _why_ and develop judgment for future decisions. The two skills are complementary: checklist for validation, review for education.

- **`legacy-migration-analyzer`** -- When the checklist detects .NET Framework 4.x projects, EOL frameworks, or legacy project file formats, reference this skill for comprehensive migration analysis. The checklist flags the version as a finding; `legacy-migration-analyzer` produces the full migration roadmap including dependency analysis, compatibility assessment, and phased upgrade plan.

- **`dotnet-security-review`** -- When the checklist identifies security findings (hardcoded secrets, missing auth attributes, WASM secret exposure, CORS misconfiguration), reference this skill for deeper security analysis. The checklist catches surface-level security patterns; `dotnet-security-review` provides comprehensive security posture assessment.

- **`dotnet-security-review-federal`** -- For LANL projects using `Denali.LANL.*` shared packages, reference this skill when the checklist identifies security findings that may have federal compliance implications.

## Reference Files

See detailed patterns, detection commands, and code examples:
- [Architecture Review Checklist](references/review-checklist.md) -- Full checklist with 11 sections covering framework, structure, hosting, state, data, security, API, observability, DI, testability, performance, and Telerik UI
- [CQRS Patterns: FreeMediator + Mapster](references/cqrs-patterns.md) -- FreeMediator migration, handler patterns, pipeline behaviors, Mapster configuration, vertical slice validation
- [Framework Detection & Upgrade Assessment](references/framework-detection.md) -- Quick detection scripts, project style detection, compatibility issues, upgrade complexity matrix
- [Red Flags Quick Reference](references/red-flags.md) -- Fast grep-based pattern matching for critical, high, and medium severity anti-patterns
