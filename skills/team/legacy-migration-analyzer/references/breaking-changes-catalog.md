# Breaking Changes Catalog

## Overview

This catalog documents breaking changes encountered when migrating from .NET Framework (4.x) to .NET 10. Each entry includes a description, severity rating, detection method, and recommended migration path.

**Severity Levels:**

| Level | Definition |
|-------|-----------|
| **Blocker** | No known automated migration path. Requires architectural changes or manual rewrite. |
| **High** | Significant code changes required. Automated tools can detect but not fully resolve. |
| **Medium** | Moderate changes required. Well-documented migration path exists. |
| **Low** | Minor changes. Often handled automatically by the Upgrade Assistant. |

---

## Category 1: ASP.NET to ASP.NET Core

### 1.1 System.Web Removal

**Description**: The entire `System.Web` namespace does not exist in .NET 10. This is the single largest breaking change for web applications. All types in `System.Web` must be replaced with ASP.NET Core equivalents.

**Severity**: High

**Detection**:
```bash
# Search for System.Web references
grep -r "using System.Web" --include="*.cs" .
grep -r "System.Web" --include="*.csproj" .
```

**Key Replacements:**

| .NET Framework (System.Web) | .NET 10 (ASP.NET Core) | Notes |
|-----------------------------|------------------------|-------|
| `HttpContext.Current` | `IHttpContextAccessor` | Must be injected via DI, not accessed statically |
| `HttpRequest` | `Microsoft.AspNetCore.Http.HttpRequest` | Different API surface |
| `HttpResponse` | `Microsoft.AspNetCore.Http.HttpResponse` | Different API surface |
| `HttpApplication` | `WebApplication` / middleware pipeline | Complete architectural change |
| `HttpModule` | Middleware classes | Implement `IMiddleware` or use convention |
| `HttpHandler` | Middleware or endpoint routing | Map to `app.MapGet()` etc. |
| `Session["key"]` | `HttpContext.Session.GetString("key")` | Requires `AddDistributedMemoryCache()` + `AddSession()` |
| `Cache` (System.Web.Caching) | `IMemoryCache` or `IDistributedCache` | Inject via DI |
| `HttpServerUtility.MapPath()` | `IWebHostEnvironment.ContentRootPath` | Combine with `Path.Combine()` |
| `HttpRuntime.AppDomainAppPath` | `IWebHostEnvironment.ContentRootPath` | Inject via DI |
| `Request.UserHostAddress` | `HttpContext.Connection.RemoteIpAddress` | Returns `IPAddress` not string |
| `Request.Url` | `HttpContext.Request.GetDisplayUrl()` | Requires `Microsoft.AspNetCore.Http.Extensions` |
| `FormsAuthentication` | ASP.NET Core Identity / Cookie Auth | Complete replacement required |
| `MembershipProvider` | ASP.NET Core Identity | Complete replacement required |
| `RoleProvider` | ASP.NET Core Identity with roles | Complete replacement required |
| `BundleConfig` | Webpack, Vite, or LibMan | Build-time bundling instead of runtime |
| `WebConfigurationManager` | `IConfiguration` | Options pattern preferred |

**Migration Path:**
1. Create an abstraction layer for `HttpContext.Current` usages on .NET Framework
2. Replace static access with dependency injection
3. Migrate consumers to use the abstraction
4. Swap implementation to ASP.NET Core equivalents after framework migration

### 1.2 Global.asax Removal

**Description**: `Global.asax` and the `HttpApplication` lifecycle events (`Application_Start`, `Application_BeginRequest`, etc.) do not exist in ASP.NET Core.

**Severity**: High

**Detection**:
```bash
find . -name "Global.asax*" -type f
grep -r "Application_Start\|Application_End\|Application_Error\|Application_BeginRequest" --include="*.cs" .
```

**Migration Path:**

| Global.asax Event | ASP.NET Core Equivalent |
|-------------------|------------------------|
| `Application_Start` | `Program.cs` / `Startup.Configure()` |
| `Application_End` | `IHostApplicationLifetime.ApplicationStopping` |
| `Application_Error` | Exception handling middleware |
| `Application_BeginRequest` | Custom middleware (early in pipeline) |
| `Application_EndRequest` | Custom middleware (response phase) |
| `Application_AuthenticateRequest` | Authentication middleware |
| `Session_Start` | Session middleware configuration |
| `Session_End` | Not directly supported; use distributed cache expiry |

