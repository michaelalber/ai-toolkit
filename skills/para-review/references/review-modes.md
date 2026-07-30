# PARA Review Modes

Three composable modes. `full` runs audit → ritual → summarize in sequence. Each reads `.para.yml`
to know which backends and roots are in scope. PARA is Tiago Forte's methodology
(fortelabs.com/blog/para); these procedures encode canonical practice, not an engineering standard.

## Mode: audit — hygiene checklist

Read-only. Produce a findings table; propose moves; change nothing until ARCHIVE.

| # | Check | Signal | Suggested action |
|---|-------|--------|------------------|
| 1 | **Misfiled by topic** | Item grouped by subject rather than actionability | Reclassify via the P→A→R→Archive order |
| 2 | **Stale Project** | No activity in N days (default 30) or past its goal/deadline | Confirm done → Archive; or revive with a next action |
| 3 | **Completed Project still in Projects** | Goal met but not archived | Archive (assets with lasting value → copy to Resources) |
| 4 | **Archivable Resource** | Topic untouched long-term / no living interest | Archive under Archive/Resources |
| 5 | **Empty / orphaned Area** | Area with no items or no maintained standard | Merge, drop to Resource, or Archive |
| 6 | **Project that is really an Area** | "Project" with no end / deadline | Reclassify to Area |
| 7 | **Area that is really a Resource** | No accountability, only interest | Reclassify to Resource |
| 8 | **Duplicated content** | Same content under ≥2 categories | Keep one authoritative copy; link the rest |
| 9 | **Inbox backlog** | Unfiled items in 00-Inbox | Route to ritual step 1 |

Severity: **High** = data-loss or wrong-place that blocks work (3, 8); **Medium** = drift that
degrades the system (1, 2, 5, 6, 7); **Low** = tidy-ups (4, 9). Report in this order.

Thresholds (`N days`) default to 30 for Projects, 180 for Resources; honor overrides if the user
states them. State the threshold used in the report.

## Mode: ritual — the weekly review

Interactive, one pass. Goal: return the system to a known-good state and surface the week's focus.

```
1. PROCESS THE INBOX TO ZERO
   For each item in every enabled inbox: classify (P/A/R/Archive) and hand to para-file, or
   defer with an explicit reason. End with an empty inbox or an explicit deferred list.

2. REVIEW ACTIVE PROJECTS
   For each Project: is it still active? does it have a clear next action? is the goal still valid?
   Mark: on-track | needs-next-action | stalled→archive-candidate | done→archive.

3. SCAN AREAS FOR DROPPED STANDARDS
   For each Area: is the standard being maintained? Surface any that have slipped.

4. SURFACE ATTENTION
   List what needs the user this week: stalled projects, slipped areas, decisions waiting,
   deadlines approaching. This is the ritual's primary output.
```

The ritual proposes; it does not bulk-move. Archiving from steps 2/3 flows into the ARCHIVE phase
with confirmation.

## Mode: summarize — change digest

For documents created or modified since the last review (use file mtime locally; `version`/updated
date on Confluence). For each:

- 1–3 sentence summary of what it is and why it matters.
- 2–5 topic tags.
- A placement note: does its current category still fit? (feeds the audit move-list).

Skip unchanged items. **Never** write document contents into the digest for items flagged sensitive
or containing PII — record a neutral title only. The digest is reference output, not a backend write.
