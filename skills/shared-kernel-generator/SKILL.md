---
name: shared-kernel-generator
description: Generates shared domain modules as NuGet packages following DenaliDataSystems patterns. Scaffolds core abstractions, entity templates, Options pattern configuration, DI extension methods, permission models, CQRS command/query templates, and DbContext patterns for vertical slice architecture. Triggers on "shared kernel", "generate module", "create shared package", "domain module", "common module", "shared entities", "create nuget package", "reusable domain", "denali module".
---

# Shared Kernel Generator

> "A Shared Kernel is a designated subset of the domain model that two or more teams agree to share, reducing duplication while maintaining bounded contexts."
> -- Eric Evans, Domain-Driven Design

> "The goal is not to eliminate all duplication, but to eliminate the wrong duplication -- the kind that couples things that should evolve independently."
> -- Vaughn Vernon, Implementing Domain-Driven Design

## Core Philosophy

This skill generates standardized shared domain modules following the **DenaliDataSystems** patterns established in `denali-core-library`. A shared kernel is the foundation of vertical slice architecture at the module boundary: it provides the contracts, entities, and infrastructure that multiple consuming applications depend on, while keeping each module independently deployable as a NuGet package.

**Non-Negotiable Constraints:**

1. **Contracts Over Implementation** -- A shared kernel exposes interfaces (`IAuditable`, `ISoftDeletable`), attributes (`[AuditedEntity]`), and entity models. It never contains application-specific business logic. If a rule only applies in one consuming application, it does not belong in the kernel.
2. **Options Pattern for All Configuration** -- Every module uses a `Denali{ModuleName}Options` class with fluent builder methods. No hardcoded connection strings, no magic strings for database names, no configuration that cannot be overridden by the consumer. See `references/options-pattern.md`.
3. **DI Extension as the Single Entry Point** -- Consumers register a module with one call: `services.AddDenali{ModuleName}(options => ...)`. This extension method handles DbContext registration, mediator handler scanning, validator registration, and caching setup. See `references/domain-module-templates.md`.
4. **Permission Model Is Hierarchical** -- Every permission follows `Module.Resource.Action` format. The `Manage` action implies all other actions for that resource. Permission constants are static classes, not enums, because they must be usable as policy names. See `references/permissions-pattern.md`.
5. **Cross-Module References Use FK IDs Only** -- When an entity in one module references an entity in another module, it stores only the foreign key ID. Navigation properties between modules are forbidden. The consuming application's DbContext configures cross-module relationships. See `references/shared-entity-patterns.md`.

## Domain Principles Table

| # | Principle | Description | Priority |
|---|-----------|-------------|----------|
| 1 | **IAuditable on Every Entity** | All entities implement `IAuditable` for `CreatedAt`, `CreatedBy`, `ModifiedAt`, `ModifiedBy` tracking. The DbContext `SaveChangesAsync` override populates these automatically. | Critical |
| 2 | **ISoftDeletable on Every Entity** | All entities implement `ISoftDeletable`. Hard deletes are intercepted in `SaveChangesAsync` and converted to soft deletes. Global query filters exclude deleted records by default. | Critical |
| 3 | **Options Pattern for Configuration** | Each module defines a sealed `Denali{ModuleName}Options` class with fluent methods (`UseSqlServer()`, `UseInMemoryDatabase()`, `WithCacheExpiration()`) and an internal `Validate()` method. | Critical |
| 4 | **Single DI Extension Method** | Each module exposes exactly one `AddDenali{ModuleName}()` extension method on `IServiceCollection`. This method registers all services, DbContext, mediator handlers, and validators. | Critical |
| 5 | **Feature.Resource.Action Permissions** | Permission constants follow `{Module}.{Resource}.{Action}` format. Standard actions: Manage, Read, Create, Update, Delete. Manage implies all other actions. | High |
| 6 | **CQRS with FreeMediator** | Commands are sealed records implementing `IRequest<T>`. Handlers are internal sealed classes using primary constructors. Validators use FluentValidation with async uniqueness checks. | High |
| 7 | **DbContext with Global Query Filters** | Each module has its own DbContext. Soft delete filters are applied to all `ISoftDeletable` entities. Audit fields are updated in the `SaveChangesAsync` override. | High |
| 8 | **NuGet Package per Module** | Each module is packaged as `DenaliDataSystems.{ModuleName}`. All modules depend on `DenaliDataSystems.Core.Abstractions`. Cross-module dependencies are avoided. | High |
| 9 | **Semantic Versioning** | MAJOR for breaking changes (interface modifications, entity renames). MINOR for new features (new command, new property). PATCH for bug fixes (validation fix, query optimization). | Medium |
| 10 | **Test with In-Memory Database** | Every module supports `UseInMemoryDatabase()` for testing. Test isolation uses unique database names (`$"TestDb_{Guid.NewGuid()}"`). Demo data seeding is opt-in via `WithDemoData()`. | Medium |

