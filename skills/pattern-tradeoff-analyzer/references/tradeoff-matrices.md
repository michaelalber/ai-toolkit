# Tradeoff Matrices

Structured comparison matrices for common pattern selection decisions. Use these as templates for your own tradeoff analysis.

---

## Tradeoff Dimensions Defined

Every pattern comparison should evaluate these dimensions. Not all dimensions are equally important for every decision -- weighting is context-dependent.

| Dimension | What It Measures | How to Assess |
|-----------|-----------------|---------------|
| **Complexity** | Structural overhead: new types, interfaces, indirection layers, files added | Count the concrete artifacts. "3 new files, 1 interface, 2 implementations" is a fact, not a judgment. |
| **Flexibility** | What future changes become easy and what becomes hard | Name specific change scenarios: "adding a 4th pricing rule" or "switching from SQL to NoSQL." |
| **Testability** | Test isolation, mock/stub requirements, setup complexity | Can you test the core logic without infrastructure? How many mocks does a typical test require? |
| **Performance** | Runtime cost of the abstraction: allocations, indirection, serialization | Only relevant when the code is on a hot path. Most pattern decisions have negligible performance impact. |
| **Team Familiarity** | Can the team read, maintain, and extend this without the original author? | Consider the least experienced team member who will touch this code. |
| **Reversibility** | Cost of undoing the decision if requirements change | A method extraction is trivially reversible. A distributed event system is not. |
| **Cognitive Load** | How much context a developer must hold in their head to understand the flow | Count the files a developer must open to trace a single request from input to output. |

### Weighting by Context

Dimension importance shifts based on project context:

**Startup / Prototype:**
- Highest weight: Reversibility, Complexity (keep it simple, keep it changeable)
- Lowest weight: Performance, Flexibility (optimize later, evolve as needed)

**Growing Product (post-product-market fit):**
- Highest weight: Testability, Team Familiarity (code must survive team growth)
- Lowest weight: Performance (unless you have measured bottlenecks)

**Mature / Regulated System:**
- Highest weight: Testability, Cognitive Load (auditability and maintainability)
- Lowest weight: Reversibility (decisions are costly to reverse regardless)

**High-Performance System (games, trading, embedded):**
- Highest weight: Performance, Complexity (abstraction costs matter here)
- Lowest weight: Flexibility (stability over extensibility)

---

## Example Comparison Matrices

### 1. Service Communication: Mediator vs Direct Injection vs Facade

**Problem:** Service A needs to coordinate work across Services B, C, and D. How should A communicate with them?

**Context:** ASP.NET Core web API, 4 developers, growing feature set, services are in the same process.

| Dimension | Mediator (MediatR) | Direct Injection | Facade Service |
|-----------|-------------------|-----------------|----------------|
| **Complexity** | NuGet package, handler classes per request, pipeline behaviors. ~2 files per operation (request + handler). | Constructor injection of 3 services. 0 new files. | 1 new facade class wrapping B, C, D. 1 file. |
| **Flexibility** | Adding cross-cutting concerns (logging, validation) is trivial via pipeline. New operations are isolated handlers. | Adding concerns requires decoration or middleware. New operations add parameters or methods to A. | Adding concerns requires modifying the facade. New operations add methods to the facade. |
| **Testability** | Each handler is independently testable with no other handlers loaded. | Requires mocking 3 services in every test of A. As dependencies grow, test setup grows. | Requires mocking the facade, which is simpler. But facade itself requires mocking B, C, D. |
| **Performance** | Reflection and dynamic dispatch overhead per request. Negligible in web API context. | Direct method calls. Zero overhead. | Direct method calls through one layer. Negligible overhead. |
| **Team Familiarity** | Team must learn MediatR conventions. Debugging requires understanding the pipeline. | Everyone understands constructor injection. No learning curve. | Simple class composition. Minimal learning curve. |
| **Reversibility** | Removing MediatR requires rewriting all handlers back to direct calls. Moderate cost. | Already the simplest approach. Nothing to reverse. | Inlining the facade is straightforward. Low cost. |
| **Cognitive Load** | Tracing a request requires finding the matching handler by convention. Indirect. | Ctrl+click from A to B, C, D. Direct and obvious. | Ctrl+click from A to facade, then to B, C, D. One extra hop. |

