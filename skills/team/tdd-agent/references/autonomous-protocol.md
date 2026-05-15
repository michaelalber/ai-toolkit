# Autonomous Protocol Reference

## Complete Session Workflow

### Session Initialization

```markdown
## TDD Agent Session

**Request**: [user's feature request]
**Mode**: Autonomous
**Stack**: [detected or specified language/framework]
**Test Framework**: [detected or specified]

### Session Initialization

1. Analyzing request...
2. Breaking down into testable behaviors:
   - [ ] Behavior 1: [description]
   - [ ] Behavior 2: [description]
   - [ ] Behavior 3: [description]

3. Identifying test file location: [path]
4. Identifying implementation file: [path]

<tdd-state>
phase: RED
iteration: 1
feature: [first behavior]
current_test: none
tests_passing: unknown
</tdd-state>

Beginning RED phase for first behavior.
```

### Complete Iteration Example

```markdown
---

### RED Phase — Iteration 1

**Target Behavior**: User can create account with email and password

**Writing Test**:

```python
# tests/test_user_service.py
import pytest
from user_service import UserService

def test_create_user_with_email_and_password():
    service = UserService()
    user = service.create_user(
        email="alice@example.com",
        password="secure123"
    )
    assert user.email == "alice@example.com"
    assert user.id is not None
```

**Running Tests**:
```
$ pytest tests/test_user_service.py::test_create_user_with_email_and_password -v
============================= test session starts =============================
collected 1 item

tests/test_user_service.py::test_create_user_with_email_and_password ERROR

E   ModuleNotFoundError: No module named 'user_service'
============================= 1 error in 0.05s ================================
```

**Failure Analysis**:
- Test fails: ✓
- Reason: `user_service` module doesn't exist
- This is expected — we haven't created the implementation yet

**Self-Check**:
- [x] Test file exists
- [x] Test is syntactically valid
- [x] Test suite runs without internal error
- [x] New test fails
- [x] Failure is for expected reason (missing module)

<tdd-state>
phase: GREEN
iteration: 1
feature: User account creation
current_test: test_create_user_with_email_and_password
tests_passing: false
test_count: 1
failing_count: 1
last_verified: Module doesn't exist yet
</tdd-state>

Proceeding to GREEN phase.

---

### GREEN Phase — Iteration 1

**Test to Satisfy**: `test_create_user_with_email_and_password`
**Required Behavior**: Return user object with email and id

**Implementation Strategy Decision**:
- Test requires: email stored, id generated
- Simplest: Store email as attribute, generate UUID for id
- Strategy: Obvious Implementation (simple attribute assignment)

**Minimal Implementation**:

```python
# user_service.py
import uuid

class User:
    def __init__(self, email, id):
        self.email = email
        self.id = id

class UserService:
    def create_user(self, email, password):
        return User(email=email, id=str(uuid.uuid4()))
```

**Note**: Password is accepted but not stored yet — test doesn't verify storage.

**Running Tests**:
```
$ pytest tests/test_user_service.py -v
============================= test session starts =============================
collected 1 item

tests/test_user_service.py::test_create_user_with_email_and_password PASSED

============================= 1 passed in 0.02s ===============================
```

**Self-Check**:
- [x] Implementation is minimal (only what test requires)
- [x] No extra features added
- [x] Test suite runs without error
- [x] All tests pass
- [x] New test passes

<tdd-state>
phase: REFACTOR
iteration: 1
feature: User account creation
current_test: test_create_user_with_email_and_password
tests_passing: true
test_count: 1
failing_count: 0
</tdd-state>

Proceeding to REFACTOR phase.

---

### REFACTOR Phase — Iteration 1

**Starting State**: 1 test passing

**Code Review**:
```python
# Current state of user_service.py
import uuid

class User:
    def __init__(self, email, id):
        self.email = email
        self.id = id

class UserService:
    def create_user(self, email, password):
        return User(email=email, id=str(uuid.uuid4()))
```

**Smell Detection**:
- [x] Methods under 10 lines: Yes
- [x] Clear naming: Yes
- [x] No duplication: Yes
- [x] Single responsibility: Yes

**Decision**: Code is clean for current scope. No refactoring needed.

**Verification** (confirming green state):
```
$ pytest tests/test_user_service.py -v
============================= 1 passed in 0.02s ===============================
```

<tdd-state>
phase: RED
iteration: 2
feature: User account creation (next behavior)
current_test: none
tests_passing: true
test_count: 1
failing_count: 0
</tdd-state>

Ready for next behavior. Proceeding to RED phase.

---

### RED Phase — Iteration 2

**Target Behavior**: Password is hashed before storage

**Writing Test**:

```python
# tests/test_user_service.py (adding to existing file)
import hashlib

