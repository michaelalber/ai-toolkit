# Code Review Checklist

## TDD Verification

- [ ] Tests written before implementation (check commit history)
- [ ] Test names follow `test_should_<expected>_when_<condition>`
- [ ] AAA pattern: clear Arrange/Act/Assert sections
- [ ] One assertion per test (except related validations)
- [ ] Edge cases covered

## YAGNI Check

- [ ] No speculative abstractions
- [ ] Interfaces justified by 3+ implementations (Rule of Three)
- [ ] No unused parameters or "future" placeholders
- [ ] Simplest solution that works

## Quality Gates

| Gate | Threshold | Pass? |
|------|-----------|-------|
| Cyclomatic Complexity | <10 per method | [ ] |
| Test Coverage | 80%+ (95% security) | [ ] |
| Maintainability Index | 70+ | [ ] |
| Code Duplication | <3% | [ ] |
| Ruff | Zero errors | [ ] |
| mypy --strict | Zero errors | [ ] |
| bandit | Zero high/medium | [ ] |

## Architecture

- [ ] Single Responsibility (one reason to change)
- [ ] Dependencies flow inward (no infrastructure in domain)
- [ ] No circular imports
- [ ] Public API minimal and documented

## Type Safety

- [ ] All public functions typed
- [ ] `Optional` explicit, not implicit `None`
- [ ] Generics used where appropriate
- [ ] No `# type: ignore` without comment

## Error Handling

- [ ] Specific exceptions, not bare `except:`
- [ ] Errors logged with context
- [ ] Fail-fast in invalid states
- [ ] Resources cleaned up (context managers)

## Performance

- [ ] No N+1 queries
- [ ] Expensive operations lazy/cached
- [ ] Async where I/O bound
- [ ] Profiled if performance-critical

## Knowledge Base Lookups

Use `search_knowledge` (grounded-code-mcp, `collection="python"`) to ground findings and recommendations in authoritative references rather than training data.

| Query | When to Call |
|-------|--------------|
| `search_knowledge("Pydantic BaseSettings configuration management", collection="python")` | At SCAN — config & secrets hygiene check |
| `search_knowledge("typing Protocol structural subtyping boundaries", collection="python")` | At SCAN — clean boundaries / dependency direction check |
| `search_knowledge("asyncio blocking call event loop", collection="python")` | At SCAN — async discipline check |
| `search_knowledge("FastAPI Django Flask application structure", collection="python")` | At DETECT — confirm idiomatic layout for the detected framework |
