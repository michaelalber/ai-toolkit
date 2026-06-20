---
name: php-package-scaffold
audience: team
description: >
  Scaffolds production-ready Composer packages for Packagist with a complete composer.json,
  PSR-4 autoloading, a Pest/PHPUnit test harness, GitHub Actions CI (PHP version matrix,
  PHPStan, PHP-CS-Fixer), and a semver tag-based publish workflow. PHP analog of
  nuget-package-scaffold, pypi-package-scaffold, and cargo-package-scaffold. Use when creating a
  reusable PHP library, configuring composer.json metadata, setting up Composer/Packagist
  publishing, or building a PHP package CI pipeline.
---

# PHP Package Scaffold (Composer / Packagist)

> "A library is a contract. Once published, every breaking change is someone else's incident."

> "Make it work, make it right, make it releasable."

## Core Philosophy

This skill produces a **publishable Composer library** — not an application. The deliverable is a package
that a stranger can `composer require vendor/package`, that installs cleanly across a matrix of supported
PHP versions, that passes static analysis and style checks in CI, and that publishes to Packagist
automatically on a semver git tag. Packagist serves whatever a tag points at, so the **tag is the
release** — discipline lives in the tag and in CI, not in a manual upload step.

A library is a long-lived contract. Semantic versioning is mandatory: `MAJOR.MINOR.PATCH`, where a MAJOR
bump is the only place a breaking change is allowed. The public API surface is everything not marked
`@internal`; treat it as frozen within a major version.

**Non-Negotiable Constraints:**
1. **Valid `composer.json`** — `composer validate --strict` passes
2. **PSR-4 autoloading** — `src/` mapped to a vendor namespace; tests in a separate `autoload-dev`
3. **`declare(strict_types=1)`** in every `src/` file
4. **Semver discipline** — tags are `vX.Y.Z`; breaking changes only on MAJOR
5. **CI gate before publish** — tests + PHPStan + style must pass on the tag
6. **Declared, bounded dependency constraints** — caret ranges, no `dev-master`, no unbounded `*`

## Domain Principles

| # | Principle | Description | Applied As |
|---|-----------|-------------|------------|
| 1 | **The tag is the release** | Packagist publishes the commit a `vX.Y.Z` tag points at. No tag, no release. | `git tag v1.2.0 && git push --tags` after CI is green on `main` |
| 2 | **Semver is a promise** | MAJOR = break, MINOR = additive, PATCH = fix. Consumers pin with `^1.0`. | Breaking change → bump MAJOR and document migration in CHANGELOG |
| 3 | **Validate before publish** | `composer validate --strict` and a CI matrix gate every release. | CI job runs on tag push; Packagist webhook fires only after merge |
| 4 | **Bounded constraints** | Dependencies use caret ranges; never `*` or a branch alias in a published lib. | `"guzzlehttp/guzzle": "^7.5"` |
| 5 | **Declared PHP support** | `require.php` states the supported range; CI tests every version in it. | `"php": "^8.1"` + matrix `[8.1, 8.2, 8.3]` |
| 6 | **Public API is curated** | Internal classes are marked `@internal` and excluded from BC guarantees. | `/** @internal */` on helpers; document the supported surface |
| 7 | **Static analysis is a gate** | PHPStan (or Psalm) at a fixed level runs in CI; new code may not lower it. | `phpstan analyse src --level=8` |
| 8 | **Style is enforced, not debated** | PHP-CS-Fixer / PHP_CodeSniffer with a committed ruleset (PSR-12). | `php-cs-fixer fix --dry-run --diff` in CI |
| 9 | **CHANGELOG is the source of truth** | Keep-a-Changelog format; every release documents Added/Changed/Fixed/Removed. | Update `CHANGELOG.md` before tagging |
| 10 | **Reproducible installs** | A library commits `composer.json` but **not** `composer.lock`; apps commit the lock. | `.gitignore` excludes `composer.lock` for libraries |

## Knowledge Base Lookups

Use `search_knowledge` (grounded-code-mcp, `collection="php"`).

| Query | When to Call |
|-------|--------------|
| `search_knowledge("composer.json schema autoload require require-dev", collection="php")` | When writing `composer.json` |
| `search_knowledge("Composer PSR-4 autoloading namespace mapping", collection="php")` | When laying out `src/` |
| `search_knowledge("Composer library versioning semantic version constraints", collection="php")` | When choosing version constraints |
| `search_knowledge("Composer publishing packagist", collection="php")` | When configuring the publish flow |
| `search_code_examples("phpunit test class assertion", language="php")` | When scaffolding the test harness |

## Workflow

### Phase 1: PLAN

Decide the package identity and surface before writing files.

```bash
php -v | head -1
# Pick: vendor/name (lowercase, hyphenated), namespace (StudlyCase), license, PHP range
# Confirm the name is free on packagist.org
```

Record: `vendor/package`, root namespace, license (SPDX id), supported PHP range, runtime deps.

### Phase 2: SCAFFOLD

See `references/composer-json-template.md` for the full manifest and `references/ci-publish-workflow.md`
for the GitHub Actions and Packagist setup.

```
composer.json
src/                       # PSR-4 root; @internal on non-public classes
tests/                     # Pest or PHPUnit; autoload-dev
.github/workflows/ci.yml   # matrix: tests + phpstan + cs-fixer
phpstan.neon.dist          # level 8
.php-cs-fixer.dist.php      # PSR-12 ruleset
CHANGELOG.md               # Keep a Changelog
README.md  LICENSE  .gitignore  .gitattributes
```

### Phase 3: VERIFY LOCALLY

