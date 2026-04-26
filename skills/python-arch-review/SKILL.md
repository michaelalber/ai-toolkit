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

Python's expressiveness without discipline produces codebases that rot. This skill enforces a TDD-first workflow where every change begins with a failing test and ends with a clean quality gate. The cycle is non-negotiable: Red, Green, Refactor, Quality Check. Every iteration. No exceptions for production code.

YAGNI is the governing constraint. The simplest code that passes the tests is the right code. Abstractions are earned through repetition (Rule of Three) — when three concrete implementations share a pattern, then extract. Until that point, duplication is cheaper than the wrong abstraction.

Quality gates are automated enforcement of standards that humans forget under deadline pressure. Ruff catches style drift. mypy catches type errors tests miss. Bandit catches security mistakes code review overlooks. Radon catches complexity creep before it becomes unmaintainable.

**What this skill IS:** A disciplined TDD process for writing, testing, and reviewing Python code. Automated quality gates enforcing measurable standards. A framework for applying YAGNI and clean architecture to real Python projects.

**What this skill is NOT:** A high-level architecture critique (use `architecture-review`). Optional for production code. Language-agnostic — every rule is specific to Python 3.10+.

## Domain Principles Table

| # | Principle | Description | Applied As |
|---|-----------|-------------|------------|
| 1 | **TDD Discipline** | Every code change begins with a failing test. The test defines the requirement; the code satisfies it. Reversing this order produces code that tests confirm rather than tests that drive design. | Before any implementation, write a failing test. Confirm it fails. Only then implement. |
| 2 | **YAGNI as Default** | Do not build what you do not need. Rule of Three governs when abstraction is justified: when three concrete cases share a pattern, extract. Not before. | Challenge every abstraction: "Do I have three concrete uses for this? If not, inline it." |
| 3 | **Type Safety as Documentation** | Type hints are executable documentation that mypy verifies on every commit. A complete signature tells the reader what it accepts, returns, and what can be None — without reading the body. | All public functions must have complete type annotations. No `# type: ignore` without an explanatory comment. |
| 4 | **Clean Architecture Boundaries** | Dependencies flow inward. Domain logic does not import infrastructure. Use `typing.Protocol` for boundaries. No circular imports. | Enforce: domain has zero imports from infrastructure. |
| 5 | **Dependency Management** | Every dependency is a liability — security vulnerabilities, breaking changes, license conflicts. Pin versions. Audit with `pip-audit`. Prefer the standard library. | Run `pip-audit` in the quality gate. Question every new dependency: "Does stdlib solve this?" |
| 6 | **Testing Quality over Quantity** | 100% coverage with meaningless assertions is worse than 80% with behavioral tests. AAA. One assertion per test. Descriptive names. Cover edge cases. | Enforce `test_should_<expected>_when_<condition>` naming. Review tests for meaningful assertions. |
| 7 | **Security as Habit** | Parameterized queries, no dynamic code execution with user input, `subprocess` with `shell=False`, secrets in environment variables, `secrets` module for tokens. | Run bandit in every quality gate. Follow [references/security-checklist.md](references/security-checklist.md). |
| 8 | **Incremental Improvement** | Large refactors fail. Each TDD cycle improves one thing. Each refactor phase cleans one smell. Over dozens of cycles the codebase transforms. | Limit refactor scope to what current tests cover. Add tests before refactoring untested code. |
| 9 | **Documentation Through Tests** | `test_should_raise_value_error_when_amount_is_negative` tells more about a function's contract than any docstring. Tests are documentation that cannot go stale. | Write test names that describe the contract. If you cannot name it clearly, the requirement is not understood. |
| 10 | **Tooling as Enforcement** | Humans forget. Tools do not. Ruff for style, mypy for types, radon for complexity, bandit for security, pytest-cov for coverage. | Run `scripts/quality_check.py <path>` before every commit. No exceptions for production code. |

## Knowledge Base Lookups

| Query | When to Call |
|-------|--------------|
| `search_knowledge("TDD red green refactor cycle")` | During RED phase — confirm test-first discipline and AAA structure |
| `search_knowledge("YAGNI rule of three abstraction")` | During REFACTOR phase — validate when abstraction is justified |
| `search_knowledge("python type hints mypy strict")` | During QUALITY CHECK — verify mypy configuration patterns |
| `search_knowledge("python cyclomatic complexity radon")` | During QUALITY CHECK — confirm complexity threshold enforcement |
| `search_knowledge("OWASP python security bandit")` | During QUALITY CHECK — verify security scanning patterns |
| `search_knowledge("clean architecture dependency direction")` | During architecture boundary reviews |
| `search_knowledge("pytest fixtures mocking boundaries")` | When writing tests — confirm mocking strategy at system boundaries |

Search before writing tests, before refactoring structural patterns, and before configuring quality gates. Cite the source path in session notes.

## Workflow: The TDD Cycle

Every code change follows four phases: **Red → Green → Refactor → Quality Check**. Sequential. No skipping. No reordering.

### Phase 1: RED -- Write a Failing Test

Write a test that describes the behavior you want. Run it. It must fail. The failure confirms the test is actually testing something new.

