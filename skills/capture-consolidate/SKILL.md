---
name: capture-consolidate
description: Merges multiple capture documents from transcript-capture and email-capture into a unified intake bundle. Assigns canonical per-project REQ-XXX IDs, deduplicates overlapping requirements, surfaces cross-document contradictions for PM resolution, and produces a final capture bundle ready for spec generation.
---

# Capture Consolidate

> "The requirements you want are in five different documents.
> The requirements you need are the ones that appear in all five and don't contradict."

> "A requirement stated twice is not two requirements.
> A requirement stated twice differently is a problem."

## Core Philosophy

Individual capture sessions — whether from transcripts or email threads — produce fragmented snapshots. The same requirement may appear in different phrasing across documents. One document may say "users must log in with SSO" while another says "SAML authentication required." A stakeholder may have clarified in a follow-up email what they requested ambiguously in the meeting. And the same `DRAFT-001` ID from two separate capture sessions refers to two completely different items.

Consolidation is the phase that makes the capture bundle coherent enough for spec generation. It does three things: assigns canonical per-project REQ numbering, deduplicates semantically equivalent requirements, and surfaces contradictions between documents so the PM can resolve them before they become conflicting specs.

This is a PM-supervised process. The skill makes proposals; the PM decides. No requirement is dropped, merged, or renumbered without PM awareness.

**What this skill does:**
- Reads all `DRAFT-NNN` capture documents for a project
- Identifies duplicate and near-duplicate requirements across documents
- Surfaces contradictions for PM resolution
- Assigns canonical `REQ-XXX` per-project IDs
- Produces a unified capture bundle ready for Phase 2 spec generation

**What this skill does NOT do:**
- It does NOT write specs — that is the spec generation phase
- It does NOT resolve contradictions autonomously — PM resolves all conflicts
- It does NOT drop any requirement without PM approval
- It does NOT push to Confluence without explicit PM instruction

## Domain Principles

| # | Principle | Applied As |
|---|-----------|------------|
| 1 | **Per-project REQ numbering** | `REQ-XXX` IDs are sequential and unique within a project. The `REQ-001` registry is maintained in `captures/req-registry.md`. No two requirements in the project share an ID. |
| 2 | **Propose, do not decide** | The skill proposes duplicates and merges. The PM approves. A proposed merge that the PM rejects results in two separate REQs. |
| 3 | **Semantic deduplication, not textual** | "SSO login" and "SAML authentication" may be the same requirement. "User authentication" may be broader. The skill flags semantic similarity; PM determines equivalence. |
| 4 | **Source provenance is preserved** | The consolidated REQ records all source documents and their DRAFT IDs. Traceability runs from REQ-XXX back to the original capture session. |
| 5 | **Contradictions block consolidation** | If two documents give contradictory positions on the same topic, the skill flags the contradiction and pauses until the PM resolves it. It does not assign a REQ ID to an unresolved conflict. |
| 6 | **Nothing is deleted** | Superseded, merged, or rejected DRAFT items move to the Retired section of the registry. They are never deleted — they are part of the audit trail. |
| 7 | **Incremental consolidation is supported** | A project may run `capture-consolidate` after each capture session, not just once at the end. The skill reads the existing `req-registry.md` and continues from the last REQ number. |

## Knowledge Base Lookups

Use `search_knowledge` (grounded-code-mcp) before the DEDUPLICATE phase.

| Query | When to Call |
|-------|-------------|
| `search_knowledge("requirements traceability matrix source mapping")` | Before DEDUPLICATE — ground traceability approach in requirements engineering standards |
| `search_knowledge("requirements deduplication equivalence semantic matching")` | Before DEDUPLICATE — calibrate semantic similarity heuristics |
| `search_knowledge("acceptance criteria given when then format")` | Before OUTPUT — confirm output format for the consolidated bundle |

**Protocol:** Call at the start of DEDUPLICATE. Do not repeat for the same session.

## Workflow: The LOAD–DEDUPLICATE–RESOLVE–RENUMBER–OUTPUT Loop

