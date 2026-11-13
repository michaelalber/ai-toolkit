# task-decomposition — operating guide

Depth relocated from SKILL.md; load it when the Workflow points here.

## Domain Principles

| # | Principle | Description |
|---|-----------|-------------|
| 1 | **Completeness Over Elegance** | A decomposition that covers all aspects with some redundancy beats an elegant one that misses a requirement. Trace every deliverable to at least one sub-task. |
| 2 | **One Agent, One Sub-Task** | Each sub-task should be executable by exactly one agent. If a sub-task requires two agents to collaborate simultaneously, it is not decomposed enough. |
| 3 | **Explicit Dependencies Only** | If sub-task B needs output from A, that dependency must be declared in the DAG. Implicit ordering is a guess, not a dependency. |
| 4 | **Verifiable Completion** | Every sub-task must have a "done" criterion verifiable without subjective judgment. "Code is clean" is not verifiable. "All tests pass and code review agent reports zero critical findings" is. |
| 5 | **Appropriate Granularity** | Decompose until each sub-task is a coherent unit for a single session of a single agent. Finer creates coordination overhead; coarser creates ambiguity. |
| 6 | **Risk-Aware Ordering** | When the dependency graph allows flexibility, prefer to execute high-risk sub-tasks early. Early failure is cheaper than late failure. |
| 7 | **Recoverable Failures** | Design decompositions so a single sub-task failure does not cascade into total plan failure. Prefer independent parallel tracks over a single serial chain. |
| 8 | **Stable Interfaces Between Sub-Tasks** | The inputs and outputs of each sub-task form a contract. Define these contracts before execution and do not change them mid-execution without re-planning. |

## Anti-Patterns

| Anti-Pattern | Why It Fails | Correct Approach |
|--------------|-------------|------------------|
| **Flat List Decomposition** | Hides dependencies, prevents parallelization, obscures failure impact | Always construct a DAG; document explicit "no dependencies" when truly flat |
| **Over-Decomposition** | Coordination overhead exceeds execution cost; dozens of tiny tasks create tracking work | Stop when each sub-task is one agent, one concern, one session |
| **Wishful Assignment** | Assigning to an agent whose domain does not match, hoping it figures it out | Verify domain alignment; report gaps honestly |
| **Implicit Dependencies** | Assuming sub-tasks run in a "reasonable" order without declaring why | Make every dependency explicit with the input/output rationale |
| **Monolithic Decomposition** | First task is "analyze everything", last is "implement everything" | Each sub-task is a single coherent unit, not a lifecycle phase with unbounded work |
| **Ignoring the Critical Path** | Treating all sub-tasks as equally urgent | Identify the critical path and focus monitoring attention on it |
| **Single-Chain Plans** | All sub-tasks in a serial chain with no parallelization | Look for independent sub-tasks; most plans have at least two parallel tracks |

## AI Discipline Rules

**The plan is the product — treat it with the same rigor as code.** Every sub-task name should be action-oriented. Every dependency should have a rationale. Every done criterion should be verifiable. If an agent can execute a sub-task without asking clarifying questions, the plan is done.

**Dependencies are constraints, not suggestions.** If B depends on A, B cannot start until A completes. Do not soften this by saying "B can probably start if we assume A will succeed." Dependencies exist because outputs flow between tasks.

**Report gaps honestly — never assign to the wrong agent to avoid a gap.** An honest "no agent available" is infinitely more valuable than a silent bad assignment. Gaps are actionable information; bad assignments are hidden failures.

**Monitor actively — a plan that is not tracked is a wish.** Verify done criteria before unblocking dependents. Assess the blast radius immediately when a sub-task fails.

## Error Recovery

**Decomposition produces too many sub-tasks** (> 15): Merge sub-tasks assigned to the same agent in sequence. Look for sub-tasks that are steps within a single agent's internal protocol (the agent handles them). Target 5–12 sub-tasks for most goals. If genuinely more are needed, group into named tracks and present tracks as the primary view.

**User rejects the plan** ("not what I meant"): Do not defend the plan — ask what aspect is wrong. Revisit UNDERSTAND: was the goal misinterpreted? Revisit granularity: is the plan too detailed? Offer two detail levels. Iterate until the user approves.

**Sub-task produces unexpected output**: Check the done criteria — did the sub-agent satisfy them? If yes but output is still wrong, the done criteria were insufficient; revise them. Assess whether downstream sub-tasks need revised inputs. Re-plan the affected DAG portion.
