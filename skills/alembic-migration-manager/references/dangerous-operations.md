# Dangerous DDL Operations — Alembic Migration Manager

Reference for the `alembic-migration-manager` skill. Catalog of DDL operations that carry elevated risk, organized by database engine.

---

## Risk Levels

| Level | Description | Action Required |
|-------|-------------|----------------|
| 🔴 Critical | Data loss possible; cannot be undone without backup restore | Explicit confirmation + backup verification before applying |
| 🟠 High | Table lock; blocks reads and writes for duration | Maintenance window or zero-downtime alternative |
| 🟡 Medium | Partial lock or performance impact | Assess table size; schedule during low-traffic window |
| 🟢 Low | Safe for online application; minimal impact | Standard review process |

---

## PostgreSQL

### Column Operations

| Operation | Risk | Lock Type | Duration | Zero-Downtime Alternative |
|-----------|------|-----------|----------|--------------------------|
| `ADD COLUMN` (nullable, no default) | 🟢 Low | None | Instant | N/A — already safe |
| `ADD COLUMN` (nullable, with default) | 🟢 Low (PG 11+) | None | Instant (PG 11+) | N/A |
| `ADD COLUMN` (NOT NULL, no default) | 🔴 Critical | Full table lock | Duration of table rewrite | Add nullable → backfill → add NOT NULL |
| `DROP COLUMN` | 🔴 Critical | AccessExclusiveLock | Instant (metadata only) | Remove app references first; then drop |
| `RENAME COLUMN` | 🟠 High | AccessExclusiveLock | Instant | Add new column → copy data → update app → drop old |
| `ALTER COLUMN TYPE` (compatible) | 🟡 Medium | AccessExclusiveLock | Instant if no rewrite | Verify no rewrite needed |
| `ALTER COLUMN TYPE` (incompatible) | 🔴 Critical | Full table lock | Duration of table rewrite | Add new column → copy → update app → drop old |
| `SET NOT NULL` | 🟡 Medium | Full table scan | Proportional to table size | Add CHECK constraint first (PG 12+) |
| `DROP NOT NULL` | 🟢 Low | AccessExclusiveLock | Instant | N/A |

### Index Operations

| Operation | Risk | Lock Type | Duration | Zero-Downtime Alternative |
|-----------|------|-----------|----------|--------------------------|
| `CREATE INDEX` | 🟠 High | ShareLock (blocks writes) | Proportional to table size | `CREATE INDEX CONCURRENTLY` |
| `CREATE INDEX CONCURRENTLY` | 🟢 Low | No table lock | Longer than regular CREATE | Use this for large tables |
| `DROP INDEX` | 🟢 Low | AccessExclusiveLock | Instant | N/A |
| `DROP INDEX CONCURRENTLY` | 🟢 Low | No table lock | Longer | Use for large tables |
| `CREATE UNIQUE INDEX` | 🟠 High | ShareLock | Proportional to table size | `CREATE UNIQUE INDEX CONCURRENTLY` |

### Table Operations

| Operation | Risk | Lock Type | Duration | Zero-Downtime Alternative |
|-----------|------|-----------|----------|--------------------------|
| `CREATE TABLE` | 🟢 Low | None | Instant | N/A |
| `DROP TABLE` | 🔴 Critical | AccessExclusiveLock | Instant | Remove app references first; rename → verify → drop |
| `RENAME TABLE` | 🟠 High | AccessExclusiveLock | Instant | Add new table → migrate data → update app → drop old |
| `TRUNCATE` | 🔴 Critical | AccessExclusiveLock | Instant | Never in a migration without explicit confirmation |

### Constraint Operations

| Operation | Risk | Lock Type | Duration | Zero-Downtime Alternative |
|-----------|------|-----------|----------|--------------------------|
| `ADD FOREIGN KEY` | 🟡 Medium | ShareRowExclusiveLock | Full table scan | `ADD CONSTRAINT ... NOT VALID` then `VALIDATE CONSTRAINT` |
| `ADD CHECK CONSTRAINT` | 🟡 Medium | Full table scan | Proportional to table size | `ADD CONSTRAINT ... NOT VALID` then `VALIDATE CONSTRAINT` |
| `DROP CONSTRAINT` | 🟢 Low | AccessExclusiveLock | Instant | N/A |

