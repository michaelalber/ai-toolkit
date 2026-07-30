# Dangerous Migration Operations & Expand-Contract

Operations that destroy data or lock live tables, and the safe sequences that replace them.

## Risk classification

| Class | Examples | Rule |
|-------|----------|------|
| **SAFE** | Add nullable column; add column with default; create a new table; add index on a small table | Apply directly after rollback test |
| **CAUTION** | Add index on a medium table; add a unique constraint; backfill data | Batch / concurrent; verify no duplicates; apply off-peak |
| **DANGEROUS** | Drop column; rename column/table; change a column type in place; add non-null no-default column; add FK to a table with orphans | Never single-step on live data — use expand-contract |

## Forbidden against shared/production databases

- `php artisan migrate:fresh` — drops **all** tables, then migrates
- `php artisan migrate:refresh` — rolls back **everything**, then re-migrates
- `php artisan db:wipe` — drops all tables
- `Schema::dropIfExists()` on a populated table without a contract phase and backup

These are local/CI tools only. There is no `--force` flag that makes them safe on real data.

## Expand-contract (parallel change)

Replace one breaking migration with a safe sequence spread across **separate deploys**. Each deploy is
backward compatible with the code running before it.

### Example: rename `users.verified` (bool) → `users.email_verified_at` (timestamp)

**Deploy 1 — EXPAND (additive only):**
```php
// migration: add the new nullable column
Schema::table('users', fn (Blueprint $t) => $t->timestamp('email_verified_at')->nullable());
```
Application code begins **dual-writing**: it sets both `verified` and `email_verified_at`. Reads still use
`verified`. Old instances during the rollout keep working because the new column is nullable and unused
by them.

**Deploy 2 — MIGRATE (backfill, batched):**
```php
User::query()->where('verified', true)->whereNull('email_verified_at')
    ->chunkById(1000, fn ($rows) => $rows->each(
        fn ($u) => $u->forceFill(['email_verified_at' => $u->updated_at])->save()
    ));
```
Switch reads to `email_verified_at`. Both columns are now populated and consistent.

**Deploy 3 — CONTRACT (drop the old shape):**
```php
// only after no deployed code references `verified`
Schema::table('users', fn (Blueprint $t) => $t->dropColumn('verified'));
```

At no point is there a window where running code reads a column that does not exist or writes a value the
schema rejects.

### Example: add a non-null column with no default

DANGEROUS in one step (old code inserts rows without the column → write failure). Sequence:

1. **Expand:** add the column `nullable()`.
2. **Migrate:** backfill existing rows; update code to always write the value.
3. **Contract:** `->change()` the column to `NOT NULL` once every row has a value and all code writes it.

## Adding an index without a long lock

Inline `->index()` on a large table takes an exclusive lock for the duration of the build. On PostgreSQL,
build it concurrently outside a transaction:

```php
public function up(): void
{
    // Disable the implicit transaction so CONCURRENTLY is allowed.
    DB::statement('CREATE INDEX CONCURRENTLY orders_status_idx ON orders (status)');
}

public function down(): void
{
    DB::statement('DROP INDEX CONCURRENTLY IF EXISTS orders_status_idx');
}

public $withinTransaction = false; // Laravel: run this migration outside a transaction
```

MySQL/MariaDB perform many `ALTER TABLE ... ADD INDEX` operations online (InnoDB `ALGORITHM=INPLACE`), but
verify for the specific version and table size; large tables may still copy.

## Dropping a table safely

1. Confirm no code references it (grep the codebase, check query logs).
2. Take a backup / export.
3. Rename it first (`orders` → `orders_deprecated`) and observe for a release.
4. Only then `dropIfExists` in a later migration.

A `down()` that recreates a dropped table cannot restore its rows — note the irreversibility in the
Migration Review.

## Irreversibility disclosure

When a migration cannot be truly reversed (any drop of populated data, a lossy type change), state it in
the Migration Review report under "Irreversible parts" and require an explicit human decision and a
verified backup before applying.
