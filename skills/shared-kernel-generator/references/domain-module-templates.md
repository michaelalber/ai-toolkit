# Domain Module Templates

## Complete Module Structure

This document provides complete templates for creating new DenaliDataSystems modules.

## Directory Structure

```
DenaliDataSystems.{ModuleName}/
├── DenaliDataSystems.{ModuleName}.csproj
├── {ModuleName}DependencyInjection.cs
├── Extensions/
│   └── Denali{ModuleName}Options.cs
├── Features/
│   └── {Feature}Feature/
│       ├── Commands/
│       │   ├── Create{Entity}/
│       │   │   ├── Create{Entity}Command.cs
│       │   │   └── Create{Entity}Validator.cs
│       │   ├── Update{Entity}/
│       │   │   ├── Update{Entity}Command.cs
│       │   │   └── Update{Entity}Validator.cs
│       │   └── Delete{Entity}/
│       │       └── Delete{Entity}Command.cs
│       ├── Queries/
│       │   ├── Get{Entity}ById/
│       │   │   └── Get{Entity}ByIdQuery.cs
│       │   └── Get{Entity}List/
│       │       ├── Get{Entity}ListQuery.cs
│       │       └── {Entity}ListDto.cs
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

## Project File Template

```xml
<!-- DenaliDataSystems.{ModuleName}.csproj -->
<Project Sdk="Microsoft.NET.Sdk">

  <PropertyGroup>
    <PackageId>DenaliDataSystems.{ModuleName}</PackageId>
    <Title>DenaliDataSystems {ModuleName} Module</Title>
    <Description>
      {Module description here}
    </Description>
    <PackageTags>denali;shared-kernel;{modulename}</PackageTags>
    <PackageReadmeFile>README.md</PackageReadmeFile>
    <PackageLicenseExpression>MIT</PackageLicenseExpression>
  </PropertyGroup>

  <ItemGroup>
    <None Include="README.md" Pack="true" PackagePath="" />
  </ItemGroup>

  <ItemGroup>
    <ProjectReference Include="..\DenaliDataSystems.Core.Abstractions\DenaliDataSystems.Core.Abstractions.csproj" />
  </ItemGroup>

  <ItemGroup>
    <PackageReference Include="Microsoft.EntityFrameworkCore" />
    <PackageReference Include="Microsoft.EntityFrameworkCore.SqlServer" />
    <PackageReference Include="Microsoft.Extensions.DependencyInjection.Abstractions" />
    <PackageReference Include="Microsoft.Extensions.Caching.Memory" />
    <PackageReference Include="FreeMediator" />
    <PackageReference Include="FluentValidation" />
    <PackageReference Include="FluentValidation.DependencyInjectionExtensions" />
  </ItemGroup>

</Project>
```

## Dependency Injection Template

```csharp
// {ModuleName}DependencyInjection.cs
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
            {
                opt.UseInMemoryDatabase(moduleOptions.InMemoryDatabaseName);
            }
            else
            {
                opt.UseSqlServer(moduleOptions.ConnectionString!);
            }
        });

        services.AddFreeMediator(typeof({ModuleName}DependencyInjection).Assembly);
        services.AddValidatorsFromAssembly(typeof({ModuleName}DependencyInjection).Assembly);

        if (options.CacheExpirationMinutes > 0)
        {
            services.AddMemoryCache();
        }

        return services;
    }

    public static async Task InitializeDenali{ModuleName}Async(this IServiceProvider services)
    {
        using var scope = services.CreateScope();
        var options = scope.ServiceProvider.GetRequiredService<Denali{ModuleName}Options>();
        var db = scope.ServiceProvider.GetRequiredService<{ModuleName}DbContext>();

        if (options.AutoMigrateDatabase && !options.IsInMemoryDatabase)
        {
            await db.Database.MigrateAsync();
        }

        if (options.SeedDemoData)
        {
            await SeedDemoDataAsync(db);
        }
    }

    private static async Task SeedDemoDataAsync({ModuleName}DbContext db)
    {
        // Implement demo data seeding
    }
}
```

## Options Class Template

```csharp
// Extensions/Denali{ModuleName}Options.cs
namespace DenaliDataSystems.{ModuleName}.Extensions;

