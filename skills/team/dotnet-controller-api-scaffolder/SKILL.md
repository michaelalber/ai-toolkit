---
name: dotnet-controller-api-scaffolder
audience: team
description: >
  Scaffolds controller-based ASP.NET Core Web API endpoints ([ApiController] /
  ControllerBase) that CONFORM to an existing codebase's conventions — base
  controller, validation approach (DataAnnotations or FluentValidation), service
  layer vs. mediator, response envelope, routing, versioning, and DI registration.
  Detect-and-match, never impose. Use when adding controllers or actions to an
  existing controller-based Web API, or joining a team that ships controller APIs.
  Triggers on "add controller", "scaffold controller", "web api controller",
  "new api controller", "controller endpoint", "[ApiController]", "ControllerBase",
  "add action to controller", "controller-based api".
  Do NOT use for greenfield Minimal APIs — use minimal-api-scaffolder. Do NOT use
  to introduce CQRS/vertical-slice into a layered project — use dotnet-vertical-slice
  only when the team has chosen that style.
---

# ASP.NET Core Controller API Scaffolder

> "When in Rome, do as the Romans do."
> — Ambrose of Milan

> "A good API is not just easy to use but also hard to misuse."
> — Joshua Bloch

## Core Philosophy

This skill adds controller-based Web API endpoints to an **existing** ASP.NET Core
codebase. The codebase already has conventions — a base controller, a validation
style, a way to talk to the data/service layer, a response shape, a routing scheme.
This skill's job is to **detect those conventions and conform to them**, producing
controllers a reviewer cannot distinguish from hand-written team code.

**Non-Negotiable Constraints:**

1. **Detect Before Generate** — No controller is written until the existing conventions are inventoried (base controller, validation, service/mediator boundary, response envelope, routing, versioning, auth). Matching the team beats matching a textbook.
2. **Conform, Don't Convert** — Never refactor existing controllers, swap their validation library, or introduce CQRS/mediator into a service-layer project. New code adopts the dominant existing pattern; style changes are a separate, explicit decision.
3. **`[ApiController]` + Attribute Routing** — Every API controller derives from `ControllerBase` (never `Controller`), carries `[ApiController]`, and uses attribute routing (`[Route]`, `[HttpGet]`…). No convention-based MVC routing for APIs.
4. **Thin Controllers** — Controllers orchestrate: bind, validate, delegate to the service/mediator boundary the project already uses, map to a response. No business logic, no EF queries inline, no `try/catch` per action when a global handler exists.
5. **Typed Contracts & ProblemDetails** — Actions accept and return DTOs (never entities), declare `[ProducesResponseType]` for every status code, and surface errors as RFC 7807 `ProblemDetails` — or the project's existing error envelope if one is established.

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

## Workflow

The lifecycle flows: **DETECT → SCAFFOLD → SECURE → DOCUMENT**. DETECT is mandatory and
gates everything else — its output is the convention profile every later phase obeys.

### Phase 1: DETECT (mandatory)

Inventory the existing conventions. See `references/convention-detection.md` for the grep commands.

- [ ] Target framework(s) — `grep <TargetFramework>` across `.csproj`
- [ ] Base controller — does an `ApiControllerBase` / `BaseApiController` exist? What does it provide?
- [ ] Data/service boundary — service layer (`IXxxService`), mediator (`Send()`), or direct `DbContext`?
- [ ] Validation approach — DataAnnotations attributes vs. FluentValidation `IValidator<T>`
- [ ] Response shape — raw DTO, `ActionResult<T>`, or a custom envelope (`ApiResponse<T>`)?
- [ ] Routing & versioning — route template prefix, versioning scheme (URL/header/query)
- [ ] Authorization default — class-level `[Authorize]`? Policies? Anonymous opt-out?
- [ ] DI registration & folder/namespace layout for controllers, DTOs, services
- [ ] **Emit the convention profile** (see State Block) and confirm it before generating

### Phase 2: SCAFFOLD

Generate controller + DTOs + (validators or annotations) matching the profile.

