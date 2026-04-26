---
name: transcript-capture
description: Converts raw Zoom/Slack AI-generated transcripts into structured capture documents for spec-driven development. Uses per-block human review to filter small talk and off-topic content. The PM guides what is in scope; the skill structures that judgment. Use when given a raw Zoom transcript, Slack AI-generated meeting summary, or pasted meeting notes that need to be converted into a structured capture document for spec-driven development.
---

# Transcript Capture

> "Information is not knowledge. The map is not the territory.
> The transcript is not the meeting."
> -- Adapted from Alfred Korzybski

> "The problem with AI-generated meeting summaries is not that they are wrong.
> It is that they are confidently, plausibly, usefully wrong in exactly the right places."

## Core Philosophy

Zoom, Slack, and Teams AI summaries are high-noise artifacts. They contain small talk, tangential discussions, resolved disagreements, social coordination, and meeting logistics alongside genuine requirements. An AI that processes them without human guidance will extract all of it — or worse, hallucinate a synthesis that sounds like requirements but reflects the model's priors rather than the stakeholder's intent.

This skill does not replace PM judgment. It structures it. The PM provides context before filtering begins, reviews candidates block by block, and annotates ambiguous items. The skill organizes the judgment workflow so nothing is silently dropped and every accepted item is traceable to its source.

**What this skill does:**
- Accepts raw transcript text or a path to a `.txt`/`.md` file
- Segments the transcript into topical conversation blocks
- Scores each block for relevance against PM-provided context
- Presents each block to the PM for accept/reject/annotate decision
- Produces a structured capture markdown in the Phase 1 output format

**What this skill does NOT do:**
- It does NOT auto-accept any block without PM review
- It does NOT invent requirements from ambiguous phrasing
- It does NOT filter silently — every dropped block is logged
- It does NOT push to Confluence without explicit PM instruction

## Domain Principles

| # | Principle | Applied As |
|---|-----------|------------|
| 1 | **PM context before AI filtering** | Collect meeting purpose, domain keywords, participant roles, and out-of-scope topics before touching the transcript. The filter is calibrated to PM input, not model defaults. |
| 2 | **Per-block review, no bulk accept** | Each candidate block is presented individually. The PM cannot approve a batch. This prevents a single "looks good" from passing irrelevant content. |
| 3 | **Transparent rejection** | Every block the skill scores as low-relevance is shown with its score and reason. The PM can override any rejection. Nothing is silently discarded. |
| 4 | **Source attribution on every item** | Every extracted requirement, decision, and open question carries speaker label and timestamp (or line range if timestamps are unavailable). |
| 5 | **Provisional IDs, not canonical REQs** | This skill assigns `DRAFT-NNN` IDs. Canonical `REQ-XXX` project numbering is assigned during `capture-consolidate`. |
| 6 | **Flag uncertainty explicitly** | Ambiguous phrasing ("we should probably..." "I think we need...") is extracted with a `[UNCERTAIN]` tag and presented to the PM with the ambiguity noted. |
| 7 | **No requirement synthesis** | The skill extracts what was said. It does not combine two vague statements into a clean requirement. Synthesis is the spec generation phase. |

## Knowledge Base Lookups

Use `search_knowledge` (grounded-code-mcp) before the FILTER phase.

| Query | When to Call |
|-------|-------------|
| `search_knowledge("requirements extraction meeting transcript interview")` | Before FILTER — ground extraction heuristics in authoritative requirements engineering practices |
| `search_knowledge("acceptance criteria given when then format")` | Before OUTPUT — confirm output format for extracted requirements |
| `search_knowledge("stakeholder requirements elicitation ambiguity")` | When flagging uncertain blocks — calibrate uncertainty thresholds |

**Protocol:** Call the extraction heuristics query at the start of FILTER. Do not call again for the same session. Cite source path if a heuristic is drawn from KB content.

## Workflow: The INTAKE–FILTER–REVIEW–OUTPUT Loop

### Phase 1: INTAKE — Gather PM Context

