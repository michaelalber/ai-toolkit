#!/bin/bash
# Claude Code status line — displays token count and context window usage.
# Claude Code pipes a JSON blob to stdin on every render cycle.
# Output: e.g.  57.5k (6.0%)  in yellow; blank until the first API call.

YELLOW='\033[0;33m'
NC='\033[0m'

input=$(cat)

used_pct=$(echo "$input" | jq -r '.context_window.used_percentage // empty')
ctx_size=$(echo "$input" | jq -r '.context_window.context_window_size // 200000')

# Nothing to show until the first API round-trip
if [[ -z "$used_pct" ]]; then
  exit 0
fi

# Derive token count from percentage × context window size
tokens_k=$(awk "BEGIN { printf \"%.1fk\", ($used_pct / 100 * $ctx_size) / 1000 }")
pct_fmt=$(printf "%.1f%%" "$used_pct")

printf "${YELLOW}%s (%s)${NC}\n" "$tokens_k" "$pct_fmt"
