#!/usr/bin/env bash
# Installs OpenCode agents and skills from the repo into ~/.config/opencode/

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OPENCODE_DIR="${HOME}/.config/opencode"

echo "Installing OpenCode agents and skills from: ${REPO_ROOT}"

mkdir -p "${OPENCODE_DIR}/agents"
mkdir -p "${OPENCODE_DIR}/skills"
mkdir -p "${OPENCODE_DIR}/commands"

# Agents and commands are copied flat, so the same prune applies: without it a
# removed agent lingers and stays spawnable. These two dirs are wholly repo-owned.
rm -f "${OPENCODE_DIR}/agents/"*.md "${OPENCODE_DIR}/commands/"*.md
find "${REPO_ROOT}/opencode/agents" -name "*.md" -exec cp -v {} "${OPENCODE_DIR}/agents/" \;
# Full resync of the repo-owned skills. cp -r overwrites and adds but never
# deletes, so a skill removed from the repo would linger here and stay
# invocable. Prune by what the repo currently ships -- skills/ is flat, so the
# old `rm -rf team professional` no longer matches anything. Skills you added
# by hand under skills/ are not in the repo listing, so they are left untouched.
for d in "${REPO_ROOT}/skills/"*/; do rm -rf "${OPENCODE_DIR}/skills/$(basename "$d")"; done
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
