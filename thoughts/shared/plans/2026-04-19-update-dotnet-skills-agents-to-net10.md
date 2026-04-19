# Update .NET Skills and Agents to .NET 10 — Implementation Plan

## Overview

Several .NET skills and agents contain stale version references to .NET 8 and .NET 9. This plan
updates all stale references to .NET 10 (the current LTS) across 5 files in 4 independent phases.
No structural changes are made — only version string substitutions.

## Current state analysis

From the research artifact (`2026-04-19-skills-and-agents-inventory.md`) and a targeted grep scan:

- `test-scaffold/SKILL.md:71` — code example uses `net9.0`
- `nuget-package-scaffold/SKILL.md` (lines 29, 46, 111–117, 184) and
  `nuget-package-scaffold/references/csproj-metadata.md` (lines 36, 52, 64, 99–101, 273, 339) —
  multi-target TFM list `net8.0;net9.0;net10.0` and a `net8.0`-conditional `ItemGroup` example
- `claude/agents/migration-orchestrator.md` (lines 3, 18, 126, 256, 346) — `.NET 8/10` throughout
- `opencode/agents/migration-orchestrator.md` (lines 2, 20, 144, 274, 364) — same content
- `dotnet-security-review/references/telerik-security.md:21` — `Telerik UI for Blazor (.NET 9+)`
- `dotnet-architecture-checklist/references/review-checklist.md:6` — `or .NET 8 LTS?`

Already correct (no changes needed): `minimal-api-scaffolder`, `rag-pipeline-dotnet`,
`4d-schema-migration`, `legacy-migration-analyzer`, `dotnet-architecture-checklist/SKILL.md`,
`dotnet-vertical-slice`, `ef-migration-manager`, `dotnet-security-review-federal`.

## Desired end state

- Every .NET target version reference in skills and agents reads `net10.0` / `.NET 10`
- No `net8.0` or `net9.0` TFM entries remain in new-package scaffolding examples
- `migration-orchestrator` description and body reference `.NET 10` only
- Telerik Blazor section header reads `.NET 10+`
- Architecture checklist no longer offers `.NET 8 LTS` as an alternative

## What we're NOT doing

- No changes to `legacy-migration-analyzer` (already .NET 10 throughout)
- No changes to `dotnet-architecture-checklist/SKILL.md` or `references/framework-detection.md`
  (these document the full version history for detection purposes — not prescribing a target)
- No changes to `dotnet-architecture-checklist/references/review-checklist.md:73`
  (`### Interactive Auto (.NET 8+)` — this is a minimum-version floor for a Blazor feature, not a
  target version recommendation; it remains accurate)
- No changes to `dotnet-security-review-federal` (only mentions `.NET 5+` in a FIPS table)
- No section template compliance fixes (separate task)
- No parity gap fixes (separate task)
- No changes to `nuget-package-scaffold` multi-target search query string at line 46
  (the query string `"net8 net9 net10"` is a KB search hint, not a version prescription — leave it)

## Implementation approach

Four independent phases, each targeting one skill or agent pair. Phases have no dependencies on
each other and can be executed in any order. Each phase is verified by confirming the target
strings no longer appear in the changed files.

---

## Phase 1: Update `test-scaffold` code example

### Overview

Replace the single `net9.0` TFM in the test project csproj example with `net10.0`.

### Changes required

#### 1. Update TargetFramework in csproj example
**File**: `skills/test-scaffold/SKILL.md`
**Line**: 71
**Change**: Replace `<TargetFramework>net9.0</TargetFramework>` with
`<TargetFramework>net10.0</TargetFramework>`

```xml
<!-- REMOVE: -->
<TargetFramework>net9.0</TargetFramework>

<!-- ADD: -->
<TargetFramework>net10.0</TargetFramework>
```

### Success criteria

#### Automated verification
- [ ] `grep -n "net9" skills/test-scaffold/SKILL.md` → no output
- [ ] `grep -n "net10" skills/test-scaffold/SKILL.md` → shows the updated line

**Implementation note**: Independent — can be executed in any order relative to other phases.

---

## Phase 2: Update `nuget-package-scaffold` TFM references

### Overview

Replace all `net8.0;net9.0;net10.0` multi-target lists with `net10.0` only, update the
decision-tree diagram, remove the `net8.0`-conditional `ItemGroup` example, and update the
dotnet tool example TFM. Affects SKILL.md and one references file.

### Changes required

#### 1. Update Domain Principles Table entry
**File**: `skills/nuget-package-scaffold/SKILL.md`
**Line**: 29
**Change**: Replace `Target multiple TFMs (net8.0, net9.0, net10.0)` with
`Target net10.0 as the primary TFM; add netstandard2.0 only when broad compatibility is required`

```
<!-- REMOVE: -->
| **Multi-Targeting** | Target multiple TFMs (net8.0, net9.0, net10.0) to maximize consumer reach | High |

<!-- ADD: -->
| **Multi-Targeting** | Target net10.0 as the primary TFM; add netstandard2.0 only when broad compatibility is required | High |
```

