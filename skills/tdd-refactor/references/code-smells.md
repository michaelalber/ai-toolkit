# Code Smells Reference

## What Are Code Smells?

Code smells are surface indications that usually correspond to deeper problems in the system. They're not bugs — the code works — but they suggest the design could be improved.

## Smell Categories

### Bloaters

Code that has grown too large.

#### Long Method

**Signs**:
- Method exceeds 10-20 lines
- Multiple levels of abstraction
- Comments explaining sections

**Why It's Bad**:
- Hard to understand
- Hard to modify
- Hard to test in isolation

**Remedies**:
- Extract Method
- Replace Temp with Query
- Replace Method with Method Object

#### Long Parameter List

**Signs**:
- More than 3-4 parameters
- Parameters that always appear together
- Boolean flag parameters

**Why It's Bad**:
- Hard to understand what each parameter does
- Easy to get order wrong
- Method is probably doing too much

**Remedies**:
- Introduce Parameter Object
- Replace Parameter with Method Call
- Preserve Whole Object

#### Large Class

**Signs**:
- Too many instance variables
- Too many methods
- Class name has "And" or "Manager"

**Why It's Bad**:
- Violates Single Responsibility
- Hard to understand
- Changes ripple through

**Remedies**:
- Extract Class
- Extract Subclass
- Extract Interface

#### Primitive Obsession

**Signs**:
- Using primitives for domain concepts (e.g., string for email)
- Constants for coding information
- Type codes

**Why It's Bad**:
- Logic scattered throughout codebase
- Validation duplicated
- No type safety

**Remedies**:
- Replace Primitive with Object
- Replace Type Code with Class
- Replace Type Code with Subclasses

### Object-Orientation Abusers

Misapplication of OO principles.

#### Switch Statements

**Signs**:
- Switch on type code
- Similar switches in multiple places
- Adding new type requires changing many switches

**Why It's Bad**:
- Violates Open-Closed Principle
- Duplication
- Easy to miss a case

**Remedies**:
- Replace Conditional with Polymorphism
- Replace Type Code with Strategy/State

#### Refused Bequest

**Signs**:
- Subclass doesn't use inherited methods
- Subclass overrides to throw exception
- Subclass ignores parent's interface

**Why It's Bad**:
- Inheritance hierarchy is wrong
- Violates Liskov Substitution

**Remedies**:
- Replace Inheritance with Delegation
- Push Down Method/Field

#### Temporary Field

**Signs**:
- Field only set in certain circumstances
- Null checks for field throughout code
- Field used by one method

**Why It's Bad**:
- Object state is confusing
- Field shouldn't be part of object

**Remedies**:
- Extract Class
- Introduce Null Object

### Change Preventers

Code that makes changes harder than necessary.

#### Divergent Change

**Signs**:
- One class changed for different reasons
- Different sections of class change at different times
- "...and then I have to change this other thing"

**Why It's Bad**:
- Class has multiple responsibilities
- Changes are scattered

**Remedies**:
- Extract Class

#### Shotgun Surgery

**Signs**:
- One change requires edits in many classes
- Same type of change in multiple places
- Fear of missing a spot

**Why It's Bad**:
- Changes are scattered
- Easy to introduce bugs

**Remedies**:
- Move Method
- Move Field
- Inline Class (combine fragments)

#### Parallel Inheritance Hierarchies

**Signs**:
- Adding subclass requires adding another subclass elsewhere
- Similar class hierarchies

**Why It's Bad**:
- Duplication
- Easy to forget parallel change

**Remedies**:
- Move Method/Field to eliminate one hierarchy

### Dispensables

Code that should be removed.

#### Comments

**Signs**:
- Comments explaining what code does
- Commented-out code
- TODOs that never get done

**Why It's Bad**:
- Comments go stale
- May hide poor code
- Adds noise

**Remedies**:
- Extract Method (use name as documentation)
- Rename (make code self-documenting)
- Just delete commented code

#### Duplicate Code

**Signs**:
- Same expression in multiple methods
- Same code in sibling classes
- Similar algorithms with variations

**Why It's Bad**:
- Bug fixes must be applied multiple times
- Easy to miss a copy

**Remedies**:
- Extract Method
- Extract Class
- Pull Up Method

#### Dead Code

**Signs**:
- Unused variables
- Unreachable code
- Methods never called
- Classes never instantiated

**Why It's Bad**:
- Clutters codebase
- Maintenance burden
- Confusion about intent

**Remedies**:
- Delete it (tests will catch if needed)

#### Speculative Generality

**Signs**:
- Hooks for future use
- Abstract classes with one subclass
- Parameters that are always the same
- Methods only called by tests

**Why It's Bad**:
- YAGNI — adds complexity for no benefit
- Makes current code harder to understand

**Remedies**:
- Collapse Hierarchy
- Inline Class
- Remove Parameter
- Rename Method (remove "abstract" prefix)

### Couplers

Code with excessive coupling.

#### Feature Envy

**Signs**:
- Method uses many methods/fields from another class
- Method seems misplaced
- Data and behavior separated

**Why It's Bad**:
- Violates encapsulation
- Changes in one class break another

**Remedies**:
- Move Method
- Extract Method (then Move)

#### Inappropriate Intimacy

**Signs**:
- Classes know too much about each other
- Bidirectional associations
- One class uses private parts of another

**Why It's Bad**:
- Tight coupling
- Changes ripple

**Remedies**:
- Move Method/Field
- Extract Class (for shared code)
- Replace Inheritance with Delegation

#### Message Chains

**Signs**:
- `a.getB().getC().getD().doSomething()`
- Long chains of getters
- Navigation through object graph

**Why It's Bad**:
- Fragile — intermediate object change breaks chain
- Exposes object structure

**Remedies**:
- Hide Delegate
- Extract Method (then Move)

#### Middle Man

**Signs**:
- Class mostly delegates to another
- Methods just pass through
- Indirection without value

**Why It's Bad**:
- Adds complexity
- No real abstraction

**Remedies**:
- Remove Middle Man
- Inline Method

## Smell Detection Checklist

Use during REFACTOR phase:

```
Quick Smell Check:
├── Any methods over 10 lines?
├── Any classes over 200 lines?
├── Any method with > 3 parameters?
├── Any primitives representing domain concepts?
├── Any duplicate code blocks?
├── Any commented-out code?
├── Any switch statements on type?
├── Any class doing too many things?
├── Any method using mostly another class's data?
└── Any unused code?
```

If any "yes", consider refactoring before adding new features.
