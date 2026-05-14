# Common 4D Patterns and .NET Equivalents

## Record Numbers / Auto-Increment

### 4D Pattern
4D uses internal record numbers that may not be sequential and can be reused after deletion.

### .NET Equivalent
```csharp
// Entity with identity
public class Entity
{
    public int Id { get; set; }  // Auto-increment
}

// EF Core configuration
builder.Property(e => e.Id)
    .UseIdentityColumn();  // SQL Server IDENTITY
```

### SQL Server
```sql
-- If you need to preserve original 4D record numbers:
CREATE TABLE [dbo].[Entity] (
    [Id] INT IDENTITY(1,1) NOT NULL,
    [Legacy4DRecordNumber] INT NULL,  -- Preserve for reference
    -- other fields
);

CREATE INDEX [IX_Entity_Legacy4DRecordNumber]
    ON [dbo].[Entity]([Legacy4DRecordNumber]);
```

## Multi-Value Fields (Subtables)

### 4D Pattern
4D supports "subtables" or multi-value fields within a record.

### .NET Equivalent
```csharp
// Parent entity
public class Order
{
    public int Id { get; set; }
    public DateTime OrderDate { get; set; }

    // Child collection replaces 4D subtable
    public virtual ICollection<OrderLine> Lines { get; set; } = new List<OrderLine>();
}

// Child entity (was subtable in 4D)
public class OrderLine
{
    public int Id { get; set; }
    public int OrderId { get; set; }
    public int LineNumber { get; set; }  // Preserve ordering
    public string ProductCode { get; set; } = string.Empty;
    public int Quantity { get; set; }
    public decimal UnitPrice { get; set; }

    public virtual Order Order { get; set; } = null!;
}
```

### SQL Server
```sql
CREATE TABLE [dbo].[Orders] (
    [Id] INT IDENTITY(1,1) NOT NULL,
    [OrderDate] DATETIME2 NOT NULL,
    CONSTRAINT [PK_Orders] PRIMARY KEY ([Id])
);

CREATE TABLE [dbo].[OrderLines] (
    [Id] INT IDENTITY(1,1) NOT NULL,
    [OrderId] INT NOT NULL,
    [LineNumber] INT NOT NULL,
    [ProductCode] NVARCHAR(50) NOT NULL,
    [Quantity] INT NOT NULL,
    [UnitPrice] DECIMAL(18,4) NOT NULL,
    CONSTRAINT [PK_OrderLines] PRIMARY KEY ([Id]),
    CONSTRAINT [FK_OrderLines_Orders] FOREIGN KEY ([OrderId])
        REFERENCES [dbo].[Orders]([Id]) ON DELETE CASCADE,
    CONSTRAINT [UQ_OrderLines_Order_Line] UNIQUE ([OrderId], [LineNumber])
);
```

## Picture / Image Storage

### 4D Pattern
4D stores pictures directly in the database as binary data.

### Option 1: Keep in Database (Small Images)
```csharp
public class Employee
{
    public int Id { get; set; }
    public byte[]? Photo { get; set; }
    public string? PhotoMimeType { get; set; }
}

// Serve image
[HttpGet("{id}/photo")]
public async Task<IActionResult> GetPhoto(int id)
{
    var employee = await _db.Employees.FindAsync(id);
    if (employee?.Photo == null)
        return NotFound();

    return File(employee.Photo, employee.PhotoMimeType ?? "image/jpeg");
}
```

### Option 2: Azure Blob Storage (Recommended)
```csharp
public class Employee
{
    public int Id { get; set; }
    public string? PhotoBlobName { get; set; }  // Blob storage key
}

// Service for blob operations
public class BlobStorageService
{
    private readonly BlobContainerClient _container;

    public async Task<string> UploadPhotoAsync(byte[] data, string fileName)
    {
        var blobName = $"photos/{Guid.NewGuid()}/{fileName}";
        var blob = _container.GetBlobClient(blobName);
        await blob.UploadAsync(new BinaryData(data));
        return blobName;
    }

    public async Task<byte[]> DownloadPhotoAsync(string blobName)
    {
        var blob = _container.GetBlobClient(blobName);
        var response = await blob.DownloadContentAsync();
        return response.Value.Content.ToArray();
    }
}
```

## Date/Time Handling

### 4D Pattern
4D stores dates and times separately, with specific epoch handling.

### .NET Migration
```csharp
// Keep separate (backward compatible)
public class Event
{
    public DateOnly? EventDate { get; set; }
    public TimeOnly? EventTime { get; set; }

    // Computed property
    [NotMapped]
    public DateTime? EventDateTime =>
        EventDate.HasValue && EventTime.HasValue
            ? EventDate.Value.ToDateTime(EventTime.Value)
            : null;
}

// Or combine during migration
public class Event
{
    public DateTime? EventDateTime { get; set; }
}
```

