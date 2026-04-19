# Python Skill Suite — Implementation Plan (Plan A)

> Plan B (Rust suite) follows after this plan is implemented and verified.

## Overview

Create 8 new Python skills mirroring the .NET suite, each adapted for Python's ecosystem
(FastAPI, Alembic, PyPI, Pydantic, etc.). Add corresponding Claude Code and OpenCode agents
for each skill. `python-arch-review` is already complete and is NOT modified.

## Current state analysis

- 53 skills exist; 0 Python-ecosystem skills beyond `python-arch-review` and `rag-pipeline-python`
- `python-arch-review` is complete (10 sections, 729 lines) — maps to `dotnet-architecture-checklist`
- Gold standard template: `skills/architecture-review/SKILL.md` (610 lines, 10 sections)
- Agent format confirmed: Claude uses `skills:` frontmatter array; OpenCode uses `skill()` body calls
- Every skill needs `references/` directory with ≥ 2 `.md` files
- State block XML tags must be unique across all skills

## Desired end state

- 8 new Python skills, each with full 10-section compliance and ≥ 2 reference files
- 8 new Claude Code agents in `claude/agents/`
- 8 new OpenCode agents in `opencode/agents/`
- Skill count in `AGENTS.md` updated from 53 → 61
- Agent count in `AGENTS.md` updated: Claude 20 → 28, OpenCode 19 → 27
- Skill suites table in `AGENTS.md` updated with new "Python" suite row

## What we're NOT doing

- Modifying `python-arch-review` (already complete)
- Creating Rust skills (Plan B)
- Fixing existing convention violations (shared `<tdd-state>` tags, stale `rag-pipeline` ref, `jira-comment-writer` references gap) — separate task
- Adding the missing `confluence-guide-writer` OpenCode agent — separate task
- Creating a `python-security-review-federal` skill in this plan (federal overlay requires the base security review to exist first; add as Phase 9 after Phase 2 is verified, or defer to a follow-on plan)

## Implementation approach

Each phase creates one skill + its references + its two agent files. Phases are independent
of each other (no skill depends on another new skill). They can be executed in any order,
but sequential execution is recommended to catch template issues early.

Phase 1 (python-security-review) is the template-setter — implement it first and verify
it fully before proceeding. If the template needs adjustment, fix it in Phase 1 before
replicating the pattern across Phases 2–8.

---

## Skill mapping: .NET → Python

| .NET Skill | Python Skill | Key ecosystem difference |
|---|---|---|
| `dotnet-security-review` | `python-security-review` | bandit/pip-audit vs. Snyk; OWASP same baseline |
| `dotnet-security-review-federal` | `python-security-review-federal` | Federal overlay on Python base; NIST/FIPS same |
| `dotnet-vertical-slice` | `python-feature-slice` | FastAPI routers + service layer; no FreeMediator |
| `ef-migration-manager` | `alembic-migration-manager` | Alembic revisions vs. EF Core migrations |
| `legacy-migration-analyzer` | `python-modernization-analyzer` | Python 2→3, Flask→FastAPI, sync→async |
| `minimal-api-scaffolder` | `fastapi-scaffolder` | FastAPI + Pydantic v2 vs. ASP.NET Minimal API |
| `nuget-package-scaffold` | `pypi-package-scaffold` | pyproject.toml + PyPI vs. .csproj + NuGet |
| `4d-schema-migration` | *(no analog — excluded)* | 4D targets .NET/SQL Server only |

`dotnet-architecture-checklist` maps to the existing `python-arch-review` — no new skill needed.

---

## Phase 1: `python-security-review` skill + agents

### Overview

Create the Python security review skill (OWASP baseline with Python-specific tooling:
bandit, pip-audit, safety, semgrep) and its two agent files. This is the template-setter
phase — get the pattern right here before replicating.

### Changes required

#### 1. Create skill directory
**File**: `skills/python-security-review/` (new directory)
**Changes**: Create directory.

