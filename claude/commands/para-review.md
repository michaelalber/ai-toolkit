---
description: Runs a periodic PARA review — hygiene audit, weekly review ritual, document summarization, and safe archiving — across local folders, OneDrive/Teams, and Confluence/Jira. Use for "weekly review", "PARA audit", or "archive finished projects". Usage: /para-review [audit|ritual|summarize|full]
allowed-tools: Bash(cat .para.yml:*), Bash(ls:*), Bash(find:*), Read
---

<para_config>
!`cat .para.yml 2>/dev/null || echo "NO .para.yml — run /para-file first to scaffold the PARA tree and config."`
</para_config>

<inbox>
!`ls -la 00-Inbox 2>/dev/null || ls -la ~/PARA/00-Inbox 2>/dev/null || echo "No inbox found."`
</inbox>

Use the **para-review** skill in the mode given in $ARGUMENTS (default: `full`).

Follow the skill's workflow: DETECT (read-only inventory from the config above) → AUDIT (drift:
misfiled, stale Projects, archivable Resources, empty Areas) → RITUAL (process inbox, review
Projects/Areas, surface attention) → SUMMARIZE (digest new/changed docs) → ARCHIVE (confirmed items
only, reversible) → REPORT.

Propose before moving. Archive, never delete. Confirm Confluence/Jira changes individually.
Lead the report with what needs the user's attention.