### Phase 1: LOAD — Read All Capture Documents

**Actions:**

1. Ask the PM which project this consolidation covers
2. Read the `captures/` directory (or PM-specified location) and list all capture documents
3. Read the existing `req-registry.md` if one exists (this is an incremental run)
4. Extract all `DRAFT-NNN` items from all capture documents into a flat working list
5. Report the LOAD summary before proceeding

**LOAD Summary:**

```markdown
### LOAD Phase Summary

**Project**: [name]
**Capture documents found**: [N] — [list filenames]
**Existing req-registry.md**: [found / not found]
**Last REQ assigned** (if registry exists): REQ-[NNN]
**DRAFT items extracted**: [total count]
  - Requirements: [N]
  - Decisions: [N]
  - Commitments: [N]
  - Open questions: [N]
  - Contradictions (within documents): [N]

Proceeding to DEDUPLICATE.
```

### Phase 2: DEDUPLICATE — Identify Overlapping Requirements

**Actions:**

1. Call `search_knowledge("requirements deduplication equivalence semantic matching")` to calibrate
2. For each DRAFT requirement, compare it against all other DRAFT requirements for:
   - **Exact match:** Identical or near-identical phrasing
   - **Semantic match:** Same functional intent, different phrasing
   - **Subset match:** One requirement is a special case of another
   - **Conflict:** Same topic, contradictory positions
3. Group matching items into candidate merge sets
4. Present each candidate merge set to the PM for decision

**Similarity Classification:**

| Class | Description | PM Decision Required |
|-------|-------------|---------------------|
| `exact` | Same requirement, same phrasing. One document likely echoes the other. | Confirm merge |
| `semantic` | Same requirement, different phrasing. ("SSO" vs "SAML authentication") | Confirm equivalence and choose canonical phrasing |
| `subset` | One is a specific case of the other. ("Login with SSO" ⊆ "Authentication system") | Decide: keep both, or roll sub into parent |
| `conflict` | Same topic, different positions. Cannot merge — must resolve first. | Resolve contradiction before REQ assignment |
| `distinct` | Similar topic, different requirements. Appears related but is actually independent. | Confirm as two separate REQs |

**Per-Merge-Set Presentation:**

```markdown
---
### Candidate Merge Set M-[NNN]

**Similarity class**: [exact | semantic | subset | conflict | distinct]
**Items in this set**:

| DRAFT ID | Source Document | Statement | Uncertainty Tags |
|----------|----------------|-----------|-----------------|
| DRAFT-002 | 2026-01-10-kickoff.md | "Users must authenticate with SSO" | — |
| DRAFT-014 | 2026-01-15-email.md | "SAML-based authentication required" | — |

**Assessment**: These appear to be the same requirement stated in different terms.
If merged: [Proposed canonical phrasing: "System must support SSO/SAML authentication"]

---
**PM decision for M-[NNN]:**
- [ ] **Merge** — treat as one requirement, use proposed phrasing
- [ ] **Merge with revised phrasing** — [PM types revised phrasing here]
- [ ] **Keep separate** — these are two distinct requirements
- [ ] **Conflict** — mark as contradiction requiring resolution

Type your decision (merge / revise / separate / conflict):
```

**After all merge sets are reviewed, post a deduplication summary:**

```markdown
### DEDUPLICATE Phase Summary

**Merge sets reviewed**: [N]
**Merged**: [N] (reduced from [N] DRAFTs to [N] distinct requirements)
**Kept separate**: [N]
**Conflicts flagged**: [N] (must resolve before REQ assignment)

Proceeding to RESOLVE for flagged conflicts.
```

### Phase 3: RESOLVE — PM Resolves Cross-Document Contradictions

For each flagged conflict, present both positions and ask the PM to resolve.

**Conflict Presentation:**

