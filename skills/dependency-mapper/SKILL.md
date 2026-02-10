---
name: dependency-mapper
description: Coupling visualization with Robert C. Martin stability metrics — makes architectural decisions visible as dependency patterns. Use to analyze module dependencies, detect circular references, and understand architectural health through quantitative metrics.
---

# Dependency Mapper

> "The dependencies between packages must not form cycles. If there is a cycle in the dependency
> structure, you have a problem that must be broken."
> -- Robert C. Martin, *Agile Software Development: Principles, Patterns, and Practices*

## Core Philosophy

Architecture is not what you draw on a whiteboard -- it is the dependency structure in your code. This skill makes that structure visible and measurable. Using Robert C. Martin's package coupling metrics (afferent/efferent coupling, instability, abstractness), you learn to see dependency patterns as architectural decisions -- and to recognize when those decisions have drifted from intent.

Every `import`, `using`, `require`, or `#include` statement is an architectural vote. Collectively, these votes determine your system's flexibility, testability, and change propagation characteristics. Most developers have a mental model of their architecture that diverges significantly from reality. This skill closes that gap with numbers.

**What this skill is:** A coaching framework that teaches you to read dependency structure as architecture, compute Robert C. Martin's package metrics, and act on the patterns they reveal.

**What this skill is not:** An automated refactoring tool. It will not rewrite your code. It will show you the truth of your dependency structure and coach you through understanding what it means.

**Why metrics before opinions:** Developers often argue about coupling in abstract terms. Metrics end these arguments by providing a shared vocabulary. When you can say "Module X has I=0.92 and depends on Module Y which has I=0.15, violating the Stable Dependencies Principle," the conversation shifts from opinion to engineering.

## Domain Principles

| # | Principle | Description |
|---|-----------|-------------|
| 1 | **Dependencies Reveal Architecture** | The actual dependency graph IS the architecture, regardless of documentation or diagrams. If the code says module A depends on module B, that is the architectural truth. |
| 2 | **Measure Before Judging** | Compute Ca, Ce, I, A, and D before forming opinions about module quality. Intuition about coupling is frequently wrong; metrics correct the record. |
| 3 | **Stable Dependencies Principle** | A module should only depend on modules that are MORE stable than itself. Formally: the I (instability) of the depender should be greater than or equal to the I of the dependee. |
| 4 | **Stable Abstractions Principle** | Stable modules (low I) should be abstract (high A). Unstable modules (high I) should be concrete (low A). This ensures that stable modules can be extended without modification. |
| 5 | **Acyclic Dependencies Principle** | The dependency graph between modules must be a Directed Acyclic Graph (DAG). Cycles create coupling chains where a change in any member of the cycle potentially affects every other member. |
| 6 | **Instability Is Not Bad** | A module with I=1.0 (maximally unstable) is not defective. It means the module depends on others but nothing depends on it. Leaf modules, UI layers, and application entry points naturally have high instability. This is correct and expected. |
| 7 | **Coupling Has Direction** | The direction of a dependency matters as much as its existence. A depends on B is architecturally different from B depends on A. Reversing a dependency often requires introducing an abstraction. |
| 8 | **Abstractness Has Cost** | High abstractness (many interfaces, few implementations) adds indirection. Abstractness is justified when it supports the Stable Abstractions Principle. Abstractness without stability is ceremony without benefit. |
| 9 | **The Main Sequence** | The ideal relationship between I and A follows the line A + I = 1. Distance from this line (D) measures how well a module balances stability with abstractness. D=0 is ideal; D approaching 0.7+ demands attention. |
| 10 | **Circular Dependencies Are Urgent** | Cycles in the dependency graph are not technical debt to be tracked -- they are structural defects that compound over time. Every cycle should be understood, and most should be broken. |

## Workflow: CACR Interaction Loop

This skill uses the **Challenge - Attempt - Compare - Reflect** coaching loop.

### Phase 1: Challenge

