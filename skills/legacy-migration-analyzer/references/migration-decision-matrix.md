# Migration Decision Matrix

## Overview

This reference provides structured decision frameworks for planning .NET Framework to .NET 10 migrations. Use these matrices to determine the migration approach, estimate effort, assess risk, and plan incremental execution.

---

## 1. Migration Approach Decision Tree

### Primary Decision: Which Strategy?

There are three core migration strategies. The right choice depends on the codebase characteristics identified during the SCAN phase.

```
START
  |
  v
Is the application a single deployable unit (monolith)?
  |
  +-- YES --> Is total LOC under 50,000?
  |             |
  |             +-- YES --> Are there hard blockers (WCF server, COM-heavy)?
  |             |             |
  |             |             +-- YES --> STRANGLER FIG
  |             |             +-- NO  --> IN-PLACE UPGRADE
  |             |
  |             +-- NO  --> Can the monolith be decomposed into
  |                         independent modules?
  |                           |
  |                           +-- YES --> PHASED DECOMPOSITION
  |                           +-- NO  --> STRANGLER FIG
  |
  +-- NO (multi-project solution)
        |
        v
      Are all projects migratable (no hard blockers)?
        |
        +-- YES --> PROJECT-BY-PROJECT UPGRADE
        |           (leaf nodes first in dependency graph)
        |
        +-- NO  --> Can blocked projects be isolated
                    behind API boundaries?
                      |
                      +-- YES --> HYBRID (migrate what you can,
                      |           keep blockers on .NET Framework,
                      |           communicate via HTTP/gRPC/messages)
                      |
                      +-- NO  --> STRANGLER FIG with
                                  long-term coexistence plan
```

### Strategy Definitions

#### In-Place Upgrade

**What**: Convert the existing solution to .NET 10 project-by-project, updating code in the same repository and deployment pipeline.

**When to use**:
- Solution is under 50K LOC
- No hard blockers (all dependencies are compatible)
- Team has .NET 10 experience
- Downtime for cutover is acceptable

**Advantages**:
- Simplest conceptually
- Single codebase throughout
- No inter-process communication overhead

**Risks**:
- "Big bang" cutover moment
- All-or-nothing for deployment
- Difficult to parallelize work

**Typical timeline**: 2-8 weeks for small solutions

#### Strangler Fig

**What**: Build new functionality in .NET 10 alongside the legacy system. Gradually route traffic from old to new. Eventually decommission the legacy system.

**When to use**:
- Large or complex codebase
- Hard blockers exist that need architectural workarounds
- Continuous delivery is required during migration
- Risk tolerance is low (need incremental validation)

**Advantages**:
- Zero downtime migration
- Incremental value delivery
- Easy rollback (just route traffic back)
- Can run old and new simultaneously

**Risks**:
- Longer total timeline
- Requires routing infrastructure (API gateway, reverse proxy)
- Temporary duplication of some functionality
- Must maintain two systems during transition

**Typical timeline**: 3-12 months depending on size

#### Hybrid Coexistence

**What**: Migrate most of the solution to .NET 10 but keep specific components on .NET Framework permanently or long-term, communicating via APIs, message queues, or shared databases.

**When to use**:
- Specific components cannot be migrated (COM dependencies, legacy protocols)
- The cost of migrating those components exceeds their value
- The organization accepts long-term maintenance of a .NET Framework component

**Advantages**:
- Pragmatic: migrates what can be migrated
- Unblocks the majority of the codebase
- Does not require solving every hard blocker

**Risks**:
- Permanent operational complexity (two runtimes)
- Inter-process communication adds latency and failure modes
- .NET Framework components still need patching and maintenance

**Typical timeline**: 2-6 months for the migrated portion; indefinite for the legacy remainder

---

## 2. Risk Scoring Framework

### Project-Level Risk Score

Score each project on a 0-10 scale across five dimensions. The weighted sum produces the project risk score.

