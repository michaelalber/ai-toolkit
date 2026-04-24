# CLAUDE.md — ai-toolkit

See [AGENTS.md](AGENTS.md) for full project conventions, skill/agent structure, templates,
and persistent decisions.

---

## Quick Reference

- **Skills:** `skills/<n>/SKILL.md` — 10 mandatory sections, gold standard: `skills/architecture-review/SKILL.md`
- **Agents:** `claude/agents/<n>.md` (Claude Code) | `opencode/agents/<n>.md` (OpenCode) — must stay in parity
- **Commands:** `claude/commands/<n>.md` (Claude Code) | `opencode/commands/<n>.md` (OpenCode)
- **Global files:** `claude/global/` → installs to `~/.claude/` | `opencode/global/` → installs to `~/.config/opencode/`
- **Hooks:** `claude/global/settings.json` — credential stop (PreToolUse) + post-write build/lint gates (PostToolUse)
- **Permissions:** `claude/global/settings.local.json` — bash allow/deny arrays, read allow/deny arrays
- **Project templates:** `project-templates/` — copy into target project roots, do not edit globally

---

## Contributor Validation

No compiled artifacts. Validation is structural.

```bash
# Count skills
find skills -name "SKILL.md" | wc -l

# Verify a skill has all 10 sections
grep -c "^## " skills/<n>/SKILL.md   # should return 10

# Check agent parity (counts must match)
ls claude/agents/*.md | wc -l
ls opencode/agents/*.md | wc -l

# Check command parity (counts must match)
ls claude/commands/*.md | wc -l
ls opencode/commands/*.md | wc -l
```

## When Adding a Skill

1. Copy gold standard: `cp -r skills/architecture-review skills/<new-name>`
2. All 10 sections required — do not skip
3. Add agent entries in **both** `claude/agents/` and `opencode/agents/`
4. Add command entries in **both** `claude/commands/` and `opencode/commands/` if user-invocable
5. Update README.md skill count and table
6. Update AGENTS.md Open Loops section

## When Adding a Command

Commands are user-invoked (typed as `/command-name`). Use `!` shell injection to give Claude
live state before it acts. Skills are model-invoked — different primitive, different directory.

**Claude Code format:**
```markdown
---
description: What it does. Trigger phrase for slash-command discovery.
allowed-tools: Bash(dotnet test:*), Read, Edit
---

<live_state>
!`command that captures current state`
</live_state>

Instruction using the injected state above.
```

**OpenCode additions** — `agent:`, `subtask:`, optional `model:`:
```markdown
---
description: What it does.
agent: build
subtask: true
---
```

Use `subtask: true` for read-heavy commands (review, research, context-prime).
Use `subtask: false` for commands that write files (new-feature, migrate) — they need primary context.

## Hook Enforcement (settings.json)

`claude/global/settings.json` installs deterministic hooks that run outside the LLM:

| Hook | Trigger | Action |
|------|---------|--------|
| PreToolUse | Any Write | Credential pattern scan — exit 2 blocks the write |
| PostToolUse | Write(*.cs) | `dotnet build --no-restore` — surfaces compile errors immediately |
| PostToolUse | Write(*.py) | `ruff check` — surfaces lint errors immediately |
| PostToolUse | Write(*.csproj) | `dotnet restore` — keeps package state current |

These run regardless of model instruction. Exit code 2 blocks the tool call. Cannot be bypassed by prompt injection.

## Global File Caution

Files in `claude/global/` and `opencode/global/` affect **every project on the user's machine** after install.
Changes to global files require explicit review before committing.
Do not batch-edit them alongside skill or agent changes.
