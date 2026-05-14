---
name: 4d-schema-migration
description: >
  Parses 4D application exports and generates SQL Server DDL, EF Core entities,
  and Blazor UI guidance. Use when migrating from 4th Dimension (4D) platform to
  .NET/SQL Server. Triggers on phrases like "migrate 4D", "4D to SQL Server",
  "4D database conversion", "4D schema", "4th dimension", "convert 4D",
  "4D application", "4D database", "4D to .NET", "4D to EF Core",
  "4D forms to Blazor".
references:
  - references/4d-to-sqlserver-typemap.md
  - references/4d-to-efcore-typemap.md
  - references/4d-forms-to-blazor.md
  - references/migration-validation-queries.md
  - references/common-4d-patterns.md
---

# 4D to .NET/SQL Server Migration

> "Data is a precious thing and will last longer than the systems themselves."
> -- Tim Berners-Lee

This skill guides migration from 4D (4th Dimension) applications to modern
.NET 10 + SQL Server 2022 + Blazor architecture.

## Core Philosophy

4D is **not just a database** — it is a complete application development platform
encompassing a relational database engine, a visual forms designer, a proprietary
programming language, triggers, and a built-in user/group security model. Migrating
from 4D is fundamentally harder than a typical database-to-database migration because
you are migrating an *entire runtime*: data types, business logic, UI forms, validation
rules, and security semantics all at once.

A naive "export tables, import rows" approach will fail. 4D has data types that have no
direct SQL Server equivalent (multi-value fields, subtables, Pictures stored as
proprietary binary). Its date/time system stores dates and times as separate values with
platform-specific epoch handling. Its NULL semantics differ from SQL Server. Its
auto-increment mechanism uses internal record numbers that can be reused after deletion.

Success requires treating the migration as a full-stack platform transition — data types
first, then schema, then business logic, then forms — with validation gates between every
phase.

## Domain Principles

| # | Principle | Rationale |
|---|-----------|-----------|
| 1 | **Data integrity above all else** | Zero rows lost, zero values corrupted. Every phase ends with a row-count and checksum comparison against the source. |
| 2 | **Type mapping accuracy** | Every 4D type must map to a SQL Server type that preserves range, precision, and semantics. Use `references/4d-to-sqlserver-typemap.md` as the authoritative reference. |
| 3 | **Form-to-Blazor fidelity** | Users must recognize their workflows. Map every 4D form type to its Blazor/Telerik equivalent per `references/4d-forms-to-blazor.md`. |
| 4 | **Incremental migration** | Migrate table-by-table, validate after each table. Never attempt a big-bang cutover without per-table sign-off. |
| 5 | **Validate at every step** | Pre-migration analysis, post-table validation, post-migration aggregate checks, and post-go-live monitoring. See `references/migration-validation-queries.md`. |
| 6 | **Preserve auto-increment sequences** | 4D record numbers may be referenced externally. Store the legacy record number in a dedicated column and create a new IDENTITY primary key. |
| 7 | **Handle blobs deliberately** | Pictures and blobs require binary round-trip testing. Decide between VARBINARY(MAX) and external blob storage early. |
| 8 | **Decompose multi-value fields** | 4D subtables and multi-value fields must become proper child tables with foreign keys. See `references/common-4d-patterns.md`. |
| 9 | **Maintain referential integrity order** | Migrate parent tables before child tables. Build foreign keys after all data is loaded, then validate with orphan-detection queries. |
| 10 | **Rollback capability at every phase** | Maintain the source 4D export untouched. Script every migration step so it can be re-run from scratch. Never modify the source. |

## Knowledge Base Lookups

| Query | When to Call |
|-------|--------------|
| `search_knowledge("4D data types integer boolean date time")` | During MAP — verify 4D type semantics before mapping to SQL Server |
| `search_knowledge("4D subtable multi-value field structure")` | During INVENTORY — identify non-standard 4D patterns requiring decomposition |
| `search_knowledge("4D methods triggers business logic")` | During INVENTORY — catalog 4D code requiring conversion to .NET services |
| `search_knowledge("SQL Server data types NVARCHAR DECIMAL DATETIME2")` | During GENERATE — verify SQL Server type selection for edge cases |
| `search_knowledge("EF Core entity configuration fluent API")` | During GENERATE — ground EF Core entity and configuration class patterns |
| `search_knowledge("Blazor Telerik form validation FluentValidation")` | During FORMS — verify form conversion patterns and validation approach |
| `search_knowledge("database migration validation row count integrity")` | During VALIDATE — confirm post-migration validation query patterns |

