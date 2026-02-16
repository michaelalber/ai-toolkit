---
name: shared-kernel-generator
description: Generates shared domain modules as NuGet packages following DenaliDataSystems patterns. Use when creating reusable modules (PickLists, People, Training, Organization, Location, Workflow, Communication) with vertical slice architecture. Triggers on phrases like "shared kernel", "common module", "shared entities", "create nuget package", "reusable domain", "denali module".
---

# Shared Kernel Generator

> "A Shared Kernel is a designated subset of the domain model that two or more teams agree to share, reducing duplication while maintaining bounded contexts." — Eric Evans, Domain-Driven Design

This skill generates standardized shared domain modules following the **DenaliDataSystems** patterns established in `denali-core-library`.

## Quick Start

1. **Identify shared domain**: PickLists, People, Training, Organization, Location, Workflow, Communication
2. **Generate vertical slice structure** using templates below
3. **Create entities** with IAuditable/ISoftDeletable interfaces
4. **Implement Commands/Queries** with FreeMediator
5. **Set up Options pattern** for module configuration
6. **Configure permissions** using Feature.Resource.Action format

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
├── DenaliDataSystems.{ModuleName}.csproj
├── {ModuleName}DependencyInjection.cs      # AddDenali{ModuleName}() extension
├── Extensions/
│   └── Denali{ModuleName}Options.cs        # Options pattern for configuration
├── Features/
│   └── {Feature}Feature/
│       ├── Commands/
│       │   ├── Create{Entity}/
│       │   │   ├── Create{Entity}Command.cs
│       │   │   └── Create{Entity}Validator.cs
│       │   ├── Update{Entity}/
│       │   └── Delete{Entity}/
│       ├── Queries/
│       │   ├── Get{Entity}ById/
│       │   └── Get{Entity}List/
│       ├── Entities/
│       │   └── Models/
│       │       └── {Entity}.cs
│       └── Data/
│           ├── {ModuleName}DbContext.cs
│           └── Configurations/
│               └── {Entity}Configuration.cs
├── Permissions/
│   └── {Feature}Permissions.cs
└── README.md
```

## Core Abstractions

### IAuditable Interface
```csharp
// DenaliDataSystems.Core.Abstractions/Contracts/IAuditable.cs
namespace DenaliDataSystems.Core.Abstractions.Contracts;

public interface IAuditable
{
    DateTime CreatedAt { get; set; }
    string CreatedBy { get; set; }
    DateTime? ModifiedAt { get; set; }
    string? ModifiedBy { get; set; }
}
```

### ISoftDeletable Interface
```csharp
// DenaliDataSystems.Core.Abstractions/Contracts/ISoftDeletable.cs
namespace DenaliDataSystems.Core.Abstractions.Contracts;

public interface ISoftDeletable
{
    bool IsDeleted { get; set; }
    DateTime? DeletedAt { get; set; }
    string? DeletedBy { get; set; }
}
```

### AuditedEntity Attribute
```csharp
// DenaliDataSystems.Core.Abstractions/Attributes/AuditedEntityAttribute.cs
namespace DenaliDataSystems.Core.Abstractions.Attributes;

/// <summary>
/// Marks an entity for automatic history tracking.
/// Changes are logged to {TableName}_History table.
/// </summary>
[AttributeUsage(AttributeTargets.Class, Inherited = false)]
public sealed class AuditedEntityAttribute : Attribute { }
```

## Entity Templates

### Entity with Interfaces (Preferred Pattern)
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

## Options Pattern

### Module Options Class
```csharp
// Extensions/Denali{ModuleName}Options.cs
namespace DenaliDataSystems.{ModuleName}.Extensions;

public sealed class Denali{ModuleName}Options
{
    /// <summary>
    /// SQL Server connection string.
    /// </summary>
    public string? ConnectionString { get; set; }

    /// <summary>
    /// Use in-memory database for testing.
    /// </summary>
    public bool IsInMemoryDatabase { get; set; }

    /// <summary>
    /// Cache expiration in minutes. Default: 30.
    /// </summary>
    public int CacheExpirationMinutes { get; set; } = 30;

    /// <summary>
    /// Auto-migrate database on startup. Default: true.
    /// </summary>
    public bool AutoMigrateDatabase { get; set; } = true;

    /// <summary>
    /// Seed demo data. Default: false.
    /// </summary>
    public bool SeedDemoData { get; set; } = false;

    /// <summary>
    /// Configures SQL Server with the specified connection string.
    /// </summary>
    public Denali{ModuleName}Options UseSqlServer(string connectionString)
    {
        ConnectionString = connectionString;
        IsInMemoryDatabase = false;
        return this;
    }

    /// <summary>
    /// Configures in-memory database for testing.
    /// </summary>
    public Denali{ModuleName}Options UseInMemoryDatabase()
    {
        IsInMemoryDatabase = true;
        return this;
    }

    /// <summary>
    /// Sets cache expiration time.
    /// </summary>
    public Denali{ModuleName}Options WithCacheExpiration(int minutes)
    {
        CacheExpirationMinutes = minutes;
        return this;
    }