### Migration Script
```sql
-- Combine separate date/time fields during migration
INSERT INTO [NewDB].[dbo].[Events] ([EventDateTime])
SELECT
    CASE
        WHEN [EventDate] IS NOT NULL AND [EventTime] IS NOT NULL
        THEN CAST([EventDate] AS DATETIME) + CAST([EventTime] AS DATETIME)
        WHEN [EventDate] IS NOT NULL
        THEN CAST([EventDate] AS DATETIME)
        ELSE NULL
    END
FROM [4DExport].[dbo].[Events]
```

## Null vs Empty String

### 4D Pattern
4D may treat empty strings and NULL differently, or inconsistently.

### .NET Standard
```csharp
// Standardize on nullable reference types
public class Customer
{
    // Required fields - use empty string default
    public string Name { get; set; } = string.Empty;

    // Optional fields - use nullable
    public string? Notes { get; set; }
}
```

### Migration Script
```sql
-- Standardize empty strings to NULL for optional fields
UPDATE [dbo].[Customers]
SET [Notes] = NULL
WHERE [Notes] = '' OR [Notes] = ' ';

-- Or standardize NULL to empty string for required fields
UPDATE [dbo].[Customers]
SET [Name] = ''
WHERE [Name] IS NULL;
```

## 4D Triggers → EF Core

### 4D Pattern
4D uses database triggers for validation and computed values.

### EF Core: SaveChanges Override
```csharp
public class AppDbContext : DbContext
{
    public override int SaveChanges()
    {
        ApplyAuditFields();
        ApplyBusinessRules();
        return base.SaveChanges();
    }

    public override async Task<int> SaveChangesAsync(CancellationToken cancellationToken = default)
    {
        ApplyAuditFields();
        ApplyBusinessRules();
        return await base.SaveChangesAsync(cancellationToken);
    }

    private void ApplyAuditFields()
    {
        var entries = ChangeTracker.Entries()
            .Where(e => e.State == EntityState.Added || e.State == EntityState.Modified);

        foreach (var entry in entries)
        {
            if (entry.Entity is IAuditable auditable)
            {
                auditable.ModifiedDate = DateTime.UtcNow;
                if (entry.State == EntityState.Added)
                {
                    auditable.CreatedDate = DateTime.UtcNow;
                }
            }
        }
    }

    private void ApplyBusinessRules()
    {
        // 4D trigger logic converted to C#
        foreach (var entry in ChangeTracker.Entries<Order>())
        {
            if (entry.State == EntityState.Added || entry.State == EntityState.Modified)
            {
                // Recompute total from lines
                entry.Entity.TotalAmount = entry.Entity.Lines.Sum(l => l.Quantity * l.UnitPrice);
            }
        }
    }
}
```

### EF Core: Interceptors (More Flexible)
```csharp
public class AuditInterceptor : SaveChangesInterceptor
{
    public override InterceptionResult<int> SavingChanges(
        DbContextEventData eventData,
        InterceptionResult<int> result)
    {
        ApplyAuditFields(eventData.Context);
        return base.SavingChanges(eventData, result);
    }

    public override ValueTask<InterceptionResult<int>> SavingChangesAsync(
        DbContextEventData eventData,
        InterceptionResult<int> result,
        CancellationToken cancellationToken = default)
    {
        ApplyAuditFields(eventData.Context);
        return base.SavingChangesAsync(eventData, result, cancellationToken);
    }

    private void ApplyAuditFields(DbContext? context)
    {
        if (context == null) return;
        // ... audit logic
    }
}

// Registration
services.AddDbContext<AppDbContext>(options =>
    options.UseSqlServer(connectionString)
           .AddInterceptors(new AuditInterceptor()));
```

## 4D Methods → .NET Services

### 4D Pattern
4D "methods" are procedures attached to tables or forms.

### Mapping Strategy

| 4D Method Type | .NET Equivalent |
|----------------|-----------------|
| Table trigger | EF Core interceptor / SaveChanges override |
| Form method | Blazor component code-behind |
| Project method (business logic) | CQRS Handler or Domain Service |
| Project method (utility) | Static helper or extension method |
| Form validation | FluentValidation validator |

### Example: Business Logic Method
```csharp
// 4D: Method "CalculateOrderDiscount" on Orders table
// .NET: Command handler

public record CalculateOrderDiscountCommand(int OrderId) : IRequest<decimal>;

public class CalculateOrderDiscountHandler : IRequestHandler<CalculateOrderDiscountCommand, decimal>
{
    private readonly AppDbContext _db;

    public CalculateOrderDiscountHandler(AppDbContext db)
    {
        _db = db;
    }

    public async Task<decimal> Handle(CalculateOrderDiscountCommand request, CancellationToken cancellationToken)
    {
        var order = await _db.Orders
            .Include(o => o.Lines)
            .Include(o => o.Customer)
            .FirstOrDefaultAsync(o => o.Id == request.OrderId, cancellationToken);

        if (order == null)
            return 0;

        // Business logic from 4D method
        var subtotal = order.Lines.Sum(l => l.Quantity * l.UnitPrice);

        // Volume discount
        if (subtotal > 1000)
            return subtotal * 0.10m;
        if (subtotal > 500)
            return subtotal * 0.05m;

        // Customer loyalty discount
        if (order.Customer.IsPreferred)
            return subtotal * 0.02m;

        return 0;
    }
}
```

