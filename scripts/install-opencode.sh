#!/usr/bin/env bash
# Installs OpenCode agents and skills from the repo into ~/.config/opencode/

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OPENCODE_DIR="${HOME}/.config/opencode"

echo "Installing OpenCode agents and skills from: ${REPO_ROOT}"

mkdir -p "${OPENCODE_DIR}/agents"
mkdir -p "${OPENCODE_DIR}/skills"
mkdir -p "${OPENCODE_DIR}/commands"

find "${REPO_ROOT}/opencode/agents" -name "*.md" -exec cp -v {} "${OPENCODE_DIR}/agents/" \;
cp -rv "${REPO_ROOT}/skills/"* "${OPENCODE_DIR}/skills/"
find "${REPO_ROOT}/opencode/commands" -name "*.md" -exec cp -v {} "${OPENCODE_DIR}/commands/" \;

echo "Done."
echo "  Agents   → ${OPENCODE_DIR}/agents/"
echo "  Skills   → ${OPENCODE_DIR}/skills/"
echo "  Commands → ${OPENCODE_DIR}/commands/"
echo ""
echo "Global config (manual — edit YOUR_USERNAME first):"
echo "  cp ${REPO_ROOT}/opencode/global/AGENTS.md ~/.config/opencode/AGENTS.md"
echo "  cp ${REPO_ROOT}/opencode/global/opencode.json ~/.config/opencode/opencode.json"