**Key deciding question:** Do you have cross-cutting concerns (logging, validation, authorization) that apply uniformly to many operations, and are you adding new operations frequently? If yes, Mediator. If not, Direct Injection until you feel the pain.

---

### 2. Notification Dispatch: Observer vs Event Aggregator vs Direct Callbacks

**Problem:** When an Order is placed, the system must send an email, update inventory, and log an audit record. How should the OrderService notify these dependents?

**Context:** Monolithic application, 3 known consumers, no expectation of dynamic subscriber registration.

| Dimension | Observer Pattern | Event Aggregator / Bus | Direct Callbacks |
|-----------|-----------------|----------------------|-----------------|
| **Complexity** | Subject interface, observer interface, subscription management in OrderService. ~3-4 new types. | Shared event bus class, event type, subscriber registration. ~3 new types plus infrastructure. | OrderService calls EmailService, InventoryService, AuditService directly. 0 new types. |
| **Flexibility** | Adding a 4th consumer: implement observer interface, register with subject. No changes to OrderService. | Adding a 4th consumer: subscribe to event. No changes to publisher. | Adding a 4th consumer: add a 4th constructor parameter and method call to OrderService. |
| **Testability** | Testing OrderService requires verifying notification calls. Observers test independently. | Publisher and subscribers test fully independently. Event bus can be replaced with a test double. | Testing OrderService requires mocking 3 (then 4, then 5) services. Setup grows linearly. |
| **Performance** | Synchronous iteration over subscriber list. Negligible. | Depends on implementation. Synchronous dispatch is comparable. Async adds latency. | Direct method calls. Zero overhead. |
| **Team Familiarity** | Well-known pattern. Subscription lifecycle (add/remove) is the gotcha. | Requires understanding the bus abstraction. "Where does this event go?" is a common question. | Everyone understands method calls. Maximum familiarity. |
| **Reversibility** | Removing Observer requires inlining calls. Moderate refactor. | Removing the bus requires connecting publishers to subscribers directly. Moderate-to-high cost. | Already the simplest form. Nothing to reverse. |
| **Cognitive Load** | Must understand subscription model. "Who is listening?" requires checking registrations. | Must understand bus routing. "Who handles OrderPlacedEvent?" requires searching for subscribers. | Call stack shows exactly what happens. Minimal cognitive load. |

**Key deciding question:** How many consumers will there be, and how often will new consumers be added? For 3 stable consumers, direct callbacks. If you expect 6+ consumers or frequent additions, Observer or Event Aggregator.

---

### 3. Object Creation: Factory Method vs Abstract Factory vs Builder vs Constructor

**Problem:** Creating report objects that vary by format (PDF, CSV, Excel). Each format requires different configuration.

**Context:** Internal business application, 3 current formats, team of 6, formats change approximately once per year.

| Dimension | Factory Method | Abstract Factory | Builder | Direct Constructor |
|-----------|---------------|-----------------|---------|-------------------|
| **Complexity** | 1 factory interface + 1 implementation per format. 4 new types for 3 formats. | 1 abstract factory + 1 concrete factory per format + product interfaces. 7+ types for 3 formats. | 1 builder interface + 1 builder per format + director. 5 types for 3 formats. | 0 new types. Conditional logic at the call site. |
| **Flexibility** | New format: add 1 factory implementation. No existing code changes. | New format: add 1 factory + all product implementations. No existing code changes. | New format: add 1 builder. No existing code changes. | New format: add a new branch to every conditional. Shotgun surgery. |
| **Testability** | Factories are independently testable. Consumers test against factory interface. | Same as Factory Method but more interfaces to mock. | Builder steps are independently testable. | Testing requires hitting all branches. |
| **Performance** | One virtual dispatch to select the factory. Negligible. | Multiple virtual dispatches. Negligible for this use case. | Multiple method calls for construction. Negligible. | Direct instantiation. Zero overhead. |
| **Team Familiarity** | Widely understood. Low learning curve. | More complex. "Why do we need families?" is a common question here since formats are not families. | Familiar from StringBuilder and HTTP client builders. | Everyone understands constructors and if/else. |
| **Reversibility** | Straightforward to inline back to conditionals. Low cost. | Significant dismantling effort. Moderate cost. | Straightforward to inline. Low cost. | Already the simplest form. |
| **Cognitive Load** | Find the factory, find the implementation. 2 hops. | Find the factory, find the concrete factory, find the products. 3+ hops. | Find the builder, follow the build steps. 2-3 hops. | Read the conditional. 1 location. |

