# Phase Verification Patterns

Per-stack verification commands to include in plan phase success criteria.

## .NET / C# (dotnet CLI)

```markdown
#### Automated verification
- [ ] `dotnet build --no-restore` — 0 errors, 0 warnings
- [ ] `dotnet test --no-build --verbosity normal` — all pass
- [ ] `dotnet format --verify-no-changes` — clean

# Scoped to a specific feature:
- [ ] `dotnet test --filter "Category=Unit&Feature=Review"` — all pass

# If migrations involved:
- [ ] `dotnet ef migrations add [MigrationName] --dry-run` — no unexpected schema changes
- [ ] `dotnet ef database update --dry-run` — migration applies without errors

# Blazor Server:
- [ ] `dotnet run` starts without runtime errors
- [ ] Navigate to [URL] — component renders without JS console errors
```

## Python

```markdown
#### Automated verification
- [ ] `python -m pytest tests/ -v` — all pass
- [ ] `python -m pytest tests/ --cov=src --cov-report=term-missing` — coverage ≥ 80%
- [ ] `ruff check .` — 0 lint errors
- [ ] `mypy src/` — 0 type errors

# Scoped to module:
- [ ] `python -m pytest tests/test_[module].py -v` — all pass

# FastAPI app:
- [ ] `uvicorn app.main:app --reload` starts without errors
- [ ] `curl http://localhost:8000/health` returns 200
```

## JavaScript / TypeScript

```markdown
#### Automated verification
- [ ] `npm run build` — 0 TypeScript errors
- [ ] `npm test` — all pass
- [ ] `npm run lint` — 0 lint errors

# Vite / Next.js:
- [ ] `npm run build` — production build succeeds
- [ ] `npm run preview` starts without errors

# Unit tests scoped:
- [ ] `npm test -- --testPathPattern=[feature]` — all pass
```

## PHP / Laravel

```markdown
#### Automated verification
- [ ] `composer test` — all pass (or `php artisan test`)
- [ ] `./vendor/bin/phpstan analyse` — 0 errors
- [ ] `./vendor/bin/php-cs-fixer fix --dry-run` — no formatting issues

# Scoped:
- [ ] `php artisan test --filter=[TestClass]` — all pass

# With migrations:
- [ ] `php artisan migrate --pretend` — SQL output looks correct
```

## Git verification (any stack)

```markdown
# Always appropriate as a final phase check:
- [ ] `git diff --stat` — only expected files changed
- [ ] `git status` — no unexpected untracked files
```

## Custom grep checks (any stack)

Use in final verification phases to confirm cleanup:

```markdown
#### Final cleanup verification
- [ ] `grep -rn "TODO\|FIXME" path/to/feature/` — 0 results from this implementation
- [ ] `grep -rn "OldTypeName" src/` — 0 results (rename complete)
- [ ] `grep -rn "deprecated_method" .` — 0 results
```

## Telerik Blazor UI verification

For projects using Telerik Blazor components:

```markdown
#### Manual verification
- [ ] `dotnet run` starts the Blazor Server app
- [ ] Navigate to [affected page URL]
- [ ] TelerikGrid renders without errors
- [ ] Browser console shows no JS interop errors
- [ ] [Specific interaction] behaves as expected
```

## Choosing which commands to include

**Always include:**
- Build command (catches compilation errors)
- Relevant unit tests (scoped to the feature if possible)

**Include when applicable:**
- Integration tests (if the phase touches infrastructure or external services)
- Lint/format check (if the project enforces it in CI)
- Migration dry-run (if the phase includes schema changes)
- Manual verification (if the change has UI or runtime behavior that tests don't cover)

**Do NOT include:**
- Full test suite in every phase (slows implementation; use scoped tests per phase, full suite in final phase)
- Build commands that require network access (use `--no-restore` / `--offline` variants)
