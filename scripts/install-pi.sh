#!/usr/bin/env bash
# Installs Pi global config from the repo into ~/.pi/agent/
#
# Usage:
#   bash scripts/install-pi.sh          # installs AGENTS-7b.md  (7B-safe default)
#   bash scripts/install-pi.sh --full   # installs AGENTS-20b.md (20B+ models)
#
# The two AGENTS files are standalone, self-contained globals — exactly one is
# copied to ~/.pi/agent/AGENTS.md. They are NOT layered/merged.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PI_DIR="${HOME}/.pi/agent"
USE_FULL=false

for arg in "$@"; do
  if [[ "$arg" == "--full" ]]; then
    USE_FULL=true
  fi
done

echo "Installing Pi global config from: ${REPO_ROOT}"

mkdir -p "${PI_DIR}"

if [[ "${USE_FULL}" == true ]]; then
  cp -v "${REPO_ROOT}/pi/global/AGENTS-20b.md" "${PI_DIR}/AGENTS.md"
  echo "Installed: AGENTS-20b.md as AGENTS.md (20B+ variant)"
  echo "  For 20B+ context, set settings.json compaction to reserveTokens 4096 / keepRecentTokens 24576."
else
  cp -v "${REPO_ROOT}/pi/global/AGENTS-7b.md" "${PI_DIR}/AGENTS.md"
  echo "Installed: AGENTS-7b.md as AGENTS.md (7B-safe default)"
  echo "  Run with --full to install the 20B+ variant instead."
fi

cp -v "${REPO_ROOT}/pi/global/models.json" "${PI_DIR}/models.json"
cp -v "${REPO_ROOT}/pi/global/settings.json" "${PI_DIR}/settings.json"

# Skills — single source of truth in skills/, identical Agent Skills format
# across Claude Code, OpenCode, and Pi. Pi discovers SKILL.md directories
# recursively under ~/.pi/agent/skills/. See pi/SKILLS-local.md for which
# skills are suited to local 32B inference vs. cloud.
mkdir -p "${PI_DIR}/skills"
cp -rv "${REPO_ROOT}/skills/"* "${PI_DIR}/skills/"

# Knowledge grounding — Pi has no MCP support, so the 50 skills that ground
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
echo "  1. Edit ${PI_DIR}/models.json — delete entries for models you have not pulled."
echo "  2. Create your Ollama model: ollama create pi-coder -f pi/global/Modelfile-7b"
echo "  3. Copy pi/global/SYSTEM.md to your project root and trim to one variant."
if ! command -v grounded-code-mcp >/dev/null 2>&1; then
  echo "  4. Install the grounded-code-mcp CLI and ensure it is on PATH —"
  echo "     without it, grounded skills (security reviews, migrations) lose their"
  echo "     authoritative source. See pi/SKILLS-local.md (📚 flag) for the affected skills."
  echo "  5. Run: pi --model ollama/pi-coder"
else
  echo "  4. Run: pi --model ollama/pi-coder"
fi
