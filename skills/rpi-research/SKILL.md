---
name: rpi-research
description: >
  RPI Research phase -- parallel codebase exploration using subagents to produce a compact,
  objective research artifact. Use for "/rpi-research topic", "research the codebase for X",
  "understand how X works before planning", "document what exists for topic".
---

# RPI Research

> "The most expensive part of a project is fixing code that was built on wrong assumptions."
> -- Adapted from Gerald Weinberg

> "Don't start coding until you know what you're building. Don't start planning until you know what exists."

## Core Philosophy

The Research phase exists to eliminate assumptions before planning begins. Context pollution is the primary reason AI-assisted implementations fail on complex tasks -- by the time an agent has explored 30 files, traced dependencies, and run a few failed builds, its context window is 80% noise.

RPI fixes this with **Frequent Intentional Compaction**: the research phase runs in a dedicated session, produces a single compact markdown artifact (~200 lines), and hands that artifact to the plan phase in a fresh context. The research artifact is the only thing the planner reads -- everything else is discarded.

**Non-Negotiable Constraints:**
1. Research is OBJECTIVE -- no opinions, critique, or suggestions anywhere in the artifact
2. Research is PARALLEL -- three subagents run concurrently to minimize context pollution
3. Research is COMPACT -- the artifact must fit in ~200 lines; more detail means less signal
4. Research is CITED -- every claim must reference a file path, ideally file:line
5. Research produces OPEN QUESTIONS -- human judgment items are surfaced, not decided
6. Research is SESSION-ISOLATED -- never research and plan in the same context window

## When NOT to Use RPI

RPI has overhead: three phases, three sessions, two human review gates. That overhead is worth it when a wrong assumption in planning would cost more than 30 minutes of rework. For these scenarios, skip RPI and work directly:

| Scenario | Why to Skip RPI |
|----------|----------------|
| **Greenfield project** | No existing codebase to research |
| **Single-file change** with clear requirements | Research scope is trivial |
| **Bug fix** with a clear reproduction path | The failing test *is* the research |
| **Formatting, linting, or mechanical refactor** | No design decisions; purely mechanical |
| **You already fully understand the area** | Research would confirm what you know |

**Rule of thumb:** If you can describe exactly which files change and how before starting, skip RPI. If you're guessing, use RPI.

## Domain Principles Table

| # | Principle | Description | Applied As |
|---|-----------|-------------|------------|
| 1 | **Parallel Reduces Pollution** | Running file-locator, code-analyzer, and pattern-finder serially fills context with exploration noise. Parallel execution means each subagent gets a clean context and the planner only sees synthesized results. | Always spawn all three subagents using the Task tool concurrently, never serially. |
| 2 | **Objective Documentation Only** | The moment a research artifact contains an opinion ("this design is problematic"), the plan phase will be biased by that framing. Research describes reality; the plan evaluates it. | Flag opinions with a mental check: "Is this a fact about what exists, or a judgment about what should exist?" If judgment, remove it. |
| 3 | **Compaction Is the Protocol** | A 600-line research artifact is worse than a 200-line one. Length is noise. The artifact should contain only what the plan phase needs: file paths, type signatures, flow traces, patterns, open questions. | Before writing, ask: "Can this be cut in half without losing information the planner needs?" |
| 4 | **Cite or Cut** | An undocumented claim in a research artifact becomes an assumption in a plan, which becomes a bug in an implementation. If you cannot cite the file, do not include the claim. | Every factual statement in the artifact must trace to a specific file path. |
| 5 | **Open Questions Protect Quality** | The leverage model: 1 wrong assumption in research → 10 wrong lines in plan → 100 wrong lines of code. Surfacing open questions for human review prevents this cascade. | Add every unverified assumption and human-judgment item to the open questions section before finalizing. |
| 6 | **Session Isolation Is Non-Negotiable** | Researching and planning in the same session defeats the purpose. The context window accumulates exploration noise and the compaction benefit is lost. | Each phase runs in a separate opencode/claude session. The artifact handoff is the isolation mechanism. |
| 7 | **Commit the Artifacts** | Research artifacts are technical documentation -- valuable for PR reviews, future feature work, and debugging. They should be committed to git alongside the code changes they enabled. | Write artifacts to `thoughts/shared/research/` and commit them with the implementation PR. |
| 8 | **Breadth Before Depth** | Find all relevant files first, then analyze the most important ones deeply. Starting deep risks missing 30% of the surface area. | File-locator runs first (or in parallel), code-analyzer reads the located files. |
| 9 | **Pattern Discovery Is First-Class** | Conventions constrain the plan. A plan that violates the existing naming, DI, or error handling patterns produces code that fails review. The pattern-finder's output is as important as the code-analyzer's. | Always spawn pattern-finder alongside the other subagents, not as an afterthought. |
| 10 | **Wrong Research Cascades** | The cost of a wrong assumption compounds: research error → plan error → implementation error → PR feedback → rework. The review investment at research/plan is 10-100x more valuable than review at code review. | Treat the human review step (between research and plan) as mandatory, not optional. |

