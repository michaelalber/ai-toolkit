# Telerik UI Security Reference

Comprehensive security guidance for Telerik UI components in .NET applications.

---

## Important: Different Telerik Product Lines

Telerik has **multiple UI product lines** with different security profiles:

| Product | Target Framework | Base Technology | CVE Risk Level |
|---------|------------------|-----------------|----------------|
| **Telerik UI for Blazor** | .NET 6+/Blazor | Native Blazor components | **LOW** |
| **Telerik UI for ASP.NET MVC** | .NET Framework 4.x | Kendo UI (jQuery wrappers) | **MEDIUM** |
| **Telerik UI for ASP.NET AJAX** | .NET Framework 4.x | RadControls (WebForms) | **HIGH** - Multiple critical CVEs |

**Critical CVE history (RadAsyncUpload RCE, etc.) applies to ASP.NET AJAX, NOT MVC or Blazor.**

---

## Part 1: Telerik UI for Blazor (.NET 9+)

Telerik UI for Blazor uses native Blazor components without jQuery dependencies. Different security model than legacy products.

### Security Considerations

| Area | Risk | Guidance |
|------|------|----------|
| TelerikUpload | File upload vulnerabilities | Server-side validation required |
| TelerikEditor | XSS via HTML content | Sanitize output, validate input |
| TelerikGrid | Data exposure, IDOR | Server-side authorization |
| State Management | Sensitive data in circuits | Don't store secrets in component state |

### TelerikUpload Security

```razor
@* Blazor Server - File Upload *@
<TelerikUpload SaveUrl="api/upload/save"
               RemoveUrl="api/upload/remove"
               AllowedExtensions="@(new List<string> { ".jpg", ".png", ".pdf" })"
               MaxFileSize="10485760"
               MinFileSize="1"
               OnUpload="@OnUploadHandler">
</TelerikUpload>

@code {
    private void OnUploadHandler(UploadEventArgs args)
    {
        // Add anti-forgery token to request
        args.RequestHeaders.Add("RequestVerificationToken", AntiForgeryToken);
    }
}
```

**Server-side validation (required):**

```csharp
[HttpPost("api/upload/save")]
[ValidateAntiForgeryToken]
public async Task<IActionResult> Save(IFormFile file)
{
    // Validate file type by content (magic bytes), not just extension
    if (!IsAllowedFileType(file))
        return BadRequest("Invalid file type");

    // Validate size
    if (file.Length > 10 * 1024 * 1024)
        return BadRequest("File too large");

    // Generate safe filename
    var safeFileName = Path.GetRandomFileName() + Path.GetExtension(file.FileName);
    var targetPath = Path.Combine(_uploadPath, safeFileName);

    // Verify path is within allowed directory
    var fullPath = Path.GetFullPath(targetPath);
    if (!fullPath.StartsWith(Path.GetFullPath(_uploadPath)))
        return BadRequest("Invalid path");

    using var stream = new FileStream(targetPath, FileMode.Create);
    await file.CopyToAsync(stream);

    return Ok(new { fileName = safeFileName });
}
```

### TelerikEditor Security

```razor
<TelerikEditor @bind-Value="@EditorContent"
               Tools="@EditorTools">
</TelerikEditor>

@code {
    private string EditorContent { get; set; }

    // Sanitize before saving to database
    private async Task SaveContent()
    {
        var sanitized = _htmlSanitizer.Sanitize(EditorContent);
        await _repository.SaveAsync(sanitized);
    }
}
```

**Use HtmlSanitizer library:**

```csharp
// Install: dotnet add package HtmlSanitizer
using Ganss.Xss;

public class ContentService
{
    private readonly HtmlSanitizer _sanitizer;

    public ContentService()
    {
        _sanitizer = new HtmlSanitizer();
        // Configure allowed tags/attributes as needed
        _sanitizer.AllowedTags.Remove("script");
        _sanitizer.AllowedTags.Remove("iframe");
        _sanitizer.AllowedAttributes.Remove("onerror");
        _sanitizer.AllowedAttributes.Remove("onclick");
    }

    public string Sanitize(string html) => _sanitizer.Sanitize(html);
}
```

### TelerikGrid Security

```razor
<TelerikGrid Data="@GridData"
             OnRead="@OnGridRead"
             Pageable="true"
             PageSize="20">
    <GridColumns>
        <GridColumn Field="@nameof(Order.Id)" />
        <GridColumn Field="@nameof(Order.CustomerName)" />
    </GridColumns>
</TelerikGrid>

@code {
    private async Task OnGridRead(GridReadEventArgs args)
    {
        // CRITICAL: Apply authorization filter server-side
        var userId = _authService.GetCurrentUserId();

        var query = _context.Orders
            .Where(o => o.UserId == userId) // Authorization check
            .AsQueryable();

        // Apply Telerik DataSource request
        var result = await query.ToDataSourceResultAsync(args.Request);
        args.Data = result.Data;
        args.Total = result.Total;
    }
}
```

