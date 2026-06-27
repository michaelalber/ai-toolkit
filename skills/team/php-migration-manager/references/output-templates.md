# Output Templates

Fill these out during the REVIEW and VERIFY phases.

## Migration Review: [migration name]

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

## Post-Apply Verification: [migration name]

```markdown
## Post-Apply Verification: [migration name]

- [ ] `migrate:status` shows the migration as run
- [ ] Schema matches intent (`php artisan db:show` / describe table)
- [ ] Backfill completed in batches; row counts reconcile
- [ ] Application test suite green
- [ ] Rollback rehearsed in staging
- [ ] No long lock observed during apply (checked slow-query / lock logs)
```
