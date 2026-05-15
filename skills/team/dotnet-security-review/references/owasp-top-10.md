# OWASP Top 10 (2021) - .NET Reference

Detailed guidance for identifying OWASP Top 10 vulnerabilities in .NET applications.

---

## A01:2021 - Broken Access Control

**Risk**: Users can act outside their intended permissions.

### What to Look For

**Missing Authorization**:
```csharp
// BAD: No authorization check
[HttpGet]
public IActionResult GetUserData(int userId) { }

// GOOD: Authorization required
[Authorize]
[HttpGet]
public IActionResult GetUserData(int userId) { }
```

**Insecure Direct Object Reference (IDOR)**:
```csharp
// BAD: No ownership check
public async Task<Order> GetOrder(int orderId)
{
    return await _context.Orders.FindAsync(orderId);
}

// GOOD: Verify ownership
public async Task<Order> GetOrder(int orderId)
{
    var order = await _context.Orders.FindAsync(orderId);
    if (order.UserId != _currentUser.Id)
        throw new UnauthorizedAccessException();
    return order;
}
```

**Path Traversal**:
```csharp
// BAD: User-controlled path
var path = Path.Combine(uploadsFolder, userInput);
return File.ReadAllBytes(path);

// GOOD: Validate and sanitize
var safeName = Path.GetFileName(userInput);
var path = Path.Combine(uploadsFolder, safeName);
```

### Search Patterns
```bash
grep -rn "\[AllowAnonymous\]" --include="*.cs"
grep -rn "FindAsync\|FirstOrDefault\|SingleOrDefault" --include="*.cs"
grep -rn "Path\.Combine.*Request\|Path\.Combine.*input" --include="*.cs"
```

### Manager Explanation
> "Access control issues allow users to view or modify data belonging to other users, or perform actions they shouldn't be authorized to do. This could lead to data breaches or unauthorized transactions."

---

## A02:2021 - Cryptographic Failures

**Risk**: Sensitive data exposed due to weak or missing encryption.

### What to Look For

**Weak Algorithms**:
```csharp
// BAD: Weak/deprecated algorithms
var md5 = MD5.Create();
var sha1 = SHA1.Create();
var des = DES.Create();

// GOOD: Strong algorithms
var sha256 = SHA256.Create();
var aes = Aes.Create();
```

**Hardcoded Secrets**:
```csharp
// BAD: Hardcoded credentials
var connectionString = "Server=prod;Password=secret123;";
var apiKey = "sk-live-abc123";

// GOOD: Use configuration/secrets management
var connectionString = Configuration.GetConnectionString("Default");
var apiKey = Configuration["ApiKey"];
```

**Missing Encryption**:
```csharp
// BAD: Sensitive data in plain text
user.SSN = request.SSN;

// GOOD: Encrypt sensitive data
user.SSN = _encryptionService.Encrypt(request.SSN);
```

### Search Patterns
```bash
grep -rn "MD5\|SHA1\|DES\|TripleDES\|RC2\|RC4" --include="*.cs"
grep -rn "password\s*=\s*\"\|Password\s*=\s*\"" --include="*.cs" --include="*.json" --include="*.config"
grep -rn "connectionString.*Password" --include="*.config" --include="*.json"
```

### Manager Explanation
> "Cryptographic failures expose sensitive information like passwords, credit cards, or personal data. Using outdated encryption or storing secrets in code makes it easier for attackers to access protected information."

---

## A03:2021 - Injection

**Risk**: Untrusted data sent to an interpreter as part of a command.

### What to Look For

**SQL Injection**:
```csharp
// BAD: String concatenation
var query = "SELECT * FROM Users WHERE Name = '" + userName + "'";
var result = context.Users.FromSqlRaw(query);

// GOOD: Parameterized queries
var result = context.Users.FromSqlRaw(
    "SELECT * FROM Users WHERE Name = {0}", userName);

// BETTER: Use LINQ
var result = context.Users.Where(u => u.Name == userName);
```

**Command Injection**:
```csharp
// BAD: User input in shell command
Process.Start("cmd", "/c ping " + userInput);

// GOOD: Avoid shell, use arguments array
var psi = new ProcessStartInfo("ping") {
    Arguments = validatedHostname,
    UseShellExecute = false
};
```

**XSS (Cross-Site Scripting)**:
```csharp
// BAD: Raw HTML output
@Html.Raw(userContent)
<div>@((MarkupString)userContent)</div>

// GOOD: Encoded output (default in Razor)
@userContent
<div>@userContent</div>
```

