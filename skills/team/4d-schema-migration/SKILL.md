---
name: 4d-schema-migration
audience: team
description: >
  Parses 4D application exports and generates SQL Server DDL, EF Core entities, and Blazor UI
  guidance. Use when migrating from 4th Dimension (4D) platform to .NET/SQL Server.
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

A naive "export tables, import rows" approach will fail. 4D has data types with no direct
SQL Server equivalent (multi-value fields, subtables, Pictures stored as proprietary
binary), stores dates and times as separate platform-specific values, has NULL semantics
that differ from SQL Server, and uses internal record numbers that can be reused after
deletion. Treat the migration as a full-stack platform transition — data types first, then
schema, then business logic, then forms — with validation gates between every phase.

The full domain-principle set, AI discipline rules, anti-pattern catalog, and knowledge-base
query-to-phase lookup live in `references/common-4d-patterns.md`; per-phase validation
checklist and error-recovery procedures live in `references/migration-validation-queries.md`.

**Knowledge base:** search the `4d_legacy` collection first for any 4D-specific behavior,
`dotnet` for target-side patterns, and cite sources in the inventory and type-mapping tables.

## Workflow

### Phase 1: INVENTORY
Export the 4D structure file and catalog: all tables with field names, types, and lengths;
all relations (N-to-1, 1-to-N, N-to-N); all indexes; all 4D methods (table triggers, form
methods, project methods); all forms (input, list, dialogs, subforms, tab forms); the 4D
version, character set, and any plugins. Every table, relation, method, and form must have a
line item in the inventory report. See `references/common-4d-patterns.md` for identifying
subtable patterns, picture storage, and multi-value fields.

### Phase 2: MAP
Map each 4D data type to its SQL Server and C#/EF Core equivalents using
`references/4d-to-sqlserver-typemap.md` and `references/4d-to-efcore-typemap.md`. Flag fields
requiring special handling: Pictures, Blobs, Objects (JSON), multi-value fields, separate
date/time pairs. Identify 4D boolean fields that use -1 for true. Decide the
NULL-vs-empty-string strategy and blob storage strategy per field. Map 4D indexes and
relations to SQL Server equivalents.
**Deliverable:** every field has a target SQL Server type, a target C# type, and a notes
column for special handling.

### Phase 3: GENERATE
Generate `CREATE TABLE` statements with proper types, constraints, and defaults. Add
`[Id] INT IDENTITY(1,1)` as primary key, `[Legacy4DRecordNumber] INT NULL` to preserve
original record references, and audit columns (`CreatedDate`, `ModifiedDate`). Generate EF
Core entity classes with navigation properties. Generate index and foreign key scripts
(foreign keys applied after data load). Document migration order: parent tables first.
Converted-table DDL and entity templates: `references/common-4d-patterns.md`.

### Phase 4: MIGRATE
Run pre-migration validation queries against the 4D export (row counts, NULL analysis,
orphan detection, date range checks). Execute data migration scripts table-by-table in
dependency order. Convert 4D booleans (`-1` or non-zero → `1`, zero → `0`). Combine separate
4D date and time fields into DATETIME2 where appropriate. Apply foreign key constraints only
after all data is loaded. Per-table INSERT/CONVERT template: `references/common-4d-patterns.md`.
**Deliverable:** all data loaded, foreign keys applied without violations, pre-migration row
counts match post-migration row counts.

### Phase 5: VALIDATE
Run row count comparison for every table (source vs. target). Run field-level spot checks and
aggregate validation (sums, averages, min/max) on numeric fields. Run relationship validation
(orphan detection on all foreign keys). Run business rule validation. Log all results to a
`MigrationAudit` table. Validation query patterns: `references/migration-validation-queries.md`.
**Deliverable:** all tables show MATCH in the migration audit, zero orphaned records, business
rule violations documented and resolved.

### Phase 6: FORMS
Map each 4D form type to its Blazor equivalent using `references/4d-forms-to-blazor.md`: input
forms → TelerikForm, list forms → TelerikGrid, dialogs → TelerikWindow, subforms → child Blazor
components, tab forms → TelerikTabStrip, reports → Telerik Report Viewer. Migrate 4D form
validation methods to FluentValidation validators. Convert 4D business logic methods to CQRS
command/query handlers.

### Phase 7: DEPLOY
Run the full validation suite one final time against production data. Capture performance
baselines for key queries (list, search, report). Deploy the Blazor application and SQL Server
database. Run the continuous validation stored procedure post-go-live. Monitor for data
anomalies in the first 30 days. Keep the 4D export available for reference during the
stabilization period.

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

## Output Template

```markdown
## 4D Migration Inventory: [App Name]
**Source**: 4D v[N] | **Target**: .NET 10 + SQL Server 2022 + Blazor
Tables: X | Fields: X | Relations: X | Methods: X | Forms: X

| # | 4D Table | Fields | SQL Server Table | Entity Class | Status |
| # | 4D Field | 4D Type | Issue | Resolution |
```

Full templates (Inventory Report, Migration Script Header, Validation Report, Forms
Conversion Status): `references/migration-validation-queries.md`.

## Integration with Other Skills

- **`ef-migration-manager`** — After generating EF Core entities in the GENERATE phase, use `ef-migration-manager` to create and manage EF Core migration files, handle schema evolution, and manage the migration history table.
- **`dotnet-vertical-slice`** — When converting 4D methods to .NET in the FORMS phase, use `dotnet-vertical-slice` to structure converted business logic as vertical slice features with CQRS command/query handlers, validators, and endpoints.
- **`legacy-migration-analyzer`** — Before starting the INVENTORY phase, run `legacy-migration-analyzer` to assess overall migration complexity, identify high-risk areas, and generate a migration risk report that feeds into the inventory.

References: `references/4d-to-sqlserver-typemap.md` | `references/4d-to-efcore-typemap.md` | `references/common-4d-patterns.md` | `references/4d-forms-to-blazor.md` | `references/migration-validation-queries.md`
