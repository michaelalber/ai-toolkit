---
name: dotnet-vertical-slice
description: >
  Scaffold vertical slice architecture with CQRS + FreeMediator, including optional
  Telerik Blazor UI generation. Use when creating feature-based .NET projects with
  command/query separation and pipeline behaviors. Triggers on "scaffold feature",
  "create slice", "new feature", "generate cqrs", "add command", "add query",
  "create handler", "vertical slice".
  Do NOT use when the project uses layer-based (N-tier) architecture — this skill
  enforces feature folder structure and will conflict with existing layer conventions.
---

# Vertical Slice Architecture with CQRS + FreeMediator

> "The whole idea is that the abstraction we use to reason about the system should be the feature, not the layer."
> -- Jimmy Bogard

## Core Philosophy

This skill scaffolds and maintains vertical slice architecture in .NET projects using FreeMediator for CQRS and pipeline behaviors. Every feature is a self-contained unit. Layers are an implementation detail inside the slice, not a project-level organizing principle.

**Non-Negotiable Constraints:**

1. **Feature Isolation** — Each feature lives in its own folder. No feature may reach into another feature's folder for types or logic.
2. **No Shared Base Handlers** — Abstract base handlers and handler inheritance defeat the purpose of vertical slices. Each handler is independent.
3. **Handler-Per-Feature** — Every command, query, or notification gets its own handler class. A single handler must never process multiple unrelated operations.
4. **Cross-Cutting via Pipeline** — Validation, logging, transactions, and caching are pipeline behaviors, not base class methods.
5. **CQRS Separation Is Structural** — Commands mutate state; queries return data. A single handler must never both read and write.

## Domain Principles Table

| # | Principle | Description | Priority |
|---|-----------|-------------|----------|
| 1 | **Feature Isolation** | Feature folder is self-contained. No imports between feature folders. Shared code lives in `Common/` or `Infrastructure/`. | Critical |
| 2 | **Handler Autonomy** | Each handler owns its dependencies and logic. Duplication between handlers is acceptable and preferred over coupling. | Critical |
| 3 | **Minimal Abstractions** | Introduce abstractions only when three or more features demonstrate an identical, stable pattern. | High |
| 4 | **Pipeline Composition** | Cross-cutting concerns are composed via FreeMediator pipeline behaviors, not handler inheritance. | Critical |
| 5 | **CQRS Boundary** | Commands return at most an identifier or status. Queries return data and must not mutate state. | Critical |
| 6 | **Request/Response Immutability** | Request and response types are C# records — immutable value objects. | High |
| 7 | **Explicit Dependencies** | Handlers declare dependencies via constructor injection. No service locator or static helpers. | High |
| 8 | **Validator Co-Location** | FluentValidation validator lives in the same feature folder as its request and handler. | High |
| 9 | **Endpoint Thinness** | Endpoints only deserialize, mediate, and serialize. No business logic. | High |
| 10 | **Test Proximity** | Tests mirror the feature folder structure and test handler, validator, and endpoint as a unit. | Medium |

## Knowledge Base Lookups

| Query | When to Call |
|-------|--------------|
| `search_knowledge("vertical slice architecture CQRS feature folder .NET")` | At session start |
| `search_knowledge("FreeMediator IRequest handler pipeline behavior .NET")` | When scaffolding handlers or pipeline behaviors |
| `search_knowledge("FluentValidation IValidator async rule .NET")` | When scaffolding validators |
| `search_knowledge("ASP.NET Core Minimal API TypedResults endpoint group")` | When scaffolding endpoints |
| `search_knowledge("EF Core DbContext dependency injection scoped lifetime")` | When scaffolding DbContext |
| `search_knowledge("C# record immutable request response DTO")` | When defining request/response types |

Search before scaffolding each new component type. Cite the source path in generated code comments.

## Workflow

Scaffold proceeds in phases: **SCAFFOLD** (create folder and stub files) → **COMMAND or QUERY** (implement handler) → **PIPELINE** (wire behaviors) → **VALIDATE** (run tests, verify isolation). Use a notification (`INotification`) when an event must fan out to multiple handlers. When a feature both reads and writes, split it: extract the write as a command and the read as a separate query. Pipeline behaviors (validation, logging, transactions, caching) belong in `Infrastructure/Behaviors/` and are registered once in DI — they must never contain feature-specific conditional logic.

### Pre-Flight Checklist

- [ ] Feature has a clear, single responsibility
- [ ] Feature name describes the action, not the layer (e.g., `CreateOrder`, not `OrderService`)
- [ ] FreeMediator is registered in `Program.cs`
- [ ] FluentValidation is registered
- [ ] Pipeline behaviors registered in correct order
- [ ] `Features/` directory exists in the project

## State Block Format

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

**Example:**

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

## Output Templates

```markdown
## Vertical Slice Session: [Feature Name]
**Pattern**: [Command | Query | Notification] | **Folder**: `Features/[Domain]/[FeatureName]/`
**Files created**: Request, Response, Handler, Validator, Endpoint
**State**: [current vslice-state block]
**Next**: [action]
```

## AI Discipline Rules

**Never create shared base handlers.** Each handler is a standalone class implementing `IRequestHandler<TRequest, TResponse>`. If two handlers look similar, that duplication is intentional — shared abstractions between handlers re-introduce the horizontal layering that vertical slices eliminate.

