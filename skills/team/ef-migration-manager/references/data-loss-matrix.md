# Data Loss Risk Matrix for EF Core Migrations

> Reference guide for detecting, categorizing, and mitigating data loss risks in Entity Framework Core migrations.

## Risk Categories

### None -- No Data Loss Risk

The migration only adds new structures or modifies metadata. No existing data is affected.

**Examples:**
- Adding a new table
- Adding a nullable column
- Creating an index
- Adding a foreign key constraint (when all rows satisfy it)

### Low -- Minimal Risk, Reversible

The migration makes changes that could theoretically affect data but are unlikely to cause loss in practice.

**Examples:**
- Adding a NOT NULL column with a default value
- Widening a column type (`nvarchar(50)` to `nvarchar(100)`, `int` to `bigint`)
- Renaming a column (data preserved, but application code must update)
- Adding a unique constraint (when no duplicates exist)

### High -- Significant Risk, Data May Be Lost

The migration alters data structure in ways that could truncate, transform, or lose data without explicit preservation steps.

**Examples:**
- Narrowing a column type (`nvarchar(200)` to `nvarchar(50)`)
- Changing column type with potential cast failures (`string` to `int`)
- Adding NOT NULL constraint without default (existing NULLs will cause failure)
- Splitting a table (data must be copied to new structure)

### Critical -- Data Will Be Lost Without Intervention

The migration removes data structures entirely. Without explicit data migration, data is permanently deleted.

**Examples:**
- Dropping a column
- Dropping a table
- Dropping a database
- Removing rows via SQL in migration

## Common Operations Matrix

| Operation | EF Core Method | Risk Level | SQL Generated | Mitigation Required |
|-----------|---------------|------------|---------------|-------------------|
| Add table | `migrationBuilder.CreateTable()` | None | `CREATE TABLE` | None |
| Drop table | `migrationBuilder.DropTable()` | Critical | `DROP TABLE` | Backup/data migration |
| Add nullable column | `migrationBuilder.AddColumn()` (nullable) | None | `ALTER TABLE ADD` | None |
| Add non-null column (with default) | `migrationBuilder.AddColumn()` (default) | Low | `ALTER TABLE ADD ... DEFAULT` | Verify default value |
| Add non-null column (no default) | `migrationBuilder.AddColumn()` | High | `ALTER TABLE ADD` | Will fail on existing rows |
| Drop column | `migrationBuilder.DropColumn()` | Critical | `ALTER TABLE DROP COLUMN` | Copy data first |
| Rename column | `migrationBuilder.RenameColumn()` | Low | `sp_rename` / `ALTER TABLE RENAME` | Update application code |
| Rename table | `migrationBuilder.RenameTable()` | Low | `sp_rename` / `ALTER TABLE RENAME` | Update application code |
| Widen column type | `migrationBuilder.AlterColumn()` | Low | `ALTER TABLE ALTER COLUMN` | Generally safe |
| Narrow column type | `migrationBuilder.AlterColumn()` | High | `ALTER TABLE ALTER COLUMN` | Verify data fits |
| Change column type | `migrationBuilder.AlterColumn()` | High | `ALTER TABLE ALTER COLUMN` | Verify cast compatibility |
| Add index | `migrationBuilder.CreateIndex()` | None | `CREATE INDEX` | None |
| Drop index | `migrationBuilder.DropIndex()` | None | `DROP INDEX` | Performance impact only |
| Add unique constraint | `migrationBuilder.AddUniqueConstraint()` | Low | `ALTER TABLE ADD CONSTRAINT` | Check for duplicates |
| Add foreign key | `migrationBuilder.AddForeignKey()` | Low | `ALTER TABLE ADD CONSTRAINT` | Check referential integrity |
| Drop foreign key | `migrationBuilder.DropForeignKey()` | None | `ALTER TABLE DROP CONSTRAINT` | None (data preserved) |
| Make column nullable | `migrationBuilder.AlterColumn()` | None | `ALTER TABLE ALTER COLUMN` | Safe operation |
| Make column non-nullable | `migrationBuilder.AlterColumn()` | High | `ALTER TABLE ALTER COLUMN` | Existing NULLs will fail |
| Change default value | `migrationBuilder.AlterColumn()` | None | `ALTER TABLE ALTER COLUMN` | Only affects new rows |
| Raw SQL data manipulation | `migrationBuilder.Sql()` | Varies | Custom SQL | Review carefully |