## Workflow

### Shared Kernel Lifecycle

```
+------------------------------------------------------------------------+
|                    Shared Kernel Lifecycle                              |
|                                                                        |
|  +---------+   +----------+   +-----------+   +---------+              |
|  | ANALYZE |-->| GENERATE |-->| CONFIGURE |-->| PACKAGE |              |
|  | Domain  |   | Entities |   | DI, Opts  |   | NuGet   |              |
|  | Scope   |   | Handlers |   | Perms     |   | Version |              |
|  +---------+   +----------+   +-----------+   +---------+              |
|       |                             |              |                   |
|       v                             v              v                   |
|  Identify what     Generate code    Wire up       Pack, version,       |
|  needs sharing     from templates   infrastructure publish             |
+------------------------------------------------------------------------+
```

### Phase 1: ANALYZE

Determine what needs to be shared across applications:

- [ ] Identify the domain area (PickLists, People, Training, Organization, Location, Workflow, Communication)
- [ ] List all entities and their relationships (parent-child within module, FK-only cross-module)
- [ ] Determine which entity interfaces apply (IAuditable, ISoftDeletable, or both)
- [ ] Identify features and their command/query operations
- [ ] Check for cross-module references that require FK-only properties
- [ ] Decide on the database schema name (lowercase module name by convention)

### Phase 2: GENERATE

Produce entities, handlers, validators, and DbContext from templates:

- [ ] Create entity classes implementing IAuditable and ISoftDeletable with `[AuditedEntity]` attribute (see `references/shared-entity-patterns.md`)
- [ ] Generate Create/Update/Delete commands with internal sealed handlers (see `references/domain-module-templates.md`)
- [ ] Generate GetById and GetList queries with DTOs and pagination
- [ ] Create FluentValidation validators with async uniqueness checks
- [ ] Create DbContext with global soft-delete query filters and audit field override (see `references/ef-configuration-patterns.md`)
- [ ] Create IEntityTypeConfiguration classes with schema, indexes, and audit field mapping

### Phase 3: CONFIGURE

Wire up dependency injection, options, and permissions:

- [ ] Create `Denali{ModuleName}Options` class with fluent configuration methods and `Validate()` (see `references/options-pattern.md`)
- [ ] Create `{ModuleName}DependencyInjection` class with `AddDenali{ModuleName}()` extension method
- [ ] Create `InitializeDenali{ModuleName}Async()` method for migration and seeding
- [ ] Define permission constants following `Module.Resource.Action` format (see `references/permissions-pattern.md`)
- [ ] Register FreeMediator handlers and FluentValidation validators from the module assembly

### Phase 4: PACKAGE

Prepare for NuGet packaging and distribution:

- [ ] Create `.csproj` file with package metadata (see `references/nuget-package-structure.md`)
- [ ] Set `PackageId` to `DenaliDataSystems.{ModuleName}`
- [ ] Add `ProjectReference` to `DenaliDataSystems.Core.Abstractions`
- [ ] Verify `Directory.Build.props` includes common settings (versioning, SourceLink, symbols)
- [ ] Set version following SemVer (MAJOR.MINOR.PATCH)
- [ ] Generate README.md for the NuGet package

## DenaliDataSystems Module Packages