Search `4d_legacy` collection first for any 4D-specific behavior. Search `dotnet` for target-side patterns. Cite sources in the migration inventory report and type mapping table.

## Workflow

### Phase 1: INVENTORY

Export the 4D structure file and catalog: all tables with field names, types, and lengths; all relations (N-to-1, 1-to-N, N-to-N); all indexes; all 4D methods (table triggers, form methods, project methods); all forms (input, list, dialogs, subforms, tab forms); the 4D version, character set, and any plugins. Every table, relation, method, and form must have a line item in the inventory report.

References: `references/common-4d-patterns.md` for identifying subtable patterns, picture storage, and multi-value fields.

### Phase 2: MAP

Map each 4D data type to its SQL Server and C#/EF Core equivalents using `references/4d-to-sqlserver-typemap.md` and `references/4d-to-efcore-typemap.md`. Flag fields requiring special handling: Pictures, Blobs, Objects (JSON), multi-value fields, separate date/time pairs. Identify 4D boolean fields that use -1 for true. Decide the NULL-vs-empty-string strategy and blob storage strategy per field. Map 4D indexes and relations to SQL Server equivalents.

**Deliverable:** Every field has a target SQL Server type, a target C# type, and a notes column for special handling.

### Phase 3: GENERATE

Generate `CREATE TABLE` statements with proper types, constraints, and defaults. Add `[Id] INT IDENTITY(1,1)` as primary key. Add `[Legacy4DRecordNumber] INT NULL` to preserve original record references. Add audit columns (`CreatedDate`, `ModifiedDate`). Generate EF Core entity classes with navigation properties. Generate index and foreign key scripts (foreign keys applied after data load). Document migration order: parent tables first.

```sql
-- Template for converted table
CREATE TABLE [dbo].[TableName] (
    [Id] INT IDENTITY(1,1) NOT NULL,
    [Legacy4DRecordNumber] INT NULL,
    -- Converted fields here
    [CreatedDate] DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    [ModifiedDate] DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    CONSTRAINT [PK_TableName] PRIMARY KEY CLUSTERED ([Id])
);
```

```csharp
// Template for converted entity
public class EntityName
{
    public int Id { get; set; }
    public int? Legacy4DRecordNumber { get; set; }
    // Properties mapped from 4D fields
    public DateTime CreatedDate { get; set; }
    public DateTime ModifiedDate { get; set; }
    public virtual ICollection<RelatedEntity> RelatedEntities { get; set; } = new List<RelatedEntity>();
}
```

### Phase 4: MIGRATE

Run pre-migration validation queries against the 4D export (row counts, NULL analysis, orphan detection, date range checks). Execute data migration scripts table-by-table in dependency order. Convert 4D booleans (`-1` or non-zero → `1`, zero → `0`). Combine separate 4D date and time fields into DATETIME2 where appropriate. Apply foreign key constraints only after all data is loaded.

```sql
-- Basic migration pattern per table
INSERT INTO [NewDB].[dbo].[TableName] ([Legacy4DRecordNumber], Col1, Col2, ...)
SELECT
    [ID],
    CONVERT(TargetType, SourceCol1),
    CASE WHEN [BoolField] <> 0 THEN 1 ELSE 0 END,
    ...
FROM [4DExport].[dbo].[SourceTable]
```

**Deliverable:** All data loaded. Foreign keys applied without violations. Pre-migration row counts match post-migration row counts.

### Phase 5: VALIDATE

Run row count comparison for every table (source vs. target). Run field-level spot checks and aggregate validation (sums, averages, min/max) on numeric fields. Run relationship validation (orphan detection on all foreign keys). Run business rule validation. Log all results to a `MigrationAudit` table. See `references/migration-validation-queries.md` for validation query patterns.

**Deliverable:** All tables show MATCH in the migration audit. Zero orphaned records. Business rule violations documented and resolved.

### Phase 6: FORMS

Map each 4D form type to its Blazor equivalent using `references/4d-forms-to-blazor.md`. Convert input forms to TelerikForm, list forms to TelerikGrid, dialogs to TelerikWindow, subforms to child Blazor components, and tab forms to TelerikTabStrip. Migrate 4D form validation methods to FluentValidation validators. Convert 4D business logic methods to CQRS command/query handlers.

| 4D Form Type | Blazor Equivalent |
|--------------|-------------------|
| Input form | Telerik Form with EditContext |
| List/Grid | TelerikGrid with OnRead |
| Dialog | TelerikWindow |
| Report | Telerik Report Viewer |
| Subform | Child component |
| Tab form | TelerikTabStrip |