Before reading the transcript, collect the context that calibrates the filter.

**Actions:**

1. Ask the PM for the transcript source — paste or file path (`.txt` or `.md`)
2. Collect context using the Intake Template below
3. Confirm understanding of in-scope and out-of-scope topics before proceeding
4. Only then → FILTER

**Do not proceed to FILTER without all six context fields.** If the PM skips a field, ask for it specifically. A poorly calibrated filter produces worse output than no filter.

**Intake Template:**

```markdown
## Transcript Capture — Intake

**Meeting purpose**: [What was this meeting for? e.g., "Q3 feature planning with the client"]
**Project / client**: [Which project does this feed into?]
**Participants**: [Name — Role, one per line. Who has decision authority?]
**In-scope topics**: [Keywords or topics that ARE relevant. e.g., "API design, authentication, reporting module"]
**Out-of-scope topics**: [Topics to exclude. e.g., "scheduling logistics, holiday plans, unrelated product lines"]
**Capture sensitivity**: [standard | thorough]
  standard  — only strong signals (explicit requirements, firm decisions, named open questions)
  thorough  — include soft signals (maybes, preferences, implied concerns) with [UNCERTAIN] tags
```

**Capture Sensitivity Guide:**

| Level | Use When | What It Includes |
|-------|----------|-----------------|
| `standard` | Clear, well-scoped requirements meeting | Explicit requirements, firm decisions, named action items, clear open questions |
| `thorough` | Exploratory, ambiguous, or early-stage meeting | All of the above + uncertain statements, implied preferences, raised concerns without resolution |

### Phase 2: FILTER — Segment and Score the Transcript

Read the full transcript and produce a scored candidate list before presenting to the PM.

**Actions:**

1. Call `search_knowledge("requirements extraction meeting transcript interview")` to calibrate
2. Read the transcript in full — do not extract during reading
3. Segment the transcript into topical conversation blocks (natural topic breaks, not fixed line counts)
4. For each block, assign:
   - **Block ID:** `B-001`, `B-002`, ...
   - **Speaker(s):** From transcript labels, or `[Unknown]`
   - **Timestamp / line range:** From transcript metadata, or line range
   - **Topic summary:** One line
   - **Relevance score:** `HIGH / MEDIUM / LOW / SKIP`
   - **Relevance reason:** One sentence — why this block is or is not in scope
   - **Signal type(s):** `requirement`, `decision`, `open-question`, `action-item`, `context`, `out-of-scope`
5. Log the filter summary before beginning per-block review

**Relevance Scoring:**

| Score | Criteria |
|-------|----------|
| `HIGH` | Directly names a feature, constraint, requirement, or decision within in-scope topics. Speaker is an authoritative stakeholder. |
| `MEDIUM` | Touches an in-scope topic but with uncertainty, indirectly, or from a non-authoritative speaker. |
| `LOW` | Tangentially related to in-scope topics. Requires PM judgment. |
| `SKIP` | Clearly out-of-scope: logistics, small talk, unrelated project discussion, repeated content. |

**SKIP blocks are not presented for review.** They are logged in the drop log. The PM can request to see the drop log at any time.

**Filter Summary Log:**

```markdown
### FILTER Phase Summary

**Transcript length**: [line count or word count]
**Blocks identified**: [N]
**HIGH relevance**: [N]
**MEDIUM relevance**: [N]
**LOW relevance**: [N]
**SKIP (not presented)**: [N]

Proceeding to per-block review. HIGH blocks first, then MEDIUM, then LOW.
```

### Phase 3: REVIEW — Per-Block PM Review

Present each non-SKIP block to the PM individually. Do not present the next block until the PM responds to the current one.

**Presentation Order:** HIGH blocks → MEDIUM blocks → LOW blocks

**Per-Block Presentation Format:**

