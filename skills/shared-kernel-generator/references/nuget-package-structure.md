# NuGet Package Structure

## Package Naming Convention

```
DenaliDataSystems.{ModuleName}
```

Examples:
- `DenaliDataSystems.Core.Abstractions`
- `DenaliDataSystems.PickLists`
- `DenaliDataSystems.People`
- `DenaliDataSystems.Training`
- `DenaliDataSystems.Organization`
- `DenaliDataSystems.Location`
- `DenaliDataSystems.Workflow`
- `DenaliDataSystems.Communication`

## Solution Structure (Vertical Slice Architecture)

```
DenaliDataSystems.CoreLibrary/
├── src/
│   ├── DenaliDataSystems.Core.Abstractions/
│   │   ├── DenaliDataSystems.Core.Abstractions.csproj
│   │   ├── Attributes/
│   │   │   └── AuditedEntityAttribute.cs
│   │   ├── Contracts/
│   │   │   ├── IAuditable.cs
│   │   │   └── ISoftDeletable.cs
│   │   └── README.md
│   │
│   ├── DenaliDataSystems.PickLists/
│   │   ├── DenaliDataSystems.PickLists.csproj
│   │   ├── PickListsDependencyInjection.cs
│   │   ├── Extensions/
│   │   │   └── DenaliPickListsOptions.cs
│   │   ├── Features/
│   │   │   └── PickListFeature/
│   │   │       ├── Commands/
│   │   │       │   ├── CreatePickList/
│   │   │       │   ├── UpdatePickList/
│   │   │       │   └── DeletePickList/
│   │   │       ├── Queries/
│   │   │       │   ├── GetPickListById/
│   │   │       │   └── GetPickLists/
│   │   │       ├── Entities/
│   │   │       │   └── Models/
│   │   │       │       ├── PickList.cs
│   │   │       │       └── PickListItem.cs
│   │   │       └── Data/
│   │   │           ├── PickListDbContext.cs
│   │   │           └── Configurations/
│   │   │               ├── PickListConfiguration.cs
│   │   │               └── PickListItemConfiguration.cs
│   │   ├── Permissions/
│   │   │   └── PickListPermissions.cs
│   │   └── README.md
│   │
│   ├── DenaliDataSystems.People/
│   │   ├── DenaliDataSystems.People.csproj
│   │   ├── PeopleDependencyInjection.cs
│   │   ├── Extensions/
│   │   │   └── DenaliPeopleOptions.cs
│   │   ├── Features/
│   │   │   └── PersonFeature/
│   │   │       ├── Commands/
│   │   │       ├── Queries/
│   │   │       ├── Entities/
│   │   │       │   └── Models/
│   │   │       │       ├── Person.cs
│   │   │       │       └── Employee.cs
│   │   │       └── Data/
│   │   ├── Permissions/
│   │   └── README.md
│   │
│   └── [other modules...]
│
├── tests/
│   ├── DenaliDataSystems.PickLists.Tests/
│   │   ├── DenaliDataSystems.PickLists.Tests.csproj
│   │   ├── Features/
│   │   │   └── PickListFeature/
│   │   │       ├── Commands/
│   │   │       │   └── CreatePickListTests.cs
│   │   │       └── Queries/
│   │   │           └── GetPickListsTests.cs
│   │   └── TestFixture.cs
│   │
│   └── [other test projects...]
│
├── Directory.Build.props          # Shared MSBuild properties
├── Directory.Packages.props       # Central package management
├── global.json                    # SDK version
├── nuget.config                   # NuGet sources
├── DenaliDataSystems.CoreLibrary.sln
├── README.md
└── CHANGELOG.md
```

## Directory.Build.props

```xml
<Project>
  <PropertyGroup>
    <!-- Framework & Language -->
    <TargetFramework>net10.0</TargetFramework>
    <LangVersion>latest</LangVersion>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
    <TreatWarningsAsErrors>true</TreatWarningsAsErrors>

    <!-- Package Metadata -->
    <Authors>Denali Data Systems</Authors>
    <Company>Denali Data Systems</Company>
    <Copyright>Copyright (c) $(Company) $([System.DateTime]::Now.Year)</Copyright>
    <Product>DenaliDataSystems Core Library</Product>

    <!-- Repository -->
    <RepositoryUrl>https://github.com/denali/denali-core-library.git</RepositoryUrl>
    <RepositoryType>git</RepositoryType>
    <PublishRepositoryUrl>true</PublishRepositoryUrl>

    <!-- Versioning -->
    <VersionPrefix>1.0.0</VersionPrefix>
    <VersionSuffix></VersionSuffix>

    <!-- Package Features -->
    <GenerateDocumentationFile>true</GenerateDocumentationFile>
    <IncludeSymbols>true</IncludeSymbols>
    <SymbolPackageFormat>snupkg</SymbolPackageFormat>
    <EmbedUntrackedSources>true</EmbedUntrackedSources>
  </PropertyGroup>

  <!-- Source Link -->
  <ItemGroup>
    <PackageReference Include="Microsoft.SourceLink.GitHub" Version="8.0.0" PrivateAssets="All"/>
  </ItemGroup>
</Project>
```

