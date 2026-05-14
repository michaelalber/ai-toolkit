---
name: email-capture
description: Converts email threads, SOWs, change requests, and pasted documents into structured capture documents for spec-driven development. Extracts requirements, decisions, commitments, and open questions with source attribution to sender and message date. Use when given an email thread, SOW, change request, or pasted document that needs to be converted into structured requirements with per-message source attribution.
---

# Email Capture

> "The difference between a requirement and a preference is whether anyone will know
> if you ship without it."
> -- Adapted from Karl Wiegers, "Software Requirements"

> "Every email thread is a negotiation. Requirements hide in the agreement,
> not the conversation."

## Core Philosophy

Email threads are lower-noise than meeting transcripts but structurally messier. Requirements are embedded in reply chains, buried under greetings and signatures, split across multiple messages, and sometimes contradicted in later replies. A change request buried in a forwarded attachment is still a requirement.

This skill reads email threads and documents methodically — parsing by sender authority, chronological order, and message type — to extract requirements, decisions, commitments, and open questions. Unlike transcript capture, email content is often more decisive ("we need X by date Y") but also more fragmented (the final agreed version is in message 12 of a 15-message thread, not in message 1).

**What this skill does:** Accepts pasted email thread text or a file path. Parses the thread to identify senders, dates, and message sequence. Extracts requirements, decisions, commitments, and open questions with source attribution. Flags contradictions between earlier and later messages. Produces a structured capture markdown with provisional `DRAFT-NNN` IDs.

**What this skill does NOT do:** Access email accounts or inboxes (input is manual paste or file), synthesize requirements from ambiguous phrasing, resolve contradictions autonomously, or push to Confluence without explicit PM instruction.

## Domain Principles

| # | Principle | Applied As |
|---|-----------|------------|
| 1 | **Chronological order matters** | Later messages supersede earlier ones on the same topic. The most recent agreed-upon statement is the requirement, not the initial ask. |
| 2 | **Sender authority is context** | A requirement stated by a decision-maker carries more weight than one from an attendee. The PM identifies who has authority during INTAKE. |
| 3 | **Attachments are first-class** | SOWs, change requests, and spec documents referenced in the thread may contain the most formally stated requirements. The PM must provide their text explicitly. |
| 4 | **Contradictions are surfaced, not resolved** | When message 5 says "X" and message 12 says "not X," both are flagged. The PM resolves which is current. |
| 5 | **Commitments are requirements** | "We can have that done by March" is a schedule requirement. "We'll include the audit log" is a feature commitment. Both are extracted. |
| 6 | **Provisional IDs, not canonical REQs** | This skill assigns `DRAFT-NNN` IDs. Canonical `REQ-XXX` project numbering is assigned during `capture-consolidate`. |
| 7 | **Thread trimming is logged** | Boilerplate (signatures, disclaimers, forwarding headers) is excluded. All exclusions are logged. |

## Knowledge Base Lookups

| Query | When to Call |
|-------|-------------|
| `search_knowledge("requirements extraction stakeholder communication written")` | Before EXTRACT — ground extraction heuristics in requirements engineering practices |
| `search_knowledge("change request specification scope document")` | When processing an SOW or change request — calibrate formality level of extraction |
| `search_knowledge("acceptance criteria given when then format")` | Before OUTPUT — confirm output format for extracted requirements |

Call at the start of EXTRACT. Do not repeat for the same session. Cite KB source path when a heuristic is drawn from KB content.

## Workflow: The INTAKE–PARSE–EXTRACT–OUTPUT Loop

### Phase 1: INTAKE — Gather PM Context

**Actions:**
1. Ask the PM to provide the email thread — paste text or give file path
2. Collect context using the Intake Template below
3. Confirm understanding of authoritative senders and document scope before proceeding
4. Only then → PARSE

**Do not proceed without all five context fields.**

**Intake Template:**

