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

**What this skill does:**
- Accepts pasted email thread text or a path to a `.txt`/`.md`/`.eml` file
- Parses the thread to identify senders, dates, and message sequence
- Extracts requirements, decisions, commitments, and open questions with source attribution
- Flags contradictions between earlier and later messages
- Produces a structured capture markdown in the Phase 1 output format with provisional `DRAFT-NNN` IDs

**What this skill does NOT do:**
- It does NOT access email accounts or inboxes — input is manual paste or file
- It does NOT synthesize requirements from ambiguous phrasing
- It does NOT resolve contradictions autonomously — contradictions go to the PM
- It does NOT push to Confluence without explicit PM instruction

## Domain Principles

| # | Principle | Applied As |
|---|-----------|------------|
| 1 | **Chronological order matters** | Later messages supersede earlier ones on the same topic. The most recent agreed-upon statement is the requirement, not the initial ask. |
| 2 | **Sender authority is context** | A requirement stated by a decision-maker carries more weight than one from an attendee. The PM identifies who has authority during INTAKE. |
| 3 | **Attachments are first-class** | SOWs, change requests, and spec documents referenced in the thread may contain the most formally stated requirements. The PM must provide their text explicitly. |
| 4 | **Contradictions are surfaced, not resolved** | When message 5 says "X" and message 12 says "not X," both are flagged. The PM resolves which is current. |
| 5 | **Commitments are requirements** | "We can have that done by March" is a schedule requirement. "We'll include the audit log" is a feature commitment. Both are extracted. |
| 6 | **Provisional IDs, not canonical REQs** | This skill assigns `DRAFT-NNN` IDs. Canonical `REQ-XXX` project numbering is assigned during `capture-consolidate`. |
| 7 | **Thread trimming is logged** | Boilerplate (signatures, disclaimers, forwarding headers, meeting invitations) is excluded from extraction. All exclusions are logged. |

## Knowledge Base Lookups

Use `search_knowledge` (grounded-code-mcp) before the EXTRACT phase.

| Query | When to Call |
|-------|-------------|
| `search_knowledge("requirements extraction stakeholder communication written")` | Before EXTRACT — ground extraction heuristics in requirements engineering practices |
| `search_knowledge("change request specification scope document")` | When processing an SOW or change request document — calibrate formality level of extraction |
| `search_knowledge("acceptance criteria given when then format")` | Before OUTPUT — confirm output format for extracted requirements |

**Protocol:** Call at the start of EXTRACT. Do not repeat for the same session. Cite KB source path when a heuristic is drawn from KB content.

## Workflow: The INTAKE–PARSE–EXTRACT–OUTPUT Loop

### Phase 1: INTAKE — Gather PM Context

Before reading the thread, collect context that guides extraction.

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
**Out-of-scope topics**: [Topics to exclude. e.g., "billing discussions", "unrelated product lines"]
```

### Phase 2: PARSE — Structure the Thread

Read the full thread and produce a parsed message map before extracting.

**Actions:**

1. Identify all messages in the thread (sender, date, subject if available)
2. Detect forwarded chains, inline replies, and attachment references
3. Build a chronological message map
4. Identify the authoritative senders from the PM's intake
5. Flag any referenced attachments that are not present in the input
6. Log the parse summary before extraction

**Parse Rules:**
- If the thread is a single document (SOW, change request, spec), treat it as one high-authority block
- If an attachment is referenced but not provided, note it in the output as `[ATTACHMENT NOT PROVIDED: filename]`
- Inline replies (text inserted into a quoted message) are attributed to the replying sender

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

Work through the parsed thread chronologically, extracting signal by message.

**Actions:**

1. Call `search_knowledge("requirements extraction stakeholder communication written")` to calibrate
2. For each message (chronological order), identify:
   - **Requirements:** Features, behaviors, or constraints the sender states the system must have
   - **Decisions:** Choices made between alternatives ("we'll go with X, not Y")
   - **Commitments:** Statements of what will be delivered or by when
   - **Open questions:** Questions asked but not answered in the thread
   - **Contradictions:** A statement that conflicts with an earlier statement on the same topic
3. Assign provisional `DRAFT-NNN` IDs to each extracted item
4. Mark the most recent position on each topic (supersedes older positions on the same item)
5. Produce the extraction log before OUTPUT

**Extraction Signal Guide:**

| Signal Type | Indicators | Example Phrases |
|---|---|---|
| `requirement` | "we need," "must have," "should include," "the system needs to," "required" | "We need SSO on day one." |
| `decision` | "we've decided," "we'll go with," "approved," "confirmed," "not X but Y" | "We're going with role-based access, not per-user." |
| `commitment` | "we can deliver," "by [date]," "included in scope," "we'll add" | "We'll include the audit log by end of Q2." |
| `open-question` | "who will handle," "need to confirm," "TBD," "still deciding," unanswered question | "Who owns the data migration?" |
| `contradiction` | Same topic, different position, different messages | Msg 3: "two weeks" / Msg 9: "one month" |

**Supersession Rule:**
When the same topic appears in multiple messages, mark earlier statements as `[SUPERSEDED by DRAFT-NNN]` and the latest position as the active requirement. Do not delete the superseded item — keep it for audit.

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

After posting the extraction log, ask the PM: "Do any of these counts look wrong? Would you like to review any category before I produce the output document?"

### Phase 4: OUTPUT — Produce Capture Document

Assemble the capture document from extracted items.

**Actions:**

1. Call `search_knowledge("acceptance criteria given when then format")` to confirm format
2. Organize extracted content by signal type
3. Produce the capture markdown using the Output Template
4. If Confluence publish is requested: ask for target space and parent page before publishing

**Output destination (default: local file):**

```
captures/[YYYY-MM-DD]-[thread-slug].md
```

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

### Capture Document

```markdown
# [Thread / Document Title] — [Date Range] — [Project / Client]

