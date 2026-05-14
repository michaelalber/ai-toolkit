---
name: nuget-package-scaffold
description: >
  NuGet package creation with CI/CD pipeline setup and test harness. Use when
  creating new NuGet packages, configuring package metadata, or setting up publish
  workflows. Do NOT use when the library is internal-only and not intended for
  NuGet publication; Do NOT use when the target is an application project.
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
| **Multi-Targeting** | Target net10.0 as the primary TFM; add netstandard2.0 only when broad compatibility is required | High |
| **Documentation** | Include XML doc comments on all public APIs; ship a README in the package | High |
| **Deterministic Builds** | Enable deterministic compilation and Source Link for reproducibility | High |
| **Strong Naming** | Sign assemblies when targeting consumers that require strong-named dependencies | Medium |
| **Source Link** | Embed source repository metadata so debuggers can step into package source | High |
| **License Compliance** | Declare license via SPDX expression or embedded file; never ship unlicensed code | Critical |
| **Dependency Management** | Pin dependency version ranges carefully; prefer minimum viable ranges | High |
| **Backward Compatibility** | Never break public API in a MINOR or PATCH release; use `[Obsolete]` before removal | Critical |

## Knowledge Base Lookups

| Query | When to Call |
|-------|--------------|
| `search_knowledge("NuGet package metadata csproj PackageId authors license README")` | At CONFIGURE phase — confirms required metadata fields and MSBuild properties |
| `search_knowledge("semantic versioning SemVer MAJOR MINOR PATCH NuGet")` | During versioning decisions — confirms SemVer rules and NuGet versioning behavior |
| `search_knowledge(".NET multi-targeting TFM net8 net9 net10 TargetFrameworks")` | When configuring TFMs — confirms multi-targeting syntax and compatibility |
| `search_knowledge("GitHub Actions NuGet publish workflow dotnet pack push")` | During CI/CD pipeline setup — confirms workflow patterns for NuGet publishing |
| `search_knowledge("XML documentation comments public API IntelliSense .NET")` | During documentation phase — authoritative XML doc comment syntax |

**Protocol:** Search at CONFIGURE and before CI/CD setup. Cite source paths in the scaffold templates and generated project files.

## Workflow

Six-step pipeline: **Scaffold → Configure → Test → Pack → Publish** (with iterate back if needed).

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

Required metadata properties checklist:

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

Multi-target decision: `TargetFrameworks: netstandard2.0;net10.0` when pre-.NET 10 consumers need support; `TargetFrameworks: net10.0` otherwise.

### Step 3: Test

```bash
dotnet test --configuration Release
```

Verify all unit tests pass on every target framework, public API surface is tested, edge cases and error paths are covered.

### Step 4: Pack and Verify

```bash
dotnet pack --configuration Release --output ./artifacts
dotnet nuget verify ./artifacts/PackageName.1.0.0.nupkg
unzip -l ./artifacts/PackageName.1.0.0.nupkg
```

### Step 5: Publish

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

## State Block

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

## Output Templates

| Template | Required Content |
|----------|-----------------|
| Project Scaffold | Created files table (path → purpose), initial state block |
| .csproj Configuration | Configured properties list (PackageId, Version, Authors, etc.), Build settings (Deterministic, Source Link, Nullable), state block |
| CI/CD Pipeline Setup | Pipeline stages table (Stage / Trigger / Actions: Build=Push/PR, Pack=Tag push, Publish=Tag+approval), state block |

Full templates: `references/cicd-templates.md`

## AI Discipline Rules

**Never Publish Without Tests:** Run `dotnet test --configuration Release` before any `dotnet nuget push`. Publishing untested code to a feed is irrecoverable damage to consumers — downstream projects will take the broken version immediately.

**Always Validate Package Metadata Before Pack:** All 11 required properties (PackageId, Version, Authors, Description, PackageLicenseExpression, PackageProjectUrl, RepositoryUrl, RepositoryType, PackageReadmeFile, PackageTags, TargetFrameworks) must be present before `dotnet pack`. Missing metadata degrades discoverability and trust on the feed.

**Never Skip Multi-Target Verification:** When `TargetFrameworks` lists multiple TFMs, test each independently: `dotnet test --framework net10.0` then `dotnet test --framework netstandard2.0`. A package that fails on one declared target is broken, even if the other passes.

**Always Review Public API Surface Before Versioning:** List all `public` types and members. Compare against the previous version. Classify: addition → MINOR, removal or modification → MAJOR, internal-only change → PATCH. Verify no `internal` types are accidentally exposed. Accidental public API expansion creates maintenance burden forever.

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

**Action:** Run `dotnet pack --configuration Release` and capture all `NU5*` warnings. Address each warning — common culprits: missing `Description`, `PackageLicenseExpression`, `PackageReadmeFile`. Re-run pack and verify zero warnings.

### Version Conflict: Feed Already Contains Version

**Action:** NuGet.org does not allow overwriting published versions — increment the version number. Unlist the broken version via nuget.org UI if needed. Update CI/CD to use git tags as version source to prevent duplicate pushes.

### Publish Error: Authentication Failure

**Action:** Verify the API key is valid and not expired. For nuget.org: check key scopes match the package ID glob. For Azure Artifacts: verify the PAT has `Packaging (Read & Write)` scope. For GitHub Packages: verify `write:packages` scope. Rotate the key if compromised and update CI/CD secrets.

### Build Failure: Target Framework Incompatibility

**Action:** Identify the API unavailable on the failing TFM. Add conditional compilation (`#if NET9_0_OR_GREATER`) for newer APIs. Provide a fallback for older TFMs. If no fallback is possible, remove the incompatible TFM from `TargetFrameworks`. Re-run `dotnet test` across all remaining targets.

### Test Failure: Framework-Specific Behavior Differences

**Action:** Identify the behavioral difference (string formatting, floating point, date handling). Add framework-specific test expectations using `#if` directives or runtime checks. Document the difference if it affects consumers.

## Integration with Other Skills

- **`dotnet-vertical-slice`** -- use to structure the internal architecture, then use this skill to wrap it as a distributable NuGet package
- **TDD skills** (`tdd-cycle`, `tdd-pair`, `tdd-agent`) -- develop the package internals using TDD workflows before progressing to the Pack step; the test project created by this scaffold integrates directly with TDD phase management
- **`mcp-server-scaffold`** -- when building an MCP server that ships as a dotnet tool NuGet package, use this skill for the packaging and `mcp-server-scaffold` for the server implementation

## Reference Files

- [.csproj Metadata Reference](references/csproj-metadata.md) -- Complete property reference for package metadata
- [CI/CD Pipeline Templates](references/cicd-templates.md) -- GitHub Actions and Azure DevOps pipeline templates
