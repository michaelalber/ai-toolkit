# NuGet Package Scaffold — Conventions, Discipline & Recovery

Depth relocated from `SKILL.md`: domain principles, knowledge-base lookup protocol,
AI discipline rules, anti-patterns, and error-recovery procedures.

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
