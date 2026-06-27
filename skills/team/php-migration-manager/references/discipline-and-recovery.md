# AI Discipline Rules & Error Recovery

Non-negotiable behaviors when operating on migrations, and how to recover when a step fails.

## AI Discipline Rules

### CRITICAL: Never `migrate:fresh` Against Shared Data

`migrate:fresh`, `migrate:refresh`, and `db:wipe` **drop all tables**. They are for local/CI databases
only. Against staging or production they are data destruction. Use `migrate` / `migrate:rollback` for
real environments.

### REQUIRED: Write `down()` and Test It

```php
public function up(): void
{
    Schema::table('users', fn (Blueprint $t) => $t->string('phone')->nullable());
}

public function down(): void
{
    Schema::table('users', fn (Blueprint $t) => $t->dropColumn('phone'));
}
```
Then prove it: `migrate` → `migrate:rollback --step=1` → `migrate:status`.

### CRITICAL: Destructive Change → Expand-Contract

Dropping or renaming a column that running code still uses causes errors mid-deploy. Split it:
**expand** (add the new shape, dual-write), **migrate** (backfill), **contract** (drop the old shape in a
later deploy once no code references it). See `references/dangerous-operations.md`.

## Error Recovery

### `down()` fails on rollback

```
Symptom: migrate:rollback throws (e.g., dropping a column an FK still references).
Fix: in down(), drop constraints/indexes before the column or table they depend on; re-test the
rollback in the scratch DB until clean. Order matters: reverse of up(), dependencies first.
```

### Migration locked a production table

```
Symptom: writes stalled during apply; slow-query log shows a long ALTER.
Recovery: for the next change, switch to expand-contract; add indexes CONCURRENTLY; run backfills in
small batches off-peak. If mid-incident, consider killing the statement and rolling back the partial
migration, then re-plan.
```

### `change()` fails: "Unknown database type" / doctrine/dbal missing

```
Symptom: a column ->change() errors on Laravel < 11.
Fix: require doctrine/dbal (composer require doctrine/dbal) for column modifications on older versions;
on Laravel 11+ native column changes are supported without it. Confirm the modified definition restates
ALL attributes (a change() replaces, it does not merge).
```
