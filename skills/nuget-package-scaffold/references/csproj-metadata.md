# .csproj Package Metadata Reference

## Required Metadata Properties

These properties must be set before any package is published. Omitting them results in NuGet warnings and degraded package quality on feeds.

| Property | Description | Example |
|----------|-------------|---------|
| `PackageId` | Unique package identifier. Convention: `Company.Product.Feature` | `Acme.Utilities.Json` |
| `Version` | SemVer 2.0.0 version string | `1.2.3` or `1.0.0-beta.1` |
| `Authors` | Comma-separated list of package authors | `Jane Doe, John Smith` |
| `Description` | Short summary displayed on nuget.org and in IDE search | `Lightweight JSON utilities for .NET` |
| `PackageLicenseExpression` | SPDX license identifier | `MIT` or `Apache-2.0` |
| `PackageProjectUrl` | URL to the project homepage or repository | `https://github.com/acme/utilities-json` |
| `RepositoryUrl` | Source repository URL (used by Source Link) | `https://github.com/acme/utilities-json.git` |
| `RepositoryType` | Source control type | `git` |

## Optional (Recommended) Metadata Properties

| Property | Description | Example |
|----------|-------------|---------|
| `PackageReadmeFile` | Path to README file to embed in the package | `README.md` |
| `PackageIcon` | Path to icon file to embed (128x128 PNG recommended) | `icon.png` |
| `PackageTags` | Space-separated tags for discoverability | `json serialization utilities` |
| `PackageReleaseNotes` | Release notes for the current version | `Fixed null handling in deserializer` |
| `Copyright` | Copyright notice | `Copyright 2025 Acme Inc.` |
| `Company` | Company or organization name | `Acme Inc.` |
| `Product` | Product name | `Acme Utilities` |
| `NeutralLanguage` | Default language for the assembly | `en-US` |
| `PackageRequireLicenseAcceptance` | Require license acceptance before install | `true` |

## Build and Compilation Properties

| Property | Description | Recommended Value |
|----------|-------------|-------------------|
| `TargetFrameworks` | Semicolon-separated target framework monikers | `net8.0;net9.0;net10.0` |
| `Nullable` | Enable nullable reference type analysis | `enable` |
| `ImplicitUsings` | Enable implicit global usings | `enable` |
| `LangVersion` | C# language version | `latest` |
| `TreatWarningsAsErrors` | Fail build on any warning | `true` |
| `WarningLevel` | Compiler warning level (0-9999) | `9999` |
| `AnalysisLevel` | Code analysis level | `latest-all` |
| `EnforceCodeStyleInBuild` | Enforce .editorconfig styles during build | `true` |

## Multi-Targeting Configuration

### Basic Multi-Target Setup

```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFrameworks>net8.0;net9.0;net10.0</TargetFrameworks>
  </PropertyGroup>
</Project>
```

### Multi-Target with .NET Standard

When you need to support older .NET Framework consumers or Xamarin:

```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFrameworks>netstandard2.0;net8.0;net9.0;net10.0</TargetFrameworks>
  </PropertyGroup>

  <!-- Polyfills for netstandard2.0 -->
  <ItemGroup Condition="'$(TargetFramework)' == 'netstandard2.0'">
    <PackageReference Include="System.Text.Json" Version="8.0.0" />
    <PackageReference Include="Microsoft.Bcl.AsyncInterfaces" Version="8.0.0" />
  </ItemGroup>
</Project>
```

### Conditional Compilation

Use preprocessor directives to handle API differences across targets:

```csharp
public static class StringExtensions
{
#if NET9_0_OR_GREATER
    public static bool ContainsIgnoreCase(this string source, string value)
        => source.Contains(value, StringComparison.OrdinalIgnoreCase);
#else
    public static bool ContainsIgnoreCase(this string source, string value)
        => source.IndexOf(value, StringComparison.OrdinalIgnoreCase) >= 0;
#endif
}
```

### Framework-Specific Dependencies

```xml
<ItemGroup Condition="'$(TargetFramework)' == 'netstandard2.0'">
  <PackageReference Include="System.Memory" Version="4.5.5" />
</ItemGroup>

<ItemGroup Condition="'$(TargetFramework)' == 'net8.0'">
  <!-- net8.0 includes System.Memory in-box -->
</ItemGroup>
```

