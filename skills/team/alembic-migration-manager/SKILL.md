---
name: alembic-migration-manager
description: Manages the full Alembic migration lifecycle with safety checks and rollback planning. Python analog of ef-migration-manager. Use when creating, reviewing, or applying database migrations in Python projects using SQLAlchemy and Alembic. Triggers on phrases like "alembic migration", "create migration", "apply migration python", "database migration python", "sqlalchemy migration", "alembic revision", "alembic upgrade", "alembic downgrade".
---

# Alembic Migration Manager

> "Every migration is a one-way door. Make sure you know what's on the other side."
> -- Adapted from database engineering practice

> "The database is the last line of defense. Treat every schema change as if it cannot be undone."
> -- Adapted from production incident post-mortems

## Core Philosophy

Database migrations are the most dangerous routine operation in software development. A bad deployment can be rolled back. A bad migration that drops a column or corrupts data cannot be undone without a backup restore — and backup restores take time that production systems do not have.

The Alembic migration lifecycle has five non-negotiable safety gates:

1. **Never apply without reviewing the generated SQL** — `alembic upgrade head --sql` before `alembic upgrade head`
2. **Every `upgrade()` must have a verified `downgrade()`** — test the rollback before applying the upgrade
3. **Data preservation is paramount** — if a migration could lose data, it requires explicit confirmation and a backup
4. **One concern per migration** — a migration that adds a column AND creates an index AND backfills data is three migrations
5. **Idempotent-safe scripts** — migrations must be safe to run on a database that is already at the target state

**What this skill is NOT:**
- It is NOT a SQLAlchemy ORM guide
- It is NOT a database design guide
- It is NOT a backup and recovery guide — it assumes backups exist

## Domain Principles

| # | Principle | Description | Applied As |
|---|-----------|-------------|------------|
| 1 | **Data Integrity First** | Schema changes that could cause data loss require explicit review and a backup confirmation before applying. Dropping a column, changing a NOT NULL constraint, or narrowing a column type are all data loss risks. | Flag any migration that drops columns, changes types, or adds NOT NULL constraints without defaults |
| 2 | **Rollback Safety** | Every `upgrade()` function must have a corresponding `downgrade()` that reverses it completely. A migration without a working `downgrade()` is a one-way door. | Test `alembic downgrade -1` on a development database before applying `upgrade` to staging |
| 3 | **Idempotent Scripts** | Migrations must be safe to run on a database that is already at the target state. Use `IF NOT EXISTS`, `IF EXISTS`, and conditional checks where appropriate. | Review generated SQL for idempotency; add guards for manual migrations |
| 4 | **Zero-Downtime Awareness** | Some DDL operations lock tables and block reads/writes. Large table operations (adding indexes, renaming columns) require zero-downtime strategies. | Check `references/dangerous-operations.md` for lock behavior by database |
| 5 | **Migration Ordering** | Alembic maintains a linear revision chain. Branching (two migrations with the same `down_revision`) causes `alembic upgrade head` to fail. | Always verify `alembic history` shows a linear chain before applying |
| 6 | **SQL Review Mandatory** | `alembic upgrade head --sql` generates the SQL without applying it. This SQL must be reviewed before applying. Autogenerate is not always correct — it misses some changes and sometimes generates incorrect SQL. | Run `--sql` flag and review output before every `upgrade head` |
| 7 | **Schema Validation** | `alembic check` compares the current database state to the SQLAlchemy models. If it reports differences, the models and database are out of sync — investigate before generating a new migration. | Run `alembic check` before `alembic revision --autogenerate` |
| 8 | **Environment Parity** | Migrations must be tested in an environment that matches production (same database engine, same version, same character set). SQLite behaves differently from PostgreSQL for many DDL operations. | Never test migrations only on SQLite if production uses PostgreSQL |
| 9 | **Seed Data Management** | Data migrations (backfilling, transforming existing data) belong in separate migration files from schema migrations. Mixing schema and data changes makes rollback complex. | One migration for schema change; a separate migration for data backfill |
| 10 | **Migration Naming** | Migration names must describe the change, not the date. `add_user_email_index` is correct. `migration_2024_01_15` is not. | `alembic revision -m "add_user_email_index"` — descriptive, lowercase, underscores |

## Knowledge Base Lookups

Use `search_knowledge` (grounded-code-mcp) to ground decisions in authoritative references.

| Query | When to Call |
|-------|--------------|
| `search_knowledge("Alembic migration revision upgrade downgrade SQLAlchemy")` | At PLAN phase — confirm Alembic lifecycle commands |
| `search_knowledge("Alembic autogenerate review SQL script")` | During REVIEW SQL phase — confirm autogenerate limitations |
| `search_knowledge("database migration zero downtime column rename PostgreSQL")` | When reviewing potentially locking operations |
| `search_knowledge("SQLAlchemy model metadata migration conflict")` | When `alembic check` reports unexpected differences |

