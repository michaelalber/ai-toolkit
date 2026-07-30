# Breaking Changes: .NET Framework 4.x to .NET 10

## Critical Breaking Changes

### 1. System.Web Removed

The entire `System.Web` namespace is not available in .NET Core/.NET 5+.

**Affected APIs:**
- `HttpContext.Current`
- `HttpRequest`/`HttpResponse`
- `Session`
- `Application`
- `Cache`
- `WebClient` (use `HttpClient`)

**Migration:**
```csharp
// OLD: .NET Framework
var value = HttpContext.Current.Request.QueryString["key"];
HttpContext.Current.Session["user"] = user;

// NEW: .NET 10 (ASP.NET Core)
// Inject IHttpContextAccessor
public class MyService
{
    private readonly IHttpContextAccessor _httpContextAccessor;

    public MyService(IHttpContextAccessor httpContextAccessor)
    {
        _httpContextAccessor = httpContextAccessor;
    }

    public void DoWork()
    {
        var value = _httpContextAccessor.HttpContext?.Request.Query["key"];
        // Session requires explicit setup in Startup
    }
}
```

### 2. Configuration System Changed

`ConfigurationManager` is replaced with `IConfiguration`.

**Migration:**
```csharp
// OLD: .NET Framework
var connectionString = ConfigurationManager.ConnectionStrings["Default"].ConnectionString;
var appSetting = ConfigurationManager.AppSettings["MySetting"];

// NEW: .NET 10
// In Program.cs
builder.Configuration.AddJsonFile("appsettings.json");

// In service
public class MyService
{
    private readonly IConfiguration _config;

    public MyService(IConfiguration config)
    {
        _config = config;
    }

    public void DoWork()
    {
        var connectionString = _config.GetConnectionString("Default");
        var appSetting = _config["MySetting"];
    }
}
```

**appsettings.json:**
```json
{
  "ConnectionStrings": {
    "Default": "Server=...;Database=..."
  },
  "MySetting": "value"
}
```

### 3. WCF Client Changes

WCF server is not supported in .NET Core/.NET 5+. WCF client has limited support.

**Options:**
1. **gRPC** - Recommended replacement for internal services
2. **REST APIs** - For HTTP-based services
3. **CoreWCF** - Community port for server-side WCF
4. **System.ServiceModel packages** - Client-only support

**gRPC Migration:**
```csharp
// Define service in .proto file
service Greeter {
    rpc SayHello (HelloRequest) returns (HelloReply);
}

// Client usage
var channel = GrpcChannel.ForAddress("https://localhost:5001");
var client = new Greeter.GreeterClient(channel);
var reply = await client.SayHelloAsync(new HelloRequest { Name = "World" });
```

### 4. Entity Framework 6 → EF Core

EF6 and EF Core are different ORMs with different APIs.

**Key Differences:**
- `DbContext.Database.SqlQuery<T>()` → `DbContext.Database.SqlQueryRaw<T>()`
- `ObjectStateManager` → `ChangeTracker`
- Lazy loading requires explicit setup
- No `ObjectContext` support

**Migration:**
```csharp
// OLD: EF6
using (var context = new MyDbContext())
{
    var items = context.Database.SqlQuery<Item>("SELECT * FROM Items").ToList();
    context.Entry(entity).State = EntityState.Modified;
}

// NEW: EF Core
using (var context = new MyDbContext())
{
    var items = context.Items.FromSqlRaw("SELECT * FROM Items").ToList();
    context.Entry(entity).State = EntityState.Modified;
}
```

### 5. Assembly Loading Changes

`AppDomain` is significantly reduced. No `AppDomain.CreateDomain()`.

**Migration:**
```csharp
// OLD: .NET Framework - Multiple AppDomains
var domain = AppDomain.CreateDomain("NewDomain");
var assembly = domain.Load("MyAssembly");

// NEW: .NET 10 - Use AssemblyLoadContext
var context = new AssemblyLoadContext("MyContext", isCollectible: true);
var assembly = context.LoadFromAssemblyPath("MyAssembly.dll");
// Unload when done
context.Unload();
```

### 6. Binary Serialization Deprecated

`BinaryFormatter` is obsolete and disabled by default (security risk).

**Migration:**
```csharp
// OLD: .NET Framework
var formatter = new BinaryFormatter();
formatter.Serialize(stream, obj);

// NEW: .NET 10 - Use System.Text.Json or other serializers
var json = JsonSerializer.Serialize(obj);
var obj = JsonSerializer.Deserialize<MyType>(json);

// Or MessagePack for binary
var bytes = MessagePackSerializer.Serialize(obj);
```

### 7. Cryptography API Changes

Some cryptography classes moved or changed.

