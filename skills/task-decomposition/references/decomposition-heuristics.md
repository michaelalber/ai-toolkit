# Decomposition Heuristics Reference

> "Controlling complexity is the essence of computer programming."
> -- Brian Kernighan

This reference provides detailed heuristics for decomposing complex goals into
sub-tasks. It covers how to choose a decomposition strategy, how to determine
the right granularity, and how to handle common decomposition challenges.

## Choosing a Decomposition Strategy

Not all goals decompose the same way. The structure of the goal determines which
strategy produces the best decomposition.

### Decision Matrix

| Goal Characteristic | Recommended Strategy | Rationale |
|---------------------|---------------------|-----------|
| Goal describes multiple independent features | Functional | Features map to sub-tasks naturally |
| Goal describes a pipeline or transformation chain | Data-flow | Stages map to sub-tasks naturally |
| Goal spans design through deployment | Temporal | Lifecycle phases provide natural ordering |
| Goal has high uncertainty or novel technology | Risk-ordered | De-risk early before committing to full plan |
| Goal has mixed characteristics | Hybrid | Use primary strategy, apply secondary within phases |

### Functional Decomposition -- Detailed

**Identification signals:**
- Goal uses words like "features," "capabilities," "modules," "components"
- Different parts of the goal map to different parts of the codebase
- Different parts of the goal require different expertise

**Procedure:**
```
1. List every noun in the goal statement (these are candidate features)
2. List every verb (these are candidate actions per feature)
3. Group nouns by relatedness:
   a. Nouns that share data -> same functional area
   b. Nouns that share users -> same functional area
   c. Nouns that can change independently -> different functional areas
4. For each functional area:
   a. Define one sub-task per major action
   b. Identify shared data or interfaces between areas
   c. Extract shared elements as prerequisite sub-tasks
5. Validate: does each sub-task map to exactly one agent?
```

**Worked example:**

```
Goal: "Build an inventory management system with barcode scanning,
       stock level alerts, and a supplier reorder portal"

Nouns: inventory, barcode, stock levels, alerts, supplier, reorder, portal
Verbs: scan, track, alert, reorder

Functional areas:
  1. Barcode scanning (scan, track) -> sensor-integration domain
  2. Stock level monitoring (track, alert) -> anomaly-detection domain
  3. Supplier reorder portal (reorder, portal) -> web application domain
  4. Core inventory data model (shared by all three) -> prerequisite

Sub-tasks:
  T1: Define inventory data model         -> tdd-agent
  T2: Implement barcode scanning service  -> tdd-agent [depends: T1]
  T3: Build stock level monitoring        -> sensor-anomaly-agent [depends: T1]
  T4: Build supplier reorder portal       -> tdd-agent [depends: T1]
  T5: Integration test full workflow      -> test-generation-agent [depends: T2, T3, T4]
  T6: Document API and user guides        -> documentation-agent [depends: T2, T3, T4]
```

### Data-Flow Decomposition -- Detailed

**Identification signals:**
- Goal uses words like "pipeline," "process," "transform," "ingest," "output"
- There is a clear input-to-output flow
- Each stage has different technical concerns (parsing, validation, transformation, storage)

**Procedure:**
```
1. Identify the input (raw data, user request, event)
2. Identify the desired output (report, response, stored artifact)
3. Trace the transformation path from input to output
4. For each transformation step:
   a. What data format enters?
   b. What data format exits?
   c. What processing logic is applied?
   d. What can go wrong (validation, errors)?
5. Create one sub-task per transformation step
6. Connect sub-tasks by their data interfaces
7. Look for branching points (one input feeds multiple outputs)
   and merge points (multiple inputs combine into one output)
```

### Temporal Decomposition -- Detailed

**Identification signals:**
- Goal spans multiple project phases (research, design, build, test, deploy)
- Later work depends on decisions made in earlier phases
- The goal includes both investigation and implementation

**Procedure:**
```
1. Identify the lifecycle phases present in the goal:
   a. Research / Investigation
   b. Design / Planning
   c. Implementation
   d. Testing / Verification
   e. Deployment / Release
   f. Documentation
2. Within each phase, apply functional decomposition if needed
3. Connect phases sequentially (research before design, design before implement)
4. Identify cross-phase parallelization:
   a. Documentation can often start during implementation
   b. Test planning can start during design
   c. Environment setup can happen parallel to implementation
```

### Risk-Ordered Decomposition -- Detailed

**Identification signals:**
- Goal involves technology the team has not used before
- Performance requirements are uncertain
- Third-party integrations have unknown reliability
- Some aspects of the goal may be technically infeasible

**Procedure:**
```
1. List every technical risk in the goal:
   a. FEASIBILITY: "Can we even do this?"
   b. PERFORMANCE: "Will it be fast enough?"
   c. INTEGRATION: "Will these systems connect?"
   d. SCALE: "Will it handle the expected load?"
2. For each risk, design a PROBE sub-task:
   a. Minimal effort to validate or invalidate
   b. Clear pass/fail criteria
   c. Produces evidence, not opinions
3. Create a GATE after all probes:
   a. All probes pass -> proceed with full decomposition
   b. Any probe fails -> re-plan or report infeasibility
4. Create the full decomposition, marking post-gate tasks as CONTINGENT
```

## Granularity Decision Guide

### The "Can You Verify It?" Test

For each sub-task, ask: "How would I verify this is done?"

