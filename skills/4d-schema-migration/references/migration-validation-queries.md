# 4D Migration Validation Queries

## Pre-Migration Validation

### Source Data Analysis

```sql
-- Analyze source table structures (run against 4D export)
-- Record counts per table
SELECT 'TableName' AS TableName, COUNT(*) AS RecordCount
FROM [4DExport].[dbo].[TableName]
UNION ALL
SELECT 'Table2' AS TableName, COUNT(*) AS RecordCount
FROM [4DExport].[dbo].[Table2]
-- Add all tables...
ORDER BY TableName;

-- Check for NULL values in critical fields
SELECT
    'Employees' AS TableName,
    'FirstName' AS FieldName,
    COUNT(*) AS NullCount
FROM [4DExport].[dbo].[Employees]
WHERE [FirstName] IS NULL OR [FirstName] = ''
UNION ALL
SELECT 'Employees', 'LastName', COUNT(*)
FROM [4DExport].[dbo].[Employees]
WHERE [LastName] IS NULL OR [LastName] = '';

-- Check for orphaned foreign keys
SELECT
    'OrderLines without Order' AS Issue,
    COUNT(*) AS Count
FROM [4DExport].[dbo].[OrderLines] ol
LEFT JOIN [4DExport].[dbo].[Orders] o ON ol.[OrderID] = o.[ID]
WHERE o.[ID] IS NULL;

-- Check for duplicate primary keys (if migrating legacy IDs)
SELECT [ID], COUNT(*) AS DuplicateCount
FROM [4DExport].[dbo].[Employees]
GROUP BY [ID]
HAVING COUNT(*) > 1;

-- Date range validation
SELECT
    'Employees' AS TableName,
    MIN([HireDate]) AS MinDate,
    MAX([HireDate]) AS MaxDate,
    COUNT(CASE WHEN [HireDate] < '1900-01-01' THEN 1 END) AS InvalidDates
FROM [4DExport].[dbo].[Employees];

-- Check for special characters that might cause issues
SELECT *
FROM [4DExport].[dbo].[Employees]
WHERE [FirstName] LIKE '%[' + CHAR(0) + '-' + CHAR(31) + ']%'  -- Control characters
   OR [FirstName] LIKE '%' + CHAR(0) + '%';  -- NULL bytes
```

### Data Quality Metrics

```sql
-- Generate data quality report
WITH FieldStats AS (
    SELECT
        'Employees' AS TableName,
        'FirstName' AS FieldName,
        COUNT(*) AS TotalRows,
        COUNT([FirstName]) AS NonNullCount,
        COUNT(DISTINCT [FirstName]) AS DistinctCount,
        SUM(CASE WHEN [FirstName] = '' THEN 1 ELSE 0 END) AS EmptyCount,
        MAX(LEN([FirstName])) AS MaxLength
    FROM [4DExport].[dbo].[Employees]
    -- Add more fields...
)
SELECT
    TableName,
    FieldName,
    TotalRows,
    NonNullCount,
    TotalRows - NonNullCount AS NullCount,
    CAST(NonNullCount * 100.0 / TotalRows AS DECIMAL(5,2)) AS CompletePct,
    DistinctCount,
    EmptyCount,
    MaxLength
FROM FieldStats
ORDER BY TableName, FieldName;
```

## Post-Migration Validation

### Row Count Comparison

```sql
-- Compare row counts between source and target
SELECT
    '4D Source' AS [Source],
    'Employees' AS TableName,
    COUNT(*) AS RecordCount
FROM [4DExport].[dbo].[Employees]
UNION ALL
SELECT
    '.NET Target',
    'Employees',
    COUNT(*)
FROM [NewDB].[dbo].[Employees]
ORDER BY TableName, [Source];
```

### Data Integrity Checks

```sql
-- Verify all records migrated (compare by legacy ID or natural key)
SELECT
    s.[ID] AS SourceID,
    t.[LegacyId] AS TargetLegacyId,
    CASE WHEN t.[Id] IS NULL THEN 'Missing in Target' ELSE 'OK' END AS Status
FROM [4DExport].[dbo].[Employees] s
LEFT JOIN [NewDB].[dbo].[Employees] t ON s.[ID] = t.[LegacyId]
WHERE t.[Id] IS NULL;

-- Verify no extra records in target
SELECT
    t.[Id] AS TargetId,
    t.[LegacyId],
    CASE WHEN s.[ID] IS NULL THEN 'Extra in Target' ELSE 'OK' END AS Status
FROM [NewDB].[dbo].[Employees] t
LEFT JOIN [4DExport].[dbo].[Employees] s ON t.[LegacyId] = s.[ID]
WHERE s.[ID] IS NULL AND t.[LegacyId] IS NOT NULL;
```

### Field-Level Validation