## Character Set / Encoding

### 4D Pattern
4D may use MacRoman, Windows-1252, or other legacy encodings.

### Migration Script
```sql
-- SQL Server uses UTF-16 for NVARCHAR
-- Ensure proper encoding during import

-- If importing from CSV, specify encoding:
BULK INSERT [dbo].[Table]
FROM 'C:\data\export.csv'
WITH (
    CODEPAGE = '1252',  -- or 'ACP' for ANSI, '65001' for UTF-8
    FIELDTERMINATOR = ',',
    ROWTERMINATOR = '\n'
);

-- Check for encoding issues after import
SELECT * FROM [dbo].[Table]
WHERE [TextField] LIKE '%�%'  -- Replacement character
   OR [TextField] LIKE '%?%' COLLATE Latin1_General_BIN;  -- Unknown chars
```

### C# Data Import
```csharp
// Read with specific encoding
using var reader = new StreamReader("export.csv", Encoding.GetEncoding(1252));

// Or detect encoding
using var reader = new StreamReader("export.csv", detectEncodingFromByteOrderMarks: true);
```

## Sequence / Counter Tables

### 4D Pattern
4D may use manual sequence tables for specific numbering.

### SQL Server Sequence
```sql
-- Create sequence
CREATE SEQUENCE [dbo].[InvoiceNumberSeq]
    START WITH 10001
    INCREMENT BY 1;

-- Use in insert
INSERT INTO [dbo].[Invoices] ([InvoiceNumber], ...)
VALUES (NEXT VALUE FOR [dbo].[InvoiceNumberSeq], ...);

-- Or in computed column
ALTER TABLE [dbo].[Invoices]
ADD [InvoiceNumber] AS (CONCAT('INV-', FORMAT(NEXT VALUE FOR [dbo].[InvoiceNumberSeq], '000000')));
```

### EF Core
```csharp
// In DbContext
modelBuilder.HasSequence<int>("InvoiceNumberSeq")
    .StartsAt(10001)
    .IncrementsBy(1);

// In entity configuration
builder.Property(e => e.InvoiceNumber)
    .HasDefaultValueSql("NEXT VALUE FOR InvoiceNumberSeq");
```

## Hierarchical / Self-Referential Data

### 4D Pattern
4D may use parent pointer or path-based hierarchy.

### EF Core: Adjacency List
```csharp
public class Category
{
    public int Id { get; set; }
    public string Name { get; set; } = string.Empty;
    public int? ParentId { get; set; }

    public virtual Category? Parent { get; set; }
    public virtual ICollection<Category> Children { get; set; } = new List<Category>();
}
```

### SQL Server: Hierarchyid (Better Performance)
```sql
CREATE TABLE [dbo].[Categories] (
    [Id] INT IDENTITY(1,1) NOT NULL,
    [Name] NVARCHAR(100) NOT NULL,
    [HierarchyPath] HIERARCHYID NOT NULL,
    [Level] AS [HierarchyPath].GetLevel(),
    CONSTRAINT [PK_Categories] PRIMARY KEY ([Id])
);

CREATE INDEX [IX_Categories_HierarchyPath] ON [dbo].[Categories]([HierarchyPath]);

-- Query all descendants
SELECT * FROM [dbo].[Categories]
WHERE [HierarchyPath].IsDescendantOf(@parentPath) = 1;
```

## Calculated Fields

### 4D Pattern
4D supports calculated fields that compute on read.

### Option 1: Computed Column (SQL Server)
```sql
-- Computed column
ALTER TABLE [dbo].[OrderLines]
ADD [LineTotal] AS ([Quantity] * [UnitPrice]);

-- Persisted computed column (stored, for indexing)
ALTER TABLE [dbo].[OrderLines]
ADD [LineTotal] AS ([Quantity] * [UnitPrice]) PERSISTED;
```

### Option 2: Entity Property (C#)
```csharp
public class OrderLine
{
    public int Quantity { get; set; }
    public decimal UnitPrice { get; set; }

    // Not mapped - computed in C#
    [NotMapped]
    public decimal LineTotal => Quantity * UnitPrice;
}
```

### Option 3: Database View
```sql
CREATE VIEW [dbo].[vw_OrderLinesWithTotals]
AS
SELECT
    ol.*,
    ol.[Quantity] * ol.[UnitPrice] AS [LineTotal],
    o.[OrderDate],
    c.[CustomerName]
FROM [dbo].[OrderLines] ol
JOIN [dbo].[Orders] o ON ol.[OrderId] = o.[Id]
JOIN [dbo].[Customers] c ON o.[CustomerId] = c.[Id];
```
