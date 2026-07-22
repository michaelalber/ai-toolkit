#!/usr/bin/env bash
# Installs Claude agents and skills from the repo into ~/.claude/

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLAUDE_DIR="${HOME}/.claude"

echo "Installing Claude agents and skills from: ${REPO_ROOT}"

mkdir -p "${CLAUDE_DIR}/agents"
mkdir -p "${CLAUDE_DIR}/skills"
mkdir -p "${CLAUDE_DIR}/commands"

find "${REPO_ROOT}/claude/agents" -name "*.md" -exec cp -v {} "${CLAUDE_DIR}/agents/" \;
# Full resync of the repo-owned subtrees: cp -r overwrites and adds but never
# deletes, so a skill removed from the repo would linger here and stay
# invocable. Only team/ and professional/ are repo-owned — anything else you
# added by hand under skills/ is left untouched.
rm -rf "${CLAUDE_DIR}/skills/team" "${CLAUDE_DIR}/skills/professional"
cp -rv "${REPO_ROOT}/skills/"* "${CLAUDE_DIR}/skills/"
find "${REPO_ROOT}/claude/commands" -name "*.md" -exec cp -v {} "${CLAUDE_DIR}/commands/" \;
cp -v "${REPO_ROOT}/claude/global/statusline.sh" "${CLAUDE_DIR}/statusline.sh"
chmod +x "${CLAUDE_DIR}/statusline.sh"

echo "Done."
echo "  Agents      → ${CLAUDE_DIR}/agents/"
echo "  Skills      → ${CLAUDE_DIR}/skills/"
echo "  Commands    → ${CLAUDE_DIR}/commands/"
echo "  Status line → ${CLAUDE_DIR}/statusline.sh"
echo ""
echo "Global config (manual — edit YOUR_USERNAME first):"
echo "  cp ${REPO_ROOT}/claude/global/CLAUDE.md ~/.claude/CLAUDE.md"
echo "  cp ${REPO_ROOT}/claude/global/settings.json ~/.claude/settings.json"
echo "  cp ${REPO_ROOT}/claude/global/settings.local.json ~/.claude/settings.local.json"
