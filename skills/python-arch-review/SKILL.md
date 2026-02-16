---
name: python-arch-review
description: Architecture review for Python 3 projects enforcing TDD (Red->Green->Refactor->Quality Check), YAGNI principles, and code quality gates. Use when (1) writing new Python code, (2) reviewing existing Python code, (3) refactoring Python modules, (4) adding tests to Python projects, (5) checking code quality metrics, (6) running quality gates before merging, or (7) improving Python architecture with type safety and clean design. Integrates Ruff, mypy, radon, bandit, pip-audit, and pytest-cov.
---

# Python Architecture Review

> "Any fool can write code that a computer can understand. Good programmers write code that humans can understand."
> -- Martin Fowler

> "Make it work, make it right, make it fast -- in that order."
> -- Kent Beck

## Core Philosophy

Python's power lies in its expressiveness, but expressiveness without discipline produces codebases that rot. This skill enforces a TDD-first workflow where every change begins with a failing test and ends with a clean quality gate. The cycle is non-negotiable: Red, Green, Refactor, Quality Check. Every iteration. No exceptions for production code.

YAGNI is the governing constraint. The simplest code that passes the tests is the right code. Abstractions are earned through repetition (Rule of Three), not anticipated through speculation. When three concrete implementations share a pattern, then and only then do you extract the abstraction. Until that point, duplication is cheaper than the wrong abstraction.

Quality gates are not bureaucracy -- they are automated enforcement of standards that humans forget under deadline pressure. Ruff catches style drift and bug-prone patterns. mypy catches type errors that tests miss. Bandit catches security mistakes that code review overlooks. Radon catches complexity creep before it becomes unmaintainable. Together, they form a safety net that frees the developer to focus on design instead of bookkeeping.

**What this skill IS:**

- A disciplined process for writing, testing, and reviewing Python code through the TDD cycle.
- A set of automated quality gates that enforce measurable standards for complexity, coverage, type safety, and security.
- A framework for applying YAGNI and clean architecture principles to real Python projects.
- A tool for making code quality objective rather than subjective.

**What this skill is NOT:**

- It is NOT a high-level architecture critique. That is what `architecture-review` does through Socratic questioning.
- It is NOT optional for production code. Spikes and prototypes get a pass; everything else goes through the gates.
- It is NOT a replacement for thinking. Quality gates catch mistakes, but they cannot enforce good design. Design judgment comes from practice.
- It is NOT language-agnostic. Every rule, tool, and pattern in this skill is specific to Python 3.10+.

## Domain Principles Table

