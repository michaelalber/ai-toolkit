# Architecture Review Checklist

## 0. Framework & Dependencies Pre-Check

### Target Framework
- [ ] Using .NET 10 LTS (preferred) or .NET 8 LTS?
- [ ] No .NET Framework 4.x projects without upgrade plan?
- [ ] No EOL frameworks (netcoreapp3.1, net5, net7)?
- [ ] SDK-style project files (not legacy)?

```bash
# Quick framework scan
grep -r "<TargetFramework" --include="*.csproj" | grep -oE "net[0-9]+\.[0-9]+|netcoreapp[0-9]+\.[0-9]+|net4[0-9]+" | sort -u
```

### Mediator Library
- [ ] Using FreeMediator (preferred over MediatR)?
- [ ] If MediatR, migration plan documented?

```bash
# Check mediator library
grep -r "FreeMediator\|MediatR" --include="*.csproj"
```

### Shared Kernel (LANL Projects)
- [ ] Using `Denali.LANL.*` shared packages where applicable?
- [ ] All shared packages on consistent version?
- [ ] No duplicate definitions of shared entities (Person, Organization, Location, etc.)?

```bash
# Check shared kernel usage
grep -rE "Denali\.LANL\." --include="*.csproj"
```

## 1. Solution Structure & Patterns
- [ ] Project organization: vertical slices vs layered?
- [ ] Dependency direction: pointing inward?
- [ ] CQRS/Mediator: appropriate boundaries?
- [ ] Feature cohesion: related code grouped?

## 1a. CQRS with FreeMediator (if applicable)
- [ ] Using FreeMediator (not MediatR)?
- [ ] One handler per file?
- [ ] Commands vs Queries properly separated?
- [ ] Pipeline behaviors: validation, logging, transactions?
- [ ] Handlers async all the way?
- [ ] No handler-to-handler calls (use events)?
- [ ] Controllers only call `Send()`—no business logic?
- [ ] Result types used (not void for commands)?
See `references/cqrs-patterns.md` for detailed checks.

## 1b. Mapster (if applicable)
- [ ] TypeAdapterConfig at startup (not per-request)?
- [ ] Using `ProjectToType<>()` for EF queries?
- [ ] No `.ToList().Adapt()` pattern?
- [ ] Mapping profiles organized by feature?
See `references/cqrs-patterns.md` for detailed checks.

## 2. Blazor Hosting & Reliability

### Blazor Server
- [ ] SignalR circuit management: reconnection strategy?
- [ ] Pod/AppService restart: state recovery plan?
- [ ] Distributed backplane: Redis/Azure SignalR configured?
- [ ] Circuit timeout settings appropriate?

### Blazor WASM
- [ ] IL trimming enabled?
- [ ] AOT compilation evaluated?
- [ ] TTI meets Core Web Vitals (<3.8s)?
- [ ] Service worker caching strategy?

### Interactive Auto (.NET 8+)
- [ ] Render mode boundaries clear?
- [ ] Prerendering state persistence?

## 3. State Management
- [ ] State location: circuit memory vs distributed store?
- [ ] Memory bloat risk: per-user session footprint estimated?
- [ ] `IDisposable` implemented where needed?
- [ ] Cascading parameters: minimal and justified?

## 4. Data Access
- [ ] DbContext lifetime: scoped correctly for circuits?
- [ ] N+1 queries: projections used?
- [ ] Connection pooling: sized for long-lived circuits?
- [ ] Async all the way down?

## 5. Security
- [ ] Auth pattern: BFF, direct API, or hybrid?
- [ ] No secrets in WASM bundles?
- [ ] `AuthenticationStateProvider` properly implemented?
- [ ] Policy-based authorization?
- [ ] Input sanitization: XSS prevention?
- [ ] CORS configured correctly?

## 6. API Design
- [ ] REST conventions: proper verbs, status codes?
- [ ] DTOs: no domain leakage?
- [ ] ProblemDetails for errors?
- [ ] Versioning strategy?

## 7. Observability
- [ ] OpenTelemetry integration?
- [ ] Metrics: SignalR vs DB vs render latency separated?
- [ ] Structured logging with correlation IDs?
- [ ] Health checks: liveness vs readiness?

## 8. Dependency Injection
- [ ] Scoped services: circuit lifetime understood?
- [ ] `OwningComponentBase` where needed?
- [ ] No service locator anti-pattern?

## 9. Testability
- [ ] bUnit coverage for components?
- [ ] Integration tests for SignalR scenarios?
- [ ] Mocking boundaries defined?

## 10. Performance
- [ ] `ShouldRender()` overridden where beneficial?
- [ ] Virtualization for large lists?
- [ ] `@key` directive used in loops?
- [ ] Lazy loading for heavy components?

## 11. Telerik UI for Blazor

### Data Binding
- [ ] Grid uses `OnRead` with `ToDataSourceResult()` for large data?
- [ ] Not mixing `Data` parameter with `OnRead`?
- [ ] Debounced filtering/searching?

### Component Config
- [ ] `TelerikRootComponent` in correct layout position?
- [ ] Virtual scrolling enabled (`ScrollMode="Virtual"`)?
- [ ] Grid state persisted externally?

### Memory & Disposal
- [ ] Popup/Window components disposed properly?
- [ ] No unnecessary re-renders from parent state?

### Theming
- [ ] Single theme CSS loaded?
- [ ] No conflicts with CSS isolation?
- [ ] Custom theme via ThemeBuilder (not inline)?

### Forms
- [ ] `TelerikValidationSummary` with `EditContext`?
- [ ] `@bind-Value` used consistently?
- [ ] TelerikEditor: XSS sanitization enabled?

### Build & Licensing
- [ ] Telerik private NuGet feed in CI/CD?
- [ ] License file excluded from source control?
- [ ] All Telerik packages same version?

### Performance Red Flags
- [ ] Nested Grids: impact assessed?
- [ ] Charts with live data: throttled?
- [ ] Scheduler/Gantt: date-range windowing?