### 1.3 Web.config to appsettings.json

**Description**: XML-based `web.config` configuration must be migrated to JSON-based `appsettings.json` with the Options pattern.

**Severity**: Medium

**Detection**:
```bash
find . -name "web.config" -o -name "app.config" | head -20
grep -r "ConfigurationManager\|WebConfigurationManager" --include="*.cs" .
```

**Migration Path:**

| web.config Section | appsettings.json Equivalent |
|--------------------|----------------------------|
| `<appSettings>` | Top-level JSON properties |
| `<connectionStrings>` | `"ConnectionStrings": { }` section |
| `<system.web>` | Middleware configuration in `Program.cs` |
| `<system.webServer>` | Kestrel configuration or reverse proxy config |
| Custom `<configSections>` | Strongly-typed Options classes with `IOptions<T>` |
| `<system.net.mail>` | `IEmailSender` implementation |
| `<system.diagnostics>` | `ILogger` / OpenTelemetry configuration |

**Code Change Example:**

```csharp
// BEFORE (.NET Framework)
var setting = ConfigurationManager.AppSettings["MySetting"];
var connStr = ConfigurationManager.ConnectionStrings["MyDb"].ConnectionString;

// AFTER (.NET 10)
// In Program.cs:
builder.Services.Configure<MyOptions>(builder.Configuration.GetSection("MySettings"));

// In consuming class:
public class MyService
{
    private readonly MyOptions _options;
    public MyService(IOptions<MyOptions> options) => _options = options.Value;
}
```

### 1.4 MVC and Web API Unification

**Description**: ASP.NET MVC (System.Web.Mvc) and ASP.NET Web API (System.Web.Http) are separate frameworks in .NET Framework. In ASP.NET Core, they are unified under `Microsoft.AspNetCore.Mvc`.

**Severity**: Medium

**Detection**:
```bash
grep -r "System.Web.Mvc\|System.Web.Http\|ApiController" --include="*.cs" .
```

**Key Changes:**

| .NET Framework | .NET 10 |
|---------------|---------|
| `System.Web.Mvc.Controller` | `Microsoft.AspNetCore.Mvc.Controller` |
| `System.Web.Http.ApiController` | `Microsoft.AspNetCore.Mvc.ControllerBase` |
| `[HttpPost] (System.Web.Http)` | `[HttpPost] (Microsoft.AspNetCore.Mvc)` |
| `IHttpActionResult` | `IActionResult` or `ActionResult<T>` |
| `Request.CreateResponse()` | `Ok()`, `BadRequest()`, `NotFound()` |
| `GlobalConfiguration.Configure()` | `builder.Services.AddControllers()` |
| Route registration in `RouteConfig.cs` | Attribute routing or `app.MapControllers()` |
| `FilterConfig` (global filters) | `builder.Services.AddControllers(o => o.Filters.Add(...))` |
| `ModelState` | Same name, different namespace |

### 1.5 SignalR Migration

**Description**: ASP.NET SignalR and ASP.NET Core SignalR are completely different implementations with incompatible wire protocols.

**Severity**: High

**Detection**:
```bash
grep -r "Microsoft.AspNet.SignalR" --include="*.csproj" .
grep -r "using Microsoft.AspNet.SignalR" --include="*.cs" .
```

**Migration Path:**
1. Hub classes must be rewritten to inherit from `Microsoft.AspNetCore.SignalR.Hub`
2. Client-side JavaScript must update to `@microsoft/signalr` package
3. Connection lifecycle is different (no automatic reconnection by default)
4. Group management API changes
5. Strongly-typed hubs are recommended in ASP.NET Core

---

## Category 2: WCF to gRPC / REST / CoreWCF

### 2.1 WCF Server-Side

**Description**: WCF server hosting is not supported in .NET 10. The `System.ServiceModel` server-side namespace does not exist. Options: CoreWCF (compatibility), gRPC (modern RPC), or REST APIs.

**Severity**: Blocker (without CoreWCF) / High (with CoreWCF)

