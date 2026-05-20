#Requires -Version 5.1
# Installs Claude agents, skills, and commands from the repo into ~/.claude/

$ErrorActionPreference = 'Stop'

$RepoRoot    = Split-Path -Parent $PSScriptRoot
$ClaudeDir   = Join-Path $HOME '.claude'
$AgentsDir   = Join-Path $ClaudeDir 'agents'
$SkillsDir   = Join-Path $ClaudeDir 'skills'
$CommandsDir = Join-Path $ClaudeDir 'commands'

Write-Host "Installing Claude agents, skills, and commands from: $RepoRoot"

New-Item -ItemType Directory -Force -Path $AgentsDir   | Out-Null
New-Item -ItemType Directory -Force -Path $SkillsDir   | Out-Null
New-Item -ItemType Directory -Force -Path $CommandsDir | Out-Null

Get-ChildItem -Path (Join-Path $RepoRoot 'claude\agents') -Filter '*.md' -Recurse |
    Copy-Item -Destination $AgentsDir -Verbose

Copy-Item -Path (Join-Path $RepoRoot 'skills\*') -Destination $SkillsDir -Recurse -Force -Verbose

Get-ChildItem -Path (Join-Path $RepoRoot 'claude\commands') -Filter '*.md' -Recurse |
    Copy-Item -Destination $CommandsDir -Verbose

Write-Host "Done."
Write-Host "  Agents   → $AgentsDir"
Write-Host "  Skills   → $SkillsDir"
Write-Host "  Commands → $CommandsDir"
