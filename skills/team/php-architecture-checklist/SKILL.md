---
name: php-architecture-checklist
audience: team
description: >
  Checklist executor for PHP / Laravel architecture reviews. Detects the PHP version, framework
  (Laravel/Symfony/plain), and autoloading layout, then runs a systematic checklist covering
  service-layer boundaries, strict typing, input validation, query safety, and config/secrets hygiene —
  producing a graded report with file:line evidence. Use to review or grade an existing PHP codebase.
  Triggers on "review this php project", "php architecture checklist", "audit php code", "laravel
  architecture review", "evaluate php codebase", "php code review", "grade this php architecture".
  Do NOT use for a Socratic design critique — use architecture-review. Do NOT use for a security audit —
  use php-security-review. Do NOT use to write new code test-first — use tdd.
---

# PHP Architecture Checklist

> "A checklist cannot fly a plane, but a pilot cannot fly safely without one."
> — Atul Gawande

## Core Architectural Values

Shared across the `dotnet` / `python` / `php` / `rust` architecture checklists — same values, language-specific checks.

| # | Value | What it means |
|---|-------|---------------|
| 1 | **Detect before judge** | Determine version/framework/structure before applying any item; context decides what is idiomatic. |
| 2 | **Evidence over opinion** | Every finding cites `file:line` and the offending pattern. "Overuses facades" is not a finding; "`OrderController.php:42` calls `DB::raw` with request input" is. |
| 3 | **Feature cohesion** | Organized by business capability, not technical layer. Cross-feature coupling is a violation. |
| 4 | **Dependencies point inward** | Domain/service logic does not depend on framework facades or HTTP. Boundaries are explicit. |
| 5 | **Explicit error handling** | Failures handled at the right layer; no silent swallowing; errors carry diagnostic context. |
| 6 | **Config & secrets hygiene** | No hardcoded secrets; configuration injected, not reached for globally; secrets from env / secret-manager. |
| 7 | **Version awareness** | Recommendations are gated to the detected version; never suggest an API that does not exist there. |
| 8 | **Tests gate change** | Untested code is a finding; high-risk modules without tests are prioritized. |
| 9 | **Graded, actionable output** | A letter grade (A–F) from counted findings, plus prioritized, version-correct recommendations. |

## Workflow

Shared skeleton: `DETECT → SCAN → REPORT → RECOMMEND`.

```
DETECT     PHP version (composer.json `require.php`), framework (Laravel/Symfony/plain + version),
           autoloading (PSR-4 in composer.json), and whether a test suite exists (PHPUnit/Pest).
           Record findings; if a version cannot be determined, ask — never assume 8.3.

SCAN       Run the PHP Checklist below section by section. Gather evidence with tooling:
             phpstan analyse              # static analysis (target level >= 6)
             php-cs-fixer fix --dry-run   # PSR-12 style drift
             composer outdated            # dependency currency
           Every violation becomes a finding with file:line and a severity (critical/high/medium/low).

REPORT     Emit the graded report (Output Template). Grade = function of counted findings.

RECOMMEND  Prioritize: critical → quick wins → modernization. Version-gate every recommendation;
           never suggest an API absent from the detected PHP / Laravel version.
```

## PHP Checklist (language-specific)

| # | Check | Severity |
|---|-------|----------|
| 1 | **Service-layer boundaries** — business logic in service classes, not controllers; constructor DI over static facades (`Auth::`, `DB::`) in domain code | Critical |
| 2 | **Strict typing** — `declare(strict_types=1)` in every file; all params and returns type-hinted; `phpstan` clean at the project level | High |
| 3 | **Input validation** — Form Requests (or equivalent) validate at the boundary; never trust raw `$request->input()` | Critical |
| 4 | **Query safety** — Eloquent / Query Builder with bound parameters; no string-concatenated SQL; no `DB::raw` on user input | Critical |
| 5 | **YAGNI / Rule of Three** — abstractions earned; no speculative repository/interface layers for a single implementation | High |
| 6 | **Config & secrets** — secrets in `.env`, read via `config()` (never `env()` outside config files); no hardcoded credentials | Critical |
| 7 | **PSR-12 + PSR-4** — `php-cs-fixer`/`phpcs` clean; correct PSR-4 autoloading; no class-per-file violations | Medium |
| 8 | **Thin controllers** — controllers orchestrate (validate → call service → return); no business rules or persistence inline | High |
| 9 | **Test coverage** — behavioral tests (PHPUnit/Pest) for business logic; high-risk untested code flagged | High |

PHP/Laravel conventions: [php conventions](references/php-conventions.md). Full section-by-section list: [review checklist](references/review-checklist.md).

## State Block

```
<arch-checklist-state>
language: php
mode: DETECT | SCAN | REPORT | RECOMMEND | COMPLETE
detected: [php 8.x | framework+version | psr-4 | tests:yes/no]
issues_found: [critical:N high:N medium:N low:N]
last_action: [what was just done]
next_action: [what should happen next]
</arch-checklist-state>
```

## Output Template

Shared across all four architecture checklists.

```markdown
## Architecture Checklist: [project] (PHP)
**Version**: [8.x] | **Framework**: [Laravel x/Symfony/plain] | **Tests**: [yes/no]

| Section | Pass | Fail | Warn |
|---------|------|------|------|
| Boundaries / Typing / Validation / Queries / Config / PSR / Tests | … | … | … |

### Grade: [A–F]
Grading: **A** 0 crit/0 high/≤3 med · **B** 0 crit/≤2 high · **C** 0 crit, gaps in one area ·
**D** 1+ crit · **F** fundamental problems (raw SQL on input, secrets in code, no service layer).

| Severity | Location | Finding | Recommendation |
|----------|----------|---------|----------------|
| CRITICAL | file:line | [pattern] | [version-gated fix] |

**Quick wins**: [low-effort, high-impact] · **Modernization**: [larger items with effort estimate]
```

## AI Discipline Rules

- **Detect the PHP/Laravel version first.** Recommending enums or readonly properties to a PHP 7.4 project produces invalid findings.
- **Evidence or it is not a finding.** Run the tools; cite `file:line`. Never grade on vibes.
- **Architecture, not security.** Injection, mass-assignment, and secrets-exposure findings belong to `php-security-review` — note them and route there.
- **Do not rewrite during a review.** Produce findings + recommendations; the team decides and `tdd` drives the fix.

## Integration with Other Skills

- **`architecture-review`** — When the grade is D/F, escalate to the Socratic critic: this checklist finds _what_ is wrong; `architecture-review` builds _why_.
- **`php-security-review`** — Companion for the security dimension (OWASP, mass-assignment, query injection).
- **`tdd`** — Methodology for adding tests the checklist flags as missing, and for driving any refactor.
- **`dotnet` / `python` / `rust`-architecture-checklist** — Sibling skills sharing this exact Core Values + workflow + output.
