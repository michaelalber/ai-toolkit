# Dangerous DDL Operations in SQLx Migrations

A catalog of DDL operations that require special care in SQLx migrations.
Includes locking behavior, SQLx-specific implications, and safer alternatives.

---

## Overview

SQLx migrations are plain SQL files. Unlike EF Core or Alembic, there is no ORM
to abstract away dangerous operations. Every DDL statement is explicit and must be
reviewed for:

1. **Data loss risk** — can this operation destroy data?
2. **Locking risk** — will this operation block reads or writes?
3. **SQLx compile-time impact** — will this break `sqlx::query!` macros?
4. **Offline cache invalidation** — `sqlx prepare` must run after any schema change

---

## DROP TABLE

**Risk Level: CRITICAL**

```sql
-- DANGEROUS: Irreversible data loss
DROP TABLE orders;

-- SAFER: Rename first, drop after verification period
ALTER TABLE orders RENAME TO orders_deprecated_20240101;
-- Wait 30 days, verify no references, then:
DROP TABLE orders_deprecated_20240101;
```

**SQLx Impact:** Any `sqlx::query!` referencing this table will fail to compile.
Run `sqlx prepare` after dropping. Fix all affected queries first.

**Locking:** Acquires exclusive lock. Fast operation, but blocks all access during execution.

**Rollback:** Impossible without a backup. Verify backup before executing.

---

## DROP COLUMN

**Risk Level: HIGH**

```sql
-- DANGEROUS: Data loss, irreversible
ALTER TABLE users DROP COLUMN legacy_field;

-- SAFER: Mark as deprecated first (application-level)
-- 1. Stop writing to the column in application code
-- 2. Deploy and verify
-- 3. Then drop the column
ALTER TABLE users DROP COLUMN legacy_field;
```

**SQLx Impact:** Any `sqlx::query!` selecting this column will fail to compile.
Update all queries to remove the column reference before running the migration.

**Locking (PostgreSQL):** Fast — does not rewrite the table. Brief exclusive lock.
**Locking (MySQL):** Table rewrite required. Blocks all access for duration.

**Rollback:** `ALTER TABLE users ADD COLUMN legacy_field <type>` — but data is lost.

---

## ALTER COLUMN TYPE

**Risk Level: HIGH**

```sql
-- DANGEROUS: May truncate data, always rewrites table
ALTER TABLE products ALTER COLUMN price TYPE NUMERIC(10,2);

-- SAFER: Add new column, backfill, swap
ALTER TABLE products ADD COLUMN price_new NUMERIC(10,2);
UPDATE products SET price_new = price::NUMERIC(10,2);
ALTER TABLE products ALTER COLUMN price TYPE NUMERIC(10,2) USING price::NUMERIC(10,2);
ALTER TABLE products DROP COLUMN price_new;
```

**SQLx Impact:** The `sqlx::query!` macro type inference will change. Queries that
bind or return the column may need type annotation updates. Run `sqlx prepare` after.

**Locking:** Full table rewrite in most cases. Blocks all access for duration.

**Rollback:** Reverse the type change — but data truncated during the forward migration is lost.

---

## ADD COLUMN NOT NULL (without default)

**Risk Level: HIGH**

```sql
-- DANGEROUS: Fails if table has existing rows (PostgreSQL)
ALTER TABLE orders ADD COLUMN status VARCHAR(50) NOT NULL;

-- SAFER: Three-step approach
-- Step 1: Add nullable column
ALTER TABLE orders ADD COLUMN status VARCHAR(50);

-- Step 2: Backfill (in batches for large tables)
UPDATE orders SET status = 'pending' WHERE status IS NULL;

-- Step 3: Add NOT NULL constraint
ALTER TABLE orders ALTER COLUMN status SET NOT NULL;
```

**SQLx Impact:** `sqlx::query!` macros that insert into this table must include the
new column. Update all INSERT queries before applying Step 3.

**Locking (PostgreSQL):** Step 1 is fast. Step 3 acquires brief lock to verify no NULLs.
**Locking (MySQL):** Each step may rewrite the table.

---

## ADD COLUMN with DEFAULT (PostgreSQL < 11)

**Risk Level: MEDIUM** (PostgreSQL 11+ is safe)

```sql
-- DANGEROUS on PostgreSQL < 11: rewrites entire table
ALTER TABLE events ADD COLUMN processed BOOLEAN DEFAULT FALSE;

-- SAFER on PostgreSQL < 11: two steps
ALTER TABLE events ADD COLUMN processed BOOLEAN;
UPDATE events SET processed = FALSE WHERE processed IS NULL;
ALTER TABLE events ALTER COLUMN processed SET DEFAULT FALSE;
ALTER TABLE events ALTER COLUMN processed SET NOT NULL;
```

