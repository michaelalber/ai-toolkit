---
description: EF Core migration with safety checks. Usage: /migrate <MigrationName>
agent: build
subtask: false
---

<migration_state>
!`dotnet ef migrations list 2>&1 | tail -20`
</migration_state>

Use the ef-migration-manager skill.
Migration name: $ARGUMENTS
Current migrations shown above. Run safety checks before applying.
Flag any data-loss risk and require explicit confirmation before proceeding.