public sealed class Denali{ModuleName}Options
{
    public string? ConnectionString { get; set; }
    public bool IsInMemoryDatabase { get; set; }
    public string InMemoryDatabaseName { get; set; } = "Denali{ModuleName}";
    public int CacheExpirationMinutes { get; set; } = 30;
    public bool AutoMigrateDatabase { get; set; } = true;
    public bool SeedDemoData { get; set; } = false;

    public Denali{ModuleName}Options UseSqlServer(string connectionString)
    {
        ConnectionString = connectionString ?? throw new ArgumentNullException(nameof(connectionString));
        IsInMemoryDatabase = false;
        return this;
    }

    public Denali{ModuleName}Options UseInMemoryDatabase(string? databaseName = null)
    {
        IsInMemoryDatabase = true;
        if (databaseName != null) InMemoryDatabaseName = databaseName;
        return this;
    }

    public Denali{ModuleName}Options WithCacheExpiration(int minutes)
    {
        CacheExpirationMinutes = minutes;
        return this;
    }

    public Denali{ModuleName}Options WithDemoData()
    {
        SeedDemoData = true;
        return this;
    }

    internal void Validate()
    {
        if (!IsInMemoryDatabase && string.IsNullOrWhiteSpace(ConnectionString))
        {
            throw new InvalidOperationException(
                "Connection string required. Call UseSqlServer() or UseInMemoryDatabase().");
        }
    }
}
```

## Entity Template

```csharp
// Features/{Feature}Feature/Entities/Models/{Entity}.cs
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

## DbContext Template

```csharp
// Features/{Feature}Feature/Data/{ModuleName}DbContext.cs
using Microsoft.EntityFrameworkCore;
using DenaliDataSystems.Core.Abstractions.Contracts;
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
        modelBuilder.ApplyConfigurationsFromAssembly(typeof({ModuleName}DbContext).Assembly);
    }

    public override Task<int> SaveChangesAsync(CancellationToken cancellationToken = default)
    {
        UpdateAuditFields();
        return base.SaveChangesAsync(cancellationToken);
    }

    private void UpdateAuditFields()
    {
        var entries = ChangeTracker.Entries()
            .Where(e => e.State is EntityState.Added or EntityState.Modified or EntityState.Deleted);

        var now = DateTime.UtcNow;

        foreach (var entry in entries)
        {
            if (entry.Entity is IAuditable auditable)
            {
                if (entry.State == EntityState.Added)
                {
                    auditable.CreatedAt = now;
                    auditable.CreatedBy ??= "System";
                }
                else if (entry.State == EntityState.Modified)
                {
                    auditable.ModifiedAt = now;
                    auditable.ModifiedBy = "System";
                }
            }

            if (entry.State == EntityState.Deleted && entry.Entity is ISoftDeletable soft)
            {
                entry.State = EntityState.Modified;
                soft.IsDeleted = true;
                soft.DeletedAt = now;
                soft.DeletedBy = "System";
            }
        }
    }
}
```