**Actions:**
1. Identify the next behavior to implement (from requirements, user story, or bug report)
2. Write a single test using Arrange-Act-Assert
3. Name it `test_should_<expected>_when_<condition>`
4. Run the test and confirm it FAILS
5. If it passes without new code, the behavior already exists or the test is wrong

**Completion Criteria:** One failing test exists with a clear expected error, following the naming convention and AAA structure.

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

Write the absolute minimum code to make the failing test pass. Not elegant. Not complete. The minimum. Resist adding behavior no test demands.

**Actions:**
1. Write the simplest code that makes the failing test pass
2. Run ALL tests (not just the new one)
3. If any test fails, fix the implementation — never change tests to match broken code
4. Stop before cleaning up — that is the Refactor phase

**Completion Criteria:** New test passes. All existing tests pass. No code beyond what the tests require.

### Phase 3: REFACTOR -- Clean Up Under Green Tests

The tests are green. Improve structure without changing behavior. Extract methods. Remove duplication. Improve names. If tests stay green, behavior is preserved.

**Actions:**
1. Look for code smells: duplication, long methods, unclear names, deep nesting
2. Apply one refactoring at a time
3. Run tests after EACH refactoring step — undo if tests break, try a smaller step
4. Apply YAGNI: do not add abstractions the tests do not require

**Completion Criteria:** All tests pass. No method over CC 10, no class over 200 lines. Names are self-documenting. No new behavior introduced.

### Phase 4: QUALITY CHECK -- Run the Full Gate

Run the complete quality gate. Not optional. Every cycle ends here.

```bash
scripts/quality_check.py <path>
```

**Gate Thresholds:**

| Gate | Tool | Threshold | Reference |
|------|------|-----------|-----------|
| Lint + Format | Ruff | Zero errors | [references/ruff-config.md](references/ruff-config.md) |
| Type Check | mypy --strict | Zero errors | [references/mypy-config.md](references/mypy-config.md) |
| Cyclomatic Complexity | radon | Methods < 10, Classes < 20 | quality_check.py `--max-complexity` |
| Maintainability Index | radon | 70+ | quality_check.py `--min-maintainability` |
| Test Coverage | pytest-cov | 80% business logic, 95% security-critical | quality_check.py `--min-coverage` |
| Security Scan | bandit | Zero high/medium findings | [references/security-checklist.md](references/security-checklist.md) |

See [references/review-checklist.md](references/review-checklist.md) for the full code review checklist.

**Completion Criteria:** `scripts/quality_check.py <path>` exits 0. No new warnings. Coverage meets threshold. Code is ready to commit.

## State Block

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

**Example:**
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

## Output Templates

```markdown
## Python Architecture Review Session
**Project**: [name] | **Path**: [path] | **Scope**: [new feature / refactor / bug fix / test improvement]

**Quality Status:** Tests [passing/failing/none] | Coverage [N%] | Ruff [clean/errors] | mypy [clean/errors] | Security [clean/findings]

**Starting Phase**: [RED — identifying first behavior to test]

[state block]
```

## AI Discipline Rules

**Always write the test first.** Never generate implementation code without a failing test. If you find yourself writing implementation without a failing test, stop, delete the implementation, and write the test. The test defines what "correct" means before you write the code.

**Never skip the quality check.** Small changes accumulate. One skipped gate leads to another. Type errors slip in, complexity creeps, security issues hide. Run `scripts/quality_check.py` after every TDD cycle — no exceptions for production code. If the gate fails, fix before committing.

**YAGNI governs all abstractions.** One concrete case needs one concrete implementation. When the third concrete case appears, then extract the abstraction. Premature abstraction — a factory when one validator is needed — is more expensive than duplication.

**Keep functions small and focused.** A function should do one thing. If a block within a function needs a comment, that block is its own function with a descriptive name. Cyclomatic complexity above 10 is a gate failure. Extract until every function has a single, clear purpose.

**Prefer composition over inheritance.** Deep inheritance hierarchies are the leading cause of fragile Python code. Use `typing.Protocol` for interface contracts. Reserve inheritance for genuine is-a relationships with shared behavior. Flat composition beats 4-level class hierarchies — each piece is independently testable.

**Type every public interface.** Every public function, method, and class attribute must have complete type annotations. `mypy --strict` enforces this. `Optional` must be explicit — never rely on implicit `None` defaults.

## Anti-Patterns Table

