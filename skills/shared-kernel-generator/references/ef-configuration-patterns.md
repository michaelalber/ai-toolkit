# EF Core Configuration Patterns

## Vertical Slice File Organization

```
DenaliDataSystems.PickLists/
├── Features/
│   └── PickListFeature/
│       ├── Entities/
│       │   └── Models/
│       │       ├── PickList.cs
│       │       └── PickListItem.cs
│       └── Data/
│           ├── PickListDbContext.cs
│           └── Configurations/
│               ├── PickListConfiguration.cs
│               └── PickListItemConfiguration.cs
```

## Module DbContext Pattern

### DbContext with Global Query Filters
```csharp
// Features/PickListFeature/Data/PickListDbContext.cs
using Microsoft.EntityFrameworkCore;
using DenaliDataSystems.Core.Abstractions.Contracts;
using DenaliDataSystems.PickLists.Features.PickListFeature.Entities.Models;

namespace DenaliDataSystems.PickLists.Features.PickListFeature.Data;

public class PickListDbContext : DbContext
{
    public PickListDbContext(DbContextOptions<PickListDbContext> options)
        : base(options)
    {
    }

    public DbSet<PickList> PickLists => Set<PickList>();
    public DbSet<PickListItem> PickListItems => Set<PickListItem>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        base.OnModelCreating(modelBuilder);

        // Apply all configurations from this assembly
        modelBuilder.ApplyConfigurationsFromAssembly(typeof(PickListDbContext).Assembly);

        // Global query filters for soft delete
        ApplySoftDeleteFilters(modelBuilder);
    }

    private static void ApplySoftDeleteFilters(ModelBuilder modelBuilder)
    {
        // Apply to all entities implementing ISoftDeletable
        foreach (var entityType in modelBuilder.Model.GetEntityTypes())
        {
            if (typeof(ISoftDeletable).IsAssignableFrom(entityType.ClrType))
            {
                var parameter = Expression.Parameter(entityType.ClrType, "e");
                var property = Expression.Property(parameter, nameof(ISoftDeletable.IsDeleted));
                var condition = Expression.Not(property);
                var lambda = Expression.Lambda(condition, parameter);

                modelBuilder.Entity(entityType.ClrType).HasQueryFilter(lambda);
            }
        }
    }

    public override Task<int> SaveChangesAsync(CancellationToken cancellationToken = default)
    {
        UpdateAuditFields();
        return base.SaveChangesAsync(cancellationToken);
    }

    public override int SaveChanges()
    {
        UpdateAuditFields();
        return base.SaveChanges();
    }

    private void UpdateAuditFields()
    {
        var entries = ChangeTracker.Entries()
            .Where(e => e.State is EntityState.Added or EntityState.Modified or EntityState.Deleted);

        var now = DateTime.UtcNow;
        var currentUser = "System"; // TODO: Inject ICurrentUser service

        foreach (var entry in entries)
        {
            if (entry.Entity is IAuditable auditable)
            {
                switch (entry.State)
                {
                    case EntityState.Added:
                        auditable.CreatedAt = now;
                        auditable.CreatedBy ??= currentUser;
                        break;

                    case EntityState.Modified:
                        auditable.ModifiedAt = now;
                        auditable.ModifiedBy = currentUser;
                        break;
                }
            }

            // Handle soft delete
            if (entry.State == EntityState.Deleted && entry.Entity is ISoftDeletable softDeletable)
            {
                entry.State = EntityState.Modified;
                softDeletable.IsDeleted = true;
                softDeletable.DeletedAt = now;
                softDeletable.DeletedBy = currentUser;
            }
        }
    }
}
```

## Entity Configuration Pattern

