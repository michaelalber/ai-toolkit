---
name: ef-migration-manager
description: EF Core migration lifecycle with safety checks and rollback planning. Use when creating, reviewing, or applying database migrations in .NET projects.
---

# EF Core Migration Manager

> "Data is a precious thing and will last longer than the systems themselves."
> -- Tim Berners-Lee

## Core Philosophy

This skill manages the full Entity Framework Core migration lifecycle: **Plan, Create, Review SQL, Test Rollback, Apply**. Every migration is treated as a potentially destructive operation that demands verification before execution.

**Non-negotiable constraints:**

1. **Never apply a migration without reviewing the generated SQL** -- EF Core's migration builder abstracts the actual DDL; always inspect what will run against the database.
2. **Every migration must have a verified rollback path** -- Before applying `Up()`, confirm that `Down()` correctly reverses all changes. If rollback is impossible, document it explicitly.
3. **Data preservation is paramount** -- Schema changes that risk data loss require explicit acknowledgment, a data migration plan, and a backup strategy before proceeding.
4. **Migrations must be idempotent-safe** -- Generated scripts for production must use the `--idempotent` flag. Manual SQL must include existence checks (`IF EXISTS`, `IF NOT EXISTS`).
5. **One concern per migration** -- Each migration addresses a single schema change. Bundling unrelated changes makes rollback dangerous and review difficult.

## Domain Principles Table

| # | Principle | Description | Priority |
|---|-----------|-------------|----------|
| 1 | **Data Integrity First** | Never sacrifice data for schema convenience. Column drops, type narrowing, and table removal require data migration plans. | Critical |
| 2 | **Rollback Safety** | Every `Up()` must have a corresponding `Down()` that fully reverses the change. Test rollback before applying forward. | Critical |
| 3 | **Idempotent Scripts** | Production scripts must be safe to run multiple times. Use `--idempotent` for generated scripts and guard clauses for manual SQL. | Critical |
| 4 | **Zero-Downtime Awareness** | Evaluate whether a migration can run while the application is live. Flag blocking operations (table locks, large data moves). | High |
| 5 | **Migration Ordering** | Migrations form a linear chain. Never reorder, edit, or delete applied migrations. Resolve conflicts by creating new migrations. | Critical |
| 6 | **SQL Review Mandatory** | Always generate and review the SQL script before applying. The C# migration code is not sufficient -- inspect the actual DDL. | Critical |
| 7 | **Schema Validation** | After applying, verify the database schema matches the EF model snapshot. Use `dotnet ef dbcontext info` and manual checks. | High |
| 8 | **Environment Parity** | Development, staging, and production databases should follow the same migration chain. Never apply ad-hoc SQL to production only. | High |
| 9 | **Seed Data Management** | Seed data belongs in migrations or `HasData()` configurations, not in application startup code. Seed changes are migration events. | Medium |
| 10 | **Migration Naming** | Use descriptive, timestamped names that convey intent: `AddUserEmailIndex`, `SplitAddressFromCustomer`, `RemoveDeprecatedStatusColumn`. | Medium |

## Workflow

### Migration Lifecycle

```
┌──────────────────────────────────────────────────────────────────────┐
│                    EF Core Migration Lifecycle                       │
│                                                                      │
│  ┌──────┐    ┌────────┐    ┌────────────┐    ┌──────────┐    ┌─────┐│
│  │ PLAN │───>│ CREATE │───>│ REVIEW SQL │───>│ TEST     │───>│APPLY││
│  │      │    │        │    │            │    │ ROLLBACK │    │     ││
│  └──────┘    └────────┘    └────────────┘    └──────────┘    └─────┘│
│      │                          │                  │            │    │
│      │                          │ FAIL             │ FAIL       │    │
│      │                          v                  v            │    │
│      │                     ┌─────────┐       ┌──────────┐      │    │
│      │                     │ REVISE  │       │ FIX DOWN │      │    │
│      │                     │ MIGRATION│      │ METHOD   │      │    │
│      │                     └─────────┘       └──────────┘      │    │
│      │                                                          │    │
│      │                    On failure after apply:                │    │
│      │                    ┌──────────────────────┐              │    │
│      │                    │ EMERGENCY ROLLBACK   │<─────────────┘    │
│      └────────────────────│ (revert migration)   │                   │
│                           └──────────────────────┘                   │
└──────────────────────────────────────────────────────────────────────┘
```