#### 2. Create SKILL.md
**File**: `skills/python-security-review/SKILL.md` (new file)
**Changes**: Full 10-section skill following gold standard. Key adaptations from `dotnet-security-review`:
- Title: "Python Security Review (OWASP Baseline)"
- Unique state tag: `<python-security-state>`
- Section 1 epigraph: same Schneier quotes are appropriate
- Section 2 Core Philosophy: Python-specific — bandit replaces Snyk for SAST; pip-audit/safety replace NuGet audit; no Telerik; Django/Flask/FastAPI injection patterns replace Razor/EF patterns
- Section 3 Domain Principles: same 10 principles, adapted — "Telerik Component Security" becomes "Framework-Specific Injection Patterns" (Django ORM raw queries, Flask Jinja2 SSTI, FastAPI query param injection)
- Section 4 Knowledge Base Lookups: `search_knowledge("OWASP python security bandit injection")`, `search_knowledge("pip-audit safety dependency vulnerability python")`, `search_knowledge("FastAPI Django Flask authentication JWT python")`
- Section 5 Workflow: RECONNAISSANCE → SCAN → REPORT → RECOMMEND; bash commands use `find . -name "*.py"`, `bandit -r .`, `pip-audit`, `safety check`
- Section 6 State Block: `<python-security-state>` with fields: phase, framework_detected, auth_mechanism, findings_count, bandit_clean, pip_audit_clean, last_action, next_action
- Section 7 Output Templates: executive summary + technical findings table (same structure as .NET version)
- Section 8 AI Discipline Rules: same 5 rules adapted — "never assert a vulnerability without reading the code", "always run bandit before reporting findings", etc.
- Section 9 Anti-Patterns: same 10 anti-patterns adapted for Python — "Django ORM raw() without parameterization", "hardcoded secrets in settings.py", "debug=True in production", "CORS allow-all in FastAPI", etc.
- Section 10 Error Recovery: 3 scenarios — "bandit false positives", "pip-audit finds no patch", "legacy code with no type hints obscures injection surface"
- Section 11 Integration: `python-arch-review`, `supply-chain-audit`, `python-security-review-federal`, `dotnet-security-review` (cross-reference for teams with mixed stacks)

#### 3. Create references directory
**File**: `skills/python-security-review/references/` (new directory)
**Changes**: Create directory.

#### 4. Create owasp-python-checklist.md reference
**File**: `skills/python-security-review/references/owasp-python-checklist.md` (new file)
**Changes**: Python-specific OWASP Top 10 checklist. Sections:
- A01 Broken Access Control: Django permission decorators, FastAPI `Depends(get_current_user)`, Flask `@login_required`
- A02 Cryptographic Failures: `secrets` module vs `random`, `hashlib` with salt, no MD5/SHA1 for passwords, `bcrypt`/`argon2`
- A03 Injection: parameterized queries (`cursor.execute(sql, params)`), ORM usage, no `eval()`/`exec()` with user input, no `subprocess(shell=True)` with user data
- A04 Insecure Design: no business logic in views, separation of concerns
- A05 Security Misconfiguration: `DEBUG=False` in production, `SECRET_KEY` from env, `ALLOWED_HOSTS` set
- A06 Vulnerable Components: `pip-audit` output interpretation, `safety check` usage
- A07 Auth Failures: JWT validation, session fixation, password hashing
- A08 Software Integrity: dependency pinning, hash verification
- A09 Logging Failures: no passwords/tokens in logs, structured logging
- A10 SSRF: `requests` URL validation, no user-controlled URLs to internal services

#### 5. Create executive-summary-template.md reference
**File**: `skills/python-security-review/references/executive-summary-template.md` (new file)
**Changes**: Manager-friendly report template (mirrors `dotnet-security-review/references/executive-summary-templates.md`). Sections: Risk Summary table, Top 3 Findings in plain language, Remediation Priority matrix, Positive Findings, Recommended Next Steps.

#### 6. Create Claude Code agent
**File**: `claude/agents/python-security-agent.md` (new file)
**Changes**: Agent frontmatter with `name: python-security-agent`, `description` with trigger phrases ("python security review", "audit python code", "check python vulnerabilities", "OWASP python", "bandit scan", "pip-audit"), `tools: Read, Bash, Glob, Grep`, `model: inherit`, `skills: [python-security-review, supply-chain-audit]`. Body: 10-section agent structure with `<python-security-agent-state>` tag.

#### 7. Create OpenCode agent
**File**: `opencode/agents/python-security-agent.md` (new file)
**Changes**: Frontmatter with `description` (same text), `mode: subagent`, `tools: read: true, bash: true, glob: true, grep: true, edit: false, write: false`. Body: same 10-section structure with `skill({ name: "python-security-review" })` and `skill({ name: "supply-chain-audit" })` calls.

### Success criteria

#### Automated verification
- [ ] `ls skills/python-security-review/SKILL.md` exists
- [ ] `ls skills/python-security-review/references/` contains ≥ 2 files
- [ ] `ls claude/agents/python-security-agent.md` exists
- [ ] `ls opencode/agents/python-security-agent.md` exists
- [ ] `grep -c "^## " skills/python-security-review/SKILL.md` returns ≥ 10 (10 sections present)
- [ ] `grep "<python-security-state>" skills/python-security-review/SKILL.md` returns 1 match
- [ ] `grep "python-security-agent-state" claude/agents/python-security-agent.md` returns ≥ 1 match

#### Manual verification
- [ ] SKILL.md sections 1–10 are all present and non-empty
- [ ] State tag `<python-security-state>` is unique (not used in any other skill)
- [ ] Claude agent `skills:` array references `python-security-review`
- [ ] OpenCode agent body contains `skill({ name: "python-security-review" })`

