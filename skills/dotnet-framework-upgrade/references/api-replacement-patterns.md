# API Replacement Patterns: .NET Framework to .NET 10

## HttpContext and Web APIs

### HttpContext.Current → IHttpContextAccessor

```csharp
// OLD: .NET Framework
public class MyService
{
    public void DoWork()
    {
        var user = HttpContext.Current.User;
        var request = HttpContext.Current.Request;
        var session = HttpContext.Current.Session["key"];
    }
}

// NEW: .NET 10
public class MyService
{
    private readonly IHttpContextAccessor _httpContextAccessor;

    public MyService(IHttpContextAccessor httpContextAccessor)
    {
        _httpContextAccessor = httpContextAccessor;
    }

    public void DoWork()
    {
        var context = _httpContextAccessor.HttpContext;
        var user = context?.User;
        var request = context?.Request;
        // Session requires explicit setup
    }
}

// Registration in Program.cs
builder.Services.AddHttpContextAccessor();
```

### HttpRequest Members

```csharp
// OLD: .NET Framework
var url = Request.Url.AbsoluteUri;
var query = Request.QueryString["key"];
var form = Request.Form["field"];
var header = Request.Headers["X-Custom"];
var cookie = Request.Cookies["name"].Value;
var body = new StreamReader(Request.InputStream).ReadToEnd();

// NEW: .NET 10
var url = $"{Request.Scheme}://{Request.Host}{Request.Path}{Request.QueryString}";
var query = Request.Query["key"];
var form = Request.Form["field"];
var header = Request.Headers["X-Custom"];
var cookie = Request.Cookies["name"];
var body = await new StreamReader(Request.Body).ReadToEndAsync();
```

### HttpResponse Members

```csharp
// OLD: .NET Framework
Response.StatusCode = 200;
Response.ContentType = "application/json";
Response.Write(json);
Response.Redirect("/path");
Response.Cookies.Add(new HttpCookie("name", "value"));

// NEW: .NET 10
Response.StatusCode = 200;
Response.ContentType = "application/json";
await Response.WriteAsync(json);
Response.Redirect("/path");
Response.Cookies.Append("name", "value", new CookieOptions { HttpOnly = true });
```

## Configuration

### ConfigurationManager → IConfiguration

```csharp
// OLD: .NET Framework
public class MyService
{
    private readonly string _connectionString;
    private readonly string _apiKey;

    public MyService()
    {
        _connectionString = ConfigurationManager.ConnectionStrings["Default"].ConnectionString;
        _apiKey = ConfigurationManager.AppSettings["ApiKey"];
    }
}

// NEW: .NET 10
public class MyService
{
    private readonly string _connectionString;
    private readonly string _apiKey;

    public MyService(IConfiguration configuration)
    {
        _connectionString = configuration.GetConnectionString("Default")!;
        _apiKey = configuration["ApiKey"]!;
    }
}

// Or use Options pattern
public class MySettings
{
    public string ApiKey { get; set; } = string.Empty;
    public int Timeout { get; set; }
}

public class MyService
{
    private readonly MySettings _settings;

    public MyService(IOptions<MySettings> options)
    {
        _settings = options.Value;
    }
}

// Registration
builder.Services.Configure<MySettings>(builder.Configuration.GetSection("MySettings"));
```

### Web.config → appsettings.json

```xml
<!-- OLD: Web.config -->
<configuration>
  <connectionStrings>
    <add name="Default" connectionString="Server=...;Database=..." />
  </connectionStrings>
  <appSettings>
    <add key="ApiKey" value="secret123" />
    <add key="MaxItems" value="100" />
  </appSettings>
</configuration>
```

```json
// NEW: appsettings.json
{
  "ConnectionStrings": {
    "Default": "Server=...;Database=..."
  },
  "ApiKey": "secret123",
  "MaxItems": 100,
  "MySettings": {
    "ApiKey": "secret123",
    "Timeout": 30
  }
}
```

## Logging

### log4net/NLog → ILogger

```csharp
// OLD: .NET Framework
private static readonly ILog Log = LogManager.GetLogger(typeof(MyService));

public void DoWork()
{
    Log.Info("Starting work");
    try
    {
        // work
        Log.Debug($"Processed {count} items");
    }
    catch (Exception ex)
    {
        Log.Error("Work failed", ex);
    }
}

// NEW: .NET 10
public class MyService
{
    private readonly ILogger<MyService> _logger;

    public MyService(ILogger<MyService> logger)
    {
        _logger = logger;
    }

    public void DoWork()
    {
        _logger.LogInformation("Starting work");
        try
        {
            // work
            _logger.LogDebug("Processed {Count} items", count);  // Structured logging
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Work failed");
        }
    }
}
```

## Caching

### MemoryCache / HttpRuntime.Cache → IMemoryCache