## Workflow

### Phase 1: PLAN

**Objective:** Understand the schema change before generating the migration.

**Steps:**

1. Identify the SQLAlchemy model change (new column, new table, index, constraint)
2. Assess data loss risk: does this change drop, narrow, or constrain existing data?
3. Identify zero-downtime requirements: is this a large table? Is the operation locking?
4. Plan the rollback: what does `downgrade()` need to do?
5. Determine if this is one migration or multiple (schema + data backfill = two migrations)

```bash
# Check current migration state
alembic current

# Review migration history
alembic history --verbose

# Check for model/database drift before generating
alembic check
```

### Phase 2: GENERATE

**Objective:** Generate the migration revision file.

```bash
# Generate autogenerated migration
alembic revision --autogenerate -m "descriptive_name_here"

# Generate empty migration (for manual or data migrations)
alembic revision -m "backfill_user_email"
```

**STOP: Review the generated file in `alembic/versions/` before proceeding.**

Autogenerate limitations — it does NOT detect:
- Stored procedures, views, triggers
- Column type changes that are semantically equivalent (e.g., `String(50)` → `String(100)`)
- Index changes on columns with custom names
- Sequence changes

### Phase 3: REVIEW SQL

**Objective:** Generate and review the SQL that will be executed.

```bash
# Generate SQL without applying — REVIEW THIS OUTPUT
alembic upgrade head --sql

# For a specific revision
alembic upgrade <revision>:head --sql
```

**Review checklist:**
- [ ] SQL matches the intended schema change
- [ ] No unexpected DROP statements
- [ ] No unexpected data loss operations
- [ ] Table locks are acceptable for the deployment window
- [ ] `downgrade()` SQL is also reviewed (run `alembic downgrade -1 --sql`)

### Phase 4: TEST ROLLBACK

**Objective:** Verify the `downgrade()` works on a development database before applying `upgrade()` to staging.

```bash
# On development database only:
# 1. Apply the migration
alembic upgrade head

# 2. Verify the schema is correct
alembic current

# 3. Test the rollback
alembic downgrade -1

# 4. Verify the rollback worked
alembic current

# 5. Re-apply for actual use
alembic upgrade head
```

### Phase 5: APPLY

**Objective:** Apply the migration to the target environment.

```bash
# Verify connection and SQL one more time (dry-run equivalent)
alembic upgrade head --sql | head -50

# Apply
alembic upgrade head

# Confirm
alembic current
```

**Rollback if needed:**
```bash
alembic downgrade -1
# Then delete the revision file from alembic/versions/ if abandoning the migration
```

## State Block

```xml
<alembic-migration-state>
  phase: PLAN | GENERATE | REVIEW_SQL | TEST_ROLLBACK | APPLY | COMPLETE
  migration_name: [descriptive name]
  data_loss_risk: none | low | medium | high
  zero_downtime_required: true | false
  sql_reviewed: true | false
  rollback_tested: true | false
  current_revision: [revision ID or "head"]
  target_revision: [revision ID or "head"]
  last_action: [description]
  next_action: [description]
</alembic-migration-state>
```

## Output Templates

### Migration Review Checklist

```markdown
## Migration Review: [migration_name]

**Revision:** [revision ID]
**Generated:** YYYY-MM-DD
**Author:** [name]

### Schema Change Summary
- **Type:** [ADD COLUMN / DROP COLUMN / ADD TABLE / DROP TABLE / ADD INDEX / MODIFY COLUMN / DATA MIGRATION]
- **Table(s) affected:** [table names]
- **Data loss risk:** [None / Low / Medium / High]
- **Estimated lock duration:** [None / Seconds / Minutes / Requires maintenance window]

### SQL Review
- [ ] `upgrade()` SQL reviewed and matches intended change
- [ ] `downgrade()` SQL reviewed and correctly reverses the change
- [ ] No unexpected DROP statements
- [ ] No unexpected data loss operations
- [ ] Idempotency verified (safe to run twice)

### Rollback Verification
- [ ] `alembic downgrade -1` tested on development database
- [ ] Database state after downgrade matches pre-migration state

### Approval
- [ ] Reviewed by: [name]
- [ ] Approved for: [dev / staging / production]
```

### Rollback Verification Template

```markdown
## Rollback Verification: [migration_name]

**Environment:** development
**Date:** YYYY-MM-DD

### Before upgrade
- `alembic current`: [revision ID]
- Schema state: [description]

### After upgrade
- `alembic current`: [new revision ID]
- Schema state: [description — matches intended change?]

### After downgrade
- `alembic current`: [original revision ID]
- Schema state: [description — matches pre-migration state?]

**Rollback verified:** ✓ Yes / ✗ No
**Notes:** [any issues encountered]
```

## AI Discipline Rules

