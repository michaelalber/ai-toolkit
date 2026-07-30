# Thread Parsing Reference — Email Capture

A reference for parsing email threads, SOWs, change requests, and document attachments. Use during the PARSE and EXTRACT phases.

---

## Email Thread Structure

### Reading Chronological Order

Email threads can be disorienting because most clients show the most recent message first. Always read bottom-to-top (or oldest-to-newest) to establish chronological order before extracting.

**Key structural markers:**
- **Sent:** / **Date:** headers — the authoritative timestamp
- **From:** / **To:** / **Cc:** — sender and authority map
- **Subject:** — thread topic; changes in subject line often signal a new topic branch
- **Re:** / **Fwd:** prefixes — reply chains and forwarded content
- **Quoted text** (indented, `>` prefix, or different formatting) — earlier message content appearing in a reply

**Inline reply rule:** When a sender inserts text inside a quoted message from another sender, attribute that inserted text to the replying sender, not the original.

---

## Message Authority Map

Build this during PARSE to calibrate extraction weight.

| Role | Typical Authority Level | Notes |
|---|---|---|
| Client executive (VP, Director, C-suite) | Decision authority | Binding commitments; scope changes carry highest weight |
| Client product owner / PM | Feature authority | Requirements and prioritization decisions |
| Client technical lead | Technical authority | Constraints, integration requirements, platform specifications |
| Client end user / analyst | Preference signal | Pain points, usability needs; not always binding requirements |
| Internal PM / BA | Relay / clarification | Often summarizes client intent — cross-reference to original client statement |
| Internal technical lead | Feasibility signal | Constraints and caveats; not scope-defining |
| Sales / account management | Commitment risk | May commit to scope without technical authority — flag any commitments |

**Supersession rule by authority:** If an executive later says something different from what a lower-authority person said, the executive's statement supersedes unless the lower-authority statement was explicitly confirmed. Document both.

---

## Document Type Reference

### Statement of Work (SOW)

SOWs are the highest-formality capture target. Structure:

| Section | What to Extract |
|---|---|
| **Scope of Work** | Requirements (explicit and implied), feature list |
| **Deliverables** | Commitments with acceptance criteria |
| **Timeline / Milestones** | Schedule commitments, dependency dates |
| **Assumptions** | Constraints and pre-conditions — extract as scope boundaries |
| **Exclusions** | What is explicitly out of scope — critical for conflict detection |
| **Change Control** | How scope changes are handled — extract as process requirements |

**Key trap:** SOW assumptions are often functional requirements in disguise. "Assumes client provides user authentication" may mean "system does not need to implement authentication" — extract that.

---

### Change Request

Change requests modify an existing scope. Always extract:
- What is being added, removed, or modified
- The approval chain (who requested, who authorized)
- Effective date
- Any impact to existing requirements (which REQs are superseded)

**Supersession discipline:** A change request always supersedes some prior requirement. When extracting from a change request, identify which DRAFT or REQ items it affects and flag them for SUPERSEDED marking.

---

### Meeting Follow-Up Email

Meeting follow-up emails often contain the most reliable capture artifacts — the sender has distilled the meeting into decisions and actions. However, they are a paraphrase of what was said, not a verbatim record.

**Extraction protocol:**
1. Extract decisions and action items as HIGH confidence
2. Extract requirements as MEDIUM confidence — cross-reference against the raw transcript if available
3. Flag any "per our discussion" references that cannot be verified against a raw transcript

---

## Contradiction Detection Patterns

Common patterns where earlier and later messages conflict:

| Pattern | Example | Detection |
|---|---|---|
| **Timeline shift** | "2 weeks" → "1 month" | Same deliverable, different date |
| **Scope expansion** | "basic auth" → "SSO required" | Feature requirement upgrade |
| **Scope reduction** | "full reporting suite" → "just the dashboard" | Feature removal |
| **Priority inversion** | "Phase 1 must-have" → "can wait for Phase 2" | Priority change |
| **Vendor change** | "we'll use AWS" → "we're going on-prem" | Platform/technology reversal |
| **Owner reassignment** | "our team handles data migration" → "you'll handle migration" | Responsibility shift |

**Rule:** When two messages contradict, extract both positions as separate DRAFT items and flag the pair as a contradiction. Do not pick the winner.

---

## Boilerplate Exclusion Reference

Content to classify as trim and log (not extract):

| Type | Examples |
|---|---|
| Email signatures | Name, title, phone, company, social links, legal disclaimers |
| Forwarding headers | "---------- Forwarded message ---------" |
| Meeting invitations | Calendar blocks, Zoom links included in email body |
| Automatic disclaimers | "This message may be confidential..." / "Consider the environment before printing" |
| Thread history markers | "On [date] [sender] wrote:" |
| Auto-reply content | Out-of-office messages |
| Unsubscribe footers | Marketing email footers |

**Log these in the trim log.** Do not extract. Do not silently discard — the trim log is the audit trail that lets the PM verify nothing was missed.

---

## Attachment Handling

Attachments referenced in threads but not provided are a common source of missing requirements.

**Protocol when an attachment is not provided:**
1. Identify the attachment name and the message that references it
2. Log it as `[ATTACHMENT NOT PROVIDED: filename]`
3. Include the reference context: who mentioned it, in what message, what they implied it contains
4. Do not infer the attachment's content

**Common high-value attachments to watch for:**
- Wireframes / mockups → UI/UX requirements
- Spreadsheet models → data structure or calculation requirements
- Earlier SOW versions → baseline scope, possible superseded requirements
- Test plans / acceptance criteria → verification requirements
- System architecture diagrams → integration and performance requirements
