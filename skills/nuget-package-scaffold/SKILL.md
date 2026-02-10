---
name: nuget-package-scaffold
description: NuGet package creation with CI/CD pipeline setup and test harness. Use when creating new NuGet packages, configuring package metadata, or setting up publish workflows.
---

# NuGet Package Scaffold

> "The best libraries are those that disappear into the code that uses them."
> -- Krzysztof Cwalina, Framework Design Guidelines

## Core Philosophy

This skill scaffolds production-ready NuGet packages with proper metadata, testing, CI/CD pipelines, and publish workflows. Every package must meet a quality bar before it reaches any feed.

**Non-negotiable constraints:**

1. **No publish without tests** -- a package without a passing test suite is not a package, it is a liability
2. **Semantic versioning is law** -- every version bump must communicate intent: breaking, feature, or fix
3. **Metadata is not optional** -- description, license, authors, repository URL, and README are required before first publish
4. **Multi-target when possible** -- support the broadest reasonable set of target frameworks for your consumers
5. **Deterministic builds** -- the same source must produce the same binary, every time

## Domain Principles

| Principle | Description | Priority |
|-----------|-------------|----------|
| **Semantic Versioning** | Follow SemVer 2.0.0 strictly: MAJOR.MINOR.PATCH with clear meaning | Critical |
| **API Surface Minimization** | Expose only what consumers need; use `internal` by default, `public` by design | Critical |
| **Multi-Targeting** | Target multiple TFMs (net8.0, net9.0, net10.0) to maximize consumer reach | High |
| **Documentation** | Include XML doc comments on all public APIs; ship a README in the package | High |
| **Deterministic Builds** | Enable deterministic compilation and Source Link for reproducibility | High |
| **Strong Naming** | Sign assemblies when targeting consumers that require strong-named dependencies | Medium |
| **Source Link** | Embed source repository metadata so debuggers can step into package source | High |
| **License Compliance** | Declare license via SPDX expression or embedded file; never ship unlicensed code | Critical |
| **Dependency Management** | Pin dependency version ranges carefully; prefer minimum viable ranges | High |
| **Backward Compatibility** | Never break public API in a MINOR or PATCH release; use `[Obsolete]` before removal | Critical |

## Workflow

### Scaffold-to-Publish Pipeline

```
┌───────────┐    ┌───────────┐    ┌──────┐    ┌──────┐    ┌─────────┐
│ Scaffold  │───>│ Configure │───>│ Test │───>│ Pack │───>│ Publish │
│           │    │           │    │      │    │      │    │         │
│ - sln     │    │ - .csproj │    │ - unit│   │ - nupkg│  │ - feed  │
│ - src     │    │ - meta   │    │ - int │    │ - snupkg│  │ - tag  │
│ - test    │    │ - ci/cd  │    │ - api │    │ - verify│  │ - notes│
│ - ci      │    │ - readme │    │       │    │        │  │         │
└───────────┘    └───────────┘    └──────┘    └──────┘    └─────────┘
```

### Step 1: Scaffold

Create the solution structure:

```
PackageName/
├── src/
│   └── PackageName/
│       ├── PackageName.csproj
│       └── Class1.cs
├── tests/
│   └── PackageName.Tests/
│       ├── PackageName.Tests.csproj
│       └── Class1Tests.cs
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── publish.yml
├── PackageName.sln
├── Directory.Build.props
├── README.md
├── LICENSE
└── .editorconfig
```

### Step 2: Configure .csproj Metadata

Checklist of required metadata properties:

- [ ] `PackageId` -- unique identifier on the feed
- [ ] `Version` -- SemVer-compliant version string
- [ ] `Authors` -- comma-separated author names
- [ ] `Description` -- concise summary of what the package does
- [ ] `PackageLicenseExpression` -- SPDX license identifier (e.g., MIT, Apache-2.0)
- [ ] `PackageProjectUrl` -- link to the project repository
- [ ] `RepositoryUrl` -- source repository URL
- [ ] `RepositoryType` -- typically `git`
- [ ] `PackageReadmeFile` -- path to the README to embed in the package
- [ ] `PackageTags` -- space-separated discovery tags
- [ ] `TargetFrameworks` -- semicolon-separated TFMs

### Step 3: Multi-Target Framework Decision Tree

```
Does the package use APIs introduced after .NET 8?
├── YES → Which version introduced the API?
│         ├── .NET 9  → TargetFrameworks: net9.0;net10.0
│         └── .NET 10 → TargetFrameworks: net10.0
└── NO  → Does the package use .NET Standard compatible APIs only?
          ├── YES → TargetFrameworks: netstandard2.0;net8.0;net9.0;net10.0
          └── NO  → TargetFrameworks: net8.0;net9.0;net10.0
```

### Step 4: Test

Run the full test suite across all target frameworks:

```bash
dotnet test --configuration Release
```