**Implementation note**: Complete and verify Phase 1 fully before starting Phase 2. Phase 1 establishes the template pattern for all subsequent phases.

---

## Phase 2: `python-security-review-federal` skill + agents

### Overview

Federal overlay on `python-security-review`. Mirrors `dotnet-security-review-federal` exactly
in structure — NIST SP 800-53, FIPS 140-2/3, DOE Order 205.1B, POA&M output. The only
difference is the base language is Python, not .NET.

### Changes required

#### 1. Create skill directory and SKILL.md
**File**: `skills/python-security-review-federal/SKILL.md` (new file)
**Changes**: Full 10-section skill. Key adaptations from `dotnet-security-review-federal`:
- Title: "Python Security Review — Federal Edition"
- Unique state tag: `<python-federal-security-state>`
- Core Philosophy: "Base review first, always" — references `python-security-review` (not `dotnet-security-review`)
- Domain Principles: identical 10 principles (NIST/FIPS/DOE requirements are language-agnostic)
- Knowledge Base Lookups: same federal queries (`search_knowledge("NIST SP 800-53 control families python")`, `search_knowledge("FIPS 140-2 cryptography python hashlib")`, `search_knowledge("DOE cybersecurity order 205.1B")`)
- Workflow: same RECONNAISSANCE → BASE REVIEW → FEDERAL OVERLAY → POA&M phases; Python-specific recon commands (`find . -name "*.py"`, `grep -r "hashlib\|cryptography" .`)
- FIPS section: Python `cryptography` library FIPS mode, `hashlib` approved algorithms, no `MD5`/`SHA1` for security purposes
- Output Templates: same POA&M template, same impact level table
- Integration: references `python-security-review` as prerequisite (not `dotnet-security-review`)

#### 2. Create references directory with 2 files
**File**: `skills/python-security-review-federal/references/nist-control-mapping.md` (new file)
**Changes**: NIST SP 800-53 control family → Python implementation checklist. Same structure as `dotnet-security-review-federal` equivalent but with Python examples (e.g., AC-3 Access Enforcement → FastAPI `Depends()` authorization, IA-5 Authenticator Management → `passlib`/`argon2` usage).

**File**: `skills/python-security-review-federal/references/poam-template.md` (new file)
**Changes**: POA&M entry template identical to .NET federal version — language-agnostic format.

#### 3. Create Claude Code agent
**File**: `claude/agents/python-federal-security-agent.md` (new file)
**Changes**: `name: python-federal-security-agent`, trigger phrases ("federal python security", "NIST python", "FISMA python", "DOE python security", "python ATO review"), `tools: Read, Bash, Glob, Grep`, `skills: [python-security-review-federal, python-security-review, supply-chain-audit]`. State tag: `<python-federal-security-agent-state>`.

#### 4. Create OpenCode agent
**File**: `opencode/agents/python-federal-security-agent.md` (new file)
**Changes**: Same as Claude agent, OpenCode format. `skill()` calls for `python-security-review-federal`, `python-security-review`, `supply-chain-audit`.

### Success criteria

#### Automated verification
- [ ] `ls skills/python-security-review-federal/references/` contains ≥ 2 files
- [ ] `grep "<python-federal-security-state>" skills/python-security-review-federal/SKILL.md` returns 1 match
- [ ] `grep -c "^## " skills/python-security-review-federal/SKILL.md` returns ≥ 10

**Implementation note**: Phase 2 is independent of Phase 1 in terms of file dependencies, but Phase 1 should be complete first since `python-security-review-federal` references `python-security-review` as a prerequisite skill.

---

## Phase 3: `python-feature-slice` skill + agents

### Overview

Python analog of `dotnet-vertical-slice`. Scaffolds feature-based architecture using FastAPI
routers, Pydantic v2 models, and a service layer. No FreeMediator equivalent exists in Python —
the pattern uses direct service injection via FastAPI's `Depends()` system instead of a
mediator. CQRS separation is structural (separate read/write service methods), not enforced
by a library.

### Changes required