```
+------------------------------------------------------------+
| Project Risk Scorecard                                      |
+------------------------------------------------------------+
| Dimension              | Weight | Score (0-10) | Weighted  |
|------------------------|--------|--------------|-----------|
| Hard Blockers          |   30%  |    [___]     |  [___]    |
| Dependency Compat.     |   25%  |    [___]     |  [___]    |
| Framework API Usage    |   20%  |    [___]     |  [___]    |
| Test Coverage Gap      |   15%  |    [___]     |  [___]    |
| Code Complexity        |   10%  |    [___]     |  [___]    |
|------------------------|--------|--------------|-----------|
| TOTAL                  |  100%  |              |  [___]    |
+------------------------------------------------------------+
```

### Scoring Guide: Hard Blockers (30%)

| Score | Description |
|-------|-------------|
| 0 | No blockers. All features have a clear .NET 10 equivalent. |
| 2 | Minor blockers. One or two APIs need workarounds but solutions are documented. |
| 4 | Moderate blockers. A key dependency (e.g., WCF) requires CoreWCF or equivalent. |
| 6 | Significant blockers. Multiple features rely on Windows-specific APIs with no cross-platform path. |
| 8 | Major blockers. Core functionality depends on COM interop, MSMQ, or undocumented protocols. |
| 10 | Show-stopper. The project fundamentally cannot run on .NET 10 without a rewrite. |

### Scoring Guide: Dependency Compatibility (25%)

| Score | Description |
|-------|-------------|
| 0 | All NuGet packages have .NET 10 compatible versions. Zero incompatibilities. |
| 2 | 1-2 packages need version upgrades with minor breaking changes. |
| 4 | 3-5 packages need upgrades, some with moderate API changes. |
| 6 | 5-10 packages need upgrades or replacements. At least one requires significant code changes. |
| 8 | More than 10 packages need attention. Multiple packages have no .NET 10 version. |
| 10 | Critical packages (ORM, DI container, web framework) are incompatible with no replacement. |

### Scoring Guide: Framework API Usage (20%)

| Score | Description |
|-------|-------------|
| 0 | No `System.Web`, `System.ServiceModel`, or Windows-specific API usage. Pure business logic. |
| 2 | Minimal `System.Web` usage (under 10 references). Configuration access only. |
| 4 | Moderate `System.Web` usage (10-50 references). Includes `HttpContext.Current` access. |
| 6 | Heavy `System.Web` usage (50-100 references). Includes custom HTTP modules or handlers. |
| 8 | Pervasive `System.Web` usage (100+ references). Application is tightly coupled to IIS pipeline. |
| 10 | The project IS the framework (custom `HttpApplication`, ISAPI filters, native modules). |

### Scoring Guide: Test Coverage Gap (15%)

| Score | Description |
|-------|-------------|
| 0 | Comprehensive test suite (80%+ coverage on business logic). All critical paths tested. |
| 2 | Good coverage (60-80%). Most business logic has tests. |
| 4 | Moderate coverage (40-60%). Key features tested but gaps exist. |
| 6 | Low coverage (20-40%). Only happy paths tested. |
| 8 | Minimal coverage (under 20%). Sporadic tests, no systematic testing. |
| 10 | No tests. Zero coverage. Migration will be blind. |

### Scoring Guide: Code Complexity (10%)

| Score | Description |
|-------|-------------|
| 0 | Simple, well-structured code. Clear separation of concerns. Under 5K LOC. |
| 2 | Clean code with some complexity. 5-15K LOC. |
| 4 | Moderate complexity. Some large classes or deep inheritance. 15-30K LOC. |
| 6 | Complex. Tight coupling, large methods, mixed concerns. 30-50K LOC. |
| 8 | Highly complex. God classes, circular dependencies, no clear architecture. 50-100K LOC. |
| 10 | Unmaintainable. No discernible architecture, massive files, undocumented behavior. 100K+ LOC. |

### Solution-Level Risk Score

Aggregate project scores using a weighted average based on project size (LOC) or criticality:

```
Solution Risk = SUM(Project_Risk * Project_Weight) / SUM(Project_Weight)

Where Project_Weight = Project_LOC / Total_LOC
  (or assign weights by business criticality)
```

### Risk Level Interpretation

