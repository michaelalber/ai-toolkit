---
name: rpi-iterate
description: >
  RPI Iterate phase -- surgically updates an existing implementation plan based on feedback
  without starting over. Use for "/rpi-iterate feedback", "update the plan", "the plan needs
  to change because X", "adjust the plan for Y", "add Z to the plan".
---

# RPI Iterate

> "A plan is not a contract with the universe. It is a hypothesis about how to achieve a goal. When new information arrives, update the hypothesis."

> "The measure of intelligence is the ability to change."
> -- Albert Einstein (attributed)

## Core Philosophy

The Iterate phase exists because planning is not perfect on the first pass. Feedback, discovered constraints, or mid-implementation surprises may require plan changes. The iterate phase makes those changes surgically -- updating only what needs to change, preserving everything that is already correct or complete.

The alternative to /rpi-iterate is discarding the plan and starting over. That loses the work invested in clarifying questions, design decisions, and prior phases. Surgical iteration preserves that investment.

**Non-Negotiable Constraints:**
1. READ the existing plan fully before making any changes -- understand what is complete and what is pending
2. Make SURGICAL edits -- change only what the feedback requires; leave valid phases alone
3. PRESERVE completed checkboxes -- never uncheck phases that have already been executed
4. ASSESS downstream impact -- a change to Phase 2 may require updating Phases 3 and 4
5. Target-research ONLY new areas -- do not re-research the whole topic
6. ADD a change log -- document what changed and why at the bottom of the plan
7. OVERWRITE in place -- do not create a new plan file; keep the same path

## Domain Principles Table

| # | Principle | Description | Applied As |
|---|-----------|-------------|------------|
| 1 | **Read Before Touching** | You cannot make a surgical edit without understanding the full plan context. What looks like a simple change in Phase 2 may cascade into Phases 3-5. | Always read the complete plan before writing a single line of updates. |
| 2 | **Preserve the Completed** | Unchecking a completed phase tells the implement agent to re-execute it. Re-executing completed phases wastes time, potentially duplicates changes, and may conflict with the current codebase state. | Identify completed phases (checked boxes) and treat them as immutable during iteration. |
| 3 | **Surgical Over Wholesale** | Rewriting a valid phase because an adjacent phase changed is unnecessary churn. If Phase 3's changes don't affect Phase 5, leave Phase 5 alone. | Ask for each phase: "Does this feedback require changing this phase? If not, skip it." |
| 4 | **Downstream Impact Is Not Optional** | A change to Phase 2 that introduces a new type will affect every phase that uses that type. Skipping the downstream review creates a plan that will fail during implementation. | For every changed phase, check all subsequent phases for impact before finalizing the update. |
| 5 | **Target Research, Not Full Research** | Re-researching the entire topic in the iterate phase defeats the session isolation principle and fills the context with noise. Only research the new areas the feedback demands. | Spawn targeted subagents only for the specific files or components the feedback changes. |
| 6 | **Change Log Is Mandatory** | Without a change log, the implementer cannot tell what changed between the plan they reviewed and the plan they are executing. This creates confusion and reduces trust in the artifact. | Add a `## Change log` section at the bottom of the plan with: what changed, which phases, and why. |
| 7 | **Overwrite In Place** | A new plan file with a new name creates ambiguity: which plan is current? The iterate phase updates the existing artifact so there is always exactly one plan for a given feature. | Write updates to the same file path; never create a `v2` or `revised` variant. |
| 8 | **Scope Changes Need Rebuild** | If the feedback changes the fundamental approach (not just a detail), the affected phases need to be rebuilt, not patched. Patching an approach-level change creates internally inconsistent plans. | Distinguish feedback type: detail adjustment (surgical) vs. approach change (phase rebuild). Be explicit about which is happening. |
| 9 | **Small Feedback → Small Update** | The iterate phase should be proportionate to the feedback. A one-line feedback item should produce a minimal plan update, not a wholesale rewrite. | Match the scope of the update to the scope of the feedback. Report what changed and what didn't. |
| 10 | **Remind Before Resuming** | After updating the plan, the implementer needs to know to review before resuming. A plan update without a review prompt risks executing changes the user has not approved. | Always end iterate with: "Please review the updated plan before resuming /rpi-implement." |

## Workflow

