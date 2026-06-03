# PHP Architecture Review Checklist

Section-by-section checklist for the PHP architecture review. Run alongside `phpstan`,
`php-cs-fixer`, and `composer outdated`.

---

## Pre-review setup

```bash
php -v                                  # confirm PHP version
grep -A2 '"require"' composer.json      # framework + php constraint
phpstan analyse --level=6 2>&1 | tail   # static analysis baseline
php-cs-fixer fix --dry-run --diff       # style drift
vendor/bin/phpunit --list-tests | wc -l # test presence
```

---

## Section 1: Boundaries & service layer
- [ ] Business logic lives in service classes, not controllers or models
- [ ] Domain/service code uses constructor DI, not static facades (`Auth::`, `DB::`, `Cache::`)
- [ ] No cross-feature imports; feature modules are cohesive
- [ ] Controllers are thin: validate → delegate → respond

## Section 2: Typing
- [ ] `declare(strict_types=1);` in every PHP file
- [ ] All function parameters and return types are hinted
- [ ] `phpstan` passes at the agreed level (>= 6) with no baseline suppressions for new code

## Section 3: Input validation
- [ ] Form Requests (or explicit validators) at every write boundary
- [ ] No direct use of unvalidated `$request->input()` / `$_POST` / `$_GET`

## Section 4: Query safety
- [ ] Eloquent / Query Builder with bound parameters everywhere
- [ ] No string-concatenated SQL; no `DB::raw` on user-controlled input
- [ ] No N+1 query patterns in hot paths (eager-load relations)

## Section 5: Config & secrets
- [ ] Secrets in `.env`; accessed via `config()`, never `env()` in application code
- [ ] No hardcoded credentials, API keys, or connection strings

## Section 6: Style & autoloading
- [ ] PSR-12 clean (`php-cs-fixer`)
- [ ] PSR-4 autoloading; one class per file; namespace matches path

## Section 7: Dependencies
- [ ] `composer.lock` committed; versions constrained
- [ ] No abandoned packages; `composer outdated` reviewed

## Section 8: Tests
- [ ] Behavioral tests (PHPUnit/Pest) cover business logic
- [ ] High-risk untested services flagged as priority candidates

---

## Grading

- **A**: 0 critical, 0 high, ≤ 3 medium
- **B**: 0 critical, ≤ 2 high
- **C**: 0 critical, significant gaps in one area
- **D**: 1+ critical (raw SQL on input, secrets in code, no service layer)
- **F**: fundamental problems across multiple areas
