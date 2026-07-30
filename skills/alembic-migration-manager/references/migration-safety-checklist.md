# Migration Safety Checklist — Alembic

Reference for the `alembic-migration-manager` skill. Use before applying any migration to staging or production.

---

## Pre-Apply Checklist

Complete all items before running `alembic upgrade head` on any non-development environment.

### 1. Migration File Review

- [ ] Migration file exists in `alembic/versions/`
- [ ] Migration name is descriptive (not `migration_001` or a timestamp)
- [ ] `upgrade()` function is implemented and non-empty
- [ ] `downgrade()` function is implemented and non-empty (not `pass`)
- [ ] `down_revision` points to the correct previous revision
- [ ] No merge conflicts in the migration file

### 2. SQL Review

- [ ] `alembic upgrade head --sql` has been run and output reviewed
- [ ] `alembic downgrade -1 --sql` has been run and output reviewed
- [ ] No unexpected DROP TABLE or DROP COLUMN statements
- [ ] No unexpected data loss operations (TRUNCATE, DELETE without WHERE)
- [ ] Column type changes are safe (widening, not narrowing)
- [ ] NOT NULL additions have a DEFAULT or the table is empty

### 3. Rollback Verification

- [ ] `alembic upgrade head` tested on development database
- [ ] `alembic downgrade -1` tested on development database
- [ ] Database state after downgrade matches pre-migration state
- [ ] No errors during upgrade or downgrade

### 4. Zero-Downtime Assessment

- [ ] Table size assessed (rows, GB) — large tables require special handling
- [ ] Lock behavior reviewed (see `dangerous-operations.md`)
- [ ] If locking operation: maintenance window scheduled or zero-downtime alternative used
- [ ] If PostgreSQL: `CREATE INDEX CONCURRENTLY` used for new indexes on large tables

### 5. Data Loss Assessment

- [ ] No columns dropped without confirming application code no longer references them
- [ ] No tables dropped without confirming no application code references them
- [ ] If backfilling: data migration tested with representative data volume
- [ ] Backup confirmed before applying to production

### 6. Environment Parity

- [ ] Migration tested on same database engine as production (not SQLite if production is PostgreSQL)
- [ ] Migration tested on same database version as production
- [ ] Migration tested with production-representative data volume (for performance)

### 7. Revision Chain

- [ ] `alembic history` shows a linear chain (no branches)
- [ ] `alembic current` on target environment shows expected current revision
- [ ] No pending migrations from other branches

---

## Post-Apply Verification

After running `alembic upgrade head`:

- [ ] `alembic current` shows the new revision
- [ ] Application starts without errors
- [ ] Smoke test: key application flows work correctly
- [ ] No unexpected errors in application logs
- [ ] Database schema matches expected state (spot-check key tables)

---

## Rollback Decision Tree

```
Migration applied → Problem detected
        |
        v
Is the problem in the application code or the schema?
        |
   Application code → Roll back the deployment (not the migration)
        |
   Schema change → Can alembic downgrade -1 reverse it safely?
                        |
                   Yes → Run alembic downgrade -1
                        |
                   No → Manual SQL rollback required
                        (document steps before executing)
```

---

## Emergency Rollback Commands

```bash
# Check current state
alembic current
alembic history --verbose

# Roll back one migration
alembic downgrade -1

# Roll back to a specific revision
alembic downgrade <revision_id>

# Roll back to base (empty database — DANGEROUS)
alembic downgrade base

# If Alembic state is wrong but database is correct:
# Reset Alembic's revision pointer without changing the schema
alembic stamp <revision_id>
```

---

## Data Migration Safety

Data migrations (backfilling, transforming existing data) require additional safety checks:

- [ ] Data migration is in a **separate** migration file from the schema change
- [ ] Data migration has been tested with production-representative data volume
- [ ] Data migration is idempotent (safe to run twice)
- [ ] Data migration has a `downgrade()` that reverses the data change (or documents why it cannot)
- [ ] Estimated execution time is acceptable for the deployment window
- [ ] If long-running: migration uses batching to avoid long transactions

### Batched Data Migration Pattern

```python
def upgrade() -> None:
    # Batch size to avoid long transactions
    batch_size = 1000
    offset = 0

    while True:
        # Process a batch
        result = op.execute(
            text("""
                UPDATE users
                SET email_normalized = LOWER(email)
                WHERE email_normalized IS NULL
                LIMIT :batch_size OFFSET :offset
            """),
            {"batch_size": batch_size, "offset": offset}
        )

        if result.rowcount == 0:
            break

        offset += batch_size


def downgrade() -> None:
    op.execute(text("UPDATE users SET email_normalized = NULL"))
```