| Module | Package Name | Purpose |
|--------|--------------|---------|
| Core Abstractions | `DenaliDataSystems.Core.Abstractions` | IAuditable, ISoftDeletable, base contracts |
| PickLists | `DenaliDataSystems.PickLists` | Configurable lookup values |
| People | `DenaliDataSystems.People` | Employee data, roles, badges |
| Training | `DenaliDataSystems.Training` | Training records, certifications |
| Organization | `DenaliDataSystems.Organization` | Org structure, hierarchy, groups |
| Location | `DenaliDataSystems.Location` | Facilities, buildings, areas |
| Workflow | `DenaliDataSystems.Workflow` | Approval workflows, state machines |
| Communication | `DenaliDataSystems.Communication` | Email, notifications, templates |

## Project Structure (Vertical Slice Architecture)

```
DenaliDataSystems.{ModuleName}/
+-- DenaliDataSystems.{ModuleName}.csproj
+-- {ModuleName}DependencyInjection.cs      # AddDenali{ModuleName}() extension
+-- Extensions/
|   +-- Denali{ModuleName}Options.cs        # Options pattern for configuration
+-- Features/
|   +-- {Feature}Feature/
|       +-- Commands/
|       |   +-- Create{Entity}/
|       |   |   +-- Create{Entity}Command.cs
|       |   |   +-- Create{Entity}Validator.cs
|       |   +-- Update{Entity}/
|       |   +-- Delete{Entity}/
|       +-- Queries/
|       |   +-- Get{Entity}ById/
|       |   +-- Get{Entity}List/
|       +-- Entities/
|       |   +-- Models/
|       |       +-- {Entity}.cs
|       +-- Data/
|           +-- {ModuleName}DbContext.cs
|           +-- Configurations/
|               +-- {Entity}Configuration.cs
+-- Permissions/
|   +-- {Feature}Permissions.cs
+-- README.md
```

## State Block Format

Maintain state across conversation turns using this block:

```
<shared-kernel-state>
mode: [ANALYZE | GENERATE | CONFIGURE | PACKAGE]
module_name: [DenaliDataSystems.{ModuleName}]
entities_generated: [count or list]
handlers_generated: [count or list]
di_configured: [true | false]
permissions_defined: [true | false]
packaged: [true | false]
last_action: [what was just done]
next_action: [what should happen next]
</shared-kernel-state>
```

### Example State Progression

```
<shared-kernel-state>
mode: ANALYZE
module_name: DenaliDataSystems.Training
entities_generated: 0
handlers_generated: 0
di_configured: false
permissions_defined: false
packaged: false
last_action: Identified Training module scope with TrainingCourse and TrainingRecord entities
next_action: Generate entity classes with IAuditable and ISoftDeletable interfaces
</shared-kernel-state>
```

```
<shared-kernel-state>
mode: GENERATE
module_name: DenaliDataSystems.Training
entities_generated: 2 (TrainingCourse, TrainingRecord)
handlers_generated: 6 (Create/Update/Delete + GetById/GetList for each entity)
di_configured: false
permissions_defined: false
packaged: false
last_action: Generated all CQRS handlers and validators for TrainingCourse and TrainingRecord
next_action: Create DenaliTrainingOptions and TrainingDependencyInjection
</shared-kernel-state>
```

```
<shared-kernel-state>
mode: PACKAGE
module_name: DenaliDataSystems.Training
entities_generated: 2 (TrainingCourse, TrainingRecord)
handlers_generated: 6
di_configured: true
permissions_defined: true
packaged: true
last_action: Created .csproj with NuGet metadata, verified all tests pass with in-memory database
next_action: Module complete, ready for consumer integration
</shared-kernel-state>
```

## Output Templates

### Module Inventory

```markdown
## Shared Kernel Module: [Module Name]

**Package**: `DenaliDataSystems.[ModuleName]`
**Version**: [X.Y.Z]
**Date**: [Date]

### Features

| Feature | Commands | Queries | Permissions |
|---------|----------|---------|-------------|
| ... | Create, Update, Delete | GetById, GetList | Manage, Read, Create, Update, Delete |

### Entities

| Entity | Table | Schema | Interfaces |
|--------|-------|--------|------------|
| ... | ... | ... | IAuditable, ISoftDeletable |

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| ConnectionString | string | null | SQL Server connection |
| IsInMemoryDatabase | bool | false | Use in-memory for testing |
| CacheExpirationMinutes | int | 30 | Cache TTL |
| AutoMigrateDatabase | bool | true | Run migrations on startup |
| SeedDemoData | bool | false | Seed test data |
```

