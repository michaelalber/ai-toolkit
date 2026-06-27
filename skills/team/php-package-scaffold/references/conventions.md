# PHP Package Scaffold — Conventions, Discipline & Recovery

Depth relocated from `SKILL.md`: the full principle set, AI discipline rules, the
anti-pattern catalog, the output report template, and error-recovery procedures.

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

## Output Report Template

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
