---
name: dotnet-vertical-slice
description: Scaffold vertical slice architecture with CQRS + FreeMediator. Use when creating feature-based .NET projects with command/query separation and pipeline behaviors.
---

# Vertical Slice Architecture with CQRS + FreeMediator

> "The whole idea is that the abstraction we use to reason about the system should be the feature, not the layer."
> -- Jimmy Bogard

## Core Philosophy

This skill scaffolds and maintains vertical slice architecture in .NET projects using FreeMediator for CQRS and pipeline behaviors. Every feature is a self-contained unit. Layers are an implementation detail inside the slice, not a project-level organizing principle.

**Non-Negotiable Constraints:**

1. **Feature Isolation** -- Each feature lives in its own folder containing all code needed to fulfill that feature: request, response, handler, validator, and endpoint. No feature may reach into another feature's folder for types or logic.
2. **No Shared Base Handlers** -- Abstract base handlers, generic CRUD handlers, and handler inheritance hierarchies defeat the purpose of vertical slices. Each handler is independent, even if handlers look similar.
3. **Handler-Per-Feature** -- Every command, query, or notification gets its own handler class in its own file. A single handler must never process multiple unrelated operations.
4. **Cross-Cutting via Pipeline, Not Inheritance** -- Validation, logging, transactions, and caching are pipeline behaviors registered in the DI container, not base class methods. Features opt into cross-cutting concerns by implementing marker interfaces, not by inheriting from shared code.
5. **CQRS Separation Is Structural** -- Commands (state mutation) and queries (state reads) are separate request types with separate handlers. A single handler must never both read and write.

## Domain Principles Table

| # | Principle | Description | Priority |
|---|-----------|-------------|----------|
| 1 | **Feature Isolation** | Each feature folder is a self-contained unit. No imports between feature folders. Shared code lives in a `Common/` or `Infrastructure/` directory, never in another feature. | Critical |
| 2 | **Handler Autonomy** | Each handler owns its dependencies, data access, and logic. Two handlers may duplicate similar code -- that is acceptable and preferred over shared abstractions that couple features. | Critical |
| 3 | **Minimal Abstractions** | Do not create interfaces, base classes, or generic handlers "for the future." Introduce abstractions only when three or more features demonstrate an identical, stable pattern. | High |
| 4 | **Pipeline Composition** | Cross-cutting concerns (validation, logging, transactions, caching) are composed via FreeMediator pipeline behaviors, not via handler inheritance or method calls inside handlers. | Critical |
| 5 | **CQRS Boundary** | Commands return at most an identifier or status. Queries return data and must not mutate state. A handler that reads and writes is a design error, not a convenience. | Critical |
| 6 | **Request/Response Immutability** | Request and response types are C# records. They are immutable value objects that cross the boundary between the caller and the handler. | High |
| 7 | **Explicit Dependencies** | Handlers declare their dependencies via constructor injection. No service locator patterns, no ambient contexts, no static helpers. | High |
| 8 | **Validator Co-Location** | The FluentValidation validator for a request lives in the same feature folder as the request and handler. Validation rules are feature-specific, not shared. | High |
| 9 | **Endpoint Thinness** | API endpoints (Minimal API or controller actions) do nothing except deserialize the request, send it through FreeMediator, and serialize the response. No business logic in endpoints. | High |
| 10 | **Test Proximity** | Tests for a feature mirror the feature folder structure. A feature's tests live together and test the handler, validator, and endpoint as a cohesive unit. | Medium |

## Workflow

### Vertical Slice Lifecycle