### Entity Template

```csharp
using System.ComponentModel.DataAnnotations;
using DenaliDataSystems.Core.Abstractions.Attributes;
using DenaliDataSystems.Core.Abstractions.Contracts;

namespace DenaliDataSystems.{ModuleName}.Features.{Feature}Feature.Entities.Models;

[AuditedEntity]
public class {Entity} : IAuditable, ISoftDeletable
{
    public int Id { get; set; }

    [Required]
    [StringLength(100)]
    public string Name { get; set; } = string.Empty;

    [StringLength(500)]
    public string? Description { get; set; }

    public bool IsActive { get; set; } = true;

    // IAuditable
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    public string CreatedBy { get; set; } = "System";
    public DateTime? ModifiedAt { get; set; }
    public string? ModifiedBy { get; set; }

    // ISoftDeletable
    public bool IsDeleted { get; set; }
    public DateTime? DeletedAt { get; set; }
    public string? DeletedBy { get; set; }
}
```

### Handler Template (Command with Internal Handler)

```csharp
using FreeMediator;
using DenaliDataSystems.{ModuleName}.Features.{Feature}Feature.Data;
using DenaliDataSystems.{ModuleName}.Features.{Feature}Feature.Entities.Models;

namespace DenaliDataSystems.{ModuleName}.Features.{Feature}Feature.Commands.Create{Entity};

public sealed record Create{Entity}Command(
    string Name,
    string? Description = null) : IRequest<int>;

internal sealed class Create{Entity}Handler(
    {ModuleName}DbContext db) : IRequestHandler<Create{Entity}Command, int>
{
    public async Task<int> Handle(Create{Entity}Command request, CancellationToken ct)
    {
        var entity = new {Entity}
        {
            Name = request.Name,
            Description = request.Description
        };

        db.{Entities}.Add(entity);
        await db.SaveChangesAsync(ct);

        return entity.Id;
    }
}
```

### DI Extension Template

```csharp
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.DependencyInjection;
using FluentValidation;
using DenaliDataSystems.{ModuleName}.Extensions;
using DenaliDataSystems.{ModuleName}.Features.{Feature}Feature.Data;

namespace DenaliDataSystems.{ModuleName};

public static class {ModuleName}DependencyInjection
{
    public static IServiceCollection AddDenali{ModuleName}(
        this IServiceCollection services,
        Action<Denali{ModuleName}Options> configureOptions)
    {
        var options = new Denali{ModuleName}Options();
        configureOptions(options);
        options.Validate();

        services.AddSingleton(options);

        services.AddDbContext<{ModuleName}DbContext>((sp, opt) =>
        {
            var moduleOptions = sp.GetRequiredService<Denali{ModuleName}Options>();
            if (moduleOptions.IsInMemoryDatabase)
                opt.UseInMemoryDatabase(moduleOptions.InMemoryDatabaseName);
            else
                opt.UseSqlServer(moduleOptions.ConnectionString!);
        });

        services.AddFreeMediator(typeof({ModuleName}DependencyInjection).Assembly);
        services.AddValidatorsFromAssembly(typeof({ModuleName}DependencyInjection).Assembly);

        if (options.CacheExpirationMinutes > 0)
            services.AddMemoryCache();

        return services;
    }
}
```

### Permission Matrix Template

```csharp
namespace DenaliDataSystems.{ModuleName}.Permissions;

public static class {Feature}Permissions
{
    public const string Manage = "{ModuleName}.{Feature}.Manage";
    public const string Read = "{ModuleName}.{Feature}.Read";
    public const string Create = "{ModuleName}.{Feature}.Create";
    public const string Update = "{ModuleName}.{Feature}.Update";
    public const string Delete = "{ModuleName}.{Feature}.Delete";

    public static readonly string[] All = { Manage, Read, Create, Update, Delete };
}
```

### Consumer Usage

