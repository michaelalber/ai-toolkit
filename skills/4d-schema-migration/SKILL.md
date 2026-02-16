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

> "The best migration is the one where users cannot tell that anything changed,
> except that everything got better."
> -- Anonymous

This skill guides migration from 4D (4th Dimension) applications to modern
.NET 10 + SQL Server 2022 + Blazor architecture.

---

## Core Philosophy

4D is **not just a database** -- it is a complete application development
platform encompassing a relational database engine, a visual forms designer,
a proprietary programming language, triggers, and a built-in user/group security
model. Migrating from 4D is fundamentally harder than a typical database-to-
database migration because you are migrating an *entire runtime*: data types,
business logic, UI forms, validation rules, and security semantics all at once.

A naive "export tables, import rows" approach will fail. 4D has data types
that have no direct SQL Server equivalent (multi-value fields, subtables,
Pictures stored as proprietary binary). Its date/time system stores dates and
times as separate values with platform-specific epoch handling. Its NULL
semantics differ from SQL Server. Its auto-increment mechanism uses internal
record numbers that can be reused after deletion.

Success requires treating the migration as a full-stack platform transition:
data types first, then schema, then business logic, then forms, with validation
gates between every phase. You must understand what 4D *is* before you can
leave it behind.

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

---

## Workflow

### Phase 1: INVENTORY

**Goal:** Build a complete catalog of the 4D application's assets.

**Actions:**
- Export the 4D structure file (`.4DB` or text structure export).
- Catalog all tables with field names, types, and lengths.
- Catalog all relations (N-to-1, 1-to-N, N-to-N).
- Catalog all indexes (B-Tree, Cluster, Keyword, Composite, Unique).
- List all 4D methods (table triggers, form methods, project methods).
- List all forms (input forms, list forms, dialogs, subforms, tab forms).
- Document the 4D version, character set, and any plugins in use.

**Completion criteria:** Inventory report generated (see Output Templates below). Every table, relation, method, and form has a line item.

**References:** `references/common-4d-patterns.md` for identifying subtable patterns, picture storage, and multi-value fields during inventory.

```
# 4D structure exports typically include:
- Tables and fields
- Relations (foreign keys)
- Indexes
- Triggers
- Methods (code)
- Forms (UI)
```

### Phase 2: MAP

**Goal:** Establish a 1:1 type mapping for every 4D field to its SQL Server and EF Core equivalents.

**Actions:**
- Map each 4D data type to its SQL Server type using `references/4d-to-sqlserver-typemap.md`.
- Map each 4D data type to its C#/EF Core type using `references/4d-to-efcore-typemap.md`.
- Flag fields that require special handling: Pictures, Blobs, Objects (JSON), multi-value fields, separate date/time pairs.
- Identify 4D boolean fields that use -1 for true (convert to BIT 0/1).
- Decide NULL-vs-empty-string strategy per field.
- Decide blob storage strategy (VARBINARY(MAX) vs. Azure Blob Storage).
- Map 4D indexes to SQL Server index types.
- Map 4D relations to SQL Server foreign key constraints.

**Completion criteria:** Type mapping table complete. Every field has a target SQL Server type, a target C# type, and a notes column for special handling.

**References:** `references/4d-to-sqlserver-typemap.md`, `references/4d-to-efcore-typemap.md`

### Phase 3: GENERATE

**Goal:** Produce SQL Server DDL scripts and EF Core entity classes.

**Actions:**
- Generate `CREATE TABLE` statements for each table with proper types, constraints, and defaults.
- Add `[Id] INT IDENTITY(1,1)` as primary key.
- Add `[Legacy4DRecordNumber] INT NULL` to preserve original record references.
- Add audit columns (`CreatedDate`, `ModifiedDate`).
- Generate EF Core entity classes with properties, navigation properties, and configuration classes.
- Generate index creation scripts.
- Generate foreign key scripts (applied after data load).
- Plan migration order: parent tables first, child tables second.

**Completion criteria:** DDL scripts execute without error on an empty SQL Server database. EF Core entities compile. Migration order documented.