```bash
composer validate --strict
composer install
vendor/bin/phpstan analyse src --level=8
vendor/bin/php-cs-fixer fix --dry-run --diff
vendor/bin/pest            # or vendor/bin/phpunit
```

### Phase 4: PUBLISH

```bash
# After CI is green on main:
# 1. Update CHANGELOG.md with the new version
# 2. Tag with semver and push
git tag v1.0.0
git push origin v1.0.0
# Packagist auto-updates via the GitHub webhook (or `composer` API hook).
```

First-time only: submit the repo URL once at packagist.org and enable the GitHub service hook so future
tags publish automatically.

## State Block

```xml
<php-package-scaffold-state>
  phase: PLAN | SCAFFOLD | VERIFY | PUBLISH | COMPLETE
  package: vendor/name
  namespace: [root namespace]
  php_range: [e.g. ^8.1]
  license: [SPDX id]
  test_runner: pest | phpunit
  phpstan_level: [n]
  ci_created: true | false
  validate_passes: true | false
  packagist_registered: true | false
  last_action: [description]
</php-package-scaffold-state>
```

## Output Templates

### PHP Package Scaffold: vendor/name

```markdown
## PHP Package Scaffold: vendor/name

### Identity
- Package: `vendor/name`
- Namespace: `Vendor\Name\`
- PHP: `^8.1` (matrix: 8.1, 8.2, 8.3)
- License: MIT

### Files Created
- [ ] `composer.json` (validates --strict)
- [ ] `src/` PSR-4 root
- [ ] `tests/` harness (Pest/PHPUnit)
- [ ] `.github/workflows/ci.yml`
- [ ] `phpstan.neon.dist` (level 8)
- [ ] `.php-cs-fixer.dist.php` (PSR-12)
- [ ] `CHANGELOG.md`, `README.md`, `LICENSE`, `.gitignore`, `.gitattributes`

### Gates
- [ ] `composer validate --strict` passes
- [ ] PHPStan level 8 clean
- [ ] CS-Fixer dry-run clean
- [ ] Tests green across the matrix

### Publish
- [ ] CHANGELOG updated
- [ ] `vX.Y.Z` tag pushed
- [ ] Packagist webhook configured
```

## AI Discipline Rules

### CRITICAL: A Library Does Not Commit `composer.lock`

Applications pin transitive versions with a lock; a library must resolve against the consumer's
constraints. `.gitignore` excludes `composer.lock` for libraries. Committing it can cause subtle
resolution conflicts downstream.

### REQUIRED: Bounded, Caret Constraints

```json
"require": { "php": "^8.1", "psr/log": "^3.0" }
```
Never `"*"`, never `"dev-main"`, never an unbounded `">=2.0"` in a published library.

### CRITICAL: Tag Only Green Commits

The tag is the release. Never tag a commit whose CI is red or untested — Packagist will serve it
immediately and consumers will install the breakage.

## Anti-Patterns Table

| # | Anti-Pattern | Why It Fails | Correct Approach |
|---|-------------|-------------|-----------------|
| 1 | **Committing `composer.lock` in a library** | Forces transitive versions on consumers; resolution conflicts | `.gitignore` the lock for libraries |
| 2 | **`"*"` / `dev-master` constraints** | Unreproducible, surprise breakage | Caret ranges on every dependency |
| 3 | **Breaking change on a MINOR/PATCH** | Violates the semver contract; silent downstream outage | Breaking → MAJOR bump + CHANGELOG migration note |
| 4 | **No PHP version matrix in CI** | "Works on my 8.3" ships, breaks on 8.1 | Matrix every version in `require.php` |
| 5 | **No `composer validate` in CI** | Invalid manifest reaches Packagist | `composer validate --strict` as a CI step |
| 6 | **Publishing dev/test files** | Bloated package, leaked fixtures | `.gitattributes export-ignore` for `tests/`, CI, configs |
| 7 | **No `@internal` markers** | Consumers couple to private classes; you can't refactor | Mark non-public classes `@internal` |
| 8 | **Hand-maintained version in code** | Drifts from the tag | Derive version from the tag / `composer` runtime API |
| 9 | **Lowering PHPStan to make CI pass** | Erodes the quality gate over time | Fix the code or baseline a specific finding, never lower the level |
| 10 | **Tagging without a CHANGELOG entry** | Consumers can't tell what changed | Update CHANGELOG before every tag |

## Error Recovery

### `composer validate` fails

```
Run `composer validate --strict` locally; it names the offending field.
Common causes: missing `license`, malformed `autoload.psr-4`, name not lowercase/hyphenated.
Fix the field and re-validate before committing.
```

### Packagist not updating after a tag

```
Symptom: a new tag does not appear on packagist.org.
Fix: confirm the GitHub webhook (Settings → Webhooks) points at packagist; click "Update" on the
Packagist package page to force a manual refresh; verify the tag is a valid `vX.Y.Z`.
```

### CI green locally but red on an older PHP

```
Symptom: matrix fails only on PHP 8.1.
Cause: used a feature from a newer PHP (readonly classes, `json_validate`, etc.) below the floor.
Fix: either raise `require.php` (a MAJOR bump if it drops support) or guard/replace the newer feature.
```

## Integration with Other Skills

| Skill | Relationship |
|-------|-------------|
| `php-architecture-checklist` | Run before the first tag to verify the package's internal structure and boundaries. |
| `php-security-review` | Audit the package (and its dependencies) for OWASP and supply-chain risks before publishing. |
| `supply-chain-audit` | Review the dependency tree for known-vulnerable or unmaintained packages. |
| `php-feature-slice` | When the package provides Laravel integration, ship a service provider following slice conventions. |
| `tdd` | Drive the public API test-first so the released contract is the tested contract. |
