#!/usr/bin/env bash
# Installs OpenCode agents and skills from the repo into ~/.config/opencode/

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OPENCODE_DIR="${HOME}/.config/opencode"

echo "Installing OpenCode agents and skills from: ${REPO_ROOT}"

mkdir -p "${OPENCODE_DIR}/agents"
mkdir -p "${OPENCODE_DIR}/skills"

cp -v "${REPO_ROOT}/opencode/agents/"*.md "${OPENCODE_DIR}/agents/"

cp -rv "${REPO_ROOT}/skills/"* "${OPENCODE_DIR}/skills/"

echo "Done. Agents → ${OPENCODE_DIR}/agents/  |  Skills → ${OPENCODE_DIR}/skills/"