| Total Score | Risk Level | Typical Duration | Recommendation |
|-------------|-----------|------------------|----------------|
| 0.0 - 2.0 | **Low** | 2-4 weeks | In-place upgrade. Low ceremony. |
| 2.1 - 4.0 | **Medium** | 1-3 months | In-place with targeted remediation. Plan for package upgrades and some API replacements. |
| 4.1 - 6.0 | **High** | 3-6 months | Strangler fig or phased approach. Significant prerequisite work needed. |
| 6.1 - 8.0 | **Critical** | 6-12 months | Major effort. Consider hybrid coexistence. Dedicated migration team recommended. |
| 8.1 - 10.0 | **Extreme** | 12+ months | Fundamental architectural challenges. Re-evaluate whether migration is the right investment. |

---

## 3. Dependency Compatibility Assessment

### Assessment Workflow

```
For each NuGet package in the solution:
  |
  v
1. Check nuget.org for .NET 10 compatible version
     |
     +-- Compatible version exists
     |     |
     |     v
     |   Are there breaking changes between current and compatible version?
     |     |
     |     +-- No  --> GREEN: Direct upgrade
     |     +-- Yes --> YELLOW: Upgrade with code changes
     |
     +-- No compatible version
           |
           v
         Is the package actively maintained?
           |
           +-- Yes --> Check GitHub issues/roadmap for .NET 10 plans
           |             |
           |             +-- Planned --> YELLOW: Wait or use preview
           |             +-- Not planned --> RED: Find replacement
           |
           +-- No (abandoned)
                 |
                 v
               Is the functionality available in .NET 10 BCL?
                 |
                 +-- Yes --> GREEN: Remove package, use built-in
                 +-- No  --> Is there an alternative package?
                               |
                               +-- Yes --> YELLOW: Replace package
                               +-- No  --> RED: Custom implementation
                                           or architectural workaround
```

### Compatibility Status Categories

| Status | Symbol | Meaning | Action Required |
|--------|--------|---------|-----------------|
| **Green** | Compatible | Package works on .NET 10 as-is or with version bump | Update version in csproj |
| **Yellow** | Needs Work | Package has a compatible version but with breaking API changes | Update code to match new API |
| **Red** | Incompatible | No .NET 10 compatible version exists | Replace with alternative or build custom |
| **Gray** | Unknown | Cannot determine compatibility; insufficient information | Manual testing required |

### Common Dependency Migration Paths

| Category | .NET Framework Dependency | .NET 10 Path | Status |
|----------|--------------------------|--------------|--------|
| **DI Container** | Unity 5.x | Microsoft.Extensions.DI (built-in) | Yellow |
| **DI Container** | Autofac 4.x | Autofac 7.x + Extensions.DI integration | Yellow |
| **DI Container** | StructureMap | Lamar (successor) | Yellow |
| **DI Container** | Castle.Windsor 5.x | Castle.Windsor 6.x | Yellow |
| **DI Container** | Ninject | Microsoft.Extensions.DI (built-in) | Yellow |
| **Logging** | log4net 2.x | Serilog or NLog (via ILogger) | Yellow |
| **Logging** | NLog 4.x | NLog 5.x + NLog.Web.AspNetCore | Yellow |
| **Logging** | ELMAH | Serilog + centralized logging | Red |
| **ORM** | EF6 | EF Core 9+ | Yellow |
| **ORM** | NHibernate 5.x | NHibernate 5.5+ (compatible) | Green |
| **ORM** | Dapper 1.x | Dapper 2.x | Green |
| **Validation** | FluentValidation 8.x | FluentValidation 11.x | Yellow |
| **Mapping** | AutoMapper 10.x | AutoMapper 13.x | Yellow |
| **HTTP** | RestSharp 106.x | HttpClient (built-in) or RestSharp 110.x | Yellow |
| **Caching** | System.Runtime.Caching | Microsoft.Extensions.Caching | Yellow |
| **Serialization** | Newtonsoft.Json | System.Text.Json or keep Newtonsoft | Green |
| **Scheduling** | Quartz.NET 3.x | Quartz.NET 3.8+ + hosting integration | Green |
| **Scheduling** | Hangfire 1.7 | Hangfire 1.8+ | Green |
| **Messaging** | NServiceBus 7.x | NServiceBus 9.x | Yellow |
| **Messaging** | MassTransit 7.x | MassTransit 8.x | Yellow |

---

## 4. Timeline Estimation Factors

### Base Effort Per Project Type

