#!/usr/bin/env bash
# Installs Claude agents and skills from the repo into ~/.claude/

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLAUDE_DIR="${HOME}/.claude"

echo "Installing Claude agents and skills from: ${REPO_ROOT}"

mkdir -p "${CLAUDE_DIR}/agents"
mkdir -p "${CLAUDE_DIR}/skills"

cp -v "${REPO_ROOT}/claude/agents/"*.md "${CLAUDE_DIR}/agents/"

cp -rv "${REPO_ROOT}/skills/"* "${CLAUDE_DIR}/skills/"

echo "Done. Agents → ${CLAUDE_DIR}/agents/  |  Skills → ${CLAUDE_DIR}/skills/"
