# Smell Severity Reference

## Overview

This reference catalogs code smells ranked by their typical baseline severity, drawn from Martin Fowler's refactoring catalog and augmented with real-world context. Baseline severity represents the smell's impact in a "typical" context -- a production service with moderate change frequency and moderate test coverage. Context modifiers adjust the baseline up or down depending on the specific situation.

---

## 1. Critical Severity -- Baseline

These smells actively cause or imminently threaten production defects. They introduce incorrect behavior, data corruption, or system instability.

### Feature Envy with Mutation

**Description**: A method in class A extensively accesses and MODIFIES fields of class B, bypassing B's encapsulation and validation logic.

**Why critical**: When B's validation rules change, the mutation path through A remains unguarded. This creates a silent correctness bug -- data enters an invalid state through a back door that no one remembers exists.

```python
# Feature Envy with Mutation -- CRITICAL
class OrderService:
    def apply_discount(self, order, discount_code):
        # This method reaches into PaymentDetails and mutates it directly,
        # bypassing PaymentDetails.apply_discount() which has validation.
        details = order.payment_details
        details.subtotal = details.subtotal - (details.subtotal * discount_code.rate)
        details.discount_applied = True
        details.discount_code = discount_code.code
        details.tax = details.subtotal * details.tax_rate  # Recalculates tax manually
        details.total = details.subtotal + details.tax + details.shipping
```

**The danger**: When PaymentDetails adds a maximum discount cap or a minimum order threshold, this method silently bypasses it.

### Long Method with Complex Branching

**Description**: A method exceeding 50-100 lines with high cyclomatic complexity (10+), multiple levels of nesting, and interleaved business rules.

**Why critical**: Each branch is a potential defect site. When branches interact (e.g., a flag set in branch 3 affects behavior in branch 7), the combinatorial explosion makes the method untestable in practice. Developers modifying one branch inadvertently break another.

```java
// Long Method with Complex Branching -- CRITICAL
public Invoice calculateInvoice(Order order, Customer customer, PromotionContext promos) {
    // 180 lines, 14 branches, 3 levels of nesting
    // Mixes discount logic, tax logic, shipping logic, and loyalty points
    // A change to tax rules requires reading the entire method to find
    // all places where tax is calculated or adjusted
}
```

**The danger**: No single developer understands all branches. Changes are made by local reasoning ("I only touched the discount part"), but implicit dependencies between branches cause regressions.

### Circular Dependencies

**Description**: Module A depends on Module B, and Module B depends on Module A (directly or transitively).

**Why critical**: Circular dependencies create deployment coupling (cannot deploy A without B), testing coupling (cannot test A without B), and comprehension coupling (cannot understand A without understanding B). They prevent independent evolution of modules and make the system brittle to change.

```
AuthService --> UserRepository --> AuthService
    ^                                  |
    +------ circular dependency -------+
```

**The danger**: A change to UserRepository's query logic requires redeploying AuthService. A test for AuthService requires a fully configured UserRepository. Build times increase. Deployment failures cascade.

### Shared Mutable State Without Synchronization

**Description**: Multiple threads or requests access and modify the same data structure without locks, atomics, or other synchronization mechanisms.

**Why critical**: This is not a smell -- it is a latent bug. Under low concurrency it works. Under production load it produces corrupted data, lost updates, or crashes. These bugs are notoriously difficult to reproduce and diagnose.

```csharp
// Shared mutable state -- CRITICAL
public class RateLimiter
{
    private Dictionary<string, int> _requestCounts = new();  // No synchronization

    public bool AllowRequest(string clientId)
    {
        if (!_requestCounts.ContainsKey(clientId))
            _requestCounts[clientId] = 0;
        _requestCounts[clientId]++;  // Race condition under concurrent access
        return _requestCounts[clientId] <= 100;
    }
}
```

---

## 2. High Severity -- Baseline

These smells significantly impede development velocity and create conditions where bugs become likely during routine changes.

### Shotgun Surgery

**Description**: A single logical change requires modifications in many different classes or files that are not obviously related.

**Why high**: The probability of missing one of the required changes increases with each additional file. Even experienced developers on the team forget a file. New developers have no chance of knowing all the touch points.

**Typical context**: Pricing rules spread across PriceCalculator, DiscountEngine, TaxService, InvoiceGenerator, and ReportBuilder. Changing the discount model requires touching all five.