## Workflow

```
PRE-RESEARCH CHECKLIST (before starting)
    [ ] Is this brownfield? (If greenfield, skip RPI entirely)
    [ ] Does a prior research artifact exist for this topic? Check thoughts/shared/research/
    [ ] What is the current git state? Run: git status && git log --oneline -3
    [ ] Record the current commit hash — add to artifact frontmatter as git_commit

SCOPE
    Parse the research topic from the command argument
    Identify the codebase root and project structure
    Determine if prior research artifacts exist (check thoughts/shared/research/)

        |
        v

DELEGATE (parallel)
    Spawn concurrently using Task tool:
    ├── @rpi-file-locator — "Find all files related to: {topic}"
    ├── @rpi-code-analyzer — "Analyze the implementation of: {topic}"
    └── @rpi-pattern-finder — "Find patterns and conventions related to: {topic}"
    Wait for ALL THREE before proceeding.

        |
        v

SYNTHESIZE
    Combine subagent outputs:
    - De-duplicate overlapping file references
    - Organize into: overview, detailed findings, code references, patterns, open questions
    - Apply the compaction check: aim for ≤ 200 lines
    - Convert any opinions or suggestions into open questions

        |
        v

WRITE
    Write to: thoughts/shared/research/YYYY-MM-DD-topic-slug.md
    Use the research artifact template (see references/research-artifact-template.md)
    Set status: complete in frontmatter

        |
        v

REPORT
    Tell the user:
    - Artifact path
    - 3-5 key findings (bullets)
    - Open questions needing human input
    - Reminder: "Review before proceeding to /rpi-plan"
```

**When Research is Done** — all five must be true:
1. Artifact written to `thoughts/shared/research/YYYY-MM-DD-topic-slug.md`
2. All three subagent outputs are incorporated
3. Every claim in the artifact cites a file path
4. Open questions section is present (even if empty — note "none identified")
5. User has been explicitly told to review before proceeding to /rpi-plan

**Exit criteria:** Research artifact written, open questions surfaced, user has been prompted to review.

## State Block

```
<rpi-research-state>
phase: SCOPE | DELEGATE | SYNTHESIZE | WRITE | REPORT | COMPLETE
topic: [research topic]
artifact_path: thoughts/shared/research/YYYY-MM-DD-topic-slug.md
subagents_spawned: 0 | 1 | 2 | 3
subagents_complete: 0 | 1 | 2 | 3
open_questions: [count]
artifact_lines: [estimated line count]
status: in_progress | complete
</rpi-research-state>
```

## Output Templates

### Research Artifact

See `references/research-artifact-template.md` for the complete template.

**Summary structure:**
```markdown
---
date: YYYY-MM-DDTHH:MM:SS
repository: [repo name]
topic: "[research topic]"
tags: [research, relevant-tag-1, relevant-tag-2]
status: complete
---

# Research: [Topic]

## Research question
[What we investigated, 1-2 sentences]

## Summary
[2-3 paragraph overview — the only section the planner MUST read]

## Detailed findings
### 1. [Component/area name]
[File paths with line references, type signatures, flow descriptions]

### 2. [Next component/area]
...

## Code references
### Core implementation
- `path/to/file` — description
### Integration points
- `path/to/file` — description
### Tests
- `path/to/test` — description

## Key design patterns
1. [Pattern and where it appears]
2. [Pattern and where it appears]

## Open questions
1. [Human-judgment item — do not proceed to plan until resolved]
2. [Unverified assumption]
```

### Report to User

```
Research complete. Artifact: thoughts/shared/research/YYYY-MM-DD-topic-slug.md

Key findings:
- [finding 1]
- [finding 2]
- [finding 3]

Open questions (review before planning):
1. [question requiring human judgment]

Next step: Review the artifact, then start a NEW session and run /rpi-plan "[feature description]"
```

## AI Discipline Rules

### CRITICAL: No Opinions in Research Artifacts