| # | Principle | Description | Applied As |
|---|-----------|-------------|------------|
| 1 | **TDD Discipline** | Every code change begins with a failing test. Not "write tests." Write a failing test FIRST, then write the minimum code to make it pass, then refactor. The test defines the requirement. The code satisfies it. Reversing this order produces code that tests confirm rather than tests that drive design. | Before writing any implementation code, write a test that fails. Confirm it fails. Only then write the implementation. |
| 2 | **YAGNI as Default** | Do not build what you do not need. Every unused abstraction is a maintenance burden, a source of confusion, and a temptation to over-engineer further. The Rule of Three governs when abstraction is justified: when three concrete cases share a pattern, extract it. Not before. | Challenge every abstraction. Ask: "Do I have three concrete uses for this? If not, inline it." |
| 3 | **Type Safety as Documentation** | Type hints are not decorations. They are executable documentation that mypy verifies on every commit. A function signature with complete type annotations tells the reader what it accepts, what it returns, and what can be None -- without reading the body. Strict mypy mode enforces this discipline. | All public functions must have complete type annotations. No `# type: ignore` without an explanatory comment. Use `Optional` explicitly. |
| 4 | **Clean Architecture Boundaries** | Dependencies flow inward. Domain logic does not import infrastructure. Infrastructure adapts to domain interfaces using Protocols or abstract base classes. No circular imports. The domain layer is the most stable layer -- it changes only when business rules change. | Enforce dependency direction: domain has zero imports from infrastructure. Use `typing.Protocol` for boundaries. |
| 5 | **Dependency Management** | Every dependency is a liability. Each one can introduce security vulnerabilities, breaking changes, and license conflicts. Pin versions. Audit regularly with `pip-audit`. Prefer the standard library over third-party packages when the standard library is adequate. | Run `pip-audit` in the quality gate. Question every new dependency: "Does the standard library solve this?" |
| 6 | **Testing Quality over Quantity** | Coverage percentage is a necessary but insufficient metric. 100% coverage with meaningless assertions is worse than 80% coverage with tests that verify behavior. Tests should follow Arrange-Act-Assert, test one behavior each, use descriptive names, and cover edge cases. | Enforce `test_should_<expected>_when_<condition>` naming. One assertion per test. Review tests for meaningful assertions. |
| 7 | **Security as Habit** | Security is not a phase. It is a habit baked into every function. Parameterized queries, no dynamic code execution with user input, `subprocess` with `shell=False`, secrets in environment variables, `secrets` module instead of `random` for tokens. Bandit catches some of this; the rest requires discipline. | Run bandit in every quality gate. Follow [references/security-checklist.md](references/security-checklist.md) for OWASP Top 10 Python checks. |
| 8 | **Incremental Improvement** | Large refactors fail. Small, tested, incremental improvements succeed. Each TDD cycle improves one thing. Each refactor phase cleans up one smell. Over dozens of cycles, the codebase transforms. This is sustainable. A weekend rewrite is not. | Limit refactor scope to what the current tests cover. Add tests before refactoring untested code. |
| 9 | **Documentation Through Tests** | Well-named tests are the best documentation. `test_should_raise_value_error_when_amount_is_negative` tells you more about the function's contract than any docstring. Tests are documentation that cannot go stale because they break when the behavior changes. | Write test names that describe the contract. If you cannot name the test clearly, you do not understand the requirement. |
| 10 | **Tooling as Enforcement** | Humans forget. Tools do not. Every standard that matters is enforced by a tool: Ruff for style and patterns, mypy for types, radon for complexity, bandit for security, pytest-cov for coverage. The quality gate script (`scripts/quality_check.py`) runs them all in sequence. If it passes, the code meets the standard. If it fails, the code does not ship. | Run `scripts/quality_check.py <path>` before every commit. No exceptions for production code. |

## Workflow: The TDD Cycle

Every code change follows the four-phase cycle: **Red -> Green -> Refactor -> Quality Check**. The phases are sequential. Do not skip phases. Do not reorder phases.

### Phase 1: RED -- Write a Failing Test

You write a test that describes the behavior you want. You run it. It fails. The failure confirms that the test is actually testing something and that the behavior does not already exist.

**Actions:**

1. Identify the next behavior to implement (from requirements, user story, or bug report)
2. Write a single test using Arrange-Act-Assert pattern
3. Name it `test_should_<expected>_when_<condition>`
4. Run the test and confirm it FAILS (red)
5. If the test passes without new code, either the behavior already exists or the test is wrong

**Key Questions:**

- What is the simplest behavior I can test next?
- Does this test name clearly describe the contract?
- Am I testing behavior or implementation detail?
- Have I covered the edge cases for this behavior?

**Completion Criteria:**

- One new test exists
- The test fails with a clear, expected error
- The test name follows the naming convention
- The test uses Arrange-Act-Assert structure

```python
def test_should_return_sum_when_two_positive_numbers():
    # Arrange
    calc = Calculator()

    # Act
    result = calc.add(2, 3)

    # Assert
    assert result == 5
```

### Phase 2: GREEN -- Minimal Implementation

You write the absolute minimum code to make the failing test pass. Not elegant code. Not complete code. The minimum. If the test expects `5`, returning `5` is a valid Green step (it will be driven to the real implementation by additional tests). Resist the urge to write more than the test demands.

**Actions:**

1. Write the simplest code that makes the failing test pass
2. Run ALL tests (not just the new one)
3. If any test fails, fix the implementation without changing tests
4. If you must change a test, go back to Red -- you are redefining the requirement

