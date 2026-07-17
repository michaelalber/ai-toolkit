#!/usr/bin/env bash
# PreToolUse / Bash — flag pipe-to-shell and find -exec shell chains.
# Exit 2 blocks the call; message must go to stderr to be seen.
set -uo pipefail

cmd=$(jq -r '.tool_input.command // empty' 2>/dev/null) || exit 0
[ -z "$cmd" ] && exit 0

CHAIN='(\|[[:space:]]*(bash|sh|zsh|python[23]?|node|perl|ruby)\b|-exec[ir]?[[:space:]]+(bash|sh|zsh|python[23]?|node|perl|ruby)\b)'

if printf '%s' "$cmd" | grep -qE "$CHAIN"; then
  echo "SHELL EXEC CHAIN DETECTED (pipe-to-shell or find -exec shell) - review before proceeding" >&2
  exit 2
fi
exit 0