```markdown
---
### Block B-[NNN] — [Relevance Score]

**Speaker**: [Name / Role, or Unknown]
**When**: [Timestamp or line range]
**Topic**: [One-line summary]
**Signal type**: [requirement | decision | open-question | action-item | context]

**Transcript excerpt**:
> [Verbatim quote of the relevant passage — 3–10 lines. Do not paraphrase.]

**Relevance reason**: [Why this block scored as it did]
[If UNCERTAIN]: ⚠ **Uncertain signal** — "[specific phrase that is ambiguous]". Flagging for PM clarification.

---
**PM decision for B-[NNN]:**
- [ ] **Accept** — include as-is
- [ ] **Accept with annotation** — include with your note: [PM types here]
- [ ] **Reject** — exclude (logged in drop log)
- [ ] **Flag for clarification** — include with a [NEEDS-CLARIFICATION] tag

Type your decision (accept / annotate / reject / flag):
```

**Review Rules:**
- Present one block at a time. Wait for PM response.
- If the PM asks to see the full block context, provide 10 additional lines before and after.
- If the PM asks to see the SKIP log at any time, show it immediately.
- If the PM asks to re-review a previously decided block, allow it without friction.
- Do not editorialize on PM decisions. Accept/reject is the PM's call.

**After all blocks are reviewed, post a review summary:**

```markdown
### REVIEW Phase Summary

**Blocks reviewed**: [N]
**Accepted**: [N]
**Accepted with annotation**: [N]
**Rejected**: [N]
**Flagged for clarification**: [N]
**SKIP (not reviewed)**: [N]

Proceeding to OUTPUT.
```

### Phase 4: OUTPUT — Produce Capture Document

Assemble the capture document from accepted blocks.

**Actions:**

1. Call `search_knowledge("acceptance criteria given when then format")` to confirm output format
2. Organize accepted content by signal type: requirements, decisions, open questions, action items
3. Assign provisional `DRAFT-NNN` IDs to all extracted requirements
4. Produce the capture markdown using the Output Template
5. If Confluence publish is requested: ask for the target space and parent page before publishing

**Provisional ID Convention:**

```
DRAFT-001, DRAFT-002, ... (within this capture session)
Canonical REQ-XXX IDs are assigned during capture-consolidate.
```

**Output destination (default: local file):**

```
captures/[YYYY-MM-DD]-[meeting-slug].md
```

If the PM requests Confluence output, ask for space key and parent page title before publishing.

## State Block

```
<transcript-capture-state>
phase: intake | filter | review | output
project: [project or client name]
meeting: [meeting name and date]
capture_sensitivity: standard | thorough
blocks_total: N
blocks_high: N
blocks_medium: N
blocks_low: N
blocks_skip: N
blocks_reviewed: N
blocks_accepted: N
blocks_rejected: N
blocks_flagged: N
current_block: B-[NNN] | complete
output_path: [file path, or "pending"]
last_action: [what was just done]
next_action: [what should happen next]
</transcript-capture-state>
```

## Output Templates

### Capture Document

```markdown
# [Meeting Name] — [Date] — [Project / Client]

> **Capture method**: transcript-capture skill | **Sensitivity**: [standard | thorough]
> **Source**: [transcript file name or "pasted"]
> **Reviewed by**: [PM name] on [date]

## Participants

- [Name] ([Role])

## Summary

[2–3 sentence overview of the meeting's purpose and outcome. Written by PM or generated from accepted context blocks.]

## Key Decisions

- [Decision statement] — *Source: [Speaker], [timestamp or line ref]*
- [Decision statement] — *Source: [Speaker], [timestamp or line ref]*

## Requirements Extracted

- [DRAFT-001] [Requirement statement] — *Source: [Speaker], [timestamp or line ref]*
- [DRAFT-002] [Requirement statement] ⚠ [UNCERTAIN] — *Source: [Speaker], [timestamp or line ref]* — PM note: [annotation if any]
- [DRAFT-003] [Requirement statement] 🔍 [NEEDS-CLARIFICATION] — *Source: [Speaker], [timestamp or line ref]*

## Open Questions

- [Question statement] — *Source: [Speaker], [timestamp or line ref]* — Assigned to: [Name or TBD]

## Action Items

- [ ] [Action statement] — Owner: [Name] — Due: [Date if stated, else "TBD"]

---

## Drop Log

> Blocks scored SKIP or rejected during review. Kept for audit trail.

| Block | Score | Reason | PM Decision |
|-------|-------|--------|-------------|
| B-003 | SKIP | Scheduling logistics — out of scope | Auto-skipped |
| B-007 | LOW | PM rejected | Rejected |
```

