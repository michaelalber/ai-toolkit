# Shared Entity Patterns

## Core Interfaces

### IAuditable Interface
```csharp
// DenaliDataSystems.Core.Abstractions/Contracts/IAuditable.cs
namespace DenaliDataSystems.Core.Abstractions.Contracts;

/// <summary>
/// Interface for entities that track creation and modification metadata.
/// </summary>
public interface IAuditable
{
    /// <summary>
    /// Date and time the entity was created (UTC).
    /// </summary>
    DateTime CreatedAt { get; set; }

    /// <summary>
    /// User who created the entity.
    /// </summary>
    string CreatedBy { get; set; }

    /// <summary>
    /// Date and time the entity was last modified (UTC).
    /// </summary>
    DateTime? ModifiedAt { get; set; }

    /// <summary>
    /// User who last modified the entity.
    /// </summary>
    string? ModifiedBy { get; set; }
}
```

### ISoftDeletable Interface
```csharp
// DenaliDataSystems.Core.Abstractions/Contracts/ISoftDeletable.cs
namespace DenaliDataSystems.Core.Abstractions.Contracts;

/// <summary>
/// Interface for entities that support soft delete.
/// </summary>
public interface ISoftDeletable
{
    /// <summary>
    /// Whether the entity has been soft deleted.
    /// </summary>
    bool IsDeleted { get; set; }

    /// <summary>
    /// Date and time the entity was deleted (UTC).
    /// </summary>
    DateTime? DeletedAt { get; set; }

    /// <summary>
    /// User who deleted the entity.
    /// </summary>
    string? DeletedBy { get; set; }
}
```

## AuditedEntity Attribute

```csharp
// DenaliDataSystems.Core.Abstractions/Attributes/AuditedEntityAttribute.cs
namespace DenaliDataSystems.Core.Abstractions.Attributes;

/// <summary>
/// Marks an entity for automatic history tracking.
/// When applied, changes to the entity are logged to a corresponding _History table.
/// </summary>
/// <example>
/// [AuditedEntity]
/// public class PickList : IAuditable, ISoftDeletable
/// {
///     // Entity properties...
/// }
/// </example>
[AttributeUsage(AttributeTargets.Class, Inherited = false)]
public sealed class AuditedEntityAttribute : Attribute
{
    /// <summary>
    /// Custom history table name. If not specified, uses {TableName}_History.
    /// </summary>
    public string? HistoryTableName { get; set; }

    /// <summary>
    /// Whether to track property-level changes. Default: true.
    /// </summary>
    public bool TrackPropertyChanges { get; set; } = true;
}
```

## Entity Implementation Patterns

### Standard Entity with All Interfaces
```csharp
using System.ComponentModel.DataAnnotations;
using DenaliDataSystems.Core.Abstractions.Attributes;
using DenaliDataSystems.Core.Abstractions.Contracts;

namespace DenaliDataSystems.PickLists.Features.PickListFeature.Entities.Models;

/// <summary>
/// A configurable lookup list for dropdown values.
/// </summary>
[AuditedEntity]
public class PickList : IAuditable, ISoftDeletable
{
    public int Id { get; set; }

    /// <summary>
    /// Display name of the pick list.
    /// </summary>
    [Required]
    [StringLength(30)]
    public string Name { get; set; } = string.Empty;

    /// <summary>
    /// Unique key for programmatic access.
    /// </summary>
    [Required]
    [StringLength(30)]
    public string Key { get; set; } = string.Empty;

    /// <summary>
    /// Optional description for administrators.
    /// </summary>
    [StringLength(255)]
    public string? Description { get; set; }

    /// <summary>
    /// Whether the pick list is active and available for use.
    /// </summary>
    public bool IsActive { get; set; } = true;

    // IAuditable implementation
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    public string CreatedBy { get; set; } = "System";
    public DateTime? ModifiedAt { get; set; }
    public string? ModifiedBy { get; set; }

    // ISoftDeletable implementation
    public bool IsDeleted { get; set; }
    public DateTime? DeletedAt { get; set; }
    public string? DeletedBy { get; set; }

    // Navigation properties
    public virtual ICollection<PickListItem> Items { get; set; } = new List<PickListItem>();
}
```

