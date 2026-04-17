# RPI & Spec-Driven Development Overview

The following are some of the ways I'm using AI in my daily software development workflow.

## RPI (Research-Plan-Implement)

A structured workflow that prevents AI-assisted development from going off the rails on complex tasks. Instead of letting an AI agent explore, plan, and code all in one go — which leads to context pollution and scope drift — RPI separates the work into three clean phases:

1. **Research** — understand what exists before planning
2. **Plan** — produce a precise, mechanical implementation contract
3. **Implement** — execute the plan faithfully, no invention required

Each phase runs in its own session with a compact handoff artifact, keeping the AI focused and recoverable.

---

## Spec-Driven Development

A discipline of writing explicit behavioral specifications for AI agents and skills *before* building them — defining vision, boundaries, success criteria, and failure modes upfront. This prevents "it kind of works" from being mistaken for "it's done."

---

## Skills

| Skill | Summary |
|---|---|
| `rpi-research` | Runs parallel codebase exploration via subagents and produces a compact research artifact to eliminate assumptions before planning. |
| `rpi-plan` | Converts a research artifact into a phased, file-precise implementation plan that can be executed mechanically. |
| `rpi-implement` | Executes an approved plan phase-by-phase with per-phase verification and checkpoint management. |
| `rpi-iterate` | Surgically updates an existing plan based on new feedback without discarding prior work. |
| `agent-spec-writer` | Guides interactive specification of a new AI agent or skill from first principles, producing a complete, deployable spec. |

## Agents

| Agent | Summary |
|---|---|
| `rpi-planner` | Orchestrates the research phase by delegating parallel exploration to subagents and writing structured artifacts to `thoughts/shared/`. |
| `rpi-implement` | Executes an approved plan from `thoughts/shared/plans/` by editing source files phase-by-phase with verification. |
| `rpi-file-locator` | Read-only subagent that locates all files relevant to a research topic, grouped by category. |
| `rpi-code-analyzer` | Read-only subagent that analyzes code structure, data flow, and integration points with precise file:line references. |
| `rpi-pattern-finder` | Read-only subagent that identifies conventions, naming standards, and test patterns relevant to a research topic. |
| `spec-extractor-agent` | Analyzes an existing codebase to produce a pre-filled draft agent spec, used before an `agent-spec-writer` session. |