```
┌────────────────────────────────────────────────────────────────────────┐
│                    Vertical Slice Lifecycle                              │
│                                                                          │
│  ┌──────────┐   ┌─────────┐   ┌──────────┐   ┌──────────┐   ┌────────┐│
│  │ SCAFFOLD  │──>│ COMMAND │──>│  QUERY   │──>│ PIPELINE │──>│VALIDATE││
│  │ Feature   │   │ or QUERY│   │ (if both)│   │ BEHAVIORS│   │        ││
│  │ Folder    │   │ Handler │   │          │   │          │   │        ││
│  └──────────┘   └─────────┘   └──────────┘   └──────────┘   └────────┘│
│       │                                             │            │      │
│       │         ┌──────────────┐                    │            │      │
│       └────────>│ NOTIFICATION │────────────────────┘            │      │
│                 │ (if needed)  │                                  │      │
│                 └──────────────┘                                  │      │
│                                                                   │      │
│  On validation failure:                                           │      │
│  ┌──────────────────┐                                             │      │
│  │ FIX HANDLER OR   │<────────────────────────────────────────────┘      │
│  │ VALIDATOR         │                                                    │
│  └──────────────────┘                                                    │
└────────────────────────────────────────────────────────────────────────┘
```

### Pre-Flight Checklist

Before scaffolding a new feature, verify:

- [ ] The feature has a clear, single responsibility (one user action or query)
- [ ] The feature name describes what it does, not what layer it belongs to (e.g., `CreateOrder`, not `OrderService`)
- [ ] FreeMediator is registered in `Program.cs` (`builder.Services.AddFreeMediator(...)`)
- [ ] FluentValidation is registered (`builder.Services.AddValidatorsFromAssembly(...)`)
- [ ] Pipeline behaviors are registered in the correct order
- [ ] The `Features/` directory exists in the project

### Command vs Query vs Notification Decision Tree

```
What does this feature do?
│
├─ Changes state in the system? (create, update, delete)
│  └─ COMMAND
│     ├─ Returns an ID or status ──> IRequest<TResponse>
│     └─ Returns nothing ──────────> IRequest
│
├─ Reads data without side effects?
│  └─ QUERY
│     └─ Returns data ─────────────> IRequest<TResponse>
│
├─ Reacts to something that already happened?
│  └─ NOTIFICATION
│     ├─ Multiple handlers needed ──> INotification
│     └─ Single handler ───────────> Consider a command instead
│
└─ Does both read and write?
   └─ SPLIT IT
      ├─ Extract the write into a COMMAND
      └─ Extract the read into a QUERY
```

## State Block Format

Maintain state across conversation turns using this block:

```
<vslice-state>
step: [SCAFFOLD | COMMAND | QUERY | NOTIFICATION | PIPELINE | VALIDATE]
feature: [description]
pattern: [command | query | notification]
folder_path: [path to feature folder]
last_action: [what was just done]
next_action: [what should happen next]
blockers: [any issues]
</vslice-state>
```

### Example State Progression

```
<vslice-state>
step: SCAFFOLD
feature: CreateOrder - creates a new order from a cart
pattern: command
folder_path: src/MyApp/Features/Orders/CreateOrder/
last_action: Created feature folder structure
next_action: Define CreateOrderCommand record and CreateOrderResponse record
blockers: none
</vslice-state>
```

```
<vslice-state>
step: COMMAND
feature: CreateOrder - creates a new order from a cart
pattern: command
folder_path: src/MyApp/Features/Orders/CreateOrder/
last_action: Implemented CreateOrderHandler with EF Core persistence
next_action: Create CreateOrderValidator with FluentValidation rules
blockers: none
</vslice-state>
```

```
<vslice-state>
step: VALIDATE
feature: CreateOrder - creates a new order from a cart
pattern: command
folder_path: src/MyApp/Features/Orders/CreateOrder/
last_action: All tests passing, handler and validator verified
next_action: Feature complete, ready for next slice
blockers: none
</vslice-state>
```

## Output Templates

### Session Start

```markdown
## Vertical Slice Session: [Feature Name]

**Project**: [Project path]
**Pattern**: [Command | Query | Notification]
**Feature Folder**: `Features/[Domain]/[FeatureName]/`

<vslice-state>
step: SCAFFOLD
feature: [description]
pattern: [command | query | notification]
folder_path: [path]
last_action: Session initialized
next_action: Create feature folder and define request/response types
blockers: none
</vslice-state>

### SCAFFOLD Phase

Creating folder structure for: [Feature Name]
```

### Feature Scaffold Report