```csharp
// In Program.cs -- Production
builder.Services.AddDenali{ModuleName}(options =>
{
    options.UseSqlServer(builder.Configuration.GetConnectionString("Default")!);
    options.WithCacheExpiration(60);
});

// In Program.cs -- Testing
builder.Services.AddDenali{ModuleName}(options =>
{
    options.UseInMemoryDatabase();
    options.WithDemoData();
});

// Using FreeMediator in a controller or service
var id = await mediator.Send(new Create{Entity}Command("Name"));
var entity = await mediator.Send(new Get{Entity}ByIdQuery(id));
```

## AI Discipline Rules

### CRITICAL: Always Implement IAuditable on Entities

Every entity in a shared kernel module must implement `IAuditable`. There are no exceptions. The DbContext `SaveChangesAsync` override depends on this interface to auto-populate `CreatedAt`, `CreatedBy`, `ModifiedAt`, and `ModifiedBy`. An entity without `IAuditable` will have blank audit trails, making it impossible to trace who changed what and when.

```csharp
// WRONG: Entity without IAuditable
public class TrainingCourse
{
    public int Id { get; set; }
    public string Title { get; set; } = string.Empty;
}

// RIGHT: Entity with IAuditable and ISoftDeletable
[AuditedEntity]
public class TrainingCourse : IAuditable, ISoftDeletable
{
    public int Id { get; set; }
    public string Title { get; set; } = string.Empty;
    // ... audit and soft delete properties
}
```

### CRITICAL: Never Put Business Logic in the Shared Kernel

The shared kernel provides data structures, contracts, and infrastructure. It does not make business decisions. If a rule applies only to one consuming application (e.g., "training records older than 5 years should be archived"), that rule belongs in the consuming application, not in the kernel. The kernel provides the `TrainingRecord` entity; the consumer decides what to do with it.

### CRITICAL: Always Use the Options Pattern for Configuration

Never hardcode connection strings, database names, cache durations, or schema names. Every configurable value must flow through the `Denali{ModuleName}Options` class. The `Validate()` method must enforce that required settings (like `ConnectionString` when not using in-memory) are provided. See `references/options-pattern.md` for the complete pattern.

```csharp
// WRONG: Hardcoded configuration
services.AddDbContext<TrainingDbContext>(opt =>
    opt.UseSqlServer("Server=prod;Database=Training;..."));

// RIGHT: Options pattern
services.AddDenaliTraining(options =>
    options.UseSqlServer(builder.Configuration.GetConnectionString("Default")!));
```

### CRITICAL: Follow Feature.Resource.Action for Permissions

Permission strings must always follow `{Module}.{Resource}.{Action}` format. Never use freeform strings like `"can_edit_training"` or `"admin"`. The hierarchical format enables dynamic policy registration, permission discovery, and the Manage-implies-all pattern. See `references/permissions-pattern.md`.

### CRITICAL: Always Generate the DI Extension Method

Every module must have exactly one `AddDenali{ModuleName}()` extension method that registers all services. Consumers must never need to register individual handlers, validators, or DbContexts manually. The extension method is the module's public API for service registration.

### CRITICAL: Cross-Module References Use FK IDs Only

When an entity references an entity from another module, store only the foreign key ID property. Never add navigation properties across module boundaries. The consuming application configures cross-module relationships in its own DbContext. See `references/shared-entity-patterns.md`.

```csharp
// WRONG: Navigation property across modules
public class Employee : Person
{
    public int OrganizationId { get; set; }
    public Organization Organization { get; set; }  // Cross-module navigation
}

// RIGHT: FK ID only
public class Employee : Person
{
    public int? OrganizationId { get; set; }  // FK only, no navigation
}
```

## Anti-Patterns Table

