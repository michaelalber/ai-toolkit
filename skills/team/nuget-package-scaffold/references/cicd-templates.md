# CI/CD Pipeline Templates for NuGet Publishing

## GitHub Actions: Build and Test (CI)

This workflow runs on every push and pull request to validate the package builds and all tests pass across target frameworks.

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

permissions:
  contents: read

jobs:
  build:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        dotnet-version: ['8.0.x', '9.0.x', '10.0.x']

    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history for versioning tools

      - name: Setup .NET ${{ matrix.dotnet-version }}
        uses: actions/setup-dotnet@v4
        with:
          dotnet-version: ${{ matrix.dotnet-version }}

      - name: Restore dependencies
        run: dotnet restore

      - name: Build
        run: dotnet build --no-restore --configuration Release

      - name: Test
        run: dotnet test --no-build --configuration Release --verbosity normal --logger "trx;LogFileName=test-results.trx"

      - name: Upload test results
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: test-results-${{ matrix.dotnet-version }}
          path: '**/TestResults/*.trx'
```

## GitHub Actions: Pack and Publish

This workflow triggers on version tag pushes (e.g., `v1.0.0`) and publishes the package to the configured feed.

```yaml
name: Publish NuGet

on:
  push:
    tags:
      - 'v*'

permissions:
  contents: read
  packages: write

env:
  DOTNET_VERSION: '9.0.x'
  PACKAGE_OUTPUT_DIR: ${{ github.workspace }}/artifacts