### Divergent Change

**Description**: A single class is modified for many different reasons by many different people. It has multiple axes of change.

**Why high**: Merge conflicts are frequent. Changes for one concern (e.g., adding a notification channel) risk breaking an unrelated concern (e.g., user authentication) because they share a class. The class grows without bound.

**Typical context**: A UserService that handles authentication, profile management, notification preferences, and activity logging. Four developers regularly have merge conflicts.

### Inappropriate Intimacy

**Description**: A class accesses the internal implementation details of another class -- reaching into private fields via reflection, depending on internal data structures, or knowing about implementation specifics that should be hidden.

**Why high**: When the internal implementation of the target class changes (as it should be free to do), the intimate class breaks. This creates invisible coupling that does not appear in interface contracts.

**Typical context**: A ReportGenerator that directly reads the internal List<OrderLine> from an Order object instead of using a public aggregation method. When Order switches to a lazy-loaded collection, ReportGenerator throws a NullReferenceException.

### God Class

**Description**: A single class that does too much -- 1000+ lines, 30+ methods, 20+ fields. It is the gravitational center of the module; everything depends on it, and it depends on everything.

**Why high**: God classes cannot be tested in isolation, cannot be understood without significant study time, and create merge conflicts when multiple developers touch them. They resist decomposition because so much depends on them.

### Middle Man (Excessive Delegation)

**Description**: A class that does almost nothing itself but delegates every call to another class. It adds a layer of indirection without adding value.

**Why high only in certain contexts**: High severity when the middle man is in a critical path and adds latency, complexity, or confusion. When developers must trace through 3-4 layers of delegation to find the actual logic, debugging time increases significantly.

---

## 3. Medium Severity -- Baseline

These smells increase cognitive load and slow development but are unlikely to cause defects on their own.

### Long Parameter List

**Description**: A method that takes 5+ parameters, especially when several parameters are of the same type.

**Why medium**: Long parameter lists increase the chance of passing arguments in the wrong order (especially with same-typed parameters). They also signal that the method may be doing too much or that a parameter object should be extracted.

```python
def create_order(customer_id, items, discount_code, tax_rate, shipping_method,
                 currency, locale, warehouse_id):
    # 8 parameters -- which is the currency and which is the locale?
```

### Data Clumps

**Description**: The same group of data items (e.g., first_name, last_name, email) appear together in multiple method signatures or classes.

**Why medium**: Data clumps indicate a missing abstraction. When a new field needs to be added to the group (e.g., phone_number), every occurrence must be updated. They also make method signatures longer and less readable.

### Primitive Obsession

**Description**: Using primitive types (strings, integers, floats) to represent domain concepts that deserve their own type (money, email addresses, postal codes, temperature).

**Why medium**: Primitives carry no validation and no semantics. A string that represents an email can be assigned any string value. A decimal that represents money can have arbitrary precision. Domain rules that should be enforced by the type system are scattered across the codebase as ad-hoc validation.

**Context escalator**: Primitive Obsession for money values in financial calculations is HIGH or CRITICAL, not medium. Floating-point arithmetic on currency produces rounding errors that compound.

### Speculative Generality

**Description**: Abstractions, interfaces, or framework hooks that were added "in case we need them" but have exactly one implementation and no concrete plan for a second.

**Why medium**: Every abstraction has a comprehension cost. Developers reading the code must understand the interface, find the implementation, and reason about why the abstraction exists. When it exists for no current reason, it wastes that cognitive effort.

### Message Chains

**Description**: A chain of method calls that navigates through a series of objects to reach the data needed: `order.getCustomer().getAddress().getCity().getPostalCode()`.

**Why medium**: The calling code is coupled to the entire chain. If any intermediate object changes its structure, the chain breaks. It also violates the Law of Demeter, making the calling code fragile.

### Parallel Inheritance Hierarchies

**Description**: Every time you add a subclass of A, you also have to add a subclass of B. The two hierarchies mirror each other.

**Why medium**: This is a form of duplication at the type level. It creates maintenance overhead and coupling between the hierarchies. Forgetting to add the parallel subclass is a common mistake.

---

## 4. Low Severity -- Baseline

These smells are real but have minimal impact on correctness, velocity, or maintainability.

### Comments Explaining "What" Instead of "Why"

