---
name: php-migration-manager
audience: team
description: >
  Manages the full Laravel database migration lifecycle with safety checks and rollback planning
  (PHP analog of ef-/alembic-/sqlx-migration-manager). Covers create, review, apply, and
  rollback; enforces a reversible down(), expand-contract for zero-downtime changes, and guards
  against destructive operations in production. Use when creating or reviewing Laravel
  migrations, planning a schema change, applying/rolling back, or designing a zero-downtime
  migration.
---

# PHP Migration Manager (Laravel)

> "A migration you cannot roll back is a deployment you cannot reverse."

> "Schema changes are the riskiest deploys you make. Treat them that way."

## Core Philosophy

Laravel migrations are version control for the database. This skill manages their full lifecycle —
**create → review → test rollback → apply → verify** — with safety gates between each step. A migration
is code that runs against production data exactly once per environment; a mistake is not a failed build,
it is corrupted or destroyed data.

The central discipline is **reversibility**. Every `up()` has a matching `down()` that returns the schema
to its prior state. The central risk is **destructive change on a live table**: dropping a column,
renaming, or adding a non-nullable column with no default while the old code still runs. For those, the
**expand-contract** pattern (a.k.a. parallel change) replaces a single dangerous migration with a safe
sequence across multiple deploys.

**Non-Negotiable Constraints:**
1. **Every `up()` has a tested `down()`** — rollback is verified, not assumed
2. **No destructive operation without expand-contract** on a table with live traffic
3. **`migrate:fresh` / `migrate:refresh` / `wipe` are forbidden against any shared or production DB**
4. **Review before apply** — a migration is read and risk-rated before `artisan migrate` runs
5. **Backfills are batched** — never one unbounded `UPDATE` on a large table
6. **Indexes on large tables are added concurrently** where the driver supports it

## Domain Principles

| # | Principle | Description | Applied As |
|---|-----------|-------------|------------|
| 1 | **Reversibility** | `down()` exactly reverses `up()`. If a change is irreversible (data loss), say so explicitly and gate it. | `up()` adds a column → `down()` drops it; tested with `migrate` then `migrate:rollback` |
| 2 | **Expand-contract** | Breaking schema changes are split: expand (add new, dual-write), migrate data, contract (drop old) — across separate deploys. | Add `email_verified_at` nullable → backfill → enforce → later drop legacy `verified` flag |
| 3 | **Additive first** | New columns are nullable or have a default so old code keeps working during the deploy window. | `$table->string('phone')->nullable();` not a non-null no-default add |
| 4 | **Batched backfills** | Data migrations chunk over rows; never one statement locking the whole table. | `Model::query()->whereNull('x')->chunkById(1000, ...)` |
| 5 | **Online index creation** | On large tables, create indexes without a long exclusive lock where the engine allows. | Postgres: raw `CREATE INDEX CONCURRENTLY` outside a transaction |
| 6 | **One concern per migration** | Each migration does one logical change; easier to review, apply, and roll back. | Separate "add column" and "backfill" migrations |
| 7 | **No prod fresh/refresh** | `migrate:fresh`, `migrate:refresh`, `db:wipe` drop tables — dev-only. | Guard with environment checks; never run against shared data |
| 8 | **Review then apply** | The migration is read, risk-rated, and rollback-tested in a scratch DB before it touches anything shared. | Run the REVIEW workflow, produce the Migration Review report, then apply |
| 9 | **Foreign keys are explicit** | FK constraints and their `onDelete` behavior are declared, and dropped in `down()` before the table/column. | `$table->foreignId('user_id')->constrained()->cascadeOnDelete();` |
| 10 | **Migrations are immutable once shipped** | Never edit a migration that has run in any shared environment — write a new one. | A mistake in a shipped migration → a corrective new migration |

## Knowledge Base Lookups

Use `search_knowledge` (grounded-code-mcp, `collection="php"`).

| Query | When to Call |
|-------|--------------|
| `search_knowledge("Laravel migration structure up down schema builder", collection="php")` | When writing the migration |
| `search_knowledge("Laravel migration rolling back rollback steps", collection="php")` | When planning and testing rollback |
| `search_knowledge("Laravel schema builder columns indexes foreign keys", collection="php")` | When defining columns/indexes/constraints |
| `search_knowledge("Laravel migration modifying columns change nullable", collection="php")` | When altering existing columns (needs doctrine/dbal on older versions) |
| `search_code_examples("Laravel migration create table foreignId", language="php")` | When generating the migration body |

## Workflow

### Phase 1: CREATE

```bash
php artisan make:migration create_orders_table          # new table
php artisan make:migration add_phone_to_users_table     # alter
```