**References:** `references/4d-to-sqlserver-typemap.md` (Complete Table Example), `references/4d-to-efcore-typemap.md` (Complete Entity Example)

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

    // Navigation properties for relations
    public virtual ICollection<RelatedEntity> RelatedEntities { get; set; } = new List<RelatedEntity>();
}
```

### Phase 4: MIGRATE

**Goal:** Transfer all data from 4D export to SQL Server with type conversions.

**Actions:**
- Run pre-migration validation queries against the 4D export (row counts, NULL analysis, orphan detection, date range checks).
- Execute data migration scripts table-by-table in dependency order.
- Convert 4D booleans (`-1` or non-zero to `1`, zero to `0`).
- Combine separate 4D date and time fields into DATETIME2 where appropriate.
- Standardize NULL vs. empty string per the mapping decisions.
- Migrate blobs with MIME type and filename metadata.
- Apply foreign key constraints after all data is loaded.
- Reseed IDENTITY columns if preserving legacy IDs.

**Completion criteria:** All data loaded. Foreign keys applied without violations. Pre-migration row counts match post-migration row counts.

**References:** `references/migration-validation-queries.md` (Pre-Migration Validation, Row Count Comparison)

```sql
-- Basic migration pattern per table:
INSERT INTO [NewDB].[dbo].[TableName] ([Legacy4DRecordNumber], Col1, Col2, ...)
SELECT
    [ID],
    CONVERT(TargetType, SourceCol1),
    CASE WHEN [BoolField] <> 0 THEN 1 ELSE 0 END,
    ...
FROM [4DExport].[dbo].[SourceTable]
```

### Phase 5: VALIDATE

**Goal:** Prove the migrated data is complete and correct.

**Actions:**
- Run row count comparison for every table (source vs. target).
- Run field-level spot checks on a sample of records.
- Run aggregate validation (sums, averages, min/max) on numeric fields.
- Run relationship validation (orphan detection on all foreign keys).
- Run business rule validation (e.g., active employees must have departments).
- Create a `MigrationAudit` table to record validation results.
- Generate a validation report.

**Completion criteria:** All tables show MATCH in the migration audit. Zero orphaned records. Business rule violations documented and resolved.

**References:** `references/migration-validation-queries.md` (Post-Migration Validation, Business Rules Validation, Aggregate Validation)

### Phase 6: FORMS

**Goal:** Convert 4D forms to Blazor components with Telerik UI.

**Actions:**
- Map each 4D form type to its Blazor equivalent using `references/4d-forms-to-blazor.md`.
- Convert input forms to TelerikForm components.
- Convert list forms to TelerikGrid with OnRead, paging, sorting, and filtering.
- Convert dialogs to TelerikWindow modals.
- Convert subforms to child Blazor components with two-way binding.
- Convert tab forms to TelerikTabStrip.
- Migrate validation logic from 4D form methods to FluentValidation validators.
- Map 4D events (On Load, On Click, On Validate) to Blazor lifecycle and event handlers.
- Convert 4D business logic methods to CQRS command/query handlers.

**Completion criteria:** Every 4D form has a corresponding Blazor component. Validation behavior matches the original 4D form. Navigation flows preserved.

**References:** `references/4d-forms-to-blazor.md`, `references/common-4d-patterns.md` (4D Methods to .NET Services, 4D Triggers to EF Core)

| 4D Form Type | Blazor Equivalent |
|--------------|-------------------|
| Input form | Telerik Form with EditContext |
| List/Grid | TelerikGrid with OnRead |
| Dialog | TelerikWindow |
| Report | Telerik Report Viewer |
| Subform | Child component |
| Tab form | TelerikTabStrip |

### Phase 7: DEPLOY

**Goal:** Go live with the migrated system and monitor for issues.

**Actions:**
- Run the full validation suite one final time against production data.
- Capture performance baselines for key queries (list, search, report).
- Deploy Blazor application and SQL Server database.
- Run continuous validation stored procedure post-go-live.
- Monitor for data anomalies in the first 30 days.
- Keep the 4D export available for reference during the stabilization period.

**Completion criteria:** Application live. No critical validation failures. Performance meets or exceeds 4D baseline. Rollback plan documented but not needed.

**References:** `references/migration-validation-queries.md` (Performance Baseline, Continuous Validation)

---

## State Block

Agents using this skill should maintain the following state block to track
migration progress across sessions:

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

---

## Output Templates

### Inventory Report

```markdown
## 4D Migration Inventory: [Application Name]

**Source**: 4D v[version] | **Target**: .NET 10 + SQL Server 2022 + Blazor
**Date**: [Analysis Date] | **Analyst**: [Name/Agent]

### Schema Summary

| Metric | Count |   | Metric | Count |
|--------|-------|---|--------|-------|
| Tables | X |   | Methods | X |
| Fields (total) | X |   | Forms | X |
| Relations | X |   | Estimated Entities | X |

### Tables to Migrate

| # | 4D Table | Fields | SQL Server Table | Entity Class | Status |
|---|----------|--------|------------------|--------------|--------|
| 1 | ... | X | ... | ... | Pending |

### Type Mapping Issues

