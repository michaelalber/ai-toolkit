# Email Capture — Templates

All phase templates and the capture document structure. Loaded just-in-time during the
INTAKE → PARSE → EXTRACT → OUTPUT loop.

---

## INTAKE — Intake Template

Collect all five context fields before proceeding to PARSE.

```markdown
## Email Capture — Intake

**Project / client**: [Which project does this thread feed into?]
**Thread / document description**: [e.g., "Client kickoff email thread", "SOW v2.1", "Change request for reporting module"]
**Authoritative senders**: [Senders whose statements carry decision weight. Name — Role. One per line.]
**In-scope topics**: [Topics or features that ARE relevant to this project.]
**Out-of-scope topics**: [Topics to exclude.]
```

---

## PARSE — Parse Summary Log

Log this before extraction.

```markdown
### PARSE Phase Summary

**Thread type**: [email thread | SOW | change request | meeting follow-up | other]
**Messages identified**: [N]
**Date range**: [earliest — latest]
**Senders**: [list with authority level: authoritative | non-authoritative]
**Attachments referenced**: [list, or "none"]
**Attachments provided**: [list, or "none"]

Proceeding to EXTRACT.
```

**Parse rules:**
- If the thread is a single document (SOW, change request, spec), treat it as one high-authority block.
- If an attachment is referenced but not provided, note it as `[ATTACHMENT NOT PROVIDED: filename]`.
- Inline replies are attributed to the replying sender.

---

## EXTRACT — Extraction Signal Guide

| Signal Type | Indicators | Example Phrases |
|---|---|---|
| `requirement` | "we need," "must have," "should include," "required" | "We need SSO on day one." |
| `decision` | "we've decided," "we'll go with," "confirmed," "not X but Y" | "We're going with role-based access." |
| `commitment` | "we can deliver," "by [date]," "included in scope," "we'll add" | "We'll include the audit log by end of Q2." |
| `open-question` | "who will handle," "TBD," "still deciding," unanswered question | "Who owns the data migration?" |
| `contradiction` | Same topic, different position, different messages | Msg 3: "two weeks" / Msg 9: "one month" |

**Supersession Rule:** When the same topic appears in multiple messages, mark earlier statements as `[SUPERSEDED by DRAFT-NNN]` and the latest position as the active requirement. Do not delete the superseded item — keep it for audit.

### EXTRACT — Extraction Log

```markdown
### EXTRACT Phase Summary

**Requirements identified**: [N]
**Decisions identified**: [N]
**Commitments identified**: [N]
**Open questions identified**: [N]
**Contradictions flagged**: [N]
**Superseded items**: [N]

Proceeding to OUTPUT — please confirm before I generate the document, or request changes.
```

---

## OUTPUT — Capture Document Template

Title line:

`# [Thread Title] — [Date Range] — [Project / Client]`

Sections, in order:

- **Participants** — Name / Role / authority level
- **Summary** — 2–3 sentences
- **Key Decisions** — statement + `Source: sender, date`
- **Requirements Extracted** — `DRAFT-NNN` + statement + source, with `[SUPERSEDED by DRAFT-NNN]` or `⚠ [UNCERTAIN]` tags
- **Commitments** — `DRAFT-NNN` + statement + source
- **Open Questions** — question + source + status (Unanswered / Answered in msg N)
- **Contradictions Flagged** — table: Item / Earlier Position / Later Position / Source-Earlier / Source-Later / PM Resolution
- **Action Items** — owner + due date
- **Missing Attachments** — filename + who referenced it
- **Thread Trim Log** — table: Excluded / Reason

Default output path: `captures/[YYYY-MM-DD]-[thread-slug].md`

---

## Session Opening

Explain the 4-phase process (intake → parse → extract → output). State that nothing is
silently excluded. Ask: where is the thread/document, what project does it feed into, and
who has decision authority. Emit the initial `<email-capture-state>` with `phase: intake`.