```markdown
## Feature Scaffolded: [FeatureName]

**Folder**: `Features/[Domain]/[FeatureName]/`

### Files Created
| File | Purpose |
|------|---------|
| `[FeatureName]Command.cs` | Request record with properties |
| `[FeatureName]Response.cs` | Response record |
| `[FeatureName]Handler.cs` | FreeMediator handler |
| `[FeatureName]Validator.cs` | FluentValidation rules |
| `[FeatureName]Endpoint.cs` | Minimal API endpoint |

### Request Shape
```csharp
public record [FeatureName]Command(...) : IRequest<[FeatureName]Response>;
```

### Next Steps
1. Implement handler logic
2. Define validation rules
3. Write tests

<vslice-state>
step: [COMMAND | QUERY]
feature: [description]
pattern: [pattern]
folder_path: [path]
last_action: Feature folder scaffolded with all file stubs
next_action: Implement handler logic
blockers: none
</vslice-state>
```

### Phase Transition

```markdown
### Phase Complete: [PHASE]

**What was accomplished:**
- [bullet points]

**Verification:**
- Tests run: [yes/no]
- Result: [pass/fail with count]
- Validation: [handler tested / validator tested / endpoint tested]

<vslice-state>
step: [NEXT_STEP]
...
</vslice-state>

### [NEXT_STEP] Phase

Next: [action]
```

## AI Discipline Rules

### CRITICAL: Never Create Shared Base Handlers

Before writing any handler, verify:

1. The handler does NOT inherit from a base class
2. The handler does NOT call a shared "CRUD helper" method
3. The handler is a standalone class implementing `IRequestHandler<TRequest, TResponse>`
4. If two handlers look similar, that is acceptable -- duplication within reason is preferable to coupling

If tempted to extract a base handler, STOP. Duplicate code between features is a feature, not a bug. Shared abstractions between handlers create the horizontal layering that vertical slices are designed to eliminate.

```csharp
// WRONG: Shared base handler
public abstract class BaseCrudHandler<TEntity, TRequest, TResponse>
    : IRequestHandler<TRequest, TResponse>
{
    protected readonly AppDbContext _db;
    // ... shared CRUD logic
}

public class CreateOrderHandler : BaseCrudHandler<Order, CreateOrderCommand, CreateOrderResponse>
{
    // Coupled to all other CRUD handlers via base class
}

// RIGHT: Independent handler
public class CreateOrderHandler : IRequestHandler<CreateOrderCommand, CreateOrderResponse>
{
    private readonly AppDbContext _db;

    public CreateOrderHandler(AppDbContext db) => _db = db;

    public async Task<CreateOrderResponse> Handle(
        CreateOrderCommand request, CancellationToken ct)
    {
        // All logic self-contained
    }
}
```

### CRITICAL: One Feature Per Folder

Each feature folder must contain exactly one cohesive operation:

1. One request type (command or query)
2. One handler
3. One validator (if applicable)
4. One endpoint (if API-exposed)
5. One response type

If a feature folder contains two handlers or two request types, STOP and split it into separate feature folders.

```
Features/
  Orders/
    CreateOrder/          <-- ONE command
      CreateOrderCommand.cs
      CreateOrderResponse.cs
      CreateOrderHandler.cs
      CreateOrderValidator.cs
      CreateOrderEndpoint.cs
    GetOrderById/         <-- ONE query
      GetOrderByIdQuery.cs
      GetOrderByIdResponse.cs
      GetOrderByIdHandler.cs
      GetOrderByIdEndpoint.cs
```

### CRITICAL: No Cross-Feature Dependencies in GREEN

When implementing a handler (the "GREEN" phase in TDD), never:

1. Import types from another feature folder
2. Call another feature's handler directly
3. Share a response type between features
4. Reference another feature's validator

If feature A needs something from feature B:
- Use a domain event (INotification) to communicate
- Extract shared types to `Common/` or the domain model
- Use a shared infrastructure service (e.g., repository, external API client)