| 4D Table | 4D Field | 4D Type | Issue | Resolution |
|----------|----------|---------|-------|------------|
| ... | ... | Picture | Large binary | Azure Blob Storage |
```

### Migration Script Header

```sql
-- ============================================================
-- 4D to SQL Server Migration Script
-- Source: 4D v[version] - [Application Name]
-- Target: SQL Server 2022
-- Table: [TableName] ([X] of [Y])
-- Generated: [Date]
-- ============================================================
-- PRE-MIGRATION: Source row count = [N]
-- DEPENDENCIES: Requires [ParentTable] to be migrated first
-- SPECIAL HANDLING: [Notes about blobs, type conversions, etc.]
-- ============================================================
```

### Validation Report

```markdown
## Migration Validation Report: [Application Name]

**Date**: [Date] | **Phase**: Post-Migration / Post-Go-Live

### Row Count Validation

| Table | Source | Target | Status |
|-------|--------|--------|--------|
| ... | X | X | MATCH/MISMATCH |

### Relationship Validation

| Relationship | Total | Orphaned | Status |
|-------------|-------|----------|--------|
| Orders -> Customers | X | 0 | PASS |

### Business Rule Validation

| Rule | Violations | Severity |
|------|-----------|----------|
| Active employees have department | 0 | Critical |
```

### Forms Conversion Status

```markdown
## Forms Migration Status: [Application Name]

