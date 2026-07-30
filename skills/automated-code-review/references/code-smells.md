# Code Smell Catalog (Fowler)

The canonical checklist for the **maintainability** review category. These are the "Bad Smells
in Code" from Martin Fowler's *Refactoring* (2nd ed., with Kent Beck). A smell is not a bug —
it is a surface indication that usually corresponds to a deeper problem. Name the smell, cite
the line, and name the resolving refactoring.

## The repo overrides

A documented repository standard always wins. Where the project's own conventions
(`CODING_STANDARDS.md`, `CONTRIBUTING.md`, linter config, established patterns) endorse
something this baseline would flag, **suppress the smell** — it is a convention, not a defect.
This is the maintainability-category application of the skill's CONVENTION CALIBRATION
constraint: detect conventions first, and never report an external-standard smell against a
project that has deliberately chosen otherwise. When unsure whether a pattern is intentional,
mark the finding "needs verification" rather than asserting the smell.

## Catalog

Each entry: **smell** — signal to look for → *resolving refactoring(s)*.

### Naming & comprehension
- **Mysterious Name** — a name that doesn't reveal intent (`data`, `tmp`, `Manager`, `handle2`) → *Rename Variable / Function / Field*.
- **Comments** — comments compensating for unclear code (explaining *what*, not *why*) → *Extract Function*, *Rename*, *Introduce Assertion*; keep comments that explain rationale.

### Duplication & change locality
- **Duplicated Code** — the same structure in more than one place → *Extract Function*, *Pull Up Method*, *Slide Statements*.
- **Divergent Change** — one module changed for many different reasons → *Split Phase*, *Extract Class* (one module, one reason to change).
- **Shotgun Surgery** — one change forces many small edits across many modules → *Move Function/Field*, *Combine Functions into Class* (gather what changes together).

### Data & coupling
- **Feature Envy** — a function more interested in another module's data than its own → *Move Function*, *Extract Function*.
- **Data Clumps** — the same group of fields/params travelling together everywhere → *Extract Class*, *Introduce Parameter Object*, *Preserve Whole Object*.
- **Primitive Obsession** — primitives standing in for domain concepts (money as `float`, phone as `string`) → *Replace Primitive with Object*, *Replace Type Code with Subclasses*.
- **Repeated Switches** — the same `switch`/`if-else` on the same condition in many places → *Replace Conditional with Polymorphism*.
- **Global / Mutable Data** — data mutable from anywhere or with an unnecessarily wide scope → *Encapsulate Variable*, *Combine Functions into Class*.
- **Temporary Field** — a field set only in certain circumstances, otherwise empty → *Extract Class*, *Introduce Special Case*.

### Structure & size
- **Long Function** — a function doing too much to hold in your head → *Extract Function*, *Replace Temp with Query*, *Decompose Conditional*.
- **Long Parameter List** — too many parameters to track → *Introduce Parameter Object*, *Preserve Whole Object*, *Replace Parameter with Query*.
- **Large Class** — a class with too many fields/responsibilities → *Extract Class/Subclass*, *Extract Interface*.
- **Lazy Element** — a class/function that no longer earns its existence → *Inline Function/Class*, *Collapse Hierarchy*.
- **Speculative Generality** — machinery built for a future that never arrived ("we might need…") → *Collapse Hierarchy*, *Inline Function/Class*, *Remove Dead Code*.

### Indirection & collaboration
- **Message Chains** — `a.getB().getC().getD()` coupling a caller to a navigation path → *Hide Delegate*, *Extract Function* + *Move Function*.
- **Middle Man** — a class that only delegates to another → *Remove Middle Man*, *Inline Function*.
- **Insider Trading** — modules trading too much private knowledge → *Move Function/Field*, *Hide Delegate*, extract a shared module.
- **Alternative Classes with Different Interfaces** — interchangeable classes with mismatched signatures → *Change Function Declaration*, *Move Function*, *Extract Superclass*.
- **Data Class** — a class that is only fields + getters/setters, no behaviour → move behaviour in via *Move Function*; *Encapsulate Record*.
- **Refused Bequest** — a subclass that ignores most of what it inherits → *Push Down Method/Field*, *Replace Subclass with Delegate*.

## Severity guidance

Smells feed the maintainability category and are severity-calibrated like any finding:
- **High** — Shotgun Surgery, Divergent Change, or Duplicated Code on business-critical logic (change amplification risk).
- **Medium** — Feature Envy, Data Clumps, Primitive Obsession, Long Function on a hot path.
- **Low / Nit** — Mysterious Name, Lazy Element, comment smells in isolated code.

A smell whose refactoring would be riskier than the smell itself is a **Nit** with a note — do
not recommend a large refactor to resolve a cosmetic smell.
