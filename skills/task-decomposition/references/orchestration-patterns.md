# Orchestration Patterns Reference

> "Plans are worthless, but planning is everything."
> -- Dwight D. Eisenhower

This reference provides multi-agent orchestration patterns for executing
decomposed task plans. It covers execution topologies, dependency DAG
construction and validation, failure handling, and coordination protocols.

## Execution Topologies

### Pattern 1: Sequential Pipeline

Sub-tasks execute one after another in a strict linear chain.

```
T1 ──> T2 ──> T3 ──> T4
```

**When to use:**
- Every sub-task depends on the output of the previous one
- No parallelization is possible
- The work is inherently staged (each stage transforms the previous output)

**Characteristics:**
- Total duration = sum of all sub-task durations
- Single point of failure at every stage
- Simple to monitor -- just track the current position in the chain
- Least efficient use of available agents (only one active at a time)

**Example:**
```
T1: Research API options           -> research-agent
T2: Implement chosen API           -> tdd-agent [depends: T1]
T3: Review implementation          -> code-review-agent [depends: T2]
T4: Document the API               -> documentation-agent [depends: T3]
```

**Coordination protocol:**
```
1. Dispatch T1
2. When T1 completes, verify done criteria, then dispatch T2
3. When T2 completes, verify done criteria, then dispatch T3
4. Continue until pipeline completes or a stage fails
5. On failure: stop the pipeline, assess, and re-plan
```

### Pattern 2: Parallel Fan-Out / Fan-In

Multiple sub-tasks execute concurrently after a shared prerequisite, then
converge at a synchronization point.

```
        ┌──> T2 ──┐
T1 ──>  ├──> T3 ──┤  ──> T5
        └──> T4 ──┘
```

**When to use:**
- Multiple independent sub-tasks share a common prerequisite
- A downstream sub-task needs the combined outputs of all parallel tracks
- You want to minimize total duration by parallelizing independent work

**Characteristics:**
- Total duration = T1 + max(T2, T3, T4) + T5
- Fan-in point (T5) is blocked until ALL parallel tracks complete
- Efficient use of agents -- multiple agents work concurrently
- Monitoring is more complex -- must track multiple active sub-tasks

**Example:**
```
T1: Define shared data model       -> tdd-agent
T2: Build API layer                -> tdd-agent [depends: T1]
T3: Build event processing         -> tdd-agent [depends: T1]
T4: Build admin dashboard          -> tdd-agent [depends: T1]
T5: Integration test all layers    -> test-generation-agent [depends: T2, T3, T4]
```

**Coordination protocol:**
```
1. Dispatch T1
2. When T1 completes, dispatch T2, T3, T4 simultaneously
3. Track completion of each parallel track independently
4. When ALL of T2, T3, T4 are complete, dispatch T5
5. On failure of any parallel track:
   a. Other tracks can continue (they are independent)
   b. T5 is blocked until the failed track is resolved
   c. Propose recovery for the failed track
```

### Pattern 3: Conditional Branching

The next sub-task depends on the result of a previous sub-task.

```
        ┌──> T2a (if probe succeeds) ──> T3
T1 ──>  │
        └──> T2b (if probe fails) ──> T3-alt
```

**When to use:**
- The decomposition includes probe or validation sub-tasks
- Different outcomes require different execution paths
- Risk-ordered decomposition with gate points

**Characteristics:**
- Total duration depends on which branch is taken
- Requires the orchestrator to evaluate branch conditions
- Plan must define both paths before execution begins
- User may need to approve branch selection

**Example:**
```
T1: Probe -- can model run on edge hardware?  -> model-optimization-agent
  IF T1 succeeds:
    T2a: Build optimized edge pipeline         -> model-optimization-agent
    T3a: Deploy to edge fleet                  -> fleet-deployment-agent
  IF T1 fails:
    T2b: Research cloud inference alternatives  -> research-agent
    T3b: Build cloud inference pipeline         -> tdd-agent
```

**Coordination protocol:**
```
1. Dispatch T1 (probe)
2. Evaluate T1 result against branch criteria
3. Present branch decision to user for confirmation
4. Dispatch the approved branch
5. If the branch was unexpected, the alternative branch plan is discarded
   (or preserved for potential future use)
```

