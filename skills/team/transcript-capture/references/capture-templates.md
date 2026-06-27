# Capture Templates

The fill-in templates for every phase of the INTAKE–FILTER–REVIEW–OUTPUT loop.
Load this file when you reach the phase that needs the template.

## Intake Template (Phase 1: INTAKE)

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

### Capture Sensitivity Levels

| Level | Use When | What It Includes |
|-------|----------|-----------------|
| `standard` | Clear, well-scoped requirements meeting | Explicit requirements, firm decisions, named action items, clear open questions |
| `thorough` | Exploratory or early-stage meeting | All of the above + uncertain statements, implied preferences, raised concerns without resolution |

## Per-Block Presentation Format (Phase 3: REVIEW)

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

## Capture Document (Phase 4: OUTPUT)

Default output path: `captures/[YYYY-MM-DD]-[meeting-slug].md`

**Header:**
`# [Meeting Name] — [Date] — [Project / Client]`

**Sections:**
- **Participants**
- **Summary** — 2–3 sentences
- **Key Decisions** — statement + source attribution
- **Requirements Extracted** — `DRAFT-NNN` + statement + source, with `⚠ [UNCERTAIN]` or `🔍 [NEEDS-CLARIFICATION]` tags
- **Open Questions** — question + owner
- **Action Items** — owner + due date
- **Drop Log** — Block / Score / Reason / PM Decision

## Session Opening

Explain the 4-phase process (intake → filter → review → output), state that nothing is
silently dropped, ask for transcript location, meeting purpose, and project. Emit the initial
`<transcript-capture-state>` block with `phase: intake`.