| Anti-Pattern | Why It's Wrong | Correct Approach |
|--------------|----------------|------------------|
| **Business logic in shared kernel** | Couples all consumers to one application's rules. Makes the kernel impossible to evolve without breaking every consumer. | The kernel provides entities and contracts. Business rules live in the consuming application. |
| **God entity with all interfaces** | An entity that implements every possible interface (`IAuditable`, `ISoftDeletable`, `IVersionable`, `ITenantScoped`, `IHierarchical`) becomes impossible to understand and test. | Implement only the interfaces that apply. IAuditable and ISoftDeletable are standard; others are case-by-case. |
| **Manual DI registration** | Requiring consumers to register each handler, validator, and service individually is error-prone and breaks when new features are added. | The `AddDenali{ModuleName}()` extension scans the assembly for handlers and validators automatically. |
| **Hardcoded configuration values** | Connection strings, schema names, and cache durations baked into code cannot be overridden per environment. | Use `Denali{ModuleName}Options` with fluent methods and `Validate()`. See `references/options-pattern.md`. |
| **Circular dependencies between modules** | Module A depending on Module B while Module B depends on Module A creates deployment order issues and makes independent versioning impossible. | All modules depend only on `Core.Abstractions`. Cross-module references use FK IDs. See `references/nuget-package-structure.md`. |
| **Missing audit interfaces** | Entities without `IAuditable` silently lose all audit trail data. The DbContext override cannot populate fields that do not exist. | Every entity implements `IAuditable` and `ISoftDeletable`. No exceptions. |
| **Unfiltered unique indexes** | A unique index without `HasFilter("[IsDeleted] = 0")` prevents restoring soft-deleted records with the same unique key. | Always use filtered unique indexes on soft-deletable entities. See `references/ef-configuration-patterns.md`. |
| **Navigation properties across modules** | Cross-module navigation properties create compile-time coupling between NuGet packages that should be independently deployable. | Use FK ID properties only. The consuming application configures relationships. See `references/shared-entity-patterns.md`. |
| **Shared DbContext across modules** | One DbContext serving multiple modules makes it impossible to version, deploy, or test modules independently. | Each module has its own DbContext. The consumer's AppDbContext can apply configurations from multiple module assemblies. |
| **Freeform permission strings** | Strings like `"admin"`, `"can_edit"`, or `"training-access"` have no structure, cannot be discovered programmatically, and do not support the Manage-implies-all hierarchy. | Follow `Module.Resource.Action` format. See `references/permissions-pattern.md`. |

## Error Recovery

### Problem: Circular Dependency Between Modules

```
Symptom: Module A references Module B, Module B references Module A.
Build fails with circular reference error.
```

**Action:**
1. Identify the shared types causing the cycle. Extract them to `DenaliDataSystems.Core.Abstractions` if they are truly universal, or create a new shared contracts package
2. Replace navigation properties with FK ID properties. The cross-module relationship should be configured only in the consuming application's DbContext
3. If both modules need to react to events from the other, use domain events (INotification) dispatched through FreeMediator in the consuming application, not direct module-to-module references
4. Verify the dependency tree: every module should depend only on `Core.Abstractions`, never on another domain module. See `references/nuget-package-structure.md`

### Problem: Breaking Change in Shared Entity

```
Symptom: Renaming a property, removing a column, or changing an interface
breaks multiple consuming applications after a NuGet update.
```

**Action:**
1. Never rename or remove public properties in a PATCH or MINOR version. These are MAJOR version changes
2. For property additions, add them as nullable to preserve backward compatibility. Existing consumers that do not set the new property will get `null`, which is safe
3. For interface changes, create a new interface (e.g., `IAuditableV2`) and have the entity implement both interfaces during a transition period
4. Update the version following SemVer: MAJOR for breaking changes, MINOR for additive changes, PATCH for bug fixes
5. Document the breaking change in CHANGELOG.md and communicate to all consuming teams before publishing

### Problem: Options Pattern Configuration Missing at Runtime

```
Symptom: InvalidOperationException -- "Connection string is required.
Call UseSqlServer() or UseInMemoryDatabase()."
```

**Action:**
1. The `Validate()` method in `Denali{ModuleName}Options` correctly caught the misconfiguration. Verify that the consumer's `Program.cs` calls `options.UseSqlServer(connectionString)` or `options.UseInMemoryDatabase()`
2. Check that the connection string is not null or empty. Common cause: `builder.Configuration.GetConnectionString("Default")` returns null because the key is missing from `appsettings.json`
3. For test projects, ensure `UseInMemoryDatabase()` is called with a unique name per test: `options.UseInMemoryDatabase($"TestDb_{Guid.NewGuid()}")`
4. If the consumer needs to defer configuration, verify the options lambda is not evaluating the connection string at registration time when it is not yet available

