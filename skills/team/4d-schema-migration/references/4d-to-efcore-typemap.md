# 4D to EF Core / C# Type Mapping

## Core Data Types

| 4D Type | C# Type | EF Core Configuration |
|---------|---------|----------------------|
| Alpha | string | `.HasMaxLength(n)` |
| Text | string | `.HasMaxLength(int.MaxValue)` or default |
| Integer | int | Default mapping |
| Long Integer | long | Default mapping |
| Integer 64 bit | long | Default mapping |
| Real | double or decimal | `.HasPrecision(p, s)` for decimal |
| Float | double | Default mapping |
| Date | DateOnly (.NET 6+) | `.HasColumnType("date")` |
| Time | TimeOnly (.NET 6+) | `.HasColumnType("time")` |
| Boolean | bool | Default mapping |
| Picture | byte[] | `.HasColumnType("varbinary(max)")` |
| Blob | byte[] | `.HasColumnType("varbinary(max)")` |
| Object | string (JSON) | Use value converter or owned entity |

## Entity Template

```csharp
using System;
using System.Collections.Generic;

namespace MyApp.Domain.Entities;

public class EntityName
{
    public int Id { get; set; }

    // String properties
    public string FieldName { get; set; } = string.Empty;

    // Nullable string
    public string? OptionalField { get; set; }

    // Numeric properties
    public decimal Amount { get; set; }
    public int Count { get; set; }

    // Date/Time properties (.NET 6+)
    public DateOnly? DateField { get; set; }
    public TimeOnly? TimeField { get; set; }
    public DateTime? DateTimeField { get; set; }

    // Boolean
    public bool IsActive { get; set; }

    // Binary
    public byte[]? ImageData { get; set; }

    // Audit fields (add to all entities)
    public DateTime CreatedDate { get; set; }
    public DateTime ModifiedDate { get; set; }

    // Navigation properties
    public int? ParentId { get; set; }
    public virtual ParentEntity? Parent { get; set; }
    public virtual ICollection<ChildEntity> Children { get; set; } = new List<ChildEntity>();
}
```

## EF Core Configuration Template

```csharp
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;

namespace MyApp.Infrastructure.Data.Configurations;

public class EntityNameConfiguration : IEntityTypeConfiguration<EntityName>
{
    public void Configure(EntityTypeBuilder<EntityName> builder)
    {
        // Table
        builder.ToTable("EntityNames");

        // Primary Key
        builder.HasKey(e => e.Id);
        builder.Property(e => e.Id)
            .UseIdentityColumn();

        // String fields
        builder.Property(e => e.FieldName)
            .HasMaxLength(50)
            .IsRequired();

        builder.Property(e => e.OptionalField)
            .HasMaxLength(200);

        // Numeric fields
        builder.Property(e => e.Amount)
            .HasPrecision(18, 2);

        // Date fields
        builder.Property(e => e.DateField)
            .HasColumnType("date");

        builder.Property(e => e.TimeField)
            .HasColumnType("time(0)");

        // Binary fields
        builder.Property(e => e.ImageData)
            .HasColumnType("varbinary(max)");

        // Audit fields
        builder.Property(e => e.CreatedDate)
            .HasDefaultValueSql("GETUTCDATE()");

        builder.Property(e => e.ModifiedDate)
            .HasDefaultValueSql("GETUTCDATE()");

        // Relationships
        builder.HasOne(e => e.Parent)
            .WithMany(p => p.Children)
            .HasForeignKey(e => e.ParentId)
            .OnDelete(DeleteBehavior.Restrict);

        // Indexes
        builder.HasIndex(e => e.FieldName);
    }
}
```

## String Type Mappings

### Alpha Fields (Fixed Length)
```csharp
// Property
public string FirstName { get; set; } = string.Empty;

// Configuration
builder.Property(e => e.FirstName)
    .HasMaxLength(50)
    .IsRequired();
```

### Text Fields (Unlimited)
```csharp
// Property
public string? Description { get; set; }

// Configuration (no max length needed)
builder.Property(e => e.Description);
// Or explicitly:
builder.Property(e => e.Description)
    .HasColumnType("nvarchar(max)");
```

### Required vs Optional
```csharp
// Required (NOT NULL with default)
public string Name { get; set; } = string.Empty;

// Optional (NULL)
public string? Notes { get; set; }

// Configuration for required
builder.Property(e => e.Name)
    .IsRequired()
    .HasMaxLength(100);

// Optional is default, but be explicit
builder.Property(e => e.Notes)
    .IsRequired(false);
```

## Numeric Type Mappings