### Search Patterns
```bash
grep -rn "FromSqlRaw\|ExecuteSqlRaw\|SqlCommand\|OleDbCommand" --include="*.cs"
grep -rn "Process\.Start\|ProcessStartInfo" --include="*.cs"
grep -rn "Html\.Raw\|MarkupString" --include="*.cs" --include="*.cshtml" --include="*.razor"
grep -rn "innerHTML\|document\.write" --include="*.js" --include="*.ts"
```

### Manager Explanation
> "Injection attacks allow attackers to send malicious commands through the application. This could let them steal data, modify records, or even take control of servers."

---

## A04:2021 - Insecure Design

**Risk**: Missing or ineffective security controls in the design.

### What to Look For

**Missing Rate Limiting**:
```csharp
// BAD: No rate limiting on sensitive endpoint
[HttpPost]
public async Task<IActionResult> Login(LoginRequest request) { }

// GOOD: Rate limited
[HttpPost]
[EnableRateLimiting("login")]
public async Task<IActionResult> Login(LoginRequest request) { }
```

**Missing Business Logic Validation**:
```csharp
// BAD: No quantity validation
public async Task<IActionResult> Purchase(int quantity)
{
    var total = quantity * item.Price;
    // Process payment
}

// GOOD: Validate business rules
public async Task<IActionResult> Purchase(int quantity)
{
    if (quantity <= 0 || quantity > MaxQuantity)
        return BadRequest();
    // Continue...
}
```

### Search Patterns
```bash
grep -rn "TODO.*security\|FIXME.*auth\|HACK" --include="*.cs"
grep -rn "RateLimiting\|Throttle" --include="*.cs"
```

### Manager Explanation
> "Insecure design means the application lacks fundamental security controls. Even if the code is bug-free, missing safeguards like rate limiting or transaction verification leave the system vulnerable."

---

## A05:2021 - Security Misconfiguration

**Risk**: Insecure default configurations or missing security hardening.

### What to Look For

**Debug Mode in Production**:
```json
// BAD: appsettings.Production.json
{
  "Logging": {
    "LogLevel": { "Default": "Debug" }
  }
}

// web.config
<compilation debug="true" />
```

**Permissive CORS**:
```csharp
// BAD: Allow all origins
builder.Services.AddCors(options => {
    options.AddPolicy("All", policy => {
        policy.AllowAnyOrigin()
              .AllowAnyMethod()
              .AllowAnyHeader();
    });
});

// GOOD: Specific origins
builder.Services.AddCors(options => {
    options.AddPolicy("Production", policy => {
        policy.WithOrigins("https://myapp.com")
              .AllowCredentials();
    });
});
```

**Missing Security Headers**:
```csharp
// Should be present
app.UseHsts();
app.UseHttpsRedirection();

// Consider adding
app.Use(async (context, next) => {
    context.Response.Headers.Add("X-Content-Type-Options", "nosniff");
    context.Response.Headers.Add("X-Frame-Options", "DENY");
    context.Response.Headers.Add("Content-Security-Policy", "default-src 'self'");
    await next();
});
```

### Search Patterns
```bash
grep -rn "AllowAnyOrigin\|AllowAnyMethod" --include="*.cs"
grep -rn "debug.*true\|Debug.*true" --include="*.json" --include="*.config"
grep -rn "UseHsts\|UseHttpsRedirection" --include="*.cs"
```

### Manager Explanation
> "Security misconfiguration is like leaving doors unlocked. Default settings, debug modes, or overly permissive rules can expose internal information or allow unauthorized access."

---

## A06:2021 - Vulnerable and Outdated Components

**Risk**: Using components with known vulnerabilities.

### What to Look For

See the `supply-chain-audit` skill (NuGet-specific review section) for comprehensive NuGet package analysis.

```bash
dotnet list package --vulnerable
dotnet list package --outdated
```

### Manager Explanation
> "Using outdated software components is like using a lock with a known flaw. Attackers know these weaknesses and actively scan for applications using vulnerable versions."

---

## A07:2021 - Identification and Authentication Failures

**Risk**: Weaknesses in authentication mechanisms.

### What to Look For

**Weak Password Requirements**:
```csharp
// BAD: Weak password policy
options.Password.RequiredLength = 4;
options.Password.RequireDigit = false;

// GOOD: Strong password policy
options.Password.RequiredLength = 12;
options.Password.RequireDigit = true;
options.Password.RequireUppercase = true;
options.Password.RequireLowercase = true;
options.Password.RequireNonAlphanumeric = true;
```

**Missing Account Lockout**:
```csharp
// BAD: No lockout
options.Lockout.AllowedForNewUsers = false;

// GOOD: Enable lockout
options.Lockout.AllowedForNewUsers = true;
options.Lockout.MaxFailedAccessAttempts = 5;
options.Lockout.DefaultLockoutTimeSpan = TimeSpan.FromMinutes(15);
```