| Anti-Pattern | Why It Fails | What to Do Instead |
|--------------|-------------|-------------------|
| **Testing After Coding** | Tests written after the fact mirror the code's structure and miss cases the developer did not think of. They give false confidence without driving design. | Follow the Red phase strictly. Write the test FIRST. Watch it fail. Then implement. |
| **Ignoring Type Hints** | Type errors are the most common source of production bugs in dynamic languages. Without types, mypy cannot help and callers must read the entire function body to understand its contract. | Run `mypy --strict`. Annotate every public function. See [references/mypy-config.md](references/mypy-config.md). |
| **Massive Test Fixtures** | Tests become coupled to the fixture. When it changes, dozens of unrelated tests break. Setup becomes so complex it needs its own tests. | Factory functions that create minimal objects. Each test builds only what it needs. |
| **Mocking Everything** | Tests that mock everything test the mocking framework, not the code. They pass when the implementation is wrong and break on every refactoring. | Mock at system boundaries (I/O, external services, time). Test business logic with real objects. |
| **God Classes** | 500+ line classes with 20+ methods violate SRP, resist testing in isolation, cause merge conflicts, and resist refactoring because everything depends on them. | Extract cohesive groups of methods into focused classes. Compose them. Each class has one reason to change. |
| **Premature Optimization** | Optimization without measurement is guessing. The bottleneck is almost never where you think. Premature optimization adds complexity, bugs, and maintenance cost for gains that may not matter. | Write clear code first. Profile under realistic load. Optimize the measured bottleneck. Verify it helped. |
| **Bare Except Clauses** | Catching everything hides bugs. `KeyboardInterrupt`, `SystemExit`, and `GeneratorExit` should not be caught. `except Exception` hides `TypeError` and `ValueError` that indicate bugs. | Catch specific exceptions. Log unexpected exceptions with full context. |
| **Ignoring the Quality Gate** | One skipped gate leads to another. Within weeks the codebase has type errors, complexity violations, and security findings expensive to fix in bulk. | Run `scripts/quality_check.py` after every TDD cycle. No exceptions for production code. |
| **Copy-Paste Test Duplication** | Test files grow to thousands of lines. When behavior changes, every copy must be updated. Missed copies produce tests that pass but verify stale behavior. | Use `pytest.mark.parametrize`. Extract shared setup into named helper functions. |
| **Circular Imports** | Indicate tangled responsibilities. Import-time vs. runtime resolution creates subtle bugs. `TYPE_CHECKING` guards hide the problem but do not fix the design. | Extract the shared dependency into a third module. Invert the dependency using `typing.Protocol`. |

## Error Recovery

### Tests Will Not Pass After Green Phase

**Indicators:** A previously passing test now fails; unrelated tests break; confusing error messages.

**Recovery:**
1. Do NOT change failing tests to match the implementation — tests define correctness
2. Run only the failing test in isolation: `pytest path/to/test.py::test_name -v`. If it passes alone, the failure is test interaction (shared state, fixture pollution).
3. Check for side effects: global mutation, class variables, mutable default arguments
4. If the test is genuinely wrong (requirements changed), go back to Red — update test first, confirm it fails, then fix implementation
5. If stuck after 10 minutes, `git stash`, confirm tests pass clean, re-apply, and bisect

### Quality Gates Fail After Refactoring

**Indicators:** `scripts/quality_check.py` exits non-zero; mypy errors after method extraction; complexity increased.

**Recovery:**
1. Most post-refactoring failures are type annotations (mypy) or import ordering (Ruff) — read the output carefully
2. For mypy failures: extracted functions often lose return type annotations
3. For Ruff: `ruff check --fix .` then `ruff format .`
4. For complexity increases: the refactoring went the wrong direction — undo it, try a smaller step
5. Fix all failures before returning to Red — do not carry quality debt forward

### Legacy Code Without Tests

**Indicators:** 0% coverage, no type annotations, 50+ line functions, no documentation.

**Recovery:**
1. Do NOT refactor untested code — you will break it and not know
2. Write characterization tests: call the function with known inputs and assert on actual outputs
3. Add type annotations to signatures only (do not change the body). Run mypy to find type bugs.
4. Once characterization tests cover paths you need to modify, THEN write a failing test for new behavior and proceed with TDD
5. Improve incrementally — each time you touch a module, leave it with more tests than it had

### Security Findings in Existing Code

**Indicators:** Bandit reports high/medium severity; `pip-audit` finds vulnerable dependencies.

**Recovery:**
1. Triage by severity — high-severity findings (SQL injection, command injection, hardcoded secrets) get fixed immediately
2. For each finding, write a test that demonstrates the vulnerability is addressed
3. Fix using bandit output or [references/security-checklist.md](references/security-checklist.md)
4. Re-run `scripts/quality_check.py` — confirm resolution and no new findings
5. For dependency vulnerabilities: update if a patched version exists; otherwise document the risk

## Integration with Other Skills

- **`architecture-review`** — When structural problems appear (circular dependencies, unclear boundaries, module coupling), use architecture-review for Socratic design critique. This skill enforces code-level quality; architecture-review examines design-level quality.
- **`tdd-cycle`** — For language-agnostic TDD coaching or when the TDD process itself needs pedagogical support. This skill adds Python-specific tooling and quality gates on top.
- **`security-review-trainer`** — When bandit findings reveal recurring patterns, use security-review-trainer to build the habit of writing secure code by default.
- **`dependency-mapper`** — When circular imports appear, use dependency-mapper to generate a concrete dependency graph and compare against intended clean architecture boundaries.

## When to Skip Quality Checks

Never skip for production code. Acceptable exceptions: spike/prototype branches (`spike/*`), documentation-only changes, CI/CD config changes. Even in these cases, run the gate before merging back to main.