**WRONG:**
```
## Detailed findings
### Authentication
The auth middleware is poorly designed -- it mixes concerns and should be refactored.
The token validation logic is duplicated across three files.
```

**RIGHT:**
```
## Detailed findings
### Authentication
The auth middleware is in `Middleware/AuthMiddleware.cs:1-156`.
Token validation logic appears in:
- `Middleware/AuthMiddleware.cs:44`
- `Services/TokenService.cs:28`
- `Infrastructure/Auth/JwtValidator.cs:15`

## Open questions
1. The token validation logic appears in three locations -- is this intentional? Should the plan consolidate?
```

### REQUIRED: Cite Every Claim

**WRONG:**
```
The system uses CQRS with MediatR.
```

**RIGHT:**
```
The system uses CQRS with MediatR (`Features/*/Commands/*Command.cs`,
`Features/*/Queries/*Query.cs`). MediatR registered in
`Infrastructure/Extensions/ServiceCollectionExtensions.cs:23`.
```

### CRITICAL: Session Isolation

**WRONG:** Research the topic and then immediately start writing the plan in the same session.

**RIGHT:** Write the research artifact, report to the user with open questions, then STOP. The plan happens in a new session.

## Anti-Patterns Table

| # | Anti-Pattern | Why It Fails | Correct Approach |
|---|-------------|-------------|-----------------|
| 1 | **Research + Plan in one session** | Context accumulates exploration noise; the compaction benefit is lost | Strict session isolation: research artifact, then new session for plan |
| 2 | **Opinions in research** | Biases the plan toward a predetermined conclusion; prevents accurate analysis | Document what exists; put all judgments in open questions |
| 3 | **Serial subagents** | Triples the context window used; defeats parallel architecture purpose | Spawn all three with Task tool concurrently |
| 4 | **No file:line citations** | Claims become assumptions in the plan, which become bugs in implementation | Every factual claim cites exact file path, ideally with line number |
| 5 | **300+ line artifacts** | Planners can't prioritize signal from noise; defeats compaction purpose | Summarize aggressively; aim for ≤ 200 lines |
| 6 | **Skipping open questions** | Human-judgment items silently become plan assumptions; cascade into bad code | Surface every unverified assumption; make human review mandatory |
| 7 | **Skipping pattern-finder** | Plan violates existing conventions; code fails review or causes subtle bugs | Always run pattern-finder in parallel with file-locator and code-analyzer |
| 8 | **Fabricating file paths** | Planner cites nonexistent files; implementation phase wastes time searching | If you cannot verify it, mark it as UNKNOWN and add to open questions |
| 9 | **Not committing artifacts** | Valuable technical documentation is lost; future sessions have no context | Commit research and plan artifacts with the implementation PR |
| 10 | **Skipping human review** | The leverage model fails; assumptions cascade from research to code at 100x cost | Make human review of research artifact a hard gate before /rpi-plan |

## Error Recovery

### Subagent returns empty results

```
Symptoms:
- rpi-file-locator returns "no files found"
- rpi-code-analyzer returns "no implementation located"

Recovery:
1. Widen the topic -- try parent concept, domain synonyms, common abbreviations
2. Re-spawn the subagent with the broader topic
3. Check if the feature might be called something different in this codebase
   (grep for domain vocabulary, not just the topic name)
4. If still empty after retry, mark the area as UNRESEARCHED in the artifact
5. Add to open questions: "Could not locate [area] -- may not exist or use different naming"
6. NEVER fabricate findings to fill the gap
```

### Context window fills during synthesis

```
Symptoms:
- Three large subagent outputs; synthesis is approaching context limit
- Not enough space to write the full artifact

Recovery:
1. Prioritize: summary and open questions are mandatory; detailed findings can be abbreviated
2. Write the artifact immediately with what you have
3. Mark any incomplete sections: "## INCOMPLETE -- context limit; re-research this area"
4. Tell user to start a new research session for the incomplete areas
```

### Prior research artifact exists but may be stale

```
Symptoms:
- thoughts/shared/research/ contains a prior artifact for this topic
- Significant time has passed or the topic's code may have changed

Recovery:
1. Read the prior artifact; compare key file paths against the current codebase
2. If major files have moved or been deleted, the artifact is stale -- conduct fresh research
3. If minor changes only, note the prior artifact and supplement with targeted re-research
4. Update the artifact's date and add a "## Updates" section
```

## Integration with Other Skills

| Skill | Relationship |
|-------|-------------|
| `rpi-plan` | Consumes the research artifact. Run after research review is complete. |
| `rpi-implement` | Executes the plan. Never runs in the same session as research. |
| `rpi-iterate` | Updates the plan if feedback requires targeted re-research of specific areas. |
| `research-synthesis` | For deeper research methodology: source credibility scoring, cross-reference matrices, structured briefings with citations. Use when research scope extends beyond the codebase (external systems, third-party libraries). |
| `session-context` | Provides git history analysis and ADR matching to seed research with change context. Useful as a pre-step before research to understand what has changed recently in the topic area. |
| `task-decomposition` | When the research topic is a large system, use task-decomposition first to break it into researachable sub-components, then run rpi-research on each. |

## .NET/Blazor Adapter Notes

When researching a .NET/Blazor codebase, extend the standard subagent prompts with these checks:

**DI Registration** — always locate the service registration surface:
- Where are services registered? (`Program.cs`, `ServiceCollectionExtensions.cs`, feature `Module.cs`)
- Is the topic's service registered as singleton, scoped, or transient? (impacts Blazor component lifecycle)

**EF Core** — identify the data access boundary:
- Is there an `IEntityTypeConfiguration<T>` for affected entities? (`Infrastructure/Persistence/Configurations/`)
- Are there pending migrations? (`dotnet ef migrations list`)
- Does the research area involve owned types, value objects, or complex mapping?

**Blazor Component Hierarchy** — for UI research:
- Is the affected component a page (`@page`), layout, or reusable component?
- Does it use `@inject`, `[Parameter]`, `[CascadingParameter]`, or `EventCallback`?
- Is it server-side (SignalR) or WebAssembly? (affects async patterns and JS interop)

**Telerik UI** — when Telerik components are present:
- Identify which Telerik component is affected (`TelerikGrid`, `TelerikForm`, `TelerikWindow`, etc.)
- Note the Telerik version from the project file — API changes between versions are common
- Is there a custom Telerik theme or CSS override file?

**FreeMediator Pipeline** — for CQRS research:
- Locate pipeline behaviors (`IPipelineBehavior<,>`) — these affect all commands/queries
- Are there validation behaviors (FluentValidation integration)?
- Note: FreeMediator, not MediatR — the registration and pipeline API differs

Always add these findings to the `## Key design patterns` section of the research artifact.

## Python Adapter Notes

When researching a Python codebase, extend the standard subagent prompts with these checks:

**Dependency Injection** — locate the wiring surface:
- FastAPI: Where are `Depends()` callables defined? Are they in a `dependencies.py` module,
  inline in route files, or composed via `lifespan` context managers?
- Is any shared state (DB session, HTTP client, cache) passed via a shared `Annotated` dependency
  or managed with `contextlib.asynccontextmanager`?
- > **Flask callout:** Is an application factory (`create_app()`) in use? Identify which extensions
  > are initialized there (`db.init_app(app)`, `login_manager.init_app(app)`).

**SQLAlchemy / Database boundary** — identify the data access surface:
- What is the `Base` metadata target? (`declarative_base()` or `DeclarativeBase` subclass in SQLAlchemy 2.x)
- Is `Session` or `AsyncSession` in use? (async requires `AsyncEngine` and `async_sessionmaker`)
- Is the topic area using ORM-level queries or Core-level `select()` statements?
- *If using Alembic:* Are there pending migrations? (`alembic current` vs. `alembic heads`)
  Are there multiple heads that need merging?

**API surface** — for FastAPI/Flask route research:
- Which `APIRouter` (FastAPI) or `Blueprint` (Flask) owns the affected endpoints?
- Trace the full `Depends()` injection chain for the affected route — all resolved dependencies
  are potential impact areas
- Identify the Pydantic request/response models (`BaseModel` subclasses) — field changes ripple
  into OpenAPI schema, validation, and serialization

**Pydantic Models** — schema and validation boundary:
- Identify all `BaseModel` subclasses in the affected area
- Note any `model_config`, `field_validator`, `model_validator`, or `computed_field` usage —
  these add behavior beyond simple field declarations
- Are models shared between API layer and domain logic, or are there separate schemas?

**Async patterns** — for async codebases:
- Is the codebase fully `async def` end-to-end, or mixed sync/async?
- Look for blocking calls in async paths: `time.sleep()`, synchronous file I/O, or sync
  SQLAlchemy sessions inside `async def` routes — these stall the event loop
- Are background tasks using `asyncio.create_task()`, `BackgroundTasks` (FastAPI), or Celery?

Always add these findings to the `## Key design patterns` section of the research artifact.