| Project Type | Base Effort (developer-days) | Notes |
|-------------|------------------------------|-------|
| Class Library (no framework deps) | 1-3 | Usually trivial: update TFM, fix compilation errors |
| Class Library (with framework deps) | 3-10 | Depends on which APIs are used |
| Console Application | 2-5 | Hosting model change + dependency updates |
| ASP.NET Web API | 10-30 | Controller migration + startup rewrite |
| ASP.NET MVC | 15-40 | Views + controllers + middleware |
| ASP.NET MVC + Web API (mixed) | 20-50 | Unified framework migration |
| WCF Service (to CoreWCF) | 10-25 | Configuration + hosting changes |
| WCF Service (to gRPC) | 20-40 | Contract redesign + client updates |
| WCF Service (to REST) | 15-35 | API design + client updates |
| Windows Service | 5-10 | Worker Service conversion |
| WinForms Application | 5-15 | Usually straightforward if Windows-only |
| WPF Application | 5-15 | Usually straightforward if Windows-only |

### Multipliers

Apply these multipliers to the base effort:

| Factor | Multiplier | Condition |
|--------|-----------|-----------|
| Test Coverage < 40% | 1.5x | Must write characterization tests first |
| Test Coverage < 20% | 2.0x | Significant test authoring effort |
| No tests at all | 2.5x | Full characterization test suite needed |
| Heavy System.Web usage (100+ refs) | 1.5x | Extensive API replacement work |
| Custom authentication | 1.3x | Security migration requires extra care |
| COM Interop present | 1.5x | Wrapper development and testing |
| Database schema migration | 1.3x | Coordinate with ef-migration-manager |
| Large solution (20+ projects) | 1.2x | Integration testing overhead |
| Team is new to .NET 10 | 1.3x | Learning curve and ramp-up time |
| Parallel development continues | 1.4x | Merge conflicts and dual maintenance |

### Estimation Formula

```
Project_Effort = Base_Effort * PRODUCT(applicable multipliers)

Solution_Effort = SUM(Project_Effort) + Integration_Testing_Buffer

Integration_Testing_Buffer = 0.15 * SUM(Project_Effort)
                             (15% overhead for cross-project integration testing)

Total_Duration = Solution_Effort / Team_Size * Parallelism_Factor

Parallelism_Factor:
  - Serial (1 dev on migration): 1.0
  - 2 devs in parallel: 0.55 (some coordination overhead)
  - 3-4 devs in parallel: 0.35 (more coordination overhead)
  - 5+ devs in parallel: 0.25 (significant coordination overhead)
```

### Example Estimation

```
Solution: 8 projects
  - 3 class libraries (no framework deps): 3 * 2 = 6 days
  - 1 class library (with System.Web refs): 1 * 7 = 7 days
  - 1 ASP.NET MVC + Web API:               1 * 35 = 35 days
  - 1 WCF service (to gRPC):               1 * 30 = 30 days
  - 1 Windows Service:                     1 * 7 = 7 days
  - 1 Console App:                         1 * 3 = 3 days

Subtotal: 88 days

Multipliers:
  - Test coverage at 35%: * 1.5 = 132 days
  - Team is new to .NET 10: * 1.3 = 171.6 days

Integration buffer: 171.6 * 0.15 = 25.7 days

Total effort: 197.3 developer-days

With 2 developers: 197.3 * 0.55 = 108.5 calendar days
                    = approximately 5 months
```

---

## 5. Team Skill Assessment

### Required Skills Inventory

Before beginning migration, assess whether the team has these skills:

```
+--------------------------------------------------------------+
| Team Skill Assessment                                         |
+--------------------------------------------------------------+
| Skill                          | Have? | Gap Action           |
|--------------------------------|-------|----------------------|
| .NET 10 / C# modern syntax    | [ ]   | Training / pairing   |
| ASP.NET Core middleware        | [ ]   | Workshop             |
| Dependency Injection (built-in)| [ ]   | Documentation review |
| EF Core (if using EF)         | [ ]   | EF Core tutorial     |
| gRPC (if replacing WCF)       | [ ]   | Protobuf training    |
| Docker / containers           | [ ]   | DevOps workshop      |
| CI/CD with .NET 10             | [ ]   | Pipeline setup guide |
| appsettings.json / Options     | [ ]   | Quick migration      |
| Minimal API / endpoint routing | [ ]   | Documentation review |
| OpenTelemetry / diagnostics    | [ ]   | Observability guide  |
+--------------------------------------------------------------+
```