**Detection**:
```bash
grep -r "ServiceHost\|ServiceBehavior\|OperationContract\|ServiceContract" --include="*.cs" .
grep -r "System.ServiceModel" --include="*.csproj" .
find . -name "*.svc" -type f
```

**Migration Options:**

| WCF Feature | CoreWCF | gRPC | REST (ASP.NET Core) |
|-------------|---------|------|---------------------|
| Request-Reply | Yes | Yes | Yes |
| One-Way | Yes | Yes (server streaming) | Yes (fire-and-forget) |
| Duplex | Partial | Yes (bidirectional streaming) | SignalR |
| SOAP/WSDL | Yes | No | No |
| BasicHttpBinding | Yes | N/A | N/A |
| NetTcpBinding | Yes | N/A (uses HTTP/2) | N/A |
| MSMQ Transport | No | No | No (use message broker) |
| WS-Security | Partial | TLS + call credentials | OAuth2 / JWT |
| WS-Federation | No | No | OpenID Connect |
| Metadata Exchange (MEX) | Yes | Proto reflection | OpenAPI/Swagger |

**Decision Guidance:**
- **Use CoreWCF** when: SOAP/WSDL is required for external consumers, rapid migration is needed, or the service contract is large and stable.
- **Use gRPC** when: both client and server are being migrated, high performance is critical, or streaming is needed.
- **Use REST** when: the service is consumed by web clients, broad interoperability is needed, or the team prefers REST patterns.

### 2.2 WCF Client-Side

**Description**: WCF client proxies (`System.ServiceModel` client-side) have limited support via the `System.ServiceModel.Http` and `System.ServiceModel.Primitives` NuGet packages.

**Severity**: Medium

**Detection**:
```bash
grep -r "ChannelFactory\|ClientBase\|EndpointAddress" --include="*.cs" .
find . -name "*.svcmap" -o -name "Reference.cs" | grep -v obj
```

**Migration Path:**
1. Install `System.ServiceModel.Http` NuGet package for BasicHttp clients
2. For NetTcp clients, use `System.ServiceModel.NetTcp` package (limited support)
3. Regenerate client proxies using `dotnet-svc` tool
4. For complex bindings, consider replacing with `HttpClient` + REST or gRPC client

---

## Category 3: Entity Framework 6 to EF Core

### 3.1 Namespace and Package Changes

**Description**: EF6 (`EntityFramework` NuGet) is replaced by EF Core (`Microsoft.EntityFrameworkCore` NuGet). All namespaces change.

**Severity**: High

**Detection**:
```bash
grep -r "using System.Data.Entity" --include="*.cs" .
grep -r "EntityFramework" --include="*.csproj" .
```

**Namespace Migration:**

| EF6 | EF Core |
|-----|---------|
| `System.Data.Entity` | `Microsoft.EntityFrameworkCore` |
| `System.Data.Entity.Infrastructure` | `Microsoft.EntityFrameworkCore.Infrastructure` |
| `System.Data.Entity.Migrations` | `Microsoft.EntityFrameworkCore.Migrations` |
| `System.Data.Entity.ModelConfiguration` | Fluent API in `OnModelCreating` |
| `System.Data.Entity.Spatial` | `NetTopologySuite` NuGet package |

### 3.2 Behavioral Differences

**Description**: EF Core has different default behaviors compared to EF6 that can change query results or application behavior.

**Severity**: High

**Key Differences:**

| Behavior | EF6 | EF Core | Impact |
|----------|-----|---------|--------|
| Lazy Loading | Enabled by default | Disabled by default | Navigation properties return null unless explicitly loaded |
| Client Evaluation | Silently evaluates in memory | Throws exception (by default) | Queries that worked in EF6 may fail in EF Core |
| Cascade Delete | Convention-based | More explicit configuration needed | Related entities may not be deleted automatically |
| Table-per-Hierarchy (TPH) | Discriminator column naming | Different conventions | Existing databases may not match expected schema |
| Many-to-Many | Requires explicit join entity (EF6) | Implicit join table (EF Core 5+) | Model simplification possible |
| Complex Types | `ComplexType` attribute | `OwnsOne` / `OwnsMany` | Different configuration API |
| Database Initializers | `CreateDatabaseIfNotExists`, etc. | `EnsureCreated` or Migrations | Different initialization strategy |
| Raw SQL | `Database.SqlQuery<T>()` | `FromSqlRaw()` / `FromSqlInterpolated()` | Different method names and behavior |
| Spatial Data | `DbGeography` / `DbGeometry` | NetTopologySuite types | Third-party library required |
| Stored Procedures | First-class mapping support | Limited (keyless entity types) | May need raw SQL for complex SP usage |
| Migration History | `__MigrationHistory` table | `__EFMigrationsHistory` table | New migration chain required |