```sql
-- Compare specific fields (spot check)
SELECT TOP 100
    s.[ID] AS SourceID,
    s.[FirstName] AS SourceFirstName,
    t.[FirstName] AS TargetFirstName,
    CASE WHEN s.[FirstName] <> t.[FirstName] THEN 'MISMATCH' ELSE 'OK' END AS FirstNameStatus,
    s.[Salary] AS SourceSalary,
    t.[Salary] AS TargetSalary,
    CASE WHEN ABS(s.[Salary] - t.[Salary]) > 0.01 THEN 'MISMATCH' ELSE 'OK' END AS SalaryStatus
FROM [4DExport].[dbo].[Employees] s
JOIN [NewDB].[dbo].[Employees] t ON s.[ID] = t.[LegacyId]
WHERE s.[FirstName] <> t.[FirstName]
   OR ABS(s.[Salary] - t.[Salary]) > 0.01;
```

### Relationship Validation

```sql
-- Verify foreign key relationships preserved
SELECT
    'Orders → Customers' AS Relationship,
    COUNT(*) AS TotalOrders,
    SUM(CASE WHEN c.[Id] IS NULL THEN 1 ELSE 0 END) AS OrphanedOrders
FROM [NewDB].[dbo].[Orders] o
LEFT JOIN [NewDB].[dbo].[Customers] c ON o.[CustomerId] = c.[Id]
UNION ALL
SELECT
    'OrderLines → Orders',
    COUNT(*),
    SUM(CASE WHEN o.[Id] IS NULL THEN 1 ELSE 0 END)
FROM [NewDB].[dbo].[OrderLines] ol
LEFT JOIN [NewDB].[dbo].[Orders] o ON ol.[OrderId] = o.[Id];
```

### Aggregate Validation

```sql
-- Compare aggregated values
SELECT
    '4D Source' AS [Source],
    COUNT(*) AS OrderCount,
    SUM([TotalAmount]) AS TotalRevenue,
    AVG([TotalAmount]) AS AvgOrderValue
FROM [4DExport].[dbo].[Orders]
UNION ALL
SELECT
    '.NET Target',
    COUNT(*),
    SUM([TotalAmount]),
    AVG([TotalAmount])
FROM [NewDB].[dbo].[Orders];

-- Compare grouped aggregates
SELECT
    s.[Year],
    s.[Month],
    s.[OrderCount] AS SourceCount,
    t.[OrderCount] AS TargetCount,
    CASE WHEN s.[OrderCount] <> t.[OrderCount] THEN 'MISMATCH' ELSE 'OK' END AS Status
FROM (
    SELECT
        YEAR([OrderDate]) AS [Year],
        MONTH([OrderDate]) AS [Month],
        COUNT(*) AS OrderCount
    FROM [4DExport].[dbo].[Orders]
    GROUP BY YEAR([OrderDate]), MONTH([OrderDate])
) s
FULL OUTER JOIN (
    SELECT
        YEAR([OrderDate]) AS [Year],
        MONTH([OrderDate]) AS [Month],
        COUNT(*) AS OrderCount
    FROM [NewDB].[dbo].[Orders]
    GROUP BY YEAR([OrderDate]), MONTH([OrderDate])
) t ON s.[Year] = t.[Year] AND s.[Month] = t.[Month]
WHERE s.[OrderCount] <> t.[OrderCount]
   OR s.[OrderCount] IS NULL
   OR t.[OrderCount] IS NULL
ORDER BY [Year], [Month];
```

## Business Rules Validation

```sql
-- Validate business rules preserved after migration

-- Example: All active employees should have a department
SELECT
    'Active employees without department' AS Rule,
    COUNT(*) AS ViolationCount
FROM [NewDB].[dbo].[Employees]
WHERE [IsActive] = 1 AND [DepartmentId] IS NULL;

-- Example: Order totals should match sum of line items
SELECT
    o.[Id] AS OrderId,
    o.[TotalAmount] AS HeaderTotal,
    SUM(ol.[Quantity] * ol.[UnitPrice]) AS LineTotal,
    o.[TotalAmount] - SUM(ol.[Quantity] * ol.[UnitPrice]) AS Difference
FROM [NewDB].[dbo].[Orders] o
JOIN [NewDB].[dbo].[OrderLines] ol ON o.[Id] = ol.[OrderId]
GROUP BY o.[Id], o.[TotalAmount]
HAVING ABS(o.[TotalAmount] - SUM(ol.[Quantity] * ol.[UnitPrice])) > 0.01;

-- Example: No future hire dates
SELECT *
FROM [NewDB].[dbo].[Employees]
WHERE [HireDate] > CAST(GETDATE() AS DATE);
```

## Index Validation

```sql
-- Verify indexes exist on target tables
SELECT
    t.name AS TableName,
    i.name AS IndexName,
    i.type_desc AS IndexType,
    STRING_AGG(c.name, ', ') AS Columns
FROM sys.indexes i
JOIN sys.tables t ON i.object_id = t.object_id
JOIN sys.index_columns ic ON i.object_id = ic.object_id AND i.index_id = ic.index_id
JOIN sys.columns c ON ic.object_id = c.object_id AND ic.column_id = c.column_id
WHERE t.name IN ('Employees', 'Orders', 'OrderLines', 'Customers')  -- List your tables
  AND i.type > 0  -- Exclude heaps
GROUP BY t.name, i.name, i.type_desc
ORDER BY t.name, i.name;

-- Compare index performance (after migration)
SELECT TOP 20
    OBJECT_NAME(s.object_id) AS TableName,
    i.name AS IndexName,
    s.user_seeks,
    s.user_scans,
    s.user_lookups,
    s.user_updates
FROM sys.dm_db_index_usage_stats s
JOIN sys.indexes i ON s.object_id = i.object_id AND s.index_id = i.index_id
WHERE s.database_id = DB_ID()
ORDER BY s.user_seeks + s.user_scans + s.user_lookups DESC;
```

