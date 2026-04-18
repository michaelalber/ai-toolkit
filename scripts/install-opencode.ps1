#Requires -Version 5.1
# Installs OpenCode agents and skills from the repo into ~/.config/opencode/

$ErrorActionPreference = 'Stop'

$RepoRoot    = Split-Path -Parent $PSScriptRoot
$OpenCodeDir = Join-Path $HOME '.config\opencode'
$AgentsDir   = Join-Path $OpenCodeDir 'agents'
$SkillsDir   = Join-Path $OpenCodeDir 'skills'

Write-Host "Installing OpenCode agents and skills from: $RepoRoot"

New-Item -ItemType Directory -Force -Path $AgentsDir | Out-Null
New-Item -ItemType Directory -Force -Path $SkillsDir | Out-Null

Get-ChildItem -Path (Join-Path $RepoRoot 'opencode\agents\*.md') |
    Copy-Item -Destination $AgentsDir -Verbose

Copy-Item -Path (Join-Path $RepoRoot 'skills\*') -Destination $SkillsDir -Recurse -Force -Verbose

Write-Host "Done. Agents → $AgentsDir  |  Skills → $SkillsDir"