## Detection Patterns in Generated SQL

### Critical Data Loss Indicators

Look for these patterns in the SQL output from `dotnet ef migrations script`:

```sql
-- CRITICAL: Column drop
ALTER TABLE [Users] DROP COLUMN [LegacyId];

-- CRITICAL: Table drop
DROP TABLE [ObsoleteRecords];

-- CRITICAL: Truncation in type change
ALTER TABLE [Products] ALTER COLUMN [Description] nvarchar(50) NOT NULL;
-- (was nvarchar(MAX) -- data WILL be truncated)

-- CRITICAL: Delete data via raw SQL
DELETE FROM [TempData] WHERE [CreatedDate] < '2024-01-01';
```

### High Risk Indicators

```sql
-- HIGH: Type change with potential cast failure
ALTER TABLE [Orders] ALTER COLUMN [Status] int NOT NULL;
-- (was nvarchar(50) -- cast may fail for non-numeric values)

-- HIGH: Adding NOT NULL without default on existing table
ALTER TABLE [Customers] ADD [RequiredField] nvarchar(100) NOT NULL;
-- (will fail if table has existing rows)

-- HIGH: Narrowing string column
ALTER TABLE [Logs] ALTER COLUMN [Message] nvarchar(200) NOT NULL;
-- (was nvarchar(500) -- values longer than 200 will be truncated)
```

### Low Risk Indicators

```sql
-- LOW: Column rename (data preserved)
EXEC sp_rename N'[Users].[UserName]', N'Username', N'COLUMN';

-- LOW: Widening column type (safe expansion)
ALTER TABLE [Products] ALTER COLUMN [Price] decimal(18,4) NOT NULL;
-- (was decimal(18,2) -- no data loss, just more precision)

-- LOW: Adding nullable column (no effect on existing rows)
ALTER TABLE [Orders] ADD [Notes] nvarchar(max) NULL;
```

### No Risk Indicators

```sql
-- NONE: New table
CREATE TABLE [AuditLogs] (
    [Id] int NOT NULL IDENTITY,
    [Action] nvarchar(100) NOT NULL,
    CONSTRAINT [PK_AuditLogs] PRIMARY KEY ([Id])
);

-- NONE: New index
CREATE INDEX [IX_Users_Email] ON [Users] ([Email]);

-- NONE: New foreign key (assuming data integrity holds)
ALTER TABLE [Orders] ADD CONSTRAINT [FK_Orders_Customers]
    FOREIGN KEY ([CustomerId]) REFERENCES [Customers] ([Id]);
```

## Mitigation Strategies

### Risk Level: None

No action required. Proceed with standard migration workflow.

### Risk Level: Low

1. Review the generated SQL to confirm the assessment
2. Test on development database with representative data
3. Verify application behavior after migration
4. Proceed with confidence

### Risk Level: High

1. Generate and carefully review the SQL script
2. Test on a copy of production data (not just development data)
3. Write explicit data preservation steps if needed
4. Consider splitting into multiple migrations
5. Ensure `Down()` method is verified

**Example: Safe NOT NULL Addition**

```csharp
protected override void Up(MigrationBuilder migrationBuilder)
{
    // Step 1: Add as nullable first
    migrationBuilder.AddColumn<string>(
        name: "Email",
        table: "Users",
        type: "nvarchar(256)",
        nullable: true);

    // Step 2: Populate existing rows with a sensible default
    migrationBuilder.Sql(
        "UPDATE [Users] SET [Email] = [Username] + '@migrated.local' WHERE [Email] IS NULL");

    // Step 3: Now make it non-nullable
    migrationBuilder.AlterColumn<string>(
        name: "Email",
        table: "Users",
        type: "nvarchar(256)",
        nullable: false,
        defaultValue: "");
}

protected override void Down(MigrationBuilder migrationBuilder)
{
    migrationBuilder.DropColumn(
        name: "Email",
        table: "Users");
}
```

