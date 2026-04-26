---
description: Runs the EF Core migration lifecycle with safety checks, rollback planning, and schema validation. Use when creating or applying EF Core migrations in .NET projects. Usage: /migrate <MigrationName>
allowed-tools: Bash(dotnet ef:*), Bash(dotnet build:*), Read
---

<migration_state>
!`dotnet ef migrations list 2>&1 | tail -20`
</migration_state>

Use the ef-migration-manager skill.
Migration name: $ARGUMENTS
Current migrations shown above. Run safety checks before applying.
Flag any data-loss risk and require explicit confirmation before proceeding.
