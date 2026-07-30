# Discipline & Recovery — Capture Consolidate

AI discipline rules, anti-patterns, and error-recovery procedures for consolidation runs.
Load this when enforcing process discipline or when a run hits an exception condition.

---

## AI Discipline Rules

**Propose merges, never execute them.** Every proposed merge is shown to the PM with both source statements before any action is taken. Never silently merge two requirements. Present candidate → PM decides → record decision.

**Contradictions block progress.** An unresolved contradiction cannot receive a REQ ID. Do not work around this by assigning the ID to one position and silently dropping the other. Both positions stay in the open questions section until the PM resolves them.

**Source provenance travels with every REQ.** The consolidated document and the REQ registry both record the DRAFT-NNN sources for every REQ. This is the audit trail that lets a reviewer trace REQ-042 back to what was actually said in the kickoff meeting.

**Semantic similarity is a proposal, not a finding.** The skill may flag two requirements as semantically similar. The PM decides whether they are actually equivalent. "Authentication" and "SSO" are related — they may not be the same requirement.

**Never recycle REQ IDs.** A REQ ID assigned to a retired requirement stays in the Retired section permanently. It is never reused — this preserves the integrity of any external references (Jira tickets, specs) that used that ID.

---

## Anti-Patterns

| Anti-Pattern | Why It Fails | What to Do Instead |
|---|---|---|
| **Silent merging** | Two different stakeholders may have intended different things | Present every candidate merge to PM before acting |
| **Conflict suppression** | The losing position may be the one the stakeholder intended | Flag all contradictions; pause until PM resolves |
| **ID recycling** | External references point to the old ID; reuse creates ambiguity | Retire IDs to the Retired section; never reuse them |
| **Single-session assumption** | Capture happens incrementally; the registry must be updatable | Check for existing `req-registry.md` on every run |
| **Confluence-first output** | PM loses review opportunity before requirements enter the spec pipeline | Default to local files; ask for explicit instruction before publishing |
| **Dropping deferred conflicts** | The conflict becomes invisible and surfaces later as a spec discrepancy | Retain unresolved conflicts as open questions with explicit `OQ-XXX` IDs |

---

## Error Recovery

**No capture documents found**: Alert the PM — "No DRAFT-NNN items found in [location]. Run `transcript-capture` or `email-capture` first, then re-run consolidation." If the PM provides an alternate location, search there.

**REQ registry corrupted or has gaps**: Alert the PM, show the suspected conflict (duplicate IDs, gap in sequence), and propose a resolution. Wait for PM instruction before repairing.

**Very large DRAFT item set (> 100 items)**: Report the count to the PM. Propose phased consolidation by topic area — "There are 143 DRAFT items. Which area should we start with?" Complete one area at a time and update the registry incrementally.

**PM wants to split a merged REQ after consolidation**: Retire the merged REQ, create two new REQs from the original DRAFT sources, assign the next two available REQ IDs, and note in the registry: "REQ-[N] retired — split into REQ-[A] and REQ-[B] on [date]."
