# Alembic Migration Conventions

Depth behind the Core Philosophy constraints: principles, knowledge-base grounding, discipline
rules, anti-patterns, and recovery. Per-operation locking/data-loss detail is in
`dangerous-operations.md`; apply/rollback checklists in `migration-safety-checklist.md`.

## Domain Principles

| # | Principle | Description | Applied As |
|---|-----------|-------------|------------|
| 1 | **Data Integrity First** | Changes that could lose data need review + a backup confirmation. Dropping a column, tightening NOT NULL, narrowing a type are all risks. | Flag migrations that drop columns, change types, or add NOT NULL without defaults |
| 2 | **Rollback Safety** | Every `upgrade()` has a `downgrade()` that fully reverses it. | Test `alembic downgrade -1` on dev before applying upgrade to staging |
| 3 | **Idempotent Scripts** | Safe to run on a database already at the target state. | `IF NOT EXISTS`/`IF EXISTS`/conditional guards where appropriate |
| 4 | **Zero-Downtime Awareness** | Some DDL locks tables; large-table ops need zero-downtime strategies. | Check `dangerous-operations.md` for lock behavior by database |
| 5 | **Migration Ordering** | Alembic maintains a linear revision chain; branching breaks `upgrade head`. | Verify `alembic history` shows a linear chain before applying |
| 6 | **SQL Review Mandatory** | Autogenerate isn't always correct — it misses some changes and emits wrong SQL. | Run `alembic upgrade head --sql` and review before every apply |
| 7 | **Schema Validation** | `alembic check` reveals model/database drift. | Run `alembic check` before `revision --autogenerate` |
| 8 | **Environment Parity** | SQLite behaves differently from PostgreSQL for many DDL ops. | Never test only on SQLite if production is PostgreSQL |
| 9 | **Seed Data Management** | Data migrations belong in separate files from schema migrations. | One migration for schema, a separate one for backfill |
| 10 | **Migration Naming** | Names describe the change, not the date. | `alembic revision -m "add_user_email_index"` — descriptive, lowercase, underscores |

## Knowledge Base Lookups

| Query | When to Call |
|-------|--------------|
| `search_knowledge("Alembic migration revision upgrade downgrade SQLAlchemy")` | PLAN — lifecycle commands |
| `search_knowledge("Alembic autogenerate review SQL script")` | REVIEW SQL — autogenerate limits |
| `search_knowledge("database migration zero downtime column rename PostgreSQL")` | Reviewing locking operations |
| `search_knowledge("SQLAlchemy model metadata migration conflict")` | When `alembic check` reports drift |

## Command Sequences

```bash
# PLAN
alembic current                    # current revision
alembic history --verbose          # revision chain
alembic check                      # model/database drift (must be clean before autogenerate)

# GENERATE
alembic revision --autogenerate -m "descriptive_name"   # or: alembic revision -m "..." (manual/data)
# STOP — review the generated file in alembic/versions/

# REVIEW SQL
alembic upgrade head --sql         # review before applying
alembic downgrade -1 --sql         # review the rollback SQL too

# TEST ROLLBACK (development only)
alembic upgrade head && alembic current
alembic downgrade -1 && alembic current
alembic upgrade head

# APPLY
alembic upgrade head && alembic current
# rollback if needed: alembic downgrade -1
```

**Autogenerate does NOT detect:** stored procedures/views/triggers; semantically-equivalent type
changes (`String(50)`→`String(100)`); index changes on custom-named columns; sequence changes.

## Discipline Rules

- **Never apply without SQL review.** After `revision --autogenerate`, review the generated file,
  then `alembic upgrade head --sql`, then apply — never `upgrade head` straight after generate.
- **Test rollback before staging.** Always `alembic upgrade head` then `alembic downgrade -1` on a
  dev database before applying to staging. An untested `downgrade()` is not a rollback plan.
- **`alembic check` before autogenerate.** If `check` reports drift, investigate first — the models
  and database may be out of sync for a reason (manual migration, hotfix, prior failed migration).

## Anti-Patterns

| # | Anti-Pattern | Why It Fails | Correct Approach |
|---|-------------|-------------|-----------------|
| 1 | Applying without SQL review | Autogenerate can emit incorrect SQL; production surprises are catastrophic | Always `--sql` and review before applying |
| 2 | Empty `downgrade()` | No rollback path; a failed deployment can't be reversed | Every `upgrade()` has a working `downgrade()` |
| 3 | Schema + data in one migration | Complex rollback; data step may fail after schema succeeds | Separate schema from data migrations |
| 4 | Testing only on SQLite | SQLite ignores constraints/DDL that PostgreSQL enforces | Test on the production engine |
| 5 | Non-descriptive names | `migration_001` tells you nothing | `add_user_email_index`, `drop_legacy_sessions_table` |
| 6 | Branching the revision chain | Two migrations sharing `down_revision` break `upgrade head` | Verify `alembic history` is linear |
| 7 | Dropping columns without a transition | App code may still reference the column → runtime errors | Nullable first → remove references → drop later |
| 8 | NOT NULL without a default | Fails on tables with existing rows | Nullable → backfill → add NOT NULL |
| 9 | Large index without `CONCURRENTLY` | Locks the table, blocks reads/writes | `CREATE INDEX CONCURRENTLY` (PostgreSQL, separate transaction) |
| 10 | Committing untested migrations | Untested migrations create false confidence | Test upgrade + downgrade before committing |

## Error Recovery

**`alembic check` reports unexpected differences** (drift before you changed anything):
1. `alembic history` for the chain; `alembic current` for the DB's revision
2. Compare the schema to the models manually; identify the drift source (hotfix, failed migration, model change without migration)
3. Intentional drift → create a migration formalizing it. Unintentional → decide which is correct and align
4. Never `revision --autogenerate` until `check` is clean

**Migration fails mid-execution** (DB in unknown state):
1. `alembic current`; inspect the schema manually to see what applied
2. Partially applied → manually reverse the applied changes; `alembic stamp <previous_revision>` to reset the pointer
3. Fix the migration file; re-test on dev; never `upgrade head` again until clean

**`downgrade()` fails:**
1. Read the error — it names the failing SQL
2. Often the downgrade drops a column with dependent objects (indexes, FKs) — drop those first
3. Test the fix on dev; if already on staging/production, manual SQL rollback may be needed — document the steps first