#### 1. Create skill directory and SKILL.md
**File**: `skills/python-feature-slice/SKILL.md` (new file)
**Changes**: Full 10-section skill. Key adaptations from `dotnet-vertical-slice`:
- Title: "Python Feature Slice Architecture"
- Unique state tag: `<python-feature-slice-state>`
- Core Philosophy: Feature isolation via Python packages (`features/orders/`, `features/users/`). No FreeMediator — use FastAPI `APIRouter` per feature + service classes injected via `Depends()`. CQRS is a naming/structural convention: `OrderReadService` vs `OrderWriteService`, not a library contract.
- Non-Negotiable Constraints: Feature isolation (no cross-feature imports), service layer owns business logic (routers are thin), Pydantic v2 models for request/response, `typing.Protocol` for service interfaces, async-first (`async def` for all I/O)
- Domain Principles: Feature Isolation, Service Autonomy (analog of Handler Autonomy), Minimal Abstractions, Dependency Injection via `Depends()`, Read/Write Service Separation, Pydantic Model Immutability, Explicit Dependencies, Validator Co-Location, Router Thinness, Test Proximity
- Knowledge Base Lookups: `search_knowledge("FastAPI APIRouter feature folder dependency injection")`, `search_knowledge("Pydantic v2 model validator BaseModel")`, `search_knowledge("python clean architecture service layer protocol")`, `search_knowledge("pytest FastAPI TestClient async fixture")`
- Workflow: DETECT (existing structure) → SCAFFOLD (feature folder + router + service + models + tests) → REGISTER (add router to app) → VERIFY
- Scaffold template: `features/<name>/__init__.py`, `features/<name>/router.py`, `features/<name>/service.py`, `features/<name>/models.py`, `features/<name>/dependencies.py`, `tests/features/<name>/test_router.py`, `tests/features/<name>/test_service.py`
- Output Templates: scaffold checklist, feature folder structure diagram, DI registration snippet

#### 2. Create references directory with 2 files
**File**: `skills/python-feature-slice/references/feature-folder-template.md` (new file)
**Changes**: Complete feature folder scaffold template with file-by-file content descriptions. Includes `router.py` pattern (thin router, `Depends()` injection), `service.py` pattern (Protocol interface + concrete implementation), `models.py` pattern (Pydantic v2 request/response models), `dependencies.py` pattern (factory functions for `Depends()`).

**File**: `skills/python-feature-slice/references/cqrs-conventions.md` (new file)
**Changes**: Python CQRS naming and structural conventions without a mediator library. Read service methods (`get_`, `list_`, `find_`), write service methods (`create_`, `update_`, `delete_`, `process_`). When to use separate read/write services vs. a single service with method separation. Async patterns for each.

#### 3. Create Claude Code agent
**File**: `claude/agents/python-feature-slice-agent.md` (new file)
**Changes**: `name: python-feature-slice-agent`, trigger phrases ("scaffold python feature", "create python slice", "fastapi feature folder", "python vertical slice", "add python endpoint"), `tools: Read, Edit, Write, Bash, Glob, Grep`, `skills: [python-feature-slice, fastapi-scaffolder]`. State tag: `<python-feature-slice-agent-state>`.

#### 4. Create OpenCode agent
**File**: `opencode/agents/python-feature-slice-agent.md` (new file)
**Changes**: OpenCode format. `skill()` calls for `python-feature-slice`, `fastapi-scaffolder`.

### Success criteria

#### Automated verification
- [ ] `ls skills/python-feature-slice/references/` contains ≥ 2 files
- [ ] `grep "<python-feature-slice-state>" skills/python-feature-slice/SKILL.md` returns 1 match
- [ ] `grep -c "^## " skills/python-feature-slice/SKILL.md` returns ≥ 10

---

## Phase 4: `alembic-migration-manager` skill + agents

### Overview

Python analog of `ef-migration-manager`. Manages the full Alembic migration lifecycle:
Plan → Generate → Review SQL → Test Rollback → Apply. Same safety philosophy — never apply
without reviewing the generated SQL, every migration must have a verified downgrade path.

### Changes required

#### 1. Create skill directory and SKILL.md
**File**: `skills/alembic-migration-manager/SKILL.md` (new file)
**Changes**: Full 10-section skill. Key adaptations from `ef-migration-manager`:
- Title: "Alembic Migration Manager"
- Unique state tag: `<alembic-migration-state>`
- Core Philosophy: Same 5 non-negotiable constraints adapted — "never apply without reviewing generated SQL", "every upgrade() must have a verified downgrade()", "data preservation is paramount", "one concern per migration", "idempotent-safe scripts"
- Domain Principles: same 10 principles adapted — "Data Integrity First", "Rollback Safety" (upgrade/downgrade), "Idempotent Scripts" (Alembic `--sql` flag + `IF EXISTS` guards), "Zero-Downtime Awareness", "Migration Ordering" (linear revision chain), "SQL Review Mandatory" (`alembic upgrade head --sql`), "Schema Validation" (`alembic check`), "Environment Parity", "Seed Data Management" (Alembic data migrations vs. `HasData()`), "Migration Naming" (`alembic revision -m "add_user_email_index"`)
- Knowledge Base Lookups: `search_knowledge("Alembic migration revision upgrade downgrade SQLAlchemy")`, `search_knowledge("Alembic autogenerate review SQL script")`, `search_knowledge("database migration zero downtime column rename PostgreSQL")`, `search_knowledge("SQLAlchemy model metadata migration conflict")`
- Workflow: PLAN → GENERATE (`alembic revision --autogenerate -m "..."`) → REVIEW SQL (`alembic upgrade head --sql`) → TEST ROLLBACK (`alembic downgrade -1` on dev) → APPLY
- Commands: `alembic revision --autogenerate`, `alembic upgrade head`, `alembic downgrade -1`, `alembic current`, `alembic history`, `alembic check`
- Output Templates: migration review checklist, rollback verification template