jobs:
  publish:
    runs-on: ubuntu-latest
    environment: nuget-publish  # Requires approval if configured

    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Setup .NET
        uses: actions/setup-dotnet@v4
        with:
          dotnet-version: ${{ env.DOTNET_VERSION }}

      - name: Extract version from tag
        id: version
        run: echo "VERSION=${GITHUB_REF_NAME#v}" >> $GITHUB_OUTPUT

      - name: Restore dependencies
        run: dotnet restore

      - name: Build
        run: dotnet build --no-restore --configuration Release -p:Version=${{ steps.version.outputs.VERSION }}

      - name: Test
        run: dotnet test --no-build --configuration Release --verbosity normal

      - name: Pack
        run: dotnet pack --no-build --configuration Release -p:Version=${{ steps.version.outputs.VERSION }} --output ${{ env.PACKAGE_OUTPUT_DIR }}

      - name: Verify package
        run: |
          ls -la ${{ env.PACKAGE_OUTPUT_DIR }}
          dotnet nuget verify ${{ env.PACKAGE_OUTPUT_DIR }}/*.nupkg || true

      - name: Push to NuGet.org
        run: |
          dotnet nuget push ${{ env.PACKAGE_OUTPUT_DIR }}/*.nupkg \
            --api-key ${{ secrets.NUGET_API_KEY }} \
            --source https://api.nuget.org/v3/index.json \
            --skip-duplicate

      - name: Push symbols to NuGet.org
        run: |
          dotnet nuget push ${{ env.PACKAGE_OUTPUT_DIR }}/*.snupkg \
            --api-key ${{ secrets.NUGET_API_KEY }} \
            --source https://api.nuget.org/v3/index.json \
            --skip-duplicate
        continue-on-error: true  # Symbol push is best-effort
```

## GitHub Actions: Publish to GitHub Packages

For teams using GitHub Packages as a private feed:

```yaml
name: Publish to GitHub Packages

on:
  push:
    tags:
      - 'v*'

permissions:
  contents: read
  packages: write

jobs:
  publish:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Setup .NET
        uses: actions/setup-dotnet@v4
        with:
          dotnet-version: '9.0.x'

      - name: Extract version from tag
        id: version
        run: echo "VERSION=${GITHUB_REF_NAME#v}" >> $GITHUB_OUTPUT

      - name: Restore
        run: dotnet restore

      - name: Build
        run: dotnet build --no-restore --configuration Release -p:Version=${{ steps.version.outputs.VERSION }}

      - name: Test
        run: dotnet test --no-build --configuration Release

      - name: Pack
        run: dotnet pack --no-build --configuration Release -p:Version=${{ steps.version.outputs.VERSION }} --output ./artifacts

      - name: Add GitHub Packages source
        run: |
          dotnet nuget add source \
            --username ${{ github.actor }} \
            --password ${{ secrets.GITHUB_TOKEN }} \
            --store-password-in-clear-text \
            --name github \
            "https://nuget.pkg.github.com/${{ github.repository_owner }}/index.json"

      - name: Push to GitHub Packages
        run: |
          dotnet nuget push ./artifacts/*.nupkg \
            --api-key ${{ secrets.GITHUB_TOKEN }} \
            --source github \
            --skip-duplicate
```

## Azure DevOps Pipeline Template

### azure-pipelines.yml (CI + Publish)

```yaml
trigger:
  branches:
    include:
      - main
  tags:
    include:
      - 'v*'

pr:
  branches:
    include:
      - main

pool:
  vmImage: 'ubuntu-latest'

variables:
  buildConfiguration: 'Release'
  dotnetVersion: '9.0.x'
  packageOutputDir: '$(Build.ArtifactStagingDirectory)/packages'

stages:
  - stage: Build
    displayName: 'Build and Test'
    jobs:
      - job: BuildAndTest
        displayName: 'Build, Test, Pack'
        steps:
          - task: UseDotNet@2
            displayName: 'Install .NET SDK'
            inputs:
              version: $(dotnetVersion)

          - script: dotnet restore
            displayName: 'Restore dependencies'

          - script: dotnet build --no-restore --configuration $(buildConfiguration)
            displayName: 'Build'

          - script: dotnet test --no-build --configuration $(buildConfiguration) --logger trx --results-directory $(Agent.TempDirectory)/TestResults
            displayName: 'Run tests'

          - task: PublishTestResults@2
            displayName: 'Publish test results'
            inputs:
              testResultsFormat: 'VSTest'
              testResultsFiles: '$(Agent.TempDirectory)/TestResults/**/*.trx'
            condition: always()

          - script: dotnet pack --no-build --configuration $(buildConfiguration) --output $(packageOutputDir)
            displayName: 'Pack'
            condition: and(succeeded(), startsWith(variables['Build.SourceBranch'], 'refs/tags/v'))

          - task: PublishBuildArtifacts@1
            displayName: 'Publish package artifacts'
            inputs:
              pathToPublish: $(packageOutputDir)
              artifactName: 'packages'
            condition: and(succeeded(), startsWith(variables['Build.SourceBranch'], 'refs/tags/v'))

  - stage: PublishDev
    displayName: 'Publish to Dev Feed'
    dependsOn: Build
    condition: and(succeeded(), startsWith(variables['Build.SourceBranch'], 'refs/tags/v'), contains(variables['Build.SourceBranch'], '-'))
    jobs:
      - deployment: PublishDevFeed
        displayName: 'Push to Dev Feed'
        environment: 'dev-feed'
        strategy:
          runOnce:
            deploy:
              steps:
                - task: NuGetCommand@2
                  displayName: 'Push to Azure Artifacts (Dev)'
                  inputs:
                    command: 'push'
                    packagesToPush: '$(Pipeline.Workspace)/packages/*.nupkg'
                    nuGetFeedType: 'internal'
                    publishVstsFeed: 'project/dev-feed'

  - stage: PublishProd
    displayName: 'Publish to NuGet.org'
    dependsOn: Build
    condition: and(succeeded(), startsWith(variables['Build.SourceBranch'], 'refs/tags/v'), not(contains(variables['Build.SourceBranch'], '-')))
    jobs:
      - deployment: PublishNuGet
        displayName: 'Push to NuGet.org'
        environment: 'nuget-production'  # Requires approval
        strategy:
          runOnce:
            deploy:
              steps:
                - task: NuGetCommand@2
                  displayName: 'Push to NuGet.org'
                  inputs:
                    command: 'push'
                    packagesToPush: '$(Pipeline.Workspace)/packages/*.nupkg'
                    nuGetFeedType: 'external'
                    publishFeedCredentials: 'NuGetOrgConnection'