```
PARSE
    Extract from $ARGUMENTS:
    - Plan file path (if provided) — otherwise use most recent in thoughts/shared/plans/
    - Feedback content (the rest of the argument)

        |
        v

READ
    Read the plan file completely.
    Identify:
    - Which phases have checked boxes (COMPLETE — do not touch)
    - Which phases are pending (may be updated)
    - The overall approach and scope boundaries

        |
        v

ASSESS
    For each pending phase:
    - Does this feedback require changing this phase?
    - If this phase changes, what downstream phases are affected?
    - Is this a detail adjustment or an approach change?

        |
        v

RESEARCH (if needed)
    If feedback requires understanding new code areas:
    Spawn targeted subagents ONLY for those areas (not the whole topic)
    @rpi-file-locator: "Find files related to: [specific new area]"
    @rpi-code-analyzer: "Analyze: [specific new component]"

        |
        v

UPDATE
    For each phase that needs updating:
    - Make targeted edits to change descriptions, file paths, success criteria
    - Rebuild phases where the approach has fundamentally changed
    - Leave unchanged phases exactly as-is
    - Update "What we're NOT doing" if scope changed
    Add ## Change log section at the bottom

        |
        v

REPORT
    Tell the user:
    - What changed (which phases, what specifically)
    - What stayed the same
    - Whether completed phases were preserved
    - Reminder: "Review before re-running /rpi-implement"
```

**Exit criteria:** Plan updated in place, change log added, completed phases preserved, user reminded to review.

## State Block

```
<rpi-iterate-state>
phase: PARSE | READ | ASSESS | RESEARCH | UPDATE | REPORT | COMPLETE
plan_path: thoughts/shared/plans/YYYY-MM-DD-description-slug.md
feedback_summary: [one-line description of the feedback]
phases_complete: [count of checked phases]
phases_to_update: [list of phase numbers]
downstream_affected: [list of phase numbers]
targeted_research_needed: true | false
status: in_progress | complete
</rpi-iterate-state>
```

## Output Templates

### Iteration Assessment Report (before making changes)

```
Plan: thoughts/shared/plans/YYYY-MM-DD-description-slug.md

Feedback: [summary of feedback]

Impact assessment:
- Phases complete (will not change): Phase 1, Phase 2
- Phases requiring update: Phase 3 — [reason]
- Downstream impact: Phase 4 — [what needs updating due to Phase 3 change]
- Phases unaffected: Phase 5

Approach change? [YES — rebuilding Phase 3 | NO — surgical update to Phase 3]

[If targeted research needed]: Spawning @rpi-code-analyzer for [specific area]...
```

### Change Log Entry

```markdown
## Change log

### [YYYY-MM-DD] — [brief description of feedback]

**Phases updated:**
- Phase 3: [What changed] — Reason: [why feedback required this change]
- Phase 4: [Downstream update] — Reason: [what Phase 3 change cascaded here]

**Phases preserved (complete):**
- Phase 1, Phase 2 — no changes

**Scope changes:**
- Added to "What we're NOT doing": [new exclusion if scope narrowed]
- Removed from "What we're NOT doing": [if scope expanded with rationale]
```

### Final Iterate Report

```
Plan updated: thoughts/shared/plans/YYYY-MM-DD-description-slug.md

Changes made:
- Phase 3: [what changed]
- Phase 4: [downstream update]

Unchanged:
- Phase 1, Phase 2 (complete — preserved)
- Phase 5 (unaffected by feedback)

Change log added at bottom of plan.

Next step: Review the updated plan, then resume /rpi-implement [plan path]
```

## AI Discipline Rules

### CRITICAL: Never Uncheck Completed Phases

**WRONG:**
```
User feedback: "Phase 3 needs to use a different file path."
Agent: Updating phases 1-5 to reflect the new approach...
[Unchecks Phase 1 and Phase 2 checkboxes]
```

**RIGHT:**
```
User feedback: "Phase 3 needs to use a different file path."
Agent: Phases 1 and 2 are already complete — leaving those unchanged.
Updating Phase 3 file path from X to Y.
Checking Phase 4 for downstream impact... Phase 4 references the same path; updating.
Phase 5 is unaffected.
```

### REQUIRED: Overwrite the Existing File