| # | 4D Form | Type | Blazor Component | Complexity | Status |
|---|---------|------|------------------|------------|--------|
| 1 | EmployeeInput | Input | EmployeeEdit.razor | Medium | Complete |
| 2 | EmployeeList | List | EmployeeList.razor | Low | Complete |
| 3 | OrderDialog | Dialog | OrderConfirmDialog.razor | Low | Pending |
```

---

## AI Discipline Rules

These rules are **CRITICAL** and must not be violated during migration work.

1. **ALWAYS validate row counts after every table migration.** Run a source-vs-target count comparison immediately after each INSERT. Never assume the migration "probably worked." Use `references/migration-validation-queries.md` for the exact queries.

2. **NEVER assume 4D types map 1:1 to SQL Server types.** Always consult `references/4d-to-sqlserver-typemap.md`. 4D Real may need DECIMAL (financial) or FLOAT (scientific). 4D Integer may be 16-bit (SMALLINT) or 32-bit (INT) depending on version. 4D Boolean may use -1 for true.

3. **ALWAYS handle NULL semantics explicitly.** 4D treats empty strings and NULL differently from SQL Server. Decide per-field whether empty becomes NULL or NULL becomes empty, and document the decision in the type mapping table.

4. **ALWAYS preserve auto-increment sequences.** Store the original 4D record number in `Legacy4DRecordNumber`. Create a new IDENTITY column for the SQL Server primary key. Never reuse 4D record numbers as SQL Server IDENTITY values without reseeding.

5. **ALWAYS test blob round-trips before bulk migration.** Migrate one Picture and one Blob field first. Verify the binary data is identical by comparing checksums. Only then proceed with bulk blob migration.

6. **NEVER migrate child tables before their parent tables.** Build and enforce a dependency-ordered migration plan. Apply foreign key constraints only after all related tables are loaded.

7. **ALWAYS generate DDL and migration scripts -- never execute ad-hoc SQL.** Every migration step must be scripted, version-controlled, and repeatable. If something goes wrong, you re-run from the script, not from memory.

---

## Anti-Patterns

| # | Anti-Pattern | Why It Fails | Correct Approach |
|---|-------------|-------------|------------------|
| 1 | **Big-bang migration without per-table validation** | A single failure in table 47 of 120 goes unnoticed until production. | Migrate and validate table-by-table. Log results to `MigrationAudit`. |
| 2 | **Ignoring multi-value fields / subtables** | 4D subtables become orphaned data or flat denormalized rows that break referential integrity. | Decompose into proper child tables with foreign keys. See `references/common-4d-patterns.md`. |
| 3 | **Assuming 4D dates work like SQL Server dates** | 4D stores date and time separately. Combining them incorrectly produces midnight timestamps or lost time components. | Use explicit CASE/CAST logic per `references/common-4d-patterns.md` (Date/Time Handling). |
| 4 | **Skipping blob migration testing** | Binary data may be silently truncated, corrupted by encoding conversion, or lose MIME type metadata. | Test single-record blob round-trip with checksum comparison before bulk migration. |
| 5 | **Not preserving referential integrity order** | Loading child rows before parent rows causes FK violations. Loading FKs before data causes insert failures. | Load data in dependency order. Apply FK constraints after all tables are populated. |
| 6 | **Using FLOAT for financial data** | 4D Real mapped to FLOAT introduces floating-point rounding in monetary calculations. | Use DECIMAL(19,4) for any field that represents money, prices, or financial amounts. |
| 7 | **Treating 4D empty strings as SQL Server NULLs universally** | Application logic may depend on the distinction. Queries using `= ''` vs. `IS NULL` will return different results. | Decide per-field. Document the decision. Apply consistently in migration scripts. |
| 8 | **Migrating forms without migrating validation logic** | Users can submit invalid data through the new Blazor forms that the old 4D forms would have rejected. | Extract 4D form validation methods and convert to FluentValidation validators. |
| 9 | **Ignoring character encoding differences** | 4D may use MacRoman or Windows-1252. Silent mojibake corrupts names, addresses, and text fields. | Always use NVARCHAR in SQL Server. Specify source encoding explicitly during import. |
| 10 | **Dropping 4D record numbers during migration** | External systems, reports, or user knowledge may reference original record numbers. | Preserve in `Legacy4DRecordNumber` column with an index for lookup. |

---

## Error Recovery

### Scenario 1: Type Mapping Failure

**Symptom:** `INSERT` or `CONVERT` fails during data migration with a type conversion error (e.g., string truncation, arithmetic overflow, invalid date).

**Recovery steps:**
1. Identify the failing field from the error message.
2. Query the source data to find the offending values: `SELECT DISTINCT [Field], LEN([Field]) FROM [4DExport].[dbo].[Table] ORDER BY LEN([Field]) DESC`.
3. Update the type mapping -- increase NVARCHAR length, switch INT to BIGINT, or add a CASE expression to handle edge cases.
4. Regenerate the DDL and migration script for the affected table.
5. Truncate the target table and re-run the migration for that table only.
6. Re-validate row counts and spot-check the affected field.

### Scenario 2: Data Truncation During Migration

**Symptom:** String data is silently truncated because the target NVARCHAR length is smaller than the actual 4D data.

**Recovery steps:**
1. Run `SELECT MAX(LEN([Field])) FROM [4DExport].[dbo].[Table]` to find actual max length.
2. Compare against the target column length.
3. ALTER the target column to accommodate the actual max length (or use NVARCHAR(MAX)).
4. Re-run the migration for the affected table.
5. Validate by comparing the longest source value against the target.

### Scenario 3: Referential Integrity Violations

**Symptom:** Adding foreign key constraints fails because orphaned child rows exist (child references a parent ID that does not exist in the parent table).

**Recovery steps:**
1. Run the orphan detection query from `references/migration-validation-queries.md`.
2. Determine root cause: was the parent table migration incomplete, or does the orphan exist in the 4D source?
3. If source orphan: decide whether to create a placeholder parent row, set the FK to NULL, or move the orphan to a quarantine table.
4. If migration error: re-run the parent table migration first.
5. Re-apply the foreign key constraint.
6. Log the resolution in the `MigrationAudit` table.

### Scenario 4: Blob Corruption

**Symptom:** Migrated images or binary data cannot be opened, rendered, or deserialized after migration.

**Recovery steps:**
1. Compare source and target blob sizes: `SELECT LEN([BlobField]) FROM source` vs. `SELECT DATALENGTH([BlobData]) FROM target`.
2. If sizes differ, the data was truncated or re-encoded. Check that the import uses binary mode, not text mode.
3. If sizes match but data is corrupt, compute MD5/SHA checksums on both sides and compare.
4. Verify the MIME type metadata was migrated correctly.
5. Re-export the blob data using binary-safe export (not CSV -- use BCP or SSIS with binary columns).
6. Re-import and verify with a single record before bulk re-migration.

---

## Integration with Other Skills

This skill works alongside other skills in the toolkit:

- **`ef-migration-manager`** -- After generating EF Core entities in the GENERATE phase, use `ef-migration-manager` to create and manage EF Core migration files, handle schema evolution, and manage the migration history table.

- **`dotnet-vertical-slice`** -- When converting 4D methods to .NET in the FORMS phase, use `dotnet-vertical-slice` to structure the converted business logic as vertical slice features with CQRS command/query handlers, validators, and endpoints.

- **`legacy-migration-analyzer`** -- Before starting the INVENTORY phase, run `legacy-migration-analyzer` to assess the overall migration complexity, identify high-risk areas, and generate a migration risk report that feeds into the inventory.

---

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

---

## References

- `references/4d-to-sqlserver-typemap.md` -- Data type mappings from 4D to SQL Server
- `references/4d-to-efcore-typemap.md` -- Data type mappings from 4D to C#/EF Core
- `references/common-4d-patterns.md` -- Common 4D patterns (subtables, blobs, dates, triggers) and their .NET equivalents
- `references/4d-forms-to-blazor.md` -- Form-by-form migration guidance from 4D to Blazor/Telerik
- `references/migration-validation-queries.md` -- Pre-migration, post-migration, and continuous validation SQL queries
