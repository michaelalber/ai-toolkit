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

Get-ChildItem -Path (Join-Path $RepoRoot 'opencode\agents') -Filter '*.md' -Recurse |
    Copy-Item -Destination $AgentsDir -Verbose

Copy-Item -Path (Join-Path $RepoRoot 'skills\*') -Destination $SkillsDir -Recurse -Force -Verbose

Get-ChildItem -Path (Join-Path $RepoRoot 'opencode\commands') -Filter '*.md' -Recurse |
    Copy-Item -Destination $CommandsDir -Verbose

Write-Host "Done."
Write-Host "  Agents   → $AgentsDir"
Write-Host "  Skills   → $SkillsDir"
Write-Host "  Commands → $CommandsDir"