**One feature per folder.** A feature folder contains exactly one request type, one handler, one validator (if applicable), one endpoint, and one response type. Two handlers in one folder means split it.

**No cross-feature imports.** Handlers must not import types from another feature folder or dispatch to another feature's handler. Use domain events (`INotification`) or shared infrastructure services for inter-feature communication.

**Pipeline behaviors are infrastructure.** A behavior with conditional logic per feature type is a design error. Use marker interfaces on the request type (e.g., `ICachedQuery`) to vary behavior without adding feature knowledge to the behavior class. Behaviors live in `Infrastructure/Behaviors/`, never inside a feature folder.

## Telerik Blazor UI Generation (Conditional)

When the project uses Telerik UI for Blazor, generate Blazor pages alongside the backend slice. Pages live in the feature folder under `Pages/` and dispatch commands/queries via FreeMediator. Only generate when the project has Telerik Blazor dependencies.

Extended feature folder structure:

```
Features/{FeatureName}/
├── Commands/Create{Entity}/, Update{Entity}/, Delete{Entity}/
├── Queries/Get{Entity}ById/, Get{Entity}List/
├── DTOs/{Entity}Dto.cs, {Entity}ListDto.cs
├── Pages/{Entity}List.razor, {Entity}Edit.razor
├── Mapping/{Entity}MappingConfig.cs (Mapster)
└── Tests/
```

See [Telerik Blazor Templates](references/telerik-blazor-templates.md) for TelerikGrid list page, TelerikForm edit page, DTO classes, Mapster mapping configuration, and scaffold bash commands.

## Anti-Patterns Table

| Anti-Pattern | Why It's Wrong | Correct Approach |
|--------------|----------------|------------------|
| **Generic CRUD handler** | Couples all features; base class changes ripple everywhere. | Each handler is standalone. Accept duplication. |
| **Shared response types** | Forces features to conform to one shape; blocks independent evolution. | Each feature defines its own response record. |
| **Fat endpoint with business logic** | Logic in HTTP layer can't be unit-tested without HTTP infrastructure. | Endpoints only deserialize, mediate, serialize. |
| **Handler calling another handler** | Hidden runtime coupling; breaks feature isolation. | Use `INotification` events or shared infrastructure services. |
| **Organizing by technical layer** | Developers touch multiple folders for one feature. | Organize by feature; each folder contains all layers for that slice. |
| **Validation in the handler** | Mixes cross-cutting logic with business logic; not reusable. | FluentValidation validator + pipeline validation behavior. |
| **Pipeline behaviors in feature folders** | Behaviors are shared infrastructure, not feature-specific. | Behaviors live in `Infrastructure/Behaviors/`. |

## Error Recovery

### Handler Not Found at Runtime
`InvalidOperationException — No handler registered for [RequestType]`
1. Verify the handler implements `IRequestHandler<TRequest, TResponse>`
2. Verify FreeMediator registration scans the correct assembly
3. Verify the handler is public, non-abstract, non-static
4. Check that the request type matches what is being sent

### Validator Not Running Before Handler
`Handler executes with invalid data, no ValidationException thrown`
1. Verify `ValidationBehavior<,>` is registered as a pipeline behavior
2. Verify the validator implements `AbstractValidator<TRequest>`
3. Verify `services.AddValidatorsFromAssemblyContaining<Program>()`
4. Verify behavior order: validation must run before the handler

### Feature Folder Growing Too Large
`A feature folder has more than 6–8 files; handler has 200+ lines`
1. Split into smaller features — separate command and query
2. If handler coordinates multiple steps, consider domain events
3. Move non-feature-specific domain logic to `Common/`

### Circular Dependency Between Features
`Feature A imports from Feature B, Feature B imports from Feature A`
1. Extract shared types to `Common/Models/` or the domain layer
2. Use domain events for communication
3. If truly interdependent, they are likely one feature incorrectly split

### Pipeline Behavior Order Causing Side Effects
`Transaction commits before validation; logging misses exceptions`
1. Correct order: Logging → Validation → Transaction → (Handler)
2. Behaviors execute in registration order (outermost first)
3. Verify each behavior calls `next()` and does not swallow exceptions

## Integration with Other Skills

- **`ef-migration-manager`** — When a slice requires schema changes, plan the migration alongside the feature. Define the entity first, then create the migration.
- **`tdd-cycle`** — Each slice is an ideal TDD unit. Write a failing handler test (RED), implement minimally (GREEN), refactor. Handler isolation makes testing straightforward without mocking half the application.
- **`tdd-agent`** — For autonomous vertical slice development: scaffold the folder, write handler tests RED, implement GREEN, refactor.

## Reference Files

- [Feature Folder Patterns](references/feature-folder-patterns.md) — Folder layouts, request/response records, handler classes, validators, FreeMediator registration
- [Pipeline Behaviors](references/pipeline-behaviors.md) — Behavior implementations for validation, logging, transactions, caching
- [Vertical Slice Testing](references/dotnet-vertical-testing.md) — Testing patterns for handlers, validators, endpoints using xUnit and FluentAssertions
- [Telerik Blazor Templates](references/telerik-blazor-templates.md) — TelerikGrid list page, TelerikForm edit page, DTO classes, Mapster config, scaffold commands