Verify:
- All unit tests pass on every target framework
- Public API surface is tested
- Edge cases and error paths are covered

### Step 5: Pack and Verify

```bash
dotnet pack --configuration Release --output ./artifacts
```

Then inspect the package:

```bash
# List package contents
dotnet nuget verify ./artifacts/PackageName.1.0.0.nupkg
unzip -l ./artifacts/PackageName.1.0.0.nupkg
```

### Step 6: Publish

```bash
# To nuget.org
dotnet nuget push ./artifacts/PackageName.1.0.0.nupkg \
  --api-key $NUGET_API_KEY \
  --source https://api.nuget.org/v3/index.json

# To a private feed
dotnet nuget push ./artifacts/PackageName.1.0.0.nupkg \
  --api-key $FEED_API_KEY \
  --source https://pkgs.dev.azure.com/org/project/_packaging/feed/nuget/v3/index.json
```

## State Block Format

Maintain state across conversation turns using this block:

```
<nuget-scaffold-state>
step: [scaffold | configure | test | pack | publish]
package_name: [name]
target_frameworks: [frameworks]
version: [version]
publish_target: [nuget.org | private feed | local]
last_action: [what was done]
next_action: [what's next]
blockers: [issues]
</nuget-scaffold-state>
```

### Example State

```
<nuget-scaffold-state>
step: configure
package_name: Acme.Utilities.Json
target_frameworks: net8.0;net9.0;net10.0
version: 1.0.0
publish_target: nuget.org
last_action: Created solution structure and test project
next_action: Configure .csproj package metadata
blockers: none
</nuget-scaffold-state>
```

## Output Templates

### Project Scaffold Output

```markdown
## NuGet Package Scaffold: [PackageName]

**Target Frameworks**: [frameworks]
**License**: [SPDX expression]
**Publish Target**: [nuget.org | private feed | local]

### Created Files

| File | Purpose |
|------|---------|
| `src/PackageName/PackageName.csproj` | Package project with metadata |
| `tests/PackageName.Tests/PackageName.Tests.csproj` | Test project (xUnit) |
| `PackageName.sln` | Solution file |
| `Directory.Build.props` | Shared build properties |
| `.github/workflows/ci.yml` | CI pipeline |
| `.github/workflows/publish.yml` | Publish pipeline |

<nuget-scaffold-state>
step: scaffold
package_name: [name]
target_frameworks: [frameworks]
version: 0.1.0
publish_target: [target]
last_action: Scaffolded solution structure
next_action: Configure .csproj package metadata
blockers: none
</nuget-scaffold-state>
```

### .csproj Configuration Output

```markdown
## Package Metadata: [PackageName]

**Configured Properties**:
- PackageId: [id]
- Version: [version]
- Authors: [authors]
- Description: [description]
- License: [license]
- TargetFrameworks: [tfms]

**Build Settings**:
- Deterministic: true
- Source Link: enabled
- Nullable: enable
- ImplicitUsings: enable

<nuget-scaffold-state>
step: configure
...
last_action: Configured .csproj package metadata
next_action: Write tests for public API
blockers: none
</nuget-scaffold-state>
```

### CI/CD Pipeline Setup Output

```markdown
## CI/CD Pipeline: [PackageName]

**CI Trigger**: Push to main, pull requests
**Publish Trigger**: Tag push (v*)

### Pipeline Stages

| Stage | Trigger | Actions |
|-------|---------|---------|
| Build | Push/PR | Restore, Build, Test |
| Pack | Tag push | Pack, Verify |
| Publish | Tag push + approval | Push to feed |

<nuget-scaffold-state>
step: configure
...
last_action: Created CI/CD pipeline configurations
next_action: Run tests across all target frameworks
blockers: none
</nuget-scaffold-state>
```

## AI Discipline Rules

### CRITICAL: Never Publish Without Tests

Before ANY `dotnet nuget push` command:
1. Verify a test project exists alongside the source project
2. Run `dotnet test` and confirm all tests pass
3. Confirm public API members have corresponding test coverage
4. If no tests exist, STOP and write tests first

Publishing untested code to a feed is irrecoverable damage to consumers.

### CRITICAL: Always Validate Package Metadata

Before ANY `dotnet pack` command:
1. Verify `PackageId` is set and follows naming conventions (Company.Product.Feature)
2. Verify `Version` follows SemVer 2.0.0
3. Verify `Description` is present and meaningful (not placeholder text)
4. Verify `PackageLicenseExpression` or `PackageLicenseFile` is set
5. Verify `PackageReadmeFile` points to an existing file
6. Verify `RepositoryUrl` is set and accessible

Missing metadata degrades discoverability and trust.

### CRITICAL: Never Skip Multi-Target Verification