### Skill Gap Impact on Timeline

| Gap Level | Description | Timeline Impact |
|-----------|-------------|----------------|
| **None** | Team has shipped .NET 10 apps before | No impact |
| **Low** | Team knows .NET Core/5/6 but not .NET 10 specifically | Add 5-10% buffer |
| **Medium** | Team knows .NET Framework well but limited .NET Core experience | Add 20-30% buffer + training sprint |
| **High** | Team primarily works in other languages; .NET Framework is legacy skill | Add 40-50% buffer + formal training |

---

## 6. Incremental Migration Strategies

### Strategy A: Project-by-Project (Dependency Order)

**Best for**: Multi-project solutions where all projects can be migrated.

```
Step 1: Build dependency graph of all projects in solution
Step 2: Identify leaf nodes (projects with no project references)
Step 3: Migrate leaf nodes first
Step 4: Work inward toward the root (entry point) project
Step 5: Migrate the entry point project last

Dependency Graph Example:

    WebApp (ASP.NET MVC)          <-- Migrate LAST (Phase 4)
       |         |
       v         v
    Services    API.Client        <-- Migrate Phase 3
       |         |
       v         v
    Domain      Shared.Models     <-- Migrate Phase 2
       |
       v
    Domain.Contracts              <-- Migrate FIRST (Phase 1)
```

**Multi-targeting during transition:**

While migrating project-by-project, intermediate projects may need to support both frameworks:

```xml
<!-- In .csproj for projects being consumed by both migrated and unmigrated projects -->
<PropertyGroup>
  <TargetFrameworks>net48;net10.0</TargetFrameworks>
</PropertyGroup>

<!-- Conditional compilation for framework-specific code -->
#if NET10_0_OR_GREATER
    // .NET 10 implementation
#elif NETFRAMEWORK
    // .NET Framework implementation
#endif
```

### Strategy B: Feature-by-Feature (Strangler Fig)

**Best for**: Monolithic applications where decomposition is needed.

```
Step 1: Identify a bounded context or feature that can be extracted
Step 2: Build the feature as a new .NET 10 service
Step 3: Set up routing (reverse proxy / API gateway) to direct
        traffic for that feature to the new service
Step 4: Validate that the new service handles all cases correctly
Step 5: Remove the feature from the legacy application
Step 6: Repeat for the next feature

Traffic Flow:

    Client Request
         |
         v
    +-- Reverse Proxy / API Gateway --+
    |                                  |
    |   /api/orders/*                  |   /api/customers/*
    |   (new .NET 10 service)          |   (legacy .NET Framework)
    |                                  |
    v                                  v
  +-------------------+    +-------------------------+
  | Orders Service    |    | Legacy Monolith         |
  | (.NET 10)         |    | (.NET Framework 4.8)    |
  +-------------------+    +-------------------------+
```

**Routing infrastructure options:**

| Tool | Use Case | Complexity |
|------|----------|-----------|
| YARP (Yet Another Reverse Proxy) | .NET-native reverse proxy | Low |
| Nginx | General-purpose reverse proxy | Low |
| Azure API Management | Cloud-native API gateway | Medium |
| Kong | Feature-rich API gateway | Medium |
| AWS ALB Path-Based Routing | AWS deployments | Low |
| Kubernetes Ingress | Container orchestration | Medium |

### Strategy C: Layer-by-Layer

**Best for**: Well-layered applications where horizontal slicing is natural.

```
Phase 1: Data Access Layer
  - Migrate repositories, EF context, data models
  - Multi-target the data layer project
  - Validate with integration tests against the same database

Phase 2: Business Logic Layer
  - Migrate services, domain logic, validators
  - These should be framework-agnostic after Phase 1

Phase 3: Presentation Layer
  - Migrate controllers, views, API endpoints
  - This is where ASP.NET to ASP.NET Core changes hit

Phase 4: Infrastructure Layer
  - Migrate hosting, configuration, logging, monitoring
  - Update deployment pipeline
```

