# Coaching Reference: Principles, Anti-Patterns, and Facilitation Recovery

Depth for `spec-coach`. SKILL.md carries the six-phase session and the behavioral discipline
rules; this file carries the principle catalog, the knowledge-base lookup map, the anti-pattern
table, a worked state-block example, and the facilitation-recovery playbook for stuck sessions.

## Domain Principles

| # | Principle | Description | Applied As |
|---|-----------|-------------|------------|
| 1 | **Vision Before Details** | The goal statement must be clear before any behavior is defined. | At the start of VISION phase, require: "What does this agent do, for whom, and how will you know it succeeded?" |
| 2 | **PRD Structure Over Prose** | Sections with named headers, tables, and code blocks can be scanned at inference time. Prose requires reading. | Every section must have a named header. Commands in code blocks. Boundaries in a table. |
| 3 | **Exact Commands** | "Run the tests" is not a command. `pytest tests/ -v --cov=src` is. Approximate commands produce guessing. | Every command must be copy-paste executable. Unknown commands are marked `[NEEDS INPUT]`. |
| 4 | **Three-Tier Boundaries** | Always / Ask First / Never. Agents without explicit boundaries fill in gaps with their own judgment. | Every spec MUST include a three-tier boundary table. All three tiers must be populated. |
| 5 | **Modular Over Monolithic** | One agent with a focused spec outperforms one agent with a sprawling spec. | When scope expands beyond one domain, challenge it: "Is this one agent or several?" |
| 6 | **Specificity Over Generality** | "Write clean code" is an aspiration. "Run `ruff check` and fail if errors" is a constraint. | Every qualitative claim must be made quantitative or procedural, and verifiable. |
| 7 | **Measurable Success Criteria** | A spec without measurable success criteria cannot be validated. | For every goal in VISION, require a corresponding criterion a third party can verify. |
| 8 | **The Spec Evolves** | The first version captures intent; subsequent versions capture what you learned. | After any session where the agent's behavior surprised you, update the spec. |
| 9 | **Domain Knowledge Belongs in the Spec** | The most valuable content is what the model does not already know: your conventions, edge cases, domain-specific error conditions. | During STRUCTURE: "What does a skilled human here know that a general-purpose AI would not?" |
| 10 | **Boundaries Protect the System** | The Never tier is the most important — it contains irreversible harms. | Populate Never by asking: "What is the worst thing this agent could do?" Then explicitly forbid it. |

## Knowledge Base Lookups

| Query | When to Call |
|-------|--------------|
| `search_knowledge("github spec kit spec template feature user stories")` | **Mandatory** when github-spec-kit type detected — before generating spec.md |
| `search_knowledge("spec kit plan template research data model contracts")` | **Mandatory** before generating plan.md |
| `search_knowledge("spec kit tasks template user story parallel task format")` | **Mandatory** before generating tasks.md |
| `search_knowledge("github spec kit constitution template principles")` | Before generating constitution.md (only if needed) |
| `search_knowledge("INVEST user story independent valuable testable")` | During STRUCTURE phase — confirm user story quality criteria |

## Anti-Patterns

| Anti-Pattern | Why It Fails | Correct Approach |
|---|---|---|
| **Vague Vision** | Every downstream section inherits the ambiguity; agent cannot prioritize when choices conflict. | Apply the three-test review. Refuse to move to STRUCTURE until vision passes. |
| **Missing Never Tier** | Agent fills in its own judgment for edge cases — exactly when judgment matters most. | Require at least two Never entries before proceeding. |
| **Monolithic Spec** | Each directive dilutes the others; context windows are finite. | One domain per spec. Create new specs when scope expands. |
| **Invented Commands** | Agent runs the wrong command, fails, developer loses trust. | Extract every command from actual project files or mark `[NEEDS INPUT]`. |
| **Aspirational Success Criteria** | Cannot be verified, tested, or used as improvement feedback. | Every criterion must answer: "How would a third party verify this without asking me?" |
| **Criteria Without Examples** | Cannot be tested without interpretation; every ambiguous criterion generates a different implementation. | One concrete example per criterion: specific input, action, expected output. |
| **INVEST Failures** | Unindependent stories create blocking dependencies; untestable stories cannot be verified. | Apply the INVEST check per story during STRUCTURE. |
| **Format Mismatch** | Different platforms require different sections and loading mechanisms; a mismatched spec fails silently. | Confirm target format in ORIENT. For github-spec-kit, always run KB lookup before generating. |
| **No Self-Check Loops** | Agent cannot distinguish "completed" from "completed correctly." | Every spec must define at least one self-check the agent runs on its own output. |
| **Spec as Documentation** | Documentation specs describe past behavior; design specs constrain future behavior. | Write the spec before building. Spec precedes implementation. |

## State Block — Worked Example

```
<spec-coach-state>
phase: guardrails
spec_type: claude-agent
domain: autonomous linting and test runner
target_file: claude/agents/quality-gate-agent.md
vision_statement: "Run linting and tests after every commit, report failures with citations, never modify code without approval"
sections_complete: commands, testing, structure, style, git
stories_invest_checked: n/a
criteria_have_examples: n/a
open_gaps: 2
never_tier_populated: false
success_criteria_defined: false
kb_lookup_complete: n/a
last_action: STRUCTURE phase complete — 2 gaps marked [NEEDS INPUT]
next_action: Elicit three-tier boundary system, starting with Never tier
</spec-coach-state>
```

## Facilitation Recovery

### User Does Not Know What the Agent Should Do
1. Ask a workflow question instead of vision: "Walk me through a typical day in this domain. What takes the most time? What do you wish happened automatically?"
2. From the answer, extract 2–3 specific tasks. Present back: "It sounds like it could focus on [task 1], [task 2], or [task 3]. Which is most valuable?"
3. Once a concrete task is chosen, return to VISION and apply the three-test review.
4. If still vague, suggest running `spec-extractor-agent` on existing code.

### Scope Keeps Expanding
1. Name the pattern: "We've added [N] new domains since we started. The spec is expanding beyond what one agent can do well."
2. Create a backlog of everything mentioned, then apply prioritization: "If you could deploy only one capability tomorrow, which would it be?"
3. Spec the one chosen. Remaining items become candidates for separate specs via `task-decomposition`.

### Commands Are Unknown
1. Mark with detection hint: `[NEEDS INPUT: run ls Makefile package.json bun.lockb yarn.lock]`
2. Point to CI config: "Check `.github/workflows/` for canonical commands."
3. Continue to GUARDRAILS without commands if needed. Return after detection.

### User Resists Populating the Never Tier
1. Reframe as protection: "The Never tier protects from edge cases the model hasn't seen."
2. Ask scenario questions: "Imagine it's 2 AM, the agent is running unattended. What one action would require you to wake someone up?"
3. Probe specific domains: "Should it ever push directly to main? Delete production data? Commit credentials?"
4. Require minimum: `🚫 Never commit secrets or credentials` before allowing progression.