## Performance Baseline

```sql
-- Capture query performance baseline for key operations

-- List query (like 4D list form)
SET STATISTICS TIME ON;
SET STATISTICS IO ON;

SELECT TOP 100
    e.[Id],
    e.[FirstName],
    e.[LastName],
    d.[Name] AS DepartmentName,
    e.[HireDate]
FROM [NewDB].[dbo].[Employees] e
LEFT JOIN [NewDB].[dbo].[Departments] d ON e.[DepartmentId] = d.[Id]
ORDER BY e.[LastName], e.[FirstName];

SET STATISTICS TIME OFF;
SET STATISTICS IO OFF;

-- Search query
SET STATISTICS TIME ON;
SET STATISTICS IO ON;

SELECT *
FROM [NewDB].[dbo].[Employees]
WHERE [LastName] LIKE 'Smith%';

SET STATISTICS TIME OFF;
SET STATISTICS IO OFF;
```

## Migration Audit Trail

```sql
-- Create migration audit table
CREATE TABLE [dbo].[MigrationAudit] (
    [Id] INT IDENTITY(1,1) PRIMARY KEY,
    [TableName] NVARCHAR(128) NOT NULL,
    [SourceCount] INT NOT NULL,
    [TargetCount] INT NOT NULL,
    [MatchStatus] NVARCHAR(50) NOT NULL,
    [MigratedDate] DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    [Notes] NVARCHAR(MAX)
);

-- Insert audit records after each table migration
INSERT INTO [dbo].[MigrationAudit] ([TableName], [SourceCount], [TargetCount], [MatchStatus], [Notes])
SELECT
    'Employees',
    (SELECT COUNT(*) FROM [4DExport].[dbo].[Employees]),
    (SELECT COUNT(*) FROM [NewDB].[dbo].[Employees]),
    CASE
        WHEN (SELECT COUNT(*) FROM [4DExport].[dbo].[Employees]) =
             (SELECT COUNT(*) FROM [NewDB].[dbo].[Employees])
        THEN 'MATCH'
        ELSE 'MISMATCH'
    END,
    'Initial migration';

-- View audit summary
SELECT
    [TableName],
    [SourceCount],
    [TargetCount],
    [MatchStatus],
    [MigratedDate]
FROM [dbo].[MigrationAudit]
ORDER BY [MigratedDate] DESC;
```

## Rollback Validation

```sql
-- If rollback is needed, verify rollback completeness

-- Check target tables are empty (after rollback)
SELECT
    t.name AS TableName,
    p.rows AS RowCount
FROM sys.tables t
JOIN sys.partitions p ON t.object_id = p.object_id
WHERE p.index_id IN (0, 1)  -- Heap or clustered index
  AND t.name IN ('Employees', 'Orders', 'OrderLines', 'Customers')
ORDER BY t.name;

-- Verify source data still intact
SELECT
    'Employees' AS TableName,
    COUNT(*) AS RecordCount
FROM [4DExport].[dbo].[Employees]
UNION ALL
SELECT 'Orders', COUNT(*) FROM [4DExport].[dbo].[Orders];
```

## Continuous Validation (Post Go-Live)

```sql
-- Create stored procedure for ongoing validation
CREATE PROCEDURE [dbo].[ValidateMigration]
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @Issues TABLE (
        Issue NVARCHAR(200),
        Severity NVARCHAR(20),
        Details NVARCHAR(MAX)
    );

    -- Check for orphaned records
    INSERT INTO @Issues
    SELECT
        'Orphaned order lines',
        'ERROR',
        CAST(COUNT(*) AS NVARCHAR(20)) + ' order lines without parent order'
    FROM [dbo].[OrderLines] ol
    LEFT JOIN [dbo].[Orders] o ON ol.[OrderId] = o.[Id]
    WHERE o.[Id] IS NULL
    HAVING COUNT(*) > 0;

    -- Check for data anomalies
    INSERT INTO @Issues
    SELECT
        'Future hire dates',
        'WARNING',
        CAST(COUNT(*) AS NVARCHAR(20)) + ' employees with future hire dates'
    FROM [dbo].[Employees]
    WHERE [HireDate] > CAST(GETDATE() AS DATE)
    HAVING COUNT(*) > 0;

    -- Return results
    SELECT * FROM @Issues;

    IF EXISTS (SELECT 1 FROM @Issues WHERE Severity = 'ERROR')
        RETURN 1;  -- Indicate errors found

    RETURN 0;  -- Success
END;
```