**Description**: Comments that restate what the code does rather than explaining WHY it does it or what business rule it implements.

```python
# Add 1 to counter   <-- "what" -- the code already says this
counter += 1

# Offset by 1 because the legacy billing system uses 1-based month indexing
# and our API uses 0-based. See JIRA-4521 for context.
counter += 1          # <-- "why" -- this is valuable
```

**Why low**: Redundant comments add noise but do not cause bugs. They do indicate that the developer felt the code needed explanation, which may signal a deeper readability issue.

### Switch Statements with Few Cases

**Description**: A switch or if/else chain with 2-4 cases.

**Why low**: Small switch statements are readable and maintainable. The "replace conditional with polymorphism" refactoring is appropriate for 6+ cases or when cases are added frequently. For stable, small switch statements, the polymorphic solution adds unnecessary abstraction.

### Lazy Class

**Description**: A class that does too little to justify its existence. It has 1-2 methods and minimal state.

**Why low**: Lazy classes add a small organizational overhead but rarely cause bugs. They may be the result of over-decomposition or leftover from a previous refactoring. Worth consolidating if you are already modifying the area, but not worth a dedicated refactoring task.

### Temporary Field

**Description**: A field on a class that is only set and used in certain execution paths, remaining null or uninitialized otherwise.

**Why low**: Temporary fields are confusing (you cannot rely on them being set) but in practice cause NullReferenceExceptions that are caught quickly. They indicate a missing method parameter or a missing extract-class refactoring.

---

## 5. Cosmetic Severity -- Baseline

These are style preferences, not code smells. They have zero measurable impact on correctness, velocity, or maintainability. Automate enforcement with linters and formatters. Never spend human review time on these.

### Naming Preferences

Variable named `dt` vs. `dateTime`, `i` vs. `index` in a short loop, `svc` vs. `service`. If the context makes the meaning clear, the abbreviated name is fine.

**When it escalates**: Naming becomes medium severity when a name is actively misleading -- e.g., a variable named `total` that actually contains a subtotal, or a method named `validate` that also persists data.

### Formatting Variations

Braces on same line vs. next line. Spaces vs. tabs. Blank lines between methods. These are solved problems -- use a formatter. If the team does not have a formatter configured, the correct refactoring is "add a formatter to the build pipeline," not "reformat every file manually."

### Import Ordering

Alphabetical, grouped by package, standard library first -- these are formatter settings. Never discuss import ordering in a code review.

### Trailing Whitespace

Invisible and harmless. Configure your editor to strip it automatically.

---

## 6. How Context Changes Severity

The baseline severities above assume a typical context. The following context factors can shift a smell up or down by one or more severity levels.

### Factors That Increase Severity

| Factor | Effect | Example |
|--------|--------|---------|
| High change frequency | +1 to +2 levels | A medium smell in code that changes every sprint becomes high. The cost is paid on every change. |
| Low test coverage | +1 level | A medium smell in untested code becomes high because there is no safety net for regressions during refactoring or during subsequent changes that interact with the smell. |
| Security-sensitive context | +1 to +2 levels | Primitive Obsession for user input in a security context (e.g., using raw strings for SQL parameters) escalates from medium to critical. |
| Financial calculation context | +1 level | Primitive Obsession for money (using float/double instead of a Money type) escalates from medium to high or critical due to rounding errors. |
| Multiple developers working in the area | +1 level | A smell that one developer can work around becomes a trap when 3-4 developers touch the code without shared context. |
| No original author available | +1 level | Smells are harder to work around when the tribal knowledge of why the code is structured this way has left the team. |

### Factors That Decrease Severity