```

## Version Management Strategies

### Strategy 1: Git Tag-Based (Manual)

The simplest approach. Version is derived from the git tag at publish time.

```bash
# Create a release
git tag v1.2.3
git push origin v1.2.3
```

In the pipeline, extract the version from the tag:

```yaml
- name: Extract version from tag
  id: version
  run: echo "VERSION=${GITHUB_REF_NAME#v}" >> $GITHUB_OUTPUT
```

Then pass it to build and pack:

```bash
dotnet build -p:Version=$VERSION
dotnet pack -p:Version=$VERSION
```

**Pros**: Simple, explicit, no extra tooling.
**Cons**: Manual process, easy to forget to tag.

### Strategy 2: MinVer (Automated from Git Tags)

MinVer reads git tags and calculates the version automatically, including prerelease suffixes based on commit distance from the last tag.

```xml
<!-- Add to .csproj or Directory.Build.props -->
<ItemGroup>
  <PackageReference Include="MinVer" Version="6.0.0" PrivateAssets="All" />
</ItemGroup>
```

MinVer behavior:
- Tag `v1.2.3` on a commit produces version `1.2.3`
- 5 commits after tag `v1.2.3` produces version `1.2.4-alpha.0.5`
- No tags at all produces version `0.0.0-alpha.0.N`

Configuration options in `.csproj`:

```xml
<PropertyGroup>
  <MinVerMinimumMajorMinor>1.0</MinVerMinimumMajorMinor>
  <MinVerTagPrefix>v</MinVerTagPrefix>
  <MinVerDefaultPreReleaseIdentifiers>preview.0</MinVerDefaultPreReleaseIdentifiers>
</PropertyGroup>
```

**Pros**: Zero manual version management in code, SemVer-compliant, deterministic.
**Cons**: Requires understanding of MinVer conventions.

### Strategy 3: GitVersion (Full Git Flow Integration)

GitVersion calculates versions based on branch names and git history using Conventional Commits or Git Flow conventions.

Install the tool:

```bash
dotnet tool install --global GitVersion.Tool
```

Configuration (`GitVersion.yml`):

```yaml
mode: ContinuousDeployment
branches:
  main:
    regex: ^main$
    tag: ''
    increment: Patch
  release:
    regex: ^release/.*$
    tag: rc
    increment: None
  feature:
    regex: ^feature/.*$
    tag: alpha
    increment: Minor
  hotfix:
    regex: ^hotfix/.*$
    tag: beta
    increment: Patch
```

Usage in CI:

```yaml
- name: Install GitVersion
  uses: gittools/actions/gitversion/setup@v3
  with:
    versionSpec: '6.x'

- name: Determine Version
  id: gitversion
  uses: gittools/actions/gitversion/execute@v3

- name: Build
  run: dotnet build -p:Version=${{ steps.gitversion.outputs.semVer }}
```

**Pros**: Rich branching strategy support, automatic prerelease handling.
**Cons**: Complex configuration, learning curve.

### Strategy 4: Version in .csproj (Simplest)

Set the version directly in the project file. Suitable for small projects with infrequent releases.

```xml
<PropertyGroup>
  <Version>1.2.3</Version>
