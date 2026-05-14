---
name: task-decomposition
description: Goal decomposition heuristics, dependency DAG construction, sub-agent assignment protocols, and multi-agent orchestration patterns. Use when breaking complex goals into sub-tasks, constructing execution plans, or coordinating work across multiple specialized agents.
---

# Task Decomposition

> "Divide each difficulty into as many parts as is feasible and necessary to resolve it."
> -- Rene Descartes, *Discourse on the Method*

## Core Philosophy

Decomposition is the fundamental act of engineering: taking something too large to hold in mind and breaking it into pieces small enough to reason about, execute, and verify independently.

The quality of a decomposition is not measured by how many sub-tasks it produces, but by three properties: **completeness** (the sub-tasks collectively achieve the goal), **independence** (each sub-task can be executed by a single agent without requiring another), and **verifiability** (each sub-task has an observable "done" criterion). A decomposition lacking any of these properties will produce coordination failures, redundant work, or unverifiable outcomes.

**Why DAGs, not lists:** A flat task list implies sequential execution and hides dependency information. A DAG makes dependencies explicit, reveals parallelization opportunities, identifies the critical path, and makes the impact of a single failure visible. Every decomposition should be a graph, not a list.

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

## Decomposition Strategies

### Strategy 1: Functional Decomposition

Split by capability, feature, or functional area. Use when the goal describes a system with identifiable, separately-implementable features whose domains map cleanly to different agent types. Apply by listing functional requirements → grouping into areas → creating one sub-task per area → extracting shared prerequisites (database schemas, shared types, configuration) as their own prerequisite sub-tasks.

```
Goal: "Add user authentication and an admin dashboard to the application"

  T1: Define auth data model (schemas, entities)         -> tdd-agent
  T2: Implement authentication flow (login, logout, JWT) -> tdd-agent [depends: T1]
  T3: Write auth integration tests                       -> test-generation-agent [depends: T2]
  T4: Build admin dashboard UI                           -> tdd-agent [depends: T1]
  T5: Review auth implementation for security            -> code-review-agent [depends: T2]
  T6: Document auth API and admin features               -> documentation-agent [depends: T2, T4]
```

### Strategy 2: Data-Flow Decomposition

Split by data transformation stages. Use when the goal describes a pipeline, ETL process, or data transformation where the work naturally flows from input to output through stages with clearly different technical concerns. Apply by tracing transformations from input to output → creating one sub-task per stage → identifying parallel branches.

```
Goal: "Build a pipeline that ingests sensor data, detects anomalies, and generates daily reports"

  T1: Implement data ingestion layer     -> tdd-agent
  T2: Build anomaly detection model      -> model-optimization-agent [depends: T1]
  T3: Configure sensor integrations      -> sensor-anomaly-agent [depends: T1]
  T4: Build report generation service    -> tdd-agent [depends: T2]
  T5: Generate test data and validate    -> test-generation-agent [depends: T1]
  T6: Document pipeline architecture     -> documentation-agent [depends: T2, T4]
```

### Strategy 3: Temporal Decomposition

Split by lifecycle phase. Use when the goal spans the full development lifecycle (design through deployment) and earlier phases produce artifacts that later phases consume. Apply by identifying phases (research, design, implement, test, deploy, document) → creating sub-tasks per phase → applying functional or data-flow decomposition within each oversized phase → looking for cross-phase parallelization (documentation often starts during implementation).

```
Goal: "Migrate the payment service from .NET Framework 4.8 to .NET 10"

  T1: Research breaking changes and compatibility  -> research-agent
  T2: Assess current codebase migration readiness  -> migration-orchestrator [depends: T1]
  T3: Audit dependencies for .NET 10 compatibility -> dependency-audit-agent [parallel: T2]
  T4: Execute migration plan                       -> migration-orchestrator [depends: T2, T3]
  T5: Generate regression test suite               -> test-generation-agent [depends: T4]
  T6: Review migrated code for issues              -> code-review-agent [depends: T4]
  T7: Update documentation for .NET 10             -> documentation-agent [depends: T4]
```

### Strategy 4: Risk-Ordered Decomposition

Split by risk level, isolating uncertain or high-risk work into early probe sub-tasks for fast validation. Use when the goal involves significant technical uncertainty or some parts may be infeasible. Design probe sub-tasks to fail fast, then gate the remaining plan on probe results.