**Migration:**
```csharp
// OLD: .NET Framework
using (var rng = new RNGCryptoServiceProvider())
{
    rng.GetBytes(buffer);
}

// NEW: .NET 10
RandomNumberGenerator.Fill(buffer);
// Or
using var rng = RandomNumberGenerator.Create();
rng.GetBytes(buffer);
```

### 8. Reflection Changes

Some reflection APIs behave differently.

**Key Changes:**
- `Assembly.LoadFrom()` may behave differently
- `Type.GetType()` assembly resolution changed
- Private member reflection may require `[DynamicallyAccessedMembers]`

```csharp
// NEW: For AOT/trimming compatibility
public void ProcessType([DynamicallyAccessedMembers(DynamicallyAccessedMemberTypes.PublicProperties)] Type type)
{
    var properties = type.GetProperties();
}
```

### 9. Globalization Changes

Some globalization behaviors changed.

**Key Changes:**
- NLS → ICU (International Components for Unicode) on Windows
- Some culture names changed
- Sort order may differ

```csharp
// Force NLS for compatibility (if needed)
// In .csproj
<ItemGroup>
    <RuntimeHostConfigurationOption Include="System.Globalization.UseNls" Value="true" />
</ItemGroup>
```

### 10. Thread.Abort() Removed

`Thread.Abort()` is not supported.

**Migration:**
```csharp
// OLD: .NET Framework
thread.Abort();

// NEW: .NET 10 - Use CancellationToken
var cts = new CancellationTokenSource();
var task = Task.Run(() => DoWork(cts.Token), cts.Token);
cts.Cancel(); // Request cancellation

void DoWork(CancellationToken token)
{
    while (!token.IsCancellationRequested)
    {
        // Work
    }
}
```

## Medium Impact Changes

### 11. Default Encoding Changed

Default encoding for `StreamReader`/`StreamWriter` is UTF-8 without BOM.

```csharp
// Explicit encoding if needed
using var reader = new StreamReader(path, Encoding.UTF8);
```

### 12. HttpClient Lifecycle

`HttpClient` should be reused via `IHttpClientFactory`.

```csharp
// OLD: .NET Framework (common mistake)
using (var client = new HttpClient())
{
    // Socket exhaustion risk
}

// NEW: .NET 10
// In DI
services.AddHttpClient<MyService>();

// In service
public class MyService
{
    private readonly HttpClient _client;

    public MyService(HttpClient client)
    {
        _client = client;
    }
}
```

### 13. Path Handling

`Path.Combine` and path handling may differ.

```csharp
// Use Path.Join for more predictable behavior
var path = Path.Join("folder", "subfolder", "file.txt");
```

### 14. Async/Await Context

`SynchronizationContext` is null by default in console apps.

```csharp
// ConfigureAwait(false) is the default behavior
await Task.Delay(1000); // Won't capture context
```

### 15. Memory Management

`GC.Collect()` behavior may differ. Avoid forcing GC.

## API Availability by .NET Version

| API | .NET Core 3.1 | .NET 6 | .NET 8 | .NET 10 |
|-----|---------------|--------|--------|---------|
| System.Web | No | No | No | No |
| WCF Server | No | No | No | No |
| WCF Client | Limited | Limited | Limited | Limited |
| EF6 | No | No | No | No |
| EF Core | Yes | Yes | Yes | Yes |
| Windows Forms | Yes* | Yes* | Yes* | Yes* |
| WPF | Yes* | Yes* | Yes* | Yes* |
| ASP.NET Core | Yes | Yes | Yes | Yes |

\* Windows only with `-windows` TFM

## Namespace Changes

| Old Namespace | New Namespace | Notes |
|---------------|---------------|-------|
| `System.Web` | `Microsoft.AspNetCore.*` | Complete rewrite |
| `System.Data.Entity` | `Microsoft.EntityFrameworkCore` | Different API |
| `System.Configuration` | `Microsoft.Extensions.Configuration` | Different API |
| `System.Web.Http` | `Microsoft.AspNetCore.Mvc` | Controllers unified |
| `Newtonsoft.Json` | `System.Text.Json` | Optional migration |

## Detection Commands

```bash
# Find all breaking changes in codebase
echo "=== System.Web Usage ==="
grep -r "using System\.Web" --include="*.cs" | wc -l

echo "=== WCF Usage ==="
grep -r "ServiceContract\|OperationContract\|using System\.ServiceModel" --include="*.cs" | wc -l

echo "=== BinaryFormatter Usage ==="
grep -r "BinaryFormatter" --include="*.cs" | wc -l

echo "=== Thread.Abort Usage ==="
grep -r "\.Abort()" --include="*.cs" | wc -l

echo "=== ConfigurationManager Usage ==="
grep -r "ConfigurationManager" --include="*.cs" | wc -l

echo "=== AppDomain.CreateDomain Usage ==="
grep -r "AppDomain\.CreateDomain\|AppDomain\.Create" --include="*.cs" | wc -l
```
