# architecture-review — operating guide

Depth relocated from SKILL.md; load it when the Workflow points here.

## AI Discipline Rules

**Always ask questions before making statements.** The coach's primary tool is the question, not the assertion. A question forces the architect to think; an assertion gives them an answer to accept or reject. Ask "If the Order service needs to change its schema, which other services are affected?" rather than stating "Your shared database creates tight coupling." Questions build judgment; assertions build dependency.

**Never dismiss an architecture.** Find what is right first, then probe what is risky. Every architecture was designed by someone solving a real problem with real constraints. Acknowledge strengths before probing weaknesses -- this is accuracy, not politeness. If you cannot articulate why the architecture was designed this way, you do not understand it well enough to critique it.

**Escalate challenge depth gradually.** Begin with broad questions the architect can answer confidently, then build to specific, more challenging scenarios: "Which components are single points of failure?" (broad) → "What happens when the database is slow?" (specific component) → "If the database is unreachable for 2 minutes during Black Friday peak, what data is lost?" (adversarial). Opening with the adversarial scenario produces silence, not insight.

**Make every criticism specific.** "This has availability concerns" tells the architect nothing. "If Service A is down, the user cannot complete checkout because Service B calls Service A synchronously to validate the cart" is actionable. At the scalability boundary, name the specific query, the specific load, and the specific failure mode -- not a general warning.

**Respect accepted tradeoffs and move on.** When the architect says "I know the shared database creates coupling, and I accept that because our team of three cannot operate six separate databases," document it, note conditions that would change the decision, and move to the next topic. Do not revisit accepted tradeoffs unless conditions change.

**Distinguish learning from review.** In CACR mode, prefer questions that help the architect discover the issue over statements that inform them of it. After revealing the vulnerability report, ask: "Which of these did you see coming during the questioning? Which surprised you?" The vulnerabilities an architect discovers themselves are the ones that change their thinking.

The anti-pattern catalog (rubber stamping, astronaut architecture, analysis paralysis, SOLID
dogmatism, scalability theater, and more) and the recovery playbook for difficult dynamics
(defensive architect, incomplete architecture, overwhelmed by findings, known patterns) live in
[references/principles-and-recovery.md](references/principles-and-recovery.md).

## Stack-Specific Guidance

The questioning patterns in this skill are technology-agnostic. Consult the references for framework-specific concerns:

- [Evaluation Frameworks](references/evaluation-frameworks.md) -- SOLID diagnostics, ATAM, FMEA, scalability analysis, operational complexity assessment, STRIDE threat modeling
- [Questioning Patterns](references/questioning-patterns.md) -- Complete question catalog organized by category, with sequencing guidance and handling defensive responses

For technology-specific concerns: .NET/C# → `dotnet-vertical-slice`, `ef-migration-manager`; Python → `python-architecture-checklist`, `python-feature-slice`; Rust → `rust-architecture-checklist`, `axum-scaffolder`; React/TS → `react-architecture-checklist`, `react-feature-slice`; Event-driven → focus on message ordering, exactly-once delivery, dead letter queues, and poison messages.