### Session Opening

```markdown
## Transcript Capture Session

I will help you convert this meeting transcript into a structured capture document
ready for spec generation.

**How this works:**

1. You tell me about the meeting (purpose, participants, what topics are in scope)
2. I read the full transcript and score each conversation block for relevance
3. I present blocks to you one at a time, starting with the highest-relevance content
4. You accept, annotate, reject, or flag each block for clarification
5. I produce a structured capture document with provisional DRAFT-NNN IDs

Nothing is silently dropped. Every rejected and skipped block is logged.

To begin, please tell me:
- Where is the transcript? (paste it here, or give me a file path)
- What was this meeting for?
- Which project does it feed into?

<transcript-capture-state>
phase: intake
project: awaiting input
meeting: awaiting input
capture_sensitivity: awaiting input
blocks_total: 0
blocks_reviewed: 0
blocks_accepted: 0
current_block: none
output_path: pending
last_action: Session opened
next_action: Collect PM context via Intake Template
</transcript-capture-state>
```

## AI Discipline Rules

### Never Auto-Accept, Never Auto-Filter

Every block shown to the PM requires an explicit PM decision. No block is accepted or rejected on behalf of the PM. If the PM does not respond to a block, wait. Do not proceed.

```
WRONG: "I accepted blocks B-001 through B-015 since they were all HIGH relevance."
RIGHT: Present B-001. Wait for PM decision. Present B-002. Wait. ...
```

### Verbatim Excerpts, Not Paraphrases

The block presentation shows verbatim transcript text, not a paraphrase. The PM reviews what was actually said, not what the AI thinks it means.

```
WRONG: "The client mentioned needing better reporting."
RIGHT: > "Sarah: Yeah, the thing that's been killing us is we can't get a weekly
        > summary out of the system. Like, the data's there, we just can't surface it."
```

### Uncertainty Is Surfaced, Not Resolved

When a speaker uses hedged language ("we might," "probably," "I think we want"), the skill flags it as `[UNCERTAIN]` and presents it to the PM. The skill does not harden uncertain phrasing into a definitive requirement.

```
WRONG: "REQ-003: System must provide weekly summary reports."
       (From: "we might want a weekly thing")
RIGHT: "[DRAFT-003] [UNCERTAIN] System may need weekly summary reporting.
        ⚠ Original phrasing was hedged: 'we might want a weekly thing' — confirm
        whether this is a firm requirement."
```

### Source Attribution Is Non-Negotiable

Every extracted item carries its source. If speaker labels are missing from the transcript, use `[Unknown Speaker]`. If timestamps are missing, use `[Line NNN–NNN]`. Never omit attribution.

### Provisional IDs Only

This skill does not assign `REQ-XXX` IDs. It assigns `DRAFT-NNN`. The `capture-consolidate` skill assigns canonical project REQ numbers. Mixing the two creates numbering conflicts.

## Anti-Patterns