### Pre-Flight Checklist

Before creating any migration, verify:

- [ ] All current migrations are applied (`dotnet ef migrations list`)
- [ ] Model snapshot is in sync with the database
- [ ] No pending changes from other developers
- [ ] Branch is up to date with main/develop
- [ ] Database backup exists (for staging/production)

### Data Loss Detection Decision Tree

```
Schema change detected
        │
        v
Is a column being dropped?
    YES ──> Does the column contain data?
                YES ──> CRITICAL: Data migration required
                NO  ──> LOW risk: proceed with caution
    NO
        │
        v
Is a column type being changed?
    YES ──> Is the new type narrower/incompatible?
                YES ──> HIGH risk: potential truncation or cast failure
                NO  ──> LOW risk: widening conversions are generally safe
    NO
        │
        v
Is a table being dropped or renamed?
    YES ──> Does the table contain data?
                YES ──> CRITICAL: Full data migration required
                NO  ──> LOW risk: empty table removal is safe
    NO
        │
        v
Is a NOT NULL constraint being added?
    YES ──> Do all existing rows have values?
                YES ──> LOW risk: constraint will succeed
                NO  ──> HIGH risk: migration will fail on existing data
    NO
        │
        v
    NONE: Standard schema change, proceed normally
```

### Step-by-Step Workflow

#### Step 1: PLAN

1. Identify the schema change required by the feature or fix
2. Consult the [Data Loss Matrix](references/data-loss-matrix.md) to assess risk
3. Determine if data migration is needed alongside schema change
4. Decide on migration strategy: single migration or multi-step

#### Step 2: CREATE

```bash
dotnet ef migrations add <MigrationName> --project <DataProject> --startup-project <StartupProject>
```

Review the generated files:
- `<Timestamp>_<MigrationName>.cs` -- the `Up()` and `Down()` methods
- `<Timestamp>_<MigrationName>.Designer.cs` -- snapshot metadata
- `<DbContext>ModelSnapshot.cs` -- updated model snapshot

#### Step 3: REVIEW SQL

```bash
dotnet ef migrations script --idempotent --project <DataProject> --startup-project <StartupProject>
```

Inspect the generated SQL for:
- Data loss operations (DROP, ALTER with data truncation)
- Blocking operations (large table locks)
- Missing index recreations
- Correct constraint naming

#### Step 4: TEST ROLLBACK

```bash
# Apply the migration
dotnet ef database update --project <DataProject> --startup-project <StartupProject>

# Immediately roll back
dotnet ef database update <PreviousMigrationName> --project <DataProject> --startup-project <StartupProject>

# Verify the rollback was clean
dotnet ef database update --project <DataProject> --startup-project <StartupProject>
```

#### Step 5: APPLY

For development: direct application via `dotnet ef database update`
For staging/production: generate an idempotent script or migration bundle

## State Block Format

Maintain state across conversation turns using this block:

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

### Example State Progression

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

### Migration Creation Report

```markdown
## Migration Created: [MigrationName]

**Project**: [DataProject]
**Context**: [DbContextName]
**Created**: [timestamp]

### Schema Changes
| Operation | Table/Column | Risk Level | Notes |
|-----------|-------------|------------|-------|
| [ADD/ALTER/DROP] | [target] | [none/low/high/critical] | [details] |

### Generated Files
- `Migrations/<timestamp>_<name>.cs`
- `Migrations/<timestamp>_<name>.Designer.cs`
- `Migrations/<DbContext>ModelSnapshot.cs`

### Up() Summary
[Brief description of forward migration logic]

### Down() Summary
[Brief description of rollback logic]

### Data Loss Assessment
- **Risk Level**: [none | low | high | critical]
- **Affected Data**: [description or "none"]
- **Mitigation**: [plan or "N/A"]

<ef-migration-state>
step: CREATE
migration_name: [name]
data_loss_risk: [level]
rollback_ready: false
sql_reviewed: false
last_action: Migration created and files generated
next_action: Generate and review SQL script
blockers: [any issues]
</ef-migration-state>
```

### SQL Review Report