### Pattern 4: Iterative Refinement

A sub-task is executed, its output is evaluated, and if the output does not
meet criteria, the sub-task is retried with adjusted inputs.

```
T1 ──> T2 ──> EVALUATE ──> [pass] ──> T3
                  │
                  └──> [fail] ──> ADJUST ──> T2 (retry)
```

**When to use:**
- Sub-task output quality is uncertain and may need multiple attempts
- Evaluation criteria are well-defined but the path to meeting them is not
- Machine learning optimization, performance tuning, or iterative design

**Characteristics:**
- Total duration is unbounded (depends on iteration count)
- Must define a maximum iteration count to prevent infinite loops
- Each iteration should provide feedback that guides the next attempt
- Diminishing returns -- set a threshold for "good enough"

**Example:**
```
T1: Build initial ML model                -> model-optimization-agent
T2: Evaluate model performance            -> model-optimization-agent
  IF accuracy < 90%:
    T2-retry: Adjust hyperparameters and retrain  (max 3 iterations)
  IF accuracy >= 90%:
    T3: Deploy optimized model             -> fleet-deployment-agent
```

**Coordination protocol:**
```
1. Dispatch T1
2. Dispatch T2 (evaluation)
3. If evaluation passes -> dispatch T3
4. If evaluation fails and iterations < max_iterations:
   a. Provide T2 results as feedback input
   b. Re-dispatch T2 with adjusted parameters
   c. Increment iteration counter
5. If evaluation fails and iterations >= max_iterations:
   a. Report that refinement did not converge
   b. Present best-so-far result to user
   c. Ask user: accept current result, continue iterating, or abandon
```

## Dependency DAG Construction

### Formal Definition

A task dependency DAG is a directed acyclic graph G = (V, E) where:
- V = set of sub-tasks
- E = set of directed edges representing dependencies
- Edge (A, B) means "B depends on A" (A must complete before B starts)
- The graph must contain no cycles

### Construction Algorithm

```
INPUT: List of sub-tasks, each with declared inputs and outputs

1. Create a node for each sub-task
2. Create an artifact registry:
   FOR EACH sub-task T:
     FOR EACH output O of T:
       Register O as produced by T
3. Create edges from artifacts:
   FOR EACH sub-task T:
     FOR EACH input I of T:
       Look up which sub-task P produces I
       IF P exists AND P != T:
         Add edge P -> T
       IF P does not exist:
         Check if I is a pre-existing artifact (already in codebase)
         IF pre-existing: no edge needed (T has no dependency for this input)
         IF not pre-existing: flag as MISSING INPUT
4. Validate: run cycle detection
5. Validate: check for orphaned nodes (no incoming or outgoing edges
   AND not a root or leaf node)
```

### Cycle Detection (Tarjan's Algorithm)

```
FUNCTION detect_cycles(G):
  index_counter = 0
  stack = []
  lowlink = {}
  index = {}
  on_stack = {}
  cycles = []

  FOR EACH node v in G:
    IF v not in index:
      strongconnect(v)

  FUNCTION strongconnect(v):
    index[v] = index_counter
    lowlink[v] = index_counter
    index_counter += 1
    stack.push(v)
    on_stack[v] = true

    FOR EACH successor w of v:
      IF w not in index:
        strongconnect(w)
        lowlink[v] = min(lowlink[v], lowlink[w])
      ELSE IF on_stack[w]:
        lowlink[v] = min(lowlink[v], index[w])

    IF lowlink[v] == index[v]:
      component = []
      REPEAT:
        w = stack.pop()
        on_stack[w] = false
        component.append(w)
      UNTIL w == v
      IF len(component) > 1:
        cycles.append(component)  // This is a cycle

  RETURN cycles
```

### Breaking Cycles

When a cycle is detected, choose one of these strategies:

| Strategy | When to Use | How to Apply |
|----------|-------------|-------------|
| **Merge** | Cyclic sub-tasks are in the same agent domain and tightly coupled | Combine into a single sub-task |
| **Split** | One sub-task has an independent part creating the back-edge | Extract the independent part as a new sub-task |
| **Invert** | The dependency direction can be reversed by redefining interfaces | Redefine which sub-task produces and which consumes the shared artifact |
| **Stage** | Both sub-tasks need partial output from each other | Introduce an intermediate "contract" sub-task that defines the interface both will use |