**WRONG:** Creating `thoughts/shared/plans/YYYY-MM-DD-description-v2.md`

**RIGHT:** Updating `thoughts/shared/plans/YYYY-MM-DD-description.md` in place.

### CRITICAL: Proportionate Changes

**WRONG:** User says "change the file path in Phase 3" → Agent rewrites the entire plan.

**RIGHT:** User says "change the file path in Phase 3" → Agent updates only the file path reference in Phase 3 and checks for downstream impact. Reports: "Updated Phase 3 file path. Phase 4 references the same file; updated there as well. Phases 1, 2, 5 unaffected."

## Anti-Patterns Table

| # | Anti-Pattern | Why It Fails | Correct Approach |
|---|-------------|-------------|-----------------|
| 1 | **Unchecking completed phases** | Causes re-execution of already-complete work; may duplicate changes or conflict with current state | Identify and preserve all checked phases before writing any updates |
| 2 | **Creating a new plan file** | Creates ambiguity about which is current; prior links and references break | Always update the existing plan file in place |
| 3 | **Re-researching the whole topic** | Fills context with noise; defeats session isolation | Spawn targeted subagents only for the specific new code areas the feedback requires |
| 4 | **Skipping downstream impact check** | Phase 3 update creates a type; Phase 4 uses the old type name; plan is internally inconsistent | For every changed phase, check all subsequent phases before finalizing |
| 5 | **Omitting the change log** | Implementer cannot tell what changed between review and execution; trust in the artifact decreases | Add ## Change log section to every iterate; list what changed and why |
| 6 | **Wholesale rewrite for small feedback** | Loses prior design decisions; requires re-review of the whole plan | Match update scope to feedback scope; report what changed vs. stayed the same |
| 7 | **Forgetting the review reminder** | User resumes /rpi-implement without reviewing the updated plan; may execute unreviewed changes | Always end with: "Review before resuming /rpi-implement" |
| 8 | **Treating approach changes as surgical** | Patching an approach-level change creates internally inconsistent plans | Distinguish detail adjustment (surgical) vs. approach change (phase rebuild); be explicit |
| 9 | **Not reading the plan before updating** | An update made without reading the context may conflict with other phases | Read the full plan before touching any section |
| 10 | **Not updating "What we're NOT doing"** | Scope change without updating the exclusion list; implementer doesn't know new boundaries | If feedback changes scope, update the exclusion list to match |

## Error Recovery

### No plan file found

```
Symptoms: No path provided in arguments and thoughts/shared/plans/ is empty or has no relevant plans

Recovery:
1. Tell the user no plan was found
2. List any plan files that DO exist in thoughts/shared/plans/ for disambiguation
3. Ask user to specify the plan path explicitly or confirm they want to create a new plan
4. Do NOT create a new plan in the iterate phase -- that belongs to /rpi-plan
```

### Feedback requires a fundamentally different approach for a completed phase

```
Symptoms: User feedback says Phase 1 (already complete) needs to use a completely different approach

Recovery:
1. Explain the situation clearly: "Phase 1 is already complete. Re-executing it would
   require reverting the existing changes first."
2. Ask the user: "Do you want to: (a) revert Phase 1 and re-execute with the new approach,
   or (b) proceed with the current Phase 1 and adapt subsequent phases?"
3. Wait for direction before making any changes
4. Document the decision in the change log
```

### Targeted research reveals the feedback is based on incorrect assumptions

```
Symptoms: User's feedback says "use the existing X interface" but targeted research shows X doesn't exist

Recovery:
1. Report the finding: "The research shows X does not exist in this codebase."
2. Present the actual options based on what does exist
3. Ask for clarified feedback before updating the plan
4. Do not update the plan based on the original (incorrect) feedback
```

## Integration with Other Skills

| Skill | Relationship |
|-------|-------------|
| `rpi-plan` | Produces the initial plan this skill updates. Substantial feedback may require a new /rpi-plan session rather than iteration. |
| `rpi-implement` | Consumes the updated plan. Must re-review after iterate before resuming implementation. |
| `rpi-research` | If iteration requires understanding an entirely new system area (not just targeted clarification), a full /rpi-research session may be warranted first. |
| `task-decomposition` | If iteration reveals the feature is larger than planned and should be split, use task-decomposition to break the plan into independent workstreams. |