    /// <summary>
    /// Enables demo data seeding.
    /// </summary>
    public Denali{ModuleName}Options WithDemoData()
    {
        SeedDemoData = true;
        return this;
    }
}
```

## Dependency Injection Extension

### Module Registration
```csharp
// {ModuleName}DependencyInjection.cs
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.DependencyInjection;
using DenaliDataSystems.{ModuleName}.Extensions;
using DenaliDataSystems.{ModuleName}.Features.{Feature}Feature.Data;

namespace DenaliDataSystems.{ModuleName};

public static class {ModuleName}DependencyInjection
{
    /// <summary>
    /// Registers all services for the {ModuleName} module.
    /// </summary>
    public static IServiceCollection AddDenali{ModuleName}(
        this IServiceCollection services,
        Action<Denali{ModuleName}Options> configureOptions)
    {
        var options = new Denali{ModuleName}Options();
        configureOptions(options);

        // Register options
        services.AddSingleton(options);

        // Register DbContext
        if (options.IsInMemoryDatabase)
        {
            services.AddDbContext<{ModuleName}DbContext>(opt =>
                opt.UseInMemoryDatabase("Denali{ModuleName}"));
        }
        else
        {
            services.AddDbContext<{ModuleName}DbContext>(opt =>
                opt.UseSqlServer(options.ConnectionString));
        }

        // Register FreeMediator handlers from this assembly
        services.AddFreeMediator(typeof({ModuleName}DependencyInjection).Assembly);

        // Register caching if needed
        if (options.CacheExpirationMinutes > 0)
        {
            services.AddMemoryCache();
        }

        return services;
    }
}
```

## Permission Model

### Permission Constants
```csharp
// Permissions/{Feature}Permissions.cs
namespace DenaliDataSystems.{ModuleName}.Permissions;

/// <summary>
/// Permission constants for {Feature} feature.
/// Format: Feature.Resource.Action
/// </summary>
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

## Command/Query Templates (FreeMediator)

### Command with Internal Handler
```csharp
// Features/{Feature}Feature/Commands/Create{Entity}/Create{Entity}Command.cs
using FreeMediator;
using FluentValidation;
using Microsoft.EntityFrameworkCore;
using DenaliDataSystems.{ModuleName}.Features.{Feature}Feature.Data;
using DenaliDataSystems.{ModuleName}.Features.{Feature}Feature.Entities.Models;

namespace DenaliDataSystems.{ModuleName}.Features.{Feature}Feature.Commands.Create{Entity};

public sealed record Create{Entity}Command(
    string Name,
    string? Description = null) : IRequest<int>;

internal sealed class Create{Entity}Handler(
    {ModuleName}DbContext db) : IRequestHandler<Create{Entity}Command, int>
{
    public async Task<int> Handle(
        Create{Entity}Command request,
        CancellationToken cancellationToken)
    {
        var entity = new {Entity}
        {
            Name = request.Name,
            Description = request.Description,
            CreatedAt = DateTime.UtcNow,
            CreatedBy = "System" // TODO: Get from ICurrentUser
        };

        db.{Entities}.Add(entity);
        await db.SaveChangesAsync(cancellationToken);

        return entity.Id;
    }
}
```

### FluentValidation Validator
```csharp
// Features/{Feature}Feature/Commands/Create{Entity}/Create{Entity}Validator.cs
using FluentValidation;
using Microsoft.EntityFrameworkCore;
using DenaliDataSystems.{ModuleName}.Features.{Feature}Feature.Data;

namespace DenaliDataSystems.{ModuleName}.Features.{Feature}Feature.Commands.Create{Entity};

public sealed class Create{Entity}Validator : AbstractValidator<Create{Entity}Command>
{
    public Create{Entity}Validator({ModuleName}DbContext db)
    {
        RuleFor(x => x.Name)
            .NotEmpty()
            .WithMessage("Name is required")
            .MaximumLength(100)
            .WithMessage("Name cannot exceed 100 characters")
            .MustAsync(async (name, ct) =>
                !await db.{Entities}.AnyAsync(e => e.Name == name && !e.IsDeleted, ct))
            .WithMessage("An entity with this name already exists");

        RuleFor(x => x.Description)
            .MaximumLength(500)
            .When(x => x.Description is not null);
    }
}
```

## DbContext Pattern

