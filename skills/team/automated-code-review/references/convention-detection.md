# Convention Detection

This reference defines the procedures for detecting project conventions before executing style and convention-dependent review checks. Convention detection ensures that automated review findings are calibrated to the project's actual standards, not to abstract ideals or the agent's training data defaults.


## Why Convention Detection Is Required

A finding that says "use snake_case for function names" is correct in a Python project that follows PEP 8 and wrong in a Python project that uses camelCase (they exist). A finding that says "add type hints" is correct in a project that uses them and noise in a project that deliberately omits them for Python 2 compatibility.

Convention detection prevents the automated reviewer from imposing external standards on a project that has its own, internally consistent conventions. The project's conventions are the standard. The only exception: security-relevant conventions (e.g., "this project uses string concatenation for SQL queries as a convention") are flagged regardless, because a consistently applied insecure pattern is still insecure.


## Detection Sources (Priority Order)

The agent should check these sources in order. Earlier sources override later ones when they conflict.

### 1. Explicit Configuration Files

These files represent deliberate, documented convention choices.

| Ecosystem | Configuration Files |
|-----------|-------------------|
| JavaScript/TypeScript | `.eslintrc`, `.eslintrc.js`, `.eslintrc.json`, `.prettierrc`, `.prettierrc.js`, `biome.json`, `deno.json` |
| Python | `.pylintrc`, `pyproject.toml` (`[tool.ruff]`, `[tool.black]`, `[tool.pylint]`), `setup.cfg`, `.flake8`, `.isort.cfg`, `ruff.toml` |
| Ruby | `.rubocop.yml`, `.rubocop_todo.yml` |
| Go | `.golangci.yml`, `.golangci.yaml` |
| Rust | `rustfmt.toml`, `.rustfmt.toml`, `clippy.toml` |
| Java/Kotlin | `checkstyle.xml`, `.editorconfig`, `ktlint` config, `spotless` config in build files |
| C#/.NET | `.editorconfig`, `.globalconfig`, `Directory.Build.props` with `<AnalysisLevel>` |
| General | `.editorconfig` (cross-language formatting) |

**Detection procedure**:
```
1. Glob for known config file patterns in the project root
2. Read each config file found
3. Extract relevant settings:
   - Indentation (tabs vs spaces, indent size)
   - Line length limit
   - Quote style (single vs double)
   - Trailing comma policy
   - Naming conventions (if configured)
   - Import ordering rules
4. Record as "explicit conventions" -- highest confidence
```

### 2. CI Pipeline Configuration

CI pipelines that enforce style represent conventions that are actively maintained.

| CI System | Files to Check |
|-----------|---------------|
| GitHub Actions | `.github/workflows/*.yml` -- look for lint/format steps |
| GitLab CI | `.gitlab-ci.yml` -- look for lint stages |
| Jenkins | `Jenkinsfile` -- look for quality gate steps |
| General | `Makefile`, `package.json` scripts, `Taskfile.yml` -- look for lint/format targets |

**Detection procedure**:
```
1. Check for CI configuration files
2. Identify linting and formatting steps
3. Note which tools are run and with what flags
4. Cross-reference with tool configuration files found in step 1
5. Record as "enforced conventions" -- high confidence
```

### 3. Code Sampling

When configuration files are absent or incomplete, sample existing code to infer conventions.

**Sampling strategy**:
```
1. Select 3-5 files in the same module/directory as the code under review
2. Prefer recently modified files (they reflect current conventions)
3. Exclude auto-generated files, vendor directories, and test fixtures
4. For each sampled file, observe:
   a. Naming: camelCase vs snake_case vs PascalCase (functions, variables, classes)
   b. Indentation: tabs vs spaces, indent size
   c. Braces/blocks: same-line vs next-line opening brace
   d. String quotes: single vs double
   e. Import organization: grouped by type? alphabetized? relative vs absolute?
   f. Error handling: try/catch, Result types, error codes, pattern
   g. Logging: structured vs unstructured, log levels used, logger patterns
   h. Comments: docstring style, inline comment frequency, TODO formats
   i. Testing: test file location, naming convention, assertion style
5. If 4 of 5 files agree on a convention, record it as "inferred"
6. If files disagree, record as "inconsistent" -- do not pick a side
```

### 4. Framework Defaults

When explicit configuration is absent, frameworks imply conventions.

| Framework | Implied Conventions |
|-----------|-------------------|
| Rails | snake_case, 2-space indent, RESTful naming, ActiveRecord patterns |
| Django | snake_case, 4-space indent, PEP 8, Django model conventions |
| Spring Boot | camelCase, Java conventions, annotation-based configuration |
| Express.js | camelCase, 2-space indent (usually), middleware chaining patterns |
| ASP.NET | PascalCase for public, camelCase for private, async/await patterns |
| React | PascalCase components, camelCase props, JSX conventions |
| FastAPI | snake_case, type hints required, Pydantic model patterns |
| Go standard library | gofmt formatting, exported names PascalCase, unexported camelCase |
| Rust standard library | snake_case, rustfmt formatting, Result-based error handling |

**Detection procedure**:
```
1. Identify the framework from package manifests and import statements
2. Record framework defaults as "framework conventions" -- medium confidence
3. Framework conventions are overridden by explicit config or consistent code sampling
```


## Convention Categories

### Naming Conventions