**PostgreSQL 11+:** `ADD COLUMN ... DEFAULT` is fast (no table rewrite). Safe.
**PostgreSQL < 11:** Full table rewrite. Check your PostgreSQL version.

**SQLx Impact:** Minimal — new column with default is backward compatible.
Run `sqlx prepare` to update the cache.

---

## CREATE INDEX (without CONCURRENTLY)

**Risk Level: MEDIUM**

```sql
-- DANGEROUS: Blocks writes during index creation
CREATE INDEX idx_orders_customer_id ON orders(customer_id);

-- SAFER: Non-blocking index creation (PostgreSQL)
CREATE INDEX CONCURRENTLY idx_orders_customer_id ON orders(customer_id);
```

**SQLx Impact:** None — indexes do not affect `sqlx::query!` compilation.
No need to run `sqlx prepare` for index-only migrations.

**Locking (PostgreSQL):**
- `CREATE INDEX`: Blocks writes for the duration of index build
- `CREATE INDEX CONCURRENTLY`: Non-blocking, but takes longer and cannot run in a transaction

**Locking (MySQL):** Online DDL available with `ALGORITHM=INPLACE, LOCK=NONE` for most index operations.

**Rollback:** `DROP INDEX idx_orders_customer_id` (fast).

---

## TRUNCATE

**Risk Level: CRITICAL**

```sql
-- DANGEROUS: Deletes all rows, irreversible without backup
TRUNCATE TABLE sessions;

-- SAFER: DELETE with WHERE (slower but auditable)
DELETE FROM sessions WHERE created_at < NOW() - INTERVAL '30 days';
```

**SQLx Impact:** None — `TRUNCATE` does not change schema.
No need to run `sqlx prepare`.

**Locking:** Acquires exclusive lock. Fast but blocks all access.

**Rollback:** Impossible without a backup.

---

## RENAME TABLE

**Risk Level: MEDIUM**

```sql
-- RISKY: Breaks all application queries referencing the old name
ALTER TABLE user_profiles RENAME TO profiles;
```

**SQLx Impact:** All `sqlx::query!` macros referencing `user_profiles` will fail to compile.
Update all queries before applying the migration, then run `sqlx prepare`.

**Locking:** Fast. Brief exclusive lock.

**Rollback:** `ALTER TABLE profiles RENAME TO user_profiles` — fast and safe.

**Recommended approach:**
1. Update all application queries to use the new name
2. Run `sqlx prepare` (will fail until migration is applied — use `DATABASE_URL` pointing to a dev DB with the rename applied)
3. Apply the migration
4. Verify build

---

## RENAME COLUMN

**Risk Level: MEDIUM**

```sql
-- RISKY: Breaks all queries referencing the old column name
ALTER TABLE users RENAME COLUMN user_name TO username;
```

**SQLx Impact:** All `sqlx::query!` macros referencing `user_name` will fail to compile.
Update all queries before applying, then run `sqlx prepare`.

**Locking:** Fast in PostgreSQL. May rewrite table in MySQL.

**Rollback:** `ALTER TABLE users RENAME COLUMN username TO user_name`.

---

## ADD FOREIGN KEY

**Risk Level: LOW-MEDIUM**

```sql
-- May fail if existing data violates the constraint
ALTER TABLE orders ADD CONSTRAINT fk_orders_customer
    FOREIGN KEY (customer_id) REFERENCES customers(id);

-- SAFER: Validate separately (PostgreSQL)
ALTER TABLE orders ADD CONSTRAINT fk_orders_customer
    FOREIGN KEY (customer_id) REFERENCES customers(id)
    NOT VALID;  -- Add constraint without validating existing rows

-- Then validate in a separate migration (or during low-traffic)
ALTER TABLE orders VALIDATE CONSTRAINT fk_orders_customer;
```

**SQLx Impact:** None — foreign keys do not affect `sqlx::query!` compilation.

**Locking (PostgreSQL):**
- `ADD CONSTRAINT ... NOT VALID`: Brief lock
- `VALIDATE CONSTRAINT`: ShareUpdateExclusiveLock (allows reads and writes)

---

## SQLx-Specific: Offline Cache Invalidation Summary

Any migration that changes the schema requires `sqlx prepare` to be run afterward.

| Operation | Requires sqlx prepare? |
|-----------|----------------------|
| `CREATE TABLE` | Yes |
| `DROP TABLE` | Yes (fix queries first) |
| `ADD COLUMN` | Yes |
| `DROP COLUMN` | Yes (fix queries first) |
| `RENAME TABLE` | Yes (fix queries first) |
| `RENAME COLUMN` | Yes (fix queries first) |
| `ALTER COLUMN TYPE` | Yes (may need query updates) |
| `CREATE INDEX` | No |
| `DROP INDEX` | No |
| `ADD CONSTRAINT` | No |
| `TRUNCATE` | No |
| `INSERT/UPDATE/DELETE` (data migration) | No |