### Blazor Security Checklist

- [ ] TelerikUpload has server-side file validation (type, size, path)
- [ ] TelerikEditor content sanitized before storage
- [ ] TelerikGrid applies server-side authorization filters
- [ ] Anti-forgery tokens used for state-changing operations
- [ ] No secrets stored in Blazor component state
- [ ] SignalR hub secured (Blazor Server)

---

## Part 2: Telerik UI for ASP.NET MVC (.NET Framework 4.8)

Telerik UI for MVC wraps Kendo UI jQuery components. Different from ASP.NET AJAX (no RadControls).

### Key Components

| Telerik MVC | Underlying | Security Focus |
|-------------|------------|----------------|
| Upload | Kendo Upload | File validation, path traversal |
| Editor | Kendo Editor | XSS, content sanitization |
| Grid | Kendo Grid | Server-side auth, data exposure |

### Kendo Upload Security (MVC)

```csharp
// Controller
[HttpPost]
[ValidateAntiForgeryToken]
public ActionResult Upload(HttpPostedFileBase file)
{
    if (file == null || file.ContentLength == 0)
        return Json(new { success = false, message = "No file" });

    // Validate extension
    var allowedExtensions = new[] { ".jpg", ".png", ".pdf" };
    var extension = Path.GetExtension(file.FileName)?.ToLowerInvariant();
    if (!allowedExtensions.Contains(extension))
        return Json(new { success = false, message = "Invalid file type" });

    // Validate content type
    var allowedTypes = new[] { "image/jpeg", "image/png", "application/pdf" };
    if (!allowedTypes.Contains(file.ContentType))
        return Json(new { success = false, message = "Invalid content type" });

    // Validate size
    if (file.ContentLength > 10 * 1024 * 1024)
        return Json(new { success = false, message = "File too large" });

    // Safe filename
    var safeFileName = Path.GetRandomFileName() + extension;
    var targetPath = Path.Combine(Server.MapPath("~/App_Data/Uploads"), safeFileName);

    // Verify path
    var uploadDir = Server.MapPath("~/App_Data/Uploads");
    if (!Path.GetFullPath(targetPath).StartsWith(uploadDir))
        return Json(new { success = false, message = "Invalid path" });

    file.SaveAs(targetPath);
    return Json(new { success = true, fileName = safeFileName });
}
```

```razor
@* View *@
@(Html.Kendo().Upload()
    .Name("files")
    .Async(a => a
        .Save("Upload", "FileManager")
        .AutoUpload(true))
    .Validation(v => v
        .AllowedExtensions(new[] { ".jpg", ".png", ".pdf" })
        .MaxFileSize(10485760))
)
```

### Kendo Editor Security (MVC)

```csharp
// Controller - Sanitize on save
[HttpPost]
[ValidateAntiForgeryToken]
[ValidateInput(false)] // Required for HTML content
public ActionResult SaveContent(string content)
{
    // Use HtmlSanitizer or similar
    var sanitizer = new HtmlSanitizer();
    var cleanContent = sanitizer.Sanitize(content);

    _repository.Save(cleanContent);
    return Json(new { success = true });
}
```

```razor
@* View *@
@(Html.Kendo().Editor()
    .Name("editor")
    .HtmlAttributes(new { style = "height:400px" })
    .Tools(tools => tools
        .Clear()
        .Bold().Italic().Underline()
        .InsertImage()
        .ViewHtml())
    .ImageBrowser(ib => ib
        .Read("ImageBrowserRead", "Editor")
        .Upload("ImageBrowserUpload", "Editor"))
)
```

### Kendo Grid Security (MVC)

```csharp
// Controller
public ActionResult GetOrders([DataSourceRequest] DataSourceRequest request)
{
    // CRITICAL: Server-side authorization
    var userId = User.Identity.GetUserId();

    var orders = _context.Orders
        .Where(o => o.UserId == userId) // Filter by current user
        .Select(o => new OrderViewModel
        {
            Id = o.Id,
            OrderDate = o.OrderDate,
            Total = o.Total
            // Don't expose sensitive fields
        });

    return Json(orders.ToDataSourceResult(request), JsonRequestBehavior.AllowGet);
}
```

### MVC Security Checklist

- [ ] All upload endpoints validate file type by content
- [ ] All upload endpoints use anti-forgery tokens
- [ ] Editor content sanitized before storage
- [ ] Grid endpoints apply server-side authorization
- [ ] No sensitive data exposed in Grid JSON responses
- [ ] jQuery version is current (check for CVEs)

---

## Part 3: Telerik UI for ASP.NET AJAX (WebForms)

**If your application uses ASP.NET AJAX (RadControls), this section applies.**

### Critical CVE History