> **Capture method**: email-capture skill
> **Source**: [thread description or file name]
> **Reviewed by**: [PM name] on [date]

## Participants

- [Name] ([Role]) — [authoritative | non-authoritative]

## Summary

[2–3 sentences describing the thread's purpose and outcome.]

## Key Decisions

- [Decision statement] — *Source: [Sender name], [date]*
- [Decision statement] — *Source: [Sender name], [date]*

## Requirements Extracted

- [DRAFT-001] [Requirement statement] — *Source: [Sender name], [date]*
- [DRAFT-002] [Requirement statement] — *Source: [Sender name], [date]*
- [DRAFT-003] [Superseded requirement] [SUPERSEDED by DRAFT-005] — *Source: [Sender name], [date]*
- [DRAFT-004] [Requirement statement with uncertainty] ⚠ [UNCERTAIN] — *Source: [Sender name], [date]*

## Commitments

- [DRAFT-005] [Commitment statement] — *Source: [Sender name], [date]*

## Open Questions

- [Question statement] — *Source: [Sender name], [date]* — Status: [Unanswered / Answered in msg N]

## Contradictions Flagged

| Item | Earlier Position | Later Position | Source (Earlier) | Source (Later) | PM Resolution |
|------|-----------------|----------------|-----------------|----------------|---------------|
| [topic] | [position A] | [position B] | [sender, date] | [sender, date] | [PM to resolve] |

## Action Items

- [ ] [Action statement] — Owner: [Name] — Due: [Date if stated, else TBD]

---

## Missing Attachments

> Referenced in the thread but not provided. Contents not captured.

- [filename] — Referenced in [sender]'s message on [date]

---

## Thread Trim Log

> Content excluded from extraction. Kept for audit.

| Excluded | Reason |
|----------|--------|
| [Sender] [date] — email signature block | Boilerplate |
| [Sender] [date] — meeting invitation | Out of scope |
```

### Session Opening

```markdown
## Email Capture Session

I will help you extract structured requirements from this email thread or document.

**How this works:**

1. You tell me about the thread (project, who has decision authority, what topics are in scope)
2. I parse the thread to identify messages, senders, and sequence
3. I extract requirements, decisions, commitments, open questions, and contradictions
4. I show you a summary of what I found and you confirm before I produce the document
5. I produce a structured capture document with provisional DRAFT-NNN IDs

To begin, please tell me:
- Where is the thread or document? (paste it here, or give me a file path)
- What project does it feed into?
- Who in this thread has decision authority?

<email-capture-state>
phase: intake
project: awaiting input
thread: awaiting input
messages_parsed: 0
authoritative_senders: awaiting input
requirements_found: 0
decisions_found: 0
commitments_found: 0
open_questions_found: 0
contradictions_found: 0
attachments_missing: none
output_path: pending
last_action: Session opened
next_action: Collect PM context via Intake Template
</email-capture-state>
```

## AI Discipline Rules

### Later Messages Supersede Earlier Ones

In any email thread, the latest position on a topic is the current requirement — unless the PM indicates otherwise. Do not present both positions as active requirements. Mark the older one as `[SUPERSEDED]`.

```
WRONG: Listing both "DRAFT-001: Timeline is 2 weeks" and "DRAFT-007: Timeline is 1 month"
       as active requirements without distinguishing which is current.
RIGHT: "DRAFT-001 [SUPERSEDED by DRAFT-007]: Timeline is 2 weeks — Source: Alice, Jan 5"
       "DRAFT-007: Timeline is 1 month — Source: Bob, Jan 12 [ACTIVE]"
```

### Surface Contradictions, Never Resolve Them

When two messages say conflicting things, extract both and flag the contradiction. Do not pick the "more reasonable" one. The PM resolves contradictions.

```
WRONG: "The timeline is 1 month" (silently picking the later message)
RIGHT: "⚠ CONTRADICTION: DRAFT-001 (Alice, Jan 5): 'two-week turnaround'
        vs DRAFT-007 (Bob, Jan 12): 'give us a full month' — PM to resolve"
```

### Commitments Are Requirements

A commitment made in an email is a requirement even if it is phrased informally. "We'll add the export feature" is as binding as "the system shall support data export."

### Source Attribution Is Non-Negotiable

Every extracted item includes sender name and message date. If sender cannot be identified, use `[Unknown Sender]`. Never omit attribution.

### Do Not Infer from Attachments Not Provided

If the thread references an attachment that was not provided, log it as missing. Do not infer its contents from context clues in the thread.

```
WRONG: "Based on the mention of 'the spec document,' I've assumed it contains X."
RIGHT: "[ATTACHMENT NOT PROVIDED: project-spec-v2.pdf] — Referenced by Alice on Jan 8.
        Contents not captured. Provide this document for full coverage."
```

## Anti-Patterns

| Anti-Pattern | Description | Why It Fails | What to Do Instead |
|---|---|---|---|
| **First-message bias** | Treating the first message's requirements as the authoritative version | Email threads evolve; requirements change in reply; the initial ask is often incomplete | Work chronologically; mark superseded items; the last agreed position is the active requirement |
| **Contradiction suppression** | Silently picking the "better" position when two messages conflict | PM loses visibility into real disagreements; resolved contradictions may actually be unresolved | Surface all contradictions with both positions and both sources |
| **Attachment assumptions** | Inferring requirement content from passing references to documents not provided | Requirements you cannot trace to actual text are invented requirements | Log missing attachments; do not guess their content |
| **Boilerplate extraction** | Extracting email signatures, disclaimers, or forwarding headers as requirements | Creates noise that clutters the capture document | Log excluded boilerplate in the trim log; never extract it as requirements |
| **Informal commitment blindness** | Treating "we'll add that" as not a requirement because it is casual | Informal commitments become disputed scope in delivery | Extract all commitments with their phrasing preserved; the PM decides their binding status |
| **Sender authority collapse** | Treating all senders as equally authoritative | Non-authoritative senders may express wishes, not decisions; attributing them equally misrepresents project agreements | Mark sender authority in the capture; let the PM weight accordingly |
| **Confluence-first output** | Publishing directly to Confluence without PM review of the local draft | PM loses review opportunity before the document enters the spec pipeline | Default to local file. Ask for explicit instruction before Confluence publish. |

## Error Recovery

### Thread Is Heavily Quoted / Interleaved

Email threads with extensive in-line quoting make chronology ambiguous.

**Recovery:**
1. Note the threading complexity during PARSE
2. Build the message map based on the reply structure rather than linear reading
3. For ambiguous attribution (who said what in inline quotes), note `[Attribution unclear — see source]` and flag for PM annotation

### Thread Contains Multiple Topics or Projects

**Recovery:**
1. Alert the PM: "This thread covers multiple topics. I found content related to [list]. Should I capture all topics, or only [in-scope topics from intake]?"
2. Capture only in-scope topics unless PM instructs otherwise
3. Note excluded topics in the trim log

### SOW or Change Request Is Very Long (>20 pages)

**Recovery:**
1. Report the document length
2. Propose a section-by-section approach: "This is a large document. I suggest we process it section by section. Which section should we start with?"
3. Produce a capture document per section, then consolidate with `capture-consolidate`

### Output File Conflicts

A capture file for this thread already exists.

**Recovery:**
1. Alert the PM: "A capture file for this thread already exists at [path]. Options: overwrite, append, or save as [path]-v2."
2. Wait for PM instruction. Do not overwrite without explicit approval.

## Integration with Other Skills

- **`transcript-capture`** — Use when the intake source is a meeting transcript rather than an email or document. Both skills produce the same `DRAFT-NNN` capture format. Use `capture-consolidate` to merge outputs.
- **`capture-consolidate`** — Run after one or more capture sessions to assign canonical `REQ-XXX` IDs, deduplicate overlapping requirements across documents, and surface contradictions.
- **`jira-review`** — After `capture-consolidate` produces the final bundle, use `jira-review` to assess whether requirements are ready to decompose into Jira tickets.
- **`confluence-guide-writer`** — If the final capture document should be published to Confluence, use this skill to format and publish after PM approval.
