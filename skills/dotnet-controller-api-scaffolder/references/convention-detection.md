# Convention Detection Reference

> The DETECT phase is mandatory. These commands inventory an existing controller-based
> codebase so generated controllers match it. Run them from the solution root, read the
> hits, and emit the convention profile before scaffolding anything.

## 1. Target framework(s)

```bash
grep -rhoE "<TargetFramework[s]?>[^<]+" --include="*.csproj" . | sort -u
```

- `net8.0` / `net9.0` / `net10.0` → ASP.NET Core. Proceed.
- `net4*` with `System.Web.Http` → classic ASP.NET Web API. **Stop**, route to `legacy-migration-analyzer`.

## 2. Base controller

```bash
# Find controllers and what they derive from
grep -rE "class \w+Controller\s*:\s*\w+" --include="*.cs" .
# Find a shared base controller
grep -rlE "class \w*(Api)?ControllerBase\b|class Base\w*Controller\b" --include="*.cs" .
```

- If a shared base exists (e.g. `ApiControllerBase : ControllerBase`), **derive from it** and reuse what it offers (a `Mediator` property, a `HandleResult()` helper, a current-user accessor).
- If none exists, derive directly from `ControllerBase` and apply `[ApiController]`.
- Note whether `[ApiController]` sits on the base or on each controller — match the placement.

## 3. Data / service boundary

```bash
# Mediator usage inside controllers
grep -rE "_mediator\.Send|Mediator\.Send|ISender|IMediator" --include="*Controller.cs" .
# Service-layer injection
grep -rE "private readonly I\w+Service|I\w+Service \w+" --include="*Controller.cs" .
# Direct DbContext use in controllers (a smell — match but flag)
grep -rE "DbContext|_context\.|_db\." --include="*Controller.cs" .
```

Decide the **dominant** boundary:

| If most controllers… | Generate |
|----------------------|----------|
| inject `IXxxService` | a service interface + injection + delegation |
| call `mediator.Send()` | command/query + `Send()` (do NOT add mediator if absent elsewhere) |
| use `DbContext` directly | match for consistency, **and** report it as a finding for a separate refactor |

Never introduce a mediator, repository, or CQRS split that the project does not already use.

## 4. Validation approach

```bash
# DataAnnotations on DTOs
grep -rE "\[(Required|StringLength|Range|EmailAddress|MaxLength|RegularExpression)\]" --include="*.cs" .
# FluentValidation
grep -rE "AbstractValidator<|IValidator<|AddValidatorsFrom" --include="*.cs" .
# Is automatic model-state filtering suppressed? (affects manual checks)
grep -rE "SuppressModelStateInvalidFilter|ConfigureApiBehaviorOptions" --include="*.cs" .
```

- DataAnnotations present, FluentValidation absent → annotate DTOs; rely on `[ApiController]` automatic 400s; **do not** add manual `ModelState` checks.
- FluentValidation present → inject `IValidator<T>`, call `ValidateAsync`, return `ValidationProblem`. Check whether automatic filtering is suppressed before deciding manual vs. automatic.
- Both present → match what the **target controller's neighbors** use; never mix within one controller.

## 5. Response shape

```bash
# Bare ActionResult / typed results
grep -rE "ActionResult<|IActionResult|return Ok\(|return NotFound\(" --include="*Controller.cs" .
# Custom envelope
grep -rE "ApiResponse<|Result<|Envelope<|ServiceResult<" --include="*.cs" .
```

- `ActionResult<T>` with `Ok()/NotFound()/CreatedAtAction()` → match.
- A custom envelope (`ApiResponse<T>`, `Result<T>`) → **return the envelope**, populating success/error fields exactly as existing actions do.

## 6. Routing & versioning

```bash
# Route templates
grep -rE "\[Route\(" --include="*Controller.cs" .
# Versioning scheme
grep -rE "ApiVersion|MapToApiVersion|UrlSegmentApiVersionReader|HeaderApiVersionReader|QueryStringApiVersionReader" --include="*.cs" .
```

- Identify the prefix (`api/[controller]`, `api/v{version:apiVersion}/[controller]`) and the versioning reader. Reuse exactly. Do not add a second scheme.

## 7. Authorization default

```bash
grep -rE "\[Authorize|\[AllowAnonymous" --include="*Controller.cs" .
grep -rE "AddAuthorization|AddPolicy|RequireRole|RequireClaim" --include="*.cs" .
```

- Note whether `[Authorize]` sits at class level by default and whether named policies exist. Match the default; reuse policy names rather than inventing new ones.

## 8. DI registration & layout

```bash
# Where services/validators are registered
grep -rnE "services\.Add(Scoped|Transient|Singleton)|builder\.Services\.Add" --include="Program.cs" --include="Startup.cs" .
# Folder layout
find . -type d -name Controllers -o -type d -name Services -o -type d -name DTOs -o -type d -name Models | sort
```

- Register new services/validators at the **same site and lifetime** the project already uses (or matching any assembly-scan registration like `AddValidatorsFromAssembly`).
- Place new files in the existing folders/namespaces; mirror naming (`*Controller`, `*Service`, `*Dto`, `*Request`).

## Convention profile (emit before SCAFFOLD)

```
Target framework : net8.0
Base controller  : ApiControllerBase (provides Mediator, HandleResult)
Data boundary    : service-layer (IXxxService)
Validation       : DataAnnotations (automatic 400, no manual ModelState)
Response shape   : ActionResult<T>
Routing          : api/v{version:apiVersion}/[controller], URL-segment versioning
Auth default     : class-level [Authorize], policies: AdminOnly, SelfOrAdmin
DI site          : Program.cs, scoped; validators via AddValidatorsFromAssembly
Layout           : Controllers/, Services/, Dtos/  (namespace MyApp.Api.*)
```

Confirm the profile with the developer when any aspect is ambiguous or mixed. Only then proceed to SCAFFOLD.