**Key Questions:**

- Is this the simplest code that passes the test?
- Am I adding behavior that no test requires?
- Do all existing tests still pass?
- Am I tempted to "clean up" before the test is green? (Stop -- that is the Refactor phase.)

**Completion Criteria:**

- The new test passes
- All existing tests still pass
- No code was written beyond what the tests require

### Phase 3: REFACTOR -- Clean Up Under Green Tests

The tests are green. Now improve the code's structure without changing its behavior. Extract methods. Remove duplication. Improve names. Simplify conditionals. The tests are your safety net: if they stay green, your refactoring preserved behavior.

**Actions:**

1. Look for code smells: duplication, long methods, unclear names, deep nesting
2. Apply one refactoring at a time (extract method, rename, inline, etc.)
3. Run tests after EACH refactoring step
4. If tests break, undo the refactoring and try a smaller step
5. Apply YAGNI: do not add abstractions the tests do not require

**Key Questions:**

- Can I extract a well-named function from this block?
- Is there duplication I can remove without adding premature abstraction?
- Are variable and function names self-documenting?
- Is the cyclomatic complexity of this method under 10?
- Am I adding new behavior? (Stop -- go back to Red.)

**Completion Criteria:**

- All tests still pass
- Code smells addressed (no method over 10 CC, no class over 200 lines)
- Names are clear and self-documenting
- No new behavior was introduced

### Phase 4: QUALITY CHECK -- Run the Full Gate

Run the complete quality gate. This is not optional. Every cycle ends here. The gate catches what the human eye misses: style drift, type errors, complexity creep, security mistakes, and coverage gaps.

**Actions:**

1. Run the quality gate script:
   ```bash
   scripts/quality_check.py <path>
   ```
2. If any gate fails, fix the issue and re-run (do not proceed with failures)
3. Review the output for warnings even when all gates pass
4. Commit only after all gates are green

**Gate Thresholds:**

| Gate | Tool | Threshold | Reference |
|------|------|-----------|-----------|
| Lint + Format | Ruff | Zero errors | [references/ruff-config.md](references/ruff-config.md) |
| Type Check | mypy --strict | Zero errors | [references/mypy-config.md](references/mypy-config.md) |
| Cyclomatic Complexity | radon | Methods < 10, Classes < 20 | quality_check.py `--max-complexity` |
| Maintainability Index | radon | 70+ | quality_check.py `--min-maintainability` |
| Test Coverage | pytest-cov | 80% business logic, 95% security-critical | quality_check.py `--min-coverage` |
| Security Scan | bandit | Zero high/medium findings | [references/security-checklist.md](references/security-checklist.md) |
| Code Duplication | pylint | < 3% | Review checklist |

See [references/review-checklist.md](references/review-checklist.md) for the full code review checklist.

**Key Questions:**

- Did all gates pass?
- Are there warnings I should address even though they are not failures?
- Is coverage adequate for the code I just wrote?
- Did bandit flag anything in the new code?

**Completion Criteria:**

- `scripts/quality_check.py <path>` exits with code 0
- No new warnings introduced
- Coverage meets threshold for the module type (80% general, 95% security-critical)
- Code is ready to commit

## State Block

Maintain state across conversation turns using the `<python-review-state>` tag:

```
<python-review-state>
mode: [red | green | refactor | quality_check | review]
project_path: [path to project root]
phase: [current TDD phase]
tests_passing: [true | false | unknown]
coverage_pct: [number or unknown]
ruff_clean: [true | false | unknown]
mypy_clean: [true | false | unknown]
security_clean: [true | false | unknown]
last_action: [what was just done]
next_action: [what should happen next]
</python-review-state>
```

### State Progression Example

```
<python-review-state>
mode: red
project_path: /home/dev/myproject
phase: RED -- writing failing test
tests_passing: true (existing tests)
coverage_pct: 82
ruff_clean: true
mypy_clean: true
security_clean: true
last_action: Identified next behavior -- user registration validation
next_action: Write test_should_raise_validation_error_when_email_is_invalid
</python-review-state>
```

