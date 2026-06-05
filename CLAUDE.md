# CLAUDE.md — ai-toolkit

See [AGENTS.md](AGENTS.md) for full project conventions, skill/agent structure, templates,
and persistent decisions.

---

## Quick Reference

- **Skills:** `skills/team/<n>/SKILL.md` or `skills/professional/<n>/SKILL.md` — subdir chosen by `audience:` frontmatter. 5-section lean layout (depth → `references/`), gold standard: `skills/team/cargo-package-scaffold/SKILL.md`
- **Agents:** `claude/agents/{team,professional}/<n>.md` (Claude Code) | `opencode/agents/{team,professional}/<n>.md` (OpenCode) — must stay in parity
- **Commands:** `claude/commands/<n>.md` (Claude Code) | `opencode/commands/<n>.md` (OpenCode) — flat, no audience subdir
- **Global files:** `claude/global/` → installs to `~/.claude/` | `opencode/global/` → installs to `~/.config/opencode/` | `pi/global/` → installs to `~/.pi/agent/`
- **Hooks:** `claude/global/settings.json` — credential stop (PreToolUse) + post-write build/lint gates (PostToolUse)
- **Permissions:** `claude/global/settings.local.json` — bash allow/deny arrays, read allow/deny arrays
- **Project templates:** `project-templates/` — copy into target project roots, do not edit globally

---

## Contributor Validation

No compiled artifacts. Validation is structural.

```bash
# Count skills
find skills -name "SKILL.md" | wc -l

# Verify a full-template skill has the 5 lean sections (in-fence template headers may push this higher)
grep -c "^## " skills/{team,professional}/<n>/SKILL.md

# Check agent parity (counts must match) — agents live under team/ and professional/ subdirs
find claude/agents -name "*.md" | wc -l
find opencode/agents -name "*.md" | wc -l

# Check command parity (counts must match) — commands are flat
ls claude/commands/*.md | wc -l
ls opencode/commands/*.md | wc -l
```

## When Adding a Skill

**Choose a tier first:**
- **Minimal** (≤ 100 lines): mode switches, conversational tools, single-instruction skills. No prescribed section structure. `≥ 1` reference file.
- **Full-template** (≤ 200 lines): domain-expert skills. 5-section lean layout. `≥ 2` reference files. Depth (principle tables, anti-patterns, discipline rules, error recovery, code/report templates) goes to `references/`, loaded just-in-time — not in SKILL.md.

Set `audience:` in the frontmatter (`team` | `professional`) — it selects the
`skills/<audience>/` install subdir, applied by `scripts/add_frontmatter.py`.

**Minimal-tier steps:**
1. Create `skills/<audience>/<new-name>/SKILL.md` with focused instructions (no template to copy)
2. Add `disable-model-invocation: true` for interactive or conversational skills
3. Create `skills/<audience>/<new-name>/references/` with ≥ 1 supporting file
4. Skip steps 3–6 below unless the skill is user-invocable

**Full-template steps:**
1. Copy gold standard: `cp -r skills/team/cargo-package-scaffold skills/<audience>/<new-name>`
2. 5-section lean layout — keep Core Philosophy/Workflow/State/Output Template/Integration in SKILL.md; push depth to `references/`; ≥ 2 reference files
3. Add agent entries in **both** `claude/agents/<audience>/` and `opencode/agents/<audience>/`
4. Add command entries in **both** `claude/commands/` and `opencode/commands/` if user-invocable
5. Update counts and tables: README.md badge + at-a-glance + structure comments; AGENTS.md Purpose line + Open Loops + Skill Suites table
6. Add a Green / Yellow / Red entry for the new skill in `pi/SKILLS-local.md`

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

Files in `claude/global/`, `opencode/global/`, and `pi/global/` affect **every project on the user's machine** after install.
Changes to any global file require explicit review before committing.
Do not batch-edit them alongside skill or agent changes.

**These files are public templates.** Do not embed specific book titles, personal document names, personal file paths, or user-specific tool references. Collection descriptions must describe topic domains only. Personal enrichment belongs in the installed copies (`~/.claude/CLAUDE.md`, `~/.config/opencode/AGENTS.md`, `~/.pi/agent/AGENTS.md`), not the repo source.
