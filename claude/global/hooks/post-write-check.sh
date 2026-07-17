#!/usr/bin/env bash
# PostToolUse / Write|Edit — dispatch a per-language check on the written file.
# Matchers only see the tool NAME, so the extension is filtered here.
# PostToolUse cannot block; output is advisory feedback on stderr.
#
# Scoping: .NET checks run ONLY against the project that owns the written file,
# found by walking up to the nearest .csproj. A bare `dotnet build` would build
# whatever cwd happened to be, which need not relate to the file at all.
set -uo pipefail

BUILD_TIMEOUT=120

file=$(jq -r '.tool_input.file_path // empty' 2>/dev/null) || exit 0
[ -z "$file" ] && exit 0
[ -f "$file" ] || exit 0

# Walk up from $1 looking for a file matching glob $2. Stops at $HOME or / so a
# stray source file outside any project never triggers a build.
find_up() {
  local dir="$1" pattern="$2" hit
  while [ -n "$dir" ] && [ "$dir" != "/" ] && [ "$dir" != "$HOME" ]; do
    hit=$(find "$dir" -maxdepth 1 -name "$pattern" -type f 2>/dev/null | head -1)
    if [ -n "$hit" ]; then printf '%s' "$hit"; return 0; fi
    dir=$(dirname "$dir")
  done
  return 1
}

resolve_dotnet() {
  if command -v dotnet >/dev/null 2>&1; then printf 'dotnet'; return 0; fi
  if [ -x "$HOME/.dotnet/dotnet" ]; then printf '%s' "$HOME/.dotnet/dotnet"; return 0; fi
  return 1
}

run_capped() { # cap runtime so a hook can never hang the session
  if command -v timeout >/dev/null 2>&1; then timeout "$BUILD_TIMEOUT" "$@"; else "$@"; fi
}

case "$file" in
  *.cs)
    proj=$(find_up "$(dirname "$file")" '*.csproj') || exit 0
    dn=$(resolve_dotnet) || exit 0
    run_capped "$dn" build "$proj" --no-restore --nologo 2>&1 | tail -15 >&2
    ;;
  *.csproj)
    dn=$(resolve_dotnet) || exit 0
    run_capped "$dn" restore "$file" 2>&1 | tail -10 >&2
    ;;
  *.py)
    if command -v ruff >/dev/null 2>&1; then
      ruff check "$file" 2>&1 | head -20 >&2
    elif command -v uvx >/dev/null 2>&1; then
      uvx ruff check "$file" 2>&1 | head -20 >&2
    fi
    ;;
esac
exit 0
