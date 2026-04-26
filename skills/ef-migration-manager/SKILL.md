---
name: ef-migration-manager
description: >
  EF Core migration lifecycle with safety checks and rollback planning. Use when
  creating, reviewing, or applying database migrations in .NET projects.
  Do NOT use when the goal is initial schema design or ad-hoc SQL management;
  Do NOT use when the project uses Dapper or raw SQL without an EF Core DbContext.
---

# EF Core Migration Manager

> "Data is a precious thing and will last longer than the systems themselves."
> -- Tim Berners-Lee

## Core Philosophy

This skill manages the full Entity Framework Core migration lifecycle: **Plan → Create → Review SQL → Test Rollback → Apply**. Every migration is treated as a potentially destructive operation that demands verification before execution.

**Non-negotiable constraints:**
1. **Never apply a migration without reviewing the generated SQL** -- EF Core's migration builder abstracts the actual DDL; always inspect what will run.
2. **Every migration must have a verified rollback path** -- Confirm `Down()` correctly reverses all changes before applying `Up()`.
3. **Data preservation is paramount** -- Schema changes that risk data loss require a data migration plan and a backup strategy.
4. **Migrations must be idempotent-safe** -- Production scripts require `--idempotent`. Manual SQL requires existence checks.
5. **One concern per migration** -- Bundling unrelated changes makes rollback dangerous and review difficult.

## Domain Principles Table

| # | Principle | Description | Priority |
|---|-----------|-------------|----------|
| 1 | **Data Integrity First** | Column drops, type narrowing, and table removal require data migration plans. | Critical |
| 2 | **Rollback Safety** | Every `Up()` must have a `Down()` that fully reverses the change. Test rollback before applying forward. | Critical |
| 3 | **Idempotent Scripts** | Production scripts must be safe to run multiple times. Use `--idempotent` or guard clauses. | Critical |
| 4 | **Zero-Downtime Awareness** | Evaluate whether a migration can run while the application is live. Flag blocking operations. | High |
| 5 | **Migration Ordering** | Migrations form a linear chain. Never reorder, edit, or delete applied migrations. | Critical |
| 6 | **SQL Review Mandatory** | The C# migration code is not sufficient -- inspect the actual DDL before applying. | Critical |
| 7 | **Schema Validation** | After applying, verify the database schema matches the EF model snapshot. | High |
| 8 | **Environment Parity** | Dev, staging, and production must follow the same migration chain. No ad-hoc SQL to production only. | High |
| 9 | **Seed Data Management** | Seed data belongs in migrations or `HasData()`, not application startup code. | Medium |
| 10 | **Migration Naming** | Use descriptive names that convey intent: `AddUserEmailIndex`, `SplitAddressFromCustomer`. | Medium |

## Knowledge Base Lookups

| Query | When to Call |
|-------|--------------|
| `search_knowledge("EF Core migration create apply rollback script generation")` | At session start — confirms dotnet-ef CLI commands and lifecycle |
| `search_knowledge("EF Core migration Up Down idempotent script SQL generation")` | During REVIEW SQL — authoritative idempotent script patterns |
| `search_knowledge("database migration zero downtime column rename data loss")` | During PLAN — zero-downtime migration strategies |
| `search_knowledge("EF Core DbContext model snapshot migration conflict resolution")` | When resolving migration conflicts |
| `search_knowledge("SQL Server PostgreSQL DDL ALTER TABLE index constraint")` | When reviewing generated DDL — safe vs. dangerous operations by database |

Search before REVIEW SQL and TEST ROLLBACK phases. Cite source paths in migration review comments.

## Workflow

The migration lifecycle flows: **PLAN → CREATE → REVIEW SQL → TEST ROLLBACK → APPLY**; on apply failure, emergency rollback returns to PLAN.

### Pre-Flight Checklist

Before creating any migration:
- [ ] All current migrations are applied (`dotnet ef migrations list`)
- [ ] Model snapshot is in sync with the database
- [ ] No pending changes from other developers
- [ ] Branch is up to date with main/develop
- [ ] Database backup exists (for staging/production)

### Data Loss Assessment

Before creating a migration, classify the change: column drop or table drop with data → **Critical**; type narrowing or NOT NULL addition on existing rows → **High**; widening type change or empty table removal → **Low**; additive change → **None**. See `references/data-loss-matrix.md` for full risk matrix.

### Step-by-Step Workflow

**Step 1: PLAN** — Identify the schema change. Consult the data loss matrix. Determine if a data migration step is needed. Decide single migration vs. multi-step.

**Step 2: CREATE**
```bash
dotnet ef migrations add <MigrationName> --project <DataProject> --startup-project <StartupProject>
```
Review the generated `Up()`, `Down()`, and updated `ModelSnapshot.cs`.

**Step 3: REVIEW SQL**
```bash
dotnet ef migrations script --idempotent --project <DataProject> --startup-project <StartupProject>
```
Inspect for: data loss operations, blocking locks, missing index recreations, constraint naming.

**Step 4: TEST ROLLBACK**
```bash
# Apply the migration
dotnet ef database update --project <DataProject> --startup-project <StartupProject>

# Roll back to the previous migration
dotnet ef database update <PreviousMigrationName> --project <DataProject> --startup-project <StartupProject>

# Re-apply to verify forward path
dotnet ef database update --project <DataProject> --startup-project <StartupProject>
```