**Example: Breaking a cycle with staging**

```
CYCLE: T3 (build API) <-> T4 (build client)
  T3 needs to know client requirements
  T4 needs to know API endpoints

RESOLUTION:
  T2.5: Define API contract (OpenAPI spec)  [new sub-task]
  T3: Build API [depends: T2.5]
  T4: Build client [depends: T2.5]

  T3 and T4 are now parallel (both depend on T2.5, not on each other)
```

## Topological Sort for Wave Assignment

### Algorithm

```
FUNCTION assign_waves(G):
  waves = []
  remaining = set(all nodes in G)

  WHILE remaining is not empty:
    wave = []
    FOR EACH node N in remaining:
      IF all predecessors of N are NOT in remaining:
        wave.append(N)
    IF wave is empty:
      ERROR: cycle detected (should not happen if DAG was validated)
    waves.append(wave)
    remaining = remaining - set(wave)

  RETURN waves
```

### Example

```
DAG:
  T1 -> T3
  T1 -> T4
  T2 -> T4
  T3 -> T5
  T4 -> T5
  T4 -> T6

Wave assignment:
  Wave 1: T1, T2        (no predecessors)
  Wave 2: T3, T4        (predecessors T1/T2 in Wave 1)
  Wave 3: T5, T6        (predecessors T3/T4 in Wave 2)

Execution timeline:
  Wave 1: T1 || T2      (parallel)
  Wave 2: T3 || T4      (parallel, after Wave 1 completes)
  Wave 3: T5 || T6      (parallel, after Wave 2 completes)
```

## Critical Path Analysis

### Definition

The critical path is the longest path through the DAG, measured by the sum of
sub-task effort estimates along the path. It determines the minimum possible
total duration, assuming unlimited parallel agents.

### Calculation

```
FUNCTION critical_path(G, weights):
  // weights maps each node to its effort estimate
  // Using longest-path in a DAG (negate weights, run shortest path)

  earliest_start = {}
  FOR EACH node N in topological order:
    IF N has no predecessors:
      earliest_start[N] = 0
    ELSE:
      earliest_start[N] = max(
        earliest_start[P] + weights[P]
        FOR EACH predecessor P of N
      )

  // The critical path ends at the node with the latest finish time
  critical_end = argmax(earliest_start[N] + weights[N] for N in G)

  // Trace back to find the path
  path = [critical_end]
  current = critical_end
  WHILE current has predecessors:
    current = the predecessor P that maximizes earliest_start[P] + weights[P]
    path.prepend(current)

  RETURN path, earliest_start[critical_end] + weights[critical_end]
```

### Using Critical Path Information

| Situation | Action |
|-----------|--------|
| Sub-task on critical path is at risk | Prioritize it; consider assigning the most capable agent |
| Sub-task NOT on critical path is delayed | Check slack -- it may not affect total duration |
| Critical path is much longer than parallel paths | Look for ways to split critical path sub-tasks to enable more parallelization |
| Multiple paths have similar length | The plan is fragile -- a delay on any path affects total duration |

## Failure Handling Patterns

### Pattern: Retry with Context

When a sub-agent fails, retry with additional context from the failure.

```
PROTOCOL:
1. Capture failure details (error messages, partial output, agent's diagnosis)
2. Check retry budget (max 2 retries per sub-task)
3. Construct enhanced context:
   a. Original sub-task inputs
   b. Failure details from previous attempt
   c. Any additional context that might help
4. Re-dispatch to the same agent with enhanced context
5. If retry succeeds -> continue plan normally
6. If retry fails -> escalate (see below)
```

### Pattern: Reassign to Alternative Agent

When a sub-agent fails and retry does not resolve, assign to a different agent.

```
PROTOCOL:
1. Analyze why the primary agent failed
2. Check if an alternative agent can handle the sub-task:
   a. Different agent with overlapping domain
   b. More general-purpose agent that can attempt the work
3. Reformulate the sub-task if needed for the new agent's protocol
4. Dispatch to alternative agent
5. If no alternative agent exists -> escalate to user
```

### Pattern: Plan Restructuring

When a failure invalidates a portion of the plan.