```
<python-review-state>
mode: green
project_path: /home/dev/myproject
phase: GREEN -- minimal implementation
tests_passing: false (new test failing as expected)
coverage_pct: 82
ruff_clean: true
mypy_clean: true
security_clean: true
last_action: Wrote test_should_raise_validation_error_when_email_is_invalid -- confirmed it fails
next_action: Write minimal validate_email function to pass the test
</python-review-state>
```

```
<python-review-state>
mode: refactor
project_path: /home/dev/myproject
phase: REFACTOR -- cleaning up under green tests
tests_passing: true (all 47 tests passing)
coverage_pct: 84
ruff_clean: true
mypy_clean: true
security_clean: true
last_action: Implemented validate_email -- all tests green
next_action: Extract email regex pattern to module constant, rename internal helper
</python-review-state>
```

```
<python-review-state>
mode: quality_check
project_path: /home/dev/myproject
phase: QUALITY CHECK -- running full gate
tests_passing: true (all 47 tests passing)
coverage_pct: 85
ruff_clean: true
mypy_clean: true
security_clean: true
last_action: Refactoring complete -- extracted constant, renamed helper, tests still green
next_action: Run scripts/quality_check.py src/
</python-review-state>
```

## Output Templates

### Session Opening

```markdown
## Python Architecture Review Session

**Project**: [project name]
**Path**: [project path]
**Scope**: [what we are working on -- new feature, refactoring, bug fix, test improvement]

**Current Quality Status:**
| Gate | Status |
|------|--------|
| Tests | [passing/failing/none] |
| Coverage | [N%] |
| Ruff | [clean/errors] |
| mypy | [clean/errors] |
| Security | [clean/findings] |

**Workflow:** We follow the TDD cycle -- Red, Green, Refactor, Quality Check -- for every change. I will guide you through each phase.

**Starting phase:** [RED -- identifying the first behavior to test]

<python-review-state>
mode: red
project_path: [path]
phase: RED -- identifying first test
tests_passing: [status]
coverage_pct: [number or unknown]
ruff_clean: [status]
mypy_clean: [status]
security_clean: [status]
last_action: Session opened, initial quality status assessed
next_action: Identify first behavior to test
</python-review-state>
```

### Phase Transition

```markdown
---

### Phase Complete: [RED | GREEN | REFACTOR | QUALITY CHECK]

**What we did:** [summary of actions taken in this phase]
**Result:** [outcome -- test written and failing / test passing / code cleaned up / gates passed]

### Moving to: [next phase]

**Next steps:**
1. [specific action]
2. [specific action]

---
```

### Quality Report

```markdown
## Quality Gate Report

**Project**: [project name]
**Date**: [date]
**Path scanned**: [path]

| Gate | Status | Details |
|------|--------|---------|
| Ruff (lint) | [PASS/FAIL] | [error count or "clean"] |
| Ruff (format) | [PASS/FAIL] | [error count or "clean"] |
| mypy --strict | [PASS/FAIL] | [error count or "clean"] |
| Cyclomatic Complexity | [PASS/FAIL] | [max CC found / threshold] |
| Maintainability Index | [PASS/FAIL] | [min MI found / threshold] |
| Coverage | [PASS/FAIL] | [percentage / threshold] |
| Bandit (security) | [PASS/FAIL] | [finding count or "clean"] |

**Overall**: [ALL GATES PASSED | FAILED: list of failed gates]

**Actions Required:**
- [action 1 if any gates failed]
- [action 2]
```

### Session Closing

```markdown
## Session Summary

**What we accomplished:**
- [list of behaviors implemented through TDD cycles]
- [number of TDD cycles completed]
- [quality improvements made]

**Quality Status at Close:**
| Gate | Before | After |
|------|--------|-------|
| Tests | [N] passing | [M] passing |
| Coverage | [N%] | [M%] |
| Ruff | [status] | [status] |
| mypy | [status] | [status] |
| Security | [status] | [status] |

**Next session starting point:**
- [what to work on next]
- [any deferred refactoring]
- [any quality issues to address]

<python-review-state>
mode: review
project_path: [path]
phase: Session complete
tests_passing: true
coverage_pct: [final number]
ruff_clean: true
mypy_clean: true
security_clean: true
last_action: Session closed -- all gates green
next_action: [what to do in next session]
</python-review-state>
```

