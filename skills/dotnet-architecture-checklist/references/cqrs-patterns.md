# CQRS Patterns: FreeMediator + Mapster

## FreeMediator vs MediatR

**FreeMediator is the preferred CQRS library** for Denali projects:
- Apache 2.0 license (no commercial restrictions)
- API-compatible with MediatR
- Same `IRequest<T>`, `IRequestHandler<TRequest, TResponse>` interfaces
- Drop-in replacement with minimal code changes

### Migration from MediatR to FreeMediator

```bash
# 1. Check current MediatR usage
grep -r "MediatR" --include="*.csproj"
grep -r "using MediatR" --include="*.cs" | wc -l

# 2. Replace package reference in .csproj
# <PackageReference Include="MediatR" Version="12.x" />
# becomes:
# <PackageReference Include="FreeMediator" Version="1.x" />

# 3. Update using statements (usually just namespace change)
# using MediatR; → using FreeMediator;

# 4. Update DI registration
# services.AddMediatR(cfg => cfg.RegisterServicesFromAssembly(assembly));
# becomes:
# services.AddFreeMediator(assembly);
```

## FreeMediator Checks

### Structure
- [ ] One handler per file (not grouped)?
- [ ] Naming convention: `{Action}{Entity}Command/Query` + `Handler`?
- [ ] Commands in `Features/{Feature}/Commands/`?
- [ ] Queries in `Features/{Feature}/Queries/`?
- [ ] Using FreeMediator (not MediatR)?

### Registration
```bash
# Verify FreeMediator registration (preferred)
grep -r "AddFreeMediator" --include="*.cs"

# Check for MediatR (should migrate)
grep -r "AddMediatR" --include="*.cs"

# Check for missing handler registrations (handlers without interface)
grep -rL "IRequestHandler\|INotificationHandler" --include="*Handler.cs"
```

### Pipeline Behaviors
- [ ] Validation behavior registered before handler execution?
- [ ] Logging behavior captures request/response?
- [ ] Exception handling behavior present?
- [ ] Transaction behavior wraps commands (not queries)?

```bash
# Find pipeline behaviors
grep -r "IPipelineBehavior\|IBehavior" --include="*.cs"
```

### Handler Patterns
- [ ] Handlers are async all the way?
- [ ] No business logic in controllers—just `Send()`?
- [ ] Queries return DTOs, not entities?
- [ ] Commands return result types (not void)?

```bash
# Controllers should only call Send()
grep -rA10 "public.*IActionResult\|public.*ActionResult" --include="*Controller.cs" | \
  grep -v "Send(\|Publish("

# Handlers returning entities (should be DTOs)
grep -r "Task<.*Entity>\|Task<List<.*Entity>>" --include="*Handler.cs"
```

### Anti-Patterns
```bash
# Handler calling another handler (use events instead)
grep -r "IMediator\|ISender" --include="*Handler.cs"

# Commands with "Get" in name (should be Query)
grep -r "class Get.*Command" --include="*.cs"

# Queries with side effects
grep -r "SaveChanges\|Add(\|Remove(\|Update(" --include="*Query*.cs"
```

---

## Mapster Checks

### Configuration
- [ ] `TypeAdapterConfig.GlobalSettings` configured at startup?
- [ ] Mapping profiles in dedicated classes?
- [ ] Compile-time code generation enabled for perf?

```bash
# Find Mapster config
grep -r "TypeAdapterConfig\|MapsterConfig" --include="*.cs"

# Check for inline mapping config (should be centralized)
grep -r "\.NewConfig()\|\.ForType<" --include="*Handler.cs" --include="*Controller.cs"
```

### EF Core Integration
- [ ] Using `ProjectToType<>()` for queries (not `Adapt()` after materialization)?
- [ ] No `.ToList().Adapt()` pattern (causes full entity load)?

```bash
# Bad: materialize then map
grep -r "\.ToList()\.Adapt\|\.ToArray()\.Adapt" --include="*.cs"

# Good: project in query
grep -r "ProjectToType<" --include="*.cs"
```

### Mapping Profiles
- [ ] Profiles organized by feature/domain?
- [ ] Complex mappings documented?
- [ ] Two-way mappings explicit (not assumed)?

```bash
# Find all mapping registrations
grep -r "config.NewConfig<\|TypeAdapterConfig.*\.NewConfig" --include="*.cs"

# Check for unmapped properties (requires runtime)
# Add to startup: TypeAdapterConfig.GlobalSettings.RequireExplicitMapping = true;
```

### Anti-Patterns
```bash
# Mapping in loops (should batch)
grep -rB5 "foreach\|for.*(" --include="*.cs" | grep -A5 "\.Adapt<"

# Generic Adapt without type (risky)
grep -r "\.Adapt()" --include="*.cs"

# Mapping entities to entities (domain leak)
grep -r "\.Adapt<.*Entity>" --include="*.cs"
```

---

## Vertical Slice Validation

### Feature Cohesion
```bash
# Each feature folder should have Commands/, Queries/, and DTOs
find . -type d -name "Features" -exec ls -la {} \;

# Handlers outside Features folder (misplaced)
find . -path "*/Features" -prune -o -name "*Handler.cs" -print
```

### Dependency Direction
```bash
# Features referencing other features (coupling)
for f in $(find . -path "*/Features/*" -name "*.cs"); do
  feature=$(echo $f | grep -oP "Features/\K[^/]+")
  grep -l "Features\." $f | grep -v "Features\.$feature" 
done
```

---

## Quick Structural Check

Expected vertical slice structure:
```
Features/
├── Users/
│   ├── Commands/
│   │   ├── CreateUser/
│   │   │   ├── CreateUserCommand.cs
│   │   │   ├── CreateUserHandler.cs
│   │   │   └── CreateUserValidator.cs
│   │   └── UpdateUser/
│   │       └── ...
│   ├── Queries/
│   │   └── GetUserById/
│   │       ├── GetUserByIdQuery.cs
│   │       ├── GetUserByIdHandler.cs
│   │       └── UserDto.cs
│   └── UserMappingConfig.cs
└── ...
```

Verify with:
```bash
find . -path "*/Features/*" -type f -name "*.cs" | \
  sed 's|/[^/]*$||' | sort -u | head -20
```
