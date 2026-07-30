# REQ Registry Guide — Capture Consolidate

A reference for managing the `req-registry.md` file across consolidation sessions. Use during the RENUMBER and OUTPUT phases.

---

## Purpose of the REQ Registry

The REQ registry (`captures/req-registry.md`) is the authoritative record of all requirement IDs for a project. It serves three purposes:

1. **ID assignment authority** — prevents duplicate REQ IDs across consolidation sessions
2. **Audit trail** — records what happened to every DRAFT and REQ (merged, superseded, retired)
3. **External reference anchor** — Jira tickets, specs, and test cases reference REQ IDs; the registry is the source of truth when those references are questioned

---

## Registry Structure

```markdown
# REQ Registry — [Project / Client]

> Per-project requirement ID registry. Updated after each capture-consolidate session.
> Never delete entries — retire them to the Retired section.
> Last REQ assigned: REQ-[NNN]
> Last updated: [date]
> Consolidation sessions: [N]

## Active Requirements

| REQ ID | Statement (short) | Source Documents | Assigned Date | Status |
|--------|-------------------|-----------------|---------------|--------|
| REQ-001 | ... | ... | ... | Active |

## Retired Requirements

> Merged, superseded, or rejected DRAFTs. IDs are never reused.

| REQ / DRAFT ID | Statement (short) | Reason Retired | Superseded By | Retired Date |
|---|---|---|---|---|
| DRAFT-001 | ... | Merged into REQ-001 | REQ-001 | ... |
```

---

## ID Assignment Rules

### Sequential, Never Recycled

REQ IDs are assigned sequentially: REQ-001, REQ-002, REQ-003, ...

A REQ ID assigned to a retired requirement is never reused. The retired ID stays in the Retired section permanently. This preserves the integrity of any Jira tickets or spec documents that referenced the old ID.

**Why this matters:** If REQ-007 is retired and REQ-007 is later reused for a different requirement, any Jira ticket that says "implements REQ-007" now has an ambiguous meaning. Permanent retirement eliminates this.

### Starting a New Project

Begin at REQ-001. Check that no `req-registry.md` exists for the project before creating one.

### Incremental Sessions

On each subsequent consolidation session:
1. Read the existing `req-registry.md`
2. Find the last assigned REQ ID (the `Last REQ assigned` metadata field)
3. Continue from the next number

**Never restart from REQ-001 on an existing project.** If the registry is missing, reconstruct it from the existing consolidated capture documents before assigning new IDs.

---

## Source Provenance Tracking

Every REQ entry records which DRAFT items it was derived from and which capture documents those DRAFTs came from.

**Format:**

| REQ ID | Merged From | Source Documents |
|--------|-------------|-----------------|
| REQ-001 | DRAFT-002, DRAFT-014 | 2026-01-10-kickoff.md, 2026-01-15-email.md |
| REQ-002 | DRAFT-007 | 2026-01-10-kickoff.md |

**Why this matters:** When a stakeholder challenges a requirement in a spec review ("Where did REQ-042 come from?"), the provenance map lets you trace it back to the exact meeting or email where it was stated.

---

## Retirement Reasons

Use these standard retirement reasons in the Retired section:

| Reason | When to Use |
|---|---|
| `Merged into [REQ-NNN]` | Two DRAFT items were consolidated into a single REQ |
| `Superseded by [REQ-NNN]` | A later statement replaced an earlier one |
| `Duplicate of [REQ-NNN]` | Exact duplicate; only one REQ assigned |
| `Rejected by PM` | PM decided this item is not a requirement |
| `Out of scope` | PM confirmed item is outside the project boundary |
| `Deferred to future phase` | Valid requirement, not in current scope |
| `Split into [REQ-NNN] and [REQ-NNN]` | A merged REQ was later found to be two distinct requirements |

---

## Splitting a Previously Merged REQ

Occasionally a merged REQ needs to be split after the fact (e.g., "SSO and SAML turn out to be two separate features for different user types").

**Protocol:**
1. Add the original merged REQ to the Retired section with reason: `Split into REQ-[A] and REQ-[B] on [date]`
2. Assign two new sequential REQ IDs for the split items
3. Record both new REQs in Active with provenance pointing back to the same DRAFT sources as the retired REQ
4. Update the provenance map

---

## Deferred Conflicts

Contradictions that the PM has not yet resolved are not assigned REQ IDs. They are retained as Open Questions in the consolidated document with `OQ-NNN` IDs.

When the PM later resolves a deferred conflict:
1. Assign a REQ ID to the resolved position
2. Add the rejected position to the Retired section with reason: `Conflict resolved — superseded by REQ-[NNN] on [date]`
3. Update the consolidated document and registry

**Never assign a REQ ID to an unresolved contradiction.** A REQ ID implies the requirement is confirmed and can be implemented. Unconfirmed items must not receive REQ IDs.

---

## Registry Integrity Checks

Run these checks before closing a consolidation session:

- [ ] No duplicate REQ IDs in the Active section
- [ ] No REQ IDs appear in both Active and Retired sections
- [ ] The `Last REQ assigned` metadata field matches the highest REQ number in the Active section
- [ ] Every retired DRAFT ID appears in the Provenance Map of an Active REQ (or is explicitly retired without a successor)
- [ ] All unresolved contradictions are in Open Questions, not in the Active Requirements table
- [ ] `Consolidation sessions` counter has been incremented
- [ ] `Last updated` date reflects today's date