**Session Issues**:
```csharp
// BAD: Long session timeout
options.ExpireTimeSpan = TimeSpan.FromDays(30);

// GOOD: Reasonable timeout with sliding
options.ExpireTimeSpan = TimeSpan.FromHours(2);
options.SlidingExpiration = true;
```

### Search Patterns
```bash
grep -rn "RequiredLength\|RequireDigit\|RequireUppercase" --include="*.cs"
grep -rn "MaxFailedAccessAttempts\|Lockout" --include="*.cs"
grep -rn "ExpireTimeSpan\|SessionTimeout" --include="*.cs"
```

### Manager Explanation
> "Authentication failures allow attackers to compromise accounts through weak passwords, brute force attacks, or session hijacking. This could give them access to user accounts or administrative functions."

---

## A08:2021 - Software and Data Integrity Failures

**Risk**: Code or data from untrusted sources without verification.

### What to Look For

**Insecure Deserialization**:
```csharp
// BAD: BinaryFormatter (NEVER use)
var formatter = new BinaryFormatter();
var obj = formatter.Deserialize(stream);

// BAD: JSON with TypeNameHandling
JsonConvert.DeserializeObject<object>(json, new JsonSerializerSettings {
    TypeNameHandling = TypeNameHandling.All
});

// GOOD: Type-safe deserialization
var obj = JsonSerializer.Deserialize<MyClass>(json);
```

**Missing Integrity Checks**:
```csharp
// BAD: No verification of downloaded content
var content = await httpClient.GetStringAsync(url);
Execute(content);

// GOOD: Verify signature/hash
var content = await httpClient.GetStringAsync(url);
if (!VerifySignature(content, expectedSignature))
    throw new SecurityException();
```

### Search Patterns
```bash
grep -rn "BinaryFormatter\|SoapFormatter\|NetDataContractSerializer" --include="*.cs"
grep -rn "TypeNameHandling" --include="*.cs"
grep -rn "Deserialize\|DeserializeObject" --include="*.cs"
```

### Manager Explanation
> "Data integrity failures allow attackers to inject malicious code or tamper with data the application trusts. This could lead to remote code execution or data manipulation."

---

## A09:2021 - Security Logging and Monitoring Failures

**Risk**: Insufficient logging to detect and respond to attacks.

### What to Look For

**Missing Authentication Logging**:
```csharp
// BAD: No logging
public async Task<IActionResult> Login(LoginRequest request)
{
    var result = await _signInManager.PasswordSignInAsync(...);
    return result.Succeeded ? Ok() : Unauthorized();
}

// GOOD: Log security events
public async Task<IActionResult> Login(LoginRequest request)
{
    var result = await _signInManager.PasswordSignInAsync(...);
    if (result.Succeeded)
        _logger.LogInformation("User {User} logged in", request.Username);
    else
        _logger.LogWarning("Failed login attempt for {User}", request.Username);
    return result.Succeeded ? Ok() : Unauthorized();
}
```

**Logging Sensitive Data**:
```csharp
// BAD: Logging sensitive data
_logger.LogInformation("Login attempt: {User}/{Password}", user, password);

// GOOD: Never log credentials
_logger.LogInformation("Login attempt for user: {User}", user);
```

### Search Patterns
```bash
grep -rn "ILogger\|_logger\.\|Log\." --include="*.cs" | head -50
grep -rn "catch.*Exception" --include="*.cs" | grep -v "Log\|log" | head -20
```

### Manager Explanation
> "Without proper logging, we cannot detect attacks in progress or investigate incidents after they occur. This delays response time and makes it harder to understand what happened during a breach."

---

## A10:2021 - Server-Side Request Forgery (SSRF)

**Risk**: Application fetches URLs provided by users without validation.

### What to Look For

**Unvalidated URL Fetch**:
```csharp
// BAD: User-controlled URL
[HttpGet]
public async Task<IActionResult> Fetch(string url)
{
    var content = await _httpClient.GetStringAsync(url);
    return Ok(content);
}

// GOOD: Validate against allowlist
[HttpGet]
public async Task<IActionResult> Fetch(string url)
{
    if (!IsAllowedUrl(url))
        return BadRequest("URL not allowed");
    var content = await _httpClient.GetStringAsync(url);
    return Ok(content);
}
```

### Search Patterns
```bash
grep -rn "HttpClient\|WebClient\|WebRequest" --include="*.cs"
grep -rn "GetAsync\|PostAsync\|GetStringAsync" --include="*.cs"
grep -rn "new Uri\(" --include="*.cs" | grep -v "\"http"
```

### Manager Explanation
> "SSRF allows attackers to make the server access internal resources or external services on their behalf. This could expose internal systems or be used to attack other services."