## AI Discipline Rules

### CRITICAL: Always Write Tests First -- No Exceptions

The test comes before the implementation. Always. If you catch yourself writing implementation code without a failing test, stop immediately, delete the implementation, and write the test. This is the single most important rule in this skill. Breaking it undermines the entire TDD discipline.

```
WRONG:
  def validate_email(email: str) -> bool:
      return "@" in email and "." in email.split("@")[1]

  # Then writing a test after the fact:
  def test_validate_email():
      assert validate_email("user@example.com") is True

RIGHT:
  # First, write the failing test:
  def test_should_return_true_when_email_has_valid_format():
      assert validate_email("user@example.com") is True

  # Run it. Watch it fail (NameError: validate_email not defined).
  # Then write the minimal implementation:
  def validate_email(email: str) -> bool:
      return "@" in email and "." in email.split("@")[1]
```

### CRITICAL: Never Skip the Quality Check Phase

It is tempting to skip the quality gate when "it is just a small change" or "I will run it later." Do not. Small changes accumulate. Type errors slip in. Complexity creeps up. Security issues hide. The quality gate is cheap to run and expensive to skip. Run it every cycle.

```
WRONG:
  # Tests pass, looks good, let me commit...
  git add . && git commit -m "add email validation"

RIGHT:
  # Tests pass. Now run the gate.
  scripts/quality_check.py src/
  # All gates pass. NOW commit.
  git add . && git commit -m "add email validation"
```

### CRITICAL: Do Not Over-Engineer -- YAGNI Governs

When you see a pattern that "might be useful later," resist the urge to abstract it. Write the concrete implementation. When the second case appears, note the similarity but keep it concrete. When the third case appears, THEN extract the abstraction. Premature abstraction is more expensive than duplication.

```
WRONG:
  # One email validator needed, so build a framework:
  class ValidatorFactory:
      _registry: dict[str, type[Validator]] = {}

      @classmethod
      def register(cls, name: str) -> Callable:
          def decorator(validator_cls: type[Validator]) -> type[Validator]:
              cls._registry[name] = validator_cls
              return validator_cls
          return decorator

  @ValidatorFactory.register("email")
  class EmailValidator(Validator):
      ...

RIGHT:
  # One email validator needed. Write one email validator.
  def validate_email(email: str) -> bool:
      """Validate email format. Simple and direct."""
      if "@" not in email:
          return False
      local, domain = email.rsplit("@", 1)
      return bool(local) and "." in domain
```

### CRITICAL: Keep Functions Small and Focused

A function should do one thing. If you need a comment to explain what a block of code within a function does, that block should be its own function with a descriptive name. Cyclomatic complexity above 10 is a gate failure for a reason: complex functions are hard to test, hard to read, and hard to maintain.

```
WRONG:
  def process_order(order: Order) -> Result:
      # Validate the order
      if not order.items:
          raise ValueError("Empty order")
      if order.total < 0:
          raise ValueError("Negative total")
      for item in order.items:
          if item.quantity <= 0:
              raise ValueError(f"Invalid quantity for {item.name}")

      # Apply discounts
      if order.customer.is_premium:
          discount = order.total * 0.1
      elif order.total > 100:
          discount = order.total * 0.05
      else:
          discount = 0
      order.total -= discount

      # Check inventory and reserve
      for item in order.items:
          stock = get_stock(item.product_id)
          if stock < item.quantity:
              raise OutOfStockError(item.name)
          reserve_stock(item.product_id, item.quantity)

      return Result(success=True, total=order.total)

RIGHT:
  def process_order(order: Order) -> Result:
      validate_order(order)
      apply_discounts(order)
      reserve_inventory(order)
      return Result(success=True, total=order.total)

  def validate_order(order: Order) -> None:
      if not order.items:
          raise ValueError("Empty order")
      if order.total < 0:
          raise ValueError("Negative total")
      for item in order.items:
          if item.quantity <= 0:
              raise ValueError(f"Invalid quantity for {item.name}")

  def apply_discounts(order: Order) -> None:
      discount = _calculate_discount(order)
      order.total -= discount

  def _calculate_discount(order: Order) -> float:
      if order.customer.is_premium:
          return order.total * 0.1
      if order.total > 100:
          return order.total * 0.05
      return 0.0

  def reserve_inventory(order: Order) -> None:
      for item in order.items:
          stock = get_stock(item.product_id)
          if stock < item.quantity:
              raise OutOfStockError(item.name)
          reserve_stock(item.product_id, item.quantity)
```