### Integer Types
```csharp
// 4D Integer (small)
public short SmallNumber { get; set; }

// 4D Longint (standard)
public int StandardNumber { get; set; }

// 4D Integer 64 bit
public long BigNumber { get; set; }
```

### Decimal/Real Types
```csharp
// Financial amounts - ALWAYS use decimal
public decimal Price { get; set; }
public decimal TaxRate { get; set; }

// Configuration
builder.Property(e => e.Price)
    .HasPrecision(19, 4);  // Money precision

builder.Property(e => e.TaxRate)
    .HasPrecision(5, 4);   // Percentage (0.0000 to 9.9999)
```

### Floating Point
```csharp
// Scientific/measurement values
public double Measurement { get; set; }
public float Ratio { get; set; }
```

## Date and Time Mappings

### DateOnly (.NET 6+)
```csharp
// 4D Date field
public DateOnly? BirthDate { get; set; }

// Configuration
builder.Property(e => e.BirthDate)
    .HasColumnType("date");
```

### TimeOnly (.NET 6+)
```csharp
// 4D Time field
public TimeOnly? StartTime { get; set; }

// Configuration
builder.Property(e => e.StartTime)
    .HasColumnType("time(0)");  // Second precision
```

### DateTime (Combined)
```csharp
// Combined date and time
public DateTime? AppointmentDateTime { get; set; }

// Configuration
builder.Property(e => e.AppointmentDateTime)
    .HasColumnType("datetime2(0)");  // Second precision
```

### Legacy DateTime Handling
```csharp
// If keeping separate date/time for compatibility
public DateOnly? AppointmentDate { get; set; }
public TimeOnly? AppointmentTime { get; set; }

// Computed property (not mapped)
[NotMapped]
public DateTime? AppointmentDateTime =>
    AppointmentDate.HasValue && AppointmentTime.HasValue
        ? AppointmentDate.Value.ToDateTime(AppointmentTime.Value)
        : null;
```

## Boolean Mapping

```csharp
// Property
public bool IsActive { get; set; }

// Configuration (with default)
builder.Property(e => e.IsActive)
    .HasDefaultValue(true);
```

## Binary/Blob Mappings

### Picture Fields
```csharp
// Property
public byte[]? Photo { get; set; }
public string? PhotoMimeType { get; set; }

// Configuration
builder.Property(e => e.Photo)
    .HasColumnType("varbinary(max)");

builder.Property(e => e.PhotoMimeType)
    .HasMaxLength(100);
```

### Generic Blob
```csharp
// Property
public byte[]? AttachmentData { get; set; }
public string? AttachmentFileName { get; set; }
public string? AttachmentMimeType { get; set; }

// Or use a value object
public class Attachment
{
    public byte[] Data { get; set; } = Array.Empty<byte>();
    public string FileName { get; set; } = string.Empty;
    public string MimeType { get; set; } = "application/octet-stream";
}
```

## Object/JSON Mappings

### Simple JSON Storage
```csharp
// Property (stored as JSON string)
public string? MetadataJson { get; set; }

// Configuration
builder.Property(e => e.MetadataJson)
    .HasColumnType("nvarchar(max)");
```

### Typed JSON with Value Converter
```csharp
// Strongly-typed property
public Dictionary<string, object>? Metadata { get; set; }

// Configuration with converter
builder.Property(e => e.Metadata)
    .HasConversion(
        v => JsonSerializer.Serialize(v, (JsonSerializerOptions?)null),
        v => JsonSerializer.Deserialize<Dictionary<string, object>>(v, (JsonSerializerOptions?)null)
    );
```

### Owned Entity (Recommended for structured data)
```csharp
// Owned type
public class Address
{
    public string Street { get; set; } = string.Empty;
    public string City { get; set; } = string.Empty;
    public string State { get; set; } = string.Empty;
    public string ZipCode { get; set; } = string.Empty;
}

// In entity
public Address? MailingAddress { get; set; }

// Configuration
builder.OwnsOne(e => e.MailingAddress, a =>
{
    a.Property(x => x.Street).HasMaxLength(200).HasColumnName("MailingStreet");
    a.Property(x => x.City).HasMaxLength(100).HasColumnName("MailingCity");
    a.Property(x => x.State).HasMaxLength(50).HasColumnName("MailingState");
    a.Property(x => x.ZipCode).HasMaxLength(20).HasColumnName("MailingZipCode");
});
```

## Relationship Mappings

