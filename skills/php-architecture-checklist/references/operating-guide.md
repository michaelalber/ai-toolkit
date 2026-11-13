# php-architecture-checklist — operating guide

Depth relocated from SKILL.md; load it when the Workflow points here.

## PHP Checklist (language-specific)

| # | Check | Severity |
|---|-------|----------|
| 1 | **Service-layer boundaries** — business logic in service classes, not controllers; constructor DI over static facades (`Auth::`, `DB::`) in domain code | Critical |
| 2 | **Strict typing** — `declare(strict_types=1)` in every file; all params and returns type-hinted; `phpstan` clean at the project level | High |
| 3 | **Input validation** — Form Requests (or equivalent) validate at the boundary; never trust raw `$request->input()` | Critical |
| 4 | **Query safety** — Eloquent / Query Builder with bound parameters; no string-concatenated SQL; no `DB::raw` on user input | Critical |
| 5 | **YAGNI / Rule of Three** — abstractions earned; no speculative repository/interface layers for a single implementation | High |
| 6 | **Config & secrets** — secrets in `.env`, read via `config()` (never `env()` outside config files); no hardcoded credentials | Critical |
| 7 | **PSR-12 + PSR-4** — `php-cs-fixer`/`phpcs` clean (`pint` on Laravel); correct PSR-4 autoloading; no class-per-file violations | Medium |
| 8 | **Thin controllers** — controllers orchestrate (validate → call service → return); no business rules or persistence inline | High |
| 9 | **Test coverage** — behavioral tests (PHPUnit/Pest) for business logic; high-risk untested code flagged | High |

PHP/Laravel conventions: [php conventions](references/php-conventions.md). Full section-by-section list + grounding query map: [review checklist](references/review-checklist.md).

## AI Discipline Rules

- **Detect the PHP/Laravel version first.** Recommending enums or readonly properties to a PHP 7.4 project produces invalid findings.
- **Evidence or it is not a finding.** Run the tools; cite `file:line`. Never grade on vibes.
- **Architecture, not security.** Injection, mass-assignment, and secrets-exposure findings belong to `php-security-review` — note them and route there.
- **Do not rewrite during a review.** Produce findings + recommendations; the team decides and `tdd-loop` drives the fix.