```
Goal: "Integrate real-time video analytics on edge devices for the fleet"

  T1: Validate model runs on target hardware     -> model-optimization-agent [PROBE]
  T2: Benchmark inference latency on edge device  -> research-agent [PROBE, parallel: T1]
  T3: Test camera integration with SDK            -> sensor-anomaly-agent [PROBE, parallel: T1]
  --- GATE: All probes must pass before proceeding ---
  T4: Build optimized inference pipeline          -> model-optimization-agent [depends: T1, T2]
  T5: Implement edge capture and publish          -> tdd-agent [depends: T3]
  T6: Deploy to test fleet                        -> fleet-deployment-agent [depends: T4, T5]
  T7: Monitor and validate production metrics     -> sensor-anomaly-agent [depends: T6]
```

## Granularity Heuristics

| Split When | Stop When |
|-----------|-----------|
| Sub-task requires two different agents | Sub-task maps to a single agent and a single concern |
| Sub-task has multiple independent deliverables | Further splitting creates sub-tasks without meaningful "done" criteria |
| Description uses "and" connecting unrelated actions | Further splitting creates more coordination cost than execution cost |
| Cannot be completed in a single focused session | Three or more resulting sub-tasks would go to the same agent in sequence with no branching |
| Both autonomous and approval-required components exist | Sub-task is already a well-understood operation for the assigned agent |
| Failure of one part would not block the other | — |

## Dependency DAG Construction

Build the graph: for each sub-task T, list the inputs it requires → if an input is produced by another sub-task P, add edge P→T → if no sub-task produces a required input, flag as GAP. Verify every output is either consumed by a downstream sub-task or is a final deliverable.

**Cycle detection:** Run topological sort (Kahn's algorithm): compute in-degree for every node → queue all nodes with in-degree 0 → dequeue a node, add to sorted order, decrement successors' in-degrees → if sorted order is missing nodes, a cycle exists among the missing nodes.

**Critical path:** Assign effort weights (S=1, M=2, L=3) → find the longest path (sum of weights) → this is the minimum total duration → sub-tasks NOT on the critical path have slack. Focus monitoring on critical path sub-tasks.

## Sub-Agent Assignment Protocol

For each sub-task: identify the primary domain → select the agent whose domain best matches → if multiple agents fit, prefer tighter domain focus, then higher autonomy, then the agent already assigned other sub-tasks in the same track. If no agent matches, check if the sub-task can be decomposed further, merged with an adjacent sub-task that has a match, or the approach changed. If still unassignable, report the gap to the user — never assign to the wrong agent to avoid a gap.

## State Block

```
<decomposition-state>
mode: understand | decompose | assign | sequence | monitor
goal: [concise goal summary]
strategy: [functional | data-flow | temporal | risk-ordered | hybrid]
sub_tasks_total: [count]
sub_tasks_assigned: [count]
sub_tasks_unassignable: [count]
dag_valid: [true | false | not_constructed]
critical_path_length: [estimated effort units]
parallel_tracks: [count of independent parallel chains]
agents_involved: [list of agent names]
last_action: [what was just completed]
next_action: [what should happen next]
</decomposition-state>
```

State transitions: UNDERSTAND → DECOMPOSE (goal analyzed) → ASSIGN (DAG constructed) → SEQUENCE (all assigned or flagged) → MONITOR (plan approved) → COMPLETE. Any state can return to UNDERSTAND if the goal changes; MONITOR can return to DECOMPOSE if a failure requires re-planning.

## Output Templates

**Goal Analysis:** Stated goal | Deliverables (numbered) | Constraints (tech stack, conventions, timeline, scope) | Assumptions (with how to verify) | Open questions (blocking vs. non-blocking)

**Decomposition Plan:** Strategy + rationale | Sub-tasks table (ID, Name, Agent, Inputs, Outputs, Done Criteria, Effort S/M/L)

```
Dependency DAG example:
T1 ──> T2 ──> T5
  └──> T3 ──> T5
T4 (independent) ──> T6
T5 ──> T6

Critical Path: T1 → T2 → T5 → T6 (8 effort units)
Waves: [1] T1, T4 | [2] T2, T3 | [3] T5 | [4] T6
```

**Progress Report:** Wave N | table of ID, Name, Agent, Status (COMPLETED/IN_PROGRESS/BLOCKED), Notes | Critical path status | Blockers | Next wave

Full templates: `references/orchestration-patterns.md`

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

## Integration with Other Skills

- [Decomposition Heuristics](references/decomposition-heuristics.md) — Detailed strategies for when to split, when to stop, and which strategy fits which goal type
- [Orchestration Patterns](references/orchestration-patterns.md) — Multi-agent execution patterns, DAG construction, cycle detection, and failure recovery protocols
