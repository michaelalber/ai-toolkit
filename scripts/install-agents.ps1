#Requires -Version 5.1
# Installs the shared skills tree from the repo into ~/.agents/skills/
#
# Usage:
#   pwsh scripts/install-agents.ps1
#
# Skills are a single source of truth in skills/ (identical Agent Skills format
# across Claude Code, OpenCode, and Pi). skills/ is flat -- this copies the whole
# tree, preserving the skills/<name>/SKILL.md layout that skill discovery walks.

$ErrorActionPreference = 'Stop'

$RepoRoot  = Split-Path -Parent $PSScriptRoot
$AgentsDir = Join-Path $HOME '.agents'
$SkillsDir = Join-Path $AgentsDir 'skills'

Write-Host "Installing skills from: $RepoRoot"

New-Item -ItemType Directory -Force -Path $SkillsDir | Out-Null

# Full resync of the repo-owned skills. Copy-Item overwrites and adds but
# never deletes, so a skill removed from the repo would linger here and stay
# invocable. Prune by what the repo currently ships -- skills\ is flat, so this
# walks each skills\<name> dir and removes its counterpart in $SkillsDir. Skills
# you added by hand under skills\ are not in the repo listing, so they are left
# untouched. Also clears any stale team\/professional\ subtrees left behind by
# an older, pre-flatten install.
foreach ($Sub in 'team', 'professional') {
    $StaleDir = Join-Path $SkillsDir $Sub
    if (Test-Path $StaleDir) { Remove-Item -Path $StaleDir -Recurse -Force }
}
Get-ChildItem -Path (Join-Path $RepoRoot 'skills') -Directory | ForEach-Object {
    $Dest = Join-Path $SkillsDir $_.Name
    if (Test-Path $Dest) { Remove-Item -Path $Dest -Recurse -Force }
}

Copy-Item -Path (Join-Path $RepoRoot 'skills\*') -Destination $SkillsDir -Recurse -Force -Verbose

Write-Host "Done."
Write-Host "  Skills → $SkillsDir"
