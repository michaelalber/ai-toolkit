# PARA Archive Policy

Archiving is the one phase of review that writes. It must be safe, reversible, and confirmed.

## When to archive

| Source category | Archive when… | Keep when… |
|-----------------|---------------|------------|
| **Project** | Goal met, or abandoned, or stalled past threshold with no intent to resume | A clear next action still exists |
| **Area** | Responsibility no longer held; standard no longer maintained | Still accountable for it |
| **Resource** | Interest is dead; untouched past threshold (default 180 days) | Still actively referenced |

**Default to keep.** Archive only on a positive signal of completion/inactivity. When unsure, leave
the item active and flag it in the report rather than archiving speculatively.

## Where archived items go

Archive **preserves the original category** so items can be restored or found later:

```
<base>/Archive/
├── Projects/<project-name>/
├── Areas/<area-name>/
└── Resources/<topic>/
```

If a completed Project produced a discrete asset with lasting reference value, **copy** that asset
into `Resources/` before archiving the project (don't strand reusable reference material in the archive).

## Safety rules (non-negotiable)

1. **Never delete.** Archive = move to `Archive/`. Deletion is out of scope for this skill.
2. **Confirm bulk moves.** Present the full move-list; act only on confirmed rows.
3. **Reversible.** Write a move-log before moving so every archive can be undone.
4. **Confirm outward writes individually.** Re-labeling a Confluence page or transitioning a Jira
   issue is visible to others — confirm each, never batch silently.
5. **Idempotent destinations.** `mkdir -p` the archive subdir; never overwrite an existing archived
   item — suffix with a date if a name collides.

## Per-backend archive operation

| Backend | Archive action |
|---------|----------------|
| local / OneDrive / Teams | `mkdir -p <base>/Archive/<orig-category>/<group>` then `mv` the item; log the from→to paths |
| Confluence | Re-label the page from `para-project`/etc. to `para-archive` (and move under the archive parent if configured) via `mcp__denali-atlassian__confluence_update_page`; confirm individually |
| Jira | A "done" PARA Project maps to closing/transitioning its issues — propose the transition via `mcp__denali-atlassian__jira_get_transitions` + `jira_transition_issue`, but execute only on explicit confirmation |

## Move-log format

Append to a dated log (e.g. `<base>/Archive/_move-log.md`) before performing moves:

```markdown
## Review 2026-06-20
| Item | From | To | Backend | Reversible-by |
|------|------|----|---------|---------------|
| Q1 launch | Projects/Q1-launch/ | Archive/Projects/Q1-launch/ | local | mv back to Projects/ |
| Old SDK notes | Resources/sdk/ | Archive/Resources/sdk/ | local | mv back to Resources/ |
```

The `Reversible-by` column makes undo a mechanical operation, not a reconstruction.
