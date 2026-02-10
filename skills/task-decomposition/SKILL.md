---
name: task-decomposition
description: Goal decomposition heuristics, dependency DAG construction, sub-agent assignment protocols, and multi-agent orchestration patterns. Use when breaking complex goals into sub-tasks, constructing execution plans, or coordinating work across multiple specialized agents.
---

# Task Decomposition

> "Divide each difficulty into as many parts as is feasible and necessary to resolve it."
> -- Rene Descartes, *Discourse on the Method*

## Core Philosophy

Decomposition is the fundamental act of engineering: taking something too large to hold in mind and breaking it into pieces small enough to reason about, execute, and verify independently. This skill provides the heuristics, patterns, and protocols for decomposing complex goals into sub-tasks and orchestrating their execution across multiple specialized agents.

The quality of a decomposition is not measured by how many sub-tasks it produces, but by three properties: **completeness** (the sub-tasks collectively achieve the goal), **independence** (each sub-task can be executed by a single agent without requiring another), and **verifiability** (each sub-task has an observable "done" criterion). A decomposition that lacks any of these three properties will produce coordination failures, redundant work, or unverifiable outcomes.

**What this skill is:** A framework for breaking goals into sub-tasks, constructing dependency DAGs, assigning work to agents, and managing multi-agent execution patterns.

**What this skill is not:** An execution engine. This skill plans and coordinates. It does not write code, run tests, or deploy systems.

**Why DAGs, not lists:** A flat task list implies sequential execution and hides dependency information. A DAG makes dependencies explicit, reveals parallelization opportunities, identifies the critical path, and makes the impact of a single failure visible. Every decomposition should be a graph, not a list.

## Domain Principles

| # | Principle | Description |
|---|-----------|-------------|
| 1 | **Completeness Over Elegance** | A decomposition that covers all aspects of the goal with some redundancy is better than an elegant decomposition that misses a requirement. Verify completeness by tracing every stated deliverable to at least one sub-task. |
| 2 | **One Agent, One Sub-Task** | Each sub-task should be executable by exactly one agent. If a sub-task requires two agents to collaborate simultaneously, it is not decomposed enough. Split at the agent boundary. |
| 3 | **Explicit Dependencies Only** | If sub-task B needs the output of sub-task A, that dependency must be declared in the DAG. Implicit ordering ("A should probably happen first") is not a dependency -- it is a guess. Unvalidated ordering wastes parallelization. |
| 4 | **Verifiable Completion** | Every sub-task must have a "done" criterion that can be verified without subjective judgment. "Code is clean" is not verifiable. "All tests pass and code review agent reports zero critical findings" is verifiable. |
| 5 | **Appropriate Granularity** | Decompose until each sub-task is a coherent unit of work for a single session of a single agent. Finer than that creates coordination overhead. Coarser than that creates ambiguity and scope creep. |
| 6 | **Risk-Aware Ordering** | When the dependency graph allows flexibility in execution order, prefer to execute high-risk sub-tasks early. Early failure is cheaper than late failure. |
| 7 | **Recoverable Failures** | Design the decomposition so that a single sub-task failure does not cascade into total plan failure. Prefer many independent tracks over a single serial chain. |
| 8 | **Stable Interfaces Between Sub-Tasks** | The inputs and outputs of each sub-task form a contract. Define these contracts before execution begins, and do not change them mid-execution without re-planning. |

## Decomposition Strategies

### Strategy 1: Functional Decomposition

Split by capability, feature, or functional area. Each sub-task implements or addresses a distinct functional concern.

**When to use:**
- The goal describes a system with identifiable features or capabilities
- Different features map cleanly to different agent domains
- Features have limited interaction at implementation time

**How to apply:**
```
1. List all functional requirements in the goal
2. Group related requirements into functional areas
3. Create one sub-task per functional area
4. Identify shared dependencies between areas (database schemas,
   shared types, configuration)
5. Extract shared dependencies as prerequisite sub-tasks
6. Connect sub-tasks via the shared prerequisite dependencies
```