### One-to-Many (4D N->1)
```csharp
// Parent entity
public class Department
{
    public int Id { get; set; }
    public string Name { get; set; } = string.Empty;
    public virtual ICollection<Employee> Employees { get; set; } = new List<Employee>();
}

// Child entity
public class Employee
{
    public int Id { get; set; }
    public string Name { get; set; } = string.Empty;
    public int DepartmentId { get; set; }
    public virtual Department Department { get; set; } = null!;
}

// Configuration
builder.HasOne(e => e.Department)
    .WithMany(d => d.Employees)
    .HasForeignKey(e => e.DepartmentId)
    .OnDelete(DeleteBehavior.Restrict);
```

### Many-to-Many
```csharp
// Entities
public class Project
{
    public int Id { get; set; }
    public virtual ICollection<Employee> Employees { get; set; } = new List<Employee>();
}

public class Employee
{
    public int Id { get; set; }
    public virtual ICollection<Project> Projects { get; set; } = new List<Project>();
}

// Configuration (EF Core 5+ implicit join)
builder.HasMany(e => e.Projects)
    .WithMany(p => p.Employees);
```

## Audit Fields Pattern

```csharp
// Base interface
public interface IAuditable
{
    DateTime CreatedDate { get; set; }
    DateTime ModifiedDate { get; set; }
    string? CreatedBy { get; set; }
    string? ModifiedBy { get; set; }
}

// Base entity
public abstract class AuditableEntity : IAuditable
{
    public DateTime CreatedDate { get; set; }
    public DateTime ModifiedDate { get; set; }
    public string? CreatedBy { get; set; }
    public string? ModifiedBy { get; set; }
}

// Your entity
public class Employee : AuditableEntity
{
    public int Id { get; set; }
    public string Name { get; set; } = string.Empty;
}

// SaveChanges interceptor
public override int SaveChanges()
{
    var entries = ChangeTracker.Entries<IAuditable>();
    foreach (var entry in entries)
    {
        if (entry.State == EntityState.Added)
        {
            entry.Entity.CreatedDate = DateTime.UtcNow;
            entry.Entity.CreatedBy = _currentUser.Id;
        }
        entry.Entity.ModifiedDate = DateTime.UtcNow;
        entry.Entity.ModifiedBy = _currentUser.Id;
    }
    return base.SaveChanges();
}
```

## Complete Entity Example

```csharp
// 4D Table: [Employees] converted to EF Core

// Entity
public class Employee
{
    public int Id { get; set; }
    public string FirstName { get; set; } = string.Empty;
    public string LastName { get; set; } = string.Empty;
    public string? MiddleName { get; set; }
    public DateOnly? HireDate { get; set; }
    public DateOnly? TerminationDate { get; set; }
    public decimal Salary { get; set; }
    public bool IsActive { get; set; }
    public byte[]? Photo { get; set; }
    public string? PhotoMimeType { get; set; }

    // Audit
    public DateTime CreatedDate { get; set; }
    public DateTime ModifiedDate { get; set; }

    // Relationships
    public int DepartmentId { get; set; }
    public virtual Department Department { get; set; } = null!;
    public virtual ICollection<EmployeeTraining> Trainings { get; set; } = new List<EmployeeTraining>();

    // Computed (not mapped)
    [NotMapped]
    public string FullName => $"{FirstName} {LastName}";
}

// Configuration
public class EmployeeConfiguration : IEntityTypeConfiguration<Employee>
{
    public void Configure(EntityTypeBuilder<Employee> builder)
    {
        builder.ToTable("Employees");

        builder.HasKey(e => e.Id);
        builder.Property(e => e.Id).UseIdentityColumn();

        builder.Property(e => e.FirstName).HasMaxLength(50).IsRequired();
        builder.Property(e => e.LastName).HasMaxLength(50).IsRequired();
        builder.Property(e => e.MiddleName).HasMaxLength(50);

        builder.Property(e => e.HireDate).HasColumnType("date");
        builder.Property(e => e.TerminationDate).HasColumnType("date");

        builder.Property(e => e.Salary).HasPrecision(18, 2);
        builder.Property(e => e.IsActive).HasDefaultValue(true);

        builder.Property(e => e.Photo).HasColumnType("varbinary(max)");
        builder.Property(e => e.PhotoMimeType).HasMaxLength(100);

        builder.Property(e => e.CreatedDate).HasDefaultValueSql("GETUTCDATE()");
        builder.Property(e => e.ModifiedDate).HasDefaultValueSql("GETUTCDATE()");

        builder.HasOne(e => e.Department)
            .WithMany(d => d.Employees)
            .HasForeignKey(e => e.DepartmentId)
            .OnDelete(DeleteBehavior.Restrict);

        builder.HasIndex(e => e.LastName);
        builder.HasIndex(e => new { e.LastName, e.FirstName });
        builder.HasIndex(e => e.DepartmentId);
    }
}
```