### Strategy D: Hybrid with Shared Database

**Best for**: When some components cannot be migrated but must share state.

```
+-------------------+        +-------------------+
| .NET 10 Service   |        | .NET Framework    |
| (new features)    |        | (legacy features) |
+-------------------+        +-------------------+
         |                            |
         v                            v
    +----------------------------------------+
    |          Shared Database                |
    |  (EF Core and EF6 both connect here)   |
    +----------------------------------------+

CAUTION: This strategy requires careful coordination:
  - Both applications must agree on schema
  - Migration ownership must be clearly assigned
  - Concurrent access patterns must be understood
  - Transaction boundaries must be respected
```

---

## 7. Go / No-Go Decision Checklist

### Before Starting Migration (Go / No-Go Gate)

```
+--------------------------------------------------------------+
| Migration Go / No-Go Checklist                                |
+--------------------------------------------------------------+
| Criterion                                      | Status       |
|------------------------------------------------|--------------|
| Scan phase complete with inventory report       | [ ] Go       |
| Risk assessment complete with scores            | [ ] Go       |
| Migration approach selected and justified       | [ ] Go       |
| Hard blockers identified with mitigations       | [ ] Go       |
| Team skill gaps assessed with training plan     | [ ] Go       |
| Timeline estimated and stakeholder-approved     | [ ] Go       |
| Test coverage baseline established              | [ ] Go       |
| Rollback strategy defined for each phase        | [ ] Go       |
| CI/CD pipeline can support dual frameworks      | [ ] Go       |
| Budget approved for estimated effort            | [ ] Go       |
+--------------------------------------------------------------+
| Decision: [ ] GO -- Proceed with Phase 0
|           [ ] NO-GO -- Address gaps before proceeding
+--------------------------------------------------------------+
```

### Phase Transition Gates

At the end of each migration phase, verify before proceeding:

```
+--------------------------------------------------------------+
| Phase [N] Completion Gate                                     |
+--------------------------------------------------------------+
| Criterion                                      | Status       |
|------------------------------------------------|--------------|
| All projects in this phase compile on .NET 10   | [ ] Pass     |
| All unit tests pass                             | [ ] Pass     |
| All integration tests pass                      | [ ] Pass     |
| No regression in existing functionality         | [ ] Pass     |
| Performance benchmarks within acceptable range  | [ ] Pass     |
| Deployment to staging successful                | [ ] Pass     |
| Rollback tested and verified                    | [ ] Pass     |
| No new hard blockers discovered                 | [ ] Pass     |
+--------------------------------------------------------------+
| Decision: [ ] PROCEED to Phase [N+1]
|           [ ] HOLD -- Address failures before continuing
|           [ ] ROLLBACK -- Revert this phase
+--------------------------------------------------------------+
```

---

## 8. Common Migration Patterns

### Pattern: Abstract-Then-Migrate

**Problem**: Code is tightly coupled to .NET Framework APIs (e.g., `HttpContext.Current` throughout the codebase).

**Solution**: Introduce abstractions on .NET Framework BEFORE migrating.

```
Step 1 (on .NET Framework):
  Create IRequestContext interface
  Create .NET Framework implementation using HttpContext.Current
  Replace all direct HttpContext.Current usages with IRequestContext

Step 2 (during migration):
  Create .NET 10 implementation using IHttpContextAccessor
  Swap registration in DI container
  No consumer code changes needed
```

### Pattern: Parallel Run

**Problem**: Need to verify that the migrated code produces identical results to the legacy code.

**Solution**: Run both old and new implementations simultaneously, compare outputs.

```
Step 1: Deploy new .NET 10 service alongside legacy service
Step 2: Route a copy of production traffic to both
Step 3: Compare responses (ignore timing differences)
Step 4: Investigate any discrepancies
Step 5: Once parity is confirmed, cut over to new service
```

### Pattern: Feature Flag Migration

**Problem**: Need to migrate incrementally but cannot deploy separate services.

**Solution**: Use feature flags to toggle between old and new code paths.

```csharp
if (featureFlags.IsEnabled("UseNewOrderProcessor"))
{
    // New .NET 10 compatible implementation
    return await _newOrderProcessor.ProcessAsync(order);
}
else
{
    // Legacy implementation
    return _legacyOrderProcessor.Process(order);
}
```

