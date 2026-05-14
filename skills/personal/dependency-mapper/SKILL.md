---
name: dependency-mapper
description: Coupling visualization with Robert C. Martin stability metrics — makes architectural decisions visible as dependency patterns. Use when analyzing module dependencies, detecting circular references, visualizing coupling, or assessing architectural health through Robert C. Martin stability metrics.
---

# Dependency Mapper

> "The dependencies between packages must not form cycles. If there is a cycle in the dependency structure, you have a problem that must be broken."
> -- Robert C. Martin, *Agile Software Development: Principles, Patterns, and Practices*

## Core Philosophy

Architecture is not what you draw on a whiteboard — it is the dependency structure in your code. This skill makes that structure visible and measurable. Using Robert C. Martin's package coupling metrics (Ca, Ce, I, A, D), you learn to see dependency patterns as architectural decisions and recognize when those decisions have drifted from intent.

Every `import`, `using`, `require`, or `#include` is an architectural vote. Most developers have a mental model that diverges significantly from reality. This skill closes that gap with numbers.

**What this skill is:** A coaching framework for reading dependency structure as architecture, computing Martin's metrics, and acting on the patterns they reveal.

**What this skill is not:** An automated refactoring tool. It shows the truth of your dependency structure; you decide what to do.

## Domain Principles

| # | Principle | Description |
|---|-----------|-------------|
| 1 | **Dependencies Reveal Architecture** | The actual dependency graph IS the architecture, regardless of documentation. |
| 2 | **Measure Before Judging** | Compute Ca, Ce, I, A, and D before forming opinions. Intuition about coupling is frequently wrong. |
| 3 | **Stable Dependencies Principle** | A module should only depend on modules MORE stable than itself: I(depender) ≥ I(dependee). |
| 4 | **Stable Abstractions Principle** | Stable modules (low I) should be abstract (high A). Unstable modules (high I) should be concrete (low A). |
| 5 | **Acyclic Dependencies Principle** | The dependency graph must be a DAG. Cycles create coupling chains where any change affects every member. |
| 6 | **Instability Is Not Bad** | I=1.0 means the module depends on others but nothing depends on it — correct for leaf modules and UI layers. |
| 7 | **Coupling Has Direction** | A depends on B is architecturally different from B depends on A. Reversing a dependency requires an abstraction. |
| 8 | **Abstractness Has Cost** | High abstractness adds indirection. Abstractness is justified only when it supports the Stable Abstractions Principle. |
| 9 | **The Main Sequence** | The ideal: A + I = 1. Distance D = \|A + I - 1\| measures how well a module balances stability with abstractness. D > 0.3 demands attention. |
| 10 | **Circular Dependencies Are Urgent** | Cycles compound over time; they are structural defects, not deferred debt. Most should be broken. |

## Knowledge Base Lookups

| Query | When to Call |
|-------|--------------|
| `search_knowledge("Robert Martin package coupling metrics instability abstractness")` | During COMPARE — verify Ca/Ce/I/A/D formulas and interpretation |
| `search_knowledge("acyclic dependencies principle stable abstractions")` | During COMPARE — ground SDP/SAP violation explanations |
| `search_knowledge("dependency inversion principle interface abstraction")` | During REFLECT — strategies for breaking cycles |
| `search_knowledge("clean architecture dependency direction layers")` | During REFLECT — verify dependency direction aligns with intended architecture |
| `search_knowledge("circular dependency refactoring strategies")` | During REFLECT — proven cycle-breaking techniques |

Search before presenting metrics (to confirm formulas) and before recommending refactoring (to confirm approach).

## Workflow: CACR Interaction Loop

**CHALLENGE → ATTEMPT → COMPARE → REFLECT**, then next module or project.

### Phase 1: Challenge

Enumerate the top-level modules/packages. Ask the user: "Before I compute metrics, sketch the dependency directions, predict which module has highest/lowest I, and predict whether any cycles exist. This is about building intuition, not speed."

### Phase 2: Attempt

User provides predictions about dependency structure, coupling, and problem areas. Coach does NOT correct yet — ask clarifying questions, record predictions for comparison, encourage reasoning.

### Phase 3: Compare

