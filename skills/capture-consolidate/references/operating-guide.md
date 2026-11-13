# capture-consolidate — operating guide

Depth relocated from SKILL.md; load it when the Workflow points here.

## Domain Principles

| # | Principle | Applied As |
|---|-----------|------------|
| 1 | **Per-project REQ numbering** | `REQ-XXX` IDs are sequential and unique within a project. The `REQ-001` registry is maintained in `captures/req-registry.md`. No two requirements share an ID. |
| 2 | **Propose, do not decide** | The skill proposes duplicates and merges. The PM approves. A proposed merge the PM rejects results in two separate REQs. |
| 3 | **Semantic deduplication, not textual** | "SSO login" and "SAML authentication" may be the same requirement. The skill flags semantic similarity; PM determines equivalence. |
| 4 | **Source provenance is preserved** | The consolidated REQ records all source documents and their DRAFT IDs. Traceability runs from REQ-XXX back to the original capture session. |
| 5 | **Contradictions block consolidation** | If two documents give contradictory positions on the same topic, the skill flags the contradiction and pauses until the PM resolves it. No REQ ID is assigned to an unresolved conflict. |
| 6 | **Nothing is deleted** | Superseded, merged, or rejected DRAFT items move to the Retired section of the registry. Never deleted — they are part of the audit trail. |
| 7 | **Incremental consolidation is supported** | A project may run `capture-consolidate` after each capture session. The skill reads the existing `req-registry.md` and continues from the last REQ number. |

## Knowledge Base Lookups

| Query | When to Call |
|-------|-------------|
| `search_knowledge("requirements traceability matrix source mapping")` | Before DEDUPLICATE — ground traceability approach in requirements engineering standards |
| `search_knowledge("requirements deduplication equivalence semantic matching")` | Before DEDUPLICATE — calibrate semantic similarity heuristics |
| `search_knowledge("acceptance criteria given when then format")` | Before OUTPUT — confirm output format for the consolidated bundle |

Call at the start of DEDUPLICATE. Do not repeat for the same session.
