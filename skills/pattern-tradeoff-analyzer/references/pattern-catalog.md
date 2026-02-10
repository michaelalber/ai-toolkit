# Pattern Catalog

Quick-reference catalog for pattern tradeoff analysis. Each entry identifies the primary force the pattern resolves, the primary cost it introduces, common confusions, and conditions where the pattern should NOT be used.

This is not a pattern tutorial. It assumes you know what these patterns do. Its purpose is to support pattern SELECTION judgment.

---

## Creational Patterns

### Factory Method

**One-line:** Delegates object creation to subclasses, allowing a class to defer instantiation to its children.

**Primary force resolved:** The calling code needs to create objects but should not know which concrete class to instantiate. Creation logic varies by context.

**Primary cost:** One new class (or method override) per product variant. The creation hierarchy mirrors the product hierarchy, which is coupling in disguise.

**Often confused with:** Abstract Factory (which creates families of related objects, not single objects), Builder (which constructs complex objects step-by-step), and the vague use of "factory" to mean "any method that returns an object."

**When NOT to use:**
- When there are fewer than 3 product variants and no expectation of more. A simple conditional or constructor call is clearer.
- When the creation logic is identical across contexts. The factory adds indirection without value.
- When you control all call sites and can change them freely. The decoupling is unnecessary.

### Abstract Factory

**One-line:** Creates families of related objects without specifying their concrete classes.

**Primary force resolved:** Multiple related objects must be created together consistently (e.g., UI widgets that must match a platform theme -- button + checkbox + dialog from the same family).

**Primary cost:** Explosive class proliferation. Each new product in the family requires changes to every factory implementation. N families times M products = N*M concrete classes plus interfaces.

**Often confused with:** Factory Method (which creates single objects, not families), Dependency Injection containers (which resolve dependencies, not create product families).

**When NOT to use:**
- When the "family" has only 1-2 products. The infrastructure is not justified.
- When products in the family do not actually need to be consistent with each other.
- When a DI container already handles the composition. Abstract Factory on top of DI is redundant.

### Builder

**One-line:** Separates construction of a complex object from its representation, allowing the same construction process to create different representations.

**Primary force resolved:** Object creation requires many parameters, optional configurations, or multi-step assembly where the order matters or varies.

**Primary cost:** A parallel class hierarchy (builder alongside the product) and verbose construction code. For simple objects, the builder is more code than inline construction.

**Often confused with:** Factory Method (which selects WHICH object to create, not HOW to create it), fluent interfaces (which are a syntax style, not the Builder pattern).