### Phase 7: DEPLOY

Run the full validation suite one final time against production data. Capture performance baselines for key queries (list, search, report). Deploy Blazor application and SQL Server database. Run continuous validation stored procedure post-go-live. Monitor for data anomalies in the first 30 days. Keep the 4D export available for reference during the stabilization period.

## State Block

```xml
<4d-migration-state>
  <mode>INVENTORY|MAP|GENERATE|MIGRATE|VALIDATE|FORMS|DEPLOY</mode>
  <source_4d_version>v19.4</source_4d_version>
  <target_sql_version>SQL Server 2022</target_sql_version>
  <target_dotnet_version>.NET 10</target_dotnet_version>
  <tables_total>0</tables_total>
  <tables_migrated>0</tables_migrated>
  <tables_validated>0</tables_validated>
  <validation_status>NOT_STARTED|IN_PROGRESS|PASS|FAIL</validation_status>
  <forms_total>0</forms_total>
  <forms_converted>0</forms_converted>
  <methods_total>0</methods_total>
  <methods_converted>0</methods_converted>
  <blob_strategy>VARBINARY|BLOB_STORAGE</blob_strategy>
  <last_action>description of last completed action</last_action>
  <next_action>description of next planned action</next_action>
  <blocking_issues>any issues preventing progress</blocking_issues>
</4d-migration-state>
```

## Output Templates

```markdown
## 4D Migration Inventory: [App Name]
**Source**: 4D v[N] | **Target**: .NET 10 + SQL Server 2022 + Blazor
Tables: X | Fields: X | Relations: X | Methods: X | Forms: X

| # | 4D Table | Fields | SQL Server Table | Entity Class | Status |
| # | 4D Field | 4D Type | Issue | Resolution |
```

Full templates (Inventory Report, Migration Script Header, Validation Report, Forms Conversion Status): `references/migration-validation-queries.md`

## AI Discipline Rules

1. **ALWAYS validate row counts after every table migration.** Run a source-vs-target count comparison immediately after each INSERT. Never assume the migration "probably worked." Use `references/migration-validation-queries.md` for the exact queries.

2. **NEVER assume 4D types map 1:1 to SQL Server types.** Always consult `references/4d-to-sqlserver-typemap.md`. 4D Real may need DECIMAL (financial) or FLOAT (scientific). 4D Integer may be 16-bit (SMALLINT) or 32-bit (INT) depending on version. 4D Boolean may use -1 for true.

3. **ALWAYS handle NULL semantics explicitly.** 4D treats empty strings and NULL differently from SQL Server. Decide per-field whether empty becomes NULL or NULL becomes empty, and document the decision in the type mapping table.

4. **ALWAYS preserve auto-increment sequences.** Store the original 4D record number in `Legacy4DRecordNumber`. Create a new IDENTITY column for the SQL Server primary key. Never reuse 4D record numbers as SQL Server IDENTITY values without reseeding.

5. **ALWAYS test blob round-trips before bulk migration.** Migrate one Picture and one Blob field first. Verify the binary data is identical by comparing checksums. Only then proceed with bulk blob migration.

6. **NEVER migrate child tables before their parent tables.** Build and enforce a dependency-ordered migration plan. Apply foreign key constraints only after all related tables are loaded.

7. **ALWAYS generate DDL and migration scripts — never execute ad-hoc SQL.** Every migration step must be scripted, version-controlled, and repeatable. If something goes wrong, re-run from the script, not from memory.

## Anti-Patterns

