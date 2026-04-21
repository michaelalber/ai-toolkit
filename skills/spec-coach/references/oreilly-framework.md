# O'Reilly Agent Spec Framework — Deep Reference

Source: "How to Write a Good Spec for AI Agents" (O'Reilly Radar)
Analysis of 2,500+ agent configurations.

## The Five Principles

### Principle 1: High-Level Vision First, Then Details

Start with a concise goal statement rather than exhaustive upfront specifications. Let the AI expand it into a detailed plan. Treat spec writing as collaborative product development.

**The insight:** "Plan first in read-only mode, then execute and iterate continuously." This matches the use of Plan Mode in tools like Claude Code — restrict the agent to analysis before generation, allowing you to refine the spec before implementation begins.

**Applied in spec-coach:** The VISION phase enforces a one-sentence goal statement with a three-test review (valuable, sufficient, verifiable) before any PRD sections are written.

**Vision statement tests:**

| Test | Question | Why It Matters |
|---|---|---|
| Specificity | "If the agent did only this, would it be valuable?" | Prevents vague goals that accept any output as success |
| Sufficiency | "If the agent did nothing else, would the goal still be met?" | Prevents under-scoped goals that need unstated dependencies |
| Verifiability | "Can a third party verify whether the agent succeeded?" | Prevents aspirational goals that cannot be tested |

---

### Principle 2: Structure Like a Professional PRD

Organize specs as formal product requirement documents with six essential sections.

**The six PRD sections:**

| Section | What to Include | Example |
|---|---|---|
| **Commands** | Exact executable commands with flags | `pytest tests/ -v --cov=src --cov-report=term-missing` |
| **Testing** | Framework location, coverage expectations, test procedures | `tests/` directory, 80% coverage required, run before every PR |
| **Project Structure** | Clear directory hierarchy | `src/`, `tests/`, `docs/`, `scripts/` |
| **Code Style** | Actual code examples of preferred patterns | Real code snippets, not style rules in prose |
| **Git Workflow** | Branch naming, commit format, PR requirements | `feat/`, `fix/`, conventional commits, PR requires 1 approval |
| **Boundaries** | Three-tier Always/Ask/Never system | See Principle 4 |

**The O'Reilly finding:** "Never commit secrets" was the most consistently helpful constraint across 2,500+ agent configurations. Not because it is clever — because it is **specific, verifiable, and bounded**. Every constraint in your spec should meet the same bar.

**Applied in spec-coach:** The STRUCTURE phase builds all six sections with the Specificity Test: "Can a third party execute this without asking for clarification?"

---

### Principle 3: Modular Prompts Over Monolithic Ones

Avoid the "curse of instructions" — when too many directives pile up, performance on each degrades significantly.

**How to modularize:**

- Divide specs into focused sections (backend/frontend, database/API)
- Create extended table-of-contents summaries for large documents
- Feed only relevant spec portions for each task
- Use subagents or skills for specialized domains
- Refresh context between major work phases

**The curse of instructions:** This is empirically documented. A 5,000-token spec covering 8 domains produces worse per-domain performance than 8 focused 500-token specs. The model cannot maintain equal attention across all constraints simultaneously.

**The modularization heuristic:**

```
ONE AGENT = ONE COHERENT DOMAIN
ONE DOMAIN = ONE COHERENT WORKFLOW
ONE WORKFLOW = ONE CLEAR ENTRY POINT AND EXIT CRITERION
```

**Applied in spec-coach:** The ORIENT phase detects scope creep. The Scope Limits rule halts the session when a single spec attempts to cover multiple unrelated domains.

**When to split a spec:**
- Two different entry points (e.g., triggered by commit vs. triggered by PR creation)
- Two different user types (developer vs. reviewer)
- Two different outputs (code changes vs. reports)
- Two different risk profiles (read-only analysis vs. write operations)

---

### Principle 4: Build Self-Checks and Constraints

Layer in quality control mechanisms at three levels.

**Three-tier boundary system:**

| Tier | Label | When | Examples |
|---|---|---|---|
| ✅ | **Always** | No approval needed — safe, routine, low-risk | Run tests, read files, generate markdown reports |
| ⚠️ | **Ask First** | Require review before proceeding — high impact, irreversible, or externally visible | Push to remote, delete files, send messages, modify shared config |
| 🚫 | **Never** | Hard stops regardless of instructions — security, compliance, or catastrophic risk | Commit secrets, force-push to main, drop production tables, bypass CI |

**LLM-as-Judge pattern:** For subjective quality assessment (code style, documentation quality), include a self-verification step where the agent compares its output against the spec criteria. The spec itself becomes the rubric.

**Conformance tests:** Tie at least one automated test directly to each spec criterion. If the spec says "always run linting before committing," the conformance test verifies that linting ran and passed in the agent's last commit.

**The exec-in-the-loop principle:** "Your role remains as 'the exec in the loop' — the spec empowers but you maintain ultimate oversight." The three-tier system is how you implement this: Always tier automates the routine; Ask First tier preserves your oversight for consequential actions; Never tier is the non-negotiable floor.

**Applied in spec-coach:** The GUARDRAILS phase elicits all three tiers in Never-first order. The VALIDATE phase ties success criteria to conformance tests.

---

### Principle 5: Test, Iterate, and Evolve

Treat spec development as continuous, not one-time.

**The iteration cycle:**

```
1. Write spec (VISION → STRUCTURE → GUARDRAILS → VALIDATE)
2. Deploy agent with spec
3. Observe behavior — what surprised you?
4. Update spec to capture the lesson
5. Resync agent to new spec version
6. Repeat
```

**Context management tools:** For large specs, use RAG or MCP to retrieve spec sections on demand rather than loading the entire spec into context for every task.

**Version control the spec:** The spec is a first-class artifact. Commit it alongside the code it governs. The spec's git history is the history of what you learned about the agent's domain.

**The spec revision trigger:** Any of these events should prompt a spec review:
- Agent behavior that surprised you (success or failure)
- New edge cases discovered in production
- Team size or process changes that affect boundaries
- New capabilities added to the underlying model
- Changes to the codebase's structure or conventions

**Applied in spec-coach:** Principle 8 (The Spec Evolves) encodes this into the skill's domain principles. The GENERATE phase output includes explicit "next steps" for first-use revision.

---

## The Spec as Executable Artifact

The key insight from the O'Reilly analysis: **specs are not documentation — they are executable artifacts.**

Documentation describes what a system does. An executable spec constrains what a system can do.

The difference is consequential:

| Documentation | Executable Spec |
|---|---|
| Written after the fact | Written before implementation |
| Describes past behavior | Constrains future behavior |
| Updated when convenient | Updated when behavior changes |
| Passive — read by humans | Active — consumed by agents at inference time |
| Correct by convention | Correct by verification |

**The emerging pattern:** Spec-driven development. Specifications drive implementation, task breakdowns, and validation — making them the primary design artifact rather than a documentation afterthought.

## Quick Reference: Spec Quality Checklist

```markdown
## Spec Quality Checklist (O'Reilly Framework)

### Principle 1: Vision
- [ ] Goal statement is one sentence
- [ ] Goal is specific (not aspirational)
- [ ] Goal is sufficient (not underscoped)
- [ ] Goal is verifiable by a third party

### Principle 2: PRD Structure
- [ ] All six sections present (commands, testing, structure, style, git, boundaries)
- [ ] Every command is copy-paste executable or marked [NEEDS INPUT]
- [ ] Code style includes actual code examples, not prose rules
- [ ] Project structure matches the actual directory layout

### Principle 3: Modularity
- [ ] Spec covers one coherent domain
- [ ] No two sections require conflicting priorities
- [ ] Spec fits in one context window without summarization

### Principle 4: Self-Checks and Constraints
- [ ] Three-tier boundary table populated in all three tiers
- [ ] "Never" tier has at least two hard stops
- [ ] Self-check loop defined for the agent's primary output
- [ ] At least one conformance test tied to a spec criterion

### Principle 5: Iteration
- [ ] Spec is version-controlled alongside the code
- [ ] Revision triggers are identified (what would prompt an update?)
- [ ] First-use review is scheduled
```
