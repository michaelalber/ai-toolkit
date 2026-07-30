# Email Capture — Discipline, Principles & Recovery

The domain principles, knowledge-base lookups, AI discipline rules, anti-patterns, and
error-recovery procedures that govern the capture loop.

---

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

---

## Knowledge Base Lookups

| Query | When to Call |
|-------|-------------|
| `search_knowledge("requirements extraction stakeholder communication written")` | Before EXTRACT — ground extraction heuristics in requirements engineering practices |
| `search_knowledge("change request specification scope document")` | When processing an SOW or change request — calibrate formality level of extraction |
| `search_knowledge("acceptance criteria given when then format")` | Before OUTPUT — confirm output format for extracted requirements |

Call at the start of EXTRACT. Do not repeat for the same session. Cite KB source path when a heuristic is drawn from KB content.

---

## AI Discipline Rules

**Later Messages Supersede Earlier Ones:** The latest agreed-upon position on a topic is the active requirement. Do not list both an older and newer position as active requirements without distinguishing which is current. Mark the older one `[SUPERSEDED by DRAFT-NNN]`.

**Surface Contradictions, Never Resolve Them:** When two messages say conflicting things, extract both and flag the contradiction with both positions and both sources. Do not silently pick the "more reasonable" one. The PM resolves contradictions.

**Commitments Are Requirements:** "We'll add the export feature" is as binding as "the system shall support data export." Extract all commitments with their phrasing preserved; the PM decides their binding status.

**Source Attribution Is Non-Negotiable:** Every extracted item includes sender name and message date. If sender cannot be identified, use `[Unknown Sender]`. Never omit attribution.

**Do Not Infer from Attachments Not Provided:** If the thread references an attachment that was not provided, log it as missing. Do not infer its contents from context clues in the thread. Log: `[ATTACHMENT NOT PROVIDED: filename] — Referenced by [sender] on [date]. Contents not captured. Provide this document for full coverage.`

---

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

---

## Error Recovery

**Thread Is Heavily Quoted / Interleaved:** Note the threading complexity during PARSE. Build the message map based on reply structure, not linear reading. For ambiguous attribution, note `[Attribution unclear — see source]` and flag for PM annotation.

**Thread Contains Multiple Topics or Projects:** Alert the PM: "This thread covers multiple topics: [list]. Should I capture all topics, or only [in-scope topics from intake]?" Capture only in-scope topics unless PM instructs otherwise. Note excluded topics in the trim log.

**SOW or Change Request Is Very Long (>20 pages):** Report the document length. Propose a section-by-section approach and wait for PM instruction on where to start. Produce a capture document per section, then consolidate with `capture-consolidate`.

**Output File Conflicts:** Alert the PM that a capture file already exists at the path. Offer options: overwrite, append, or save as `-v2`. Wait for PM instruction. Do not overwrite without explicit approval.