| Anti-Pattern | Description | Why It Fails | What to Do Instead |
|---|---|---|---|
| **Bulk acceptance** | Presenting all HIGH blocks at once with a single PM approval | One "looks good" passes irrelevant content; PM cannot meaningfully review a wall of text | Present one block at a time. Wait for explicit PM decision per block. |
| **Silent filtering** | Dropping SKIP blocks without logging them | PM cannot audit what was excluded; legitimate requirements can be lost | Log every SKIP block in the drop log. Make the log available on request. |
| **Requirement synthesis** | Combining two vague statements into a polished requirement | Creates requirements that nobody said; the synthesis is the AI's interpretation, not the stakeholder's intent | Extract verbatim. Flag ambiguity. Leave synthesis for the spec generation phase. |
| **Hardening uncertainty** | Converting "we might need X" into "System shall X" | Generates false requirements; wastes spec review time | Tag `[UNCERTAIN]`, present verbatim, let PM decide whether to confirm or exclude. |
| **Skipping intake** | Jumping straight to filtering without PM context | The filter has no calibration; everything scores MEDIUM; the PM has to review noise | Collect all six intake fields before reading the transcript. |
| **Paraphrasing excerpts** | Showing the AI's summary of a block instead of the verbatim text | PM reviews the AI's interpretation, not the actual words; paraphrase errors propagate | Show verbatim transcript text in the block presentation. |
| **Confluence-first output** | Publishing directly to Confluence without PM review of the local draft | PM loses the ability to review the capture document before it enters the spec pipeline | Default to local file. Ask for explicit instruction before publishing to Confluence. |

## Error Recovery

### Transcript Has No Speaker Labels

Many Zoom AI transcripts strip speaker names or use generic labels ("Speaker 1").

**Recovery:**
1. Note the missing labels during INTAKE: "This transcript does not have speaker labels. I will use [Speaker A], [Speaker B], etc. based on conversational context, and mark them [Inferred]."
2. Ask the PM to identify at least one speaker by a phrase they recognize ("Which speaker says [X]?")
3. Infer other speakers from context where possible, mark all inferred labels `[Inferred]`
4. Where inference is not possible, use `[Unknown Speaker]`
5. Flag all blocks with unresolved attribution during REVIEW — PM can annotate

### Transcript Is Very Long (>200 blocks)

**Recovery:**
1. Report the block count to the PM during the FILTER summary
2. Propose a prioritized review: "There are 247 blocks. I suggest we review all HIGH blocks first (N), then you decide whether to continue to MEDIUM."
3. Never present LOW blocks without explicit PM instruction to do so
4. Offer a SKIP-log review as an alternative to reviewing every LOW block manually

### PM Wants to Change Intake Context Mid-Review

The PM realizes mid-review that the scope is wrong ("Actually, the pricing discussion IS in scope").

**Recovery:**
1. Accept the scope change without friction
2. Re-score already-reviewed blocks that may be affected by the change
3. Present re-scored blocks for PM re-review before continuing with new blocks
4. Update the Intake Template record with the revised scope

### Output File Conflicts

A capture file for this date and meeting already exists.

**Recovery:**
1. Alert the PM: "A capture file for this meeting already exists at [path]. Options: overwrite, append, or save as [path]-v2."
2. Wait for PM instruction. Do not overwrite without explicit approval.

### Transcript Is a Slack AI Summary, Not a Full Transcript

Slack AI summaries are already filtered by another AI — they are not raw transcripts.

**Recovery:**
1. Note this to the PM: "This appears to be a Slack AI summary, not a raw transcript. It has already been filtered by Slack's model, which may have dropped relevant content."
2. Recommend the PM retrieve the original thread if possible
3. If the PM wants to proceed with the summary: treat it as a single HIGH-relevance block and present it for annotation, rather than segmenting it

## Integration with Other Skills

- **`email-capture`** — Use when the intake source is an email thread or document instead of a meeting transcript. Both skills produce the same `DRAFT-NNN` capture format. Use `capture-consolidate` to merge outputs from both.
- **`capture-consolidate`** — Run after one or more `transcript-capture` and/or `email-capture` sessions to assign canonical `REQ-XXX` IDs, deduplicate overlapping requirements, and surface contradictions across capture documents.
- **`jira-review`** — After capture-consolidate produces the final bundle, use `jira-review` to assess whether the requirements are ready to decompose into Jira tickets.
- **`confluence-guide-writer`** — If the final capture document should be published to Confluence as a stakeholder-facing artifact, use this skill to format and publish it after PM approval.
