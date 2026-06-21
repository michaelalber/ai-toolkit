---
description: File an incoming document into the PARA system across local folders, OneDrive/Teams, and Confluence/Jira — scaffolding the structure if missing.
agent: build
subtask: false
---

<para_config>
!`cat .para.yml 2>/dev/null || echo "NO .para.yml — para-file will scaffold the PARA tree and write a starter config."`
</para_config>

<inbox>
!`ls -la 00-Inbox 2>/dev/null || ls -la ~/PARA/00-Inbox 2>/dev/null || echo "No inbox found at ./00-Inbox or ~/PARA/00-Inbox."`
</inbox>

Use the **para-file** skill to file the item given in $ARGUMENTS (or, if none, the inbox above).

Follow the skill's workflow: DETECT (load the config above; scaffold the PARA tree if missing) →
CLASSIFY by actionability (Projects → Areas → Resources → Archives, first match wins) → SUMMARIZE
(1–3 sentences + tags) → FILE via the correct backend adapter → RECORD in the index.

Confirm before the first outward-facing write to Confluence or Jira. Never delete a source.