```markdown
---
### Conflict C-[NNN] — Resolution Required

**Topic**: [What this conflict is about]

| Position | Statement | Source Document | Date | Speaker / Sender |
|----------|-----------|----------------|------|-----------------|
| A | "[exact quote or statement A]" | [filename] | [date] | [speaker/sender] |
| B | "[exact quote or statement B]" | [filename] | [date] | [speaker/sender] |

**Why this matters**: Implementing A and B together would [describe the conflict].

---
**PM resolution for C-[NNN]:**
- [ ] **Position A is current** — B is superseded
- [ ] **Position B is current** — A is superseded
- [ ] **Both are valid** — they apply to different scenarios (PM explains below)
- [ ] **Neither is final** — this is still open (becomes an open question)

PM explanation (required for "Both" or "Neither"):
```

**Conflicts block REQ assignment.** The RESOLVE phase must complete before RENUMBER begins. If the PM defers a conflict ("we'll figure this out later"), it is logged as an open question in the consolidated output — not assigned a REQ ID.

### Phase 4: RENUMBER — Assign Canonical REQ-XXX IDs

**Actions:**

1. Load the current `req-registry.md` to find the last-used REQ number (or start at `REQ-001`)
2. For each accepted requirement (merged or individual), assign the next sequential `REQ-XXX`
3. Record the mapping: `REQ-XXX ← DRAFT-NNN (source doc) + DRAFT-NNN (source doc) ...`
4. Record superseded DRAFTs in the Retired section
5. Update `req-registry.md`

**REQ ID assignment is sequential, never recycled.** A retired REQ ID (from a deleted or superseded requirement) is never reused — it stays in the Retired section permanently.

**Renumber Log:**

```markdown
### RENUMBER Phase Summary

**REQs assigned this session**: [N]
  Starting REQ: REQ-[NNN]
  Ending REQ:   REQ-[NNN]
**DRAFTs retired**: [N]
**Open questions retained without REQ**: [N]

Proceeding to OUTPUT.
```

### Phase 5: OUTPUT — Produce Consolidated Capture Bundle

Produce two outputs:
1. **`captures/consolidated-[YYYY-MM-DD].md`** — The unified capture document for this consolidation run
2. **`captures/req-registry.md`** — The running REQ registry for the project (create or update)

**If Confluence output is requested:** Ask for target space and parent page before publishing. Default to local files.

## State Block

```
<capture-consolidate-state>
phase: load | deduplicate | resolve | renumber | output
project: [project name]
capture_docs: [list of filenames]
draft_items_total: N
merge_sets_total: N
merge_sets_reviewed: N
merged: N
kept_separate: N
conflicts_total: N
conflicts_resolved: N
conflicts_pending: N
last_req_before: REQ-[NNN] | none
last_req_after: REQ-[NNN] | pending
output_path_consolidated: [path or pending]
output_path_registry: [path or pending]
last_action: [what was just done]
next_action: [what should happen next]
</capture-consolidate-state>
```

## Output Templates

### Consolidated Capture Document

```markdown
# Consolidated Capture Bundle — [Project / Client] — [Date]

> **Capture method**: capture-consolidate skill
> **Source documents**: [list of filenames]
> **Consolidated by**: [PM name] on [date]
> **REQ range this session**: REQ-[NNN] – REQ-[NNN]

## Summary

[2–3 sentences describing the scope of this consolidation: what meetings/threads were covered, date range, number of requirements.]

## Participants (across all sources)

- [Name] ([Role]) — [authoritative | non-authoritative]

## Key Decisions

- [Decision statement] — *Sources: [list of source docs and dates]*

## Requirements

| REQ ID | Statement | Source Documents | Uncertainty | Status |
|--------|-----------|-----------------|-------------|--------|
| REQ-001 | [Statement] | [filename], [filename] | — | Active |
| REQ-002 | [Statement] | [filename] | [UNCERTAIN] | Active |
| REQ-003 | [Statement] | [filename] | [NEEDS-CLARIFICATION] | Active |

## Commitments

| REQ ID | Statement | Source | Due Date |
|--------|-----------|--------|----------|
| REQ-010 | [Commitment] | [sender, filename] | [date or TBD] |

## Open Questions

| # | Question | Source | Assigned To | Status |
|---|----------|--------|-------------|--------|
| OQ-001 | [Question] | [filename] | [Name or TBD] | Open |
| OQ-002 | [Unresolved conflict: topic] | [filename], [filename] | [PM] | Pending resolution |

## Action Items

- [ ] [Action] — Owner: [Name] — Due: [Date or TBD]

---

## Provenance Map

> Maps REQ-XXX IDs back to their DRAFT source IDs and documents.

| REQ ID | Merged From | Source Documents |
|--------|-------------|-----------------|
| REQ-001 | DRAFT-002, DRAFT-014 | 2026-01-10-kickoff.md, 2026-01-15-email.md |
| REQ-002 | DRAFT-007 | 2026-01-10-kickoff.md |
```