```csharp
// OLD: .NET Framework
public class CacheService
{
    public T Get<T>(string key)
    {
        return (T)MemoryCache.Default.Get(key);
    }

    public void Set<T>(string key, T value, int minutes)
    {
        MemoryCache.Default.Set(key, value, DateTimeOffset.Now.AddMinutes(minutes));
    }
}

// NEW: .NET 10
public class CacheService
{
    private readonly IMemoryCache _cache;

    public CacheService(IMemoryCache cache)
    {
        _cache = cache;
    }

    public T? Get<T>(string key)
    {
        return _cache.Get<T>(key);
    }

    public void Set<T>(string key, T value, int minutes)
    {
        _cache.Set(key, value, TimeSpan.FromMinutes(minutes));
    }

    public T GetOrCreate<T>(string key, Func<T> factory, int minutes)
    {
        return _cache.GetOrCreate(key, entry =>
        {
            entry.AbsoluteExpirationRelativeToNow = TimeSpan.FromMinutes(minutes);
            return factory();
        })!;
    }
}

// Registration
builder.Services.AddMemoryCache();
```

## Session

### Session → ISession

```csharp
// OLD: .NET Framework
Session["UserId"] = userId;
var userId = (int)Session["UserId"];

// NEW: .NET 10
// Setup in Program.cs
builder.Services.AddSession(options =>
{
    options.IdleTimeout = TimeSpan.FromMinutes(30);
    options.Cookie.HttpOnly = true;
    options.Cookie.IsEssential = true;
});
app.UseSession();

// Usage (extension methods)
HttpContext.Session.SetInt32("UserId", userId);
var userId = HttpContext.Session.GetInt32("UserId");

// For complex objects
HttpContext.Session.SetString("User", JsonSerializer.Serialize(user));
var user = JsonSerializer.Deserialize<User>(HttpContext.Session.GetString("User")!);
```

## Entity Framework 6 → EF Core

### DbContext Changes

```csharp
// OLD: EF6
public class MyDbContext : DbContext
{
    public MyDbContext() : base("name=DefaultConnection") { }

    public DbSet<User> Users { get; set; }
}

// NEW: EF Core
public class MyDbContext : DbContext
{
    public MyDbContext(DbContextOptions<MyDbContext> options) : base(options) { }

    public DbSet<User> Users => Set<User>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.ApplyConfigurationsFromAssembly(typeof(MyDbContext).Assembly);
    }
}

// Registration
builder.Services.AddDbContext<MyDbContext>(options =>
    options.UseSqlServer(builder.Configuration.GetConnectionString("Default")));
```

### Query Changes

```csharp
// OLD: EF6
var users = context.Users
    .Include("Department")
    .Where(u => u.IsActive)
    .ToList();

var result = context.Database.SqlQuery<UserDto>("SELECT * FROM Users WHERE Active = 1").ToList();

// NEW: EF Core
var users = await context.Users
    .Include(u => u.Department)  // Lambda instead of string
    .Where(u => u.IsActive)
    .ToListAsync();

var result = await context.Database
    .SqlQueryRaw<UserDto>("SELECT * FROM Users WHERE Active = 1")
    .ToListAsync();
```

### Entity State

```csharp
// OLD: EF6
context.Entry(entity).State = EntityState.Modified;
context.Entry(entity).CurrentValues.SetValues(updated);

// NEW: EF Core (same API)
context.Entry(entity).State = EntityState.Modified;
context.Entry(entity).CurrentValues.SetValues(updated);

// EF Core addition: Update without loading
context.Users.Where(u => u.DepartmentId == oldId)
    .ExecuteUpdate(s => s.SetProperty(u => u.DepartmentId, newId));
```

## Web API Controllers

### ApiController → ControllerBase

```csharp
// OLD: .NET Framework Web API
public class UsersController : ApiController
{
    public IHttpActionResult Get()
    {
        var users = _service.GetUsers();
        return Ok(users);
    }

    public IHttpActionResult Get(int id)
    {
        var user = _service.GetUser(id);
        if (user == null)
            return NotFound();
        return Ok(user);
    }

    public IHttpActionResult Post([FromBody] UserDto dto)
    {
        if (!ModelState.IsValid)
            return BadRequest(ModelState);

        var user = _service.CreateUser(dto);
        return Created($"/api/users/{user.Id}", user);
    }
}

// NEW: .NET 10
[ApiController]
[Route("api/[controller]")]
public class UsersController : ControllerBase
{
    private readonly IUserService _service;

    public UsersController(IUserService service)
    {
        _service = service;
    }

    [HttpGet]
    public async Task<ActionResult<IEnumerable<UserDto>>> Get()
    {
        var users = await _service.GetUsersAsync();
        return Ok(users);
    }

    [HttpGet("{id}")]
    public async Task<ActionResult<UserDto>> Get(int id)
    {
        var user = await _service.GetUserAsync(id);
        if (user == null)
            return NotFound();
        return Ok(user);
    }

    [HttpPost]
    public async Task<ActionResult<UserDto>> Post(UserDto dto)
    {
        // Validation automatic with [ApiController]
        var user = await _service.CreateUserAsync(dto);
        return CreatedAtAction(nameof(Get), new { id = user.Id }, user);
    }
}
```

