# 4D to SQL Server Type Mapping

## Core Data Types

| 4D Type | SQL Server Type | Notes |
|---------|-----------------|-------|
| Alpha | NVARCHAR(n) | Use NVARCHAR for Unicode support; n = field length |
| Text | NVARCHAR(MAX) | For unlimited text |
| Integer | INT | 32-bit signed integer |
| Long Integer | BIGINT | 64-bit signed integer |
| Integer 64 bit | BIGINT | Same as Long Integer |
| Real | FLOAT or DECIMAL(p,s) | Use DECIMAL for financial data |
| Float | FLOAT | 64-bit floating point |
| Date | DATE | SQL Server 2008+ native date |
| Time | TIME(7) | Precision to 100 nanoseconds |
| Boolean | BIT | 0 = false, 1 = true |
| Picture | VARBINARY(MAX) | Binary storage for images |
| Blob | VARBINARY(MAX) | Binary large object |
| Object | NVARCHAR(MAX) | Store as JSON |

## String Types

### Alpha Fields
```sql
-- 4D Alpha field with max length 50
-- Becomes:
[FieldName] NVARCHAR(50) NULL

-- If NOT NULL in 4D:
[FieldName] NVARCHAR(50) NOT NULL DEFAULT ''
```

### Text Fields
```sql
-- 4D Text field (unlimited)
-- Becomes:
[FieldName] NVARCHAR(MAX) NULL

-- Consider: If text is typically small but can be large
[FieldName] NVARCHAR(4000) NULL  -- Faster for short strings
```

## Numeric Types

### Integer Types
```sql
-- 4D Integer (16-bit in older versions)
[FieldName] SMALLINT NULL

-- 4D Longint (32-bit)
[FieldName] INT NULL

-- 4D Integer 64 bit
[FieldName] BIGINT NULL
```

### Real/Float Types
```sql
-- 4D Real for general calculations
[FieldName] FLOAT NULL

-- 4D Real for financial/precise calculations
[FieldName] DECIMAL(18, 4) NULL

-- Money fields (always use DECIMAL)
[Amount] DECIMAL(19, 4) NOT NULL DEFAULT 0
```

## Date and Time Types

### Date Only
```sql
-- 4D Date
[DateField] DATE NULL

-- With default to today
[DateField] DATE NOT NULL DEFAULT CAST(GETUTCDATE() AS DATE)
```

### Time Only
```sql
-- 4D Time (seconds from midnight)
[TimeField] TIME(0) NULL  -- Second precision

-- If 4D stores milliseconds
[TimeField] TIME(3) NULL  -- Millisecond precision
```

### Combined DateTime
```sql
-- 4D often stores date and time in separate fields
-- Combine in SQL Server:
[DateTimeField] DATETIME2(0) NULL

-- Or keep separate for backward compatibility:
[DatePart] DATE NULL
[TimePart] TIME(0) NULL

-- Computed column for combined:
[FullDateTime] AS (CAST([DatePart] AS DATETIME2) + CAST([TimePart] AS DATETIME2))
```

## Boolean Type

```sql
-- 4D Boolean
[IsActive] BIT NOT NULL DEFAULT 0

-- Note: 4D may use -1 for true in some versions
-- Migration script should handle: CASE WHEN [4DField] <> 0 THEN 1 ELSE 0 END
```

## Binary Types

### Picture Fields
```sql
-- 4D Picture
[ImageData] VARBINARY(MAX) NULL

-- Consider file storage instead for large images:
[ImagePath] NVARCHAR(500) NULL  -- Path to blob storage
```

### Blob Fields
```sql
-- 4D Blob
[BlobData] VARBINARY(MAX) NULL

-- With file type tracking:
[BlobData] VARBINARY(MAX) NULL,
[BlobMimeType] NVARCHAR(100) NULL,
[BlobFileName] NVARCHAR(255) NULL
```

## Object Type (4D v17+)

```sql
-- 4D Object (JSON-like)
[ObjectData] NVARCHAR(MAX) NULL

-- With JSON validation (SQL Server 2016+):
[ObjectData] NVARCHAR(MAX) NULL
    CONSTRAINT [CK_TableName_ObjectData_JSON] CHECK (ISJSON([ObjectData]) = 1)
```

## Special Considerations

### Auto-Increment / Sequences

