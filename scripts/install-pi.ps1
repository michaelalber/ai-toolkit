#Requires -Version 5.1
# Installs Pi global config from the repo into ~/.pi/agent/
#
# Usage:
#   pwsh scripts/install-pi.ps1          # installs AGENTS-7b.md  (7B-safe default)
#   pwsh scripts/install-pi.ps1 -Full    # installs AGENTS-20b.md (20B+ models)
#
# The two AGENTS files are standalone, self-contained globals — exactly one is
# copied to ~/.pi/agent/AGENTS.md. They are NOT layered/merged.

param(
    [switch]$Full
)

$ErrorActionPreference = 'Stop'

$RepoRoot = Split-Path -Parent $PSScriptRoot
$PiDir    = Join-Path $HOME '.pi\agent'

Write-Host "Installing Pi global config from: $RepoRoot"

New-Item -ItemType Directory -Force -Path $PiDir | Out-Null

if ($Full) {
    Copy-Item -Path (Join-Path $RepoRoot 'pi\global\AGENTS-20b.md') -Destination (Join-Path $PiDir 'AGENTS.md') -Force -Verbose
    Write-Host "Installed: AGENTS-20b.md as AGENTS.md (20B+ variant)"
    Write-Host "  For 20B+ context, set settings.json compaction to reserveTokens 4096 / keepRecentTokens 24576."
} else {
    Copy-Item -Path (Join-Path $RepoRoot 'pi\global\AGENTS-7b.md') -Destination (Join-Path $PiDir 'AGENTS.md') -Force -Verbose
    Write-Host "Installed: AGENTS-7b.md as AGENTS.md (7B-safe default)"
    Write-Host "  Run with -Full to install the 20B+ variant instead."
}

Copy-Item -Path (Join-Path $RepoRoot 'pi\global\models.json')   -Destination (Join-Path $PiDir 'models.json')   -Force -Verbose
Copy-Item -Path (Join-Path $RepoRoot 'pi\global\settings.json') -Destination (Join-Path $PiDir 'settings.json') -Force -Verbose

# Skills — single source of truth in skills/, identical Agent Skills format
# across Claude Code, OpenCode, and Pi. Pi discovers SKILL.md directories
# recursively under ~/.pi/agent/skills/. See pi/SKILLS-local.md for which
# skills are suited to local 32B inference vs. cloud.
$SkillsDir = Join-Path $PiDir 'skills'
New-Item -ItemType Directory -Force -Path $SkillsDir | Out-Null
Copy-Item -Path (Join-Path $RepoRoot 'skills\*') -Destination $SkillsDir -Recurse -Force -Verbose

# Knowledge grounding — Pi has no MCP support, so the 50 skills that ground
# against the knowledge base call the grounded-code-mcp CLI directly (see the
# Knowledge Grounding section of the installed AGENTS.md). Warn if it is missing.
$Grounded = Get-Command grounded-code-mcp -ErrorAction SilentlyContinue
if ($Grounded) {
    $GroundedStatus = "found on PATH"
} else {
    $GroundedStatus = "NOT FOUND — 50 grounded skills will fall back to training data"
}

Write-Host ""
Write-Host "Done."
Write-Host "  AGENTS.md     → $(Join-Path $PiDir 'AGENTS.md')"
Write-Host "  models.json   → $(Join-Path $PiDir 'models.json')"
Write-Host "  settings.json → $(Join-Path $PiDir 'settings.json')"
Write-Host "  skills        → $SkillsDir"
Write-Host "  grounded-code-mcp CLI → $GroundedStatus"
Write-Host ""
Write-Host "Model selection: Pi runs the single defaultModel in settings.json (switch with /model)."
Write-Host "  Per-task auto-routing is OPT-IN and not installed. To enable it, copy"
Write-Host "  pi/global/router-config.json.example → $(Join-Path $PiDir 'router-config.json')"
Write-Host "  (drop the .example suffix and the _README key)."
Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. Edit $(Join-Path $PiDir 'models.json') — delete entries for models you have not pulled."
Write-Host "  2. Create your Ollama model: ollama create pi-coder -f pi/global/Modelfile-7b"
Write-Host "  3. Copy pi/global/SYSTEM.md to your project root and trim to one variant."
if (-not $Grounded) {
    Write-Host "  4. Install the grounded-code-mcp CLI and ensure it is on PATH —"
    Write-Host "     without it, grounded skills (security reviews, migrations) lose their"
    Write-Host "     authoritative source. See pi/SKILLS-local.md (📚 flag) for the affected skills."
    Write-Host "  5. Run: pi --model ollama/pi-coder"
} else {
    Write-Host "  4. Run: pi --model ollama/pi-coder"
}
