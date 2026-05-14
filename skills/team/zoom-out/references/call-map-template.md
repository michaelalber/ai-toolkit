# Call Map Template

Fill this in when running zoom-out. Copy into your session scratchpad or NOTES.md.

```markdown
## Call Map: [FunctionName / ModuleName]

**File:** `path/to/file.ext:line`
**Purpose:** [one sentence]

### Callers

| Call site | File:line | Context |
|-----------|-----------|---------|
| [caller function] | `file:N` | [why it calls this] |

### Called by (upstream orchestrators)

| Orchestrator | File:line | Domain concept |
|-------------|-----------|----------------|
| [orchestrator] | `file:N` | [what domain feature it serves] |

### Public API (what this module exposes)

- `FunctionA(args) → return` — [purpose]
- `FunctionB(args) → return` — [purpose]

### Key dependencies

| Dependency | Type | Why needed |
|-----------|------|-----------|
| [import/module] | stdlib / internal / external | [what it provides] |

### Non-obvious constraints

- [constraint 1]
- [constraint 2]
```
