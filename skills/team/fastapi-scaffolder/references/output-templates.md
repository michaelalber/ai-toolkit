# FastAPI Scaffolder Output Template

The endpoint scaffold checklist the skill reports to the user.

```markdown
## FastAPI Endpoint Scaffold: [Endpoint Name]

### Endpoint Configuration
- [ ] Router created with `prefix` and `tags`
- [ ] Versioning prefix set: `/api/v1/`
- [ ] Authentication dependency added

### Models
- [ ] Request model(s) created (Pydantic v2, frozen)
- [ ] Response model(s) created
- [ ] Field validators added where needed

### OpenAPI Documentation
- [ ] `summary` set on every route
- [ ] `description` set on routes with complex behavior
- [ ] `response_model` set on every route
- [ ] `responses` dict includes all possible status codes
- [ ] `tags` set on router

### Security
- [ ] Authentication dependency applied
- [ ] Authorization (role/permission) applied if needed
- [ ] Rate limiting applied

### Tests
- [ ] Unit tests for service layer
- [ ] Integration tests with TestClient
- [ ] Authentication tested (valid token, invalid token, missing token)

### Verification
- [ ] App starts without errors
- [ ] `/docs` renders the new endpoints
- [ ] All tests pass
- [ ] `ruff check` passes
- [ ] `mypy` passes
```

## Project Structure

```
app/
  main.py              # FastAPI app creation, middleware, router registration
  config.py            # Settings (pydantic-settings BaseSettings)
  dependencies.py      # Shared dependencies (get_db, get_current_user)
  exceptions.py        # Custom exception handlers
  health.py            # Health check endpoints
  routers/
    __init__.py
    v1/
      __init__.py
      [feature].py     # Feature routers
```