**Step 5: APPLY** — Development: `dotnet ef database update`. Staging/production: generate an idempotent script or migration bundle.

## State Block

```
<ef-migration-state>
step: [PLAN | CREATE | REVIEW_SQL | TEST_ROLLBACK | APPLY | ROLLBACK | ERROR_RECOVERY]
migration_name: [descriptive name, e.g., AddUserEmailIndex]
data_loss_risk: [none | low | high | critical]
rollback_ready: [true | false]
sql_reviewed: [true | false]
last_action: [what was just done]
next_action: [what should happen next]
blockers: [any issues preventing progress]
</ef-migration-state>
```

**Example:**

```
<ef-migration-state>
step: PLAN
migration_name: SplitCustomerAddress
data_loss_risk: high
rollback_ready: false
sql_reviewed: false
last_action: Identified need to extract Address columns into separate table
next_action: Create migration with data copy logic
blockers: Must verify all existing customers have address data
</ef-migration-state>
```

## Output Templates

```markdown
## Migration Review: [MigrationName]
**Risk**: [none|low|high|critical] | **SQL Reviewed**: [yes|no] | **Rollback Tested**: [yes|no]

| Operation | Table/Column | Risk | Notes |
|-----------|-------------|------|-------|
| [ADD/ALTER/DROP] | [target] | [level] | [details] |

**Findings**: [any issues from SQL review]
**Rollback Command**: `dotnet ef database update [PreviousMigration] ...`
```

Full report templates (Creation Report, SQL Review Report, Apply Report): `references/migration-commands.md`.

## AI Discipline Rules

**Never apply without SQL review.** Generate the script with `--idempotent`, inspect every statement for data loss potential, then apply. If the SQL has not been reviewed, STOP.

**Always verify rollback before production.** Apply to development, run `dotnet ef database update <PreviousMigration>`, verify the schema returns to its prior state, re-apply to confirm. A migration without a working `Down()` is not production-ready.

**Never ignore data loss warnings.** When `dotnet ef migrations add` warns about data loss, STOP. Assess impact using `references/data-loss-matrix.md`. Create a data preservation step (new column → copy data → drop old column) rather than suppressing the warning. Explicit acknowledgment and mitigation must be in place before proceeding.

**Always check pending migrations before creating new ones.** Run `dotnet ef migrations list` first. If any migrations are marked as pending, apply them before adding new ones. Creating a migration on top of unapplied migrations creates ordering risks and conflicts.

## Anti-Patterns Table

| Anti-Pattern | Why It's Dangerous | Correct Approach |
|--------------|-------------------|------------------|
| Apply migration without reviewing SQL | Hidden data loss, unexpected locks, constraint violations | Always generate and review SQL script first |
| Skip rollback testing | Discover broken `Down()` during production incident | Test rollback in development for every migration |
| Edit an already-applied migration | Breaks migration chain, causes snapshot desync | Create a new corrective migration instead |
| Bundle unrelated schema changes | One failure blocks all changes, rollback is all-or-nothing | One concern per migration |
| Use `EnsureCreated()` alongside migrations | `EnsureCreated` bypasses migration history entirely | Use migrations exclusively for schema management |
| Delete migration files to "fix" issues | Corrupts migration history and model snapshot | Use `dotnet ef migrations remove` for unapplied migrations |
| Hardcode connection strings in migrations | Security risk, environment coupling | Use configuration and `IDesignTimeDbContextFactory` |
| Apply migrations in application startup | Race conditions in multi-instance deployments | Use deployment scripts, bundles, or CI/CD pipeline |

## Error Recovery

**Migration apply failed mid-execution**: Check `__EFMigrationsHistory` to see if the migration was recorded. Manually revert partial changes via SQL. Remove the history entry if needed (`DELETE FROM __EFMigrationsHistory WHERE MigrationId = '<id>'`). Fix the migration and re-apply. Wrap complex migrations in explicit transactions to prevent partial application.

**Broken migration chain**: Run `dotnet ef migrations list` to see the discrepancy. If migrations exist in DB but not in code, restore missing files from git. If code migrations were never applied, apply them in order. Last resort: create a baseline migration, empty its `Up()` method (schema already exists), and apply as a no-op.

**Data loss detected after apply**: STOP all further migrations immediately. Restore from the most recent backup. Re-examine the offending migration, create a corrected version with data preservation, and add the scenario to the team review checklist.

**Model snapshot out of sync**: Do NOT manually edit `ModelSnapshot.cs`. Run `dotnet ef migrations remove` to remove the last unapplied migration (this regenerates the snapshot). Verify alignment, then re-create the migration.

**Migration timeout on large table**: Increase command timeout in the migration using `migrationBuilder.Sql("SET LOCK_TIMEOUT <ms>;")`. For very large tables, use batched data migrations or online schema change tools (`pt-online-schema-change` for MySQL; online index operations for SQL Server). Schedule blocking operations during maintenance windows.

## Integration with Other Skills

- **`dotnet-vertical-slice`** -- When creating a new vertical slice feature, use this skill to manage schema changes required by the feature's data layer. The migration should be part of the slice implementation.
- **`legacy-migration-analyzer`** -- When analyzing legacy systems, use this skill to plan the EF Core schema replacing the legacy database. Coordinate between legacy analysis findings and the new migration plan.