**Example:**
```
Goal: "Add user authentication and an admin dashboard to the application"

Functional decomposition:
  T1: Define auth data model (schemas, entities)         -> tdd-agent
  T2: Implement authentication flow (login, logout, JWT) -> tdd-agent [depends: T1]
  T3: Write auth integration tests                       -> test-generation-agent [depends: T2]
  T4: Build admin dashboard UI                           -> tdd-agent [depends: T1]
  T5: Review auth implementation for security            -> code-review-agent [depends: T2]
  T6: Document auth API and admin features               -> documentation-agent [depends: T2, T4]
```

### Strategy 2: Data-Flow Decomposition

Split by data transformation stages. Each sub-task processes data from one form to another.

**When to use:**
- The goal describes a pipeline, ETL process, or data transformation
- The work naturally flows from input to output through transformation stages
- Each stage has clearly different technical concerns

**How to apply:**
```
1. Identify the input data and the desired output
2. Trace the transformations required from input to output
3. Create one sub-task per transformation stage
4. Connect sub-tasks by the data artifacts they produce and consume
5. Identify stages that can process data in parallel (independent branches)
```

**Example:**
```
Goal: "Build a data pipeline that ingests sensor data, detects anomalies,
       and generates daily reports"

Data-flow decomposition:
  T1: Implement data ingestion layer     -> tdd-agent
  T2: Build anomaly detection model      -> model-optimization-agent [depends: T1]
  T3: Configure sensor integrations      -> sensor-anomaly-agent [depends: T1]
  T4: Build report generation service    -> tdd-agent [depends: T2]
  T5: Generate test data and validate    -> test-generation-agent [depends: T1]
  T6: Document pipeline architecture     -> documentation-agent [depends: T2, T4]
```

### Strategy 3: Temporal Decomposition

Split by lifecycle phase. Each sub-task corresponds to a phase in the project or feature lifecycle.

**When to use:**
- The goal spans the full development lifecycle (design through deployment)
- Earlier phases produce artifacts that later phases consume
- The work is naturally ordered by time

**How to apply:**
```
1. Identify the lifecycle phases involved (research, design, implement,
   test, deploy, document)
2. Create sub-tasks for each phase
3. Within each phase, apply functional or data-flow decomposition
   if the phase is too large for a single agent
4. Connect phases sequentially
5. Look for cross-phase parallelization (documentation can often
   start during implementation)
```

**Example:**
```
Goal: "Migrate the payment service from .NET Framework 4.8 to .NET 10"

Temporal decomposition:
  T1: Research breaking changes and compatibility  -> research-agent
  T2: Assess current codebase migration readiness  -> migration-orchestrator [depends: T1]
  T3: Audit dependencies for .NET 10 compatibility -> dependency-audit-agent [parallel: T2]
  T4: Execute migration plan                       -> migration-orchestrator [depends: T2, T3]
  T5: Generate regression test suite               -> test-generation-agent [depends: T4]
  T6: Review migrated code for issues              -> code-review-agent [depends: T4]
  T7: Update documentation for .NET 10             -> documentation-agent [depends: T4]
```

### Strategy 4: Risk-Ordered Decomposition

Split by risk level, isolating uncertain or high-risk work into early sub-tasks for fast validation.

**When to use:**
- The goal involves significant technical uncertainty
- Some parts of the goal may be infeasible and early detection saves effort
- The team needs to "de-risk" before committing to the full plan

**How to apply:**
```
1. Identify the riskiest aspects of the goal:
   a. Technical unknowns (will this approach work?)
   b. Integration risks (will these components connect?)
   c. Performance risks (will this meet latency/throughput targets?)
   d. External dependency risks (is this third-party service reliable?)
2. Create probe sub-tasks for each high-risk area
3. Design probe sub-tasks to fail fast (minimal effort to validate)
4. Gate the remaining plan on probe results
5. Create the full decomposition, but mark post-probe tasks as
   CONTINGENT on probe success
```

