---
name: para-file
audience: team
description: >
  Captures and files an incoming document into the PARA system (Projects, Areas, Resources, Archives)
  across local folders, OneDrive/Teams synced paths, and Confluence/Jira — scaffolding the PARA
  structure if missing and classifying by actionability. Use when filing a new note, document, link,
  or downloaded file; when sorting an inbox; or when asked "where does this go" / "file this".
  Do NOT use for periodic review, auditing, or archiving completed work — use para-review instead.
---

# PARA File

> "Organize by actionability, not by subject. The right question is not *what is this about?*
> but *which project will this move forward?*" — adapted from Tiago Forte, fortelabs.com/blog/para

## Core Philosophy

PARA sorts every piece of information into exactly four categories that exist identically on every
platform: **Projects** (short-term efforts with a goal and an end), **Areas** (ongoing
responsibilities with a standard to maintain, no end date), **Resources** (topics of ongoing
interest / reference), and **Archives** (inactive items from the other three). The discipline that
makes PARA work is sorting by *actionability*, not topic — a document about "marketing" is not
filed under a "Marketing" folder; it is filed wherever it is most actionable right now.

This skill files one item at a time. It is deliberately fast — the cost of a slightly-wrong filing
is near zero because items move freely between categories as their status changes, and `para-review`
catches drift later. Bias toward placing the item and moving on, not toward a perfect taxonomy.

**Non-Negotiable Constraints:**
1. ACTIONABILITY ORDER — evaluate Projects → Areas → Resources → Archives, in that order, and file
   at the first match. The most actionable home wins. (Decision tree in `references/classification-heuristics.md`.)
2. FOUR CATEGORIES ONLY — never invent a fifth top-level bucket. Sub-structure lives *inside* P/A/R.
3. NEVER DESTROY — filing only creates or moves; it never deletes. Overwrites require explicit confirmation.
4. CONFIG-DRIVEN — read `.para.yml` for every root, label, and backend. If absent, scaffold and write it.
5. CONFIRM CROSS-BACKEND — publishing to Confluence/Jira is outward-facing; confirm before the first write in a session.

The full category criteria, edge cases, and anti-patterns live in `references/classification-heuristics.md`.

## Workflow

```
DETECT      Read .para.yml (project root). Resolve local roots, OneDrive/Teams synced paths,
            Confluence space + label scheme, Jira active-project keys. If config is missing OR a
            declared local root has no Projects/Areas/Resources/Archive tree → SCAFFOLD.
            No files moved yet. (Schema: references/config-schema.md.)

SCAFFOLD    (only if missing) Create the four roots + an inbox under each declared local/OneDrive
            base; write a starter .para.yml. Confluence/Jira are mapped, never auto-created — report
            the label/space scheme for the user to confirm. Idempotent: never clobber an existing tree.

CLASSIFY    Apply the actionability decision tree to the item. Output: category (P/A/R/Archive),
            target location (folder | Confluence parent | Jira project), and a one-line rationale.
            If ambiguous between two categories, state both and pick the more actionable; do not stall.

SUMMARIZE   Produce a 1–3 sentence summary + 2–5 topic tags for the item, to aid retrieval and to
            confirm the classification. Skip only for items the user marks trivial.

FILE        Execute via the matching backend adapter (references/backend-adapters.md):
              local / OneDrive / Teams → move-or-create file into <root>/<category>/...
              Confluence              → create/label page under the mapped space
              Jira                    → tag/associate with the active project (Projects only)
            Capture the result path/URL. Never delete the source without confirmation.

RECORD      Append the filing (item, category, destination, tags, summary) to the PARA index note
            and emit the result. Update .para.yml only if a new root/label was introduced.
```

**Exit criteria:** item placed in exactly one category via the correct backend; summary + tags
recorded; destination path/URL reported; no source destroyed; `.para.yml` consistent.

## State Block

```
<para-file-state>
phase: DETECT | SCAFFOLD | CLASSIFY | SUMMARIZE | FILE | RECORD | COMPLETE
config_found: true | false
scaffolded: true | false | n/a
item: [name or description]
backend: local | onedrive | teams | confluence | jira
category: project | area | resource | archive | undecided
destination: [path or URL]
tags: [comma-separated]
source_preserved: true | false
last_action: [description]
next_action: [description]
</para-file-state>
```

## Output Template

- **`.para.yml` schema + scaffolding layout** — `references/config-schema.md`.
- **Category criteria, actionability decision tree, edge cases, anti-patterns** — `references/classification-heuristics.md`.
- **Per-backend file/move/label operations (filesystem, OneDrive/Teams, Confluence + Jira via Atlassian MCP)** — `references/backend-adapters.md`.

## Integration with Other Skills

| Skill | Relationship |
|-------|-------------|
| `para-review` | Run periodically after filing — audits structure, runs the weekly ritual, and archives completed items. |
| `confluence-guide-writer` | Use when a filed Confluence page should be expanded into a full user guide. |
| `jira-comment-writer` | Use when filing relates to an active Jira project and needs a structured comment. |
| `research-synthesis` | Use when a filed Resource warrants deeper multi-source research before filing. |