## Source Link Configuration

Source Link embeds repository metadata in the PDB so debuggers can automatically download source files.

### GitHub Source Link

```xml
<PropertyGroup>
  <PublishRepositoryUrl>true</PublishRepositoryUrl>
  <EmbedUntrackedSources>true</EmbedUntrackedSources>
  <IncludeSymbols>true</IncludeSymbols>
  <SymbolPackageFormat>snupkg</SymbolPackageFormat>
</PropertyGroup>

<ItemGroup>
  <PackageReference Include="Microsoft.SourceLink.GitHub" Version="8.0.0" PrivateAssets="All" />
</ItemGroup>
```

### Azure DevOps Source Link

```xml
<ItemGroup>
  <PackageReference Include="Microsoft.SourceLink.AzureRepos.Git" Version="8.0.0" PrivateAssets="All" />
</ItemGroup>
```

### Bitbucket Source Link

```xml
<ItemGroup>
  <PackageReference Include="Microsoft.SourceLink.Bitbucket.Git" Version="8.0.0" PrivateAssets="All" />
</ItemGroup>
```

## Deterministic Build Settings

Deterministic builds ensure the same source code produces the same binary output regardless of build machine or time.

```xml
<PropertyGroup>
  <Deterministic>true</Deterministic>
  <ContinuousIntegrationBuild Condition="'$(CI)' == 'true'">true</ContinuousIntegrationBuild>
</PropertyGroup>
```

The `ContinuousIntegrationBuild` property normalizes file paths in PDBs during CI builds. It should only be enabled in CI -- not during local development -- to preserve the debugger experience.

## Strong Naming Setup

Strong naming is required when consumers demand it (e.g., some enterprise environments, certain .NET Framework hosting scenarios).

### Using a Key File

```xml
<PropertyGroup>
  <SignAssembly>true</SignAssembly>
  <AssemblyOriginatorKeyFile>$(MSBuildProjectDirectory)\..\keys\MyPackage.snk</AssemblyOriginatorKeyFile>
</PropertyGroup>
```

### Generating a Strong Name Key

```bash
# Generate a full key pair (keep private, do NOT commit)
sn -k MyPackage.snk

# Extract the public key only (safe to commit)
sn -p MyPackage.snk MyPackage.pub.snk

# Delay-sign during local development, full-sign in CI
```

### Delay Signing

```xml
<PropertyGroup>
  <SignAssembly>true</SignAssembly>
  <DelaySign>true</DelaySign>
  <AssemblyOriginatorKeyFile>MyPackage.pub.snk</AssemblyOriginatorKeyFile>
</PropertyGroup>
```

**Important**: Strong naming is NOT a security mechanism. It provides identity, not trust. Do not confuse strong naming with Authenticode signing.

## README and Icon Packaging

### Embedding a README

```xml
<PropertyGroup>
  <PackageReadmeFile>README.md</PackageReadmeFile>
</PropertyGroup>

<ItemGroup>
  <None Include="..\..\README.md" Pack="true" PackagePath="\" />
</ItemGroup>
```

The `PackagePath="\"` places the README at the package root where NuGet expects it.

### Embedding an Icon

```xml
<PropertyGroup>
  <PackageIcon>icon.png</PackageIcon>
</PropertyGroup>

<ItemGroup>
  <None Include="..\..\icon.png" Pack="true" PackagePath="\" />
</ItemGroup>
```

Requirements for the icon:
- PNG format
- 128x128 pixels (displayed at 64x64 on nuget.org)
- Transparent background recommended
- Keep file size under 1MB

## License Expression vs. License File

### SPDX License Expression (Preferred)

```xml
<PropertyGroup>
  <PackageLicenseExpression>MIT</PackageLicenseExpression>
</PropertyGroup>
```

Common SPDX identifiers: `MIT`, `Apache-2.0`, `BSD-2-Clause`, `BSD-3-Clause`, `LGPL-3.0-only`, `GPL-3.0-only`.

For dual licensing:
```xml
<PackageLicenseExpression>MIT OR Apache-2.0</PackageLicenseExpression>
```

### License File (When SPDX Is Not Sufficient)