**Example:**
```
Goal: "Integrate real-time video analytics on edge devices for the fleet"

Risk-ordered decomposition:
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

Use these rules to determine when to split a sub-task further versus when to stop decomposing.

### Split When

| Signal | Action |
|--------|--------|
| Sub-task requires two different agents | Split at the agent boundary |
| Sub-task has multiple independent deliverables | Split into one sub-task per deliverable |
| Sub-task description uses "and" connecting unrelated actions | Split at the "and" |
| Sub-task cannot be completed in a single focused session | Split by natural pause points |
| Sub-task has both autonomous and approval-required components | Split into autonomous and gated sub-tasks |
| Failure of one part would not necessarily block the other part | Split into independent sub-tasks |

### Stop When

| Signal | Action |
|--------|--------|
| Sub-task maps to a single agent and a single concern | Stop -- this is the right granularity |
| Further splitting would produce sub-tasks without meaningful "done" criteria | Stop -- you have reached the atomic level |
| Further splitting would create more coordination cost than execution cost | Stop -- over-decomposition is waste |
| Three or more resulting sub-tasks would be assigned to the same agent in sequence with no branching between them | Merge them back -- they are one logical unit |
| Sub-task is already a well-understood operation for the assigned agent | Stop -- the agent knows how to handle it |

## Dependency DAG Construction

### Building the Graph

```
FOR EACH sub-task T:
  1. List the inputs T requires (data, artifacts, preconditions)
  2. For each input:
     a. If the input exists already (in the codebase, environment) -> no dependency
     b. If the input is produced by another sub-task P -> add edge P -> T
     c. If the input is not available and no sub-task produces it -> GAP
  3. List the outputs T produces
  4. Verify that every output is either:
     a. Consumed by at least one downstream sub-task, OR
     b. Is a final deliverable of the goal
