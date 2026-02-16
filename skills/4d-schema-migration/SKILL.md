---
name: 4d-schema-migration
description: Parses 4D application exports and generates SQL Server DDL, EF Core entities, and Blazor UI guidance. Use when migrating from 4th Dimension (4D) platform to .NET/SQL Server. Triggers on phrases like "migrate 4d", "4d schema", "4th dimension", "convert 4d", "4d application", "4d database", "4d to sql server", "4d to .net".
---

# 4D to .NET/SQL Server Migration

> "4D is not just a database—it's a complete application development platform including database, UI forms, methods, and business logic."

This skill guides migration from 4D applications to modern .NET 10 + SQL Server + Blazor architecture.

## Quick Start

1. **Gather 4D exports**: Structure export, method exports, form definitions
2. **Map schema**: Use `references/4d-to-sqlserver-typemap.md` for data type conversion
3. **Generate DDL**: Create SQL Server tables with proper constraints
4. **Generate entities**: Create EF Core entities using `references/4d-to-efcore-typemap.md`
5. **Plan UI migration**: Review forms using `references/4d-forms-to-blazor.md`
6. **Validate**: Run queries from `references/migration-validation-queries.md`

## Understanding 4D

4D (4th Dimension) is a **complete application platform**, not just a database:
- **Database engine**: Relational with proprietary data types
- **Forms designer**: Visual UI builder (similar to WinForms)
- **Methods**: Business logic in 4D language
- **Triggers**: Database triggers for validation
- **Users/Groups**: Built-in security model

Migration requires converting ALL components, not just the schema.

## Migration Process

### Step 1: Export 4D Structure

From 4D, export the structure file (usually `.4DB` or structure export):

```
# 4D structure exports typically include:
- Tables and fields
- Relations (foreign keys)
- Indexes
- Triggers
- Methods (code)
- Forms (UI)
```

### Step 2: Analyze Schema

```bash
# If you have a text export of the 4D structure:
# Look for table definitions
grep -E "^\[.*\]$|^Field_" 4d_structure.txt

# Identify relationships
grep -i "relation\|link\|many\|one" 4d_structure.txt

# Find index definitions
grep -i "index\|unique" 4d_structure.txt
```

### Step 3: Generate SQL Server DDL

For each 4D table, generate SQL Server CREATE TABLE:

```sql
-- Template for converted table
CREATE TABLE [dbo].[TableName] (
    [Id] INT IDENTITY(1,1) NOT NULL,
    -- Converted fields here
    [CreatedDate] DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    [ModifiedDate] DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    CONSTRAINT [PK_TableName] PRIMARY KEY CLUSTERED ([Id])
);
```

See `references/4d-to-sqlserver-typemap.md` for complete type mappings.

### Step 4: Generate EF Core Entities

```csharp
// Template for converted entity
public class EntityName
{
    public int Id { get; set; }
    // Properties mapped from 4D fields
    public DateTime CreatedDate { get; set; }
    public DateTime ModifiedDate { get; set; }

    // Navigation properties for relations
    public virtual ICollection<RelatedEntity> RelatedEntities { get; set; } = new List<RelatedEntity>();
}
```

See `references/4d-to-efcore-typemap.md` for C# type mappings.

### Step 5: Plan Form Migration

4D forms map to Blazor components. Common patterns:

| 4D Form Type | Blazor Equivalent |
|--------------|-------------------|
| Input form | Telerik Form with EditContext |
| List/Grid | TelerikGrid with OnRead |
| Dialog | TelerikWindow |
| Report | Telerik Report Viewer |
| Subform | Child component |

See `references/4d-forms-to-blazor.md` for detailed mappings.

### Step 6: Migrate Business Logic

4D methods become:
- **Validation logic** → FluentValidation validators
- **Business rules** → Command/Query handlers
- **Triggers** → EF Core interceptors or domain events
- **Calculated fields** → Computed columns or entity methods

### Step 7: Data Migration

```sql
-- Generate migration scripts for each table
-- See references/migration-validation-queries.md

-- Basic pattern:
INSERT INTO [NewDB].[dbo].[TableName] (Col1, Col2, ...)
SELECT
    CONVERT(TargetType, SourceCol1),
    CONVERT(TargetType, SourceCol2),
    ...
FROM [4DExport].[dbo].[SourceTable]
```

## Output Format

```markdown
## 4D Migration Analysis: [Application Name]

**Source**: 4D v[version]
**Target**: .NET 10 + SQL Server 2022 + Blazor
**Date**: [Analysis Date]

### Schema Summary

| Metric | Count |
|--------|-------|
| Tables | X |
| Relations | X |
| Methods | X |
| Forms | X |
| Estimated Entities | X |

### Tables to Migrate

| 4D Table | SQL Server Table | Entity Class | Status |
|----------|------------------|--------------|--------|
| ... | ... | ... | Pending/Complete |

### Type Mapping Issues

| 4D Field | 4D Type | Issue | Resolution |
|----------|---------|-------|------------|
| ... | ... | ... | ... |

### Form Migration Plan

| 4D Form | Blazor Component | Complexity |
|---------|------------------|------------|
| ... | ... | Low/Med/High |

### Business Logic Migration

| 4D Method | Target | Notes |
|-----------|--------|-------|
| ... | Handler/Service/Validator | ... |

### Data Migration Scripts

- [ ] Pre-migration validation queries
- [ ] Data transformation scripts
- [ ] Post-migration validation queries

### Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| ... | High/Med/Low | ... |
```

## Common 4D Patterns

See `references/common-4d-patterns.md` for:
- Auto-increment sequences
- Blob/Picture storage
- Multi-value fields
- Subtable patterns
- 4D date/time handling
- Character set considerations

## Validation Checklist

- [ ] All tables mapped to SQL Server
- [ ] All fields have correct type mappings
- [ ] All relationships preserved as foreign keys
- [ ] Indexes recreated appropriately
- [ ] Business logic identified and assigned to handlers
- [ ] Forms mapped to Blazor components
- [ ] Data migration scripts tested
- [ ] Row counts match source
- [ ] Key business reports validated

## References

- `references/4d-to-sqlserver-typemap.md` - Data type mappings to SQL Server
- `references/4d-to-efcore-typemap.md` - Data type mappings to C#/EF Core
- `references/common-4d-patterns.md` - Common 4D patterns and their .NET equivalents
- `references/4d-forms-to-blazor.md` - Form migration guidance
- `references/migration-validation-queries.md` - Validation queries for data integrity