---

## MySQL / MariaDB

### Column Operations

| Operation | Risk | Lock Type | Duration | Zero-Downtime Alternative |
|-----------|------|-----------|----------|--------------------------|
| `ADD COLUMN` (end of table) | 🟢 Low (MySQL 8+) | None (online DDL) | Instant | N/A |
| `ADD COLUMN` (middle of table) | 🟡 Medium | Table copy | Proportional to table size | Add at end; reorder is cosmetic only |
| `DROP COLUMN` | 🔴 Critical | Table copy (MySQL 5.7) / Online (MySQL 8+) | Varies | Remove app references first |
| `RENAME COLUMN` | 🟢 Low (MySQL 8+) | None | Instant | N/A |
| `MODIFY COLUMN` (type change) | 🟡 Medium | Table copy | Proportional to table size | Add new column → copy → update app → drop old |

### Index Operations

| Operation | Risk | Lock Type | Duration | Zero-Downtime Alternative |
|-----------|------|-----------|----------|--------------------------|
| `CREATE INDEX` | 🟢 Low (MySQL 8+) | None (online DDL) | Proportional to table size | N/A — already online |
| `DROP INDEX` | 🟢 Low | None | Instant | N/A |

---

## SQLite

**Warning:** SQLite has very limited DDL support. Many operations require a full table rebuild.

| Operation | Risk | Notes |
|-----------|------|-------|
| `ADD COLUMN` (nullable) | 🟢 Low | Supported directly |
| `ADD COLUMN` (NOT NULL, no default) | 🔴 Critical | Not supported — requires table rebuild |
| `DROP COLUMN` | 🟠 High | Supported in SQLite 3.35+ only; requires table rebuild in older versions |
| `RENAME COLUMN` | 🟡 Medium | Supported in SQLite 3.25+ |
| `ALTER COLUMN TYPE` | 🔴 Critical | Not supported — requires table rebuild |
| `CREATE INDEX` | 🟢 Low | Supported |

**Critical:** If production uses PostgreSQL, never test migrations only on SQLite. SQLite will silently accept operations that PostgreSQL will reject.

---

## Zero-Downtime Patterns

### Adding a NOT NULL column to a large table

```python
# Migration 1: Add nullable column
def upgrade() -> None:
    op.add_column("users", sa.Column("phone", sa.String(20), nullable=True))

def downgrade() -> None:
    op.drop_column("users", "phone")

# Migration 2: Backfill data (separate migration)
def upgrade() -> None:
    op.execute(text("UPDATE users SET phone = '' WHERE phone IS NULL"))

def downgrade() -> None:
    op.execute(text("UPDATE users SET phone = NULL"))

# Migration 3: Add NOT NULL constraint (after app code handles the column)
def upgrade() -> None:
    op.alter_column("users", "phone", nullable=False)

def downgrade() -> None:
    op.alter_column("users", "phone", nullable=True)
```

### Creating an index on a large PostgreSQL table

```python
from alembic import op
from sqlalchemy import text

def upgrade() -> None:
    # Use CONCURRENTLY to avoid table lock
    # Note: cannot be inside a transaction — use execute_if or connection.execute
    op.execute(text(
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_users_email ON users (email)"
    ))

def downgrade() -> None:
    op.execute(text(
        "DROP INDEX CONCURRENTLY IF EXISTS ix_users_email"
    ))
```

**Note:** `CREATE INDEX CONCURRENTLY` cannot run inside a transaction. Configure Alembic to use `transaction_per_migration = false` for this migration, or use a raw connection.

### Renaming a column (zero-downtime)

```
Phase 1: Add new column (nullable)
Phase 2: Deploy app code that writes to BOTH old and new column
Phase 3: Backfill new column from old column
Phase 4: Deploy app code that reads from new column
Phase 5: Drop old column
```

This requires 5 separate migrations and 3 deployments. It is the correct approach for production systems that cannot tolerate downtime.
