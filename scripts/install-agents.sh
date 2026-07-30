#!/usr/bin/env bash
# Installs the shared skills tree from the repo into ~/.agents/skills/
#
# Usage:
#   bash scripts/install-agents.sh
#
# Skills are a single source of truth in skills/ (identical Agent Skills format
# across Claude Code, OpenCode, and Pi). This copies both the team/ and
# professional/ subtrees, preserving the skills/<audience>/<name>/SKILL.md layout
# that skill discovery walks recursively.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
AGENTS_DIR="${HOME}/.agents"
SKILLS_DIR="${AGENTS_DIR}/skills"

echo "Installing skills from: ${REPO_ROOT}"

mkdir -p "${SKILLS_DIR}"

# Full resync of the repo-owned skills. cp -r overwrites and adds but never
# deletes, so a skill removed from the repo would linger here and stay
# invocable. Prune by what the repo currently ships -- skills/ is flat, so the
# old `rm -rf team professional` no longer matches anything. Skills you added
# by hand under skills/ are not in the repo listing, so they are left untouched.
for d in "${REPO_ROOT}/skills/"*/; do rm -rf "${SKILLS_DIR}/$(basename "$d")"; done
cp -rv "${REPO_ROOT}/skills/"* "${SKILLS_DIR}/"

echo ""
echo "Done."
echo "  Skills → ${SKILLS_DIR}/"
