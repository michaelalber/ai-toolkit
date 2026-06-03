# Automated Review Output Templates

The structured output formats the REPORT phase must produce.

## Per-File Analysis Log

```markdown
### File: [path]

**Purpose**: [what this file does]
**Lines**: [total lines]
**Language**: [language]

#### Checklist Results

| Category | Items Checked | Pass | Fail | N/A |
|----------|--------------|------|------|-----|
| Security | [N] | [N] | [N] | [N] |
| Correctness | [N] | [N] | [N] | [N] |
| Performance | [N] | [N] | [N] | [N] |
| Maintainability | [N] | [N] | [N] | [N] |
| Style | [N] | [N] | [N] | [N] |

#### Findings

| # | Line | Category | Severity | Finding | Evidence | Suggested Fix |
|---|------|----------|----------|---------|----------|---------------|

#### Positive Observations

- [what this file does well]
```

## Consolidated Report

```markdown
## Automated Code Review Report

**Scope**: [description]
**Files reviewed**: [N]
**Review date**: [date]
**Conventions detected**: [summary]

### Critical Findings
[Findings with full evidence, one per section]

### High Findings
[Findings with full evidence]

### Medium Findings
[Findings, grouped by theme where possible]

### Low / Nit Findings
[Summary table format]

### Needs Verification
[Findings where context was ambiguous]

### Positive Observations
[Per-file and cross-cutting positive observations]

### Review Statistics

| Metric | Value |
|--------|-------|
| Files reviewed | [N] |
| Checklist items evaluated | [N] |
| Total findings | [N] |
| Critical | [N] |
| High | [N] |
| Medium | [N] |
| Low | [N] |
| Nit | [N] |
| Needs verification | [N] |
| False positives filtered | [N] |
| Positive observations | [N] |
```
