# Red Flags Quick Reference

Fast pattern matching for common anti-patterns. Use `grep` or IDE search.

## Critical (Fix Immediately)

```bash
# .NET Framework 4.x (needs upgrade to .NET 10)
grep -rE "<TargetFramework>net4[0-9]+</TargetFramework>" --include="*.csproj"

# EOL frameworks (upgrade immediately)
grep -rE "<TargetFramework>(netcoreapp3\.[0-9]+|net5\.0|net7\.0)</TargetFramework>" --include="*.csproj"

# Legacy project file format (needs SDK-style conversion)
find . -name "*.csproj" -exec grep -L "Sdk=" {} \;

# Singleton DbContext - causes connection issues
grep -r "AddSingleton<.*DbContext" --include="*.cs"

# Hardcoded secrets
grep -rE "(password|secret|apikey|connectionstring)\s*=\s*\"[^\"]+\"" --include="*.cs" -i

# Sync over async
grep -r "\.Result" --include="*.cs"
grep -r "\.Wait()" --include="*.cs"
grep -r "Task\.Run.*\.Result" --include="*.cs"

# Memory leaks - missing disposal
grep -r "class.*:.*ComponentBase" --include="*.cs" | xargs -I{} grep -L "IDisposable" {}
```

## High (Address Soon)

```bash
# Telerik Grid loading full dataset
grep -r "Data=\"@" --include="*.razor" | grep -i grid

# N+1 query patterns (Include missing)
grep -r "\.Select.*\.ToList\|\.Select.*\.ToArray" --include="*.cs"

# Cascading parameter overuse
grep -r "\[CascadingParameter\]" --include="*.cs" | wc -l
# If >10, review necessity

# State stored in circuit
grep -r "private.*List<\|private.*Dictionary<" --include="*.razor"
```

## Medium (Technical Debt)

```bash
# Missing async suffix
grep -r "public.*Task<" --include="*.cs" | grep -v "Async("

# Direct HttpClient usage (should use IHttpClientFactory)
grep -r "new HttpClient()" --include="*.cs"

# Magic strings
grep -rE "\"[A-Za-z]{10,}\"" --include="*.cs" | grep -v "//\|nameof\|const"

# Empty catch blocks
grep -rA2 "catch\s*(" --include="*.cs" | grep -B1 "{\s*}"
```

## Telerik-Specific

```bash
# Multiple theme CSS (should be one)
grep -r "telerik.*\.css" --include="*.html" --include="*.razor" | wc -l

# Missing TelerikRootComponent
grep -rL "TelerikRootComponent" --include="MainLayout.razor"

# Version mismatch check
grep -r "Telerik" --include="*.csproj" | grep -oE "[0-9]+\.[0-9]+\.[0-9]+" | sort -u
# If multiple versions, needs alignment

# Grid without OnRead (for large data)
grep -rB5 -A5 "TelerikGrid" --include="*.razor" | grep -v "OnRead"
```

## Security

```bash
# API keys in WASM
find . -path "*/Client/*" -name "*.cs" | xargs grep -l "ApiKey\|Secret\|Bearer"

# Missing authorization attributes
grep -r "public.*Controller" --include="*.cs" | xargs -I{} grep -L "\[Authorize\]" {}

# AllowAnonymous on sensitive endpoints
grep -rB5 "\[AllowAnonymous\]" --include="*.cs" | grep -E "Delete|Update|Create|Admin"
```

## Project Structure

```bash
# Circular dependency hints
find . -name "*.csproj" -exec grep -l "ProjectReference" {} \; | \
  xargs -I{} sh -c 'echo "=== {} ===" && grep "ProjectReference" {}'

# Missing test projects
find . -name "*.csproj" | grep -i test | wc -l
# If 0, flag missing tests
```

## CQRS / FreeMediator / Mapster

```bash
# Using MediatR instead of FreeMediator (consider migration)
grep -r "MediatR" --include="*.csproj"
grep -r "AddMediatR" --include="*.cs"

# Handler calling another handler (should use events)
grep -r "IMediator\|ISender" --include="*Handler.cs"

# Commands named like queries
grep -r "class Get.*Command" --include="*.cs"

# Queries with side effects (writes in query handlers)
grep -r "SaveChanges\|\.Add(\|\.Remove(" --include="*Query*.cs"

# Business logic in controllers (should only call Send)
grep -rA10 "public.*IActionResult" --include="*Controller.cs" | grep -v "Send(\|Publish("

# Mapster: materialize then map (perf issue)
grep -r "\.ToList()\.Adapt\|\.ToArray()\.Adapt" --include="*.cs"

# Mapster: inline config outside startup (should centralize)
grep -r "\.NewConfig()\|\.ForType<" --include="*Handler.cs" --include="*Controller.cs"

# Handlers returning entities instead of DTOs
grep -r "Task<.*Entity>\|Task<List<.*Entity>>" --include="*Handler.cs"
```

## Shared Kernel (LANL Projects)

```bash
# Duplicated entities that should come from shared kernel
grep -r "class Person\|class Employee\|class Organization\|class Location" --include="*.cs" | grep -v "Denali\.LANL\."

# Inconsistent shared package versions
grep -r "Denali.LANL" --include="*.csproj" | grep -oE "[0-9]+\.[0-9]+\.[0-9]+" | sort -u
# If multiple versions shown, needs alignment

# Missing shared kernel references (check if domain entities are locally defined)
find . -name "*.cs" -exec grep -l "class Person\|class Training\|class Organization" {} \; | head -10
```