### CRITICAL: Prefer Composition Over Inheritance

Deep inheritance hierarchies are the leading cause of fragile, hard-to-test Python code. Use composition by default. Use `typing.Protocol` for interface contracts. Reserve inheritance for genuine "is-a" relationships with shared behavior, not shared interfaces.

```
WRONG:
  class BaseRepository:
      def connect(self) -> None: ...
      def disconnect(self) -> None: ...

  class BaseUserRepository(BaseRepository):
      def get_user(self, id: str) -> User: ...

  class CachedUserRepository(BaseUserRepository):
      def get_user(self, id: str) -> User: ...

  class AuditedCachedUserRepository(CachedUserRepository):
      def get_user(self, id: str) -> User: ...
      # 4 levels deep. Good luck testing this.

RIGHT:
  class UserRepository(Protocol):
      def get_user(self, id: str) -> User | None: ...

  class PostgresUserRepository:
      def __init__(self, connection: Connection) -> None:
          self._conn = connection

      def get_user(self, id: str) -> User | None:
          ...

  class CachedUserRepository:
      def __init__(self, inner: UserRepository, cache: Cache) -> None:
          self._inner = inner
          self._cache = cache

      def get_user(self, id: str) -> User | None:
          cached = self._cache.get(id)
          if cached is not None:
              return cached
          user = self._inner.get_user(id)
          if user is not None:
              self._cache.set(id, user)
          return user
  # Flat composition. Each piece is independently testable.
```

### CRITICAL: Type Every Public Interface

Every public function, method, and class attribute must have complete type annotations. This is enforced by `mypy --strict`. Type annotations serve as machine-verified documentation, catch entire categories of bugs at static analysis time, and enable IDE support that makes the codebase navigable. `Optional` must be explicit -- never rely on implicit `None` defaults.

```
WRONG:
  def get_user(id, include_deleted=False):
      ...

  def process(data):
      results = []
      for item in data:
          results.append(transform(item))
      return results

RIGHT:
  def get_user(
      id: str,
      *,
      include_deleted: bool = False,
  ) -> User | None:
      ...

  def process(data: Sequence[RawItem]) -> list[ProcessedItem]:
      return [transform(item) for item in data]
```

## Anti-Patterns Table