| Factor | Effect | Example |
|--------|--------|---------|
| Code is never modified | -1 to -2 levels | A critical smell in code that has not changed in 2 years and has no planned changes drops to low. The smell is real but the cost is not being paid. |
| High test coverage | -1 level | A high smell in code with 90% coverage and thorough integration tests drops to medium. Tests contain the blast radius of defects. |
| Code is scheduled for replacement | -1 to -2 levels | Any smell in a module being rewritten next quarter drops to cosmetic. Do not refactor what you are about to delete. |
| Single developer owns the module | -1 level | Some smells (like Shotgun Surgery) are less dangerous when one person has full context. The risk is knowledge silos, but the immediate defect risk is lower. |
| Read-only code path | -1 level | Feature Envy without mutation (read-only access to another object's data) is less dangerous than Feature Envy with mutation. |

---

## 7. Smell Interactions -- Compounding Effects

Individual smells are evaluated at their baseline severity, but smells interact. Two medium smells in the same module can compound into a critical problem.

### Long Method + Shotgun Surgery

**Individual severities**: Long Method (high), Shotgun Surgery (high).

**Combined effect**: CRITICAL. A long method that is also part of a shotgun surgery pattern means that every change requires understanding 100+ lines of complex code AND finding all the other files that need the same change. The probability of a correct change drops dramatically.

### Primitive Obsession + Duplicated Validation

**Individual severities**: Primitive Obsession (medium), duplicated code (medium).

**Combined effect**: HIGH. When a domain concept is represented as a primitive, its validation logic is duplicated everywhere the primitive is used. When the validation rules change, every duplication site must be updated. Missing one site is a defect.

**Example**: Email represented as a string. Email format validation appears in UserRegistration, ContactForm, InvitationService, and AdminPanel. When the validation regex is updated, one of the four locations is missed.

### Feature Envy + No Tests

**Individual severities**: Feature Envy (high with mutation, medium without), no tests (context modifier, +1 level).

**Combined effect**: CRITICAL. Feature Envy creates hidden coupling. Without tests, changes to either class cannot be verified. The combination means that a change to the target class silently breaks the envious class, and no test catches it until production.

### Divergent Change + God Class

**Individual severities**: Divergent Change (high), God Class (high).

**Combined effect**: CRITICAL. A God Class that is also subject to divergent change is the single most expensive smell combination in a codebase. Every developer on the team is working in the same 2000-line file for different reasons, creating constant merge conflicts, and every change risks breaking an unrelated feature because concerns are not separated.

### Speculative Generality + Inappropriate Intimacy

**Individual severities**: Speculative Generality (medium), Inappropriate Intimacy (high).

**Combined effect**: HIGH (amplified). The abstraction was added speculatively, so it does not actually hide the right details. Clients reach around the abstraction to access implementation details because the abstraction does not serve their needs. This is worse than no abstraction -- it creates a false sense of encapsulation.

### Data Clumps + Long Parameter List

**Individual severities**: Data Clumps (medium), Long Parameter List (medium).

**Combined effect**: MEDIUM-HIGH. The same group of parameters appears in many method signatures, making each signature long. Extracting a parameter object solves both smells simultaneously. The compound effect is higher because the solution is simple and the improvement is multiplicative.

---

## 8. Smell Detection Checklist

Use this checklist when examining code during a refactor-challenger exercise:

```
COUPLING SMELLS (check first -- highest typical severity):
  [ ] Feature Envy -- Does any method use more of another class's data than its own?
  [ ] Inappropriate Intimacy -- Does any class access another class's internals?
  [ ] Shotgun Surgery -- Does a single logical change require modifying multiple files?
  [ ] Circular Dependencies -- Do any modules depend on each other?

COMPLEXITY SMELLS (check second):
  [ ] Long Method -- Any methods over 30 lines with branching?
  [ ] God Class -- Any classes over 500 lines or with 20+ methods?
  [ ] Divergent Change -- Is any class modified for multiple unrelated reasons?
  [ ] Complex Conditional -- Any nested if/else deeper than 3 levels?

ABSTRACTION SMELLS (check third):
  [ ] Primitive Obsession -- Are domain concepts represented as primitives?
  [ ] Data Clumps -- Do the same parameters appear together in multiple places?
  [ ] Long Parameter List -- Any methods with 5+ parameters?
  [ ] Parallel Inheritance -- Do type hierarchies mirror each other?

DUPLICATION SMELLS (check fourth):
  [ ] Copy-paste code -- Are similar code blocks repeated in multiple locations?
  [ ] Duplicated validation -- Is the same validation logic in multiple places?
  [ ] Duplicated conditional -- Is the same if/else structure repeated?

NAMING/READABILITY SMELLS (check last -- lowest typical severity):
  [ ] Misleading names -- Do any names actively misrepresent what the code does?
  [ ] Comments explaining "what" -- Are comments restating the code?
  [ ] Dead code -- Are there unreachable methods or unused variables?
  [ ] Inconsistent naming -- Does the same concept have different names?
```
