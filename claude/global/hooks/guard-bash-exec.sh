#!/usr/bin/env bash
# PreToolUse / Bash — flag pipe-to-shell and find -exec shell chains.
# Exit 2 blocks the call; message must go to stderr to be seen.
set -uo pipefail

cmd=$(jq -r '.tool_input.command // empty' 2>/dev/null) || exit 0
[ -z "$cmd" ] && exit 0

CHAIN='(\|[[:space:]]*(bash|sh|zsh|python[23]?|node|perl|ruby)\b|-exec[ir]?[[:space:]]+(bash|sh|zsh|python[23]?|node|perl|ruby)\b)'

# Scan with quoted spans removed. The pattern is matched against raw text, so a
# SEARCH STRING that merely contains a pipe followed by a shell name — a grep
# pattern, a sed s|…|…| substitution, documentation about this very hook — is
# otherwise indistinguishable from a real exec chain. Quoted text cannot be a
# command position, so stripping it removes that entire false-positive class.
# Not airtight (nested quoting, heredocs): a real chain must be unquoted to run,
# and unquoted chains still match.
scan=$(printf '%s' "$cmd" | sed "s/'[^']*'//g; s/\"[^\"]*\"//g")

if printf '%s' "$scan" | grep -qE "$CHAIN"; then
  echo "SHELL EXEC CHAIN DETECTED (pipe-to-shell or find -exec shell) - review before proceeding" >&2
  exit 2
fi
exit 0
