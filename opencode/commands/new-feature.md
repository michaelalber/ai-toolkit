---
description: Scaffold a new vertical slice feature. Usage: /new-feature <FeatureName>
agent: build
subtask: false
---

<project_structure>
!`find . -name "*.csproj" | head -10`
!`ls -la src/ 2>/dev/null || ls -la`
</project_structure>

Use the dotnet-vertical-slice skill to scaffold: $ARGUMENTS

Follow the existing project structure shown above.
Run dotnet build after scaffolding to confirm no compilation errors.
