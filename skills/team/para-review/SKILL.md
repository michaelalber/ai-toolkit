---
name: para-review
audience: team
description: >
  Runs a periodic PARA review across local folders, OneDrive/Teams synced paths, and Confluence/Jira:
  a hygiene audit (misfiled items, stale Projects, archivable Resources, empty Areas), the weekly
  review ritual (process inbox, update project list, surface what needs attention), document
  summarization, and safe archiving of completed/inactive items. Use for "weekly review", "PARA
  audit", "clean up my files", or "archive finished projects". Do NOT use to file a single new
  document — use para-file instead.
---

# PARA Review

> "Your system stays useful only if you tend it. Review converts a pile into a garden —
> completed projects move to the archive, and attention returns to what is alive." — adapted from
> Tiago Forte, fortelabs.com/blog/para

## Core Philosophy

A PARA system degrades without maintenance: finished projects linger in Projects, the inbox fills,
Resources accumulate that no longer match any living interest, and items drift into the wrong
category. This skill is the counterweight. It runs in three composable modes — **audit** (find
drift), **ritual** (the weekly review), and **summarize** (digest new/changed material) — and ends
with **safe archiving** of what is demonstrably done or inactive.

Review is read-mostly and proposal-first. It surfaces findings and a proposed move-list, then acts
only on what the user (or the ritual's rules) confirms. The bias is the inverse of `para-file`:
filing is fast and forgiving; review is careful, because archiving and bulk moves touch many items
at once and must never lose data.

**Non-Negotiable Constraints:**
1. PROPOSE BEFORE MOVING — every audit/archive action is presented as a reviewable list first; bulk
   moves require confirmation. No silent reorganization.
2. ARCHIVE, NEVER DELETE — completed/inactive items move to Archive (preserving original category);
   deletion is never performed by this skill.
3. ACTIONABILITY IS THE RULER — judge placement by the same P→A→R→Archive actionability order
   `para-file` uses; flag mismatches, don't impose new taxonomies.
4. CONFIG-DRIVEN, READ-ONLY FIRST — load `.para.yml`; the DETECT/AUDIT passes only read. Writes
   happen only in ARCHIVE, after confirmation.
5. REVERSIBLE — record every move so it can be undone; outward-facing (Confluence/Jira) changes are
   confirmed individually.

The full audit checklist, weekly-ritual steps, and per-backend archive procedure live in `references/`.

## Workflow

```
DETECT      Load .para.yml. Resolve enabled backends + roots. Read-only inventory: count items per
            category per backend, list inbox contents, note last-modified ages. No writes.

AUDIT       (mode: audit) Scan for drift against references/review-modes.md checklist:
              · misfiled items (topic-filed, wrong actionability category)
              · stale Projects (no activity in N days, or past their goal date)
              · archivable Resources (no living interest / untouched long-term)
              · empty or orphaned Areas; duplicated content across categories
            Output: findings table + proposed move-list. Nothing moved yet.

RITUAL      (mode: ritual) Run the weekly review steps (references/review-modes.md):
              process the inbox to zero, review each active Project's status, scan Areas for
              dropped standards, surface items needing attention this week. Interactive.

SUMMARIZE   (mode: summarize) For new/changed documents since the last review, produce short
            summaries + tags — a digest that aids filing and recall. Skips unchanged items.

ARCHIVE     Act on confirmed items only. Move completed Projects and inactive Areas/Resources to
            Archive (nesting by original category) via the matching backend adapter. Record each
            move for reversibility. Confirm Confluence/Jira changes individually.

REPORT      Emit the review report (references/report-template.md): what was audited, findings by
            severity, what was archived, what needs the user's attention, and the move log.
```

**Exit criteria:** every enabled backend inventoried; drift surfaced as a confirmable list; inbox
processed (ritual mode); confirmed items archived with a reversible move log; report emitted. No
deletions; no unconfirmed bulk moves.

## State Block

```
<para-review-state>
phase: DETECT | AUDIT | RITUAL | SUMMARIZE | ARCHIVE | REPORT | COMPLETE
mode: audit | ritual | summarize | full
backends_scanned: [comma-separated]
inbox_count: [n]
findings: [count by severity]
proposed_moves: [n]
confirmed_moves: [n]
archived: [n]
move_log: [path]
last_action: [description]
next_action: [description]
</para-review-state>
```

## Output Template

- **Audit checklist, weekly-review ritual steps, summarization rules** — `references/review-modes.md`.
- **When/how to archive per backend, reversibility & move-log format** — `references/archive-policy.md`.
- **Review report structure (findings by severity, attention list, move log)** — `references/report-template.md`.

## Integration with Other Skills

| Skill | Relationship |
|-------|-------------|
| `para-file` | The companion capture skill — review fixes drift that filing introduced; both share `.para.yml`. |
| `research-synthesis` | Use when a surfaced Resource warrants deeper investigation before keeping or archiving. |
| `confluence-guide-writer` | Use when a reviewed Confluence Project page should graduate into a published guide. |
| `session-context` | Use to carry an unfinished multi-session review forward without re-scanning from scratch. |