```csharp
// WRONG: Cross-feature dependency
using MyApp.Features.Customers.GetCustomerById; // Importing from another feature!

public class CreateOrderHandler : IRequestHandler<CreateOrderCommand, CreateOrderResponse>
{
    public async Task<CreateOrderResponse> Handle(...)
    {
        var customer = await _mediator.Send(new GetCustomerByIdQuery(request.CustomerId));
        // Coupling to another feature's request/response types
    }
}

// RIGHT: Use domain model or infrastructure service
public class CreateOrderHandler : IRequestHandler<CreateOrderCommand, CreateOrderResponse>
{
    private readonly AppDbContext _db;

    public async Task<CreateOrderResponse> Handle(...)
    {
        var customer = await _db.Customers.FindAsync(request.CustomerId);
        // Uses shared infrastructure (DbContext), not another feature
    }
}
```

### CRITICAL: Pipeline Behaviors Are Infrastructure, Not Features

Pipeline behaviors handle cross-cutting concerns and belong in `Infrastructure/Behaviors/` or `Common/Behaviors/`, never inside a feature folder:

1. Validation behavior -- runs FluentValidation before every handler
2. Logging behavior -- logs request/response for diagnostics
3. Transaction behavior -- wraps handlers in a database transaction
4. Caching behavior -- caches query responses

Behaviors are registered once in the DI container and apply across all features via the pipeline. They must never contain feature-specific logic.

If a behavior needs to act differently per feature, use a marker interface on the request type (e.g., `ICachedQuery`) rather than adding conditional logic inside the behavior.

```csharp
// WRONG: Feature-specific logic inside a pipeline behavior
public class ValidationBehavior<TRequest, TResponse> : IPipelineBehavior<TRequest, TResponse>
{
    public async Task<TResponse> Handle(TRequest request, ...)
    {
        if (request is CreateOrderCommand cmd)
        {
            // Feature-specific validation does NOT belong here
        }
    }
}

// RIGHT: Generic behavior using FluentValidation
public class ValidationBehavior<TRequest, TResponse> : IPipelineBehavior<TRequest, TResponse>
    where TRequest : IRequest<TResponse>
{
    private readonly IEnumerable<IValidator<TRequest>> _validators;

    public async Task<TResponse> Handle(TRequest request, ...)
    {
        // Runs all validators registered for this request type
        // No feature-specific knowledge
    }
}
```

## Anti-Patterns Table

| Anti-Pattern | Why It's Wrong | Correct Approach |
|--------------|----------------|------------------|
| **Generic CRUD handler** (`BaseCrudHandler<TEntity>`) | Couples all features to a shared abstraction. Changes to the base class ripple across every feature. Eliminates the independence that makes vertical slices valuable. | Each handler is a standalone class. Accept duplication between handlers. |
| **Shared response types** (`ApiResponse<T>` for all features) | Forces every feature to conform to a single response shape. Makes it impossible to evolve one feature's response without affecting others. | Each feature defines its own response record tailored to its specific return data. |
| **Fat endpoint with business logic** | Puts logic in the HTTP layer where it cannot be unit tested without HTTP infrastructure. Violates the thin-endpoint principle. | Endpoints only deserialize, send to mediator, and serialize the response. All logic lives in the handler. |
| **Handler calling another handler via mediator** | Creates hidden runtime coupling between features. Makes execution order opaque. Breaks feature isolation. | Use domain events (INotification) for decoupled communication. Or use shared infrastructure services. |
| **Organizing by technical layer** (`Controllers/`, `Services/`, `Repositories/`) | Forces developers to touch multiple folders for a single feature. Makes it hard to understand, modify, or delete a feature as a unit. | Organize by feature. Each feature folder contains all layers for that slice. |
| **Validation in the handler** instead of using FluentValidation + pipeline | Mixes cross-cutting validation with business logic. Cannot be reused or composed. Makes handlers harder to test. | Define a FluentValidation validator for each request. Let the validation pipeline behavior run it automatically. |
| **Putting pipeline behaviors inside feature folders** | Behaviors are infrastructure shared across all features. Placing them in a feature folder implies feature-specific ownership. | Pipeline behaviors live in `Infrastructure/Behaviors/` or `Common/Behaviors/`. |

## Error Recovery

### Problem: FreeMediator Handler Not Found at Runtime

