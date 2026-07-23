#!/usr/bin/env bash
# Installs Pi config and skills from the repo into ~/.pi/agent/
#
# Usage:
#   bash scripts/install-pi.sh
#
# Installs the shared skills tree, plus global config on a FRESH install only.
#
# Global config (AGENTS.md, models.json, settings.json) is copy-if-absent: a new
# install gets a working set, but an existing file is never overwritten. All
# three are expected to be edited after install (host URLs, model names, local
# rules), so a re-run must not discard those edits. Skills are still a full
# resync — they are repo-owned and carry no user state.
# Target model tier is 20B+ — smaller models are below the agentic-coding floor.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PI_DIR="${HOME}/.pi/agent"

echo "Installing Pi config and skills from: ${REPO_ROOT}"

mkdir -p "${PI_DIR}"

# Global config — copy-if-absent, never overwrite. Unlike install-claude.sh and
# install-opencode.sh (which leave their global files fully manual), Pi needs
# these three present to start at all, so a fresh install seeds them. An
# existing file is always left alone: it is the user's, not the repo's.
GLOBAL_SKIPPED=""
for f in AGENTS.md models.json settings.json; do
  if [[ -e "${PI_DIR}/${f}" ]]; then
    echo "  ${f} — already present, left untouched"
    GLOBAL_SKIPPED="${GLOBAL_SKIPPED} ${f}"
  else
    cp -v "${REPO_ROOT}/pi/global/${f}" "${PI_DIR}/${f}"
  fi
done

# Skills — single source of truth in skills/, identical Agent Skills format
# across Claude Code, OpenCode, and Pi. Pi discovers SKILL.md directories
# recursively under ~/.pi/agent/skills/. See pi/SKILLS-local.md for which
# skills are suited to local 32B inference vs. cloud.
#
# Full resync of the repo-owned subtrees: cp -r overwrites and adds but never
# deletes, so a skill removed from the repo would linger here and stay
# invocable. Only team/ and professional/ are repo-owned — anything else you
# added by hand under skills/ is left untouched.
mkdir -p "${PI_DIR}/skills"
rm -rf "${PI_DIR}/skills/team" "${PI_DIR}/skills/professional"
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
echo "  skills        → ${PI_DIR}/skills/"
echo "  grounded-code-mcp CLI → ${GROUNDED_STATUS}"
echo ""
if [[ -n "${GLOBAL_SKIPPED// /}" ]]; then
  echo "Global config left untouched (already present — never overwritten):"
  for f in ${GLOBAL_SKIPPED}; do
    echo "  ${f} — to take the repo version, diff it first:"
    echo "      diff ${PI_DIR}/${f} ${REPO_ROOT}/pi/global/${f}"
  done
  echo ""
fi
echo "  Compaction ships tuned for a 128K model. On a 40K dense model, lower"
echo "  settings.json to reserveTokens 2048 / keepRecentTokens 8192."
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
echo "       ollama create qwen3.6-35b-a3b-agent -f pi/global/Modelfile-moe-agent  # MoE, 128K"
echo "       ollama create qwen3.6-27b-agent     -f pi/global/Modelfile-20b        # dense, 128K"
echo "  3. Copy pi/global/SYSTEM.md to your project root."
if ! command -v grounded-code-mcp >/dev/null 2>&1; then
  echo "  4. Install the grounded-code-mcp CLI and ensure it is on PATH —"
  echo "     without it, grounded skills (security reviews, migrations) lose their"
  echo "     authoritative source. See pi/SKILLS-local.md (📚 flag) for the affected skills."
  echo "  5. Run: pi --model ollama-lan/qwen3.6-27b-agent:latest"
else
  echo "  4. Run: pi --model ollama-lan/qwen3.6-27b-agent:latest"
fi