#### 2. Update TFM decision tree
**File**: `skills/nuget-package-scaffold/SKILL.md`
**Lines**: 111–117
**Change**: Collapse the decision tree to reflect net10.0 as the single modern target.
Replace the block:

```
<!-- REMOVE: -->
Does the package use APIs introduced after .NET 8?
│         ├── .NET 9  → TargetFrameworks: net9.0;net10.0
│         └── .NET 10 → TargetFrameworks: net10.0
...
          ├── YES → TargetFrameworks: netstandard2.0;net8.0;net9.0;net10.0
          └── NO  → TargetFrameworks: net8.0;net9.0;net10.0

<!-- ADD: -->
Does the package need to support pre-.NET 10 consumers?
│         ├── YES → TargetFrameworks: netstandard2.0;net10.0
│         └── NO  → TargetFrameworks: net10.0
```

#### 3. Update state block default
**File**: `skills/nuget-package-scaffold/SKILL.md`
**Line**: 184
**Change**: Replace `target_frameworks: net8.0;net9.0;net10.0` with
`target_frameworks: net10.0`

#### 4. Update TargetFrameworks example in csproj-metadata
**File**: `skills/nuget-package-scaffold/references/csproj-metadata.md`
**Line**: 36
**Change**: Replace example value `` `net8.0;net9.0;net10.0` `` with `` `net10.0` ``

#### 5. Update standard library csproj example
**File**: `skills/nuget-package-scaffold/references/csproj-metadata.md`
**Line**: 52
**Change**: Replace `<TargetFrameworks>net8.0;net9.0;net10.0</TargetFrameworks>` with
`<TargetFrameworks>net10.0</TargetFrameworks>`

#### 6. Update netstandard compatibility csproj example
**File**: `skills/nuget-package-scaffold/references/csproj-metadata.md`
**Line**: 64
**Change**: Replace `<TargetFrameworks>netstandard2.0;net8.0;net9.0;net10.0</TargetFrameworks>`
with `<TargetFrameworks>netstandard2.0;net10.0</TargetFrameworks>`

#### 7. Remove net8.0-conditional ItemGroup example
**File**: `skills/nuget-package-scaffold/references/csproj-metadata.md`
**Lines**: 99–101
**Change**: Replace the `net8.0` conditional `ItemGroup` with a `net10.0` equivalent comment.

```xml
<!-- REMOVE: -->
<ItemGroup Condition="'$(TargetFramework)' == 'net8.0'">
  <!-- net8.0 includes System.Memory in-box -->
</ItemGroup>

<!-- ADD: -->
<ItemGroup Condition="'$(TargetFramework)' == 'net10.0'">
  <!-- net10.0 includes System.Memory in-box -->
</ItemGroup>
```

#### 8. Update full csproj example near line 273
**File**: `skills/nuget-package-scaffold/references/csproj-metadata.md`
**Line**: 273
**Change**: Replace `<TargetFrameworks>net8.0;net9.0;net10.0</TargetFrameworks>` with
`<TargetFrameworks>net10.0</TargetFrameworks>`

#### 9. Update dotnet tool csproj example
**File**: `skills/nuget-package-scaffold/references/csproj-metadata.md`
**Line**: 339
**Change**: Replace `<TargetFramework>net9.0</TargetFramework>` with
`<TargetFramework>net10.0</TargetFramework>`

### Success criteria

#### Automated verification
- [ ] `grep -n "net8\|net9" skills/nuget-package-scaffold/SKILL.md` → only line 46 (KB search query string — expected, not a version prescription)
- [ ] `grep -n "net8\|net9" skills/nuget-package-scaffold/references/csproj-metadata.md` → no output
- [ ] `grep -c "net10" skills/nuget-package-scaffold/references/csproj-metadata.md` → ≥ 6 matches

**Implementation note**: Independent — can be executed in any order relative to other phases.

---

## Phase 3: Update `migration-orchestrator` agents

### Overview

Replace all `.NET 8/10` references with `.NET 10` in both the Claude Code and OpenCode agent
files. Both files have identical content at different line numbers; update both in this phase.

### Changes required

#### 1. Update frontmatter description — Claude agent
**File**: `claude/agents/migration-orchestrator.md`
**Line**: 3
**Change**: Replace `".NET Framework to .NET 8/10 migrations"` with
`".NET Framework to .NET 10 migrations"`

#### 2. Update opening paragraph — Claude agent
**File**: `claude/agents/migration-orchestrator.md`
**Line**: 18
**Change**: Replace `".NET Framework to .NET 8/10 migrations"` with
`".NET Framework to .NET 10 migrations"`

#### 3. Update dependency scan step — Claude agent
**File**: `claude/agents/migration-orchestrator.md`
**Line**: 126
**Change**: Replace `"check .NET 8/10 compatibility"` with `"check .NET 10 compatibility"`