**Key deciding question:** Are there truly product families (related objects that must be consistent), or just single objects that vary? Single varying objects with 3 stable variants = Factory Method or even direct constructor. Product families = Abstract Factory. Complex multi-step construction = Builder.

---

### 4. Data Access: Repository vs Direct ORM vs Query Object

**Problem:** Encapsulating data access for a domain with 12 entity types, a mix of simple CRUD and complex multi-table queries.

**Context:** .NET application using Entity Framework Core. Team of 5. Some developers prefer raw LINQ, others want abstraction.

| Dimension | Repository Pattern | Direct DbContext Injection | Query Object / Specification |
|-----------|-------------------|--------------------------|------------------------------|
| **Complexity** | 1 interface + 1 implementation per entity (or 1 generic + N specific). 12-24 new types. | 0 new types. Inject DbContext where needed. | 1 base query class + 1 query per complex operation. ~8-15 types for the complex queries. |
| **Flexibility** | Changing ORM: rewrite all repository implementations. Adding queries: add methods to repositories. | Changing ORM: rewrite all consumers (scattered LINQ). Adding queries: write them inline. | Changing ORM: rewrite query execution. Adding queries: add a new query class. |
| **Testability** | Mock repository interface. Simple and clean. But mocking masks ORM behaviors (lazy loading, tracking). | Requires in-memory DbContext or integration tests. Tests are more realistic but slower. | Mock query execution. Queries are testable logic. |
| **Performance** | Repository can hide inefficient queries. Generic repositories often prevent query optimization. | Full ORM control. Developer can optimize queries directly. | Queries can be optimized individually without affecting other operations. |
| **Team Familiarity** | Ubiquitous pattern. Every .NET developer has seen it. Opinions vary on whether it adds value over EF. | Requires EF knowledge. No additional abstraction to learn. | Less common. Requires explaining the query object concept. |
| **Reversibility** | Removing repositories: inline queries into consumers. Moderate cost for 12 entities. | Already the simplest form. | Removing query objects: inline into consumers. Lower cost than full repository removal. |
| **Cognitive Load** | Find the repository, find the method, trust the implementation. 2 hops. | Find the query inline. 1 hop. But complex queries clutter business logic. | Find the query object. 1-2 hops. Complex queries are isolated. |

**Key deciding question:** Is the primary goal testability (Repository), query optimization control (Direct DbContext), or complex query encapsulation without full repository overhead (Query Object)? For EF Core specifically: do you gain enough from Repository to justify wrapping an abstraction that is already a repository?

---

### 5. State Management: State Pattern vs Switch/Enum vs State Machine Library

**Problem:** An Order entity transitions through states: Draft, Submitted, Approved, Shipped, Delivered, Cancelled. Each state has different allowed transitions and behaviors.

**Context:** E-commerce backend, 6 states with 10 valid transitions, behaviors differ by state, compliance requires state transition logging.

| Dimension | State Pattern (GoF) | Switch on Enum | State Machine Library (e.g., Stateless) |
|-----------|---------------------|---------------|----------------------------------------|
| **Complexity** | 1 state interface + 6 state classes + context class. 8 new types. | 1 enum + switch statements in relevant methods. 0-1 new types. | 1 library dependency + configuration code. 1-2 new types. |
| **Flexibility** | New state: add 1 class. New behavior: add to interface (affects all states). | New state: add enum value + branches in every switch. New behavior: add a new switch. | New state: add to configuration. New behavior: add trigger or action. |
| **Testability** | Each state class tests independently. Transition logic is localized. | Must test every branch in every switch. State-behavior coupling makes isolation difficult. | Configuration is testable. Library handles transition mechanics. |
| **Performance** | Virtual dispatch per state method call. Negligible for order processing. | Direct branching. Fastest option. Negligible difference in practice. | Library overhead. Negligible for order processing. |
| **Team Familiarity** | Understood in principle but rarely implemented manually in practice. | Everyone understands switch statements. Maximum familiarity. | Requires learning the library API. Moderate learning curve. |
| **Reversibility** | Collapsing back to switch: moderate effort for 6 states. | Already the simplest form. | Removing library: rewrite as switch or state pattern. Moderate cost. |
| **Cognitive Load** | Understanding all states requires reading 6 files. Understanding one state is trivial. | Understanding all behavior requires reading every switch. Understanding one transition requires scanning multiple switches. | Configuration file shows all states and transitions in one place. Low cognitive load for understanding the machine. |