### Risk Level: Critical

1. **STOP** -- Do not apply without a full plan
2. Create a database backup before proceeding
3. Write a data migration plan:
   a. Where will the data go?
   b. How will it be transformed?
   c. How can we verify completeness?
4. Implement the migration in stages (multiple migrations)
5. Verify data preservation at each stage
6. Keep the backup until the full pipeline is verified

**Example: Safe Column Drop with Data Preservation**

```csharp
// Migration 1: Copy data to new location
public partial class CopyLegacyStatusToNewColumn : Migration
{
    protected override void Up(MigrationBuilder migrationBuilder)
    {
        // Add the new column
        migrationBuilder.AddColumn<string>(
            name: "StatusDescription",
            table: "Orders",
            type: "nvarchar(100)",
            nullable: true);

        // Copy data from old column to new column
        migrationBuilder.Sql(@"
            UPDATE [Orders]
            SET [StatusDescription] = CASE [StatusCode]
                WHEN 0 THEN 'Pending'
                WHEN 1 THEN 'Processing'
                WHEN 2 THEN 'Shipped'
                WHEN 3 THEN 'Delivered'
                WHEN 4 THEN 'Cancelled'
                ELSE 'Unknown (' + CAST([StatusCode] AS nvarchar(10)) + ')'
            END");
    }

    protected override void Down(MigrationBuilder migrationBuilder)
    {
        migrationBuilder.DropColumn(
            name: "StatusDescription",
            table: "Orders");
    }
}

// Migration 2: Drop old column (only after verifying data was copied)
public partial class RemoveLegacyStatusCode : Migration
{
    protected override void Up(MigrationBuilder migrationBuilder)
    {
        migrationBuilder.DropColumn(
            name: "StatusCode",
            table: "Orders");
    }

    protected override void Down(MigrationBuilder migrationBuilder)
    {
        migrationBuilder.AddColumn<int>(
            name: "StatusCode",
            table: "Orders",
            type: "int",
            nullable: false,
            defaultValue: 0);

        // NOTE: Original data cannot be fully restored from StatusDescription
        // This is a one-way migration -- document this limitation
        migrationBuilder.Sql(@"
            UPDATE [Orders]
            SET [StatusCode] = CASE [StatusDescription]
                WHEN 'Pending' THEN 0
                WHEN 'Processing' THEN 1
                WHEN 'Shipped' THEN 2
                WHEN 'Delivered' THEN 3
                WHEN 'Cancelled' THEN 4
                ELSE 0
            END");
    }
}
```

**Example: Safe Table Split**