### Standard Configuration
```csharp
// Features/PickListFeature/Data/Configurations/PickListConfiguration.cs
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using DenaliDataSystems.PickLists.Features.PickListFeature.Entities.Models;

namespace DenaliDataSystems.PickLists.Features.PickListFeature.Data.Configurations;

public class PickListConfiguration : IEntityTypeConfiguration<PickList>
{
    public void Configure(EntityTypeBuilder<PickList> builder)
    {
        // Table mapping with schema
        builder.ToTable("PickLists", "picklists");

        // Primary key
        builder.HasKey(e => e.Id);

        // Properties
        builder.Property(e => e.Name)
            .HasMaxLength(30)
            .IsRequired();

        builder.Property(e => e.Key)
            .HasMaxLength(30)
            .IsRequired();

        builder.Property(e => e.Description)
            .HasMaxLength(255);

        // Audit fields
        ConfigureAuditFields(builder);

        // Soft delete fields
        ConfigureSoftDeleteFields(builder);

        // Indexes
        builder.HasIndex(e => e.Key)
            .IsUnique()
            .HasFilter("[IsDeleted] = 0")
            .HasDatabaseName("UX_PickLists_Key");

        builder.HasIndex(e => e.Name)
            .HasFilter("[IsDeleted] = 0")
            .HasDatabaseName("IX_PickLists_Name");

        builder.HasIndex(e => e.IsActive)
            .HasDatabaseName("IX_PickLists_IsActive");

        // Relationships
        builder.HasMany(e => e.Items)
            .WithOne(e => e.PickList)
            .HasForeignKey(e => e.PickListId)
            .OnDelete(DeleteBehavior.Cascade);
    }

    private static void ConfigureAuditFields(EntityTypeBuilder<PickList> builder)
    {
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
    }

    private static void ConfigureSoftDeleteFields(EntityTypeBuilder<PickList> builder)
    {
        builder.Property(e => e.IsDeleted)
            .HasDefaultValue(false);

        builder.Property(e => e.DeletedAt)
            .HasColumnType("datetime2(0)");

        builder.Property(e => e.DeletedBy)
            .HasMaxLength(100);
    }
}
```

### Child Entity Configuration
```csharp
// Features/PickListFeature/Data/Configurations/PickListItemConfiguration.cs
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using DenaliDataSystems.PickLists.Features.PickListFeature.Entities.Models;

namespace DenaliDataSystems.PickLists.Features.PickListFeature.Data.Configurations;

public class PickListItemConfiguration : IEntityTypeConfiguration<PickListItem>
{
    public void Configure(EntityTypeBuilder<PickListItem> builder)
    {
        builder.ToTable("PickListItems", "picklists");

        builder.HasKey(e => e.Id);

        builder.Property(e => e.Text)
            .HasMaxLength(100)
            .IsRequired();

        builder.Property(e => e.Value)
            .HasMaxLength(100)
            .IsRequired();

        builder.Property(e => e.SortOrder)
            .HasDefaultValue(0);

        builder.Property(e => e.IsDefault)
            .HasDefaultValue(false);

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

        // Indexes
        builder.HasIndex(e => new { e.PickListId, e.Value })
            .IsUnique()
            .HasFilter("[IsDeleted] = 0")
            .HasDatabaseName("UX_PickListItems_PickListId_Value");

        builder.HasIndex(e => new { e.PickListId, e.SortOrder })
            .HasDatabaseName("IX_PickListItems_PickListId_SortOrder");

        builder.HasIndex(e => e.IsActive)
            .HasDatabaseName("IX_PickListItems_IsActive");
    }
}
```

## Filtered Unique Indexes

Always use filtered indexes for unique constraints on soft-deletable entities:

```csharp
// CORRECT: Filtered unique index (allows "deleted" duplicates)
builder.HasIndex(e => e.Key)
    .IsUnique()
    .HasFilter("[IsDeleted] = 0")
    .HasDatabaseName("UX_TableName_ColumnName");

// WRONG: Unfiltered unique (prevents restoring deleted items with same key)
builder.HasIndex(e => e.Key)
    .IsUnique();
```

## Index Naming Convention

```
IX_TableName_ColumnName           # Non-unique index
UX_TableName_ColumnName           # Unique index
IX_TableName_Col1_Col2            # Composite index
FK_ChildTable_ParentTable         # Foreign key constraint name
```

## Enum Conversion

### Store as String (Recommended for Readability)
```csharp
builder.Property(e => e.Status)
    .HasConversion<string>()
    .HasMaxLength(50)
    .HasDefaultValue(PickListStatus.Active);
```

### Store as Int (More Efficient)
```csharp
builder.Property(e => e.Status)
    .HasConversion<int>()
    .HasDefaultValue(PickListStatus.Active);
```

## Date/Time Types

```csharp
// DateTime with precision (no milliseconds for audit dates)
builder.Property(e => e.CreatedAt)
    .HasColumnType("datetime2(0)");

// DateOnly for dates without time
builder.Property(e => e.HireDate)
    .HasColumnType("date");

// Use default value for creation date
builder.Property(e => e.CreatedAt)
    .HasDefaultValueSql("GETUTCDATE()");
```

## Relationship Patterns

### One-to-Many (Parent-Child)
```csharp
// In parent configuration
builder.HasMany(e => e.Items)
    .WithOne(e => e.PickList)
    .HasForeignKey(e => e.PickListId)
    .OnDelete(DeleteBehavior.Cascade);
```