```sql
-- 4D uses internal record numbers
-- SQL Server: Use IDENTITY

CREATE TABLE [dbo].[TableName] (
    [Id] INT IDENTITY(1,1) NOT NULL,
    -- ... other fields
    CONSTRAINT [PK_TableName] PRIMARY KEY CLUSTERED ([Id])
);

-- Or use SEQUENCE for more control:
CREATE SEQUENCE [dbo].[TableName_Seq] START WITH 1 INCREMENT BY 1;
```

### Null Handling

```sql
-- 4D may treat empty strings as null or vice versa
-- Standardize in SQL Server:

-- Migration: Convert empty to NULL
CASE WHEN LTRIM(RTRIM([Field])) = '' THEN NULL ELSE [Field] END

-- Or convert NULL to empty (if app expects it)
ISNULL([Field], '')
```

### Character Set

```sql
-- 4D may use various encodings
-- Always use NVARCHAR in SQL Server for Unicode

-- If source is ASCII-only, NVARCHAR still works
-- Slightly more storage but universal compatibility
```

## Index Types

| 4D Index Type | SQL Server Equivalent |
|---------------|----------------------|
| B-Tree | NONCLUSTERED INDEX |
| Cluster B-Tree | CLUSTERED INDEX |
| Automatic | NONCLUSTERED INDEX |
| Keywords | FULLTEXT INDEX |
| Composite | NONCLUSTERED INDEX (multiple columns) |
| Unique | UNIQUE INDEX |

```sql
-- Standard index
CREATE NONCLUSTERED INDEX [IX_Table_Field] ON [dbo].[Table]([Field]);

-- Unique index
CREATE UNIQUE NONCLUSTERED INDEX [UX_Table_Field] ON [dbo].[Table]([Field]);

-- Composite index
CREATE NONCLUSTERED INDEX [IX_Table_Field1_Field2]
    ON [dbo].[Table]([Field1], [Field2]);

-- Full-text (for Text fields with keyword search)
CREATE FULLTEXT INDEX ON [dbo].[Table]([TextField])
    KEY INDEX [PK_Table];
```

## Relation Types

| 4D Relation | SQL Server Implementation |
|-------------|---------------------------|
| Many-to-One | Foreign Key |
| One-to-Many | Foreign Key (reverse direction) |
| Many-to-Many | Junction table with two FKs |

```sql
-- Many-to-One (4D N->1)
ALTER TABLE [dbo].[ChildTable]
ADD CONSTRAINT [FK_Child_Parent]
    FOREIGN KEY ([ParentId]) REFERENCES [dbo].[ParentTable]([Id]);

-- Many-to-Many
CREATE TABLE [dbo].[Table1_Table2] (
    [Table1Id] INT NOT NULL,
    [Table2Id] INT NOT NULL,
    CONSTRAINT [PK_Table1_Table2] PRIMARY KEY ([Table1Id], [Table2Id]),
    CONSTRAINT [FK_T1T2_Table1] FOREIGN KEY ([Table1Id]) REFERENCES [dbo].[Table1]([Id]),
    CONSTRAINT [FK_T1T2_Table2] FOREIGN KEY ([Table2Id]) REFERENCES [dbo].[Table2]([Id])
);
```

## Complete Table Example

```sql
-- 4D Table: [Employees]
-- Fields: ID (Longint), FirstName (Alpha 50), LastName (Alpha 50),
--         HireDate (Date), Salary (Real), IsActive (Boolean), Photo (Picture)

CREATE TABLE [dbo].[Employees] (
    [Id] INT IDENTITY(1,1) NOT NULL,
    [FirstName] NVARCHAR(50) NOT NULL DEFAULT '',
    [LastName] NVARCHAR(50) NOT NULL DEFAULT '',
    [HireDate] DATE NULL,
    [Salary] DECIMAL(18, 2) NOT NULL DEFAULT 0,
    [IsActive] BIT NOT NULL DEFAULT 1,
    [Photo] VARBINARY(MAX) NULL,
    [CreatedDate] DATETIME2(0) NOT NULL DEFAULT GETUTCDATE(),
    [ModifiedDate] DATETIME2(0) NOT NULL DEFAULT GETUTCDATE(),
    CONSTRAINT [PK_Employees] PRIMARY KEY CLUSTERED ([Id])
);

CREATE NONCLUSTERED INDEX [IX_Employees_LastName]
    ON [dbo].[Employees]([LastName]);

CREATE NONCLUSTERED INDEX [IX_Employees_HireDate]
    ON [dbo].[Employees]([HireDate]);
```
