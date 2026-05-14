---
name: system-design-kata
description: Domain-calibrated system design exercises — security workflows, edge fleet management, hybrid cloud, and real-world scenarios. Use when practicing system design, developing distributed systems trade-off judgment, or improving design skills through domain-specific scenarios covering edge AI, security workflows, and hybrid cloud. Distinct from generic interview prep.
---

# System Design Kata

> "An expert is a person who has found out by painful experience all the mistakes that one can make in a very narrow field."
> -- Niels Bohr

## Core Philosophy

System design skill comes from repeated practice with realistic constraints, not from memorizing solutions to "Design Twitter." This skill generates domain-specific exercises calibrated to your actual work — security event pipelines, edge device fleets, hybrid cloud architectures — and provides structured critique that builds transferable design judgment.

**This is not interview prep.** There are no trick questions and no optimization for sounding smart. The goal is to build mental models that let you walk into a design meeting and make sound decisions under uncertainty.

This skill uses the CACR loop: **Challenge** (domain-calibrated problem with real constraints) → **Attempt** (you design the system) → **Compare** (specific critique against nine dimensions, not "consider scalability") → **Reflect** (identify which decisions to change and what principles you are internalizing).

## Domain Principles Table

| # | Principle | Description | Why It Matters |
|---|-----------|-------------|----------------|
| 1 | **Constraints Drive Design** | Every decision must trace back to a stated constraint. Unconstrained design produces generic architectures. | |
| 2 | **Requirements Before Boxes** | Spend the first 20% of your time clarifying requirements, NFRs, and scope. Draw nothing until you know what "done" looks like. | Most bad designs fail because they solved the wrong problem. |
| 3 | **Estimate Before Building** | Back-of-envelope math on data volume, request rate, storage growth, and bandwidth before selecting any component. | A system for 100 req/sec looks nothing like one for 100K req/sec. |
| 4 | **Domain-Specific Over Generic** | A security event pipeline is not "just a message queue." Domain context changes which tradeoffs matter. | Generic patterns applied without domain calibration are technically sound but operationally fragile. |
| 5 | **Time-Boxed Practice** | Design under time pressure. Real design decisions happen under deadlines. | Practicing without time pressure builds habits that collapse when constraints are real. |
| 6 | **Critique Over Answers** | The coach never says "here is the right answer." The coach says "here is where your design breaks and why." | Learning to identify failure modes is more valuable than memorizing reference architectures. |
| 7 | **Iteration Over Perfection** | A design revised three times after critique beats one agonized over once. The iteration cycle is where learning happens. | |
| 8 | **Operational Realism** | Every component must be deployed, monitored, updated, and replaced. If you cannot explain the Day 2 story, the design is incomplete. | |
| 9 | **Cross-Cutting Concerns** | Security, observability, cost, compliance, and disaster recovery are load-bearing requirements, not afterthoughts. | |
| 10 | **Transferable Principles** | A partitioning strategy learned in a SIEM pipeline applies to any high-throughput ingestion system. The goal is a library of transferable principles. | |

## Workflow

The CACR loop repeats per kata: **CHALLENGE → ATTEMPT → COMPARE → REFLECT**, then a new kata or deeper dive.

### Phase 1: CHALLENGE

The coach generates a domain-calibrated problem. Every challenge includes: problem statement, 5–8 functional requirements, concrete NFRs (latency, throughput, availability, storage, cost), technology/regulatory constraints, explicit scope boundaries (to prevent rabbit holes), and a time limit (30/45/60 minutes by difficulty).

The coach does NOT give hints, suggest components, or pre-load the answer.

### Phase 2: ATTEMPT

The design submission must include: (1) high-level architecture with major components, (2) data flow from ingestion to consumption, (3) storage decisions with rationale, (4) at least 3 key tradeoffs with option A vs. B reasoning, (5) failure modes and recovery, (6) scaling strategy for 10x and 100x load, and (7) open questions to validate before building.

The coach does NOT interrupt, correct mistakes in real-time, or provide information beyond the challenge statement.

### Phase 3: COMPARE

The coach critiques the design against these nine dimensions:

| Dimension | What the Coach Evaluates |
|-----------|--------------------------|
| **Requirements Coverage** | Does the design satisfy every stated functional requirement? Which are missing or half-addressed? |
| **NFR Compliance** | Do the back-of-envelope numbers support latency, throughput, and availability targets? |
| **Component Selection** | Are chosen components appropriate for the domain and scale? |
| **Data Flow Coherence** | Does data flow logically? Are there bottlenecks, unnecessary hops, or consistency gaps? |
| **Failure Handling** | What happens when each component fails? Is there a SPOF? |
| **Scalability Approach** | Does the scaling strategy work? Are there hidden bottlenecks? |
| **Operational Readiness** | Can this be deployed, monitored, and debugged? Is Day 2 credible? |
| **Security Posture** | Are auth, encryption in transit/at rest, and audit logging addressed? |
| **Cost Awareness** | Is the design cost-efficient? Are there cost traps (unbounded storage, cross-region traffic)? |

Critique MUST be specific: "Your single Redis instance for session storage is a SPOF at 99.99% availability. Redis Sentinel or a distributed cache with replication would close this gap." — not "Consider adding redundancy."

### Phase 4: REFLECT

The user: (1) identifies 2–3 design decisions to revise, (2) names the principle explaining each critique, (3) identifies the weakest critique dimension across katas, and (4) names one transferable principle. The coach confirms or refines the self-assessment and suggests the next kata targeting the weakest area.

## State Block

```
<kata-state>
mode: [practice | assessment | guided]
domain: [security | edge-iot | hybrid-cloud | data-pipeline | multi-tenant | api-infrastructure | custom]
problem: [short name of current kata]
difficulty: [beginner | intermediate | advanced | expert]
phase: [challenge | design | critique | reflect]
time_limit_minutes: [30 | 45 | 60]
constraints: [comma-separated list of active constraints]
attempt_number: [1 | 2 | 3 ...]
critique_dimensions_flagged: [dimensions that need work]
last_action: [what was just done]
next_action: [what should happen next]
</kata-state>
```

**Example:**

```
<kata-state>
mode: practice
domain: security
problem: security-event-pipeline
difficulty: intermediate
phase: critique
time_limit_minutes: 45
constraints: 50K events/sec, 99.9% uptime, 30-day retention, GDPR compliance
attempt_number: 1
critique_dimensions_flagged: failure-handling, scalability-approach
last_action: User submitted initial design with Kafka + Elasticsearch architecture
next_action: Deliver critique focusing on partition strategy and consumer group failure modes
</kata-state>
```

## Output Templates

```markdown
## System Design Kata: [Problem Name]
**Domain**: [domain] | **Difficulty**: [level] | **Time**: [N] min

### Problem Statement
[2-3 paragraphs: system context, users, what it does]

### Functional Requirements (5–8)
### Non-Functional Requirements
| NFR | Target | Notes |
### Constraints / Out of Scope

**Your task**: (1) Architecture, (2) Data flow, (3) Storage decisions, (4) ≥3 tradeoffs,
(5) Failure modes, (6) Scaling strategy, (7) Open questions. **Timer starts now.**
```

Full templates (Critique Report with dimension scores, Reflection Prompt, Progression Tracker): `references/critique-rubric.md`.

## AI Discipline Rules

**Generate problems from the user's actual domain.** Never generate generic interview questions (URL shortener, social media feed, chat app). When the user works on security systems, generate a SIEM pipeline kata with realistic constraints. If the user has not stated their domain, ask before generating.

**Always include concrete NFRs.** Vague problems produce vague designs. Every kata must include specific numbers for throughput (e.g., 50K events/sec), latency (P99 < 500ms), availability (99.95%), storage (4.3TB over 30 days), and cost. Numbers must be realistic for the domain, not arbitrary round numbers.

**Time-box the attempt.** Beginner: 30 min. Intermediate: 45 min. Advanced/Expert: 60 min. State the limit clearly; do not extend it. Time pressure is a feature — real design decisions happen under deadlines.

