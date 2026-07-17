#!/usr/bin/env bash
# PreToolUse / Write|Edit|NotebookEdit — block writing credential-shaped literals.
# Scans the CONTENT BEING WRITTEN (every string in tool_input), not the file on
# disk, so it catches the new secret rather than a pre-existing one.
set -uo pipefail

payload=$(jq -r '[.tool_input | .. | strings] | join("\n")' 2>/dev/null) || exit 0
[ -z "$payload" ] && exit 0

PATTERN='(password|passwd|secret|api[-_.]?key|token|connectionstring|bearer|private[-_.]?key)[[:space:]]*[=:][[:space:]]*["'\''`][^"'\''`]{6,}'

if printf '%s' "$payload" | grep -qiE "$PATTERN"; then
  echo "CREDENTIAL PATTERN DETECTED in content being written - review before proceeding" >&2
  exit 2
fi
exit 0
