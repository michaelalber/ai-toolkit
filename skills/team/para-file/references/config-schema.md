# `.para.yml` — PARA Configuration Schema

A per-project file at the project root. It declares every PARA root, the OneDrive/Teams synced
paths, the Confluence space + label scheme, and the Jira active-project keys. Both `para-file` and
`para-review` read it; `para-file` writes/scaffolds it when absent.

## Schema

```yaml
# .para.yml — PARA system configuration
version: 1

# Local filesystem roots. Each base contains Projects/ Areas/ Resources/ Archive/ + an inbox.
local:
  base: ~/PARA                 # required if local is used
  inbox: ~/PARA/00-Inbox       # default: <base>/00-Inbox
  category_dirs:               # override folder names if desired
    projects: Projects
    areas: Areas
    resources: Resources
    archive: Archive

# OneDrive and Microsoft Teams files. NO MCP exists for these — they are operated on via their
# LOCALLY-SYNCED folder paths. Teams files are OneDrive/SharePoint-backed and appear under the
# OneDrive sync folder on disk. Treat each as an additional filesystem root.
onedrive:
  enabled: false
  base: ~/OneDrive/PARA
  inbox: ~/OneDrive/PARA/00-Inbox
teams:
  enabled: false
  base: ~/OneDrive - <Org>/Teams/PARA   # adjust to your synced Teams library path

# Confluence — via the Atlassian MCP. PARA categories map to labels within one space.
confluence:
  enabled: false
  space_key: PARA
  parent_pages:                # optional: a parent page per category for hierarchy
    projects: null
    areas: null
    resources: null
    archive: null
  label_scheme:                # PARA category -> Confluence label
    projects: para-project
    areas: para-area
    resources: para-resource
    archive: para-archive

# Jira — via the Atlassian MCP. Only PARA *Projects* map to Jira. Active Jira projects ARE
# active PARA Projects; their issues are the project's actionable work.
jira:
  enabled: false
  active_projects: []          # e.g. [ABC, XYZ]

# Where the filing index/log note lives (one authoritative record of what was filed).
index:
  path: ~/PARA/PARA-Index.md
```

## Rules

- **Minimum viable config:** `local.base` alone is enough; everything else defaults off.
- **`enabled: false`** on a backend means `para-file`/`para-review` skip it entirely.
- **Never store secrets here.** Atlassian auth is handled by the MCP, not this file.
- **Paths use `~`** for the home directory; expand at read time.
- A backend declared but unreachable (e.g. OneDrive path not synced) is **reported, not invented** —
  the skill surfaces the gap rather than guessing a location.

## Scaffolding layout (created when missing)

For each enabled local/OneDrive/Teams base:

```
<base>/
├── 00-Inbox/          # capture point for unfiled items
├── Projects/          # active, goal-bearing efforts
├── Areas/             # ongoing responsibilities
├── Resources/         # topics of interest / reference
└── Archive/           # inactive items, sub-grouped by original category
    ├── Projects/
    ├── Areas/
    └── Resources/
```

Scaffolding is **idempotent** — existing directories and files are never clobbered. Confluence and
Jira are mapped (labels/space/keys), never auto-created; the skill reports the intended scheme for
the user to confirm before the first outward write.
