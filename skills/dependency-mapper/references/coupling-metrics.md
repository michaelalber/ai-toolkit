# Coupling Metrics Reference

> "The granule of reuse is the granule of release."
> -- Robert C. Martin

This reference explains Robert C. Martin's package coupling metrics as defined in
*Agile Software Development: Principles, Patterns, and Practices* (2003) and
*Clean Architecture* (2017). These metrics quantify the dependency structure
of a system at the package (module, assembly, namespace) level.

## The Six Metrics

### Ca -- Afferent Coupling (Incoming)

**Definition:** The number of modules outside this module that depend on types
within this module.

**Interpretation:** Ca measures responsibility. A module with high Ca is
depended upon by many others. Changes to this module ripple outward.

**Example:**
```
Module: Authentication
  - UserService imports Authentication.TokenValidator
  - OrderService imports Authentication.AuthContext
  - AdminPanel imports Authentication.RoleChecker
  Ca = 3
```

High Ca means: this module is load-bearing. Treat changes carefully.
Low Ca means: few modules care about this one. Changes are low-risk.

### Ce -- Efferent Coupling (Outgoing)

**Definition:** The number of modules outside this module that this module
depends on.

**Interpretation:** Ce measures dependency. A module with high Ce depends on
many other modules. It is sensitive to changes elsewhere.

**Example:**
```
Module: ReportGenerator
  - imports DataAccess (for queries)
  - imports Formatting (for output)
  - imports Authentication (for access control)
  - imports Logging (for audit trail)
  Ce = 4
```

High Ce means: this module is vulnerable to changes in its dependencies.
Low Ce means: this module is self-contained.

### I -- Instability

**Formula:** `I = Ce / (Ca + Ce)`

**Range:** 0.0 (maximally stable) to 1.0 (maximally unstable)

**Special case:** If Ca + Ce = 0, the module has no dependencies in either
direction. By convention, I = 0 (treat isolated modules as stable).

**Interpretation:**
- I = 0.0: Nothing this module depends on can change without affecting it,
  BUT many things depend on it. It resists change because change is costly.
- I = 1.0: This module depends on others but nothing depends on it. It can
  change freely because no one is affected.
- I = 0.5: Balanced -- equal incoming and outgoing coupling.

**Worked examples:**

```
Module: Domain (Core business logic)
  Ca = 7 (seven modules import from Domain)
  Ce = 1 (Domain imports only a logging abstraction)
  I = 1 / (7 + 1) = 0.125
  Interpretation: Very stable. Changes here affect 7 other modules.

Module: WebAPI (HTTP controllers)
  Ca = 0 (nothing imports from WebAPI)
  Ce = 5 (WebAPI imports Domain, Auth, Validation, Mapping, Config)
  I = 5 / (0 + 5) = 1.000
  Interpretation: Maximally unstable. Can change freely; nothing depends on it.

Module: SharedUtilities
  Ca = 4 (four modules import from SharedUtilities)
  Ce = 3 (SharedUtilities imports Logging, Config, Serialization)
  I = 3 / (4 + 3) = 0.429
  Interpretation: Moderately stable. Changes require care.
```

### A -- Abstractness

**Formula:** `A = Na / Nc`

Where:
- Na = number of abstract types (interfaces, abstract classes, pure virtual classes)
- Nc = total number of types (classes, interfaces, structs, enums) in the module

**Range:** 0.0 (fully concrete) to 1.0 (fully abstract)

**Worked example:**

```
Module: Domain
  Types: IOrderRepository (abstract), IPaymentGateway (abstract),
         Order (concrete), OrderLine (concrete), Money (concrete),
         OrderStatus (enum)
  Na = 2, Nc = 6
  A = 2 / 6 = 0.333

Module: Infrastructure
  Types: SqlOrderRepository (concrete), StripePaymentGateway (concrete),
         DbContext (concrete), MigrationRunner (concrete)
  Na = 0, Nc = 4
  A = 0 / 4 = 0.000
```

### D -- Distance from the Main Sequence

**Formula:** `D = |A + I - 1|`

**Range:** 0.0 (on the Main Sequence) to ~0.707 (maximally distant, at corners)

**Interpretation:** D measures how well a module balances stability with
abstractness. The ideal is D = 0, meaning the module sits exactly on the
Main Sequence line.

**Practical thresholds:**

| D Value | Assessment |
|---------|------------|
| 0.0 - 0.1 | Excellent -- on or very near the Main Sequence |
| 0.1 - 0.3 | Acceptable -- minor deviation |
| 0.3 - 0.5 | Investigate -- may indicate a design issue |
| 0.5+ | Action needed -- module is in the Zone of Pain or Uselessness |

## The Main Sequence

The Main Sequence is the line from point (I=0, A=1) to point (I=1, A=0) on
the I-A graph. It represents the ideal balance:

- **Stable modules should be abstract** (so they can be extended without modification)
- **Unstable modules should be concrete** (they change freely, no need for abstraction overhead)

```
  A (Abstractness)
  1.0 ┤ *                          Ideal stable module:
      │   *                        I=0, A=1 (pure abstractions,
  0.8 ┤     *                      everyone depends on them)
      │       *
  0.6 ┤         *
      │           * <-- Main Sequence (A + I = 1)
  0.4 ┤             *
      │               *
  0.2 ┤                 *
      │                   *        Ideal unstable module:
  0.0 ┤                     *      I=1, A=0 (concrete implementations,
      └──┬──┬──┬──┬──┬──┬──┬──┤   nothing depends on them)
        0.0   0.2  0.4  0.6  1.0
                I (Instability)
```