#### 4. Update missing API step — Claude agent
**File**: `claude/agents/migration-orchestrator.md`
**Line**: 256
**Change**: Replace `"find .NET 8/10 equivalent"` with `"find .NET 10 equivalent"`

#### 5. Update session template Target Framework field — Claude agent
**File**: `claude/agents/migration-orchestrator.md`
**Line**: 346
**Change**: Replace `"Target Framework: [.NET 8/10]"` with `"Target Framework: [.NET 10]"`

#### 6–10. Apply identical changes to OpenCode agent
**File**: `opencode/agents/migration-orchestrator.md`
**Lines**: 2, 20, 144, 274, 364
**Change**: Same five substitutions as steps 1–5 above (`.NET 8/10` → `.NET 10`)

### Success criteria

#### Automated verification
- [ ] `grep -n "\.NET 8" claude/agents/migration-orchestrator.md` → no output
- [ ] `grep -n "\.NET 8" opencode/agents/migration-orchestrator.md` → no output
- [ ] `grep -c "\.NET 10" claude/agents/migration-orchestrator.md` → ≥ 5 matches
- [ ] `grep -c "\.NET 10" opencode/agents/migration-orchestrator.md` → ≥ 5 matches

**Implementation note**: Independent — can be executed in any order relative to other phases.
Both agent files must be updated together in this phase to maintain parity.

---

## Phase 4: Update Telerik section header and architecture checklist

### Overview

Two small single-line fixes: the Telerik security reference file section header and the
architecture checklist `.NET 8 LTS` alternative.

### Changes required

#### 1. Update Telerik Blazor section header
**File**: `skills/dotnet-security-review/references/telerik-security.md`
**Line**: 21
**Change**: Replace `## Part 1: Telerik UI for Blazor (.NET 9+)` with
`## Part 1: Telerik UI for Blazor (.NET 10+)`

```markdown
<!-- REMOVE: -->
## Part 1: Telerik UI for Blazor (.NET 9+)

<!-- ADD: -->
## Part 1: Telerik UI for Blazor (.NET 10+)
```

#### 2. Update architecture checklist framework question
**File**: `skills/dotnet-architecture-checklist/references/review-checklist.md`
**Line**: 6
**Change**: Replace `- [ ] Using .NET 10 LTS (preferred) or .NET 8 LTS?` with
`- [ ] Using .NET 10 LTS?`

```markdown
<!-- REMOVE: -->
- [ ] Using .NET 10 LTS (preferred) or .NET 8 LTS?

<!-- ADD: -->
- [ ] Using .NET 10 LTS?
```

### Success criteria

#### Automated verification
- [ ] `grep -n "\.NET 9+" skills/dotnet-security-review/references/telerik-security.md` → no output
- [ ] `grep -n "\.NET 10+" skills/dotnet-security-review/references/telerik-security.md` → shows line 21
- [ ] `grep -n "\.NET 8 LTS" skills/dotnet-architecture-checklist/references/review-checklist.md` → no output

**Implementation note**: Independent — can be executed in any order relative to other phases.

---

## Testing strategy

No production code — no unit or integration tests apply. Verification is grep-based string
confirmation after each phase. All verification commands are listed per phase above.

Final cross-check after all phases complete:
```bash
grep -rn "net8\.0\|net9\.0\|\.NET 8\b\|\.NET 9\b" \
  skills/test-scaffold/ \
  skills/nuget-package-scaffold/ \
  skills/dotnet-security-review/references/telerik-security.md \
  skills/dotnet-architecture-checklist/references/review-checklist.md \
  claude/agents/migration-orchestrator.md \
  opencode/agents/migration-orchestrator.md
```
Expected: zero matches (or only the KB search query string on
`skills/nuget-package-scaffold/SKILL.md:46`).

## Rollback plan

All changes are in version-controlled Markdown files. To revert any phase:

```bash
# Revert a single file
git checkout -- skills/test-scaffold/SKILL.md

# Revert all changed files at once
git checkout -- \
  skills/test-scaffold/SKILL.md \
  skills/nuget-package-scaffold/SKILL.md \
  skills/nuget-package-scaffold/references/csproj-metadata.md \
  claude/agents/migration-orchestrator.md \
  opencode/agents/migration-orchestrator.md \
  skills/dotnet-security-review/references/telerik-security.md \
  skills/dotnet-architecture-checklist/references/review-checklist.md
```

No migrations, no deployments, no compiled artifacts — rollback is instantaneous.

## Notes

- Phases are fully independent; the implementer may execute them in any order or in parallel.
- The KB search query string at `skills/nuget-package-scaffold/SKILL.md:46`
  (`"net8 net9 net10 TargetFrameworks"`) is intentionally left unchanged — it is a search hint,
  not a version prescription.
- `dotnet-architecture-checklist/references/review-checklist.md:73`
  (`### Interactive Auto (.NET 8+)`) is intentionally left unchanged — it is a minimum-version
  floor for a Blazor rendering feature, not a target version recommendation.