```markdown
## SQL Review: [MigrationName]

### Generated SQL
```sql
[The actual SQL that will be executed]
```

### Review Checklist
- [ ] No unexpected DROP statements
- [ ] Column type changes are safe (widening, not narrowing)
- [ ] Indexes are properly created/maintained
- [ ] Foreign key constraints are correct
- [ ] Default values are set for NOT NULL additions
- [ ] Table locks are acceptable for table size
- [ ] Idempotency guards are present (for production scripts)

### Findings
| # | Severity | Finding | Recommendation |
|---|----------|---------|----------------|
| 1 | [INFO/WARN/CRITICAL] | [what was found] | [what to do] |

<ef-migration-state>
step: REVIEW_SQL
migration_name: [name]
data_loss_risk: [level]
rollback_ready: false
sql_reviewed: true
last_action: SQL reviewed and findings documented
next_action: Test rollback in development
blockers: [any critical findings]
</ef-migration-state>
```

### Apply Report

```markdown
## Migration Applied: [MigrationName]

**Environment**: [Development | Staging | Production]
**Method**: [Direct | Script | Bundle]
**Applied At**: [timestamp]

### Verification
- [ ] Migration appears in `__EFMigrationsHistory`
- [ ] Schema matches model snapshot
- [ ] Application starts without errors
- [ ] Key queries execute successfully

### Rollback Command
```bash
dotnet ef database update [PreviousMigrationName] --project [DataProject] --startup-project [StartupProject]
```

<ef-migration-state>
step: APPLY
migration_name: [name]
data_loss_risk: [level]
rollback_ready: true
sql_reviewed: true
last_action: Migration applied to [environment]
next_action: Verify application behavior
blockers: none
</ef-migration-state>
```

## AI Discipline Rules

### CRITICAL: Never Apply Without SQL Review

Before applying ANY migration, the generated SQL must be reviewed:

1. Run `dotnet ef migrations script` to generate the SQL
2. Inspect every statement for data loss potential
3. Verify idempotency for production deployments
4. Document findings in the SQL Review Report

If the SQL has not been reviewed, STOP. Generate the script and review it first.

```csharp
// WRONG: Applying without review
// > dotnet ef database update

// RIGHT: Review first, then apply
// > dotnet ef migrations script --idempotent -o migration.sql
// > [review migration.sql]
// > dotnet ef database update
```

### CRITICAL: Always Verify Rollback

Every migration must have a tested rollback path:

1. Apply the migration to a development database
2. Run `dotnet ef database update <PreviousMigration>` to roll back
3. Verify the database returns to its previous state
4. Re-apply to confirm the forward path still works

If rollback fails, fix the `Down()` method before proceeding. A migration without a working rollback is not ready for production.

```csharp
// In the migration file, verify Down() reverses Up()
protected override void Up(MigrationBuilder migrationBuilder)
{
    migrationBuilder.AddColumn<string>(
        name: "Email",
        table: "Users",
        type: "nvarchar(256)",
        maxLength: 256,
        nullable: true);
}

protected override void Down(MigrationBuilder migrationBuilder)
{
    // This MUST exist and correctly reverse the Up()
    migrationBuilder.DropColumn(
        name: "Email",
        table: "Users");
}
```

### CRITICAL: Never Ignore Data Loss Warnings

EF Core will flag potential data loss operations. These warnings are not optional:

1. If `dotnet ef migrations add` warns about data loss, STOP
2. Assess the impact using the [Data Loss Matrix](references/data-loss-matrix.md)
3. Create a data migration plan if needed
4. Only proceed with explicit acknowledgment and mitigation in place

```csharp
// EF Core warning example:
// An operation was scaffolded that may result in the loss of data.
// Please review the migration for accuracy.

// NEVER suppress this with:
// migrationBuilder.Sql("-- data loss acknowledged");

// INSTEAD: Create a data preservation migration:
protected override void Up(MigrationBuilder migrationBuilder)
{
    // Step 1: Create new column
    migrationBuilder.AddColumn<string>(
        name: "StatusText",
        table: "Orders",
        nullable: true);

    // Step 2: Copy data
    migrationBuilder.Sql(
        "UPDATE Orders SET StatusText = CAST(Status AS nvarchar(50))");

    // Step 3: Drop old column (only after data is safe)
    migrationBuilder.DropColumn(
        name: "Status",
        table: "Orders");
}
```

### CRITICAL: Always Check Pending Migrations

Before creating a new migration, verify the current state:

1. Run `dotnet ef migrations list` to see all migrations
2. Check for any unapplied migrations (marked as pending)
3. Apply pending migrations before creating new ones
4. If another developer has added migrations, pull and apply first