**When NOT to use:**
- When the object has fewer than 4-5 parameters and no optional configuration. Use a constructor or named arguments.
- When the construction sequence never varies. The builder's flexibility is unused overhead.
- When the language supports named/default parameters natively (Python, Kotlin, C#). Language features often eliminate the need.

### Singleton

**One-line:** Ensures a class has exactly one instance and provides a global access point to it.

**Primary force resolved:** A resource that is expensive to create, must be shared, and would cause conflicts if duplicated (database connection pools, hardware interfaces, configuration caches).

**Primary cost:** Global mutable state. Hidden coupling between every consumer and the singleton instance. Severely impairs testability -- you cannot substitute or reset state between tests without workarounds.

**Often confused with:** Static classes (which are not instances and cannot implement interfaces), service locator (which provides access to services but does not enforce single-instance), DI-registered singletons (which are lifecycle-managed, not globally accessible).

**When NOT to use:**
- In any codebase with unit tests. Prefer DI container lifetime management.
- When the "single instance" requirement is assumed, not proven. Ask: what actually breaks if there are two?
- When used primarily for convenience of global access rather than instance uniqueness.

---

## Structural Patterns

### Adapter

**One-line:** Converts the interface of a class into another interface clients expect, allowing incompatible interfaces to work together.

**Primary force resolved:** You need to use an existing class but its interface does not match what your code expects. Typically arises at integration boundaries with third-party libraries or legacy code.

**Primary cost:** One wrapper class per adapted interface. If the adapted interface evolves, the adapter must track those changes. Can mask fundamental incompatibilities (different error models, threading assumptions) behind a superficially compatible interface.

**Often confused with:** Facade (which simplifies a complex interface, not translates between interfaces), Decorator (which adds behavior, not translates interfaces), Proxy (which controls access, not translates).

**When NOT to use:**
- When you control both interfaces and can simply change one to match the other.
- When the interfaces differ in semantics, not just signature. An adapter that converts synchronous to asynchronous calls is hiding a fundamental mismatch, not adapting.
- When there are more adapters than direct implementations. That suggests the abstraction is wrong.

### Facade

**One-line:** Provides a simplified interface to a complex subsystem, reducing coupling between clients and the subsystem's internals.

**Primary force resolved:** Clients need to interact with a subsystem but should not be exposed to its internal complexity. The subsystem has many classes and the common use cases need only a fraction of its API.

**Primary cost:** The facade can become a God Object over time as more operations are added. It hides complexity but does not eliminate it -- debugging requires looking through the facade to the subsystem. It can also prevent clients from using advanced subsystem features.

**Often confused with:** Adapter (which translates interfaces, not simplifies them), Mediator (which coordinates between peers, not simplifies access to a subsystem).

**When NOT to use:**
- When clients need fine-grained control over subsystem behavior. The facade's simplification becomes a limitation.
- When the subsystem is not actually complex. Wrapping a simple API in a facade adds indirection without value.
- When the facade becomes a bottleneck for changes -- every new subsystem feature requires a facade update.

### Decorator

**One-line:** Attaches additional responsibilities to an object dynamically, providing a flexible alternative to subclassing for extending functionality.

**Primary force resolved:** You need to add behavior to individual objects at runtime without affecting other objects of the same class. The combinations of behaviors are too numerous for subclassing (the combinatorial explosion problem).

**Primary cost:** Many small objects that are hard to debug because behavior is distributed across a chain. Object identity becomes confusing (the decorated object is not the same reference as the original). Stack depth increases with each decoration layer.

**Often confused with:** Proxy (which controls access, not adds behavior), Adapter (which changes interface, not adds behavior), inheritance (which is compile-time, not runtime).

**When NOT to use:**
- When there are only 1-2 possible extensions. Subclassing or composition is simpler and more debuggable.
- When the extensions interact in complex ways. Decorators assume independent, stackable behaviors.
- When ordering of decorations matters and is hard to enforce. The implicit ordering of a decorator chain is a subtle bug source.

### Proxy

**One-line:** Provides a surrogate or placeholder for another object to control access to it.

**Primary force resolved:** You need to control access to an object -- for lazy initialization, access control, logging, caching, or remote access -- without the client knowing it is not talking to the real object.

**Primary cost:** Added indirection and latency. The proxy must maintain interface compatibility with the real subject, which creates tight coupling to its interface. Proxies can mask performance characteristics (a remote proxy hides network calls behind a local-looking interface).

**Often confused with:** Decorator (which adds behavior, not controls access), Adapter (which changes interface, not controls access), Facade (which simplifies interface, not controls access).

**When NOT to use:**
- When the access control can be handled at the call site with a simple check.
- When the proxy hides a fundamentally different execution model (remote calls disguised as local calls). This leads to fallacy-of-distributed-computing bugs.
- When the real subject's interface changes frequently. The proxy becomes maintenance overhead.

---

## Behavioral Patterns

### Strategy

**One-line:** Defines a family of algorithms, encapsulates each one, and makes them interchangeable at runtime.

**Primary force resolved:** Multiple algorithms can solve the same problem, and the choice between them must be deferred to runtime or configuration. The algorithms vary independently from the clients that use them.

**Primary cost:** One interface plus one class per algorithm variant. Clients must be aware that strategies exist and typically must select or inject one. For a small number of strategies that rarely change, a switch statement is simpler.

**Often confused with:** State (which changes behavior based on internal state transitions, not external selection), Command (which encapsulates a request, not an algorithm), simple polymorphism (which dispatches on type, not on injected behavior).

**When NOT to use:**
- When you have 2-3 algorithms that are stable and known at compile time. An if/else or switch is clearer.
- When the "strategies" share significant logic and differ in only a few lines. Extract the common logic and parameterize the difference.
- When the strategy selection is always the same for a given type. That is polymorphism, not strategy.

### Observer

**One-line:** Defines a one-to-many dependency so that when one object changes state, all dependents are notified and updated automatically.

**Primary force resolved:** Multiple objects need to react to changes in another object, but the source should not know the specifics of its dependents. Decouples the source of events from the consumers.

**Primary cost:** Memory leaks from unremoved subscriptions. Debugging difficulty -- when something goes wrong, the call stack shows the notification mechanism, not the business logic chain. Ordering of notifications is typically undefined. Performance impact with many observers.

**Often confused with:** Mediator (which centralizes communication logic, while Observer distributes it), Event Bus/Aggregator (which decouples via a shared channel, while Observer couples directly to the subject), Pub/Sub (which is typically message-based and possibly asynchronous, while Observer is synchronous method calls).

**When NOT to use:**
- When there is only one observer. Direct method calls or callbacks are simpler.
- When notification ordering matters and is complex. Observer does not guarantee order.
- When observers trigger cascading updates to other observers. This creates hard-to-debug chain reactions.
- When the subscription lifecycle is hard to manage (risk of memory leaks in long-lived applications).

### Command

**One-line:** Encapsulates a request as an object, allowing parameterization of clients with different requests, queueing, logging, and undo operations.

**Primary force resolved:** You need to decouple the invoker of an operation from the object that performs it, and/or you need to support undo, queueing, or logging of operations.

**Primary cost:** One class per command. If commands are trivial (single method calls), the overhead is significant relative to the work done. Command objects must capture all state needed for execution and undo, which can be complex.

**Often confused with:** Strategy (which encapsulates algorithms, not requests), Function objects/lambdas (which are lightweight commands without the undo/logging infrastructure).

**When NOT to use:**
- When you do not need undo, queueing, or logging. A direct method call or lambda is simpler.
- When commands are trivially simple. The class-per-command overhead is not justified for single-line operations.
- When the language has first-class functions. Lambdas and closures often eliminate the need for the Command pattern's class structure.

### Mediator

**One-line:** Defines an object that encapsulates how a set of objects interact, promoting loose coupling by preventing objects from referring to each other directly.

**Primary force resolved:** A set of objects communicate in complex, many-to-many ways. Direct references between them create a tangled web of dependencies that is hard to understand and modify.

**Primary cost:** The mediator becomes a God Object that knows about every colleague. All interaction logic is centralized in one place, which can become a maintenance bottleneck. Testing requires the mediator plus at least the relevant colleagues.

**Often confused with:** Facade (which simplifies a subsystem's interface for external clients, while Mediator coordinates internal communication), Observer (which is one-to-many notification, while Mediator is many-to-many coordination), Event Bus (which is typically simpler and less opinionated than a full Mediator).

**When NOT to use:**
- When the communication is primarily one-to-many (use Observer instead).
- When there are only 2-3 communicating objects. Direct references are simpler.
- When the mediator would just be forwarding calls without adding coordination logic. That is indirection without value.

---

## Architectural Patterns

### Repository

**One-line:** Mediates between the domain and data mapping layers, providing a collection-like interface for accessing domain objects.

**Primary force resolved:** Domain logic should not know about data access mechanics. Queries should be encapsulated and reusable. Data access should be substitutable for testing.

**Primary cost:** An abstraction layer over what might already be an abstraction (e.g., Repository over Entity Framework, which is already a repository/unit-of-work). Custom query methods proliferate as requirements grow. Generic repositories often leak ORM concerns or force awkward query expressions.

**Often confused with:** DAO (Data Access Object, which is more data-centric and less domain-centric), Active Record (which combines domain and persistence, the opposite of Repository), Service Layer (which orchestrates operations, not data access).

**When NOT to use:**
- When using an ORM that already provides repository-like semantics (EF Core's DbContext, Django's QuerySet). Adding Repository over these is a repository over a repository.
- When queries are ad-hoc, complex, and rarely reused (reporting, analytics). Repository's collection metaphor breaks down for complex queries.
- For scripts, tools, or short-lived applications where testability through data access substitution is unnecessary.

### CQRS (Command Query Responsibility Segregation)

**One-line:** Separates read and write models, allowing each to be optimized independently.

**Primary force resolved:** Read and write patterns are fundamentally different in shape, scale, or optimization needs. The read model needs denormalized, query-optimized views. The write model needs normalized, consistency-focused structures.

**Primary cost:** Two models to maintain, synchronize, and deploy. Eventual consistency between read and write sides. Significantly increased infrastructure complexity. Testing must cover both paths and the synchronization between them.

**When NOT to use:**
- For simple CRUD applications where reads and writes have the same shape.
- When the team does not have experience with eventual consistency and its debugging challenges.
- When the data volume and query complexity do not justify the overhead. Most applications work fine with a single model.

### Event Sourcing

**One-line:** Stores the sequence of state-changing events rather than current state, allowing reconstruction of state at any point in time.

**Primary force resolved:** Audit trail requirements, temporal queries ("what was the state at time X"), complex domain event workflows, and the need to replay or reprocess historical events.

**Primary cost:** Dramatically increased storage and query complexity. Rebuilding current state from events is expensive without snapshots. Schema evolution of events is painful. Every query of current state requires either projection maintenance or event replay. Debugging requires understanding the event history, not just current state.

**When NOT to use:**
- When you do not need audit trails, temporal queries, or event replay. The cost is enormous without these specific forces.
- When developers are unfamiliar with the paradigm. The learning curve is steep and errors are costly.
- For CRUD-dominant domains where the history of changes has no business value.
- When you need strong consistency for reads. Event Sourcing naturally leads to eventual consistency.

### Vertical Slice Architecture

**One-line:** Organizes code by feature (vertical slice through all layers) rather than by technical layer (horizontal).

**Primary force resolved:** Features should be independently developable, deployable, and understandable. Changes to one feature should not ripple through shared layers. New team members should be able to understand a feature by reading one directory.

**Primary cost:** Potential code duplication across slices. Shared cross-cutting concerns (logging, auth, validation) must be handled through conventions or middleware rather than shared layers. Discovering shared patterns across slices requires discipline.

**When NOT to use:**
- When features share significant domain logic and duplication would be genuinely harmful (not just uncomfortable).
- For very small applications where layered architecture is simpler and sufficient.
- When the team strongly prefers and is productive with layered architecture and the codebase is not experiencing the forces that vertical slices resolve.
