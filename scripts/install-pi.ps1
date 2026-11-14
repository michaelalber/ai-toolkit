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
# rules), so a re-run must not discard those edits. Skills are a full resync
# into ~/.agents/skills/ via install-agents.ps1 — repo-owned, no user state.
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

# Skills — installed once to ~/.agents/skills/ by install-agents.ps1. Pi reads
# both ~/.pi/agent/skills/ and ~/.agents/skills/, and a name found in both is a
# collision warning, so the repo skills are NOT copied to ~/.pi/agent/skills/.
# See pi/SKILLS-local.md for which skills suit local inference vs. cloud.
#
# <AI-Generated START>
# Migration: an older version of this script copied the repo skills into
# ~/.pi/agent/skills/. Remove those copies; skills you added by hand stay.
$PiSkillsDir = Join-Path $PiDir 'skills'
if (Test-Path $PiSkillsDir) {
    foreach ($Name in @('team', 'professional') + (Get-ChildItem -Path (Join-Path $RepoRoot 'skills') -Directory | ForEach-Object Name)) {
        $Dest = Join-Path $PiSkillsDir $Name
        if (Test-Path $Dest) { Remove-Item -Path $Dest -Recurse -Force }
    }
    if (-not (Get-ChildItem -Path $PiSkillsDir -Force)) {
        Remove-Item -Path $PiSkillsDir
    } else {
        Write-Host "  $PiSkillsDir kept — it holds skills not from this repo"
    }
}
& (Join-Path $PSScriptRoot 'install-agents.ps1')
$SkillsDir = Join-Path $HOME '.agents\skills'
# <AI-Generated END>

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
Write-Host "  skills        → $SkillsDir (shared with Goose / Open WebUI)"
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
Write-Host "  Compaction ships tuned for a 128K window. On a 32-40K window, lower"
Write-Host "  settings.json to reserveTokens 2048 / keepRecentTokens 8192."
Write-Host ""
Write-Host "Model selection: Pi runs the single defaultModel in settings.json (switch with /model)."
Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. Edit $(Join-Path $PiDir 'models.json') — set the ollama baseUrl to your Ollama host"
Write-Host "     and delete entries for models you have not pulled."
Write-Host "  2. Set OLLAMA_CONTEXT_LENGTH=131072 on the Ollama server (Pi cannot set the"
Write-Host "     context per request), then pull the models:"
Write-Host "       ollama pull flint:40b-a2b-qat-int4"
Write-Host "       ollama pull gemma4:31b-nvfp4"
if (-not $Grounded) {
    Write-Host "  3. Install the grounded-code-mcp CLI and ensure it is on PATH —"
    Write-Host "     without it, grounded skills (security reviews, migrations) lose their"
    Write-Host "     authoritative source. See pi/SKILLS-local.md (📚 flag) for the affected skills."
    Write-Host "  4. Run: pi --model ollama/flint:40b-a2b-qat-int4"
} else {
    Write-Host "  3. Run: pi --model ollama/flint:40b-a2b-qat-int4"
}