| # | Anti-Pattern | Why It Fails | Correct Approach |
|---|-------------|-------------|------------------|
| 1 | **Big-bang migration without per-table validation** | A single failure in table 47 of 120 goes unnoticed until production. | Migrate and validate table-by-table. Log results to `MigrationAudit`. |
| 2 | **Ignoring multi-value fields / subtables** | 4D subtables become orphaned data or flat denormalized rows that break referential integrity. | Decompose into proper child tables with foreign keys. See `references/common-4d-patterns.md`. |
| 3 | **Assuming 4D dates work like SQL Server dates** | 4D stores date and time separately. Combining them incorrectly produces midnight timestamps or lost time components. | Use explicit CASE/CAST logic per `references/common-4d-patterns.md` (Date/Time Handling). |
| 4 | **Skipping blob migration testing** | Binary data may be silently truncated, corrupted by encoding conversion, or lose MIME type metadata. | Test single-record blob round-trip with checksum comparison before bulk migration. |
| 5 | **Not preserving referential integrity order** | Loading child rows before parent rows causes FK violations. Loading FKs before data causes insert failures. | Load data in dependency order. Apply FK constraints after all tables are populated. |
| 6 | **Using FLOAT for financial data** | 4D Real mapped to FLOAT introduces floating-point rounding in monetary calculations. | Use DECIMAL(19,4) for any field that represents money, prices, or financial amounts. |
| 7 | **Treating 4D empty strings as SQL Server NULLs universally** | Application logic may depend on the distinction. Queries using `= ''` vs. `IS NULL` return different results. | Decide per-field. Document the decision. Apply consistently in migration scripts. |
| 8 | **Migrating forms without migrating validation logic** | Users can submit invalid data that the old 4D forms would have rejected. | Extract 4D form validation methods and convert to FluentValidation validators. |
| 9 | **Ignoring character encoding differences** | 4D may use MacRoman or Windows-1252. Silent mojibake corrupts names, addresses, and text fields. | Always use NVARCHAR in SQL Server. Specify source encoding explicitly during import. |
| 10 | **Dropping 4D record numbers during migration** | External systems, reports, or user knowledge may reference original record numbers. | Preserve in `Legacy4DRecordNumber` column with an index for lookup. |

## Error Recovery

**Type mapping failure** (INSERT/CONVERT fails with type conversion error): Query source to find offending values (`SELECT DISTINCT [Field], LEN([Field]) FROM [4DExport].[dbo].[Table] ORDER BY LEN([Field]) DESC`). Update the type mapping, regenerate DDL and migration script for the affected table, truncate the target table and re-run, then re-validate row counts and spot-check the affected field.

**Data truncation** (string data silently truncated): Run `SELECT MAX(LEN([Field])) FROM [4DExport].[dbo].[Table]` to find actual max length. Compare against target column length. ALTER the target column, re-run the migration, and validate by comparing the longest source value against the target.

**Referential integrity violations** (FK constraints fail): Run orphan detection query from `references/migration-validation-queries.md`. If source orphan: create a placeholder parent, set the FK to NULL, or quarantine the row. If migration error: re-run the parent table migration first. Re-apply the foreign key constraint and log the resolution in `MigrationAudit`.

**Blob corruption** (migrated images/binary data unreadable): Compare source and target blob sizes. If sizes differ, the data was truncated or re-encoded — use binary-safe export (BCP or SSIS with binary columns, not CSV). If sizes match, compute checksums on both sides and compare. Re-import and verify with a single record before bulk re-migration.

## Integration with Other Skills

- **`ef-migration-manager`** — After generating EF Core entities in the GENERATE phase, use `ef-migration-manager` to create and manage EF Core migration files, handle schema evolution, and manage the migration history table.
- **`dotnet-vertical-slice`** — When converting 4D methods to .NET in the FORMS phase, use `dotnet-vertical-slice` to structure converted business logic as vertical slice features with CQRS command/query handlers, validators, and endpoints.
- **`legacy-migration-analyzer`** — Before starting the INVENTORY phase, run `legacy-migration-analyzer` to assess overall migration complexity, identify high-risk areas, and generate a migration risk report that feeds into the inventory.

References: `references/4d-to-sqlserver-typemap.md` | `references/4d-to-efcore-typemap.md` | `references/common-4d-patterns.md` | `references/4d-forms-to-blazor.md` | `references/migration-validation-queries.md`

## Validation Checklist

Use this checklist as the final gate before each phase transition:

- [ ] All tables mapped to SQL Server with correct types
- [ ] All fields have verified type mappings (no assumptions)
- [ ] All relationships preserved as foreign keys
- [ ] Indexes recreated appropriately (B-Tree, Unique, Full-Text)
- [ ] Multi-value fields decomposed into child tables
- [ ] Blob strategy decided and tested (VARBINARY vs. external storage)
- [ ] Auto-increment sequences preserved with legacy ID column
- [ ] NULL vs. empty-string strategy documented per field
- [ ] Business logic identified and assigned to CQRS handlers
- [ ] Forms mapped to Blazor components with validation
- [ ] Data migration scripts tested and repeatable
- [ ] Row counts match source for every table
- [ ] Aggregate values match source for key numeric fields
- [ ] Foreign key relationships validated (zero orphans)
- [ ] Key business reports produce identical output
- [ ] Performance baselines captured and acceptable
- [ ] Rollback plan documented and tested