**What to detect**:
- Function/method naming: camelCase, snake_case, PascalCase
- Variable naming: same as above, or project-specific patterns
- Class/type naming: PascalCase (nearly universal), but check for exceptions
- Constant naming: SCREAMING_SNAKE_CASE, PascalCase, or project-specific
- File naming: kebab-case, snake_case, PascalCase, camelCase
- Test naming: `test_*`, `*_test`, `*Test`, `*Spec`, `should_*`, `it_*`

**Recording format**:
```
naming:
  functions: snake_case (inferred from 5/5 sampled files)
  variables: snake_case (inferred from 5/5 sampled files)
  classes: PascalCase (inferred from 3/3 class definitions)
  constants: SCREAMING_SNAKE_CASE (inferred from 4/5 files)
  files: kebab-case (inferred from directory listing)
  tests: test_* prefix (inferred from test directory)
```

### Error Handling Patterns

**What to detect**:
- Primary error mechanism: exceptions, Result/Either types, error codes, sentinel values
- Exception granularity: custom exception hierarchy vs built-in exceptions
- Error propagation: rethrow with context, wrap and rethrow, log and rethrow, swallow
- Error response format: structured error objects, string messages, HTTP status only
- Retry patterns: present or absent, what is retried

**Recording format**:
```
error_handling:
  mechanism: exceptions (inferred from code sampling)
  granularity: custom exception hierarchy (AppError -> ValidationError, NotFoundError)
  propagation: wrap and rethrow with context
  response_format: structured JSON { "error": { "code": "...", "message": "..." } }
  retry: present for HTTP client calls, absent for database
```

### Logging Patterns

**What to detect**:
- Logger type: structured (JSON) vs unstructured (string)
- Log levels used: which levels appear in practice (DEBUG/INFO/WARN/ERROR)
- Logger initialization: per-file, per-class, singleton, injected
- Context inclusion: request IDs, user IDs, trace IDs in log lines
- Sensitive data handling: are PII or secrets ever logged?

**Recording format**:
```
logging:
  type: structured JSON
  levels_used: INFO, WARN, ERROR (DEBUG absent in production code)
  initialization: per-module (logger = logging.getLogger(__name__))
  context: request_id included via middleware
  sensitive_data: no PII observed in sampled log statements
```

### Testing Patterns

**What to detect**:
- Test location: co-located (`*.test.js`), separate directory (`tests/`), both
- Test naming: `test_function_name`, `should_do_thing`, `it('does thing')`
- Assertion style: built-in assert, fluent assertions, BDD-style expect
- Test structure: arrange-act-assert, given-when-then, setup/teardown
- Mocking approach: dependency injection, monkey-patching, mock library
- Coverage expectations: coverage config present, minimum thresholds

**Recording format**:
```
testing:
  location: separate tests/ directory, mirroring src/ structure
  naming: test_<function_name>_<scenario>
  assertions: pytest assert with descriptive messages
  structure: arrange-act-assert
  mocking: pytest-mock (mocker fixture)
  coverage: pytest-cov configured, 80% minimum in CI
```


## Conflict Resolution

When detection sources disagree:

```
Priority:
1. Explicit configuration files (highest -- these are deliberate choices)
2. CI-enforced standards (actively maintained and checked)
3. Code sampling majority (what the team actually does)
4. Framework defaults (what the framework expects)

When two sources of equal priority disagree:
- Record the conflict: "naming: camelCase (eslintrc) vs snake_case (3/5 files)"
- Do NOT report style findings in the conflicted area
- Note the inconsistency as a maintainability observation:
  "The project has inconsistent naming conventions. ESLint is configured
   for camelCase but 3 of 5 sampled files use snake_case. Consider
   aligning the configuration with the actual codebase or vice versa."
```


## Convention Report Format

After detection, produce this summary before beginning the ANALYZE phase:

```markdown
### Convention Detection Report

**Detection sources used**: [config files, CI, code sampling, framework defaults]
**Confidence level**: [high (explicit config) | medium (inferred) | low (framework defaults only)]

| Convention Area | Detected Value | Source | Confidence |
|----------------|---------------|--------|------------|
| Naming (functions) | snake_case | .pylintrc + code sampling | High |
| Naming (classes) | PascalCase | code sampling (5/5) | High |
| Indentation | 4 spaces | .editorconfig | High |
| Line length | 120 chars | pyproject.toml [tool.ruff] | High |
| Quote style | double | code sampling (4/5) | Medium |
| Import ordering | stdlib, third-party, local | .isort.cfg | High |
| Error handling | custom exceptions, wrap-and-rethrow | code sampling | Medium |
| Logging | structured JSON, per-module logger | code sampling | Medium |
| Testing | pytest, tests/ directory, test_ prefix | pytest.ini + code sampling | High |

**Conflicts detected**: [none, or description of conflicts]
**Areas with insufficient data**: [conventions that could not be determined]
```

This report becomes the reference standard for all style and convention-related findings in the review. Every style finding MUST reference a convention from this report.


## When Conventions Cannot Be Detected

If the project has no configuration files, no CI, and fewer than 3 files to sample:

```
1. Record: "Conventions not determinable -- insufficient project context"
2. Fall back to language-standard conventions:
   - Python: PEP 8
   - JavaScript: no assumption (too much variation)
   - Go: gofmt (effectively universal)
   - Rust: rustfmt (effectively universal)
   - Java: Google Java Style or project-specific (check for config)
   - Ruby: Ruby Style Guide (community standard)
3. Mark ALL style findings as "low confidence -- project conventions not detected"
4. Do NOT mark style findings as anything above "nit" severity
   when conventions are not detected
```

This prevents the automated reviewer from confidently asserting style violations when it does not actually know the project's standards.