### Module DbContext with Global Query Filters
```csharp
// Features/{Feature}Feature/Data/{ModuleName}DbContext.cs
using Microsoft.EntityFrameworkCore;
using DenaliDataSystems.{ModuleName}.Features.{Feature}Feature.Entities.Models;

namespace DenaliDataSystems.{ModuleName}.Features.{Feature}Feature.Data;

public class {ModuleName}DbContext : DbContext
{
    public {ModuleName}DbContext(DbContextOptions<{ModuleName}DbContext> options)
        : base(options)
    {
    }

    public DbSet<{Entity}> {Entities} => Set<{Entity}>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        base.OnModelCreating(modelBuilder);

        // Apply configurations from this assembly
        modelBuilder.ApplyConfigurationsFromAssembly(typeof({ModuleName}DbContext).Assembly);

        // Global query filter for soft delete
        modelBuilder.Entity<{Entity}>()
            .HasQueryFilter(e => !e.IsDeleted);
    }

    public override Task<int> SaveChangesAsync(CancellationToken cancellationToken = default)
    {
        UpdateAuditFields();
        return base.SaveChangesAsync(cancellationToken);
    }

    private void UpdateAuditFields()
    {
        var entries = ChangeTracker.Entries()
            .Where(e => e.State is EntityState.Added or EntityState.Modified);

        foreach (var entry in entries)
        {
            if (entry.Entity is IAuditable auditable)
            {
                if (entry.State == EntityState.Added)
                {
                    auditable.CreatedAt = DateTime.UtcNow;
                    auditable.CreatedBy ??= "System";
                }
                else
                {
                    auditable.ModifiedAt = DateTime.UtcNow;
                    auditable.ModifiedBy = "System"; // TODO: Get from ICurrentUser
                }
            }
        }
    }
}
```

## EF Core Configuration

### Entity Configuration
```csharp
// Features/{Feature}Feature/Data/Configurations/{Entity}Configuration.cs
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using DenaliDataSystems.{ModuleName}.Features.{Feature}Feature.Entities.Models;

namespace DenaliDataSystems.{ModuleName}.Features.{Feature}Feature.Data.Configurations;

public class {Entity}Configuration : IEntityTypeConfiguration<{Entity}>
{
    public void Configure(EntityTypeBuilder<{Entity}> builder)
    {
        builder.ToTable("{Entities}", "{modulename}");

        builder.HasKey(e => e.Id);

        builder.Property(e => e.Name)
            .HasMaxLength(100)
            .IsRequired();

        builder.Property(e => e.Description)
            .HasMaxLength(500);

        builder.Property(e => e.CreatedBy)
            .HasMaxLength(100)
            .IsRequired();

        builder.Property(e => e.ModifiedBy)
            .HasMaxLength(100);

        builder.Property(e => e.DeletedBy)
            .HasMaxLength(100);

        // Indexes
        builder.HasIndex(e => e.Name)
            .IsUnique()
            .HasFilter("[IsDeleted] = 0")
            .HasDatabaseName($"UX_{Entities}_Name");

        builder.HasIndex(e => e.IsActive)
            .HasDatabaseName($"IX_{Entities}_IsActive");
    }
}
```

## Consumer Usage

### Installing the Package
```bash
dotnet add package DenaliDataSystems.{ModuleName}
```

### Registering the Module
```csharp
// In Program.cs or Startup.cs
builder.Services.AddDenali{ModuleName}(options =>
{
    options.UseSqlServer(builder.Configuration.GetConnectionString("Default")!);
    options.WithCacheExpiration(60);
});

// Or for testing
builder.Services.AddDenali{ModuleName}(options =>
{
    options.UseInMemoryDatabase();
    options.WithDemoData();
});
```

### Using FreeMediator
```csharp
// In a controller or service
public class {Entity}Controller(IMediator mediator) : ControllerBase
{
    [HttpPost]
    public async Task<IActionResult> Create(Create{Entity}Command command)
    {
        var id = await mediator.Send(command);
        return CreatedAtAction(nameof(GetById), new { id }, id);
    }
}
```

## Output Format

```markdown
## Shared Kernel Module: [Module Name]

**Package**: `DenaliDataSystems.[ModuleName]`
**Version**: [X.Y.Z]
**Date**: [Date]

### Features

| Feature | Commands | Queries | Permissions |
|---------|----------|---------|-------------|
| ... | ... | ... | ... |

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

### Usage Example

```csharp
// Registration
builder.Services.AddDenali{ModuleName}(opt => opt.UseSqlServer(connStr));

// Usage
var result = await mediator.Send(new Create{Entity}Command("Name"));
```
```

## Validation Checklist

- [ ] Entities implement IAuditable and ISoftDeletable interfaces
- [ ] Entities have [AuditedEntity] attribute where appropriate
- [ ] Vertical slice structure (Features/{Feature}/Commands/Queries/Entities/Data)
- [ ] Options pattern implemented (Denali{ModuleName}Options)
- [ ] DI extension method (AddDenali{ModuleName})
- [ ] Permission constants follow Feature.Resource.Action format
- [ ] Commands are sealed records with internal handlers
- [ ] Validators use FluentValidation with async rules
- [ ] DbContext has global query filter for soft delete
- [ ] DbContext auto-updates audit fields on SaveChangesAsync
- [ ] EF configurations use filtered unique indexes

## References

- `references/shared-entity-patterns.md` - IAuditable, ISoftDeletable, [AuditedEntity] patterns
- `references/nuget-package-structure.md` - DenaliDataSystems package structure
- `references/ef-configuration-patterns.md` - Vertical slice EF configuration
- `references/options-pattern.md` - Module configuration patterns
- `references/permissions-pattern.md` - Feature.Resource.Action permission model
