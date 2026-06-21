# PARA Backend Adapters

How each PARA operation maps onto a concrete backend. The category is decided once (by the
classification heuristics); the adapter only executes placement. Read `.para.yml` to learn which
backends are enabled and their roots/labels.

## Adapter selection

| Item origin / target | Adapter | Mechanism |
|----------------------|---------|-----------|
| Local file or note | **filesystem** | Move/create under `<local.base>/<category>/` |
| OneDrive document | **filesystem** (OneDrive sync path) | Move/create under `<onedrive.base>/<category>/` |
| Teams / SharePoint file | **filesystem** (Teams sync path) | Move/create under `<teams.base>/<category>/` |
| Knowledge-base page | **confluence** | Atlassian MCP — create/label page |
| Active goal-bearing work | **jira** | Atlassian MCP — associate with active project (Projects only) |

> **OneDrive & Teams have no API connector here.** Both are operated on as ordinary local folders
> via their synced paths. Microsoft Teams files live in a SharePoint document library that OneDrive
> syncs to disk; point `teams.base` at that synced folder. If the path is not present on disk, report
> "not synced" — never fabricate a remote location.

## Filesystem / OneDrive / Teams

Use the standard file tools (Read, Write) and `Bash(mkdir -p ...)`, `Bash(mv ...)`.

```
DESTINATION = <base>/<category_dir>/<group>/<filename>
  where <group> is the project name, area name, or resource topic (created if absent).
  Archive destinations nest by original category: <base>/Archive/<original-category>/<group>/.
```

- **Create** (new note): write the content + a small frontmatter header (title, tags, summary, filed-date).
- **Move** (existing file): `mkdir -p` the destination dir, then `mv`. Confirm before overwriting an
  existing file at the destination; never silently clobber.
- **Preserve the source** unless the user asked to move it. Default to *copy-then-report* for items
  outside a PARA base; *move* for items already inside the inbox.

## Confluence (Atlassian MCP)

Categories map to **labels within one space** (`confluence.space_key`), optionally under a per-category
parent page. Relevant MCP tools (load via ToolSearch when needed):

| Operation | Tool |
|-----------|------|
| Find existing page before creating | `mcp__denali-atlassian__confluence_search` |
| Create the page | `mcp__denali-atlassian__confluence_create_page` |
| Update an existing page | `mcp__denali-atlassian__confluence_update_page` |
| List spaces (verify space_key) | `mcp__denali-atlassian__confluence_list_spaces` |

Procedure: search for an existing page by title → if absent, create under the mapped parent → apply
the PARA label from `label_scheme` (plus the item's topic tags). Creating/labeling a page is an
outward-facing write — **confirm before the first one in a session.**

## Jira (Atlassian MCP)

Only PARA **Projects** map to Jira; Areas/Resources/Archives never do. A Jira project in
`jira.active_projects` *is* an active PARA Project.

| Operation | Tool |
|-----------|------|
| Confirm the project exists | `mcp__denali-atlassian__jira_list_projects` |
| Find a related issue | `mcp__denali-atlassian__jira_search` |
| Attach context as a comment | `mcp__denali-atlassian__jira_add_comment` |
| Create an issue (only if asked) | `mcp__denali-atlassian__jira_create_issue` |

Default behavior is to **associate** the filed item with the project (a comment or link), not to
create issues. Creating Jira issues is high-impact — do it only on explicit instruction.

## RECORD step (all backends)

After placement, append one row to the index note at `index.path`:

```markdown
| Date | Item | Category | Backend | Destination | Tags |
|------|------|----------|---------|-------------|------|
| 2026-06-20 | Q3 launch brief | Project | confluence | <url> | launch, marketing |
```

The index is the single authoritative record of what was filed where — one row per filing, never
duplicated content.
