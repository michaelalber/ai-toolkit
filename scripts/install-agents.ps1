#Requires -Version 5.1
# Installs the shared skills tree from the repo into ~/.agents/skills/
#
# Usage:
#   pwsh scripts/install-agents.ps1
#
# Skills are a single source of truth in skills/ (identical Agent Skills format
# across Claude Code, OpenCode, and Pi). This copies both the team/ and
# professional/ subtrees, preserving the skills/<audience>/<name>/SKILL.md layout
# that skill discovery walks recursively.

$ErrorActionPreference = 'Stop'

$RepoRoot  = Split-Path -Parent $PSScriptRoot
$AgentsDir = Join-Path $HOME '.agents'
$SkillsDir = Join-Path $AgentsDir 'skills'

Write-Host "Installing skills from: $RepoRoot"

New-Item -ItemType Directory -Force -Path $SkillsDir | Out-Null

# Full resync of the repo-owned subtrees: Copy-Item overwrites and adds but
# never deletes, so a skill removed from the repo would linger here and stay
# invocable. Only team\ and professional\ are repo-owned — anything else you
# added by hand under skills\ is left untouched.
foreach ($Sub in 'team', 'professional') {
    $StaleDir = Join-Path $SkillsDir $Sub
    if (Test-Path $StaleDir) { Remove-Item -Path $StaleDir -Recurse -Force }
}

Copy-Item -Path (Join-Path $RepoRoot 'skills\*') -Destination $SkillsDir -Recurse -Force -Verbose

Write-Host "Done."
Write-Host "  Skills → $SkillsDir"