```
PROTOCOL:
1. Identify all sub-tasks affected by the failure:
   a. Direct dependents of the failed sub-task
   b. Transitive dependents (dependents of dependents)
2. Classify affected sub-tasks:
   a. BLOCKED: cannot proceed without failed sub-task's output
   b. INDEPENDENT: can continue on separate tracks
   c. OBSOLETE: no longer relevant given the failure
3. For BLOCKED sub-tasks:
   a. Can the blocker be worked around?
   b. Can the dependency be removed by reformulating?
   c. Can a manual intervention provide the missing input?
4. Produce revised plan
5. Present to user for approval
6. Do NOT resume execution until approval is granted
```

### Pattern: Graceful Degradation

When a sub-task failure means the full goal cannot be achieved, but partial
results are still valuable.

```
PROTOCOL:
1. Identify which deliverables are still achievable
2. Identify which deliverables are lost due to the failure
3. Present to user:
   "Sub-task [X] failed. As a result:
    - Deliverables [A, B] are complete and valid
    - Deliverable [C] is partially complete ([detail])
    - Deliverable [D] cannot be achieved without [X]
    Options:
    a. Accept partial results
    b. Attempt alternative approach for [D]
    c. Retry [X] with modified scope"
4. Execute user's chosen option
```

## Coordination Protocols

### Wave Dispatch Protocol

```
FOR EACH wave W in execution order:
  1. Verify all predecessor waves are COMPLETED
  2. For each sub-task T in wave W:
     a. Verify all of T's predecessors are COMPLETED
     b. Gather T's inputs from predecessor outputs
     c. Dispatch T to its assigned agent
  3. Monitor all sub-tasks in W:
     a. Track status: PENDING -> IN_PROGRESS -> COMPLETED | FAILED
     b. When any sub-task completes, verify done criteria
     c. When any sub-task fails, assess impact on current and future waves
  4. Wave W is COMPLETED when all sub-tasks in W are COMPLETED
  5. Wave W is FAILED if any sub-task fails and recovery is needed
  6. Report wave status to user
```

### Progress Reporting Protocol

```
AFTER EACH wave completes:
  Report:
  1. Wave number and sub-tasks completed
  2. Total progress: [completed] / [total] sub-tasks
  3. Critical path status: on track | at risk | delayed
  4. Any blocked sub-tasks and their blockers
  5. Estimated remaining effort
  6. Next wave preview (sub-tasks to be dispatched)
```

### Handoff Protocol Between Agents

When one agent's output becomes another agent's input:

```
1. Verify the producing agent's done criteria are met
2. Collect the output artifacts:
   a. Files created or modified (with paths)
   b. Test results (pass/fail counts)
   c. Reports or documents produced
   d. Configuration changes made
3. Format the handoff context for the consuming agent:
   a. What was done (summary of completed sub-task)
   b. What was produced (list of artifacts with locations)
   c. What the consuming agent needs to do (its sub-task description)
   d. Any caveats or known issues from the producing agent
4. Dispatch the consuming agent with the handoff context
```

## Scaling Considerations

### Small Goals (1-5 sub-tasks)

- Sequential pipeline or simple fan-out is sufficient
- Overhead of formal DAG construction may exceed benefit
- Use lightweight tracking (checklist, not full state block)

### Medium Goals (5-15 sub-tasks)

- Full DAG construction is valuable
- Wave-based execution with parallel tracks
- Formal progress reporting after each wave
- Critical path analysis guides attention

### Large Goals (15+ sub-tasks)

- Group sub-tasks into named tracks or phases first
- Present the plan hierarchically: tracks first, then sub-tasks within tracks
- Consider breaking into multiple decomposition sessions
- Track-level monitoring with drill-down into sub-task detail
- Plan for re-planning -- large plans rarely survive first contact intact

### Effort Estimation Weights

Use consistent weights for critical path calculation:

| Estimate | Weight | Typical Duration |
|----------|--------|------------------|
| Small (S) | 1 | Single focused agent session (< 30 min equivalent) |
| Medium (M) | 2 | Multiple steps within one agent session |
| Large (L) | 3 | Full agent session with verification |
| Extra-Large (XL) | 5 | Consider splitting -- may be too coarse |