### Self-Referential (Hierarchy)
```csharp
// Employee supervisor relationship
builder.HasOne(e => e.Supervisor)
    .WithMany(e => e.DirectReports)
    .HasForeignKey(e => e.SupervisorId)
    .OnDelete(DeleteBehavior.Restrict)
    .HasConstraintName("FK_Employees_Supervisor");
```

### Cross-Module References

For cross-module references, configure in the consuming application only:

```csharp
// Module entity has FK property but NO navigation
public class Employee : IAuditable, ISoftDeletable
{
    public int? OrganizationId { get; set; }  // FK only, no navigation
}

// In consuming app's DbContext
modelBuilder.Entity<Employee>()
    .HasOne<Organization>()  // No navigation property
    .WithMany()
    .HasForeignKey(e => e.OrganizationId)
    .OnDelete(DeleteBehavior.Restrict);
```

## Global Query Filters

### Soft Delete Filter
```csharp
// Applied automatically in DbContext
modelBuilder.Entity<PickList>()
    .HasQueryFilter(e => !e.IsDeleted);
```

### Bypassing Filters
```csharp
// To include deleted records
var allRecords = await db.PickLists
    .IgnoreQueryFilters()
    .ToListAsync();

// To explicitly query deleted records
var deletedOnly = await db.PickLists
    .IgnoreQueryFilters()
    .Where(e => e.IsDeleted)
    .ToListAsync();
```

## Value Objects with Owned Types

```csharp
// For complex types stored in the same table
builder.OwnsOne(e => e.Address, address =>
{
    address.Property(a => a.Street)
        .HasColumnName("AddressStreet")
        .HasMaxLength(200);

    address.Property(a => a.City)
        .HasColumnName("AddressCity")
        .HasMaxLength(100);

    address.Property(a => a.State)
        .HasColumnName("AddressState")
        .HasMaxLength(50);

    address.Property(a => a.ZipCode)
        .HasColumnName("AddressZipCode")
        .HasMaxLength(20);
});
```

## Inheritance Strategies

### TPH (Table Per Hierarchy) - Single Table
```csharp
// All types in one table with discriminator
builder.HasDiscriminator<string>("PersonType")
    .HasValue<Person>("Person")
    .HasValue<Employee>("Employee")
    .HasValue<Contractor>("Contractor");
```

### TPT (Table Per Type) - Separate Tables
```csharp
// Each type gets its own table, joined by PK
// Base type
builder.ToTable("People", "people");

// Derived type (in separate configuration)
builder.ToTable("Employees", "people");
```

### TPC (Table Per Concrete Type) - No Inheritance Table
```csharp
// Complete tables for each concrete type
builder.UseTpcMappingStrategy();
```

## Consumer Integration

### Consuming Multiple Modules
```csharp
// In consuming application's DbContext
public class AppDbContext : DbContext
{
    // Reference module DbSets
    public DbSet<PickList> PickLists => Set<PickList>();
    public DbSet<Person> People => Set<Person>();
    public DbSet<Employee> Employees => Set<Employee>();
    public DbSet<Organization> Organizations => Set<Organization>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        base.OnModelCreating(modelBuilder);

        // Apply module configurations
        modelBuilder.ApplyConfigurationsFromAssembly(
            typeof(PickListDbContext).Assembly);
        modelBuilder.ApplyConfigurationsFromAssembly(
            typeof(PeopleDbContext).Assembly);
        modelBuilder.ApplyConfigurationsFromAssembly(
            typeof(OrganizationDbContext).Assembly);

        // Configure cross-module relationships
        ConfigureCrossModuleRelationships(modelBuilder);
    }

    private static void ConfigureCrossModuleRelationships(ModelBuilder modelBuilder)
    {
        // Employee → Organization
        modelBuilder.Entity<Employee>()
            .HasOne<Organization>()
            .WithMany()
            .HasForeignKey(e => e.OrganizationId)
            .OnDelete(DeleteBehavior.Restrict);

        // Employee → Room (Location module)
        modelBuilder.Entity<Employee>()
            .HasOne<Room>()
            .WithMany()
            .HasForeignKey(e => e.LocationId)
            .OnDelete(DeleteBehavior.Restrict);
    }
}
```

## Migration Considerations

### Creating Migrations
```bash
# Add migration for specific DbContext
dotnet ef migrations add InitialCreate --context PickListDbContext --output-dir Migrations/PickLists

# Update database
dotnet ef database update --context PickListDbContext
```

### Schema Separation
Each module uses its own schema to avoid table name collisions:
- `picklists.PickLists`
- `people.Employees`
- `training.TrainingRecords`
- `org.Organizations`
