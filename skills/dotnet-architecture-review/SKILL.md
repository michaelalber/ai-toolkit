---
name: dotnet-architecture-review
description: Conducts rigorous architecture reviews of .NET Blazor applications using CQRS patterns. Use when asked to review architecture, audit code quality, assess technical debt, evaluate Blazor projects, check for anti-patterns, review .NET solutions, or validate FreeMediator/Mapster usage. Triggers on phrases like "review this project", "architecture review", "audit this code", "check for issues", "evaluate this solution", "review CQRS patterns", "check handlers", "check framework version", "shared kernel review".
---

# .NET Blazor Architecture Review

Conduct architecture reviews using Well-Architected Framework principles for .NET Blazor applications.

## Quick Start

When triggered, determine context first:
1. **Target framework**: .NET Framework 4.x or .NET 6/8/10+?
2. **Hosting model**: Blazor Server, WASM, or Interactive Auto?
3. **Infrastructure**: Azure, GCP, on-prem?
4. **UI framework**: Telerik, MudBlazor, Radzen, vanilla?
5. **Shared kernel**: Using LANL shared NuGet packages?

Then run the review using the checklist in `references/review-checklist.md`.

If using CQRS with FreeMediator/Mapster, also check `references/cqrs-patterns.md`.

For .NET Framework detection and upgrade assessment, see `references/framework-detection.md`.

## Review Process

1. **Scan solution structure**: `find . -name "*.csproj" -o -name "*.sln" | head -20`
2. **Check for red flags**: See `references/red-flags.md` for quick pattern matching
3. **Deep dive by category**: Use full checklist for thorough review
4. **Generate report**: Use output format below

## Output Format

```markdown
## Architecture Review: [Solution Name]

**Context**: [Blazor Server|WASM|Auto] on [Azure|GCP|On-Prem]
**Date**: [Review Date]

### Grade: [A-F]
[One sentence rationale]

### Critical Failure Points
Where this fails first under load:
1. ...

### Anti-Patterns Detected
| Issue | Location | Severity |
|-------|----------|----------|
| ... | ... | High/Med/Low |

### Quick Wins
Low-effort, high-impact fixes:
1. ...

### Modernization Opportunities
.NET 9+ features applicable:
1. ...

### Technical Debt Register
| Item | Priority | Effort | Impact |
|------|----------|--------|--------|
| ... | P1/P2/P3 | S/M/L | S/M/L |
```

## Grading Scale

- **A**: Production-ready, follows best practices, observable, testable
- **B**: Solid foundation, minor improvements needed
- **C**: Functional but has significant gaps in one area
- **D**: Multiple architectural issues, needs refactoring
- **F**: Fundamental problems, consider rewrite

## Key Decision Points

**Circuit State**: If storing user state in circuit memory → flag as critical risk
**Grid Data**: If Telerik Grid uses `Data` instead of `OnRead` with large datasets → flag perf issue
**DbContext Lifetime**: If singleton or incorrectly scoped → flag as critical
**Auth Tokens**: If tokens visible in WASM → flag as security issue
**Mediator Library**: FreeMediator preferred over MediatR (see below)
**Framework Version**: .NET Framework 4.x requires upgrade path assessment

## Framework Detection

Detect target framework version early to guide review approach:

```bash
# Check target framework(s) across all projects
grep -r "<TargetFramework" --include="*.csproj" | grep -oE "net[0-9]+\.[0-9]+|netcoreapp[0-9]+\.[0-9]+|net4[0-9]+" | sort -u

# Identify .NET Framework 4.x projects (need upgrade)
grep -rE "<TargetFramework>net4[0-9]+</TargetFramework>" --include="*.csproj"

# Check for multi-targeting
grep -r "<TargetFrameworks>" --include="*.csproj"

# Identify SDK-style vs old-style projects
grep -L "Sdk=" *.csproj  # Old-style (needs conversion)
```

**Framework Version Impact:**
- **net48/net472**: Legacy .NET Framework - flag for upgrade to .NET 10 LTS
- **netcoreapp3.1**: End-of-life - upgrade immediately
- **net6.0**: LTS ends Nov 2024 - plan upgrade
- **net8.0**: Current LTS - good for production
- **net10.0**: Latest LTS - recommended for new projects

## FreeMediator vs MediatR Detection

FreeMediator is the preferred CQRS library (Apache 2.0 license, no commercial restrictions):

```bash
# Check which mediator library is in use
grep -r "MediatR\|FreeMediator" --include="*.csproj"
grep -r "using MediatR\|using FreeMediator" --include="*.cs" | head -5

# FreeMediator registration pattern
grep -r "AddFreeMediator" --include="*.cs"

# MediatR registration pattern (consider migration)
grep -r "AddMediatR" --include="*.cs"
```

**Migration Guidance:**
- MediatR → FreeMediator: API-compatible, change package reference and using statements
- FreeMediator maintains same `IRequest<T>`, `IRequestHandler<,>` interfaces

## Shared Kernel Validation

For projects consuming LANL shared NuGet packages:

```bash
# Check for shared kernel package references
grep -rE "Denali\.LANL\.(People|Training|Organization|Location|Workflow|Communication)" --include="*.csproj"

# Verify consistent versions across all shared packages
grep -r "Denali.LANL" --include="*.csproj" | grep -oE "[0-9]+\.[0-9]+\.[0-9]+" | sort -u

# Check for duplicated entity definitions (should use shared kernel)
grep -r "class Person\|class Employee\|class Organization\|class Location" --include="*.cs" | grep -v "\.Denali\.LANL\."
```

**Shared Kernel Checklist:**
- [ ] Using official `Denali.LANL.*` packages (not local copies)?
- [ ] All shared packages on same version?
- [ ] No duplicate entity definitions that should come from shared kernel?
- [ ] EF Core configurations use shared `IEntityTypeConfiguration<T>`?
- [ ] DbContext includes shared entity DbSets via `modelBuilder.ApplyConfigurationsFromAssembly()`?
