# Principles, Knowledge Lookups, Discipline & Recovery

> Depth for the Controller API Scaffolder. SKILL.md carries the lean intent; this file
> carries the full principle set, knowledge-base queries, discipline rules, anti-patterns,
> and error-recovery procedures.

## Domain Principles Table

| # | Principle | Description | Priority |
|---|-----------|-------------|----------|
| 1 | **Convention Inventory** | Before writing, identify the base controller, validation approach, data/service boundary, response envelope, routing template, versioning scheme, and auth default in use. The inventory drives every later choice. | Critical |
| 2 | **Match the Data Boundary** | If controllers call a service layer (`IUserService`), generate that. If they `mediator.Send()`, generate that. If they hit `DbContext` directly, match it (and flag the smell, do not silently "fix" it). | Critical |
| 3 | **Match the Validation Style** | DataAnnotations on DTOs with automatic `[ApiController]` 400s, OR injected `IValidator<T>` (FluentValidation) — whichever the project uses. Never mix styles into one controller. | Critical |
| 4 | **`[ProducesResponseType]` Everywhere** | Every action declares all status codes (`[ProducesResponseType<T>(200)]`, `404`, `400`…) so OpenAPI/Swagger and clients see the full contract. | Critical |
| 5 | **Attribute Routing & Verbs** | RESTful verbs and routes: `[HttpGet("{id:int}")]`, `[HttpPost]`, proper status codes (`CreatedAtAction` for 201, `NoContent` for 204). | Critical |
| 6 | **DTOs at the Boundary** | Requests and responses are DTOs/records. Domain entities never cross the controller boundary in either direction. | Critical |
| 7 | **Authorization Default** | Match the project default — class-level `[Authorize]` with explicit `[AllowAnonymous]` opt-out is preferred. Never leave a new mutating endpoint unintentionally anonymous. | Critical |
| 8 | **Versioning Consistency** | Adopt the existing versioning scheme (URL segment, header, or query) exactly — do not introduce a second scheme. | High |
| 9 | **CancellationToken Flow** | Every async action accepts `CancellationToken` and propagates it through the service/mediator call chain. | High |
| 10 | **Async All The Way** | Actions are `async Task<ActionResult<T>>`; no `.Result`/`.Wait()`; data access is awaited. | High |

## Knowledge Base Lookups

| Query | When to Call |
|-------|--------------|
| `search_knowledge("ASP.NET Core controller ApiController attribute routing ActionResult")` | At DETECT/SCAFFOLD — confirm current controller + attribute-routing patterns |
| `search_knowledge("ASP.NET Core model validation DataAnnotations ApiController automatic 400")` | When the project uses DataAnnotations — confirm automatic validation behavior |
| `search_knowledge("ASP.NET Core FluentValidation controller IValidator inject")` | When the project uses FluentValidation — confirm injection pattern |
| `search_knowledge("ASP.NET Core ProblemDetails RFC 7807 controller error handling")` | At SECURE/DOCUMENT — confirm ProblemDetails and global exception handling |
| `search_knowledge("ASP.NET Core API versioning controller URL segment header")` | When matching the versioning scheme |
| `search_knowledge("ASP.NET Core authorization policy controller Authorize")` | At SECURE — confirm authorization attribute and policy patterns |

ASP.NET Core platform APIs change across versions. Prefer the **Microsoft Learn MCP**
for official ASP.NET Core controller/validation/versioning docs; use `grounded_dotnet`
for book and Telerik specifics. Generated code must use confirmed API signatures for
the detected `<TargetFramework>` — never training-data assumptions. Cite source paths
in generated file headers.

## AI Discipline Rules

**Run DETECT before writing a single line.** The convention profile is a prerequisite,
not a formality. If the project mixes styles, adopt the **dominant** one and say so; if
there is genuinely no dominant pattern, surface the ambiguity and ask — do not pick for
the team silently.

**Derive from `ControllerBase`, never `Controller`, for APIs.** `Controller` pulls in
view/rendering concerns an API does not need. Always pair with `[ApiController]` to get
automatic 400s, binding-source inference, and ProblemDetails.

**Match the data boundary exactly.** A service-layer project gets a `IXxxService`
injection; a mediator project gets `mediator.Send()`. Never introduce a mediator,
repository, or CQRS split into a project that does not already use it — that is an
architecture decision, not a scaffolding choice. If you see direct `DbContext` use in
controllers, match it to stay consistent but flag it as a finding for a separate refactor.

**Never invent a second validation or versioning scheme.** One validation style per
controller, matching the project. One versioning scheme per project. Adding a competing
scheme fragments the API surface.

**Keep actions thin and async.** Bind → validate → delegate → map → return a typed
`ActionResult<T>`. Accept and propagate `CancellationToken`. No business logic, no inline
EF queries, no per-action `try/catch` when a global exception handler exists.

## Anti-Patterns Table

| # | Anti-Pattern | Problem | Correct Approach |
|---|-------------|---------|------------------|
| 1 | **Scaffolding before detecting** | New controller clashes with team conventions; fails review | Run DETECT, emit the profile, then generate to match |
| 2 | **Imposing CQRS/mediator** | Forces an architecture the team did not choose | Generate the service-layer call the project already uses |
| 3 | **Deriving from `Controller`** | Drags MVC view machinery into an API | `ControllerBase` + `[ApiController]` |
| 4 | **Returning entities** | Leaks the data model; over-posting and serialization risk | Request/response DTOs only |
| 5 | **Fat controller actions** | Business logic + EF queries inline; untestable | Delegate to the service/mediator boundary |
| 6 | **Missing `[ProducesResponseType]`** | OpenAPI shows an incomplete contract | Declare every status code per action |
| 7 | **Mixed validation styles** | DataAnnotations and FluentValidation in one controller | One style, matching the project |
| 8 | **Per-action try/catch** | Duplicates error handling already centralized | Let a global exception handler produce ProblemDetails |
| 9 | **Silent anonymous endpoints** | Forgetting `[Authorize]` exposes mutating actions | Class-level `[Authorize]`, explicit `[AllowAnonymous]` |
| 10 | **String/`object` returns** | No type safety, no schema | `ActionResult<TDto>` with typed DTOs |

## Error Recovery

**No dominant convention (mixed service layer + mediator + direct DbContext):** Do not
guess. Report the mix with file:line evidence, recommend the team pick one, and — if they
must proceed — generate against the style used by the most recently modified controllers,
labeling the choice explicitly.

**Project is Minimal-API based, not controllers:** Stop and route to
`minimal-api-scaffolder`. Do not bolt controllers onto a Minimal API project without an
explicit decision to run both paradigms.

**Custom response envelope (`ApiResponse<T>`) detected:** Match it exactly — return the
envelope, not raw DTOs or bare `Ok(dto)`. Mirror how existing actions populate
success/error fields. A new endpoint returning a different shape breaks every client
that expects the envelope.

**Automatic 400 vs. manual validation conflict:** With `[ApiController]` + DataAnnotations,
model-state 400s are automatic — do not add manual `if (!ModelState.IsValid)`. With
FluentValidation, the project may suppress automatic model-state filtering; match whichever
is configured in `Program.cs`/`Startup.cs` rather than assuming.

**.NET Framework / legacy `ApiController` (System.Web.Http):** This skill targets ASP.NET
Core. If the project is classic ASP.NET Web API on .NET Framework, note it and route to
`legacy-migration-analyzer` before scaffolding new endpoints into a framework slated for
migration.
