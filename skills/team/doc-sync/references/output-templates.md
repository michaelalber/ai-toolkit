# Doc Sync Output Templates

## Staleness Report

```markdown
# Documentation Staleness Report

**Scope**: [directory/namespace]
**Date**: [YYYY-MM-DD]
**Files analyzed**: [count]

## Summary

| Category | Count | Action Required |
|----------|-------|-----------------|
| Current | [N] | None |
| Stale | [N] | Update docs |
| Missing | [N] | Generate docs |
| Orphaned | [N] | Remove docs |
| Drift | [N] | Correct docs |

## Critical Items (Orphaned + Drift)

| File | Member | Issue | Last Code Change | Last Doc Change |
|------|--------|-------|------------------|-----------------|
| [path] | [member] | [category] | [date] | [date] |

## Stale Items

| File | Member | Days Since Code Change | Days Since Doc Change |
|------|--------|----------------------|---------------------|
| [path] | [member] | [N] | [N] |

## Missing Documentation

| File | Member | Visibility | Priority |
|------|--------|-----------|----------|
| [path] | [member] | public | [high/medium/low] |
```

## XML Doc Coverage Report

```markdown
# XML Doc Coverage: [Namespace/Project]

**Date**: [YYYY-MM-DD]
**Total public members**: [count]
**Documented**: [count] ([percentage]%)
**Missing docs**: [count]

## Coverage by Type

| Type | Total Members | Documented | Missing | Coverage |
|------|--------------|------------|---------|----------|
| [ClassName] | [N] | [N] | [N] | [%] |

## Missing Documentation Details

### [ClassName]

- `MethodName(ParamType)` -- public, no XML doc
- `PropertyName` -- public, no XML doc

## Quality Issues

| File | Member | Issue |
|------|--------|-------|
| [path] | [member] | Summary restates method name |
| [path] | [member] | Missing exception documentation |
| [path] | [member] | Param name mismatch |
```
