# Python Feature Slice Output Templates

## Scaffold Checklist

```markdown
## Feature Slice Scaffold: [Feature Name]

### Files Created
- [ ] `features/<name>/__init__.py`
- [ ] `features/<name>/router.py`
- [ ] `features/<name>/service.py`
- [ ] `features/<name>/models.py`
- [ ] `features/<name>/dependencies.py`
- [ ] `tests/features/<name>/__init__.py`
- [ ] `tests/features/<name>/test_router.py`
- [ ] `tests/features/<name>/test_service.py`

### Registration
- [ ] Router added to `main.py` / `app/routers.py`
- [ ] Prefix set: `/api/v1/<name>`
- [ ] Tags set: `["<name>"]`

### Verification
- [ ] `uvicorn` starts without errors
- [ ] `/docs` renders the new endpoints
- [ ] `pytest tests/features/<name>/` passes
- [ ] No cross-feature imports detected
```

## Feature Folder Structure

```
project/
├── features/
│   └── orders/
│       ├── __init__.py
│       ├── router.py          ← thin: extract, call service, return
│       ├── service.py         ← business logic; Protocol + concrete
│       ├── models.py          ← Pydantic v2 request/response models
│       └── dependencies.py    ← Depends() factory functions
├── shared/
│   ├── database.py            ← SQLAlchemy session factory
│   └── auth.py                ← get_current_user dependency
├── tests/
│   └── features/
│       └── orders/
│           ├── test_router.py ← TestClient integration tests
│           └── test_service.py← unit tests with mocked deps
└── main.py                    ← app creation + router registration
```