</PropertyGroup>
```

Bump manually before each release via a PR.

**Pros**: No tooling required, immediately visible.
**Cons**: Easy to forget, merge conflicts on version bumps.

## Environment-Based Publish Targets

### Development Feed (Every CI Build)

Push prerelease packages to an internal feed for testing:

```yaml
- name: Push to dev feed
  if: github.ref == 'refs/heads/main'
  run: |
    dotnet nuget push ./artifacts/*.nupkg \
      --api-key ${{ secrets.DEV_FEED_KEY }} \
      --source https://pkgs.dev.azure.com/org/project/_packaging/dev/nuget/v3/index.json \
      --skip-duplicate
```

### Staging Feed (Release Candidates)

Push release candidates for integration testing:

```yaml
- name: Push to staging feed
  if: contains(github.ref, '-rc')
  run: |
    dotnet nuget push ./artifacts/*.nupkg \
      --api-key ${{ secrets.STAGING_FEED_KEY }} \
      --source https://pkgs.dev.azure.com/org/project/_packaging/staging/nuget/v3/index.json \
      --skip-duplicate
```

### Production (NuGet.org)

Push stable releases only after approval:

```yaml
- name: Push to NuGet.org
  if: startsWith(github.ref, 'refs/tags/v') && !contains(github.ref, '-')
  run: |
    dotnet nuget push ./artifacts/*.nupkg \
      --api-key ${{ secrets.NUGET_API_KEY }} \
      --source https://api.nuget.org/v3/index.json \
      --skip-duplicate
```

## Signing and Verification

### NuGet Package Signing (Author Signing)

Author signing provides cryptographic proof that a package was produced by a specific publisher.

```bash
# Sign with a certificate
dotnet nuget sign ./artifacts/MyPackage.1.0.0.nupkg \
  --certificate-path ./certificate.pfx \
  --certificate-password $CERT_PASSWORD \
  --timestamper http://timestamp.digicert.com
```

In CI (GitHub Actions):

```yaml
- name: Sign NuGet package
  run: |
    echo "${{ secrets.SIGNING_CERT_BASE64 }}" | base64 -d > cert.pfx
    dotnet nuget sign ./artifacts/*.nupkg \
      --certificate-path cert.pfx \
      --certificate-password "${{ secrets.SIGNING_CERT_PASSWORD }}" \
      --timestamper http://timestamp.digicert.com
    rm cert.pfx
```

### Package Verification

Verify a package signature before consuming it:

```bash
dotnet nuget verify ./artifacts/MyPackage.1.0.0.nupkg --all
```

In CI, add a verification step after pack:

```yaml
- name: Verify package integrity
  run: |
    for pkg in ./artifacts/*.nupkg; do
      echo "Verifying $pkg"
      dotnet nuget verify "$pkg" || true
      # List contents for manual review
      unzip -l "$pkg"
    done
```

### Repository Signing (NuGet.org)

NuGet.org applies its own repository signature to all packages. This is automatic and requires no configuration from package authors. Repository-signed packages have an additional layer of trust beyond author signing.

## Release Workflow with Approval Gates

### GitHub Actions: Environment Protection Rules

Configure the `nuget-publish` environment in GitHub repository settings with:
- Required reviewers (1 or more team members)
- Wait timer (optional delay before deployment)
- Branch restrictions (only allow `main` or `refs/tags/v*`)

```yaml
jobs:
  publish:
    runs-on: ubuntu-latest
    environment: nuget-publish  # This triggers the approval gate

    steps:
      # ... build, test, pack, push steps ...
```

### Azure DevOps: Environment Approvals

In Azure DevOps, configure approval checks on the `nuget-production` environment:

```yaml
- stage: PublishProd
  jobs:
    - deployment: PublishNuGet
      environment: 'nuget-production'  # Configured with approvals in Azure DevOps UI
      strategy:
        runOnce:
          deploy:
            steps:
              # ... push steps ...
```

### Full Release Checklist Workflow

A comprehensive release workflow that enforces quality gates:

```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  validate:
    runs-on: ubuntu-latest
    outputs:
      version: ${{ steps.version.outputs.VERSION }}
      is-prerelease: ${{ contains(github.ref, '-') }}
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Extract version
        id: version
        run: echo "VERSION=${GITHUB_REF_NAME#v}" >> $GITHUB_OUTPUT

      - name: Validate version format
        run: |
          VERSION="${{ steps.version.outputs.VERSION }}"
          if [[ ! "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+(-[a-zA-Z0-9.]+)?$ ]]; then
            echo "ERROR: Invalid version format: $VERSION"
            echo "Expected: MAJOR.MINOR.PATCH or MAJOR.MINOR.PATCH-prerelease"
            exit 1
          fi

  build-and-test:
    needs: validate
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-dotnet@v4
        with:
          dotnet-version: '9.0.x'

      - run: dotnet restore
      - run: dotnet build --configuration Release -p:Version=${{ needs.validate.outputs.version }}
      - run: dotnet test --configuration Release --no-build --verbosity normal

      - run: dotnet pack --configuration Release --no-build -p:Version=${{ needs.validate.outputs.version }} --output ./artifacts

      - uses: actions/upload-artifact@v4
        with:
          name: packages
          path: ./artifacts/

  publish:
    needs: [validate, build-and-test]
    runs-on: ubuntu-latest
    environment: ${{ needs.validate.outputs.is-prerelease == 'true' && 'nuget-prerelease' || 'nuget-production' }}
    steps:
      - uses: actions/download-artifact@v4
        with:
          name: packages
          path: ./artifacts

      - uses: actions/setup-dotnet@v4
        with:
          dotnet-version: '9.0.x'

      - name: Push to NuGet.org
        run: |
          dotnet nuget push ./artifacts/*.nupkg \
            --api-key ${{ secrets.NUGET_API_KEY }} \
            --source https://api.nuget.org/v3/index.json \
            --skip-duplicate

      - name: Push symbols
        run: |
          dotnet nuget push ./artifacts/*.snupkg \
            --api-key ${{ secrets.NUGET_API_KEY }} \
            --source https://api.nuget.org/v3/index.json \
            --skip-duplicate
        continue-on-error: true

  create-release:
    needs: [validate, publish]
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4

      - name: Create GitHub Release
        uses: softprops/action-gh-release@v2
        with:
          tag_name: ${{ github.ref_name }}
          name: "v${{ needs.validate.outputs.version }}"
          prerelease: ${{ needs.validate.outputs.is-prerelease == 'true' }}
          generate_release_notes: true
```

## Quick Reference: Publish Commands

### Local Feed (For Development)

```bash
# Create a local feed directory
mkdir -p ~/local-nuget-feed

# Pack and push to local feed
dotnet pack --configuration Release --output ./artifacts
dotnet nuget push ./artifacts/*.nupkg --source ~/local-nuget-feed

# Configure the local feed in NuGet.Config
dotnet nuget add source ~/local-nuget-feed --name LocalFeed
```

### NuGet.org

```bash
dotnet nuget push ./artifacts/*.nupkg \
  --api-key YOUR_API_KEY \
  --source https://api.nuget.org/v3/index.json
```

### Azure Artifacts

```bash
dotnet nuget push ./artifacts/*.nupkg \
  --api-key az \
  --source https://pkgs.dev.azure.com/ORG/PROJECT/_packaging/FEED/nuget/v3/index.json
```

### GitHub Packages

```bash
dotnet nuget push ./artifacts/*.nupkg \
  --api-key YOUR_GITHUB_TOKEN \
  --source https://nuget.pkg.github.com/OWNER/index.json
```

## NuGet.Config for Multiple Sources

Place at the solution root to configure feed resolution order:

```xml
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <packageSources>
    <clear />
    <add key="nuget.org" value="https://api.nuget.org/v3/index.json" />
    <add key="dev-feed" value="https://pkgs.dev.azure.com/org/project/_packaging/dev/nuget/v3/index.json" />
  </packageSources>

  <packageSourceMapping>
    <packageSource key="nuget.org">
      <package pattern="*" />
    </packageSource>
    <packageSource key="dev-feed">
      <package pattern="Acme.*" />
    </packageSource>
  </packageSourceMapping>
</configuration>
```

Package source mapping ensures that internal packages are only resolved from the internal feed, preventing dependency confusion attacks.
