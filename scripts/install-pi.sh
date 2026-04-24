#!/usr/bin/env bash
# Installs Pi global config from the repo into ~/.pi/agent/

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PI_DIR="${HOME}/.pi/agent"

echo "Installing Pi global config from: ${REPO_ROOT}"

mkdir -p "${PI_DIR}"

cp -v "${REPO_ROOT}/pi/global/AGENTS.md" "${PI_DIR}/AGENTS.md"

echo "Done. AGENTS.md → ${PI_DIR}/AGENTS.md"
echo ""
echo "Note: Copy pi/global/SYSTEM.md to your project root to customize the system prompt per-project."