### Pattern: Database-First Migration

**Problem**: The database schema is shared between multiple applications and cannot be changed.

**Solution**: Migrate the application code while keeping the database schema unchanged.

```
Step 1: Scaffold EF Core model from existing database
Step 2: Verify that EF Core model matches EF6 behavior
Step 3: Write integration tests that validate CRUD operations
Step 4: Swap EF6 for EF Core in the application
Step 5: ONLY after all applications are migrated, consider schema improvements
```

---

## 9. Risk Mitigation Strategies

### Mitigation: Characterization Tests

**When**: Test coverage is below 60% on business logic.

**How**:
1. Identify critical business workflows
2. Write tests that capture current behavior (pass/fail based on what the code DOES, not what it SHOULD do)
3. Run tests on .NET Framework to establish baseline
4. Run the same tests after migration to detect behavioral changes
5. Any test failure indicates a migration-introduced regression

### Mitigation: Canary Deployment

**When**: Migrating a high-traffic production service.

**How**:
1. Deploy the migrated service to a canary environment
2. Route 1-5% of production traffic to the canary
3. Monitor error rates, latency, and business metrics
4. If metrics are stable for 24-48 hours, increase traffic percentage
5. If metrics degrade, immediately route all traffic back to legacy

### Mitigation: Blue-Green Deployment

**When**: Full cutover is required but rollback must be instant.

**How**:
1. Blue environment runs the legacy .NET Framework application
2. Green environment runs the migrated .NET 10 application
3. Load balancer switches from Blue to Green
4. If issues arise, switch back to Blue in seconds
5. Both environments share the same database (ensure compatibility)

### Mitigation: Database Compatibility Layer

**When**: EF6 and EF Core must coexist during a phased migration.

**How**:
1. Both ORMs connect to the same database
2. EF Core is read-only initially (EF6 owns schema changes)
3. Gradually move write operations to EF Core
4. When all operations are on EF Core, remove EF6
5. Use `ef-migration-manager` to manage the transition

---

## 10. Post-Migration Validation Checklist

After the migration is complete, verify the following:

```
+--------------------------------------------------------------+
| Post-Migration Validation                                     |
+--------------------------------------------------------------+
| Category: Functional                                          |
|   [ ] All unit tests pass                                     |
|   [ ] All integration tests pass                              |
|   [ ] All end-to-end tests pass                               |
|   [ ] Manual smoke test of critical workflows                 |
|   [ ] Authentication and authorization working                |
|   [ ] All API endpoints responding correctly                  |
|   [ ] Background jobs and scheduled tasks running             |
|                                                               |
| Category: Performance                                         |
|   [ ] Response times within acceptable range                  |
|   [ ] Memory usage within acceptable range                    |
|   [ ] CPU usage within acceptable range                       |
|   [ ] Database query performance validated                    |
|   [ ] No memory leaks detected under load                     |
|                                                               |
| Category: Operations                                          |
|   [ ] Logging producing expected output                       |
|   [ ] Health checks responding                                |
|   [ ] Metrics and telemetry collecting                        |
|   [ ] Alerting configured and tested                          |
|   [ ] Deployment pipeline green for .NET 10                    |
|   [ ] Rollback procedure documented and tested                |
|                                                               |
| Category: Security                                            |
|   [ ] HTTPS/TLS configured correctly                          |
|   [ ] Authentication tokens validating correctly              |
|   [ ] CORS policy applied correctly                           |
|   [ ] Anti-forgery tokens working                             |
|   [ ] Data protection keys migrated or regenerated            |
|   [ ] No new security scan findings                           |
|                                                               |
| Category: Cleanup                                             |
|   [ ] Legacy .NET Framework projects removed from solution    |
|   [ ] Multi-targeting removed (single TFM: net10.0)           |
|   [ ] Compatibility shim packages removed                     |
|   [ ] web.config files removed (unless IIS hosting required)  |
|   [ ] Global.asax removed                                     |
|   [ ] Conditional compilation directives removed              |
|   [ ] Legacy NuGet packages removed                           |
|   [ ] Documentation updated to reflect .NET 10                 |
+--------------------------------------------------------------+
```