#### 2. Create references directory with 2 files
**File**: `skills/alembic-migration-manager/references/migration-safety-checklist.md` (new file)
**Changes**: Pre-apply checklist: SQL reviewed, downgrade tested, data loss risk assessed, backup confirmed, zero-downtime evaluated (table locks, `ALTER TABLE` behavior by database), idempotency verified.

**File**: `skills/alembic-migration-manager/references/dangerous-operations.md` (new file)
**Changes**: Catalog of dangerous DDL operations by database (PostgreSQL, MySQL, SQLite). Column drops, type changes, NOT NULL additions, large table index creation, foreign key additions. For each: risk level, zero-downtime alternative, rollback complexity.

#### 3. Create Claude Code agent
**File**: `claude/agents/alembic-migration-agent.md` (new file)
**Changes**: `name: alembic-migration-agent`, trigger phrases ("alembic migration", "create migration", "apply migration python", "database migration python", "sqlalchemy migration"), `tools: Read, Edit, Write, Bash, Glob, Grep`, `skills: [alembic-migration-manager]`. State tag: `<alembic-migration-agent-state>`.

#### 4. Create OpenCode agent
**File**: `opencode/agents/alembic-migration-agent.md` (new file)
**Changes**: OpenCode format. `skill()` call for `alembic-migration-manager`.

### Success criteria

#### Automated verification
- [ ] `ls skills/alembic-migration-manager/references/` contains ≥ 2 files
- [ ] `grep "<alembic-migration-state>" skills/alembic-migration-manager/SKILL.md` returns 1 match
- [ ] `grep -c "^## " skills/alembic-migration-manager/SKILL.md` returns ≥ 10

---

## Phase 5: `python-modernization-analyzer` skill + agents

### Overview

Python analog of `legacy-migration-analyzer`. Analyzes legacy Python codebases and produces
actionable modernization plans. Primary migration paths: Python 2 → 3.12+, sync → async,
Flask/Django monolith → FastAPI microservices, requirements.txt → pyproject.toml, bare classes
→ Pydantic/dataclasses. Does NOT perform the migration — assesses, quantifies risk, and plans.

### Changes required

#### 1. Create skill directory and SKILL.md
**File**: `skills/python-modernization-analyzer/SKILL.md` (new file)
**Changes**: Full 10-section skill. Key adaptations from `legacy-migration-analyzer`:
- Title: "Python Modernization Analyzer"
- Unique state tag: `<python-modernization-state>`
- Core Philosophy: Same 5 constraints — "assess before acting", "incremental migration over big-bang rewrites", "preserve business logic unchanged", "dependencies are the real blockers", "every recommendation must cite evidence"
- Domain Principles: Risk Assessment First, Incremental Migration, API Compatibility Analysis (use `pyupgrade --py312-plus`, `2to3`, `pylint --py3k`), Dependency Audit (`pip-audit`, `pip list --outdated`), Business Logic Isolation, Test Coverage Gate (characterization tests before migrating), Configuration Migration (`requirements.txt` → `pyproject.toml`, env var patterns), Authentication and Identity (Flask-Login → FastAPI JWT, Django auth → custom), Database Access Layer (raw SQL → SQLAlchemy ORM, sync SQLAlchemy → async), Deployment Pipeline (bare scripts → Docker + CI/CD)
- Knowledge Base Lookups: `search_knowledge("python 2 to 3 migration 2to3 pyupgrade")`, `search_knowledge("Flask to FastAPI migration async")`, `search_knowledge("SQLAlchemy sync to async migration")`, `search_knowledge("pyproject.toml packaging pip dependency management")`
- Workflow: SCAN (codebase inventory) → ASSESS (risk scoring) → PLAN (phased migration plan) → REPORT
- Tooling: `2to3 -l`, `pyupgrade --py312-plus`, `pylint --py3k`, `pip-audit`, `vulture` (dead code), `radon` (complexity baseline)
- Output Templates: risk matrix, migration phase plan template, dependency compatibility table

#### 2. Create references directory with 2 files
**File**: `skills/python-modernization-analyzer/references/migration-risk-matrix.md` (new file)
**Changes**: Risk scoring matrix for common Python modernization scenarios. Rows: Python 2→3 syntax, async migration, framework swap, dependency upgrade, type annotation addition, packaging modernization. Columns: Effort (S/M/L/XL), Risk (Low/Med/High/Critical), Blocker potential, Recommended order.

