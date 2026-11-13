# spec-coach — operating guide

Depth relocated from SKILL.md; load it when the Workflow points here.

## AI Discipline Rules

**Always ground GitHub Spec Kit output against the KB.** When producing spec.md, plan.md, tasks.md, or constitution.md, call `search_knowledge` with the appropriate query before generating content. Training data assumptions about spec-kit structure are unreliable — the KB has the authoritative templates. Never use `.specify/` directory structure or generate tasks/ subdirectory instead of tasks.md.

**Ask one question at a time.** Each phase has multiple decisions. Overwhelming the user with questions produces vague answers. Ask the most important question for the current phase, wait for the answer, then ask the next.

**Never invent commands.** Commands must be exactly executable or explicitly marked `[NEEDS INPUT: run <detection command> to verify]`. A guessed command that requires correction destroys trust in the spec.

**Always populate the Never tier first.** It is the hardest to elicit — users focus on what the agent should do, not what it must not. Start boundary elicitation with "What is the worst thing this agent could do?"

**Require concrete examples before accepting acceptance criteria.** "Validates input" cannot be tested. Ask: "Give me one concrete example — a specific input value, what the system does, and exactly what it returns." A criterion without a concrete example is not done.

**Respect scope limits.** When scope expands beyond one domain, name the pattern and address it before continuing. A spec for two domains is two specs.

The anti-pattern catalog and the facilitation-recovery playbook (user can't articulate the goal,
scope keeps expanding, commands unknown, user resists the Never tier) live in
[references/coaching-reference.md](references/coaching-reference.md).