Scan source for import/dependency statements. Build the dependency graph. Compute Ca, Ce, I, A, D per module. Detect cycles. Present results alongside predictions.

### Phase 4: Reflect

Guide the user through: where predictions matched reality, where they diverged, which SDP violations are intentional vs. accidental, which one dependency to change first, and which cycle is most urgent to break.

## State Block

```
<dependency-state>
mode: scan | analyze | predict | reflect
project_path: [absolute path to project root]
language: [primary language detected]
modules_analyzed: [count]
circular_deps_found: [count of cycles]
instability_violations: [count of SDP violations]
main_sequence_distance: [average D across all modules]
last_action: [what was just completed]
next_action: [what should happen next]
</dependency-state>
```

## Output Templates

### Metrics Table

```markdown
## Package Coupling Metrics: [Project Name]

| Module | Ca | Ce | I     | A     | D     | Zone |
|--------|----|----|-------|-------|-------|------|
| Core   | 8  | 1  | 0.111 | 0.750 | 0.139 | --   |
| Data   | 3  | 4  | 0.571 | 0.200 | 0.229 | --   |
| Web    | 0  | 6  | 1.000 | 0.000 | 0.000 | --   |
| Shared | 6  | 5  | 0.455 | 0.100 | 0.445 | Pain |

**Formulas:**
- Ca: Afferent Coupling (incoming dependencies — how many depend on this)
- Ce: Efferent Coupling (outgoing dependencies — how many this depends on)
- I: Instability = Ce / (Ca + Ce), range [0,1]; 0=stable, 1=unstable
- A: Abstractness = abstract types / total types, range [0,1]
- D: Distance from Main Sequence = |A + I − 1|, range [0,1]; 0=ideal
- Zone: "Pain" = low I AND low A (stable+concrete); "Useless" = high I AND high A
```

### Dependency Scan Report

```markdown
## Dependency Scan: [Project Name]
**Language**: [language] | **Modules**: [count] | **Cycles detected**: [N]

### Raw Dependencies
[ModuleA] --> [ModuleB]
[ModuleA] --> [ModuleC]
...

### Circular Dependencies
Cycle 1: [A] → [B] → [C] → [A] — impact: independent deployment impossible, changes cascade
Breaking strategies: (1) Extract interface from A into shared abstractions, (2) Merge tightly-coupled modules, (3) Replace back-edge with event mechanism

### SDP Violations
| Depender | I(depender) | Dependee | I(dependee) | Delta |
|----------|-------------|----------|-------------|-------|
| Data | 0.571 | Shared | 0.455 | 0.116 |

Delta > 0.3 = high priority; < 0.1 may be acceptable depending on context.
```

Full templates (Main Sequence Chart, Violation List, Refactoring Suggestions): `references/coupling-metrics.md`.

## AI Discipline Rules

**Always compute actual metrics from code — never estimate or guess.** Scan actual source files for import/dependency statements. If a project is too large to fully scan, scan a representative subset and state scope clearly.

**Present numbers first, interpretation second.** Show the metrics table before offering commentary. Prevent anchoring the user's thinking with conclusions before they examine the evidence.

**Distinguish intentional coupling from accidental coupling.** A web controller depending on a service layer is intentional. A utility module depending on a domain module is likely accidental. Always ask: was this dependency a deliberate decision, or the path of least resistance?

**High instability is not a problem without context.** A module with I=1.0 that has Ca=0 (nothing depends on it) can change freely — this is correct for leaf modules. Do not flag high instability without checking what depends on the module.

**Circular dependencies are always worth discussing.** Even two-module cycles prevent independent deployment, complicate testing, and create opaque change propagation. The question is not whether to discuss them but how urgently to address them.

**Prioritize violations that matter.** Focus on: (1) cycles crossing deployment boundaries, (2) SDP violations in frequently-changing modules, (3) Zone of Pain modules that are also change hotspots. Leave stable, rarely-modified violations for later.

**Acknowledge when metrics are incomplete.** Dynamic dependencies, DI containers, and message queues may be invisible to static analysis. Partial truth stated clearly is more valuable than false precision.

## Anti-Patterns