```markdown
## Email Capture — Intake

**Project / client**: [Which project does this thread feed into?]
**Thread / document description**: [e.g., "Client kickoff email thread", "SOW v2.1", "Change request for reporting module"]
**Authoritative senders**: [Senders whose statements carry decision weight. Name — Role. One per line.]
**In-scope topics**: [Topics or features that ARE relevant to this project.]
**Out-of-scope topics**: [Topics to exclude.]
```

### Phase 2: PARSE — Structure the Thread

**Actions:**
1. Identify all messages in the thread (sender, date, subject if available)
2. Detect forwarded chains, inline replies, and attachment references
3. Build a chronological message map
4. Identify the authoritative senders from the PM's intake
5. Flag any referenced attachments that are not present in the input
6. Log the parse summary before extraction

**Parse Rules:**
- If the thread is a single document (SOW, change request, spec), treat it as one high-authority block
- If an attachment is referenced but not provided, note it as `[ATTACHMENT NOT PROVIDED: filename]`
- Inline replies are attributed to the replying sender

**Parse Summary Log:**

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

### Phase 3: EXTRACT — Pull Requirements, Decisions, Commitments, Open Questions

**Actions:**
1. Call `search_knowledge("requirements extraction stakeholder communication written")` to calibrate
2. Work through the parsed thread chronologically, extracting signal by message
3. Assign provisional `DRAFT-NNN` IDs to each extracted item
4. Mark the most recent position on each topic (supersedes older positions on the same item)
5. Produce the extraction log before OUTPUT

**Extraction Signal Guide:**

| Signal Type | Indicators | Example Phrases |
|---|---|---|
| `requirement` | "we need," "must have," "should include," "required" | "We need SSO on day one." |
| `decision` | "we've decided," "we'll go with," "confirmed," "not X but Y" | "We're going with role-based access." |
| `commitment` | "we can deliver," "by [date]," "included in scope," "we'll add" | "We'll include the audit log by end of Q2." |
| `open-question` | "who will handle," "TBD," "still deciding," unanswered question | "Who owns the data migration?" |
| `contradiction` | Same topic, different position, different messages | Msg 3: "two weeks" / Msg 9: "one month" |

**Supersession Rule:** When the same topic appears in multiple messages, mark earlier statements as `[SUPERSEDED by DRAFT-NNN]` and the latest position as the active requirement. Do not delete the superseded item — keep it for audit.

**Extraction Log:**

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

### Phase 4: OUTPUT — Produce Capture Document

**Actions:**
1. Call `search_knowledge("acceptance criteria given when then format")` to confirm format
2. Organize extracted content by signal type
3. Produce the capture markdown using the Output Template below
4. If Confluence publish is requested: ask for target space and parent page before publishing

Default output path: `captures/[YYYY-MM-DD]-[thread-slug].md`

## State Block

```
<email-capture-state>
phase: intake | parse | extract | output
project: [project or client name]
thread: [thread description and date range]
messages_parsed: N
authoritative_senders: [list]
requirements_found: N
decisions_found: N
commitments_found: N
open_questions_found: N
contradictions_found: N
attachments_missing: [list or "none"]
output_path: [file path, or "pending"]
last_action: [what was just done]
next_action: [what should happen next]
</email-capture-state>
```

## Output Templates

**Capture Document structure:**
`# [Thread Title] — [Date Range] — [Project / Client]`
Sections: Participants (Name / Role / authority level) | Summary (2–3 sentences) | Key Decisions (statement + Source: sender, date) | Requirements Extracted (DRAFT-NNN + statement + source, with `[SUPERSEDED by DRAFT-NNN]` or `⚠ [UNCERTAIN]` tags) | Commitments (DRAFT-NNN + statement + source) | Open Questions (question + source + status: Unanswered / Answered in msg N) | Contradictions Flagged (table: Item / Earlier Position / Later Position / Source-Earlier / Source-Later / PM Resolution) | Action Items (owner + due date) | Missing Attachments (filename + who referenced it) | Thread Trim Log (table: Excluded / Reason).

