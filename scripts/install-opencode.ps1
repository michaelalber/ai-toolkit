#Requires -Version 5.1
# Installs OpenCode agents, skills, and commands from the repo into ~/.config/opencode/

$ErrorActionPreference = 'Stop'

$RepoRoot    = Split-Path -Parent $PSScriptRoot
$OpenCodeDir = Join-Path $HOME '.config\opencode'
$AgentsDir   = Join-Path $OpenCodeDir 'agents'
$SkillsDir   = Join-Path $OpenCodeDir 'skills'
$CommandsDir = Join-Path $OpenCodeDir 'commands'

Write-Host "Installing OpenCode agents, skills, and commands from: $RepoRoot"

New-Item -ItemType Directory -Force -Path $AgentsDir   | Out-Null
New-Item -ItemType Directory -Force -Path $SkillsDir   | Out-Null
New-Item -ItemType Directory -Force -Path $CommandsDir | Out-Null

# Agents and commands are copied flat, so the same prune applies: without it a
# removed agent lingers and stays spawnable. These two dirs are wholly repo-owned.
Remove-Item -Path (Join-Path $AgentsDir '*.md')   -Force -ErrorAction SilentlyContinue
Remove-Item -Path (Join-Path $CommandsDir '*.md') -Force -ErrorAction SilentlyContinue

Get-ChildItem -Path (Join-Path $RepoRoot 'opencode\agents') -Filter '*.md' -Recurse |
    Copy-Item -Destination $AgentsDir -Verbose

# Full resync of the repo-owned subtrees: Copy-Item overwrites and adds but
# never deletes, so a skill removed from the repo would linger here and stay
# invocable. Only team\ and professional\ are repo-owned — anything else you
# added by hand under skills\ is left untouched.
foreach ($Sub in 'team', 'professional') {
    $StaleDir = Join-Path $SkillsDir $Sub
    if (Test-Path $StaleDir) { Remove-Item -Path $StaleDir -Recurse -Force }
}

Copy-Item -Path (Join-Path $RepoRoot 'skills\*') -Destination $SkillsDir -Recurse -Force -Verbose

Get-ChildItem -Path (Join-Path $RepoRoot 'opencode\commands') -Filter '*.md' -Recurse |
    Copy-Item -Destination $CommandsDir -Verbose

Write-Host "Done."
Write-Host "  Agents   → $AgentsDir"
Write-Host "  Skills   → $SkillsDir"
Write-Host "  Commands → $CommandsDir"
