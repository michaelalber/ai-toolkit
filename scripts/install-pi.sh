#!/usr/bin/env bash
# Installs Pi global config from the repo into ~/.pi/agent/
#
# Usage:
#   bash scripts/install-pi.sh          # installs AGENTS-lite.md (7B-safe default)
#   bash scripts/install-pi.sh --full   # installs AGENTS.md (20B models)

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PI_DIR="${HOME}/.pi/agent"
USE_FULL=false

for arg in "$@"; do
  if [[ "$arg" == "--full" ]]; then
    USE_FULL=true
  fi
done

echo "Installing Pi global config from: ${REPO_ROOT}"

mkdir -p "${PI_DIR}"

if [[ "${USE_FULL}" == true ]]; then
  cp -v "${REPO_ROOT}/pi/global/AGENTS.md" "${PI_DIR}/AGENTS.md"
  echo "Installed: AGENTS.md (20B variant)"
else
  cp -v "${REPO_ROOT}/pi/global/AGENTS-lite.md" "${PI_DIR}/AGENTS.md"
  echo "Installed: AGENTS-lite.md as AGENTS.md (7B-safe default)"
  echo "  Run with --full to install the 20B variant instead."
fi

cp -v "${REPO_ROOT}/pi/global/models.json" "${PI_DIR}/models.json"
cp -v "${REPO_ROOT}/pi/global/settings.json" "${PI_DIR}/settings.json"

echo ""
echo "Done."
echo "  AGENTS.md  → ${PI_DIR}/AGENTS.md"
echo "  models.json → ${PI_DIR}/models.json"
echo "  settings.json → ${PI_DIR}/settings.json"
echo ""
echo "Next steps:"
echo "  1. Edit ${PI_DIR}/models.json — uncomment the models you have pulled."
echo "  2. Create your Ollama model: ollama create my-coder -f pi/global/Modelfile-7b"
echo "  3. Copy pi/global/SYSTEM.md to your project root and trim to one variant."
echo "  4. Run: pi --model ollama/my-coder"