```xml
<PropertyGroup>
  <PackageLicenseFile>LICENSE</PackageLicenseFile>
</PropertyGroup>

<ItemGroup>
  <None Include="..\..\LICENSE" Pack="true" PackagePath="\" />
</ItemGroup>
```

**Note**: `PackageLicenseExpression` and `PackageLicenseFile` are mutually exclusive. Do not set both.

### Deprecated: License URL

The `PackageLicenseUrl` property is deprecated and should not be used for new packages. Migrate to expression or file.

## Example: Complete Library .csproj

```xml
<Project Sdk="Microsoft.NET.Sdk">

  <PropertyGroup>
    <!-- Package Identity -->
    <PackageId>Acme.Utilities.Json</PackageId>
    <Version>1.0.0</Version>
    <Authors>Acme Engineering</Authors>
    <Company>Acme Inc.</Company>
    <Description>Lightweight JSON utilities for .NET applications. Provides extension methods for serialization, deserialization, and JSON path queries.</Description>
    <Copyright>Copyright 2025 Acme Inc.</Copyright>

    <!-- Target Frameworks -->
    <TargetFrameworks>net8.0;net9.0;net10.0</TargetFrameworks>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
    <LangVersion>latest</LangVersion>

    <!-- Package Metadata -->
    <PackageLicenseExpression>MIT</PackageLicenseExpression>
    <PackageProjectUrl>https://github.com/acme/utilities-json</PackageProjectUrl>
    <RepositoryUrl>https://github.com/acme/utilities-json.git</RepositoryUrl>
    <RepositoryType>git</RepositoryType>
    <PackageTags>json serialization utilities extensions</PackageTags>
    <PackageReadmeFile>README.md</PackageReadmeFile>
    <PackageIcon>icon.png</PackageIcon>

    <!-- Build Quality -->
    <TreatWarningsAsErrors>true</TreatWarningsAsErrors>
    <AnalysisLevel>latest-all</AnalysisLevel>
    <EnforceCodeStyleInBuild>true</EnforceCodeStyleInBuild>

    <!-- Deterministic / Reproducible -->
    <Deterministic>true</Deterministic>
    <ContinuousIntegrationBuild Condition="'$(CI)' == 'true'">true</ContinuousIntegrationBuild>

    <!-- Source Link / Symbols -->
    <PublishRepositoryUrl>true</PublishRepositoryUrl>
    <EmbedUntrackedSources>true</EmbedUntrackedSources>
    <IncludeSymbols>true</IncludeSymbols>
    <SymbolPackageFormat>snupkg</SymbolPackageFormat>

    <!-- Documentation -->
    <GenerateDocumentationFile>true</GenerateDocumentationFile>
    <NoWarn>$(NoWarn);CS1591</NoWarn> <!-- Suppress missing XML doc warnings during development -->
  </PropertyGroup>

  <!-- Pack README and icon into the package -->
  <ItemGroup>
    <None Include="..\..\README.md" Pack="true" PackagePath="\" />
    <None Include="..\..\icon.png" Pack="true" PackagePath="\" />
  </ItemGroup>

  <!-- Source Link for GitHub -->
  <ItemGroup>
    <PackageReference Include="Microsoft.SourceLink.GitHub" Version="8.0.0" PrivateAssets="All" />
  </ItemGroup>

</Project>
```

## Example: Complete .NET Tool .csproj

A .NET tool is a special kind of NuGet package that contains a console application.