## Directory.Packages.props (Central Package Management)

```xml
<Project>
  <PropertyGroup>
    <ManagePackageVersionsCentrally>true</ManagePackageVersionsCentrally>
  </PropertyGroup>

  <ItemGroup>
    <!-- EF Core -->
    <PackageVersion Include="Microsoft.EntityFrameworkCore" Version="10.0.0" />
    <PackageVersion Include="Microsoft.EntityFrameworkCore.SqlServer" Version="10.0.0" />
    <PackageVersion Include="Microsoft.EntityFrameworkCore.InMemory" Version="10.0.0" />
    <PackageVersion Include="Microsoft.EntityFrameworkCore.Tools" Version="10.0.0" />

    <!-- Extensions -->
    <PackageVersion Include="Microsoft.Extensions.DependencyInjection.Abstractions" Version="10.0.0" />
    <PackageVersion Include="Microsoft.Extensions.Logging.Abstractions" Version="10.0.0" />
    <PackageVersion Include="Microsoft.Extensions.Caching.Memory" Version="10.0.0" />

    <!-- Mediator -->
    <PackageVersion Include="FreeMediator" Version="2.0.0" />

    <!-- Validation -->
    <PackageVersion Include="FluentValidation" Version="11.9.0" />
    <PackageVersion Include="FluentValidation.DependencyInjectionExtensions" Version="11.9.0" />

    <!-- Testing -->
    <PackageVersion Include="xunit" Version="2.7.0" />
    <PackageVersion Include="xunit.runner.visualstudio" Version="2.5.7" />
    <PackageVersion Include="Microsoft.NET.Test.Sdk" Version="17.9.0" />
    <PackageVersion Include="FluentAssertions" Version="6.12.0" />
    <PackageVersion Include="NSubstitute" Version="5.1.0" />
  </ItemGroup>
</Project>
```

## Module .csproj Template

```xml
<Project Sdk="Microsoft.NET.Sdk">

  <PropertyGroup>
    <PackageId>DenaliDataSystems.PickLists</PackageId>
    <Title>DenaliDataSystems PickLists Module</Title>
    <Description>
      Shared pick list management module with configurable lookup values.
      Provides entities, CQRS commands/queries, and EF Core configurations.
    </Description>
    <PackageTags>denali;shared-kernel;picklists;lookup;cqrs</PackageTags>
    <PackageReadmeFile>README.md</PackageReadmeFile>
    <PackageLicenseExpression>MIT</PackageLicenseExpression>
  </PropertyGroup>

  <ItemGroup>
    <None Include="README.md" Pack="true" PackagePath="" />
  </ItemGroup>

  <ItemGroup>
    <ProjectReference Include="..\DenaliDataSystems.Core.Abstractions\DenaliDataSystems.Core.Abstractions.csproj" />
  </ItemGroup>

  <ItemGroup>
    <PackageReference Include="Microsoft.EntityFrameworkCore" />
    <PackageReference Include="Microsoft.EntityFrameworkCore.SqlServer" />
    <PackageReference Include="Microsoft.Extensions.DependencyInjection.Abstractions" />
    <PackageReference Include="Microsoft.Extensions.Caching.Memory" />
    <PackageReference Include="FreeMediator" />
    <PackageReference Include="FluentValidation" />
    <PackageReference Include="FluentValidation.DependencyInjectionExtensions" />
  </ItemGroup>

</Project>
```

## Core Abstractions .csproj

```xml
<Project Sdk="Microsoft.NET.Sdk">

  <PropertyGroup>
    <PackageId>DenaliDataSystems.Core.Abstractions</PackageId>
    <Title>DenaliDataSystems Core Abstractions</Title>
    <Description>
      Core interfaces and attributes for DenaliDataSystems modules.
      Includes IAuditable, ISoftDeletable, and AuditedEntityAttribute.
    </Description>
    <PackageTags>denali;core;abstractions;interfaces</PackageTags>
    <PackageReadmeFile>README.md</PackageReadmeFile>
    <PackageLicenseExpression>MIT</PackageLicenseExpression>
  </PropertyGroup>

  <ItemGroup>
    <None Include="README.md" Pack="true" PackagePath="" />
  </ItemGroup>

  <!-- No external dependencies - pure abstractions -->

</Project>
```

## Test Project .csproj

```xml
<Project Sdk="Microsoft.NET.Sdk">

  <PropertyGroup>
    <IsPackable>false</IsPackable>
    <IsTestProject>true</IsTestProject>
  </PropertyGroup>

  <ItemGroup>
    <ProjectReference Include="..\..\src\DenaliDataSystems.PickLists\DenaliDataSystems.PickLists.csproj" />
  </ItemGroup>

  <ItemGroup>
    <PackageReference Include="Microsoft.NET.Test.Sdk" />
    <PackageReference Include="xunit" />
    <PackageReference Include="xunit.runner.visualstudio" PrivateAssets="all" />
    <PackageReference Include="FluentAssertions" />
    <PackageReference Include="NSubstitute" />
    <PackageReference Include="Microsoft.EntityFrameworkCore.InMemory" />
  </ItemGroup>

</Project>
```