**Session Opening:** Explain the 4-phase process (intake → parse → extract → output). State that nothing is silently excluded. Ask: where is the thread/document, what project does it feed into, and who has decision authority. Emit initial `<email-capture-state>` with `phase: intake`.

Full template: `references/email-capture-templates.md`

## AI Discipline Rules

**Later Messages Supersede Earlier Ones:** The latest agreed-upon position on a topic is the active requirement. Do not list both an older and newer position as active requirements without distinguishing which is current. Mark the older one `[SUPERSEDED by DRAFT-NNN]`.

**Surface Contradictions, Never Resolve Them:** When two messages say conflicting things, extract both and flag the contradiction with both positions and both sources. Do not silently pick the "more reasonable" one. The PM resolves contradictions.

**Commitments Are Requirements:** "We'll add the export feature" is as binding as "the system shall support data export." Extract all commitments with their phrasing preserved; the PM decides their binding status.

**Source Attribution Is Non-Negotiable:** Every extracted item includes sender name and message date. If sender cannot be identified, use `[Unknown Sender]`. Never omit attribution.

**Do Not Infer from Attachments Not Provided:** If the thread references an attachment that was not provided, log it as missing. Do not infer its contents from context clues in the thread. Log: `[ATTACHMENT NOT PROVIDED: filename] — Referenced by [sender] on [date]. Contents not captured. Provide this document for full coverage.`

## Anti-Patterns

| Anti-Pattern | Why It Fails | What to Do Instead |
|---|---|---|
| **First-message bias** | Email threads evolve; the initial ask is often incomplete | Work chronologically; mark superseded items; the last agreed position is active |
| **Contradiction suppression** | PM loses visibility into real disagreements | Surface all contradictions with both positions and both sources |
| **Attachment assumptions** | Requirements you cannot trace to actual text are invented requirements | Log missing attachments; do not guess their content |
| **Boilerplate extraction** | Creates noise that clutters the capture document | Log excluded boilerplate in the trim log; never extract it as requirements |
| **Informal commitment blindness** | Informal commitments become disputed scope in delivery | Extract all commitments; PM decides binding status |
| **Sender authority collapse** | Non-authoritative senders express wishes, not decisions | Mark sender authority; let PM weight accordingly |
| **Confluence-first output** | PM loses review opportunity before spec pipeline | Default to local file; ask for explicit instruction before Confluence publish |

## Error Recovery

**Thread Is Heavily Quoted / Interleaved:** Note the threading complexity during PARSE. Build the message map based on reply structure, not linear reading. For ambiguous attribution, note `[Attribution unclear — see source]` and flag for PM annotation.

**Thread Contains Multiple Topics or Projects:** Alert the PM: "This thread covers multiple topics: [list]. Should I capture all topics, or only [in-scope topics from intake]?" Capture only in-scope topics unless PM instructs otherwise. Note excluded topics in the trim log.

**SOW or Change Request Is Very Long (>20 pages):** Report the document length. Propose a section-by-section approach and wait for PM instruction on where to start. Produce a capture document per section, then consolidate with `capture-consolidate`.

**Output File Conflicts:** Alert the PM that a capture file already exists at the path. Offer options: overwrite, append, or save as `-v2`. Wait for PM instruction. Do not overwrite without explicit approval.

## Integration with Other Skills

- **`transcript-capture`** — Use when the intake source is a meeting transcript rather than an email or document. Both skills produce the same `DRAFT-NNN` capture format. Use `capture-consolidate` to merge outputs.
- **`capture-consolidate`** — Run after one or more capture sessions to assign canonical `REQ-XXX` IDs, deduplicate overlapping requirements, and surface contradictions.
- **`jira-review`** — After `capture-consolidate` produces the final bundle, use `jira-review` to assess whether requirements are ready to decompose into Jira tickets.
- **`confluence-guide-writer`** — If the final capture document should be published to Confluence, use this skill to format and publish after PM approval.