### 3.3 DbContext Configuration

**Description**: EF6 uses constructors with connection string names and configuration files. EF Core uses `DbContextOptions` and dependency injection.

**Severity**: Medium

**Code Change Example:**

```csharp
// BEFORE (EF6)
public class MyDbContext : DbContext
{
    public MyDbContext() : base("name=MyConnectionString") { }
    public DbSet<Customer> Customers { get; set; }
}

// AFTER (EF Core)
public class MyDbContext : DbContext
{
    public MyDbContext(DbContextOptions<MyDbContext> options) : base(options) { }
    public DbSet<Customer> Customers { get; set; }
}

// Registration in Program.cs:
builder.Services.AddDbContext<MyDbContext>(options =>
    options.UseSqlServer(builder.Configuration.GetConnectionString("MyConnectionString")));
```

### 3.4 EDMX / Database-First Models

**Description**: EDMX files (`.edmx`) and the visual designer are not supported in EF Core. Database-first workflows use `dotnet ef dbcontext scaffold`.

**Severity**: High

**Detection**:
```bash
find . -name "*.edmx" -type f
grep -r "ObjectContext\|EntityObject" --include="*.cs" .
```

**Migration Path:**
1. Scaffold EF Core model from existing database:
   ```bash
   dotnet ef dbcontext scaffold "ConnectionString" Microsoft.EntityFrameworkCore.SqlServer -o Models
   ```
2. Compare generated model with EDMX model for discrepancies
3. Add Fluent API configuration for any customizations from the EDMX
4. Remove EDMX file and related generated code
5. Coordinate new migration baseline with `ef-migration-manager`

---

## Category 4: Windows-Specific APIs

### 4.1 Windows Registry

**Description**: `Microsoft.Win32.Registry` is available on .NET 10 but only on Windows. Code using the Registry will not work on Linux/macOS.

**Severity**: Medium (if Windows-only) / High (if cross-platform required)

**Detection**:
```bash
grep -r "Microsoft.Win32.Registry\|RegistryKey\|Registry.LocalMachine\|Registry.CurrentUser" --include="*.cs" .
```

**Migration Path:**
- Install `Microsoft.Win32.Registry` NuGet package (Windows-only)
- For cross-platform: replace with `IConfiguration` reading from environment variables or files
- Guard with `RuntimeInformation.IsOSPlatform(OSPlatform.Windows)` if mixed usage

### 4.2 System.Drawing

**Description**: `System.Drawing` on .NET Framework wraps GDI+ (Windows-only). On .NET 10, `System.Drawing.Common` is Windows-only and throws `PlatformNotSupportedException` on Linux/macOS.

**Severity**: High (if cross-platform required)

**Detection**:
```bash
grep -r "using System.Drawing\|System.Drawing.Common" --include="*.cs" .
grep -r "System.Drawing" --include="*.csproj" .
```

**Migration Path:**

| Use Case | Replacement Library |
|----------|-------------------|
| Image resizing/manipulation | `SixLabors.ImageSharp` |
| PDF generation with images | `QuestPDF`, `iTextSharp` replacement |
| Chart generation | `ScottPlot`, `LiveCharts2` |
| Barcode generation | `ZXing.Net`, `BarcodeLib` |
| Simple color/point types | `System.Drawing.Primitives` (cross-platform) |

### 4.3 Windows Event Log

**Description**: `System.Diagnostics.EventLog` is Windows-only in .NET 10.

**Severity**: Medium

**Detection**:
```bash
grep -r "EventLog\|EventLogEntry" --include="*.cs" .
```