def test_password_is_hashed():
    service = UserService()
    user = service.create_user(
        email="bob@example.com",
        password="mypassword"
    )
    # Password should not be stored in plain text
    assert user.password_hash is not None
    assert user.password_hash != "mypassword"
    # Should be able to verify password
    expected_hash = hashlib.sha256("mypassword".encode()).hexdigest()
    assert user.password_hash == expected_hash
```

**Running Tests**:
```
$ pytest tests/test_user_service.py -v
============================= test session starts =============================
collected 2 items

tests/test_user_service.py::test_create_user_with_email_and_password PASSED
tests/test_user_service.py::test_password_is_hashed FAILED

E   AttributeError: 'User' object has no attribute 'password_hash'
============================= 1 failed, 1 passed in 0.03s =====================
```

**Failure Analysis**:
- Test fails: ✓
- Reason: `User` doesn't have `password_hash` attribute
- Previous test still passes: ✓
- Expected failure: ✓

<tdd-state>
phase: GREEN
iteration: 2
feature: Password hashing
current_test: test_password_is_hashed
tests_passing: false
test_count: 2
failing_count: 1
</tdd-state>

Proceeding to GREEN phase.
```

## Multi-Iteration Workflow

### Behavior Breakdown Pattern

For complex features, break into iterations:

```markdown
## Feature: Shopping Cart

### Behaviors to Implement (in order):
1. Cart can be created empty
2. Item can be added to cart
3. Cart tracks item quantities
4. Cart calculates total price
5. Item can be removed from cart
6. Cart can be cleared

### Iteration Plan:
| Iteration | RED (Test) | GREEN (Implement) | REFACTOR |
|-----------|------------|-------------------|----------|
| 1 | test_new_cart_is_empty | Cart class | - |
| 2 | test_add_item | add_item method | - |
| 3 | test_item_quantity | quantity tracking | Maybe extract Item class |
| 4 | test_total_price | total calculation | - |
| 5 | test_remove_item | remove_item method | - |
| 6 | test_clear_cart | clear method | Final cleanup |
```

### Between-Iteration Checklist

After each complete iteration (RED → GREEN → REFACTOR):

```
Iteration Complete Checklist:
├── All tests passing?
├── Implementation minimal for all tests?
├── Code reviewed for smells?
├── State block updated?
├── Ready for next behavior?
└── Document progress
```

## Error Recovery Protocols

### Protocol: Test Infrastructure Failure

```
Symptom: Tests won't run at all

Steps:
1. Check test file syntax
   $ python -m py_compile tests/test_file.py

2. Check imports
   $ python -c "from module import Class"

3. Check test framework
   $ pytest --version
   $ pytest --collect-only

4. Fix infrastructure issue
5. Do NOT write implementation until tests run
6. Resume from last valid state
```

### Protocol: Unexpected Test Failure

```
Symptom: A test that was passing now fails

Steps:
1. Identify which test failed
2. Check if change affected that test's dependencies
3. If during REFACTOR: Revert immediately
4. If during GREEN: Check for interference
5. Run test in isolation
   $ pytest path/to/test.py::specific_test -v

6. Fix the regression before proceeding
```

### Protocol: Flaky Test Detected

```
Symptom: Test sometimes passes, sometimes fails

Steps:
1. Run test 10 times
   $ pytest test_file.py::test_name --count=10

2. Identify source of non-determinism:
   - Time-dependent?
   - Random values?
   - External service?
   - Shared state?

3. Fix the test to be deterministic
4. Verify with multiple runs
5. Only then continue TDD cycle
```

### Protocol: State Recovery

```
Symptom: Lost track of TDD state

Steps:
1. Run full test suite
   $ pytest -v

2. Analyze results:
   - All pass → REFACTOR or new RED
   - One fails → GREEN for that test
   - Many fail → Something broke, investigate

3. Check recent changes:
   $ git diff
   $ git status

4. Reconstruct state block:
   <tdd-state>
   phase: [determined from analysis]
   iteration: [count from test file]
   ...
   </tdd-state>

5. Log the recovery
6. Continue from reconstructed state
```

## Session Completion

### Completion Criteria

```
Session is complete when:
├── All planned behaviors are implemented
├── All tests pass
├── Code has been refactored
├── No obvious smells remain
└── User's original request is satisfied
```

### Session Summary Template

```markdown
## TDD Session Complete

**Feature**: [description]
**Duration**: [iterations completed]

### Tests Written:
1. `test_behavior_one` - [description]
2. `test_behavior_two` - [description]
...

### Final Test Run:
```
[output showing all tests pass]
```

### Implementation Summary:
- Files created/modified: [list]
- Key classes/functions: [list]
- Architecture notes: [if any]

### Coverage Notes:
- Behaviors covered: [list]
- Edge cases to consider for future: [list]

### Code Quality:
- Refactorings performed: [list]
- Remaining smells: [none | list]

<tdd-state>
phase: COMPLETE
iterations: N
tests_passing: true
test_count: N
</tdd-state>
```