```csharp
public partial class SplitAddressFromCustomer : Migration
{
    protected override void Up(MigrationBuilder migrationBuilder)
    {
        // Step 1: Create the new Addresses table
        migrationBuilder.CreateTable(
            name: "Addresses",
            columns: table => new
            {
                Id = table.Column<int>(nullable: false)
                    .Annotation("SqlServer:Identity", "1, 1"),
                CustomerId = table.Column<int>(nullable: false),
                Street = table.Column<string>(maxLength: 200, nullable: true),
                City = table.Column<string>(maxLength: 100, nullable: true),
                State = table.Column<string>(maxLength: 50, nullable: true),
                ZipCode = table.Column<string>(maxLength: 20, nullable: true),
                Country = table.Column<string>(maxLength: 100, nullable: true)
            },
            constraints: table =>
            {
                table.PrimaryKey("PK_Addresses", x => x.Id);
                table.ForeignKey(
                    name: "FK_Addresses_Customers_CustomerId",
                    column: x => x.CustomerId,
                    principalTable: "Customers",
                    principalColumn: "Id",
                    onDelete: ReferentialAction.Cascade);
            });

        // Step 2: Copy address data from Customers to Addresses
        migrationBuilder.Sql(@"
            INSERT INTO [Addresses] ([CustomerId], [Street], [City], [State], [ZipCode], [Country])
            SELECT [Id], [Street], [City], [State], [ZipCode], [Country]
            FROM [Customers]
            WHERE [Street] IS NOT NULL OR [City] IS NOT NULL");

        // Step 3: Drop address columns from Customers
        // Only AFTER data is copied!
        migrationBuilder.DropColumn(name: "Street", table: "Customers");
        migrationBuilder.DropColumn(name: "City", table: "Customers");
        migrationBuilder.DropColumn(name: "State", table: "Customers");
        migrationBuilder.DropColumn(name: "ZipCode", table: "Customers");
        migrationBuilder.DropColumn(name: "Country", table: "Customers");
    }

    protected override void Down(MigrationBuilder migrationBuilder)
    {
        // Reverse: add columns back, copy data, drop table
        migrationBuilder.AddColumn<string>(name: "Street", table: "Customers",
            maxLength: 200, nullable: true);
        migrationBuilder.AddColumn<string>(name: "City", table: "Customers",
            maxLength: 100, nullable: true);
        migrationBuilder.AddColumn<string>(name: "State", table: "Customers",
            maxLength: 50, nullable: true);
        migrationBuilder.AddColumn<string>(name: "ZipCode", table: "Customers",
            maxLength: 20, nullable: true);
        migrationBuilder.AddColumn<string>(name: "Country", table: "Customers",
            maxLength: 100, nullable: true);

        migrationBuilder.Sql(@"
            UPDATE c
            SET c.[Street] = a.[Street],
                c.[City] = a.[City],
                c.[State] = a.[State],
                c.[ZipCode] = a.[ZipCode],
                c.[Country] = a.[Country]
            FROM [Customers] c
            INNER JOIN [Addresses] a ON c.[Id] = a.[CustomerId]");

        migrationBuilder.DropTable(name: "Addresses");
    }
}
```

## Decision Tree: Proceed vs Stop

```
Data loss risk assessed
        │
        v
Risk = None?
    YES ──> PROCEED: Follow standard workflow
    NO
        │
        v
Risk = Low?
    YES ──> PROCEED with review: Generate SQL, test on dev, verify
    NO
        │
        v
Risk = High?
    YES ──> CAUTION:
            ├── Is data preservation plan documented? ──> YES ──> PROCEED with plan
            │                                          └── NO  ──> STOP: Write plan first
            └── Has the SQL been tested on production-like data?
                    YES ──> PROCEED
                    NO  ──> STOP: Test first
    NO
        │
        v
Risk = Critical?
    YES ──> STOP:
            ├── 1. Create database backup
            ├── 2. Write multi-step migration plan
            ├── 3. Implement data preservation migrations
            ├── 4. Test on production data copy
            ├── 5. Get team review
            └── 6. Schedule maintenance window if needed
            Then ──> PROCEED only when all steps complete
```

## Quick Reference: SQL Patterns to Watch For

| SQL Pattern | Risk | What It Means |
|------------|------|---------------|
| `DROP TABLE` | Critical | Entire table and data removed |
| `DROP COLUMN` | Critical | Column and all its data removed |
| `ALTER COLUMN ... nvarchar(N)` (smaller N) | High | String truncation possible |
| `ALTER COLUMN ... NOT NULL` (no default) | High | Existing NULLs will cause failure |
| `ALTER COLUMN ... int` (was string) | High | Cast failures on non-numeric data |
| `DELETE FROM` | Critical | Direct data removal |
| `TRUNCATE TABLE` | Critical | All rows removed |
| `sp_rename` | Low | Rename only, data preserved |
| `CREATE TABLE` | None | New structure, no data impact |
| `CREATE INDEX` | None | Performance change only |
| `ADD COLUMN ... NULL` | None | Nullable addition, safe |
| `ADD COLUMN ... DEFAULT` | Low | Default applied to existing rows |
| `ADD CONSTRAINT ... FOREIGN KEY` | Low | May fail if orphans exist |
| `ADD CONSTRAINT ... UNIQUE` | Low | May fail if duplicates exist |