### Entity with Relationships
```csharp
using System.ComponentModel.DataAnnotations;
using DenaliDataSystems.Core.Abstractions.Attributes;
using DenaliDataSystems.Core.Abstractions.Contracts;

namespace DenaliDataSystems.PickLists.Features.PickListFeature.Entities.Models;

/// <summary>
/// An individual item within a pick list.
/// </summary>
[AuditedEntity]
public class PickListItem : IAuditable, ISoftDeletable
{
    public int Id { get; set; }

    /// <summary>
    /// Foreign key to parent PickList.
    /// </summary>
    public int PickListId { get; set; }

    /// <summary>
    /// Display text for the item.
    /// </summary>
    [Required]
    [StringLength(100)]
    public string Text { get; set; } = string.Empty;

    /// <summary>
    /// Value stored when item is selected.
    /// </summary>
    [Required]
    [StringLength(100)]
    public string Value { get; set; } = string.Empty;

    /// <summary>
    /// Display order within the list.
    /// </summary>
    public int SortOrder { get; set; }

    /// <summary>
    /// Whether this item is the default selection.
    /// </summary>
    public bool IsDefault { get; set; }

    /// <summary>
    /// Whether the item is active and available for selection.
    /// </summary>
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

    // Navigation
    public virtual PickList PickList { get; set; } = null!;
}
```

## People Module Entities

### Person Entity
```csharp
using System.ComponentModel.DataAnnotations;
using DenaliDataSystems.Core.Abstractions.Attributes;
using DenaliDataSystems.Core.Abstractions.Contracts;

namespace DenaliDataSystems.People.Features.PersonFeature.Entities.Models;

[AuditedEntity]
public class Person : IAuditable, ISoftDeletable
{
    public int Id { get; set; }

    [Required]
    [StringLength(100)]
    public string FirstName { get; set; } = string.Empty;

    [Required]
    [StringLength(100)]
    public string LastName { get; set; } = string.Empty;

    [StringLength(100)]
    public string? MiddleName { get; set; }

    [StringLength(20)]
    public string? Suffix { get; set; }

    [StringLength(100)]
    public string? PreferredName { get; set; }

    [Required]
    [StringLength(255)]
    public string Email { get; set; } = string.Empty;

    [StringLength(50)]
    public string? WorkPhone { get; set; }

    [StringLength(50)]
    public string? MobilePhone { get; set; }

    // Computed properties (not persisted)
    public string FullName => string.IsNullOrEmpty(MiddleName)
        ? $"{FirstName} {LastName}"
        : $"{FirstName} {MiddleName} {LastName}";

    public string DisplayName => PreferredName ?? FirstName;

    public string FormalName => $"{LastName}, {FirstName}";

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

### Employee Entity (Extends Person)
```csharp
using System.ComponentModel.DataAnnotations;
using DenaliDataSystems.Core.Abstractions.Attributes;

namespace DenaliDataSystems.People.Features.PersonFeature.Entities.Models;

[AuditedEntity]
public class Employee : Person
{
    [Required]
    [StringLength(50)]
    public string EmployeeNumber { get; set; } = string.Empty;

    [StringLength(20)]
    public string? ZNumber { get; set; }

    [StringLength(50)]
    public string? BadgeNumber { get; set; }

    public DateOnly? HireDate { get; set; }

    public DateOnly? TerminationDate { get; set; }

    public EmployeeStatus Status { get; set; } = EmployeeStatus.Active;

    public EmploymentType EmploymentType { get; set; } = EmploymentType.FullTime;

    // Organization reference (FK only, not navigation - cross-module)
    public int? OrganizationId { get; set; }

    // Location reference (FK only - cross-module)
    public int? LocationId { get; set; }

    // Self-reference for supervisor (same module, navigation OK)
    public int? SupervisorId { get; set; }

    [StringLength(200)]
    public string? JobTitle { get; set; }

    [StringLength(50)]
    public string? JobCode { get; set; }

    // Navigation within module
    public virtual Employee? Supervisor { get; set; }
    public virtual ICollection<Employee> DirectReports { get; set; } = new List<Employee>();

    // Computed
    public bool IsActive => Status == EmployeeStatus.Active;
}

public enum EmployeeStatus
{
    Active = 1,
    OnLeave = 2,
    Terminated = 3,
    Retired = 4
}

public enum EmploymentType
{
    FullTime = 1,
    PartTime = 2,
    Contractor = 3,
    Intern = 4,
    Temporary = 5
}
```

## Training Module Entities

```csharp
using System.ComponentModel.DataAnnotations;
using DenaliDataSystems.Core.Abstractions.Attributes;
using DenaliDataSystems.Core.Abstractions.Contracts;

namespace DenaliDataSystems.Training.Features.TrainingFeature.Entities.Models;

