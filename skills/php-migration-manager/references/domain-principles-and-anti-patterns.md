# Domain Principles, Knowledge Lookups & Anti-Patterns

The reasoning behind the migration lifecycle: the principles each phase applies, the knowledge-base
queries that ground the work, and the anti-patterns the safety gates exist to prevent.

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

## Anti-Patterns

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
