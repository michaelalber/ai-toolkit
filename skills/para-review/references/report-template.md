# PARA Review Report Template

Emitted at the REPORT phase. Adapt sections to the mode(s) that ran (`audit`, `ritual`,
`summarize`, or `full`). Keep it scannable — the user should see what needs them in the first screen.

```markdown
# PARA Review — {date}

**Mode:** {audit | ritual | summarize | full}
**Backends scanned:** {local, onedrive, teams, confluence, jira}
**Thresholds:** stale Project > {N} days · inactive Resource > {M} days

## Inventory
| Category | Local | OneDrive | Teams | Confluence | Jira |
|----------|-------|----------|-------|------------|------|
| Projects |  |  |  |  |  |
| Areas    |  |  |  |  | — |
| Resources|  |  |  |  | — |
| Archive  |  |  |  |  | — |
| Inbox    |  |  |  | — | — |

## Needs your attention  ⚠ (lead with this)
- {stalled project / slipped area / approaching deadline / decision waiting}

## Findings (by severity)
### High
| Item | Issue | Proposed action |
|------|-------|-----------------|
### Medium
| Item | Issue | Proposed action |
|------|-------|-----------------|
### Low
| Item | Issue | Proposed action |
|------|-------|-----------------|

## Weekly ritual  (ritual / full only)
- **Inbox:** {processed N → 0 | M deferred (reasons)}
- **Projects:** {on-track / needs-next-action / archive-candidate counts}
- **Areas:** {standards maintained / slipped}

## Change digest  (summarize / full only)
| Document | Summary | Tags | Placement OK? |
|----------|---------|------|---------------|

## Archived this review
| Item | From | To | Backend |
|------|------|----|---------|
_Move log: {path}. Every move is reversible (see `Reversible-by`)._

## Confirmations still needed
- {outward-facing Confluence/Jira changes awaiting individual confirmation}
```

## Reporting rules

- **Lead with "Needs your attention."** The point of review is to redirect focus; bury nothing the
  user must act on.
- **Findings are proposals, not done deeds** — until ARCHIVE runs on confirmed rows, the column is
  "Proposed action".
- **Cite counts and thresholds** so the review is reproducible and the user can tune them.
- **Separate "archived" (done) from "confirmations needed" (pending)** so the user never assumes an
  outward change happened when it is still waiting on them.
