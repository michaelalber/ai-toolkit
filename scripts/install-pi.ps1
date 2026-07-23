#Requires -Version 5.1
# Installs Pi config and skills from the repo into ~/.pi/agent/
#
# Usage:
#   pwsh scripts/install-pi.ps1
#
# Installs the shared skills tree, plus global config on a FRESH install only.
#
# Global config (AGENTS.md, models.json, settings.json) is copy-if-absent: a new
# install gets a working set, but an existing file is never overwritten. All
# three are expected to be edited after install (host URLs, model names, local
# rules), so a re-run must not discard those edits. Skills are still a full
# resync — they are repo-owned and carry no user state.
# Target model tier is 20B+ — smaller models are below the agentic-coding floor.

$ErrorActionPreference = 'Stop'

$RepoRoot = Split-Path -Parent $PSScriptRoot
$PiDir    = Join-Path $HOME '.pi\agent'

Write-Host "Installing Pi config and skills from: $RepoRoot"

New-Item -ItemType Directory -Force -Path $PiDir | Out-Null

# Global config — copy-if-absent, never overwrite. Unlike install-claude and
# install-opencode (which leave their global files fully manual), Pi needs these
# three present to start at all, so a fresh install seeds them. An existing file
# is always left alone: it is the user's, not the repo's.
$GlobalSkipped = @()
foreach ($f in 'AGENTS.md', 'models.json', 'settings.json') {
    $Dest = Join-Path $PiDir $f
    if (Test-Path $Dest) {
        Write-Host "  $f — already present, left untouched"
        $GlobalSkipped += $f
    } else {
        Copy-Item -Path (Join-Path $RepoRoot (Join-Path 'pi\global' $f)) -Destination $Dest -Verbose
    }
}

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
Write-Host "  skills        → $SkillsDir"
Write-Host "  grounded-code-mcp CLI → $GroundedStatus"
Write-Host ""
if ($GlobalSkipped.Count -gt 0) {
    Write-Host "Global config left untouched (already present — never overwritten):"
    foreach ($f in $GlobalSkipped) {
        $Dest = Join-Path $PiDir $f
        $Src  = Join-Path $RepoRoot (Join-Path 'pi\global' $f)
        Write-Host "  $f — to take the repo version, diff it first:"
        Write-Host "      Compare-Object (Get-Content '$Dest') (Get-Content '$Src')"
    }
    Write-Host ""
}
Write-Host "  Compaction ships tuned for a 128K model. On a 40K dense model, lower"
Write-Host "  settings.json to reserveTokens 2048 / keepRecentTokens 8192."
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
