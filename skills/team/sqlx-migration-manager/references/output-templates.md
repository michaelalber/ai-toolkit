# SQLx Migration Output Templates

## Migration Review Report

```markdown
## SQLx Migration Review: [migration-name]

**File**: `migrations/[timestamp]_[name].sql`
**Database**: [PostgreSQL | MySQL | SQLite]
**Review Date**: [date]

### SQL Review

```sql
[migration SQL here]
```

### Risk Assessment

| Risk | Level | Notes |
|------|-------|-------|
| Data Loss | [None/Low/Medium/High] | [description] |
| Table Lock | [None/Low/Medium/High] | [description] |
| Zero-Downtime Safe | [Yes/No/Conditional] | [description] |
| Rollback Complexity | [Simple/Moderate/Complex] | [description] |

### Rollback Plan

```sql
-- Rollback SQL
[rollback SQL here]
```

### Checklist

- [ ] SQL reviewed completely
- [ ] No unintended data loss
- [ ] Locking behavior acceptable
- [ ] Rollback SQL verified
- [ ] Tested on development database
- [ ] sqlx prepare run after apply
- [ ] cargo build passes
```

## Post-Apply Verification

```markdown
## Post-Apply Verification

- [ ] `sqlx migrate info` shows migration as applied
- [ ] `cargo build` succeeds
- [ ] `SQLX_OFFLINE=true cargo build` succeeds (offline cache valid)
- [ ] Application starts without errors
- [ ] Affected queries return expected results
```