**Migration Path:**
- Replace with `ILogger` + Serilog/NLog sinks for structured logging
- For Windows-specific deployments, use `Microsoft.Extensions.Logging.EventLog` package
- For cross-platform: use Serilog with file, console, or centralized logging sinks

### 4.4 Windows Performance Counters

**Description**: `System.Diagnostics.PerformanceCounter` is Windows-only. .NET 10 uses `System.Diagnostics.Metrics` and OpenTelemetry.

**Severity**: Medium

**Detection**:
```bash
grep -r "PerformanceCounter\|PerformanceCounterCategory" --include="*.cs" .
```

**Migration Path:**
1. Replace `PerformanceCounter` reads with `System.Diagnostics.Metrics`
2. Use `Meter` and `Counter<T>` / `Histogram<T>` for custom metrics
3. Export via OpenTelemetry to Prometheus, Azure Monitor, or similar
4. For Windows-specific monitoring, use `System.Diagnostics.PerformanceCounter` NuGet package

### 4.5 Windows Management Instrumentation (WMI)

**Description**: `System.Management` (WMI) is Windows-only in .NET 10.

**Severity**: Medium

**Detection**:
```bash
grep -r "System.Management\|ManagementObject\|ManagementScope\|WqlObjectQuery" --include="*.cs" .
```

**Migration Path:**
- Install `System.Management` NuGet package (Windows-only)
- For cross-platform alternatives, use `/proc` filesystem on Linux or platform-specific APIs
- Consider replacing with `System.Diagnostics.Process` for process management scenarios

### 4.6 Windows Services

**Description**: `System.ServiceProcess.ServiceBase` is replaced by `Microsoft.Extensions.Hosting.BackgroundService` or Worker Service template.

**Severity**: Medium

**Detection**:
```bash
grep -r "ServiceBase\|ServiceInstaller\|ServiceProcessInstaller" --include="*.cs" .
find . -name "ProjectInstaller.cs" -type f
```

**Migration Path:**

```csharp
// BEFORE (.NET Framework Windows Service)
public class MyService : ServiceBase
{
    protected override void OnStart(string[] args) { /* ... */ }
    protected override void OnStop() { /* ... */ }
}

// AFTER (.NET 10 Worker Service)
public class MyWorker : BackgroundService
{
    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        while (!stoppingToken.IsCancellationRequested)
        {
            // ... do work
            await Task.Delay(TimeSpan.FromSeconds(10), stoppingToken);
        }
    }
}

// Can still run as Windows Service with:
// builder.Services.AddWindowsService();
// Or as systemd on Linux:
// builder.Services.AddSystemd();
```

---

## Category 5: Common NuGet Package Replacements

### 5.1 Direct Replacements

| .NET Framework Package | .NET 10 Replacement | Notes |
|----------------------|---------------------|-------|
| `Microsoft.AspNet.Mvc` | `Microsoft.AspNetCore.Mvc` | Part of ASP.NET Core shared framework |
| `Microsoft.AspNet.WebApi` | `Microsoft.AspNetCore.Mvc` | Unified with MVC |
| `Microsoft.AspNet.SignalR` | `Microsoft.AspNetCore.SignalR` | Incompatible wire protocol |
| `Microsoft.AspNet.Identity` | `Microsoft.AspNetCore.Identity` | Different storage model |
| `Microsoft.Owin` | Built-in ASP.NET Core middleware | OWIN concepts absorbed into ASP.NET Core |
| `EntityFramework` (6.x) | `Microsoft.EntityFrameworkCore` | See EF section above |
| `Newtonsoft.Json` | `System.Text.Json` (or keep Newtonsoft) | `System.Text.Json` is default, Newtonsoft still supported |
| `Unity` (DI container) | `Microsoft.Extensions.DependencyInjection` | Built-in DI; or use third-party |
| `Autofac` (4.x) | `Autofac` (7.x+) + `Autofac.Extensions.DependencyInjection` | New integration package needed |
| `Castle.Windsor` (5.x) | `Castle.Windsor` (6.x+) | Breaking changes in registration API |
| `StructureMap` | `Lamar` | StructureMap is discontinued; Lamar is the successor |
| `log4net` | `Serilog` or `NLog` + `Microsoft.Extensions.Logging` | log4net works but modern alternatives preferred |
| `NLog` (4.x) | `NLog` (5.x+) + `NLog.Web.AspNetCore` | New integration package for ASP.NET Core |
| `Serilog` (2.x) | `Serilog` (4.x+) + `Serilog.AspNetCore` | Minimal API integration available |
| `System.Configuration.ConfigurationManager` | `Microsoft.Extensions.Configuration` | Options pattern recommended |
| `System.Web.Http.OData` | `Microsoft.AspNetCore.OData` | Complete API redesign |
| `FluentValidation` (8.x) | `FluentValidation` (11.x+) | New ASP.NET Core integration |
| `AutoMapper` (10.x) | `AutoMapper` (13.x+) | New DI registration pattern |
| `MediatR` (9.x) | `MediatR` (12.x+) | Updated DI registration |
| `Hangfire` | `Hangfire` (1.8+) | ASP.NET Core server package needed |
| `Quartz.NET` (3.x) | `Quartz.NET` (3.8+) | New hosting integration |
| `RestSharp` (106.x) | `RestSharp` (110.x+) or `HttpClient` | Major API changes in 107+ |
| `Dapper` | `Dapper` (latest) | Fully compatible, minimal changes |
| `StackExchange.Redis` | `StackExchange.Redis` (latest) | Fully compatible |