```
Symptom: InvalidOperationException - No handler registered for [RequestType]
```

**Action:**
1. Verify the handler class implements `IRequestHandler<TRequest, TResponse>` (or `IRequestHandler<TRequest>` for void commands)
2. Verify FreeMediator registration in `Program.cs` scans the correct assembly: `services.AddFreeMediator(cfg => cfg.RegisterServicesFromAssembly(typeof(Program).Assembly))`
3. Verify the handler is a public, non-abstract, non-static class
4. Check that the request type in the handler matches the request type being sent

### Problem: Validator Not Running Before Handler

```
Symptom: Handler executes with invalid data, no ValidationException thrown
```

**Action:**
1. Verify `ValidationBehavior<,>` is registered as a pipeline behavior in DI
2. Verify the validator class exists and implements `AbstractValidator<TRequest>`
3. Verify FluentValidation validators are registered: `services.AddValidatorsFromAssemblyContaining<Program>()`
4. Verify the pipeline behavior order: validation should run before the handler
5. Check that the request type matches between the validator and the handler

### Problem: Feature Folder Growing Too Large

```
Symptom: A feature folder has more than 6-8 files, handler has 200+ lines
```

**Action:**
1. The feature is doing too much -- split it into smaller features
2. Extract the write operation as a command and the read as a separate query
3. If the handler coordinates multiple steps, consider whether each step is a separate feature triggered by notifications
4. Domain logic that is not feature-specific should move to a domain entity or domain service in `Common/`

### Problem: Circular Dependency Between Features

```
Symptom: Feature A imports from Feature B, Feature B imports from Feature A
```

**Action:**
1. Neither feature should import from the other -- this violates feature isolation
2. Extract the shared types to `Common/Models/` or the domain layer
3. Use domain events (INotification) for communication: Feature A publishes an event, Feature B handles it independently
4. If the features are truly interdependent, they may be a single feature that was incorrectly split

### Problem: Pipeline Behavior Order Causing Side Effects

```
Symptom: Transaction commits before validation, or logging misses exceptions
```

**Action:**
1. Review the behavior registration order in `Program.cs`
2. Correct order is typically: Logging -> Validation -> Transaction -> (Handler)
3. Behaviors execute in registration order (outermost first, innermost last)
4. Verify each behavior calls `next()` and does not swallow exceptions

## Integration with Other Skills

- **`ef-migration-manager`** -- When a vertical slice feature requires new database tables or columns, use `ef-migration-manager` to create and apply the migration. The migration should be planned alongside the feature: define the entity in the slice, then create the migration. The handler's data access code depends on the schema being in place.
- **`blazor-telerik-component`** -- Grid and form components are the UI layer of a vertical slice. Start with this skill to build the backend (command/query handler, validator, endpoint), then use `blazor-telerik-component` to create the Blazor component that calls the endpoint. The feature's response record defines the shape of the data the component will display.
- **`tdd-cycle`** -- Vertical slices are ideal for TDD. Each slice is a small, testable unit. Use `tdd-cycle` to drive the handler implementation: write a failing test for the handler's behavior (RED), implement the handler minimally (GREEN), then refactor. The handler's isolation makes it straightforward to test without mocking half the application.
- **`tdd-agent`** -- For autonomous development of vertical slice features, `tdd-agent` can drive the entire cycle: scaffold the feature folder, write handler tests in RED, implement in GREEN, refactor. The strict guardrails of `tdd-agent` pair well with the structural constraints of vertical slices -- both prioritize discipline and small, verifiable steps.

## Reference Files

See detailed patterns and code examples:
- [Feature Folder Patterns](references/feature-folder-patterns.md) -- Complete folder layouts, request/response records, handler classes, validators, and FreeMediator registration
- [Pipeline Behaviors](references/pipeline-behaviors.md) -- FreeMediator pipeline behavior implementations for validation, logging, transactions, and caching
- [Vertical Slice Testing](references/dotnet-vertical-testing.md) -- Testing patterns for handlers, validators, endpoints, and pipeline behaviors using xUnit and FluentAssertions