## Zone of Pain (High Stability, Low Abstractness)

**Location:** Bottom-left corner (I near 0, A near 0)

**Characteristics:** The module is concrete (no abstractions) but highly
stable (many modules depend on it). This means many modules depend on
concrete implementations, making change painful.

**Why it hurts:** You cannot extend the module through abstraction (because
there are no abstractions). You cannot change it freely (because too many
things depend on it). You are stuck.

**Common occupants:**
- Database schema modules with no repository abstraction
- Configuration classes depended on by the entire system
- Utility modules with static methods and no interfaces

**Exception:** Some modules belong here legitimately. String, List, and
other foundational library types are concrete and stable, but they are
so mature that they rarely change. Volatility matters: a concrete, stable
module that never changes is not in pain.

## Zone of Uselessness (High Instability, High Abstractness)

**Location:** Top-right corner (I near 1, A near 1)

**Characteristics:** The module is highly abstract (mostly interfaces) but
maximally unstable (nothing depends on it). The abstractions serve no one.

**Why it is useless:** Abstractions exist to provide extension points for
stable modules. If nothing depends on the abstractions, they add complexity
without value.

**Common occupants:**
- Interface modules created "just in case"
- Abstract base classes with a single implementation and no dependents
- Plugin interfaces where no plugins were ever written

## Stable Dependencies Principle (SDP)

**Statement:** The dependencies between modules should be in the direction
of stability. A module should only depend on modules that are more stable
than itself.

**Formal criterion:** For every dependency A -> B, I(A) >= I(B).

**Why it matters:** If an unstable module (easy to change) depends on another
unstable module (also easy to change), that is fine -- both can adapt. But
if a stable module (hard to change, many dependents) depends on an unstable
module (likely to change), then every change to the unstable module forces
change in the stable module, which in turn forces change in everything
that depends on the stable module. The cost amplifies.

**Violation example:**

```
Module: Core (I = 0.15, very stable)
Module: Reports (I = 0.80, very unstable)

Dependency: Core --> Reports

VIOLATION: Core (I=0.15) depends on Reports (I=0.80).
Core is more stable than its dependency.
When Reports changes, Core must adapt, and everything that
depends on Core (many modules, because Ca is high) must also adapt.

Fix: Invert the dependency. Define an IReportGenerator interface in Core.
Have Reports implement it. Now Reports --> Core, which satisfies SDP
because I(Reports)=0.80 >= I(Core)=0.15.
```

## Stable Abstractions Principle (SAP)

**Statement:** A module should be as abstract as it is stable. Stable modules
should be abstract so that their stability does not prevent extension.
Unstable modules should be concrete since their instability allows concrete
code to be changed easily.

**Formal criterion:** A module should be near the Main Sequence: D should be
close to 0.

**Why it matters:** A stable concrete module (Zone of Pain) is rigid -- it
cannot be extended through polymorphism and it is too costly to change
directly. A stable abstract module provides extension points: new behavior
can be added by creating new implementations without modifying the module.

**Applying SAP:**

```
Module: PaymentProcessing
  I = 0.10 (very stable, many dependents)
  A = 0.15 (mostly concrete)
  D = |0.15 + 0.10 - 1| = 0.75

This module is in the Zone of Pain. To move it toward the Main Sequence:
  - Extract interfaces for key services (IPaymentProcessor, IRefundHandler)
  - Move concrete implementations to a separate module (PaymentProcessing.Impl)
  - Dependents now depend on PaymentProcessing (abstract) while
    PaymentProcessing.Impl depends on PaymentProcessing

After refactoring:
  PaymentProcessing: I=0.08, A=0.80, D=|0.80+0.08-1|=0.12
  PaymentProcessing.Impl: I=0.85, A=0.05, D=|0.05+0.85-1|=0.10
```

## Computing Metrics from Code

### Step 1: Identify Modules

Modules are the unit of analysis. Choose the right granularity:

| Language | Typical Module Boundary |
|----------|------------------------|
| C# / .NET | Project (assembly / .csproj) |
| Java | Package (top-level or second-level) |
| TypeScript/JS | Directory at a chosen depth, or package.json workspaces |
| Python | Top-level package directory |
| Go | Package (directory) |
| Rust | Crate or top-level module |

### Step 2: Build the Dependency Graph

For each module, scan source files for dependency declarations:

1. Parse import/using/require statements
2. Map each imported type or module to its owning module
3. Record directed edges: importing module -> imported module
4. Ignore self-references (module depending on itself)
5. Cross-reference with build system (project references, package manifests)

### Step 3: Compute Ca and Ce

For each module M:
- Ca(M) = count of distinct modules that have at least one import from M
- Ce(M) = count of distinct modules that M imports from

### Step 4: Compute I, A, D

- I(M) = Ce(M) / (Ca(M) + Ce(M)), or 0 if both are 0
- A(M) = count abstract types in M / count total types in M
- D(M) = |A(M) + I(M) - 1|

### Step 5: Detect Cycles

Run a cycle detection algorithm (e.g., Tarjan's strongly connected components
or DFS with back-edge detection) on the directed dependency graph. Report
each cycle as an ordered list of modules.

### Step 6: Check SDP

For each edge A -> B in the dependency graph:
- If I(A) < I(B), flag as an SDP violation
- Record the delta: I(B) - I(A)
- Higher delta = more severe violation