### 5.2 Packages with No Direct Replacement

| .NET Framework Package | Status | Recommendation |
|----------------------|--------|----------------|
| `System.Web.Helpers` | Discontinued | Use ASP.NET Core Tag Helpers / Razor components |
| `Microsoft.AspNet.WebPages` | Discontinued | Use Razor Pages |
| `DotNetOpenAuth` | Discontinued | Use `Microsoft.AspNetCore.Authentication.OpenIdConnect` |
| `ELMAH` | Windows-only | Use Serilog + structured logging |
| `Glimpse` | Discontinued | Use OpenTelemetry + Application Insights |
| `WebGrease` | Discontinued | Use modern bundlers (Webpack, Vite) |
| `Microsoft.AspNet.Web.Optimization` | Discontinued | Use WebOptimizer or build-time bundling |

---

## Category 6: .NET Upgrade Assistant Usage

### 6.1 Installation

```bash
dotnet tool install -g upgrade-assistant
```

### 6.2 Analysis Mode (Recommended First Step)

```bash
# Analyze without making changes
upgrade-assistant analyze <SolutionPath> --target-tfm net10.0

# Analyze a specific project
upgrade-assistant analyze <ProjectPath> --target-tfm net10.0
```

### 6.3 Upgrade Mode

```bash
# Interactive upgrade
upgrade-assistant upgrade <SolutionPath> --target-tfm net10.0

# Upgrade specific project
upgrade-assistant upgrade <ProjectPath> --target-tfm net10.0

# Non-interactive (for CI)
upgrade-assistant upgrade <SolutionPath> --target-tfm net10.0 --non-interactive
```

### 6.4 What the Upgrade Assistant Handles

| Change | Automated | Manual Review Needed |
|--------|-----------|---------------------|
| Project file conversion (csproj) | Yes | Verify no settings lost |
| Target framework update | Yes | N/A |
| NuGet package updates | Partial | Verify compatibility |
| Namespace updates | Partial | Verify correctness |
| API replacements | Partial | Many require manual intervention |
| web.config migration | Partial | Custom sections need manual work |
| Startup/Program.cs creation | Yes (template) | Customize for your app |
| Global.asax migration | No | Manual migration required |
| Authentication migration | No | Manual migration required |
| WCF migration | No | Architectural decision required |

### 6.5 API Compatibility Analyzers

Add analyzers to your project for compile-time detection of compatibility issues:

```xml
<!-- In .csproj file -->
<ItemGroup>
  <PackageReference Include="Microsoft.DotNet.UpgradeAssistant.Extensions.Default.Analyzers"
                    Version="*"
                    PrivateAssets="all" />
</ItemGroup>
```

These analyzers will produce warnings for:
- APIs that do not exist in .NET 10
- APIs with behavioral differences
- APIs that require platform-specific packages
- Deprecated patterns that should be modernized

---

## Category 7: Configuration and Hosting

