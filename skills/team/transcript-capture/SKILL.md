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

**What this skill does:** Accepts raw transcript text or a file path, segments into topical conversation blocks, scores each block for relevance, presents each to the PM for accept/reject/annotate decision, produces a structured capture markdown with `DRAFT-NNN` IDs.

**What this skill does NOT do:** Auto-accept any block, invent requirements from ambiguous phrasing, filter silently, or push to Confluence without explicit PM instruction.

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

| Query | When to Call |
|-------|-------------|
| `search_knowledge("requirements extraction meeting transcript interview")` | Before FILTER — ground extraction heuristics in authoritative requirements engineering practices |
| `search_knowledge("acceptance criteria given when then format")` | Before OUTPUT — confirm output format for extracted requirements |
| `search_knowledge("stakeholder requirements elicitation ambiguity")` | When flagging uncertain blocks — calibrate uncertainty thresholds |

Call the extraction heuristics query at the start of FILTER. Do not repeat for the same session. Cite source path if a heuristic is drawn from KB content.

## Workflow: The INTAKE–FILTER–REVIEW–OUTPUT Loop

### Phase 1: INTAKE — Gather PM Context

**Actions:**
1. Ask the PM for the transcript source — paste or file path (`.txt` or `.md`)
2. Collect context using the Intake Template below
3. Confirm understanding of in-scope and out-of-scope topics before proceeding
4. Only then → FILTER

**Do not proceed to FILTER without all six context fields.** If the PM skips a field, ask for it specifically.

**Intake Template:**

```markdown
## Transcript Capture — Intake

**Meeting purpose**: [What was this meeting for? e.g., "Q3 feature planning with the client"]
**Project / client**: [Which project does this feed into?]
**Participants**: [Name — Role, one per line. Who has decision authority?]
**In-scope topics**: [Keywords or topics that ARE relevant]
**Out-of-scope topics**: [Topics to exclude]
**Capture sensitivity**: [standard | thorough]
  standard  — only strong signals (explicit requirements, firm decisions, named open questions)
  thorough  — include soft signals (maybes, preferences, implied concerns) with [UNCERTAIN] tags
```

| Level | Use When | What It Includes |
|-------|----------|-----------------|
| `standard` | Clear, well-scoped requirements meeting | Explicit requirements, firm decisions, named action items, clear open questions |
| `thorough` | Exploratory or early-stage meeting | All of the above + uncertain statements, implied preferences, raised concerns without resolution |

### Phase 2: FILTER — Segment and Score the Transcript

**Actions:**
1. Call `search_knowledge("requirements extraction meeting transcript interview")` to calibrate
2. Read the transcript in full — do not extract during reading
3. Segment into topical conversation blocks (natural topic breaks, not fixed line counts)
4. For each block, assign: Block ID (`B-001`, ...), Speaker(s), Timestamp / line range, Topic summary, Relevance score (`HIGH / MEDIUM / LOW / SKIP`), Relevance reason, Signal type(s)
5. Log the filter summary, then begin per-block review

**Relevance Scoring:**

| Score | Criteria |
|-------|----------|
| `HIGH` | Directly names a feature, constraint, requirement, or decision within in-scope topics. Speaker is an authoritative stakeholder. |
| `MEDIUM` | Touches an in-scope topic but with uncertainty, indirectly, or from a non-authoritative speaker. |
| `LOW` | Tangentially related. Requires PM judgment. |
| `SKIP` | Clearly out-of-scope: logistics, small talk, unrelated project discussion, repeated content. |

SKIP blocks are not presented for review — they are logged in the drop log. PM can request the drop log at any time.

After scoring, post a brief summary (block counts by score, totals) before beginning per-block review.

### Phase 3: REVIEW — Per-Block PM Review

Present each non-SKIP block individually. Do not present the next block until the PM responds to the current one. Order: HIGH → MEDIUM → LOW.

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

**Review Rules:** Present one block at a time and wait. If the PM requests full block context, provide 10 additional lines. If the PM requests the SKIP log, show it immediately. Allow re-review of previously decided blocks without friction. Do not editorialize on PM decisions.

After all blocks are reviewed, post a brief summary (accepted / rejected / flagged / skipped counts) before proceeding to OUTPUT.

### Phase 4: OUTPUT — Produce Capture Document

**Actions:**
1. Call `search_knowledge("acceptance criteria given when then format")` to confirm output format
2. Organize accepted content by signal type: requirements, decisions, open questions, action items
3. Assign provisional `DRAFT-NNN` IDs to all extracted requirements
4. Produce the capture markdown (see Output Templates)
5. If Confluence publish is requested: ask for target space and parent page before publishing

Default output path: `captures/[YYYY-MM-DD]-[meeting-slug].md`

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

