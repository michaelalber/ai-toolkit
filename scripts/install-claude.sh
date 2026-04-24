#!/usr/bin/env bash
# Installs Claude agents and skills from the repo into ~/.claude/

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLAUDE_DIR="${HOME}/.claude"

echo "Installing Claude agents and skills from: ${REPO_ROOT}"

mkdir -p "${CLAUDE_DIR}/agents"
mkdir -p "${CLAUDE_DIR}/skills"
mkdir -p "${CLAUDE_DIR}/commands"

cp -v "${REPO_ROOT}/claude/agents/"*.md "${CLAUDE_DIR}/agents/"
cp -rv "${REPO_ROOT}/skills/"* "${CLAUDE_DIR}/skills/"
cp -v "${REPO_ROOT}/claude/commands/"*.md "${CLAUDE_DIR}/commands/"

echo "Done."
echo "  Agents   → ${CLAUDE_DIR}/agents/"
echo "  Skills   → ${CLAUDE_DIR}/skills/"
echo "  Commands → ${CLAUDE_DIR}/commands/"
echo ""
echo "Global config (manual — edit YOUR_USERNAME first):"
echo "  cp ${REPO_ROOT}/claude/global/CLAUDE.md ~/.claude/CLAUDE.md"
echo "  cp ${REPO_ROOT}/claude/global/settings.json ~/.claude/settings.json"
echo "  cp ${REPO_ROOT}/claude/global/settings.local.json ~/.claude/settings.local.json"