## nuget.config

```xml
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <packageSources>
    <clear />
    <add key="nuget.org" value="https://api.nuget.org/v3/index.json" />
    <add key="DenaliPrivate" value="https://nuget.denali.local/v3/index.json" />
  </packageSources>

  <packageSourceCredentials>
    <DenaliPrivate>
      <add key="Username" value="%DENALI_NUGET_USER%" />
      <add key="ClearTextPassword" value="%DENALI_NUGET_TOKEN%" />
    </DenaliPrivate>
  </packageSourceCredentials>

  <activePackageSource>
    <add key="All" value="(Aggregate source)" />
  </activePackageSource>
</configuration>
```

## Package README.md Template

```markdown
# DenaliDataSystems.PickLists

Shared pick list management module for DenaliDataSystems applications.

## Installation

```bash
dotnet add package DenaliDataSystems.PickLists
```

## Features

- Configurable lookup lists (pick lists)
- Pick list items with sorting and defaults
- CQRS commands and queries using FreeMediator
- FluentValidation validators
- EF Core configurations with soft delete support

## Usage

### Registration

```csharp
// In Program.cs
builder.Services.AddDenaliPickLists(options =>
{
    options.UseSqlServer(builder.Configuration.GetConnectionString("Default")!);
    options.WithCacheExpiration(60); // 60 minutes
});
```

### Testing Configuration

```csharp
builder.Services.AddDenaliPickLists(options =>
{
    options.UseInMemoryDatabase();
    options.WithDemoData();
});
```

### Using Commands/Queries

```csharp
// Inject IMediator
public class PickListService(IMediator mediator)
{
    public async Task<int> CreatePickList(string name, string key)
    {
        var command = new CreatePickListCommand(name, key);
        return await mediator.Send(command);
    }

    public async Task<PickListDto?> GetPickList(int id)
    {
        var query = new GetPickListByIdQuery(id);
        return await mediator.Send(query);
    }
}
```

## Permissions

| Permission | Description |
|------------|-------------|
| `PickLists.PickList.Manage` | Full access to manage pick lists |
| `PickLists.PickList.Read` | Read-only access to pick lists |

## Database Schema

Tables are created in the `picklists` schema:
- `picklists.PickLists`
- `picklists.PickListItems`

## Dependencies

- DenaliDataSystems.Core.Abstractions
- Microsoft.EntityFrameworkCore.SqlServer
- FreeMediator
- FluentValidation

## Changelog

See [CHANGELOG.md](https://github.com/denali/denali-core-library/blob/main/CHANGELOG.md)
```

## Publishing

### Manual Publish
```bash
# Build release
dotnet build -c Release

# Pack
dotnet pack -c Release -o ./packages

# Push to private feed
dotnet nuget push ./packages/*.nupkg --source DenaliPrivate --api-key $DENALI_NUGET_TOKEN
```

### CI/CD (GitHub Actions)
```yaml
name: Publish NuGet

on:
  push:
    tags:
      - 'v*'

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup .NET
        uses: actions/setup-dotnet@v4
        with:
          dotnet-version: '10.0.x'

      - name: Restore
        run: dotnet restore

      - name: Build
        run: dotnet build -c Release --no-restore

      - name: Test
        run: dotnet test -c Release --no-build

      - name: Pack
        run: dotnet pack -c Release --no-build -o ./packages

      - name: Push
        run: dotnet nuget push ./packages/*.nupkg --source ${{ secrets.NUGET_SOURCE }} --api-key ${{ secrets.NUGET_API_KEY }}
```

## Versioning Strategy

Use [Semantic Versioning](https://semver.org/):

- **MAJOR**: Breaking changes (interface changed, entity renamed)
- **MINOR**: New features (new command, new property)
- **PATCH**: Bug fixes (validation fix, query optimization)

Pre-release versions:
- `1.0.0-alpha.1` - Early development
- `1.0.0-beta.1` - Feature complete, testing
- `1.0.0-rc.1` - Release candidate
- `1.0.0` - Stable release

## Module Dependencies

```
DenaliDataSystems.Core.Abstractions
    └── (no dependencies)

DenaliDataSystems.PickLists
    └── DenaliDataSystems.Core.Abstractions

DenaliDataSystems.People
    └── DenaliDataSystems.Core.Abstractions

DenaliDataSystems.Training
    └── DenaliDataSystems.Core.Abstractions

DenaliDataSystems.Organization
    └── DenaliDataSystems.Core.Abstractions

DenaliDataSystems.Location
    └── DenaliDataSystems.Core.Abstractions

DenaliDataSystems.Workflow
    └── DenaliDataSystems.Core.Abstractions

DenaliDataSystems.Communication
    └── DenaliDataSystems.Core.Abstractions
```

Cross-module relationships (e.g., Employee → Organization) are configured in the consuming application, not in the packages themselves.