## Dependency Injection

### Unity/Autofac → Built-in DI

```csharp
// OLD: Unity in .NET Framework
var container = new UnityContainer();
container.RegisterType<IUserService, UserService>();
container.RegisterType<IDbContext, MyDbContext>(new PerRequestLifetimeManager());

// OLD: Autofac
var builder = new ContainerBuilder();
builder.RegisterType<UserService>().As<IUserService>();
builder.RegisterType<MyDbContext>().As<IDbContext>().InstancePerRequest();

// NEW: .NET 10 Built-in DI
builder.Services.AddScoped<IUserService, UserService>();
builder.Services.AddDbContext<MyDbContext>();  // Scoped by default

// Transient (new instance each time)
builder.Services.AddTransient<IEmailService, EmailService>();

// Singleton
builder.Services.AddSingleton<ICacheService, CacheService>();

// Factory
builder.Services.AddScoped<IOrderProcessor>(sp =>
{
    var config = sp.GetRequiredService<IConfiguration>();
    var logger = sp.GetRequiredService<ILogger<OrderProcessor>>();
    return new OrderProcessor(config["OrderApi"]!, logger);
});
```

## Exception Handling

### Global Exception Handler

```csharp
// OLD: .NET Framework (Global.asax)
protected void Application_Error()
{
    var ex = Server.GetLastError();
    // Log and handle
}

// NEW: .NET 10 (Middleware)
public class ExceptionMiddleware
{
    private readonly RequestDelegate _next;
    private readonly ILogger<ExceptionMiddleware> _logger;

    public ExceptionMiddleware(RequestDelegate next, ILogger<ExceptionMiddleware> logger)
    {
        _next = next;
        _logger = logger;
    }

    public async Task InvokeAsync(HttpContext context)
    {
        try
        {
            await _next(context);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Unhandled exception");
            await HandleExceptionAsync(context, ex);
        }
    }

    private static async Task HandleExceptionAsync(HttpContext context, Exception ex)
    {
        context.Response.ContentType = "application/problem+json";
        context.Response.StatusCode = StatusCodes.Status500InternalServerError;

        var problem = new ProblemDetails
        {
            Status = 500,
            Title = "An error occurred",
            Detail = ex.Message  // Remove in production
        };

        await context.Response.WriteAsJsonAsync(problem);
    }
}

// Registration
app.UseMiddleware<ExceptionMiddleware>();
// Or use built-in
app.UseExceptionHandler("/error");
```

## File Uploads

```csharp
// OLD: .NET Framework
[HttpPost]
public IHttpActionResult Upload()
{
    var file = HttpContext.Current.Request.Files[0];
    var path = HttpContext.Current.Server.MapPath("~/uploads");
    file.SaveAs(Path.Combine(path, file.FileName));
    return Ok();
}

// NEW: .NET 10
[HttpPost]
public async Task<IActionResult> Upload(IFormFile file)
{
    if (file == null || file.Length == 0)
        return BadRequest("No file uploaded");

    var uploadsPath = Path.Combine(_environment.ContentRootPath, "uploads");
    Directory.CreateDirectory(uploadsPath);

    var filePath = Path.Combine(uploadsPath, file.FileName);
    using var stream = new FileStream(filePath, FileMode.Create);
    await file.CopyToAsync(stream);

    return Ok(new { file.FileName, file.Length });
}
```

## Background Tasks

```csharp
// OLD: .NET Framework (Timer or Thread)
public class BackgroundService
{
    private Timer _timer;

    public void Start()
    {
        _timer = new Timer(DoWork, null, TimeSpan.Zero, TimeSpan.FromMinutes(5));
    }

    private void DoWork(object state)
    {
        // Background work
    }
}

// NEW: .NET 10 (BackgroundService)
public class MyBackgroundService : BackgroundService
{
    private readonly IServiceProvider _services;
    private readonly ILogger<MyBackgroundService> _logger;

    public MyBackgroundService(IServiceProvider services, ILogger<MyBackgroundService> logger)
    {
        _services = services;
        _logger = logger;
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        while (!stoppingToken.IsCancellationRequested)
        {
            using var scope = _services.CreateScope();
            var service = scope.ServiceProvider.GetRequiredService<IMyService>();

            try
            {
                await service.DoWorkAsync(stoppingToken);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Background task failed");
            }

            await Task.Delay(TimeSpan.FromMinutes(5), stoppingToken);
        }
    }
}

// Registration
builder.Services.AddHostedService<MyBackgroundService>();
```
