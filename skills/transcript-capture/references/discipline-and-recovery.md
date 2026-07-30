# Discipline, Principles, Anti-Patterns, and Error Recovery

The depth behind transcript-capture: the full domain-principle set, the non-negotiable
AI discipline rules, the anti-pattern catalog, and error-recovery procedures.

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
