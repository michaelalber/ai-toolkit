#Requires -Version 5.1
# Installs Claude agents and skills from the repo into ~/.claude/

$ErrorActionPreference = 'Stop'

$RepoRoot   = Split-Path -Parent $PSScriptRoot
$ClaudeDir  = Join-Path $HOME '.claude'
$AgentsDir  = Join-Path $ClaudeDir 'agents'
$SkillsDir  = Join-Path $ClaudeDir 'skills'

Write-Host "Installing Claude agents and skills from: $RepoRoot"

New-Item -ItemType Directory -Force -Path $AgentsDir | Out-Null
New-Item -ItemType Directory -Force -Path $SkillsDir | Out-Null

Get-ChildItem -Path (Join-Path $RepoRoot 'claude\agents\*.md') |
    Copy-Item -Destination $AgentsDir -Verbose

Copy-Item -Path (Join-Path $RepoRoot 'skills\*') -Destination $SkillsDir -Recurse -Force -Verbose

Write-Host "Done. Agents → $AgentsDir  |  Skills → $SkillsDir"