**File**: `skills/python-modernization-analyzer/references/compatibility-patterns.md` (new file)
**Changes**: Common Python 2→3 and sync→async compatibility patterns with before/after examples. `print` statement, `unicode`/`str`, `dict.iteritems()`, `async def` conversion, `asyncio.run()`, `httpx` vs `requests` for async HTTP.

#### 3. Create Claude Code agent
**File**: `claude/agents/python-modernization-agent.md` (new file)
**Changes**: `name: python-modernization-agent`, trigger phrases ("modernize python", "python 2 to 3", "upgrade python", "migrate flask to fastapi", "python legacy migration", "async migration python"), `tools: Read, Bash, Glob, Grep`, `skills: [python-modernization-analyzer, python-arch-review]`. State tag: `<python-modernization-agent-state>`.

#### 4. Create OpenCode agent
**File**: `opencode/agents/python-modernization-agent.md` (new file)
**Changes**: OpenCode format. `skill()` calls for `python-modernization-analyzer`, `python-arch-review`.

### Success criteria

#### Automated verification
- [ ] `ls skills/python-modernization-analyzer/references/` contains ≥ 2 files
- [ ] `grep "<python-modernization-state>" skills/python-modernization-analyzer/SKILL.md` returns 1 match
- [ ] `grep -c "^## " skills/python-modernization-analyzer/SKILL.md` returns ≥ 10

---

## Phase 6: `fastapi-scaffolder` skill + agents

### Overview

Python analog of `minimal-api-scaffolder`. Scaffolds FastAPI endpoints with OpenAPI
documentation (built-in), Pydantic v2 request/response models, JWT authentication,
rate limiting, and health checks. FastAPI has OpenAPI built-in — no separate configuration
needed, but metadata decoration is still required for quality documentation.

### Changes required

#### 1. Create skill directory and SKILL.md
**File**: `skills/fastapi-scaffolder/SKILL.md` (new file)
**Changes**: Full 10-section skill. Key adaptations from `minimal-api-scaffolder`:
- Title: "FastAPI Scaffolder"
- Unique state tag: `<fastapi-scaffold-state>`
- Non-Negotiable Constraints: OpenAPI-First (every endpoint has `summary`, `description`, `response_model`, `responses` dict), Versioning from Day One (`/api/v1/` prefix via `APIRouter(prefix="/api/v1")`), Security by Default (`Depends(get_current_user)` on all routers; anonymous is explicit opt-out), Pydantic v2 Models (all request/response types are `BaseModel` subclasses; no `dict` returns), Typed Responses (explicit `response_model=`, no bare `dict` or `Any` returns)
- Domain Principles: Router Grouping (one `APIRouter` per feature), Request/Response Models (Pydantic v2 `BaseModel`, `model_config = ConfigDict(frozen=True)` for immutability), Validation Integration (Pydantic validators in models; `HTTPException` for validation errors), OpenAPI Documentation (`summary`, `description`, `response_model`, `responses`, `tags`), Versioning Strategy (URL prefix default), Authorization Patterns (`Depends()` chain), Rate Limiting (`slowapi` or `fastapi-limiter`), Error Handling (custom exception handlers returning RFC 7807 Problem Details), CORS Configuration (explicit origins from config), Health Checks (`/health`, `/health/ready`, `/health/live`)
- Knowledge Base Lookups: `search_knowledge("FastAPI APIRouter endpoint Pydantic v2 response_model")`, `search_knowledge("FastAPI JWT authentication Depends security")`, `search_knowledge("FastAPI OpenAPI documentation summary description tags")`, `search_knowledge("FastAPI rate limiting slowapi middleware")`, `search_knowledge("FastAPI health check endpoint lifespan")`
- Workflow: DETECT → CONFIGURE (project structure, versioning, auth) → SCAFFOLD (router + models + dependencies) → SECURE (auth + rate limiting) → DOCUMENT (OpenAPI metadata) → VERIFY
- Output Templates: scaffold checklist, router template, model template, dependency template

#### 2. Create references directory with 2 files
**File**: `skills/fastapi-scaffolder/references/router-template.md` (new file)
**Changes**: Complete FastAPI router scaffold template. Includes: `APIRouter` setup with prefix/tags, Pydantic v2 request/response models, `Depends()` injection pattern, typed response with `response_model`, error handling with `HTTPException`, OpenAPI metadata decoration, async handler pattern.

**File**: `skills/fastapi-scaffolder/references/security-patterns.md` (new file)
**Changes**: FastAPI security patterns: JWT bearer token validation with `python-jose`/`PyJWT`, OAuth2 password flow, API key header auth, `Depends()` chain for role-based access, CORS configuration for production vs. development.