### 7.1 Hosting Model

| .NET Framework | .NET 10 |
|---------------|---------|
| IIS hosting (in-process via `w3wp.exe`) | Kestrel + optional reverse proxy (IIS, Nginx, YARP) |
| `System.Web.HttpApplication` pipeline | Middleware pipeline in `Program.cs` |
| Application pools | Process management via systemd, IIS, or container orchestrator |
| Machine.config | No equivalent; use environment-specific appsettings |
| GAC (Global Assembly Cache) | No equivalent; use NuGet packages or local deployment |

### 7.2 Dependency Injection

| .NET Framework | .NET 10 |
|---------------|---------|
| No built-in DI | `Microsoft.Extensions.DependencyInjection` built-in |
| Third-party containers (Unity, Autofac, etc.) | Built-in DI or third-party with `IServiceProviderFactory` |
| Service Locator pattern | Constructor injection (anti-pattern to pattern) |
| `HttpContext.Current` for ambient context | `IHttpContextAccessor` via DI |

### 7.3 Logging

| .NET Framework | .NET 10 |
|---------------|---------|
| `System.Diagnostics.Trace` | `Microsoft.Extensions.Logging.ILogger<T>` |
| `log4net` / `NLog` directly | `ILogger<T>` with Serilog/NLog as provider |
| Event Log (Windows) | Structured logging + configurable sinks |
| No structured logging standard | Built-in structured logging with scopes |

---

## Category 8: Security and Authentication

### 8.1 Authentication Migration

| .NET Framework | .NET 10 | Effort |
|---------------|---------|--------|
| Forms Authentication | Cookie Authentication middleware | High |
| Windows Authentication | Negotiate/NTLM middleware | Medium |
| ASP.NET Membership | ASP.NET Core Identity | High |
| ASP.NET Simple Membership | ASP.NET Core Identity | High |
| WIF (Windows Identity Foundation) | OpenID Connect / JWT Bearer | High |
| OWIN Cookie Auth | ASP.NET Core Cookie Auth | Medium |
| OAuth via DotNetOpenAuth | `Microsoft.AspNetCore.Authentication.OAuth` | High |
| ADFS | OpenID Connect with ADFS | Medium |
| Azure AD (ADAL) | MSAL + Microsoft Identity Web | Medium |
| Custom `IPrincipal` / `IIdentity` | `ClaimsPrincipal` / `ClaimsIdentity` | Medium |

### 8.2 Anti-Forgery / CSRF

```csharp
// BEFORE (.NET Framework)
@Html.AntiForgeryToken()
[ValidateAntiForgeryToken]

// AFTER (.NET 10) - same attribute name, different namespace
// Auto-validation available:
builder.Services.AddControllersWithViews(options =>
    options.Filters.Add(new AutoValidateAntiforgeryTokenAttribute()));
```

### 8.3 Data Protection

| .NET Framework | .NET 10 |
|---------------|---------|
| `MachineKey` for encryption/signing | `Microsoft.AspNetCore.DataProtection` |
| `machineKey` in web.config | `builder.Services.AddDataProtection()` |
| Shared machine key across servers | Key ring with shared storage (Redis, Azure Blob, file share) |

---

## Quick Reference: Detection Commands

Run these commands to quickly assess the scope of a migration:

```bash
# Count System.Web usages (biggest indicator of migration effort)
grep -rc "System\.Web" --include="*.cs" . | grep -v ":0" | sort -t: -k2 -nr

# Count WCF usages
grep -rc "ServiceContract\|OperationContract\|ServiceHost" --include="*.cs" . | grep -v ":0"

# Count EF6 usages
grep -rc "System\.Data\.Entity" --include="*.cs" . | grep -v ":0"

# Find EDMX files
find . -name "*.edmx" -type f

# Find web.config files
find . -name "web.config" -type f

# Count Windows-specific APIs
grep -rc "Registry\.\|EventLog\|PerformanceCounter\|System\.Management" --include="*.cs" . | grep -v ":0"

# List all NuGet packages across solution
dotnet list package

# List NuGet packages with available updates
dotnet list package --outdated

# Check for .NET 10 incompatible packages
dotnet list package --target-framework net10.0
```