```xml
<Project Sdk="Microsoft.NET.Sdk">

  <PropertyGroup>
    <!-- Tool Identity -->
    <PackageId>Acme.Tools.CodeGen</PackageId>
    <Version>1.0.0</Version>
    <Authors>Acme Engineering</Authors>
    <Company>Acme Inc.</Company>
    <Description>Code generation tool for Acme project scaffolding. Generates boilerplate code from YAML templates.</Description>
    <Copyright>Copyright 2025 Acme Inc.</Copyright>

    <!-- Tool-Specific Properties -->
    <OutputType>Exe</OutputType>
    <TargetFramework>net9.0</TargetFramework>
    <PackAsTool>true</PackAsTool>
    <ToolCommandName>acme-codegen</ToolCommandName>

    <!-- Language Settings -->
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
    <LangVersion>latest</LangVersion>

    <!-- Package Metadata -->
    <PackageLicenseExpression>MIT</PackageLicenseExpression>
    <PackageProjectUrl>https://github.com/acme/tools-codegen</PackageProjectUrl>
    <RepositoryUrl>https://github.com/acme/tools-codegen.git</RepositoryUrl>
    <RepositoryType>git</RepositoryType>
    <PackageTags>codegen scaffolding tool dotnet-tool</PackageTags>
    <PackageReadmeFile>README.md</PackageReadmeFile>

    <!-- Build Quality -->
    <TreatWarningsAsErrors>true</TreatWarningsAsErrors>
    <AnalysisLevel>latest-all</AnalysisLevel>

    <!-- Deterministic / Reproducible -->
    <Deterministic>true</Deterministic>
    <ContinuousIntegrationBuild Condition="'$(CI)' == 'true'">true</ContinuousIntegrationBuild>

    <!-- Source Link / Symbols -->
    <PublishRepositoryUrl>true</PublishRepositoryUrl>
    <EmbedUntrackedSources>true</EmbedUntrackedSources>
    <IncludeSymbols>true</IncludeSymbols>
    <SymbolPackageFormat>snupkg</SymbolPackageFormat>
  </PropertyGroup>

  <ItemGroup>
    <None Include="..\..\README.md" Pack="true" PackagePath="\" />
  </ItemGroup>

  <ItemGroup>
    <PackageReference Include="Microsoft.SourceLink.GitHub" Version="8.0.0" PrivateAssets="All" />
  </ItemGroup>

</Project>
```

**Key differences from a library package:**
- `OutputType` is `Exe` instead of the default `Library`
- `PackAsTool` is `true` to indicate this is a .NET tool
- `ToolCommandName` defines the CLI command name after installation
- Typically targets a single framework (tools run on the developer machine, not in consumer projects)

## Directory.Build.props for Shared Properties

When a solution contains multiple packages, use `Directory.Build.props` to share common properties:

```xml
<Project>
  <PropertyGroup>
    <Authors>Acme Engineering</Authors>
    <Company>Acme Inc.</Company>
    <Copyright>Copyright 2025 Acme Inc.</Copyright>
    <PackageLicenseExpression>MIT</PackageLicenseExpression>
    <RepositoryType>git</RepositoryType>

    <!-- Shared Build Settings -->
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
    <LangVersion>latest</LangVersion>
    <TreatWarningsAsErrors>true</TreatWarningsAsErrors>
    <AnalysisLevel>latest-all</AnalysisLevel>
    <EnforceCodeStyleInBuild>true</EnforceCodeStyleInBuild>

    <!-- Shared Deterministic/Source Link -->
    <Deterministic>true</Deterministic>
    <ContinuousIntegrationBuild Condition="'$(CI)' == 'true'">true</ContinuousIntegrationBuild>
    <PublishRepositoryUrl>true</PublishRepositoryUrl>
    <EmbedUntrackedSources>true</EmbedUntrackedSources>
    <IncludeSymbols>true</IncludeSymbols>
    <SymbolPackageFormat>snupkg</SymbolPackageFormat>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="Microsoft.SourceLink.GitHub" Version="8.0.0" PrivateAssets="All" />
  </ItemGroup>
</Project>
```

## NuGet Pack Warning Reference

| Warning | Meaning | Fix |
|---------|---------|-----|
| `NU5048` | Both `PackageLicenseUrl` and `PackageLicenseExpression` are set | Remove `PackageLicenseUrl` |
| `NU5100` | Assembly not inside a `lib` or `ref` folder | Check `PackagePath` values |
| `NU5104` | Prerelease dependency in stable package | Either make the package prerelease or use a stable dependency |
| `NU5105` | SemVer 2.0.0 version (e.g., build metadata) | Only an issue if targeting legacy NuGet clients |
| `NU5118` | File not added to the package | Ensure `Pack="true"` is set on the item |
| `NU5125` | No README found at `PackageReadmeFile` path | Fix the path or add the file |
| `NU5128` | TFM dependency group missing | Add dependency entries for all `TargetFrameworks` |
| `NU5129` | TFM has no `ref` or `lib` assets | Check build output for missing assemblies |
| `NU5131` | README file exceeds size limit | Reduce README size (max 1MB) |