**Key deciding question:** How many states, and does behavior differ significantly per state? For 3 states with simple transitions, switch on enum. For 6+ states with different behaviors per state, State Pattern or State Machine Library. The library wins if you value declarative configuration and transition visualization.

---

### 6. Cross-Cutting Concerns: Decorator Chain vs Middleware Pipeline vs AOP

**Problem:** Need to add logging, validation, retry logic, and caching around service calls. These concerns apply to many services.

**Context:** Microservice with 15 service operations, 4 cross-cutting concerns, .NET with DI container.

| Dimension | Decorator Chain | Middleware Pipeline | AOP (Aspect-Oriented) |
|-----------|----------------|--------------------|-----------------------|
| **Complexity** | 1 decorator class per concern per service interface. 4 concerns times N interfaces = potentially many classes. | 1 middleware class per concern. 4 classes total regardless of service count. | Attribute or configuration per concern. Minimal code, but framework dependency. |
| **Flexibility** | Decorators compose per-service. Can apply different concerns to different services. Fine-grained control. | Pipeline applies uniformly to all requests passing through it. Coarse-grained. | Attributes can be applied selectively per method. Medium granularity. |
| **Testability** | Each decorator tests independently. Clean and isolated. | Each middleware tests independently. Pipeline order tested separately. | Aspects test independently, but verifying they apply correctly requires integration tests. |
| **Performance** | N layers of indirection per call. Negligible for typical service calls. | N middleware hops per request. Negligible for typical service calls. | Compile-time or runtime weaving. Compile-time has zero runtime cost. Runtime has reflection overhead. |
| **Team Familiarity** | Decorator pattern is well-known. DI registration of chains can be confusing. | Middleware is familiar from ASP.NET Core. Natural extension of existing patterns. | AOP is less familiar. "Magic" attribute behavior surprises developers. |
| **Reversibility** | Remove a decorator: change DI registration. Low cost. | Remove middleware: change pipeline configuration. Low cost. | Remove aspect: remove attribute. Low cost. But understanding what was removed requires knowing what the aspect did. |
| **Cognitive Load** | Debugging requires understanding the decorator chain order. N hops to trace through. | Pipeline order is visible in configuration. Standard pattern. | Behavior is implicit. Developers must know to look for aspects. Highest hidden complexity. |

**Key deciding question:** Do cross-cutting concerns apply uniformly to all operations (Middleware) or selectively per-service (Decorator)? Does the team value explicit code over implicit behavior (Decorator/Middleware over AOP)?

---

## Building Your Own Matrix

### Template

Copy this template for your own pattern comparisons:

```markdown
### [Decision Title]: [Option A] vs [Option B] vs [Option C]

**Problem:** [What design tension are you resolving?]

**Context:** [Technology stack, team size, lifecycle stage, specific constraints]

| Dimension | [Option A] | [Option B] | [Option C] |
|-----------|-----------|-----------|-----------|
| **Complexity** | [count files, types, interfaces] | | |
| **Flexibility** | [what changes easily, what is hard] | | |
| **Testability** | [mock requirements, isolation quality] | | |
| **Performance** | [only if on hot path] | | |
| **Team Familiarity** | [who on the team knows this well] | | |
| **Reversibility** | [cost to undo or migrate away] | | |
| **Cognitive Load** | [hops to trace, files to read] | | |

**Key deciding question:** [The one question whose answer determines the right choice]
```

### Process

1. **Start with the problem, not the options.** Write the problem statement first. If you cannot articulate the problem clearly, you are not ready to compare solutions.
2. **Identify the forces.** What varies? What must be stable? What must perform? What might change?
3. **Weight the dimensions.** Not all rows matter equally. Cross out rows that are irrelevant to your context. Star the rows that dominate the decision.
4. **Fill in concrete values.** "Better testability" is not useful. "Requires 0 mocks vs 3 mocks per test" is useful.
5. **Name the deciding question.** There is almost always one question whose answer tips the balance. Find it.
6. **State your decision and the tradeoff you are accepting.** "I chose X because the primary force is Y, and I accept the cost of Z."
7. **Record the conditions for revisiting.** "If we exceed 5 variants, switch from switch statement to Strategy." This prevents golden hammers and premature abstraction alike.