### CRITICAL: Never Apply Without SQL Review

**WRONG:**
```bash
alembic revision --autogenerate -m "add_user_table"
alembic upgrade head  # Applied without reviewing the SQL
```

**RIGHT:**
```bash
alembic revision --autogenerate -m "add_user_table"
# STOP: review the generated file in alembic/versions/
alembic upgrade head --sql  # Review this output
# STOP: confirm the SQL is correct
alembic upgrade head  # Only after SQL review
```

### REQUIRED: Test Rollback Before Staging

**WRONG:** Apply migration to staging without testing `downgrade()` on development.

**RIGHT:** Always run `alembic upgrade head` then `alembic downgrade -1` on development before applying to staging. A `downgrade()` that has never been tested is not a rollback plan.

### CRITICAL: `alembic check` Before Autogenerate

**WRONG:** Run `alembic revision --autogenerate` when `alembic check` reports differences.

**RIGHT:** If `alembic check` reports differences, investigate why before generating. The models and database may be out of sync for a reason — a manual migration, a hotfix, or a previous failed migration.

## Anti-Patterns Table

| # | Anti-Pattern | Why It Fails | Correct Approach |
|---|-------------|-------------|-----------------|
| 1 | **Applying without SQL review** | Autogenerate can generate incorrect SQL; surprises in production are catastrophic | Always run `--sql` flag and review before applying |
| 2 | **Empty `downgrade()` function** | No rollback path; a failed deployment cannot be reversed | Every `upgrade()` must have a working `downgrade()` |
| 3 | **Schema + data in one migration** | Rollback is complex; data migration may fail after schema change succeeds | Separate schema migrations from data migrations |
| 4 | **Testing only on SQLite** | SQLite ignores many constraints and DDL operations that PostgreSQL enforces | Test on the same database engine as production |
| 5 | **Non-descriptive migration names** | `migration_001` tells you nothing; debugging requires reading every file | Use descriptive names: `add_user_email_index`, `drop_legacy_sessions_table` |
| 6 | **Branching the revision chain** | Two migrations with the same `down_revision` cause `upgrade head` to fail | Always verify `alembic history` shows a linear chain |
| 7 | **Dropping columns without a transition period** | Application code may still reference the column; causes runtime errors | Add column as nullable first; remove application references; then drop in a later migration |
| 8 | **Adding NOT NULL without a default** | Fails on tables with existing rows | Add as nullable first; backfill; then add NOT NULL constraint |
| 9 | **Large index creation without `CONCURRENTLY`** | Locks the table for the duration; blocks reads and writes | Use `CREATE INDEX CONCURRENTLY` for PostgreSQL; requires a separate transaction |
| 10 | **Committing migration files without testing** | Untested migrations in version control create false confidence | Test every migration (upgrade + downgrade) before committing |

## Error Recovery

### `alembic check` reports unexpected differences

```
Symptoms: alembic check reports model/database drift before you made any changes

Recovery:
1. Run `alembic history` to see the current revision chain
2. Run `alembic current` to see what revision the database is at
3. Compare the database schema to the SQLAlchemy models manually
4. Identify the source of drift: manual hotfix, failed migration, or model change without migration
5. If drift is intentional (hotfix): create a migration that formalizes the change
6. If drift is unintentional: determine which is correct (model or database) and align them
7. Never run `alembic revision --autogenerate` until `alembic check` is clean
```

### Migration fails mid-execution

```
Symptoms: alembic upgrade head fails partway through; database is in unknown state

Recovery:
1. Run `alembic current` to see the current revision
2. Check the database schema manually to understand what was applied
3. If the migration is partially applied: manually reverse the applied changes
4. Run `alembic stamp <previous_revision>` to reset Alembic's revision pointer
5. Fix the migration file
6. Re-test on development before re-applying
7. Never run `alembic upgrade head` again until the state is clean
```

### `downgrade()` fails

```
Symptoms: alembic downgrade -1 fails; cannot roll back

Recovery:
1. Read the error message — it usually identifies the specific SQL that failed
2. Check if the downgrade is trying to drop a column that has dependent objects (indexes, foreign keys)
3. Fix the `downgrade()` function to drop dependent objects first
4. Test the fixed downgrade on development
5. If the migration has already been applied to staging/production: manual SQL rollback may be required
6. Document the manual rollback steps before attempting them
```

## Integration with Other Skills

| Skill | Relationship |
|-------|-------------|
| `python-feature-slice` | When a new feature requires database schema changes, use this skill to manage the migration lifecycle. |
| `python-arch-review` | Architecture review may identify schema design issues before migrations are generated. |
| `python-security-review` | Migration files may contain sensitive data (default values, seed data) — review for CUI and credentials. |
| `ef-migration-manager` | Cross-reference for teams with mixed Python/.NET stacks. Safety philosophy is identical; commands differ. |
