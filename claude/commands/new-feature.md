---
description: Scaffold a new vertical slice feature with CQRS + FreeMediator. Usage: /new-feature <FeatureName>
allowed-tools: Read, Write, Edit, Bash(dotnet build:*)
---

<project_structure>
!`find . -name "*.csproj" | head -10`
!`ls -la src/ 2>/dev/null || ls -la`
</project_structure>

Use the dotnet-vertical-slice skill to scaffold: $ARGUMENTS

Follow the existing project structure shown above.
Run dotnet build after scaffolding to confirm no compilation errors.