| Anti-Pattern | Description | Why It Fails | What to Do Instead |
|--------------|-------------|-------------|-------------------|
| **Testing After Coding** | Writing the implementation first, then writing tests to confirm it works. | Tests written after the fact test the implementation, not the requirement. They mirror the code's structure and miss the cases the developer did not think of. They give false confidence without driving design. | Follow the Red phase strictly. Write the test FIRST. Watch it fail. Then implement. The test defines what "correct" means before you write the code. |
| **Ignoring Type Hints** | Leaving functions untyped or using `Any` liberally. "Python is dynamic, types are optional." | Type errors are the most common source of production bugs in dynamic languages. Without types, mypy cannot help you, IDEs cannot autocomplete, and the next developer must read the entire function body to understand its contract. | Run `mypy --strict`. Add type annotations to every public function. Use `typing.Protocol` for interfaces. See [references/mypy-config.md](references/mypy-config.md). |
| **Massive Test Fixtures** | Creating elaborate setup functions or fixtures that build complex object graphs for every test. | Tests become coupled to the fixture, not to the behavior. When the fixture changes, dozens of tests break for reasons unrelated to their purpose. Test setup becomes so complex that it needs its own tests. | Use factory functions that create minimal objects. Each test builds only what it needs. Use `pytest` fixtures sparingly and only for truly shared setup (database connections, temp directories). |
| **Mocking Everything** | Replacing every dependency with a mock to test in "isolation." | Tests that mock everything test the mocking framework, not the code. They pass when the implementation is wrong because the mocks return whatever you told them to. They break on every refactoring because they test internal structure. | Mock at boundaries (I/O, external services, time). Test business logic with real objects. Use `typing.Protocol` to define boundaries, then provide simple fakes for testing. |
| **God Classes** | Classes with 500+ lines, 20+ methods, and multiple unrelated responsibilities. "It is convenient to have everything in one place." | God classes violate Single Responsibility, are impossible to test in isolation, create merge conflicts in teams, and resist refactoring because everything depends on them. | Extract cohesive groups of methods into focused classes. Use composition to assemble them. Each class should have one reason to change. |
| **Premature Optimization** | Optimizing code before profiling. Adding caching, async, or complex data structures because "it might be slow." | Optimization without measurement is guessing. The bottleneck is almost never where you think it is. Premature optimization adds complexity, bugs, and maintenance cost for performance gains that may not matter. | Write clear, simple code first. Profile under realistic load. Optimize the measured bottleneck. Verify the optimization actually helped. |
| **Bare Except Clauses** | Using `except:` or `except Exception:` to catch everything. "It prevents crashes." | Catching everything hides bugs. `KeyboardInterrupt`, `SystemExit`, and `GeneratorExit` should not be caught. Even `except Exception` hides `TypeError` and `ValueError` that indicate bugs in your code, not runtime errors. | Catch specific exceptions. Log unexpected exceptions with full context. Use context managers for resource cleanup instead of try/except blocks. |
| **Ignoring the Quality Gate** | Running the quality gate selectively or skipping it when "it is just a small change." | Small changes accumulate. One skipped gate leads to another. Within weeks, the codebase has type errors, complexity violations, and security findings that are expensive to fix in bulk. The gate exists to prevent drift. | Run `scripts/quality_check.py` after every TDD cycle. No exceptions for production code. If the gate fails, fix the issue before committing. |
| **Copy-Paste Test Duplication** | Copying an existing test and changing one value instead of parameterizing. | Test files grow to thousands of lines. When the behavior changes, every copy must be updated individually. Missed copies produce tests that pass but verify stale behavior. | Use `pytest.mark.parametrize` for tests that vary only in input/output. Extract shared setup into well-named helper functions. |
| **Circular Imports** | Module A imports from Module B, which imports from Module A. "It works if you import inside the function." | Circular imports indicate tangled responsibilities. Import-time vs. runtime resolution creates subtle bugs. `TYPE_CHECKING` guards hide the problem but do not fix the design. | Extract the shared dependency into a third module. Invert the dependency using `typing.Protocol`. Restructure so dependencies flow in one direction. |

## Error Recovery

### Problem: Tests Will Not Pass After Green Phase

The implementation looks correct, but one or more tests fail unexpectedly.

**Indicators:**

- A previously passing test now fails
- The new test passes but an unrelated test breaks
- Test failures have confusing error messages unrelated to the change

**Recovery Actions:**

1. Do NOT change the failing tests to match the implementation. The tests define correctness.
2. Run only the failing test in isolation: `pytest path/to/test.py::test_name -v`. If it passes in isolation, the failure is caused by test interaction (shared state, fixture pollution).
3. Check for side effects in your implementation: did you modify a global, a class variable, or a mutable default argument?
4. If the failing test is genuinely wrong (testing behavior that should change), go back to the Red phase: update the test first to define the new expected behavior, confirm it fails, then fix the implementation.
5. If you cannot identify the cause within 10 minutes, `git stash` your changes and confirm the tests pass on the clean codebase. Then re-apply and bisect.

### Problem: Quality Gates Fail After Refactoring