**Capture Document header:**
`# [Meeting Name] — [Date] — [Project / Client]`
Sections: Participants | Summary (2–3 sentences) | Key Decisions (statement + source attribution) | Requirements Extracted (DRAFT-NNN + statement + source, with `⚠ [UNCERTAIN]` or `🔍 [NEEDS-CLARIFICATION]` tags) | Open Questions (question + owner) | Action Items (owner + due date) | Drop Log (Block / Score / Reason / PM Decision)

**Session Opening:** Explain the 4-phase process (intake → filter → review → output), state that nothing is silently dropped, ask for transcript location, meeting purpose, and project. Emit initial `<transcript-capture-state>` with `phase: intake`.

Full template: `references/capture-templates.md`

## AI Discipline Rules

**Never Auto-Accept, Never Auto-Filter:** Every block shown to the PM requires an explicit PM decision. No block is accepted or rejected on the PM's behalf. Present one block, wait for response, then present the next — without exception.

**Verbatim Excerpts, Not Paraphrases:** The block presentation shows verbatim transcript text, not a paraphrase. The PM reviews what was actually said, not what the AI thinks it means. Paraphrase errors propagate forward into specs.

**Uncertainty Is Surfaced, Not Resolved:** When a speaker uses hedged language ("we might," "probably," "I think we want"), flag it `[UNCERTAIN]` and present it verbatim. Do not harden uncertain phrasing into a definitive requirement. Let the PM decide whether to confirm or exclude.

**Source Attribution Is Non-Negotiable:** Every extracted item carries its source. Missing speaker labels become `[Unknown Speaker]`. Missing timestamps become `[Line NNN–NNN]`. Never omit attribution.

**Provisional IDs Only:** This skill assigns `DRAFT-NNN` IDs. The `capture-consolidate` skill assigns canonical `REQ-XXX` numbers. Mixing the two creates numbering conflicts.

## Anti-Patterns

| Anti-Pattern | Why It Fails | What to Do Instead |
|---|---|---|
| **Bulk acceptance** | One "looks good" passes irrelevant content | Present one block at a time. Wait for explicit PM decision per block. |
| **Silent filtering** | PM cannot audit what was excluded; legitimate requirements can be lost | Log every SKIP block in the drop log. Make the log available on request. |
| **Requirement synthesis** | Creates requirements that nobody said | Extract verbatim. Flag ambiguity. Leave synthesis for the spec generation phase. |
| **Hardening uncertainty** | Generates false requirements; wastes spec review time | Tag `[UNCERTAIN]`, present verbatim, let PM decide whether to confirm or exclude. |
| **Skipping intake** | The filter has no calibration; everything scores MEDIUM | Collect all six intake fields before reading the transcript. |
| **Paraphrasing excerpts** | PM reviews the AI's interpretation, not the actual words | Show verbatim transcript text in the block presentation. |
| **Confluence-first output** | PM loses the ability to review the capture document before it enters the spec pipeline | Default to local file. Ask for explicit instruction before publishing. |

## Error Recovery

**Transcript Has No Speaker Labels:** During INTAKE, note the missing labels and switch to `[Speaker A]`, `[Speaker B]`, etc. Ask the PM to identify at least one speaker by a recognizable phrase. Mark all inferred labels `[Inferred]`. Flag unresolved attribution during REVIEW.

**Transcript Is Very Long (>200 blocks):** Report the block count during the FILTER summary. Propose prioritized review: all HIGH blocks first, then ask whether to continue to MEDIUM. Never present LOW blocks without explicit PM instruction.

**PM Wants to Change Intake Context Mid-Review:** Accept the scope change without friction. Re-score already-reviewed blocks that may be affected. Present re-scored blocks for PM re-review before continuing. Update the Intake Template record with the revised scope.

**Output File Conflicts:** Alert the PM that a capture file already exists at the path. Offer options: overwrite, append, or save as `-v2`. Wait for PM instruction. Do not overwrite without explicit approval.

**Transcript Is a Slack AI Summary:** Note to the PM that this is a pre-filtered artifact — Slack's model may have dropped relevant content. Recommend retrieving the original thread. If the PM proceeds, treat the summary as a single HIGH block for annotation rather than segmenting it.

## Integration with Other Skills

- **`email-capture`** — Use when the intake source is an email thread instead of a meeting transcript. Both produce the same `DRAFT-NNN` format; use `capture-consolidate` to merge outputs.
- **`capture-consolidate`** — Run after one or more capture sessions to assign canonical `REQ-XXX` IDs, deduplicate overlapping requirements, and surface contradictions.
- **`jira-review`** — After capture-consolidate produces the final bundle, assess whether requirements are ready to decompose into Jira tickets.
- **`confluence-guide-writer`** — If the final capture document should be published as a stakeholder-facing artifact, use this skill to format and publish it after PM approval.
