# Impact Assessment Guide

How to determine which phases are affected by a given feedback change during /rpi-iterate.

## The impact assessment process

Before touching the plan, read it completely and map the dependency graph:

```
Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5
                      ↑
               [feedback changes this]
```

Ask for each subsequent phase: "Does Phase 3's change affect what Phase 4 or Phase 5 need to do?"

## Dependency types that create cascading impact

### Type A: New type introduced

If feedback causes Phase N to introduce a new type (class, interface, enum):
- Every subsequent phase that uses that type needs updating
- Tests that mock or instantiate that type need updating

**Check for:** Type names in subsequent phases' change descriptions.

### Type B: File path changed

If feedback changes a file path in Phase N:
- Every subsequent phase that references that file needs updating
- The "Code references" section in the plan header may need updating

**Check for:** The old file path in every subsequent phase's change descriptions.

### Type C: Method signature changed

If feedback changes a method signature in Phase N:
- Every phase that calls that method needs updating
- Test phases that verify that method's behavior need updating

**Check for:** The method name in subsequent phases and test phases.

### Type D: Scope boundary changed

If feedback changes what is in or out of scope:
- Update the "Desired end state" section
- Update the "What we're NOT doing" section
- Review all phases for changes that now fall outside the new scope boundary
- Review the testing strategy section

### Type E: Infrastructure/registration change

If feedback changes how a component is registered or wired in DI:
- Update any phase that references the registration point
- Update any test phase that sets up the same DI configuration

## Determining: detail adjustment vs. approach change

### Detail adjustment (surgical edit)
- Wrong file path → correct file path
- Wrong method name → correct method name
- Missing `using` statement noted → add to plan
- Wrong test assertion type → correct assertion

**Action:** Edit the specific line(s). Leave the rest of the phase intact.

### Approach change (phase rebuild)
- Wrong pattern used → use a different pattern
- Wrong layer for the change → move to a different layer
- Wrong infrastructure component → use a different service
- Sequencing is wrong → phases need reordering

**Action:** Rebuild the affected phase(s). Clearly state what changed and why in the change log.

## Quick assessment checklist

Before updating the plan, answer these questions:

```
1. Which phase(s) does the feedback directly target?
   → [list phase numbers]

2. Are any of these phases already complete (checked)?
   → [YES: cannot change these | NO: proceed]

3. For each directly targeted phase, what changes?
   → [describe changes per phase]

4. Does any targeted phase introduce or change:
   - A type name? → check all subsequent phases
   - A file path? → check all subsequent phases
   - A method signature? → check all subsequent phases
   - A DI registration? → check all subsequent phases

5. Is this a detail adjustment or an approach change?
   → [detail: surgical edit | approach: phase rebuild]

6. Does the feedback change the scope boundary?
   → [YES: update Desired end state and What we're NOT doing | NO: skip]

7. Does the feedback require researching new code areas?
   → [YES: spawn targeted subagents for those areas | NO: skip]
```

## Assessing completed phases

Completed phases (with checked boxes) cannot be changed. But feedback may reveal that the implementation needs adjustment because of what was already done.

In this situation:
1. Note the conflict in the change log
2. Add a new phase (or modify a pending phase) to address the adjustment needed
3. Do NOT uncheck the completed phase
4. If the adjustment requires reverting the completed work: stop and tell the user; this is outside the iterate scope

Example:
```
Phase 1 (complete): Added IEmailService injection to ReviewHandler
Feedback: "Use IEmailQueueService, not IEmailService"

Cannot change Phase 1 (complete). Options:
Option A: Add Phase 1b to update the injection (before Phase 2)
Option B: Update Phase 2 to replace IEmailService with IEmailQueueService

Tell user: "Phase 1 is already complete and injected IEmailService. To use
IEmailQueueService instead, Phase 1 would need to be reverted. Shall I add a
Phase 1b to update the injection, or would you prefer to manually revert Phase 1
and then re-execute from the beginning?"
```

## When to recommend a new /rpi-plan instead of /rpi-iterate

Recommend starting fresh when:
- More than 50% of the pending phases need to be rebuilt
- The fundamental approach (not just details) is wrong
- The feedback implies the research artifact was wrong and needs to be re-researched
- Completed phases conflict with the needed approach and would need to be reverted

In these cases, the iterate overhead is higher than starting a new plan session.