The refactoring phase introduced quality gate failures (Ruff errors, mypy errors, complexity violations).

**Indicators:**

- `scripts/quality_check.py` exits with non-zero code
- Ruff reports new lint errors from refactored code
- mypy reports type errors after method extraction or signature changes
- Radon reports increased complexity (refactoring went the wrong direction)

**Recovery Actions:**

1. Read the gate output carefully. Most failures after refactoring are type annotation issues (mypy) or import ordering (Ruff).
2. For mypy failures: check that extracted functions have complete type annotations. Method extraction often loses return type annotations.
3. For Ruff failures: run `ruff check --fix .` for auto-fixable issues, then `ruff format .` for formatting.
4. For complexity increases: the refactoring made things worse. Undo it (`git checkout -- <file>`) and try a different approach. Splitting a method should reduce complexity, not increase it.
5. Fix all gate failures before returning to the Red phase. Do not carry quality debt forward.

### Problem: Legacy Code Without Tests

You need to modify code that has no tests, and you cannot write a failing test because you do not know what the code does.

**Indicators:**

- Coverage is 0% or near 0% for the module
- The code has no type annotations
- Functions are long (50+ lines) with high cyclomatic complexity
- No documentation or outdated documentation

**Recovery Actions:**

1. Do NOT refactor untested code. You will break it and not know.
2. Write characterization tests first: tests that document current behavior, not desired behavior. Call the function with known inputs and assert on the actual outputs.
3. Add type annotations to the function signature (do not change the body). Run mypy to find type-related bugs.
4. Once you have characterization tests covering the paths you need to modify, THEN write a failing test for the new behavior, and proceed with the normal TDD cycle.
5. Accept that legacy code improvement is gradual. Each time you touch a module, leave it with more tests than it had before. Over time, coverage rises and confidence grows.

### Problem: Security Findings in Existing Code

Bandit or the security checklist reveals vulnerabilities in code you did not write.

**Indicators:**

- Bandit reports high or medium severity findings
- `pip-audit` finds vulnerable dependencies
- The security checklist from [references/security-checklist.md](references/security-checklist.md) has unchecked items

**Recovery Actions:**

1. Triage by severity: high-severity findings (SQL injection, command injection, hardcoded secrets) get fixed immediately.
2. For each finding, write a test that demonstrates the vulnerability is addressed (e.g., a test that proves parameterized queries are used).
3. Fix the finding using the guidance in the bandit output or the security checklist.
4. Re-run `scripts/quality_check.py` to confirm the finding is resolved and no new findings were introduced.
5. For dependency vulnerabilities (`pip-audit`), update the dependency if a patched version exists. If no patch exists, evaluate whether the vulnerability affects your usage and document the risk.

## Integration with Other Skills

- **`architecture-review`** -- Use for high-level design critique. When this skill identifies structural problems (circular dependencies, unclear boundaries, coupling between modules), the architecture-review skill provides Socratic questioning to explore the design tradeoffs. This skill enforces code-level quality; architecture-review examines design-level quality.

- **`tdd-cycle`** -- Shares the Red-Green-Refactor workflow. When working in a non-Python language or when the TDD process itself needs coaching (not just enforcement), use tdd-cycle for the pedagogical approach. This skill adds Python-specific tooling and quality gates on top of the TDD discipline.

- **`security-review-trainer`** -- When bandit findings or the security checklist reveal patterns that recur, use security-review-trainer to build the habit of writing secure code by default. This skill scans for security issues; security-review-trainer teaches you to avoid them.

- **`dependency-mapper`** -- When the architecture boundaries are unclear or circular imports appear, use dependency-mapper to generate a concrete dependency graph from the codebase. Compare the actual dependency graph against the intended clean architecture boundaries. This skill defines the rules; dependency-mapper shows the reality.

## When to Skip Quality Checks

Never skip for production code. Acceptable exceptions:

- Spike/prototype branches (labeled `spike/*`)
- Documentation-only changes
- CI/CD config changes

Even in these cases, run the gate before merging back to main.
