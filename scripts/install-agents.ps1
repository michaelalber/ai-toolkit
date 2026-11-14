#Requires -Version 5.1
# Installs the shared skills tree from the repo into ~/.agents/skills/
#
# Usage:
#   pwsh scripts/install-agents.ps1
#
# Skills are a single source of truth in skills/ (identical Agent Skills format
# across Claude Code, OpenCode, and Pi). skills/ is flat -- this copies the whole
# tree, preserving the skills/<name>/SKILL.md layout that skill discovery walks.
#
# ~/.agents/skills/ is the one shared install: Pi, Goose, and Open WebUI all read
# it. Pi also reads ~/.pi/agent/skills/, so install-pi.ps1 calls this script
# instead of keeping a second copy there.

$ErrorActionPreference = 'Stop'

$RepoRoot  = Split-Path -Parent $PSScriptRoot
$AgentsDir = Join-Path $HOME '.agents'
$SkillsDir = Join-Path $AgentsDir 'skills'
$Manifest  = Join-Path $SkillsDir '.ai-toolkit-installed'

Write-Host "Installing skills from: $RepoRoot"

New-Item -ItemType Directory -Force -Path $SkillsDir | Out-Null

# <AI-Generated START>
# Full resync. Copy-Item never deletes, so remove (a) every skill the repo ships
# now and (b) every skill the last run installed, per the manifest -- (b) is
# what drops a skill that was deleted from the repo. Skills you added by hand
# are in neither list and are left untouched. Also clears stale team\ and
# professional\ subtrees from a pre-flatten install.
$RepoSkills = Get-ChildItem -Path (Join-Path $RepoRoot 'skills') -Directory | ForEach-Object Name
$Previous   = if (Test-Path $Manifest) { Get-Content $Manifest } else { @() }
$ToRemove   = @('team', 'professional') + $Previous + $RepoSkills |
    Where-Object { $_ -and $_ -notmatch '[\\/]' -and -not $_.StartsWith('.') } |
    Sort-Object -Unique
foreach ($Name in $ToRemove) {
    $Dest = Join-Path $SkillsDir $Name
    if (Test-Path $Dest) { Remove-Item -Path $Dest -Recurse -Force }
}

Copy-Item -Path (Join-Path $RepoRoot 'skills\*') -Destination $SkillsDir -Recurse -Force
Set-Content -Path $Manifest -Value $RepoSkills
# <AI-Generated END>

Write-Host "Done."
Write-Host "  Skills → $SkillsDir ($($RepoSkills.Count) installed)"