- [ ] Create the controller deriving from the detected base (or `ControllerBase` + `[ApiController]`)
- [ ] Apply the project's route template and versioning scheme
- [ ] Generate CRUD (or requested) actions with correct verbs and status codes
- [ ] Create request/response DTOs (records) — no entity leakage
- [ ] Add validation in the project's style (DataAnnotations OR `IValidator<T>`)
- [ ] Delegate to the project's data boundary (service OR mediator OR matched DbContext)
- [ ] Register any new service/validator in DI following the existing registration site

### Phase 3: SECURE

- [ ] Apply the authorization default (class-level `[Authorize]`, explicit `[AllowAnonymous]`)
- [ ] Apply specific policies for sensitive actions, matching existing policy names
- [ ] Confirm CORS/rate-limiting are inherited from existing middleware (do not add a second config)
- [ ] Verify no secrets or connection strings are introduced inline

### Phase 4: DOCUMENT

- [ ] Every action declares `[ProducesResponseType]` for all status codes
- [ ] XML doc comments on public actions if the project ships them (`GenerateDocumentationFile`)
- [ ] Swagger/OpenAPI renders the new controller grouped correctly
- [ ] Request/response schemas appear in the OpenAPI document

## State Block Format

```
<controller-scaffold-state>
mode: DETECT | SCAFFOLD | SECURE | DOCUMENT
target_framework: net8.0
base_controller: ApiControllerBase   # or "ControllerBase (none found)"
data_boundary: service-layer         # service-layer | mediator | direct-dbcontext
validation: dataannotations          # dataannotations | fluentvalidation
response_shape: ActionResult<T>      # ActionResult<T> | ApiResponse<T> envelope | raw DTO
versioning: url-segment              # url-segment | header | query | none
auth_default: class-level [Authorize]
controllers_created: [UsersController]
last_action: Detected conventions; emitted profile for confirmation
next_action: Scaffold UsersController matching service-layer + DataAnnotations
</controller-scaffold-state>
```

## Output Templates

```markdown
## Convention Profile: [Solution] | .NET [version]
| Aspect | Detected | New code will |
|--------|----------|--------------|
| Base controller | ApiControllerBase | derive from it |
| Data boundary | IXxxService service layer | inject + delegate |
| Validation | DataAnnotations | annotate DTOs |
| Response shape | ActionResult<T> | match |
| Versioning | /api/v{n} URL segment | match |
| Auth default | class-level [Authorize] | match |

## Controller: [Resource]Controller
Route: /api/v{n}/[resource] | Base: [base] | Auth: [Required/Anonymous]
| Verb | Route | Action | Request DTO | Response DTO | Status Codes |
| GET | / | GetAll | [Query]DTO | PagedResult<T> | 200,401 |
| GET | /{id} | GetById | — | TDto | 200,404,401 |
| POST | / | Create | CreateTRequest | TDto | 201,400,401 |
| PUT | /{id} | Update | UpdateTRequest | — | 204,400,404,401 |
| DELETE | /{id} | Delete | — | — | 204,404,401 |
```

Full controller, DTO, validator, ProblemDetails, and testing templates:
`references/controller-patterns.md`. Convention detection commands:
`references/convention-detection.md`. Auth/CORS/rate-limit/integration-test patterns:
`references/security-and-testing.md`.

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

## Integration with Other Skills

| Skill | Integration Point | When to Use |
|-------|-------------------|-------------|
| **dotnet-architecture-checklist** | Review the controller/N-tier project before and after scaffolding | Confirms the detected style and grades against it |
| **minimal-api-scaffolder** | Sibling for the Minimal API paradigm | When the project is (or should be) Minimal API, not controllers |
| **dotnet-vertical-slice** | Alternative for teams that have chosen CQRS/vertical slice | Only when the team uses that architecture — not for layered projects |
| **test-scaffold** | Generate controller integration tests | `WebApplicationFactory<Program>` tests exercising the new actions |
| **dotnet-security-review** | Security audit of the new endpoints | Verify auth, validation, CORS, and no entity leakage |
| **ef-migration-manager** | Schema changes behind new endpoints | When new actions require entities or migrations |
| **react-feature-slice** | Front-end consumer of these endpoints | Generate the typed React data layer that calls the new controller |

References: `references/convention-detection.md` (detection grep commands + decision rules) |
`references/controller-patterns.md` (controller, DTO, validator, ProblemDetails templates for
service-layer and mediator variants) | `references/security-and-testing.md` (authorization,
CORS, rate limiting, integration tests).