| Anti-Pattern | Why It Fails | Correct Approach |
|--------------|-------------|------------------|
| **Metric Worship** | Optimizing D to zero produces over-abstracted code. Metrics are diagnostic, not prescriptive. | Use metrics to identify areas for investigation, then apply judgment. |
| **Ignoring Direction** | Treating coupling as symmetric loses critical architectural information. | Always specify direction: "A depends on B." Direction determines who is affected. |
| **Treating All Coupling Equally** | Depending on a stable abstract module is cheap; depending on a volatile concrete module is expensive. | Weight coupling by the instability and volatility of the dependee. |
| **Refactoring Stable Modules** | Low-I modules (many dependents) propagate changes widely — dangerous to refactor. | Refactor unstable modules first. Add abstractions to stable modules only when SAP demands it. |
| **Breaking Cycles by Adding Indirection** | A "pass-through" module that depends on both A and B does not break the cycle. | Break cycles by inverting one dependency using an interface, or by merging tightly-coupled modules. |
| **Snapshot Analysis Only** | Architecture drifts over time; a one-time measurement misses trends. | Track metrics across commits or sprints. Trend matters more than absolute values. |
| **Confusing Packages with Classes** | Martin's metrics apply to packages (modules, assemblies, namespaces), not individual classes. | Apply Ca/Ce/I/A/D at the package or module level. |
| **Ignoring the Build System** | Some dependencies are invisible in source code but present in build configs. | Cross-reference source analysis with build declarations (csproj, package.json, go.mod, Cargo.toml). |

## Error Recovery

**Project too large to analyze fully**: Identify architectural layers or bounded contexts. Analyze one layer at a time, then analyze inter-layer dependencies. Present hierarchical view: layer-level metrics first, then module-level within each layer. Ask: "Which layer or area do you want to focus on?"

**User does not understand the metrics**: Pause the CACR loop. Walk through the formulas with a concrete two-module example (e.g., OrderService: Ca=2, Ce=3, I=0.60 vs. Database: Ca=5, Ce=0, I=0.00). Reference `references/coupling-metrics.md`. Resume with a simpler challenge (fewer modules).

**Metrics look good but architecture feels wrong**: Check for hidden coupling not visible in imports (shared DB tables, configuration, message queues). Check whether modules are too coarse-grained and hide internal coupling. Investigate temporal coupling (must execute in order) and feature envy (modules reaching into each other's data). These are not captured by static import analysis.

**User wants to skip prediction and see metrics directly**: Respect the request. Show metrics. Then ask the user to predict for a different area of the codebase — explaining that calibrating intuition against reality is the fastest way to build architectural judgment.

## Integration with Other Skills

| Skill | Integration Point |
|-------|-------------------|
| **architecture-review** | Use dependency-mapper metrics as quantitative input; metrics provide evidence for architectural concerns |
| **pattern-tradeoff-analyzer** | When coupling patterns are revealed, use this skill to evaluate whether a design pattern would improve structure |
| **architecture-journal** | Record metric trends and refactoring decisions for longitudinal tracking |
| **technical-debt-assessor** | SDP violations, cycles, and Zone of Pain modules feed directly into technical debt assessment |
| **refactor-challenger** | When breaking a cycle or fixing an SDP violation, use this skill to evaluate the refactoring approach |
| **code-review-coach** | Reference dependency metrics to evaluate whether a change improves or degrades structure |

## Stack-Specific Guidance

| Language | Import Mechanism | Common Tool |
|----------|------------------|----|
| C# / .NET | `using` + `.csproj` references | NDepend, dotnet-depends |
| Java | `import` + Maven/Gradle | JDepend, ArchUnit |
| TypeScript/JS | `import`/`require` + package.json | Madge, dependency-cruiser |
| Python | `import` + pyproject.toml | pydeps, import-linter |
| Go | `import` + go.mod | `go mod graph`, govulncheck |
| Rust | `use` + Cargo.toml | cargo-depgraph, cargo-tree |

**Granularity:** < 10 modules → module level. 10–50 → module level grouped by layer. 50–200 → layer/bounded context first. 200+ → subsystem level, then drill down.

Reference files: [Coupling Metrics Reference](references/coupling-metrics.md) | [Visualization Patterns](references/visualization-patterns.md)
