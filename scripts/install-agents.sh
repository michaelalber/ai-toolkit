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
cp -rv "${REPO_ROOT}/skills/"* "${SKILLS_DIR}/"

echo ""
echo "Done."
echo "  Skills → ${SKILLS_DIR}/"