| Answer | Granularity Assessment |
|--------|----------------------|
| "I would run the tests and check they pass" | Good -- verifiable, atomic |
| "I would look at the code and see if it looks right" | Too vague -- what specifically would you check? Split further or refine done criteria |
| "I would check multiple things: the API works, the tests pass, and the docs are updated" | Too coarse -- split into three sub-tasks |
| "I would check that the variable name changed" | Too fine -- this is a single operation inside a larger sub-task |

### The "Single Agent Session" Test

For each sub-task, ask: "Can a single agent complete this in one focused session
without needing to pause for input from another agent?"

| Answer | Granularity Assessment |
|--------|----------------------|
| "Yes, one agent can handle this from start to finish" | Good granularity |
| "The agent would need to wait for results from another task" | Add the dependency explicitly -- the sub-task itself may be fine |
| "The agent would need to switch between different types of work" | Too coarse -- split by work type |
| "This would take three minutes and is trivial" | Too fine -- merge with adjacent sub-task for same agent |

### The "Blast Radius" Test

For each sub-task, ask: "If this sub-task fails, what else fails?"

| Answer | Granularity Assessment |
|--------|----------------------|
| "Only this sub-task and its direct dependents" | Good -- failure is contained |
| "Everything downstream fails" | Consider splitting to isolate the risky part from the safe part |
| "Nothing else is affected" | Good -- this sub-task is independently valuable |
| "It is hard to tell what would be affected" | Dependencies are not explicit enough -- revisit the DAG |

## Common Decomposition Mistakes

### Mistake 1: Decomposing by File Instead of by Concern

```
WRONG:
  T1: Modify UserController.cs
  T2: Modify UserService.cs
  T3: Modify UserRepository.cs

RIGHT:
  T1: Implement user authentication endpoint (spans controller, service, repository)
  T2: Add authorization checks to existing endpoints
  T3: Write integration tests for auth flows
```

Files are implementation details. Decompose by functional concern, then let the
executing agent determine which files to touch.

### Mistake 2: Decomposing Steps Within a Single Agent's Protocol

```
WRONG:
  T1: Write the first failing test
  T2: Write the minimal implementation to pass the test
  T3: Refactor the implementation
  T4: Write the next failing test
  (This is the TDD agent's internal protocol, not a decomposition)

RIGHT:
  T1: Implement the payment processing service using TDD -> tdd-agent
  T2: Review the payment service for security issues -> code-review-agent
```

Do not decompose into steps that a single agent already handles internally.
Trust the agent's protocol.

### Mistake 3: Creating Dependencies Where None Exist

```
WRONG:
  T1: Write backend API
  T2: Write frontend UI [depends: T1]
  (If the API contract is defined upfront, frontend can start immediately)

RIGHT:
  T1: Define API contract (OpenAPI spec)
  T2: Implement backend API [depends: T1]
  T3: Implement frontend UI [depends: T1]
  (T2 and T3 run in parallel after the contract is established)
```

Always ask: "Does T2 actually need T1's OUTPUT, or does it just need an
AGREEMENT that T1 will eventually produce?" If the latter, extract the
agreement as a separate sub-task and parallelize.

### Mistake 4: Ignoring Cross-Cutting Concerns

```
WRONG:
  T1: Build feature A
  T2: Build feature B
  T3: Build feature C
  (Where does logging go? Error handling? Auth checks?)

RIGHT:
  T0: Establish cross-cutting infrastructure (logging, error handling, auth middleware)
  T1: Build feature A [depends: T0]
  T2: Build feature B [depends: T0]
  T3: Build feature C [depends: T0]
```

Cross-cutting concerns are shared prerequisites. Extract them or they will be
implemented inconsistently across features.

### Mistake 5: Serial Plan When Parallel Is Possible

```
WRONG:
  T1 -> T2 -> T3 -> T4 -> T5 (all serial, total duration = sum of all)

RIGHT:
  T1 -> T2 -> T4
     -> T3 -> T4    (T2 and T3 parallel after T1, total duration shorter)
  T5 (independent, parallel to everything)
```

Always look for independence. Two sub-tasks are independent if neither needs
the other's output. Independent sub-tasks should be in the same wave.

## Hybrid Decomposition

Most real goals require a combination of strategies. Use a primary strategy for
the top-level decomposition and a secondary strategy within individual sub-tasks.

### Common Hybrid Patterns

| Primary | Secondary | When to Use |
|---------|-----------|-------------|
| Temporal | Functional | Full-lifecycle goal with multiple features per phase |
| Risk-ordered | Functional | Uncertain goal with multiple feature areas |
| Functional | Data-flow | Feature-oriented goal where each feature is a pipeline |
| Temporal | Risk-ordered | Lifecycle goal where early phases have high uncertainty |

### Hybrid Example

```
Goal: "Modernize the legacy reporting system to a real-time dashboard
       with historical data migration"

Primary: Temporal (research -> migrate -> build -> deploy)
Secondary: Risk-ordered within research phase

  Phase 0 (Risk probes):
    T1: Validate real-time data streaming feasibility  [PROBE]
    T2: Test legacy data export compatibility          [PROBE]
  --- GATE ---
  Phase 1 (Migration):
    T3: Migrate historical data to new schema          [depends: T2]
    T4: Build data streaming pipeline                  [depends: T1]
  Phase 2 (Implementation):
    T5: Build dashboard UI                             [depends: T4]
    T6: Implement historical data queries              [depends: T3]
  Phase 3 (Verification):
    T7: Integration test full system                   [depends: T5, T6]
    T8: Performance test real-time path                [depends: T5]
  Phase 4 (Documentation):
    T9: Document system architecture                   [depends: T5, T6]
    T10: Write user guide for dashboard                [depends: T5]
```
