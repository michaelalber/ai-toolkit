---
name: dotnet-framework-upgrade
description: Analyzes .NET Framework 4.x codebases and generates upgrade path to .NET 10+ LTS. Use when upgrading legacy .NET Framework projects, migrating to .NET Core/5+, or assessing upgrade complexity. Triggers on phrases like "upgrade framework", "migrate to .net 10", "framework to core", "legacy .net", ".net framework upgrade", "modernize .net".
---

# .NET Framework to .NET 10 Upgrade

> "Upgrading from .NET Framework is not just changing a version number—it's migrating to a fundamentally different runtime with different APIs, hosting models, and deployment patterns."

This skill guides the upgrade from .NET Framework 4.x to .NET 10 LTS (or .NET 8 LTS).

## Quick Start

1. **Analyze project files**: SDK-style vs legacy `.csproj` format
2. **Scan for blockers**: System.Web, WCF, Windows-only APIs
3. **Check dependencies**: Use `references/package-replacement-map.md`
4. **Generate upgrade plan**: Prioritize by complexity
5. **Execute incrementally**: Convert one project at a time

## Target Framework Recommendations

| Scenario | Target |
|----------|--------|
| New projects | .NET 10 (latest LTS) |
| Production upgrades | .NET 10 or .NET 8 (current LTS) |
| Shared libraries | Multi-target if needed |

## Analysis Process

### Step 1: Project Inventory

```bash
# Find all project files
find . -name "*.csproj" -o -name "*.vbproj" -o -name "*.fsproj"

# Check target frameworks
grep -r "<TargetFramework" --include="*.csproj" | sort -u

# Identify SDK-style vs legacy projects
find . -name "*.csproj" -exec grep -L "Sdk=" {} \;  # Legacy format

# Check for packages.config (needs migration)
find . -name "packages.config"

# Check solution structure
find . -name "*.sln" -exec cat {} \;
```

### Step 2: Dependency Analysis

```bash
# Find package references (SDK-style)
grep -r "<PackageReference" --include="*.csproj"

# Find packages.config references (legacy)
grep -r "<package " --include="packages.config"

# Identify .NET Framework-specific packages
grep -rE "System\.Web\.|Microsoft\.AspNet\." --include="*.csproj" --include="packages.config"

# Check for in-house/private packages
grep -r "PrivateAssets\|internal\." --include="*.csproj"
```

### Step 3: API Compatibility Scan

```bash
# System.Web dependencies (major blocker)
grep -r "using System\.Web" --include="*.cs" | wc -l
grep -r "System\.Web\." --include="*.cs" | head -20

# WCF usage (needs alternative)
grep -r "using System\.ServiceModel" --include="*.cs"
grep -r "ServiceContract\|OperationContract" --include="*.cs"

# Windows-specific APIs
grep -r "using System\.Windows\.Forms" --include="*.cs"
grep -r "using System\.Drawing" --include="*.cs"

# ConfigurationManager (needs replacement)
grep -r "ConfigurationManager" --include="*.cs"

# Binary serialization (security concern)
grep -r "BinaryFormatter" --include="*.cs"

# App.config/Web.config usage
find . -name "*.config" -type f
grep -r "appSettings\|connectionStrings" --include="*.config"
```

### Step 4: Generate Upgrade Report

See Output Format section below.

## Upgrade Strategies

### Strategy 1: In-Place Upgrade (Recommended for most projects)
1. Convert `.csproj` to SDK-style
2. Update target framework to `net10.0`
3. Replace incompatible packages
4. Fix breaking API changes
5. Update configuration to `appsettings.json`

### Strategy 2: Parallel Migration (For complex apps)
1. Create new .NET 10 project alongside legacy
2. Copy/migrate code file by file
3. Share database via EF Core
4. Run both in parallel during transition

### Strategy 3: Strangler Fig (For monoliths)
1. Extract features as new .NET 10 microservices
2. Route requests to new services
3. Gradually replace legacy components
4. Decommission old app when empty

## Project File Conversion

### Legacy `.csproj` Format
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

### SDK-Style `.csproj` Format (Target)
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

### Web Project SDK-Style
```xml
<Project Sdk="Microsoft.NET.Sdk.Web">

  <PropertyGroup>
    <TargetFramework>net10.0</TargetFramework>
  </PropertyGroup>

</Project>
```

## Output Format

```markdown
## .NET Framework Upgrade Analysis: [Solution Name]

**Source Framework**: .NET Framework [4.x]
**Target Framework**: .NET 10 LTS
**Date**: [Analysis Date]

### Executive Summary
[2-3 sentences on overall complexity and timeline]

### Project Inventory

| Project | Type | Current Framework | Upgrade Complexity |
|---------|------|-------------------|-------------------|
| ... | Class Library | net48 | Low/Medium/High |
| ... | Web App | net472 | High |

### Blocking Issues

| Issue | Projects Affected | Remediation |
|-------|-------------------|-------------|
| System.Web dependency | 3 | Replace with ASP.NET Core |
| WCF Services | 1 | Migrate to gRPC or REST |
| packages.config | 5 | Convert to PackageReference |

### Package Replacements Required

| Current Package | Replacement | Notes |
|-----------------|-------------|-------|
| ... | ... | ... |

### API Changes Required

| Old API | New API | Files Affected |
|---------|---------|----------------|
| ConfigurationManager | IConfiguration | 12 |
| System.Web.HttpContext | HttpContext | 8 |

### Recommended Upgrade Order

1. **Shared libraries first** (no web dependencies)
2. **Data access layer** (EF6 → EF Core)
3. **Business logic** (after dependencies ready)
4. **Web/API layer** (last, most changes)

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| ... | High/Med/Low | High/Med/Low | ... |

### Next Steps

1. ...
2. ...
3. ...
```

## Complexity Classification

### Low Complexity (1-2 weeks)
- Class libraries with no web dependencies
- Console applications
- Already uses SDK-style project
- Standard NuGet packages only

### Medium Complexity (2-4 weeks)
- Web API (non-MVC)
- Entity Framework 6 → EF Core migration
- Some configuration changes
- Limited System.Web usage

### High Complexity (4-8+ weeks)
- Full ASP.NET MVC application
- Heavy System.Web dependencies
- WCF services
- Windows-specific features
- Custom MSBuild tasks
- Binary serialization

## References

- `references/breaking-changes-4x-to-10.md` - Breaking changes by version
- `references/package-replacement-map.md` - Package replacement guide
- `references/api-replacement-patterns.md` - API migration patterns
- `references/aspnet-to-blazor-patterns.md` - Web app migration patterns

## Tools

### .NET Upgrade Assistant
```bash
# Install
dotnet tool install -g upgrade-assistant

# Analyze solution
upgrade-assistant analyze <solution.sln>

# Upgrade project
upgrade-assistant upgrade <project.csproj>
```

### API Port (Compatibility Analysis)
```bash
# Install
dotnet tool install -g Microsoft.DotNet.ApiCompat.Tool

# Analyze
apicompat <assembly.dll> --target-framework net10.0
```

### try-convert (Project File Conversion)
```bash
# Install
dotnet tool install -g try-convert

# Convert project
try-convert -p <project.csproj>

# Convert solution
try-convert -w <solution.sln>
```
