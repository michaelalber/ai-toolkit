#!/usr/bin/env bash
# Installs the shared skills tree from the repo into ~/.agents/skills/
#
# Usage:
#   bash scripts/install-agents.sh
#
# Skills are a single source of truth in skills/ (identical Agent Skills format
# across Claude Code, OpenCode, and Pi). skills/ is flat -- this copies the whole
# tree, preserving the skills/<name>/SKILL.md layout that skill discovery walks.
#
# ~/.agents/skills/ is the one shared install: Pi, Goose, and Open WebUI all read
# it. Pi also reads ~/.pi/agent/skills/, so install-pi.sh calls this script
# instead of keeping a second copy there.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
AGENTS_DIR="${HOME}/.agents"
SKILLS_DIR="${AGENTS_DIR}/skills"
MANIFEST="${SKILLS_DIR}/.ai-toolkit-installed"

echo "Installing skills from: ${REPO_ROOT}"

mkdir -p "${SKILLS_DIR}"

# <AI-Generated START>
# Full resync. cp -r never deletes, so remove (a) every skill the repo ships
# now and (b) every skill the last run installed, per the manifest -- (b) is
# what drops a skill that was deleted from the repo. Skills you added by hand
# are in neither list and are left untouched.
if [[ -f "${MANIFEST}" ]]; then
  while IFS= read -r name; do
    [[ -n "${name}" && "${name}" != */* && "${name}" != .* ]] && rm -rf "${SKILLS_DIR:?}/${name}"
  done < "${MANIFEST}"
fi
for d in "${REPO_ROOT}/skills/"*/; do rm -rf "${SKILLS_DIR:?}/$(basename "$d")"; done
cp -r "${REPO_ROOT}/skills/"* "${SKILLS_DIR}/"
for d in "${REPO_ROOT}/skills/"*/; do basename "$d"; done > "${MANIFEST}"
# <AI-Generated END>

echo ""
echo "Done."
echo "  Skills → ${SKILLS_DIR}/ ($(wc -l < "${MANIFEST}") installed)"