```

### Cycle Detection

After constructing the DAG, verify it is acyclic:

```
Algorithm: Topological Sort (Kahn's Algorithm)
1. Compute in-degree for every node
2. Add all nodes with in-degree 0 to a queue
3. While queue is not empty:
   a. Remove node N from queue
   b. Add N to sorted order
   c. For each successor S of N:
      - Decrement in-degree of S
      - If in-degree of S becomes 0, add S to queue
4. If sorted order contains all nodes -> DAG is valid
5. If sorted order is missing nodes -> CYCLE EXISTS among the missing nodes
```

### Critical Path Calculation

```
1. Assign weights to each sub-task (estimated effort: S=1, M=2, L=3)
2. Find the longest path through the DAG (sum of weights)
3. This is the critical path -- it determines the minimum total duration
4. Sub-tasks NOT on the critical path have slack (can be delayed without
   affecting total duration)
5. Focus monitoring attention on critical path sub-tasks
```

## Sub-Agent Assignment Protocol

### Assignment Rules

```
FOR EACH sub-task T:
  1. Identify the primary domain of T
  2. Look up the Available Sub-Agents table
  3. Select the agent whose domain best matches
  4. If multiple agents could handle T:
     a. Prefer the agent with tighter domain focus
     b. Prefer the agent with higher autonomy (less coordination overhead)
     c. If still tied, prefer the agent already assigned other sub-tasks
        in the same track (reduces context switching)
  5. If no agent matches:
     a. Check if T can be decomposed further to match available agents
     b. If not, flag as UNASSIGNABLE
  6. Record the assignment with rationale
```

### Handling Unassignable Sub-Tasks

```
When a sub-task has no matching agent:
  1. Document what capability is needed
  2. Check if the sub-task can be reformulated:
     a. Can it be split so that parts match available agents?
     b. Can it be merged with an adjacent sub-task that HAS an agent?
     c. Can the approach be changed to use available capabilities?
  3. If reformulation fails:
     a. Report the gap to the user
     b. Offer options: user handles manually, skip, or restructure
     c. Mark the sub-task as UNASSIGNABLE in the plan
     d. Mark all downstream dependents as CONTINGENT on resolution
```

## State Block

Maintain state across conversation turns using this block:

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

**State transitions:**

```
UNDERSTAND --> DECOMPOSE    (goal analyzed, constraints identified)
DECOMPOSE  --> ASSIGN       (sub-tasks defined, DAG constructed)
ASSIGN     --> SEQUENCE     (all sub-tasks assigned or flagged)
SEQUENCE   --> MONITOR      (execution plan approved by user)
MONITOR    --> COMPLETE     (all sub-tasks completed or handled)

Any state  --> UNDERSTAND   (goal changes, re-analyze)
MONITOR    --> DECOMPOSE    (failure requires plan restructuring)
```

## Output Templates

### Template 1: Goal Analysis

```markdown
## Goal Analysis

**Stated goal:** [user's exact words]

**Deliverables:**
1. [deliverable 1]
2. [deliverable 2]
3. [deliverable 3]

**Constraints:**
- Tech stack: [languages, frameworks, infrastructure]
- Conventions: [patterns, standards observed in codebase]
- Timeline: [if stated]
- Scope boundaries: [what is explicitly out of scope]

**Assumptions:**
- [assumption 1 -- will verify by...]
- [assumption 2 -- will verify by...]

**Open questions:**
- [question 1 -- needed before decomposition can proceed]
- [question 2 -- can proceed but may affect granularity]
```

### Template 2: Decomposition Plan

```markdown
## Decomposition Plan

**Strategy:** [functional | data-flow | temporal | risk-ordered]
**Rationale:** [why this strategy fits this goal]

### Sub-Tasks

| ID | Name | Description | Agent | Inputs | Outputs | Done Criteria | Effort |
|----|------|-------------|-------|--------|---------|---------------|--------|
| T1 | ... | ... | ... | ... | ... | ... | S/M/L |

### Dependency DAG

```
T1 ──> T2 ──> T5
  └──> T3 ──> T5
T4 (independent) ──> T6
T5 ──> T6
```

### Critical Path
T1 -> T2 -> T5 -> T6 (estimated: 8 effort units)

### Execution Waves
- Wave 1: T1, T4 (parallel)
- Wave 2: T2, T3 (parallel, after T1)
- Wave 3: T5 (after T2 and T3)
- Wave 4: T6 (after T4 and T5)

### Unassignable Sub-Tasks
[list or "None"]

### Risk Points
- T2 is on the critical path and involves [risk] -- early failure here blocks T5 and T6
```

### Template 3: Progress Report

```markdown
## Progress Report: Wave [N]

| ID | Name | Agent | Status | Notes |
|----|------|-------|--------|-------|
| T1 | ... | ... | COMPLETED | [evidence of completion] |
| T2 | ... | ... | IN_PROGRESS | [current state] |
| T3 | ... | ... | BLOCKED | Waiting on T2 |

**Critical path status:** [on track | at risk | delayed]
**Blockers:** [description or "none"]
**Next wave:** [wave N+1 sub-tasks, or "pending resolution of blockers"]
```

## Anti-Patterns

| Anti-Pattern | Why It Fails | Correct Approach |
|--------------|-------------|------------------|
| **Flat List Decomposition** | Hides dependencies, prevents parallelization, obscures impact of failure. | Always construct a DAG. If all sub-tasks truly have no dependencies, document that explicitly. |
| **Over-Decomposition** | Coordination overhead exceeds execution cost. Dozens of tiny tasks create more work tracking than doing. | Stop decomposing when each sub-task is one agent, one concern, one session. |
| **Wishful Assignment** | Assigning a sub-task to an agent whose domain does not match, hoping it will figure it out. | Verify domain alignment. If no agent fits, report the gap honestly. |
| **Implicit Dependencies** | Assuming sub-tasks will execute in a reasonable order without declaring why. | Make every dependency explicit with the input/output rationale. |
| **Monolithic Decomposition** | Three sub-tasks where the first is "analyze everything" and the last is "implement everything." | Each sub-task should be a single coherent unit, not a lifecycle phase containing unbounded work. |
| **Ignoring the Critical Path** | Treating all sub-tasks as equally urgent. | Identify the critical path and focus attention on sub-tasks that determine total duration. |
| **Single-Chain Plans** | All sub-tasks in a single serial chain with no parallelization. | Look for independent sub-tasks that can run in parallel. Most real plans have at least two parallel tracks. |

## Integration with Other Skills

| Skill | Integration Point |
|-------|-------------------|
| **decomposition-heuristics** (reference) | Detailed strategies for when to split, when to stop, and which decomposition strategy fits which goal type. |
| **orchestration-patterns** (reference) | Multi-agent execution patterns (sequential, parallel, conditional, iterative) and DAG construction techniques. |

## Stack-Specific Guidance

Detailed reference materials for applying decomposition and orchestration:

- [Decomposition Heuristics](references/decomposition-heuristics.md) -- Goal decomposition strategies, granularity heuristics, and worked examples of splitting complex goals
- [Orchestration Patterns](references/orchestration-patterns.md) -- Multi-agent execution patterns, dependency DAG construction, cycle detection, and failure recovery protocols

## AI Discipline Rules

### The plan is the product -- treat it with the same rigor as code

A sloppy decomposition produces sloppy execution. Every sub-task name should be action-oriented. Every dependency should have a rationale. Every done criterion should be verifiable. If the plan is not precise enough that an agent can execute a sub-task without asking clarifying questions, the plan is not done.

### Dependencies are constraints, not suggestions

If sub-task B depends on sub-task A, B cannot start until A completes. Do not soften this by saying "B can probably start in parallel if we assume A will succeed." Dependencies exist because outputs flow between tasks. Violating a dependency means executing without required inputs.

### Report gaps honestly -- never assign to the wrong agent to avoid a gap

An honest "no agent available for this sub-task" is infinitely more valuable than silently assigning it to an agent that will do it badly. Gaps in the plan are actionable information. Bad assignments are hidden failures.

### Monitor actively -- a plan that is not tracked is a wish

After dispatching sub-tasks, track their status. When a sub-task completes, verify its done criteria before unblocking dependents. When a sub-task fails, assess the blast radius immediately. A plan without monitoring is just a document.

## Error Recovery

### Decomposition produces too many sub-tasks

**Symptoms:** More than 15 sub-tasks for a goal, many are trivial or overlapping.

**Recovery:**
1. Review the granularity heuristics -- merge sub-tasks assigned to the same agent in sequence
2. Look for sub-tasks that are steps within a single agent's protocol (the agent handles internal steps)
3. Target 5-12 sub-tasks for most goals
4. If the goal genuinely requires more, group sub-tasks into named tracks and present tracks as the primary view

### User rejects the plan

**Symptoms:** User says "this is not what I meant" or "this is too complicated."

**Recovery:**
1. Do not defend the plan -- ask what aspect is wrong
2. Revisit UNDERSTAND phase -- was the goal misinterpreted?
3. Revisit granularity -- is the plan too detailed for the user's needs?
4. Offer a simplified view: "Here is the plan at two levels of detail"
5. Iterate until the user approves

### Sub-task produces unexpected output

**Symptoms:** A sub-agent completes but its output does not match what downstream sub-tasks expect.

**Recovery:**
1. Check the done criteria -- did the sub-agent satisfy them?
2. If done criteria were met but output is still wrong, the done criteria were insufficient
3. Revise the done criteria for the completed sub-task
4. Assess whether the downstream sub-tasks need revised inputs
5. Re-plan the affected portion of the DAG