When the package targets multiple frameworks:
1. Run tests on EVERY target framework, not just the default
2. Use `dotnet test --framework <tfm>` for each target if CI does not cover all
3. Watch for API differences between frameworks (e.g., `netstandard2.0` lacks newer APIs)
4. Verify conditional compilation directives (`#if NET8_0_OR_GREATER`) compile correctly

A package that fails on one of its declared targets is broken.

### CRITICAL: Always Review Public API Surface

Before incrementing any version:
1. List all `public` types and members in the package
2. Compare against previous version's public API
3. Classify changes: addition (MINOR), removal/modification (MAJOR), internal-only (PATCH)
4. Verify no `internal` types are accidentally exposed
5. Check that `[EditorBrowsable(EditorBrowsableState.Never)]` is used for infrastructure types

Accidental public API expansion creates maintenance burden forever.

## Anti-Patterns

| Anti-Pattern | Why It's Wrong | Correct Approach |
|--------------|----------------|------------------|
| Publishing without version bump | Consumers cannot distinguish builds; caching breaks | Always increment version for every publish |
| Exposing all types as `public` | Inflates API surface; locks you into supporting everything | Default to `internal`; promote to `public` deliberately |
| Hardcoded dependency versions | Forces consumers into version conflicts | Use minimum viable version ranges (e.g., `[8.0.0, )`) |
| Skipping Source Link | Consumers cannot debug into your package source | Always configure Source Link for public packages |
| Single target framework | Excludes consumers on other frameworks unnecessarily | Multi-target unless APIs require a specific TFM |
| Publishing prerelease to nuget.org without suffix | Stable version number occupies the version space permanently | Use `-alpha`, `-beta`, `-rc` suffixes for prereleases |
| Missing README in package | Consumers see no documentation on nuget.org package page | Always set `PackageReadmeFile` and include the file |

## Error Recovery

### Pack Failure: Missing Required Metadata

**Problem**: `dotnet pack` warns about missing metadata or produces a package that fails validation.

**Action**:
1. Run `dotnet pack --configuration Release` and capture all warnings
2. Address each `NU5*` warning -- these are NuGet-specific pack warnings
3. Common culprits: missing `Description`, missing `PackageLicenseExpression`, missing `PackageReadmeFile`
4. Re-run pack and verify zero warnings

### Version Conflict: Feed Already Contains Version

**Problem**: `dotnet nuget push` fails because the version already exists on the feed.

**Action**:
1. NuGet.org does NOT allow overwriting published versions -- this is by design
2. Increment the version number (PATCH for fixes, MINOR for features)
3. If this was a mistake, unlist the broken version via nuget.org UI
4. Update CI/CD to prevent duplicate version pushes (use git tags as version source)

### Publish Error: Authentication Failure

**Problem**: Push fails with 401 or 403 errors.

**Action**:
1. Verify the API key is valid and not expired
2. For nuget.org: check key scopes match the package ID glob pattern
3. For Azure Artifacts: verify the PAT has Packaging (Read & Write) scope
4. For GitHub Packages: verify the `GITHUB_TOKEN` or PAT has `write:packages` scope
5. Rotate the key if compromised and update CI/CD secrets

### Build Failure: Target Framework Incompatibility

**Problem**: Code compiles on one TFM but fails on another.

**Action**:
1. Identify the API that is unavailable on the failing TFM
2. Add conditional compilation: `#if NET9_0_OR_GREATER` for newer APIs
3. Provide a fallback implementation for older TFMs
4. If no fallback is possible, remove the incompatible TFM from `TargetFrameworks`
5. Re-run `dotnet test` across all remaining targets

### Test Failure: Framework-Specific Behavior Differences

**Problem**: Tests pass on one TFM but fail on another due to behavioral differences.

**Action**:
1. Identify the behavioral difference (often string formatting, floating point, or date handling)
2. Add framework-specific test expectations using `#if` directives or runtime checks
3. Consider whether the behavior difference is a bug in your code or an expected platform difference
4. Document the difference if it affects consumers

## Integration with Other Skills

- **`dotnet-vertical-slice`** -- when scaffolding a package that implements a vertical slice feature, use `dotnet-vertical-slice` to structure the internal architecture, then use this skill to wrap it as a distributable NuGet package
- **TDD skills** (`tdd-cycle`, `tdd-pair`, `tdd-agent`) -- use TDD workflows to develop the package internals before progressing to the Pack step; the test project created by this scaffold integrates directly with TDD phase management
- **`mcp-server-scaffold`** -- when building an MCP server that ships as a dotnet tool NuGet package, use this skill for the packaging and `mcp-server-scaffold` for the server implementation

## Stack-Specific Guidance

See reference files for detailed configurations:
- [.csproj Metadata Reference](references/csproj-metadata.md) -- Complete property reference for package metadata
- [CI/CD Pipeline Templates](references/cicd-templates.md) -- GitHub Actions and Azure DevOps pipeline templates