The coach presents a real project (the user's own codebase or a provided example) and asks the user to analyze its dependency structure.

**Coach actions:**
1. Identify the project path, language, and build system
2. Enumerate the top-level modules/packages/namespaces
3. Frame the challenge: "Before I analyze this project, tell me what you think the dependency structure looks like."

**Challenge prompt template:**
```
I see [N] modules in this project: [list].

Before I compute the metrics, I want you to:
1. Sketch the dependency direction between these modules (who depends on whom)
2. Predict which module has the highest instability (I)
3. Predict which module has the lowest instability
4. Predict whether any circular dependencies exist
5. Identify the module you think is closest to the Main Sequence

Take your time. This is about building intuition, not speed.
```

### Phase 2: Attempt

The user provides their predictions about the dependency structure, coupling patterns, and potential problem areas.

**Coach actions during Attempt:**
- Do NOT correct the user yet
- Ask clarifying questions if predictions are vague
- Record the user's predictions for comparison
- Encourage the user to explain their reasoning

**Key questions to prompt deeper thinking:**
- "Why do you think that module has high instability?"
- "What makes you suspect a cycle between those two?"
- "Which dependency direction surprised you most as you thought about it?"

### Phase 3: Compare

The coach presents the actual metrics computed from the codebase.

**Coach actions:**
1. Scan the project source for import/dependency statements
2. Build the dependency graph
3. Compute Ca, Ce, I, A, D for each module
4. Detect circular dependencies
5. Present results alongside the user's predictions

**Comparison output structure:**
```
## Dependency Analysis Results

### Module Metrics

| Module | Ca | Ce | I | A | D | Your Prediction |
|--------|----|----|---|---|---|-----------------|
| ...    | .. | .. | . | . | . | ...             |

### Dependency Graph
[text-based directed graph]

### Circular Dependencies
[list of cycles found, or "None detected"]

### Stable Dependencies Principle Violations
[list of dependencies where I(depender) < I(dependee)]

### Main Sequence Analysis
[modules with D > 0.3, categorized by Zone of Pain or Zone of Uselessness]

### Your Predictions vs Reality
[side-by-side comparison highlighting where intuition matched and diverged]
```

### Phase 4: Reflect

The coach guides the user through interpreting the results and planning improvements.

**Reflection questions:**
1. "Where did your predictions match reality? What gave you accurate intuition?"
2. "Where did your predictions diverge? What assumptions were wrong?"
3. "Looking at the SDP violations, which of these dependencies are intentional design decisions vs accidental coupling?"
4. "If you could change ONE dependency to improve the architecture, which would it be and why?"
5. "Which circular dependency (if any) is most urgent to break? What strategy would you use?"

**Coach actions during Reflect:**
- Help the user distinguish intentional coupling from accidental coupling
- Prioritize violations by impact, not by metric severity
- Suggest concrete refactoring strategies for the most impactful changes
- Record insights for the architecture journal if that skill is active

## State Block

Maintain state across conversation turns using this block:

```
<dependency-state>
mode: scan | analyze | predict | reflect
project_path: [absolute path to project root]
language: [primary language detected]
modules_analyzed: [count of modules/packages scanned]
circular_deps_found: [count of circular dependency cycles]
instability_violations: [count of SDP violations]
main_sequence_distance: [average D across all modules]
last_action: [what was just completed]
next_action: [what should happen next in the CACR loop]
</dependency-state>
```

**State transitions:**

```
┌───────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│ CHALLENGE │────>│ ATTEMPT │────>│ COMPARE │────>│ REFLECT │
│  (scan)   │     │(predict)│     │(analyze)│     │(reflect)│
└───────────┘     └─────────┘     └─────────┘     └─────────┘
      ^                                                 │
      └─────────────────────────────────────────────────┘
                    (next module or project)
```

## Output Templates

### Template 1: Dependency Scan Report

```markdown
## Dependency Scan: [Project Name]

**Project:** [path]
**Language:** [language]
**Modules Found:** [count]
**Scan Date:** [date]

### Module Inventory

| Module | Files | Public Types | Abstract Types | Dependencies |
|--------|-------|-------------|----------------|--------------|
| ...    | ...   | ...         | ...            | ...          |

### Raw Dependency List

[ModuleA] --> [ModuleB]
[ModuleA] --> [ModuleC]
[ModuleB] --> [ModuleD]
...
```

### Template 2: Metrics Table

```markdown
## Package Coupling Metrics

| Module | Ca | Ce | I | A | D | Zone |
|--------|----|----|-------|-------|-------|------|
| Core   | 8  | 1  | 0.111 | 0.750 | 0.139 | --   |
| Data   | 3  | 4  | 0.571 | 0.200 | 0.229 | --   |
| Web    | 0  | 6  | 1.000 | 0.000 | 0.000 | --   |
| Shared | 6  | 5  | 0.455 | 0.100 | 0.445 | Pain |

**Legend:**
- Ca: Afferent Coupling (incoming dependencies)
- Ce: Efferent Coupling (outgoing dependencies)
- I: Instability = Ce / (Ca + Ce), range [0,1]
- A: Abstractness = abstract types / total types, range [0,1]
- D: Distance from Main Sequence = |A + I - 1|, range [0,1]
- Zone: "Pain" if I<0.2 and A<0.2; "Useless" if I>0.8 and A>0.8
```

### Template 3: Circular Dependency Visualization

```markdown
## Circular Dependencies Detected

### Cycle 1: [ModuleA] <-> [ModuleB] <-> [ModuleC]

    ┌──────────┐
    │ ModuleA  │
    └────┬─────┘
         │ depends on
         v
    ┌──────────┐
    │ ModuleB  │
    └────┬─────┘
         │ depends on
         v
    ┌──────────┐
    │ ModuleC  │
    └────┬─────┘
         │ depends on
         │
         └──────────> back to ModuleA [CYCLE]

**Impact:** A change in any of these three modules may force recompilation
and retesting of all three. Independent deployment is impossible.

**Breaking strategies:**
1. Dependency Inversion: Extract interface from [ModuleA] into a shared
   abstractions module that [ModuleC] depends on instead
2. Merge: If the cycle is tight, these modules may belong together
3. Callback/Event: Replace the back-edge with an event mechanism
```

### Template 4: Main Sequence Chart (Text-Based)

```markdown
## Main Sequence Chart

  A (Abstractness)
  1.0 ┤ Zone of            /
      │ Uselessness       /
  0.8 ┤                  /  [Core]
      │                 /
  0.6 ┤               /
      │              /
  0.4 ┤            /
      │           /
  0.2 ┤     [Shared]     [Data]
      │        /
  0.0 ┤──────/──────────────── [Web]
      └──┬──┬──┬──┬──┬──┬──┬──┤
        0.0   0.2  0.4  0.6  0.8  1.0
                I (Instability)

The Main Sequence is the diagonal line from (0,1) to (1,0).
Distance from this line (D) measures architectural balance.
```

### Template 5: Violation List

```markdown
## Stable Dependencies Principle Violations

| Depender | I(depender) | Dependee | I(dependee) | Delta |
|----------|-------------|----------|-------------|-------|
| Data     | 0.571       | Shared   | 0.455       | 0.116 |
| ...      | ...         | ...      | ...         | ...   |

**Interpretation:** [Depender] has instability [X] but depends on
[Dependee] with instability [Y]. Since I(depender) < I(dependee),
the depender is more stable than its dependency. This means changes
in the less-stable dependee will ripple into the more-stable depender,
violating the principle that dependencies should point toward stability.

**Severity:** Violations with Delta > 0.3 are high priority.
Violations with Delta < 0.1 may be acceptable depending on context.
```

### Template 6: Refactoring Suggestions

```markdown
## Recommended Refactorings (Priority Order)

### 1. Break Cycle: [ModuleA] <-> [ModuleB]
**Impact:** High -- affects [N] other modules transitively
**Strategy:** Extract interface [IFoo] from [ModuleA] into [Abstractions]
**Estimated effort:** [Small | Medium | Large]
**Risk:** [Low | Medium | High] -- [explanation]

### 2. Fix SDP Violation: [Data] -> [Shared]
**Impact:** Medium -- [Shared] changes propagate to stable [Data]
**Strategy:** Invert dependency by having [Shared] depend on an
abstraction defined in [Data]
**Estimated effort:** Medium
**Risk:** Medium -- requires updating [N] call sites
```

## AI Discipline Rules

### ALWAYS compute actual metrics from code -- never estimate or guess

Scan the actual source files for import/using/require statements. Count actual types and abstract types. Produce real numbers. If a project is too large to fully scan in one pass, scan a representative subset and clearly state what was included and excluded.

### Present numbers first, interpretation second

Show the metrics table before offering any commentary. Let the user see the raw data. Then provide interpretation. This prevents anchoring the user's thinking with your conclusions before they have examined the evidence.

### Distinguish intentional coupling from accidental coupling

Not all coupling is bad. A web controller depending on a service layer is intentional architecture. A utility module depending on a domain module is likely accidental. Always ask: "Is this dependency here because someone decided it should be, or because it was the path of least resistance?"

### A module with I=1.0 is fine if it is at the edge of the system; context matters

Instability is only a problem when it violates the Stable Dependencies Principle. A maximally unstable module that nothing else depends on (Ca=0) is perfectly positioned -- it can change freely without affecting anything. Do not flag high instability without checking what depends on the module.

### Circular dependencies are always worth discussing -- they indicate architectural confusion

Even when a cycle involves only two modules, it deserves attention. Cycles prevent independent deployment, complicate testing, and create change propagation that is difficult to reason about. The question is not whether to discuss them but how urgently to address them.

### Do not recommend fixing everything -- focus on violations that matter for the system's goals

A system with three SDP violations and one cycle does not need all four addressed immediately. Prioritize by: (1) cycles that cross deployment boundaries, (2) SDP violations involving frequently-changing modules, (3) Zone of Pain modules that are also change hotspots. Leave stable, rarely-modified violations for later.

### Never present metrics without explaining what they mean

Not every user will know what Ca=8 signifies. Always include the legend. Always explain what a violation means in practical terms ("this means a change to X will force you to retest Y").

### Acknowledge when metrics are incomplete

If the analysis could not parse certain files, if dynamic dependencies exist that static analysis cannot capture, or if the project uses dependency injection that obscures the true graph, say so explicitly. Partial truth stated clearly is more valuable than false precision.

## Anti-Patterns

| Anti-Pattern | Why It Fails | Correct Approach |
|--------------|-------------|------------------|
| **Metric Worship** | Optimizing D to zero for every module produces over-abstracted code. Metrics are diagnostic, not prescriptive. | Use metrics to identify areas for investigation, then apply judgment about whether a violation matters in context. |
| **Ignoring Direction** | Treating coupling as symmetric ("A and B are coupled") loses critical architectural information. | Always specify direction: "A depends on B." Direction determines who is affected by changes. |
| **Treating All Coupling Equally** | A dependency on a stable, abstract module is architecturally different from a dependency on a volatile concrete module. | Weight coupling by the instability and volatility of the dependee. Depending on a stable abstraction is cheap; depending on a volatile implementation is expensive. |
| **Refactoring Stable Modules** | Modules with low instability (many dependents) are dangerous to refactor because changes propagate widely. | Refactor unstable modules first. Add abstractions to stable modules only when the Stable Abstractions Principle demands it. |
| **Breaking Cycles by Adding Indirection** | Inserting a "pass-through" module between A and B does not break the cycle if the new module depends on both. It adds complexity without improving structure. | Break cycles by inverting one dependency direction using an abstraction (interface/protocol) or by merging tightly-coupled modules. |
| **Snapshot Analysis Only** | Measuring metrics once provides a snapshot. Architecture drifts over time. | Track metrics across commits or sprints. Trend matters more than absolute values. |
| **Confusing Packages with Classes** | Martin's metrics apply to packages (modules, assemblies, namespaces), not individual classes. Applying them at the wrong granularity produces misleading results. | Apply Ca/Ce/I/A/D at the package or module level. Use class-level coupling metrics (like CBO) for class-level analysis. |
| **Ignoring the Build System** | Some dependency relationships are invisible in source code but present in build configurations (project references, package manifests). | Cross-reference source-level analysis with build system declarations (csproj, package.json, go.mod, Cargo.toml). |

## Error Recovery

### Project too large to analyze fully

**Symptoms:** Hundreds of modules, analysis would take excessive time or produce unreadable output.

**Recovery:**
1. Identify the architectural layers or bounded contexts
2. Analyze one layer or context at a time
3. Then analyze the inter-layer dependencies separately
4. Present a hierarchical view: layer-level metrics first, then module-level within each layer

**Coach response:**
```
This project has [N] modules, which is too many to analyze meaningfully in
one pass. Let's work hierarchically:

1. First, I'll identify the major architectural layers/contexts
2. We'll analyze dependencies BETWEEN layers
3. Then drill into the layer you're most concerned about

Which layer or area of the codebase do you want to focus on?
```

### User does not understand the metrics

**Symptoms:** User's predictions are random or they ask "what does instability mean?" during the Attempt phase.

**Recovery:**
1. Pause the CACR loop
2. Walk through the metrics using a concrete two-module example
3. Provide the coupling-metrics reference
4. Resume with a simpler challenge (fewer modules)

**Coach response:**
```
Let me step back and explain these metrics with a concrete example before
we continue. See [references/coupling-metrics.md] for the full reference.

Consider two modules:
- OrderService: depends on 3 modules, and 2 modules depend on it
  Ca=2, Ce=3, I = 3/(2+3) = 0.60
- Database: depends on 0 modules, and 5 modules depend on it
  Ca=5, Ce=0, I = 0/(5+0) = 0.00

OrderService is unstable (I=0.60) -- it can change relatively freely.
Database is maximally stable (I=0.00) -- everyone depends on it, so
changes are costly.

Now, should OrderService depend on Database, or vice versa?
```

### Metrics look good but architecture feels wrong

**Symptoms:** All modules are near the Main Sequence, no cycles detected, but the user reports the system is hard to change.

**Recovery:**
1. Check for hidden coupling: shared mutable state, database tables as integration points, message queues, configuration files
2. Check granularity: are "modules" actually monolithic packages with internal coupling?
3. Check temporal coupling: must things happen in a specific order across modules?
4. Check for feature envy: are modules reaching into each other's data?

**Coach response:**
```
The metrics look healthy at the package level, but your experience says
otherwise. This usually means one of:

1. **Hidden coupling** not visible in imports (shared DB tables, config,
   environment variables)
2. **Wrong granularity** -- the modules are too coarse and hide internal
   coupling problems
3. **Temporal coupling** -- modules must be deployed or executed in a
   specific order
4. **Feature envy** -- modules access each other's data through shared
   types rather than through clean interfaces

Let's investigate. Which of these resonates with your experience?
```

### User wants to skip prediction and go straight to metrics

**Symptoms:** User says "just show me the numbers."

**Recovery:**
1. Respect the request but explain the pedagogical value
2. Offer a compromise: show metrics first, then ask the user to predict for a SECOND area

**Coach response:**
```
I'll show you the metrics now. But I want to make a case for the
prediction step: research on expert performance shows that calibrating
your intuition against reality is the fastest way to build architectural
judgment.

Here are the metrics. After you review them, I'll ask you to predict
the metrics for a different part of the system.
```

## Integration with Other Skills

| Skill | Integration Point |
|-------|-------------------|
| **architecture-review** | Use dependency-mapper results as quantitative input to architecture reviews. Metrics provide evidence for architectural concerns. |
| **pattern-tradeoff-analyzer** | When dependency-mapper reveals coupling patterns, use pattern-tradeoff-analyzer to evaluate whether introducing a design pattern would improve the structure. |
| **architecture-journal** | Record dependency analysis findings, metric trends, and refactoring decisions in the architecture journal for longitudinal tracking. |
| **technical-debt-assessor** | SDP violations, cycles, and Zone of Pain modules feed directly into technical debt assessment. Use dependency-mapper metrics to quantify coupling-related debt. |
| **refactor-challenger** | When dependency-mapper suggests breaking a cycle or fixing an SDP violation, use refactor-challenger to evaluate the refactoring approach before executing. |
| **code-review-coach** | During code reviews, reference dependency metrics to evaluate whether a change improves or degrades the dependency structure. |

**Workflow example: Architecture Review augmented with Dependency Mapping**

```
1. Start architecture-review session
2. Invoke dependency-mapper to scan the project
3. Present metrics alongside architectural concerns
4. Use metrics to prioritize which concerns have quantitative support
5. Record findings in architecture-journal with metric baselines
6. Track metric changes over subsequent reviews
```

## Stack-Specific Guidance

Detailed reference materials for applying these concepts:

- [Coupling Metrics Reference](references/coupling-metrics.md) -- Complete explanation of Robert C. Martin's package coupling metrics with formulas, examples, and computation approaches
- [Visualization Patterns](references/visualization-patterns.md) -- Text-based dependency graph formats, circular dependency visualization, and tool recommendations per language ecosystem

### Language-Specific Dependency Detection

| Language | Import Mechanism | Detection Approach | Common Tool |
|----------|------------------|--------------------|-------------|
| C# / .NET | `using` + `.csproj` references | Parse project references and using statements | NDepend, dotnet-depends |
| Java | `import` + Maven/Gradle deps | Parse import statements and build files | JDepend, ArchUnit |
| TypeScript/JS | `import`/`require` + package.json | Parse ES module imports and CJS requires | Madge, dependency-cruiser |
| Python | `import`/`from...import` + setup.py/pyproject.toml | Parse import statements and package config | pydeps, import-linter |
| Go | `import` + go.mod | Parse import paths and module declarations | `go mod graph`, govulncheck |
| Rust | `use` + Cargo.toml | Parse use statements and Cargo dependencies | cargo-depgraph, cargo-tree |

### Granularity Guidelines

| Project Size | Recommended Granularity | Rationale |
|-------------|------------------------|-----------|
| < 10 modules | Module (package/namespace) level | Small enough to analyze completely |
| 10-50 modules | Module level, grouped by layer | Group related modules for readability |
| 50-200 modules | Layer/bounded context level first, then drill down | Too many modules for a single metrics table |
| 200+ modules | Subsystem level, then layer, then module | Hierarchical analysis required |
