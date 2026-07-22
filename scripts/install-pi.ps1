#Requires -Version 5.1
# Installs Pi global config from the repo into ~/.pi/agent/
#
# Usage:
#   pwsh scripts/install-pi.ps1
#
# Installs the single Pi global (pi\global\AGENTS.md) to ~/.pi/agent/AGENTS.md,
# matching how claude/global and opencode/global each ship one global file.
# Target model tier is 20B+ — smaller models are below the agentic-coding floor.

$ErrorActionPreference = 'Stop'

$RepoRoot = Split-Path -Parent $PSScriptRoot
$PiDir    = Join-Path $HOME '.pi\agent'

Write-Host "Installing Pi global config from: $RepoRoot"

New-Item -ItemType Directory -Force -Path $PiDir | Out-Null

Copy-Item -Path (Join-Path $RepoRoot 'pi\global\AGENTS.md') -Destination (Join-Path $PiDir 'AGENTS.md') -Force -Verbose
Write-Host "Installed: AGENTS.md (target tier 20B+)"
Write-Host "  Compaction ships tuned for a 128K model. On a 40K dense model, lower"
Write-Host "  settings.json to reserveTokens 2048 / keepRecentTokens 8192."

Copy-Item -Path (Join-Path $RepoRoot 'pi\global\models.json')   -Destination (Join-Path $PiDir 'models.json')   -Force -Verbose
Copy-Item -Path (Join-Path $RepoRoot 'pi\global\settings.json') -Destination (Join-Path $PiDir 'settings.json') -Force -Verbose

# Skills — single source of truth in skills/, identical Agent Skills format
# across Claude Code, OpenCode, and Pi. Pi discovers SKILL.md directories
# recursively under ~/.pi/agent/skills/. See pi/SKILLS-local.md for which
# skills are suited to local 32B inference vs. cloud.
#
# Full resync of the repo-owned subtrees: Copy-Item overwrites and adds but
# never deletes, so a skill removed from the repo would linger here and stay
# invocable. Only team\ and professional\ are repo-owned — anything else you
# added by hand under skills\ is left untouched.
$SkillsDir = Join-Path $PiDir 'skills'
New-Item -ItemType Directory -Force -Path $SkillsDir | Out-Null
foreach ($Sub in 'team', 'professional') {
    $StaleDir = Join-Path $SkillsDir $Sub
    if (Test-Path $StaleDir) { Remove-Item -Path $StaleDir -Recurse -Force }
}
Copy-Item -Path (Join-Path $RepoRoot 'skills\*') -Destination $SkillsDir -Recurse -Force -Verbose

# Knowledge grounding — Pi reaches MCP only through a community extension, so
# the 50 skills that ground against the knowledge base call the grounded-code-mcp
# CLI directly (see the Knowledge Grounding section of the installed AGENTS.md).
# Warn if it is missing.
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
Write-Host "  1. Edit $(Join-Path $PiDir 'models.json') — set the ollama-lan baseUrl to your Ollama host"
Write-Host "     and delete entries for models you have not pulled."
Write-Host "  2. Create your Ollama model:"
Write-Host "       ollama create qwen3.6-35b-a3b-agent -f pi/global/Modelfile-moe-agent  # MoE, 128K"
Write-Host "       ollama create qwen3.6-27b-agent     -f pi/global/Modelfile-20b        # dense, 128K"
Write-Host "  3. Copy pi/global/SYSTEM.md to your project root."
if (-not $Grounded) {
    Write-Host "  4. Install the grounded-code-mcp CLI and ensure it is on PATH —"
    Write-Host "     without it, grounded skills (security reviews, migrations) lose their"
    Write-Host "     authoritative source. See pi/SKILLS-local.md (📚 flag) for the affected skills."
    Write-Host "  5. Run: pi --model ollama-lan/qwen3.6-27b-agent:latest"
} else {
    Write-Host "  4. Run: pi --model ollama-lan/qwen3.6-27b-agent:latest"
}