## Entity Configuration Template

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

        // Audit fields
        builder.Property(e => e.CreatedAt)
            .HasColumnType("datetime2(0)")
            .HasDefaultValueSql("GETUTCDATE()");

        builder.Property(e => e.CreatedBy)
            .HasMaxLength(100)
            .IsRequired();

        builder.Property(e => e.ModifiedAt)
            .HasColumnType("datetime2(0)");

        builder.Property(e => e.ModifiedBy)
            .HasMaxLength(100);

        // Soft delete
        builder.Property(e => e.IsDeleted)
            .HasDefaultValue(false);

        builder.Property(e => e.DeletedAt)
            .HasColumnType("datetime2(0)");

        builder.Property(e => e.DeletedBy)
            .HasMaxLength(100);

        // Global query filter
        builder.HasQueryFilter(e => !e.IsDeleted);

        // Indexes
        builder.HasIndex(e => e.Name)
            .HasFilter("[IsDeleted] = 0")
            .HasDatabaseName("IX_{Entities}_Name");

        builder.HasIndex(e => e.IsActive)
            .HasDatabaseName("IX_{Entities}_IsActive");
    }
}
```

## Create Command Template

```csharp
// Features/{Feature}Feature/Commands/Create{Entity}/Create{Entity}Command.cs
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

## Create Command Validator Template

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
            .NotEmpty().WithMessage("Name is required")
            .MaximumLength(100).WithMessage("Name cannot exceed 100 characters")
            .MustAsync(async (name, ct) =>
                !await db.{Entities}.AnyAsync(e => e.Name == name && !e.IsDeleted, ct))
            .WithMessage("An entity with this name already exists");

        RuleFor(x => x.Description)
            .MaximumLength(500)
            .When(x => x.Description is not null);
    }
}
```

## Update Command Template

```csharp
// Features/{Feature}Feature/Commands/Update{Entity}/Update{Entity}Command.cs
using FreeMediator;
using Microsoft.EntityFrameworkCore;
using DenaliDataSystems.{ModuleName}.Features.{Feature}Feature.Data;

namespace DenaliDataSystems.{ModuleName}.Features.{Feature}Feature.Commands.Update{Entity};

public sealed record Update{Entity}Command(
    int Id,
    string Name,
    string? Description,
    bool IsActive) : IRequest<bool>;

internal sealed class Update{Entity}Handler(
    {ModuleName}DbContext db) : IRequestHandler<Update{Entity}Command, bool>
{
    public async Task<bool> Handle(Update{Entity}Command request, CancellationToken ct)
    {
        var entity = await db.{Entities}.FindAsync([request.Id], ct);
        if (entity is null) return false;

        entity.Name = request.Name;
        entity.Description = request.Description;
        entity.IsActive = request.IsActive;

        await db.SaveChangesAsync(ct);
        return true;
    }
}
```

## Delete Command Template

```csharp
// Features/{Feature}Feature/Commands/Delete{Entity}/Delete{Entity}Command.cs
using FreeMediator;
using DenaliDataSystems.{ModuleName}.Features.{Feature}Feature.Data;

namespace DenaliDataSystems.{ModuleName}.Features.{Feature}Feature.Commands.Delete{Entity};

public sealed record Delete{Entity}Command(int Id) : IRequest<bool>;

internal sealed class Delete{Entity}Handler(
    {ModuleName}DbContext db) : IRequestHandler<Delete{Entity}Command, bool>
{
    public async Task<bool> Handle(Delete{Entity}Command request, CancellationToken ct)
    {
        var entity = await db.{Entities}.FindAsync([request.Id], ct);
        if (entity is null) return false;

        db.{Entities}.Remove(entity); // Soft delete via SaveChanges override
        await db.SaveChangesAsync(ct);
        return true;
    }
}
```

## Get By Id Query Template

```csharp
// Features/{Feature}Feature/Queries/Get{Entity}ById/Get{Entity}ByIdQuery.cs
using FreeMediator;
using Microsoft.EntityFrameworkCore;
using DenaliDataSystems.{ModuleName}.Features.{Feature}Feature.Data;
using DenaliDataSystems.{ModuleName}.Features.{Feature}Feature.Entities.Models;

namespace DenaliDataSystems.{ModuleName}.Features.{Feature}Feature.Queries.Get{Entity}ById;

public sealed record Get{Entity}ByIdQuery(int Id) : IRequest<{Entity}?>;

