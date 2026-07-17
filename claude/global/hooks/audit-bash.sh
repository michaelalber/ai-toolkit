#!/usr/bin/env bash
# PostToolUse / Bash — append every executed command to an audit log.
set -uo pipefail

cmd=$(jq -r '.tool_input.command // empty' 2>/dev/null) || exit 0
[ -z "$cmd" ] && exit 0

ts=$(date -u '+%Y-%m-%dT%H:%M:%SZ')
log_dir="$HOME/.claude/logs"
mkdir -p "$log_dir" || exit 0
printf '[%s] %s\n' "$ts" "$cmd" >> "$log_dir/bash-audit.log"
exit 0