Creating a migration on top of unapplied migrations creates ordering risks and potential conflicts.

```bash
# Check current state
dotnet ef migrations list --project src/Data --startup-project src/Web

# Look for "(Pending)" markers
# If any exist, apply them first:
dotnet ef database update --project src/Data --startup-project src/Web

# THEN create your new migration
dotnet ef migrations add YourNewMigration --project src/Data --startup-project src/Web
```

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
| Apply migrations in application startup | Race conditions in multi-instance deployments, blocks startup | Use deployment scripts, bundles, or CI/CD pipeline |

## Error Recovery

### Problem: Migration Apply Failed Mid-Execution

The migration partially applied, leaving the database in an inconsistent state.

**Action:**
1. Check which statements executed by inspecting the database schema
2. If the migration is in `__EFMigrationsHistory`, it was recorded as applied
3. Manually revert the partial changes using SQL
4. Remove the history entry if needed: `DELETE FROM __EFMigrationsHistory WHERE MigrationId = '<MigrationId>'`
5. Fix the migration and re-apply
6. Consider wrapping complex migrations in explicit transactions

```sql
-- Check migration history
SELECT * FROM __EFMigrationsHistory ORDER BY MigrationId DESC;

-- Remove a partially applied migration record
DELETE FROM __EFMigrationsHistory
WHERE MigrationId = '20250115120000_AddUserPreferences';
```

### Problem: Broken Migration Chain

Migration history in the database does not match the migrations in code (e.g., after a merge conflict or deleted migration file).

**Action:**
1. Run `dotnet ef migrations list` to see the discrepancy
2. If migrations exist in DB but not in code: restore the missing migration files from git
3. If migrations exist in code but were never applied: apply them in order
4. As a last resort, create a baseline migration from current schema:

```bash
# Remove all migration files
# Create a fresh migration from current model
dotnet ef migrations add Baseline --project src/Data --startup-project src/Web

# Empty the Up() method (schema already exists)
# Apply as a no-op to sync history
```

### Problem: Data Loss Detected After Apply

A migration dropped data that should have been preserved.

**Action:**
1. IMMEDIATELY stop further migrations
2. Restore from the most recent backup
3. Re-examine the migration that caused data loss
4. Create a corrected migration with proper data preservation
5. Add the scenario to your team's review checklist

### Problem: Model Snapshot Out of Sync

The `ModelSnapshot.cs` file does not reflect the actual database state.

**Action:**
1. Do NOT manually edit the snapshot file
2. Remove the last unapplied migration: `dotnet ef migrations remove`
3. Verify the snapshot matches the database
4. Re-create the migration
5. If the snapshot is badly corrupted, consider regenerating from scratch:

```bash
# Nuclear option: rebuild snapshot from current model
# WARNING: Only do this if you understand the implications
dotnet ef migrations remove  # Repeat until only applied migrations remain
dotnet ef migrations add ResyncSnapshot
dotnet ef migrations remove  # This updates the snapshot without a migration
```

### Problem: Migration Timeout on Large Table

A migration on a large table times out due to long-running ALTER operations.

**Action:**
1. Increase the command timeout in the migration:

```csharp
protected override void Up(MigrationBuilder migrationBuilder)
{
    // Increase timeout for large table operations
    migrationBuilder.Sql("SET LOCK_TIMEOUT 300000;"); // 5 minutes

    migrationBuilder.AddColumn<string>(
        name: "NewColumn",
        table: "LargeTable",
        nullable: true);
}
```

2. Consider batched data migrations for very large tables
3. For production, schedule during maintenance windows
4. Use online schema change tools (e.g., `pt-online-schema-change` for MySQL, online index operations for SQL Server)

## Integration with Other Skills

- **`dotnet-vertical-slice`** -- When creating a new vertical slice feature, use this skill to manage any database schema changes required by the feature's data layer. The migration should be part of the slice's implementation, following the Plan/Create/Review/Apply lifecycle.
- **`dotnet-vertical-slice`** (Telerik Blazor UI section) -- When Blazor UI components require new data fields or entities, coordinate schema changes through this skill. Ensure migrations are applied before updating component data bindings. Grid and form components that bind to entity properties need their backing schema changes managed here.
- **`legacy-migration-analyzer`** -- When analyzing legacy systems for migration, use this skill to plan the EF Core schema that will replace the legacy database. Coordinate between the legacy analysis findings and the new migration plan.
