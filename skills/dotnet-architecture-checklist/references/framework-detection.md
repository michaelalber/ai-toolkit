# .NET Framework Detection & Upgrade Assessment

## Quick Framework Detection

```bash
# Comprehensive framework scan
grep -r "<TargetFramework" --include="*.csproj"

# Categorize findings
echo "=== .NET Framework 4.x (Legacy - Upgrade Required) ==="
grep -rE "<TargetFramework>net4[0-9]+</TargetFramework>" --include="*.csproj"

echo "=== .NET Core 3.x (EOL - Upgrade Immediately) ==="
grep -rE "<TargetFramework>netcoreapp3\.[0-9]+</TargetFramework>" --include="*.csproj"

echo "=== .NET 5 (EOL - Upgrade) ==="
grep -rE "<TargetFramework>net5\.0</TargetFramework>" --include="*.csproj"

echo "=== .NET 6 (LTS Ending Nov 2024) ==="
grep -rE "<TargetFramework>net6\.0</TargetFramework>" --include="*.csproj"

echo "=== .NET 7 (EOL May 2024) ==="
grep -rE "<TargetFramework>net7\.0</TargetFramework>" --include="*.csproj"

echo "=== .NET 8 (Current LTS) ==="
grep -rE "<TargetFramework>net8\.0</TargetFramework>" --include="*.csproj"

echo "=== .NET 9 (STS - Support ends May 2026) ==="
grep -rE "<TargetFramework>net9\.0</TargetFramework>" --include="*.csproj"

echo "=== .NET 10 (Latest LTS - Recommended) ==="
grep -rE "<TargetFramework>net10\.0</TargetFramework>" --include="*.csproj"
```

## Project Style Detection

```bash
# SDK-style projects (modern)
grep -l "Sdk=\"Microsoft.NET.Sdk" --include="*.csproj" -r

# Legacy-style projects (need conversion before upgrade)
find . -name "*.csproj" -exec grep -L "Sdk=" {} \;

# Check for packages.config (legacy - migrate to PackageReference)
find . -name "packages.config"

# Check for AssemblyInfo.cs (legacy - usually auto-generated in SDK projects)
find . -name "AssemblyInfo.cs" | head -10
```

## Framework Compatibility Issues

### Namespace Changes (.NET Framework → .NET)

```bash
# System.Web (not available in .NET Core/5+)
grep -r "using System.Web" --include="*.cs"

# System.Configuration (replaced by Microsoft.Extensions.Configuration)
grep -r "ConfigurationManager" --include="*.cs"

# Windows-specific (needs Windows TFM)
grep -r "using System.Windows.Forms\|using System.Drawing" --include="*.cs"

# WCF client (needs System.ServiceModel packages)
grep -r "using System.ServiceModel" --include="*.cs"

# Binary serialization (security concern, not recommended)
grep -r "BinaryFormatter\|ISerializable" --include="*.cs"
```

### Package Compatibility

```bash
# Check for .NET Framework-only packages
grep -rE "Microsoft\.AspNet\." --include="*.csproj"
grep -rE "System\.Web\." --include="*.csproj"

# Check for packages needing replacement
grep -r "Newtonsoft.Json" --include="*.csproj"  # Consider System.Text.Json
grep -r "log4net\|NLog" --include="*.csproj"    # Consider Serilog or MS.Extensions.Logging
grep -r "Unity\|Autofac\|Ninject" --include="*.csproj"  # Consider built-in DI
```

## Upgrade Complexity Assessment

### Low Complexity
- SDK-style project
- No System.Web references
- No WCF services
- Standard NuGet packages

### Medium Complexity
- Legacy project file (needs conversion)
- Some namespace changes required
- Package replacements needed
- Unit tests need migration

### High Complexity
- System.Web.* dependencies
- WCF services (needs gRPC migration)
- Windows-specific APIs
- Custom MSBuild tasks
- Heavy reflection usage
- Binary serialization

## Framework-Specific Concerns

### .NET Framework 4.x Projects
- [ ] Uses SDK-style project file? (Required for upgrade)
- [ ] Has packages.config? (Migrate to PackageReference)
- [ ] WCF services? (Migrate to gRPC or REST)
- [ ] ASP.NET Web Forms? (Rewrite to Blazor)
- [ ] ASP.NET MVC? (Migrate to ASP.NET Core MVC or Blazor)
- [ ] Entity Framework 6? (Migrate to EF Core)
- [ ] System.Web dependencies? (Replace with ASP.NET Core equivalents)

### .NET 6/7 Projects Upgrading to .NET 10
- [ ] Check for deprecated APIs
- [ ] Review breaking changes in each version
- [ ] Update minimal API syntax if applicable
- [ ] Review new language features to adopt

## Recommended Actions by Framework

| Current Framework | Action | Priority |
|-------------------|--------|----------|
| net48, net472 | Full migration to .NET 10 | Critical |
| netcoreapp3.1 | Upgrade to .NET 10 | Critical (EOL) |
| net5.0 | Upgrade to .NET 10 | High (EOL) |
| net6.0 | Plan upgrade to .NET 10 | Medium (LTS ending) |
| net7.0 | Upgrade to .NET 10 | High (EOL) |
| net8.0 | Maintain, upgrade when convenient | Low |
| net9.0 | Upgrade to .NET 10 for LTS | Medium |
| net10.0 | Current target | None |