Write both `up()` and `down()`. Prefer additive, nullable changes. See
`references/migration-safety-checklist.md` for column-by-column guidance.

### Phase 2: REVIEW

Read the migration and risk-rate it **before** applying. Classify each operation as
SAFE / CAUTION / DANGEROUS using `references/dangerous-operations.md`. Produce the Migration Review
report (template below). DANGEROUS operations require an expand-contract plan.

### Phase 3: TEST ROLLBACK

Apply and immediately roll back in a scratch database to prove `down()` works.

```bash
php artisan migrate --database=scratch
php artisan migrate:rollback --database=scratch --step=1
php artisan migrate:status --database=scratch
```

If `down()` errors or leaves residue, fix it before going further.

### Phase 4: APPLY

```bash
php artisan migrate --step          # records each migration separately for granular rollback
php artisan migrate:status
```

### Phase 5: VERIFY

Confirm the schema, run the backfill (batched), and re-run the app's test suite. Produce the
Post-Apply Verification report.

## State Block

```xml
<php-migration-manager-state>
  phase: CREATE | REVIEW | TEST_ROLLBACK | APPLY | VERIFY | COMPLETE
  migration: [migration file]
  laravel_version: [detected]
  operation_class: SAFE | CAUTION | DANGEROUS
  expand_contract_required: true | false
  down_method_present: true | false
  rollback_tested: true | false
  backfill_required: true | false
  applied: true | false
  last_action: [description]
</php-migration-manager-state>
```

## Output Templates

### Migration Review: [migration name]

```markdown
## Migration Review: [migration name]

**Operation(s):** [add column / drop column / rename / index / FK / backfill]
**Risk class:** SAFE | CAUTION | DANGEROUS
**Reversible:** yes | no (explain)

### Findings
| Operation | Class | Risk | Mitigation |
|-----------|-------|------|------------|
| add `phone` nullable | SAFE | none | — |
| drop `legacy_flag` | DANGEROUS | data loss; old code reads it | expand-contract: stop reads → deploy → drop later |

### Rollback Plan
- `down()` reverses: [list]
- Irreversible parts: [list or "none"]
- Tested: yes | no

### Decision
- [ ] Apply as-is (SAFE)
- [ ] Apply with batched backfill (CAUTION)
- [ ] Split into expand-contract sequence (DANGEROUS)
```

### Post-Apply Verification: [migration name]

```markdown
## Post-Apply Verification: [migration name]

- [ ] `migrate:status` shows the migration as run
- [ ] Schema matches intent (`php artisan db:show` / describe table)
- [ ] Backfill completed in batches; row counts reconcile
- [ ] Application test suite green
- [ ] Rollback rehearsed in staging
- [ ] No long lock observed during apply (checked slow-query / lock logs)
```

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

## Anti-Patterns Table

| # | Anti-Pattern | Why It Fails | Correct Approach |
|---|-------------|-------------|-----------------|
| 1 | **Empty or missing `down()`** | Cannot roll back a bad deploy | Always write and test `down()` |
| 2 | **`migrate:fresh` in prod/staging** | Drops every table — total data loss | `migrate` / `migrate:rollback` only on shared DBs |
| 3 | **Non-null, no-default column on a live table** | Old code inserts NULL → write failures during deploy | Add nullable / with default, backfill, then enforce |
| 4 | **Renaming a column in one migration** | Old code reads the old name mid-deploy | Expand-contract: add new, dual-write, drop old later |
| 5 | **Unbounded backfill `UPDATE`** | Locks the table; replication lag; timeouts | `chunkById()` batches with throttling |
| 6 | **Editing a shipped migration** | Environments diverge; some ran the old version | Write a new corrective migration |
| 7 | **Index on a huge table inside a transaction** | Long exclusive lock blocks writes | `CREATE INDEX CONCURRENTLY` (Postgres) outside a transaction |
| 8 | **Mixing schema + heavy data change** | Hard to review and roll back; long transaction | Separate schema and data migrations |
| 9 | **FK dropped after its column in `down()`** | `down()` fails on constraint dependency | Drop the FK before the column/table in `down()` |
| 10 | **Applying before reviewing** | Risk discovered in production | REVIEW + rollback test gate every apply |

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

## Integration with Other Skills

| Skill | Relationship |
|-------|-------------|
| `php-feature-slice` | A new slice that needs schema changes uses this skill for the migration lifecycle. |
| `php-architecture-checklist` | The checklist flags missing `down()` and direct-SQL risks this skill prevents. |
| `php-security-review` | Reviews migrations for unsafe raw SQL and over-broad grants. |
| `php-api-scaffolder` | When an endpoint needs new tables/columns, sequence the migration before shipping the route. |
| `tdd` | Backfill logic and data transformations are driven test-first against a scratch database. |