internal sealed class Get{Entity}ByIdHandler(
    {ModuleName}DbContext db) : IRequestHandler<Get{Entity}ByIdQuery, {Entity}?>
{
    public async Task<{Entity}?> Handle(Get{Entity}ByIdQuery request, CancellationToken ct)
    {
        return await db.{Entities}
            .AsNoTracking()
            .FirstOrDefaultAsync(e => e.Id == request.Id, ct);
    }
}
```

## Get List Query Template

```csharp
// Features/{Feature}Feature/Queries/Get{Entity}List/Get{Entity}ListQuery.cs
using FreeMediator;
using Microsoft.EntityFrameworkCore;
using DenaliDataSystems.{ModuleName}.Features.{Feature}Feature.Data;

namespace DenaliDataSystems.{ModuleName}.Features.{Feature}Feature.Queries.Get{Entity}List;

public sealed record Get{Entity}ListQuery(
    string? SearchTerm = null,
    bool? IsActive = null,
    int Page = 1,
    int PageSize = 20) : IRequest<{Entity}ListResult>;

public sealed record {Entity}ListResult(
    IReadOnlyList<{Entity}ListDto> Items,
    int TotalCount,
    int Page,
    int PageSize);

public sealed record {Entity}ListDto(
    int Id,
    string Name,
    string? Description,
    bool IsActive,
    DateTime CreatedAt);

internal sealed class Get{Entity}ListHandler(
    {ModuleName}DbContext db) : IRequestHandler<Get{Entity}ListQuery, {Entity}ListResult>
{
    public async Task<{Entity}ListResult> Handle(Get{Entity}ListQuery request, CancellationToken ct)
    {
        var query = db.{Entities}.AsNoTracking();

        if (!string.IsNullOrWhiteSpace(request.SearchTerm))
        {
            query = query.Where(e => e.Name.Contains(request.SearchTerm));
        }

        if (request.IsActive.HasValue)
        {
            query = query.Where(e => e.IsActive == request.IsActive.Value);
        }

        var totalCount = await query.CountAsync(ct);

        var items = await query
            .OrderBy(e => e.Name)
            .Skip((request.Page - 1) * request.PageSize)
            .Take(request.PageSize)
            .Select(e => new {Entity}ListDto(
                e.Id,
                e.Name,
                e.Description,
                e.IsActive,
                e.CreatedAt))
            .ToListAsync(ct);

        return new {Entity}ListResult(items, totalCount, request.Page, request.PageSize);
    }
}
```

## Permissions Template

```csharp
// Permissions/{Feature}Permissions.cs
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

## README Template

```markdown
# DenaliDataSystems.{ModuleName}

{Module description}

## Installation

```bash
dotnet add package DenaliDataSystems.{ModuleName}
```

## Features

- {Feature 1}
- {Feature 2}

## Usage

### Registration

```csharp
builder.Services.AddDenali{ModuleName}(options =>
{
    options.UseSqlServer(connectionString);
});
```

### Commands and Queries

```csharp
// Create
var id = await mediator.Send(new Create{Entity}Command("Name"));

// Read
var entity = await mediator.Send(new Get{Entity}ByIdQuery(id));

// List
var result = await mediator.Send(new Get{Entity}ListQuery(SearchTerm: "test"));

// Update
await mediator.Send(new Update{Entity}Command(id, "New Name", null, true));

// Delete
await mediator.Send(new Delete{Entity}Command(id));
```

## Permissions

| Permission | Description |
|------------|-------------|
| `{ModuleName}.{Feature}.Manage` | Full access |
| `{ModuleName}.{Feature}.Read` | Read-only access |
| `{ModuleName}.{Feature}.Create` | Create new entities |
| `{ModuleName}.{Feature}.Update` | Update existing entities |
| `{ModuleName}.{Feature}.Delete` | Delete entities |

## Database Schema

Tables are created in the `{modulename}` schema.
```
