#!/usr/bin/env bash
# Installs Pi global config from the repo into ~/.pi/agent/
#
# Usage:
#   bash scripts/install-pi.sh
#
# Installs the single Pi global (pi/global/AGENTS.md) to ~/.pi/agent/AGENTS.md,
# matching how claude/global and opencode/global each ship one global file.
# Target model tier is 20B+ — smaller models are below the agentic-coding floor.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PI_DIR="${HOME}/.pi/agent"

echo "Installing Pi global config from: ${REPO_ROOT}"

mkdir -p "${PI_DIR}"

cp -v "${REPO_ROOT}/pi/global/AGENTS.md" "${PI_DIR}/AGENTS.md"
echo "Installed: AGENTS.md (target tier 20B+)"
echo "  Compaction ships tuned for a 128K model. On a 40K dense model, lower"
echo "  settings.json to reserveTokens 2048 / keepRecentTokens 8192."

cp -v "${REPO_ROOT}/pi/global/models.json" "${PI_DIR}/models.json"
cp -v "${REPO_ROOT}/pi/global/settings.json" "${PI_DIR}/settings.json"

# Skills — single source of truth in skills/, identical Agent Skills format
# across Claude Code, OpenCode, and Pi. Pi discovers SKILL.md directories
# recursively under ~/.pi/agent/skills/. See pi/SKILLS-local.md for which
# skills are suited to local 32B inference vs. cloud.
mkdir -p "${PI_DIR}/skills"
cp -rv "${REPO_ROOT}/skills/"* "${PI_DIR}/skills/"

# Knowledge grounding — Pi reaches MCP only through a community extension, so
# the 50 skills that ground
# against the knowledge base call the grounded-code-mcp CLI directly (see the
# Knowledge Grounding section of the installed AGENTS.md). Warn if it is missing.
if command -v grounded-code-mcp >/dev/null 2>&1; then
  GROUNDED_STATUS="found on PATH"
else
  GROUNDED_STATUS="NOT FOUND — 50 grounded skills will fall back to training data"
fi

echo ""
echo "Done."
echo "  AGENTS.md     → ${PI_DIR}/AGENTS.md"
echo "  models.json   → ${PI_DIR}/models.json"
echo "  settings.json → ${PI_DIR}/settings.json"
echo "  skills        → ${PI_DIR}/skills/"
echo "  grounded-code-mcp CLI → ${GROUNDED_STATUS}"
echo ""
echo "Model selection: Pi runs the single defaultModel in settings.json (switch with /model)."
echo "  Per-task auto-routing is OPT-IN and not installed. To enable it, copy"
echo "  pi/global/router-config.json.example → ${PI_DIR}/router-config.json"
echo "  (drop the .example suffix and the _README key)."
echo ""
echo "Next steps:"
echo "  1. Edit ${PI_DIR}/models.json — set the ollama-lan baseUrl to your Ollama host"
echo "     and delete entries for models you have not pulled."
echo "  2. Create your Ollama model:"
echo "       ollama create qwen3-30b-a3b-agent -f pi/global/Modelfile-moe-agent   # MoE, 128K"
echo "       ollama create qwen3-32b-agent     -f pi/global/Modelfile-20b         # dense, 40K"
echo "  3. Copy pi/global/SYSTEM.md to your project root."
if ! command -v grounded-code-mcp >/dev/null 2>&1; then
  echo "  4. Install the grounded-code-mcp CLI and ensure it is on PATH —"
  echo "     without it, grounded skills (security reviews, migrations) lose their"
  echo "     authoritative source. See pi/SKILLS-local.md (📚 flag) for the affected skills."
  echo "  5. Run: pi --model ollama-lan/qwen3-30b-a3b-agent:latest"
else
  echo "  4. Run: pi --model ollama-lan/qwen3-30b-a3b-agent:latest"
fi