#### 3. Create Claude Code agent
**File**: `claude/agents/fastapi-scaffold-agent.md` (new file)
**Changes**: `name: fastapi-scaffold-agent`, trigger phrases ("scaffold fastapi", "create fastapi endpoint", "fastapi router", "add fastapi route", "fastapi api", "python rest api"), `tools: Read, Edit, Write, Bash, Glob, Grep`, `skills: [fastapi-scaffolder, python-feature-slice, python-security-review]`. State tag: `<fastapi-scaffold-agent-state>`.

#### 4. Create OpenCode agent
**File**: `opencode/agents/fastapi-scaffold-agent.md` (new file)
**Changes**: OpenCode format. `skill()` calls for `fastapi-scaffolder`, `python-feature-slice`, `python-security-review`.

### Success criteria

#### Automated verification
- [ ] `ls skills/fastapi-scaffolder/references/` contains ≥ 2 files
- [ ] `grep "<fastapi-scaffold-state>" skills/fastapi-scaffolder/SKILL.md` returns 1 match
- [ ] `grep -c "^## " skills/fastapi-scaffolder/SKILL.md` returns ≥ 10

---

## Phase 7: `pypi-package-scaffold` skill + agents

### Overview

Python analog of `nuget-package-scaffold`. Scaffolds production-ready PyPI packages with
`pyproject.toml`, `hatch`/`flit`/`build` tooling, GitHub Actions publish workflow, test
harness, and documentation. Same quality bar: no publish without tests, SemVer, metadata
required, deterministic builds.

### Changes required

#### 1. Create skill directory and SKILL.md
**File**: `skills/pypi-package-scaffold/SKILL.md` (new file)
**Changes**: Full 10-section skill. Key adaptations from `nuget-package-scaffold`:
- Title: "PyPI Package Scaffold"
- Unique state tag: `<pypi-package-state>`
- Non-Negotiable Constraints: No publish without tests, SemVer is law, metadata required (`name`, `version`, `description`, `license`, `authors`, `readme`, `requires-python`, `classifiers`), multi-Python-version support (`python_requires = ">=3.10"`), deterministic builds (pinned build dependencies)
- Domain Principles: Semantic Versioning, API Surface Minimization (`__all__` in `__init__.py`), Python Version Support (`python_requires`, test matrix in CI), Documentation (docstrings + README + `mkdocs`/`sphinx`), Deterministic Builds (pinned `build` deps, `PYTHONHASHSEED=0`), Type Stubs (ship `py.typed` marker, inline types or `.pyi` stubs), License Compliance (SPDX in `pyproject.toml`), Dependency Management (version ranges with upper bounds for libraries, pinned for apps), Backward Compatibility (deprecation warnings before removal), Source Distribution + Wheel (always ship both `sdist` and `wheel`)
- Knowledge Base Lookups: `search_knowledge("pyproject.toml package metadata hatch flit build")`, `search_knowledge("semantic versioning python package PyPI")`, `search_knowledge("GitHub Actions python publish PyPI workflow")`, `search_knowledge("python type stubs py.typed inline types")`
- Workflow: SCAFFOLD (pyproject.toml + src layout) → CONFIGURE (metadata, classifiers, extras) → TEST (pytest matrix) → BUILD (`python -m build`) → PUBLISH (twine/trusted publishing)
- Output Templates: `pyproject.toml` template, GitHub Actions publish workflow template, release checklist

#### 2. Create references directory with 2 files
**File**: `skills/pypi-package-scaffold/references/pyproject-template.md` (new file)
**Changes**: Complete `pyproject.toml` template with all required and recommended fields. Sections: `[build-system]`, `[project]` (name, version, description, readme, license, authors, requires-python, classifiers, dependencies, optional-dependencies), `[project.urls]`, `[tool.hatch]` or `[tool.flit]`, `[tool.pytest.ini_options]`, `[tool.mypy]`, `[tool.ruff]`.

**File**: `skills/pypi-package-scaffold/references/ci-publish-workflow.md` (new file)
**Changes**: GitHub Actions workflow for PyPI publishing using Trusted Publishing (OIDC, no API tokens). Includes: test matrix (Python 3.10, 3.11, 3.12, 3.13), build step, TestPyPI publish on PR, PyPI publish on tag, attestation generation.

#### 3. Create Claude Code agent
**File**: `claude/agents/pypi-package-agent.md` (new file)
**Changes**: `name: pypi-package-agent`, trigger phrases ("create python package", "scaffold pypi", "publish python package", "pyproject.toml setup", "python library scaffold"), `tools: Read, Edit, Write, Bash, Glob, Grep`, `skills: [pypi-package-scaffold, supply-chain-audit]`. State tag: `<pypi-package-agent-state>`.

#### 4. Create OpenCode agent
**File**: `opencode/agents/pypi-package-agent.md` (new file)
**Changes**: OpenCode format. `skill()` calls for `pypi-package-scaffold`, `supply-chain-audit`.

### Success criteria