### REQ Registry (`captures/req-registry.md`)

```markdown
# REQ Registry — [Project / Client]

> Per-project requirement ID registry. Updated after each capture-consolidate session.
> Never delete entries — retire them to the Retired section.

## Active Requirements

| REQ ID | Statement (short) | Source Documents | Assigned Date | Status |
|--------|-------------------|-----------------|---------------|--------|
| REQ-001 | SSO/SAML authentication | kickoff.md, email.md | 2026-01-20 | Active |
| REQ-002 | Weekly summary report | kickoff.md | 2026-01-20 | Active |

## Retired Requirements

> Merged, superseded, or rejected DRAFTs. Never recycled.

| REQ / DRAFT ID | Statement (short) | Reason Retired | Superseded By | Retired Date |
|---------------|-------------------|---------------|---------------|--------------|
| DRAFT-001 | "SSO login required" | Merged into REQ-001 | REQ-001 | 2026-01-20 |
| DRAFT-014 | "SAML authentication" | Merged into REQ-001 | REQ-001 | 2026-01-20 |

## Registry Metadata

- **Last REQ assigned**: REQ-[NNN]
- **Last updated**: [date]
- **Consolidation sessions**: [N]
```

### Session Opening

```markdown
## Capture Consolidate Session

I will merge your capture documents into a unified bundle and assign canonical REQ-XXX IDs.

**How this works:**

1. I read all capture documents for the project and the existing REQ registry (if any)
2. I identify duplicate and near-duplicate requirements across documents
3. I present each candidate merge set to you for a decision — merge, keep separate, or flag as conflict
4. You resolve any cross-document contradictions
5. I assign canonical REQ-XXX IDs and produce the consolidated capture bundle

To begin, which project is this consolidation for, and where are the capture documents?
(Default location: captures/ in the project root)

<capture-consolidate-state>
phase: load
project: awaiting input
capture_docs: awaiting input
draft_items_total: 0
merge_sets_total: 0
merge_sets_reviewed: 0
merged: 0
kept_separate: 0
conflicts_total: 0
conflicts_resolved: 0
conflicts_pending: 0
last_req_before: none
last_req_after: pending
output_path_consolidated: pending
output_path_registry: pending
last_action: Session opened
next_action: PM provides project name and capture document location
</capture-consolidate-state>
```

## AI Discipline Rules

### Propose Merges, Never Execute Them

Every proposed merge is shown to the PM with both source statements before any action is taken. The skill never silently merges two requirements.

```
WRONG: "I merged DRAFT-002 and DRAFT-014 because they're the same thing."
RIGHT: "DRAFT-002 and DRAFT-014 appear to be the same requirement phrased differently.
        Proposed merge: 'System must support SSO/SAML authentication.'
        Do you want to merge these, keep them separate, or rephrase the merged version?"
```

### Contradictions Block Progress

An unresolved contradiction cannot receive a REQ ID. The skill does not work around this by assigning the ID to one position and silently dropping the other. Both positions stay in the open questions section until the PM resolves them.

### Source Provenance Travels With Every REQ

The consolidated document and the REQ registry both record the DRAFT-NNN sources for every REQ. This is the audit trail that lets a reviewer trace REQ-042 back to what was actually said in the kickoff meeting.

