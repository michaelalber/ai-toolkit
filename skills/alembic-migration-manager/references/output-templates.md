# Alembic Migration Output Templates

## Migration Review Checklist

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

## Rollback Verification

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