[AuditedEntity]
public class TrainingCourse : IAuditable, ISoftDeletable
{
    public int Id { get; set; }

    [Required]
    [StringLength(50)]
    public string Code { get; set; } = string.Empty;

    [Required]
    [StringLength(200)]
    public string Title { get; set; } = string.Empty;

    [StringLength(2000)]
    public string? Description { get; set; }

    public int? DurationMinutes { get; set; }

    public TrainingType Type { get; set; }

    public bool IsRequired { get; set; }

    /// <summary>
    /// Months until certification expires. Null = never expires.
    /// </summary>
    public int? ValidityMonths { get; set; }

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

    // Navigation
    public virtual ICollection<TrainingRecord> Records { get; set; } = new List<TrainingRecord>();
}

[AuditedEntity]
public class TrainingRecord : IAuditable, ISoftDeletable
{
    public int Id { get; set; }

    /// <summary>
    /// Reference to Employee (cross-module FK, no navigation).
    /// </summary>
    public int EmployeeId { get; set; }

    public int TrainingCourseId { get; set; }

    public DateOnly CompletedDate { get; set; }

    public DateOnly? ExpirationDate { get; set; }

    public TrainingStatus Status { get; set; }

    public decimal? Score { get; set; }

    [StringLength(100)]
    public string? CertificateNumber { get; set; }

    [StringLength(500)]
    public string? Notes { get; set; }

    // IAuditable
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    public string CreatedBy { get; set; } = "System";
    public DateTime? ModifiedAt { get; set; }
    public string? ModifiedBy { get; set; }

    // ISoftDeletable
    public bool IsDeleted { get; set; }
    public DateTime? DeletedAt { get; set; }
    public string? DeletedBy { get; set; }

    // Navigation (within module only)
    public virtual TrainingCourse TrainingCourse { get; set; } = null!;

    // Computed
    public bool IsExpired => ExpirationDate.HasValue &&
        ExpirationDate.Value < DateOnly.FromDateTime(DateTime.Today);

    public bool IsExpiringSoon(int daysWarning = 30) =>
        ExpirationDate.HasValue &&
        ExpirationDate.Value <= DateOnly.FromDateTime(DateTime.Today.AddDays(daysWarning));
}

public enum TrainingType
{
    Online = 1,
    InPerson = 2,
    SelfStudy = 3,
    OnTheJob = 4
}

public enum TrainingStatus
{
    NotStarted = 0,
    InProgress = 1,
    Completed = 2,
    Failed = 3,
    Expired = 4
}
```

## Cross-Module Reference Pattern

When entities from different modules need to reference each other, use **foreign key IDs only** (no navigation properties) to maintain loose coupling:

```csharp
// Employee (People module) references Organization and Location by ID only
public class Employee : Person
{
    // Cross-module references - IDs only
    public int? OrganizationId { get; set; }  // From DenaliDataSystems.Organization
    public int? LocationId { get; set; }       // From DenaliDataSystems.Location

    // Within-module references - navigation OK
    public int? SupervisorId { get; set; }
    public virtual Employee? Supervisor { get; set; }
}
```

The consuming application's DbContext configures cross-module relationships:

```csharp
// In consuming app's AppDbContext.OnModelCreating
modelBuilder.Entity<Employee>()
    .HasOne<Organization>()
    .WithMany()
    .HasForeignKey(e => e.OrganizationId)
    .OnDelete(DeleteBehavior.Restrict);

modelBuilder.Entity<Employee>()
    .HasOne<Room>()
    .WithMany()
    .HasForeignKey(e => e.LocationId)
    .OnDelete(DeleteBehavior.Restrict);
```

## Data Annotations vs Fluent API

**Use Data Annotations for:**
- Simple validations ([Required], [StringLength], [Range])
- Display metadata that travels with the model

**Use Fluent API for:**
- Table/schema mapping
- Index definitions
- Relationship configuration
- Query filters
- Value conversions

```csharp
// Entity uses data annotations for validation
public class PickList : IAuditable, ISoftDeletable
{
    [Required]
    [StringLength(30)]
    public string Name { get; set; } = string.Empty;
}

// Configuration uses Fluent API for database mapping
public class PickListConfiguration : IEntityTypeConfiguration<PickList>
{
    public void Configure(EntityTypeBuilder<PickList> builder)
    {
        builder.ToTable("PickLists", "picklists");
        builder.HasIndex(e => e.Key).IsUnique().HasFilter("[IsDeleted] = 0");
    }
}
```