| CVE | Component | Risk | Affected Versions | Fixed Version |
|-----|-----------|------|-------------------|---------------|
| CVE-2019-18935 | RadAsyncUpload | Remote Code Execution | Before 2020.1.114 | 2020.1.114+ |
| CVE-2017-11317 | RadAsyncUpload | Remote Code Execution | Before 2017.2.621 | 2017.2.621+ |
| CVE-2017-9248 | Telerik.Web.UI | Cryptographic Weakness | Before 2017.2.621 | 2017.2.621+ |
| CVE-2014-2217 | RadEditor DialogHandler | Path Traversal | Before 2014.1 | 2014.1+ |

### Manager Explanation

> "RadAsyncUpload vulnerabilities have been actively exploited in the wild to achieve remote code execution - complete server takeover. If your application uses Telerik UI for ASP.NET AJAX, version verification is critical."

### RadAsyncUpload Security (if used)

**web.config - Required Settings:**

```xml
<configuration>
  <appSettings>
    <!-- CRITICAL: Use strong, unique keys - NEVER use defaults -->
    <add key="Telerik.AsyncUpload.ConfigurationEncryptionKey"
         value="[GENERATE-32-BYTE-BASE64-KEY]" />
    <add key="Telerik.Upload.ConfigurationHashKey"
         value="[GENERATE-32-BYTE-BASE64-KEY]" />
    <add key="Telerik.Web.UI.DialogParametersEncryptionKey"
         value="[GENERATE-32-BYTE-BASE64-KEY]" />
  </appSettings>
</configuration>
```

### Machine Keys Configuration

```xml
<configuration>
  <system.web>
    <machineKey
      validationKey="[64-BYTE-HEX-KEY]"
      decryptionKey="[32-BYTE-HEX-KEY]"
      validation="HMACSHA256"
      decryption="AES" />
  </system.web>
</configuration>
```

### Generate Secure Keys

```powershell
# Validation key (64 bytes = 128 hex chars)
$bytes = New-Object byte[] 64
[Security.Cryptography.RNGCryptoServiceProvider]::Create().GetBytes($bytes)
$validationKey = -join ($bytes | ForEach-Object { $_.ToString("X2") })
Write-Host "validationKey: $validationKey"

# Decryption key (32 bytes = 64 hex chars)
$bytes = New-Object byte[] 32
[Security.Cryptography.RNGCryptoServiceProvider]::Create().GetBytes($bytes)
$decryptionKey = -join ($bytes | ForEach-Object { $_.ToString("X2") })
Write-Host "decryptionKey: $decryptionKey"

# Base64 key for Telerik settings
$bytes = New-Object byte[] 32
[Security.Cryptography.RNGCryptoServiceProvider]::Create().GetBytes($bytes)
[Convert]::ToBase64String($bytes)
```

### ASP.NET AJAX Security Checklist (Critical)

- [ ] Telerik version is 2020.1.114 or later
- [ ] Custom `ConfigurationEncryptionKey` configured
- [ ] Custom `ConfigurationHashKey` configured
- [ ] Custom `DialogParametersEncryptionKey` configured
- [ ] Custom ASP.NET machine keys configured
- [ ] RadAsyncUpload file restrictions enforced
- [ ] RadEditor `RemoveScripts` filter enabled
- [ ] DialogHandler access restricted

---

## Search Commands

```bash
# Identify which Telerik product is used
grep -rn "Telerik.UI.for.Blazor\|TelerikRootComponent" --include="*.razor" --include="*.cs"
grep -rn "Kendo.Mvc\|Html.Kendo()" --include="*.cshtml" --include="*.cs"
grep -rn "Telerik.Web.UI\|RadAsyncUpload\|RadEditor" --include="*.aspx" --include="*.cs"

# Check package versions
grep -rn "Telerik" --include="*.csproj" --include="packages.config"

# Blazor uploads
grep -rn "TelerikUpload\|SaveUrl" --include="*.razor"

# MVC/Kendo uploads
grep -rn "Kendo.*Upload\|\.Upload(" --include="*.cshtml"

# ASP.NET AJAX RadAsyncUpload
grep -rn "RadAsyncUpload" --include="*.aspx" --include="*.ascx"

# Encryption keys (ASP.NET AJAX)
grep -rn "ConfigurationEncryptionKey\|ConfigurationHashKey" --include="*.config"

# Machine keys
grep -rn "machineKey\|validationKey\|decryptionKey" --include="*.config"

# Editor usage
grep -rn "TelerikEditor\|Kendo.*Editor\|RadEditor" --include="*.razor" --include="*.cshtml" --include="*.aspx"

# Grid authorization patterns
grep -rn "ToDataSourceResult\|OnRead" --include="*.cs" --include="*.razor"
```

---

## References

- Telerik UI for Blazor Security: https://docs.telerik.com/blazor-ui/security
- Telerik UI for MVC Security: https://docs.telerik.com/aspnet-mvc/security
- Telerik UI for AJAX Security: https://docs.telerik.com/devtools/aspnet-ajax/security/security-overview
- Kendo UI Security: https://docs.telerik.com/kendo-ui/security
- HtmlSanitizer: https://github.com/mganss/HtmlSanitizer
- OWASP File Upload: https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html