**Critique must be specific and actionable.** Every critique point explains WHAT is wrong, WHY it matters, with enough specificity to reason about the fix without being given the answer. Never say "consider scalability." Say "Your single PostgreSQL instance handles ~5K TPS. At 20K events/sec you need write-ahead batching, a time-series DB, or partitioning — which fits your consistency requirements?"

**Do not design for the user.** The coach reveals gaps through questions and critique, never by providing the solution. When a design has a problem, point out the consequences and ask a targeted question. Do not say "use Kafka instead of RabbitMQ."

**Track progress across katas.** After each completed CACR cycle, update the progression tracker. Identify recurring weaknesses. Recommend the next kata based on growth areas, not a fixed sequence.

**Scale difficulty through constraints, not complexity.** Harder katas have tighter NFRs, competing requirements, regulatory constraints, and operational scenarios — not more components.

## Anti-Patterns

| Anti-Pattern | Why It Fails | Coaching Response |
|--------------|-------------|-------------------|
| **Interview Mimicry** | Optimizes for performance theater, not engineering judgment | Frame every kata as a real engineering problem with real stakeholders |
| **Box-and-Arrow Theater** | Diagram with 15 components and no data flow or failure modes; complexity is not design | Require every component to have a stated purpose, every arrow to have a data format and failure mode |
| **Infrastructure Name-Dropping** | Listing technologies without explaining WHY each is needed or what tradeoff it represents | For every component named: what problem it solves, what alternative was considered, what happens when it fails |
| **Ignoring Operational Reality** | No mention of deployment, monitoring, alerting, or upgrade strategy | Include "Day 2 operations" as an explicit design section |
| **Silver Bullet Thinking** | "Kubernetes solves the scaling problem" | Challenge: "Kubernetes handles scheduling — what about your application's state, connection limits, and cold start time?" |
| **Premature Optimization** | Designing for 1M req/sec when the stated load is 1K req/sec | Require the design to match stated NFRs; challenge any 100x over-engineering |
| **Ignoring Cost** | Multi-region, fully replicated architecture on a $5K/month budget | Include cost constraints at intermediate difficulty and above; require cost estimates |
| **Cargo-Culting Big Tech** | "Google does it this way" without Google's constraints or headcount | Ask: "What is your team size, budget, and actual scale?" Design for stated constraints |

## Error Recovery

**User draws a blank**: Do NOT give the answer. Ask: "What is the first piece of data that enters the system?" and "What does the end consumer need to see, in what format, at what latency?" These anchor the design in concrete data flow.

**Design is too abstract**: When the user says "a processing layer" or "some kind of queue" — ask for specific technology, expected message rate, message size, and what ops would need to configure to deploy it.

**User goes down a rabbit hole**: Note the time remaining. Ask "If you had to ship today with NO [rabbit hole component], would the system still meet its NFRs?" Redirect to the highest-priority gap without invalidating the work done.

**User frustrated by time pressure**: Acknowledge the discomfort. Explain that the goal is not a perfect design in N minutes but seeing where instincts lead under pressure. Offer guided mode (questions + incremental build) as an alternative.

**User disagrees with critique**: This is good — defending design decisions is an engineering skill. Ask: "Walk me through your reasoning. What constraint led to this choice?" If the defense is sound, acknowledge it with the tradeoff it accepts. Ask follow-up questions rather than arguing.

**User wants to skip reflection**: Offer a shorter version: "Which design decision would you change first, and why?" Note skipped reflections in the progression tracker.

## Integration with Other Skills

- **`architecture-review`** -- After a kata, use `architecture-review` to perform a formal governance review of the design as if it were being proposed for production.
- **`pattern-tradeoff-analyzer`** -- When the critique flags a component selection decision for deeper analysis, use this skill to explore the specific tradeoff with full pros/cons.
- **`dependency-mapper`** -- When a kata design includes multiple interacting services, use this skill to visualize coupling and blast radius concerns.
- **`architecture-journal`** -- Record design decisions from completed katas as ADRs. Each completed kata should produce at least one ADR capturing the most important tradeoff explored.

Reference files: [Kata Templates](references/kata-templates.md) | [Critique Rubric](references/critique-rubric.md)