### Problem: Soft-Delete Query Filter Not Applied

```
Symptom: Deleted records appear in query results even though
IsDeleted is set to true in the database.
```

**Action:**
1. Verify the entity implements `ISoftDeletable`. The global query filter only applies to entities with this interface
2. Verify the DbContext's `OnModelCreating` calls `builder.HasQueryFilter(e => !e.IsDeleted)` or uses the dynamic filter application pattern from `references/ef-configuration-patterns.md`
3. Check for `IgnoreQueryFilters()` calls in the query that might be bypassing filters unintentionally
4. If using a shared AppDbContext in the consumer, verify that `ApplyConfigurationsFromAssembly` is called for the module's assembly

## Integration with Other Skills

- **`dotnet-vertical-slice`** -- Consuming applications use vertical slice architecture to build features on top of the shared kernel. The kernel provides entities and CQRS templates; the vertical slice skill scaffolds the feature folders, endpoints, and UI components that use them. Start with `shared-kernel-generator` to build the module, then use `dotnet-vertical-slice` to build features in the consuming application.
- **`ef-migration-manager`** -- When adding or modifying entities in a shared kernel module, use `ef-migration-manager` to create migrations for the module's DbContext. Each module uses its own schema (e.g., `picklists`, `people`, `training`) to avoid table name collisions. Migrations should be generated against the module's DbContext, not the consumer's AppDbContext.
- **`nuget-package-scaffold`** -- After generating all module code, use `nuget-package-scaffold` to finalize the `.csproj` metadata, `Directory.Build.props`, `Directory.Packages.props`, and CI/CD publishing pipeline. The package structure follows the conventions documented in `references/nuget-package-structure.md`.
- **`dotnet-architecture-checklist`** -- Before publishing a new version of a shared kernel module, run the architecture checklist to verify: all entities implement required interfaces, all handlers are internal sealed, all configurations use filtered indexes, Options pattern is properly implemented, and DI extension method is complete.

## Validation Checklist

- [ ] Entities implement IAuditable and ISoftDeletable interfaces
- [ ] Entities have `[AuditedEntity]` attribute where appropriate
- [ ] Vertical slice structure (Features/{Feature}/Commands/Queries/Entities/Data)
- [ ] Options pattern implemented (`Denali{ModuleName}Options` with `Validate()`)
- [ ] DI extension method (`AddDenali{ModuleName}`) registers all services
- [ ] Initialize method (`InitializeDenali{ModuleName}Async`) handles migrations and seeding
- [ ] Permission constants follow `Module.Resource.Action` format
- [ ] Commands are sealed records with internal sealed handlers
- [ ] Validators use FluentValidation with async uniqueness rules
- [ ] DbContext has global query filter for soft delete
- [ ] DbContext intercepts hard deletes and converts to soft deletes
- [ ] DbContext auto-updates audit fields on `SaveChangesAsync`
- [ ] EF configurations use filtered unique indexes (`HasFilter("[IsDeleted] = 0")`)
- [ ] EF configurations specify schema name, datetime2(0) precision, and index naming conventions
- [ ] Cross-module references use FK IDs only (no navigation properties)
- [ ] `.csproj` includes NuGet package metadata and Core.Abstractions reference

## References

- `references/shared-entity-patterns.md` -- IAuditable, ISoftDeletable, `[AuditedEntity]` patterns, cross-module FK reference pattern
- `references/nuget-package-structure.md` -- DenaliDataSystems package structure, Directory.Build.props, versioning strategy, CI/CD publishing
- `references/ef-configuration-patterns.md` -- Vertical slice EF configuration, filtered indexes, global query filters, relationship patterns
- `references/options-pattern.md` -- Module configuration patterns, fluent API, multi-module registration, appsettings.json binding
- `references/permissions-pattern.md` -- Feature.Resource.Action permission model, policy registration, Blazor authorization, role mapping
- `references/domain-module-templates.md` -- Complete module templates for DI, entities, commands, queries, DbContext, and README
