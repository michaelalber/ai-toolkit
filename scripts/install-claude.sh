#!/usr/bin/env bash
# Installs Claude agents and skills from the repo into the active Claude profile.
#
# Target defaults to ~/.claude and follows CLAUDE_CONFIG_DIR when set — the same
# variable Claude Code itself uses to pick a profile. To deploy a second profile:
#   CLAUDE_CONFIG_DIR=~/.claude-denali scripts/install-claude.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLAUDE_DIR="${CLAUDE_CONFIG_DIR:-${HOME}/.claude}"

echo "Installing Claude agents and skills from: ${REPO_ROOT}"
echo "                                    into: ${CLAUDE_DIR}"

mkdir -p "${CLAUDE_DIR}/agents"
mkdir -p "${CLAUDE_DIR}/skills"
mkdir -p "${CLAUDE_DIR}/commands"

# Agents and commands are copied flat, so the same prune applies: without it a
# removed agent lingers and stays spawnable. These two dirs are wholly repo-owned.
rm -f "${CLAUDE_DIR}/agents/"*.md "${CLAUDE_DIR}/commands/"*.md
find "${REPO_ROOT}/claude/agents" -name "*.md" -exec cp -v {} "${CLAUDE_DIR}/agents/" \;
# Full resync of the repo-owned skills. cp -r overwrites and adds but never
# deletes, so a skill removed from the repo would linger here and stay
# invocable. Prune by what the repo currently ships -- skills/ is flat, so the
# old `rm -rf team professional` no longer matches anything. Skills you added
# by hand under skills/ are not in the repo listing, so they are left untouched.
for d in "${REPO_ROOT}/skills/"*/; do rm -rf "${CLAUDE_DIR}/skills/$(basename "$d")"; done
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