### Semantic Similarity Is a Proposal, Not a Finding

The skill may flag two requirements as semantically similar. The PM decides whether they are actually equivalent. "Authentication" and "SSO" are related — they may not be the same requirement. Surface the candidate; let the PM adjudicate.

### Never Recycle REQ IDs

A REQ ID assigned to a retired requirement stays in the Retired section permanently. It is never reused. This preserves the integrity of any external references (Jira tickets, specs) that used that ID.

## Anti-Patterns

| Anti-Pattern | Description | Why It Fails | What to Do Instead |
|---|---|---|---|
| **Silent merging** | Merging semantically similar requirements without PM review | Two different stakeholders may have intended different things; "authentication" and "SSO" are not always synonyms | Present every candidate merge to PM before acting |
| **Conflict suppression** | Choosing one position in a contradiction and not surfacing the other | The losing position may be the one the stakeholder intended; unresolved conflicts become disputed scope | Flag all contradictions; pause until PM resolves |
| **ID recycling** | Reusing a REQ ID after the original requirement is retired | External references (Jira, specs) point to the old ID; reuse creates ambiguity about which requirement is meant | Retire IDs to the Retired section; never reuse them |
| **Single-session assumption** | Treating consolidation as a one-time, end-of-capture activity | Capture happens incrementally; the registry must support being updated after each session | Check for existing `req-registry.md` on every run; continue from the last REQ number |
| **Confluence-first output** | Publishing directly to Confluence without PM review of the local draft | PM loses review opportunity before requirements enter the spec pipeline | Default to local files; ask for explicit instruction before Confluence publish |
| **Dropping deferred conflicts** | Removing an unresolved conflict from the output because "it will be figured out later" | The conflict becomes invisible and surfaces later as a spec discrepancy or implementation disagreement | Retain unresolved conflicts as open questions in the output with explicit `OQ-XXX` IDs |

## Error Recovery

### No Capture Documents Found

The `captures/` directory is empty or no `DRAFT-NNN` items were found.

**Recovery:**
1. Alert the PM: "No capture documents were found in [location]. Run `transcript-capture` or `email-capture` first to produce DRAFT-NNN items, then re-run consolidation."
2. If the PM provides an alternate location, search there

### REQ Registry Is Corrupted or Missing REQ Assignments

**Recovery:**
1. Alert the PM: "The REQ registry appears to have a gap or inconsistency at [location]."
2. Show the PM the suspected conflict (e.g., duplicate REQ IDs, gap in sequence)
3. Propose a resolution: "I can repair the registry by [proposed action]. Shall I proceed?"
4. Wait for PM instruction. Do not repair without approval.

### Very Large DRAFT Item Set (>100 items)

**Recovery:**
1. Report the count to the PM
2. Propose a phased approach: "There are 143 DRAFT items. I suggest we deduplicate by topic area. Which area should we start with?"
3. Complete one area at a time; update the registry incrementally

### PM Wants to Split a Merged REQ After Consolidation

A REQ that was merged in a previous session needs to be split.

**Recovery:**
1. Retire the merged REQ (add to Retired section)
2. Create two new REQs from the original DRAFT sources
3. Assign the next two available REQ IDs
4. Note in the registry: "REQ-[N] retired — split into REQ-[A] and REQ-[B] on [date]"

## Integration with Other Skills

- **`transcript-capture`** — Produces `DRAFT-NNN` capture documents from meeting transcripts. This skill is the downstream consumer.
- **`email-capture`** — Produces `DRAFT-NNN` capture documents from email threads and documents. This skill is the downstream consumer.
- **`jira-review`** — After consolidation produces `REQ-XXX` requirements, use `jira-review` to assess readiness for Jira ticket decomposition.
- **`task-decomposition`** — Use after `jira-review` to decompose consolidated requirements into Jira-sized tickets.
- **`confluence-guide-writer`** — If the consolidated capture bundle should be published to Confluence as a stakeholder-facing artifact, use this skill after PM approval.
