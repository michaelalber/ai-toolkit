# SQLx Migration Conventions

Depth behind the Core Philosophy constraints: principles, knowledge-base grounding, discipline
rules, anti-patterns, and recovery. Per-operation locking/data-loss detail is in
`dangerous-operations.md`; the apply/rollback checklists and command reference in
`migration-safety-checklist.md`.

## Domain Principles

| # | Principle | Description | Applied As |
|---|-----------|-------------|------------|
| 1 | **SQL Review Mandatory** | SQLx migrations are plain SQL — the SQL IS the migration. Review every line for correctness, data-loss risk, and performance. | Read the file completely before `sqlx migrate run`; flag destructive operations. |
| 2 | **Rollback First** | A migration that cannot be rolled back has not been tested. | Run `sqlx migrate revert` in development; verify the schema returns to the previous state. |
| 3 | **Offline Cache Discipline** | Compile-time query verification needs `.sqlx/`; it goes stale after every migration. | Run `sqlx prepare` after every `sqlx migrate run`; commit the updated `.sqlx/`. |
| 4 | **Zero-Downtime Awareness** | Some DDL locks tables; `ADD COLUMN` with a default rewrites the table; `DROP COLUMN` is fast but irreversible. | Note the locking behavior and zero-downtime safety of each operation. |
| 5 | **Migration Naming** | Files are `<timestamp>_<description>.sql`; the description must be meaningful. | `add_user_email_index`, not `migration_001`. The name is permanent once applied. |
| 6 | **Transactional DDL** | PostgreSQL supports transactional DDL; MySQL does not. | PostgreSQL: wrap complex migrations in transactions. MySQL: plan manual rollback. |
| 7 | **Data Migration Separation** | Keep DDL and DML in separate files; mixing complicates rollback and extends locks. | DDL file first, then DML file. |
| 8 | **Compile-Time Query Verification** | `sqlx::query!` macros verify against the schema; post-migration queries fail until `sqlx prepare` runs. | After each migration, `sqlx prepare` then verify `cargo build`. |
| 9 | **Migration Immutability** | SQLx tracks applied migrations by checksum; editing one breaks `sqlx migrate run`. | Never edit an applied migration; create a new one to fix mistakes. |
| 10 | **Environment Parity** | A migration that's 1s on an empty table may take 10min on a production table. | Test against a production-like dataset before applying to production. |

## Knowledge Base Lookups

| Query | When to Call |
|-------|--------------|
| `search_knowledge("SQLx migration sqlx migrate run revert")` | Migration lifecycle — command syntax/behavior |
| `search_knowledge("SQLx compile time query verification sqlx prepare")` | Cache regeneration workflow |
| `search_knowledge("database migration zero downtime PostgreSQL")` | Zero-downtime planning — locking behavior |
| `search_knowledge("SQLx transaction migration rollback")` | Rollback planning — transaction behavior |
| `search_knowledge("PostgreSQL ALTER TABLE locking DDL")` | DDL review — locking implications |

## Discipline Rules

- **Never apply without review.** Don't just run `sqlx migrate run`. First show the SQL and a risk
  assessment (data loss, locking, rollback complexity), then apply. *Right:* "Reviewing: adds a
  nullable column → data loss: none, locking: low (no rewrite), rollback: DROP COLUMN. Proceeding."
- **Always regenerate the cache after apply.** A migration isn't "done" at `sqlx migrate run`. Run
  `sqlx prepare`, verify `SQLX_OFFLINE=true cargo build`, and commit `.sqlx/` with the migration —
  otherwise other developers and CI get compile errors.
- **Never modify applied migrations.** Editing an applied file causes a checksum mismatch on the
  next `sqlx migrate run`. To fix a mistake, create a new migration (`sqlx migrate add fix_...`).

## Anti-Patterns

| # | Anti-Pattern | Why It Fails | Correct Approach |
|---|-------------|-------------|-----------------|
| 1 | **Apply without review** | Unreviewed SQL can cause data loss, locks, wrong schema | Read the file completely before `sqlx migrate run` |
| 2 | **Skip rollback test** | An untested rollback is a one-way door | Test `sqlx migrate revert` in development first |
| 3 | **Forget `sqlx prepare`** | Stale cache → other devs get compile errors, CI fails | Run `sqlx prepare` after every run; commit `.sqlx/` |
| 4 | **Modify applied migrations** | Checksum mismatch error | Create a new migration to fix mistakes |
| 5 | **DDL + DML in one migration** | Longer locks, complex rollback | Separate DDL and DML files |
| 6 | **Ignore locking behavior** | `ADD COLUMN DEFAULT` rewrites the table → multi-minute outage on large tables | Check locking per operation; use `pg_repack`/online DDL |
| 7 | **Non-descriptive names** | `migration_001.sql` says nothing | `add_user_email_unique_index`, `drop_legacy_sessions_table` |
| 8 | **Destructive ops without backup** | `DROP`/`TRUNCATE` are irreversible | Verify a recent backup; consider soft-delete first |
| 9 | **Not committing Cargo.lock** | sqlx version drift → different migration behavior | Commit `Cargo.lock` for application crates |
| 10 | **Skipping `sqlx migrate info`** | Can run a migration twice or miss one | Always verify applied state after run |

## Error Recovery

**Checksum mismatch error** (`sqlx migrate run` fails with "migration checksum mismatch"):
1. Identify the mismatch: `sqlx migrate info`
2. Determine if the migration was already applied to this database
3. If applied and modified: serious — the schema may be inconsistent
4. Development: `sqlx migrate revert` to the previous migration, then re-apply. Production: DO NOT
   auto-fix — escalate to DBA. Root cause: someone modified an applied migration. Prevention: never edit applied files.

**`sqlx prepare` fails** ("error connecting to database" or query errors):
1. Verify `DATABASE_URL` is set and the database is accessible
2. Verify the migration was applied: `sqlx migrate info`
3. Query errors mean the migration broke existing `sqlx::query!` macros — update them to match
4. Run `cargo build` to see which queries fail; fix them, then re-run `sqlx prepare`

**Migration applied but build fails** (`sqlx migrate run` succeeds, `cargo build` fails):
1. `cargo build 2>&1 | grep error` to find failing `sqlx::query!` macros
2. Check whether the migration changed the schema in a way that breaks the queries
3. Update the queries, or if the migration was wrong: `sqlx migrate revert`, fix, re-apply
4. After fixing: `sqlx prepare`, then `cargo build`

**Zero-downtime migration required** (table rewrite or long-running lock):
1. Identify the locking operation (`ALTER TABLE ... DEFAULT`, `CREATE INDEX` without `CONCURRENTLY`)
2. PostgreSQL: use `CREATE INDEX CONCURRENTLY`; add nullable column then `UPDATE` in batches; `pg_repack` for rewrites
3. Split into steps: (1) add nullable column (fast) → (2) backfill in batches (no lock) → (3) add NOT NULL (brief lock)
4. Document the multi-step approach in the migration file comments