#### Automated verification
- [ ] `ls skills/pypi-package-scaffold/references/` contains ≥ 2 files
- [ ] `grep "<pypi-package-state>" skills/pypi-package-scaffold/SKILL.md` returns 1 match
- [ ] `grep -c "^## " skills/pypi-package-scaffold/SKILL.md` returns ≥ 10

---

## Phase 8: `AGENTS.md` and suite table updates

### Overview

Update the repository's `AGENTS.md` to reflect the new skill count (53 → 61), agent counts
(Claude 20 → 28, OpenCode 19 → 27), and add the Python suite row to the Skill Suites table.
Also update the Open Loops section.

### Changes required

#### 1. Update skill count
**File**: `AGENTS.md`
**Changes**: In the Project Overview section, update `53+` to `61+`. In the Open Loops section, update the skill count note.

#### 2. Update agent count parity note
**File**: `AGENTS.md`
**Changes**: In the Open Loops section, update Claude agent count from 20 → 28 and OpenCode from 19 → 27.

#### 3. Add Python suite to Skill Suites table
**File**: `AGENTS.md`
**Changes**: Add new row to the Skill Suites table:
```
| Python | python-security-review, python-security-review-federal, python-feature-slice, alembic-migration-manager, python-modernization-analyzer, fastapi-scaffolder, pypi-package-scaffold, python-arch-review | Python patterns, migrations, security, scaffolding |
```

#### 4. Update architecture-review Stack-Specific Guidance
**File**: `skills/architecture-review/SKILL.md`
**Changes**: In the "Stack-Specific Guidance" section at line 607, the Python cross-reference already exists. No change needed — `python-arch-review` is already referenced there. Verify the line reads correctly and add a note about `python-feature-slice` and `fastapi-scaffolder` for structural patterns (mirrors the .NET cross-references to `dotnet-vertical-slice`).

### Success criteria

#### Automated verification
- [ ] `grep "61" AGENTS.md` finds the updated skill count
- [ ] `grep "Python" AGENTS.md` finds the new suite row in the Skill Suites table
- [ ] `grep -c "python-security-review" AGENTS.md` returns ≥ 1

#### Manual verification
- [ ] Skill Suites table has a Python row with all 8 skills listed
- [ ] Open Loops section reflects updated counts

**Implementation note**: Phase 8 must run AFTER all skill phases (1–7) are complete. It is a summary/bookkeeping phase.

---

## Testing strategy

Each phase is self-contained and verified immediately after completion. No integration tests
are needed — skills are Markdown files, not compiled code. Verification is structural:
- File existence checks (`ls`)
- Section count checks (`grep -c "^## "`)
- State tag uniqueness checks (`grep` across all skills)
- Reference file count checks (`ls references/`)
- Agent format checks (frontmatter field presence)

After all phases complete, run a final cross-skill uniqueness check:
```bash
grep -r "<.*-state>" skills/*/SKILL.md | grep -oP "<[^>]+-state>" | sort | uniq -d
```
This must return empty (no duplicate state tags).

---

## Rollback plan

Each phase creates new files only — no existing files are modified until Phase 8.

- **Phases 1–7 rollback**: `rm -rf skills/<skill-name>/` + `rm claude/agents/<agent>.md` + `rm opencode/agents/<agent>.md`
- **Phase 8 rollback**: `git checkout AGENTS.md skills/architecture-review/SKILL.md`
- **Full rollback**: `git checkout HEAD -- AGENTS.md skills/architecture-review/SKILL.md && git clean -fd skills/python-* skills/alembic-* skills/fastapi-* skills/pypi-* claude/agents/python-* claude/agents/alembic-* claude/agents/fastapi-* claude/agents/pypi-* opencode/agents/python-* opencode/agents/alembic-* opencode/agents/fastapi-* opencode/agents/pypi-*`

---

## Notes

- Plan B (Rust suite) follows this plan. Do not begin Plan B until Plan A is fully verified.
- The `python-security-review-federal` skill (Phase 2) requires `python-security-review` (Phase 1) to exist as a referenced prerequisite — implement Phase 1 first.
- `python-feature-slice` and `fastapi-scaffolder` cross-reference each other in their agent `skills:` arrays — both must exist before the agents are fully functional, but each skill file is independently valid.
- State tag uniqueness is the most common error in new skill creation. The final cross-skill grep in the Testing Strategy section must pass before declaring Plan A complete.
- New state tags introduced in this plan: `<python-security-state>`, `<python-federal-security-state>`, `<python-feature-slice-state>`, `<alembic-migration-state>`, `<python-modernization-state>`, `<fastapi-scaffold-state>`, `<pypi-package-state>`
- New agent state tags: `<python-security-agent-state>`, `<python-federal-security-agent-state>`, `<python-feature-slice-agent-state>`, `<alembic-migration-agent-state>`, `<python-modernization-agent-state>`, `<fastapi-scaffold-agent-state>`, `<pypi-package-agent-state>`
