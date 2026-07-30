# Domain Principles, Knowledge Lookups, Anti-Patterns, and Recovery

Depth for `architecture-review`. SKILL.md carries the CACR loop and the discipline rules; this
file carries the principle catalog, the knowledge-base lookup map, the anti-pattern table, a
worked state-block example, and the recovery playbook for difficult review dynamics.

## Domain Principles

| # | Principle | Description | Applied As |
|---|-----------|-------------|------------|
| 1 | **Every Decision Has a Tradeoff** | There is no free lunch in architecture. Every choice that gives you something also takes something away. The question is never "is there a tradeoff?" but "is this the right tradeoff for our context?" | Surface the cost of every architectural choice, even when the user presents it as obviously correct. |
| 2 | **Question Assumptions First** | The most dangerous part of any architecture is the assumptions that nobody stated. Unstated assumptions become unplanned outages. | Before evaluating the architecture, enumerate the assumptions it depends on. Challenge each one. |
| 3 | **Failure Modes Before Features** | Features are what you build. Failure modes are what you live with. Every component will eventually fail. The architecture must have answers before anyone writes a line of code. | For every component and integration point, ask: "What happens when this fails?" |
| 4 | **Coupling Is the Enemy You Cannot See** | Coupling hides in shared databases, synchronized deployments, implicit contracts, and temporal dependencies. The damage appears months later when a "simple change" breaks three other services. | Map every dependency. For each one, ask: "If I change this, what else breaks?" |
| 5 | **Operational Complexity Counts** | An architecture that is elegant on a whiteboard but impossible to operate is a failed architecture. Every additional service is another thing to monitor, deploy, scale, secure, and debug at 3 AM. | For every component, ask: "Who deploys this? Who monitors it? Who debugs it at 3 AM?" |
| 6 | **SOLID as Diagnostic, Not Dogma** | The SOLID principles are lenses for diagnosis, not commandments to follow blindly. A violation tells you something is wrong, but the fix depends on context, team size, and expected change patterns. | Apply SOLID principles as diagnostic questions, not as rules to enforce. |
| 7 | **Scalability Has a Cost** | Premature scalability adds complexity, cost, and operational burden for a future that may never arrive. The right answer depends on likelihood and preparation cost. | Ask: "What is the first bottleneck? At what load does it break? What is the cost of fixing it later?" |
| 8 | **Security Is an Architecture Concern** | Authentication boundaries, authorization models, data classification, encryption, and audit logging are architectural decisions. A security review after the architecture is frozen finds expensive problems. | Identify trust boundaries, data flows across them, and the authentication/authorization model at each boundary. |
| 9 | **Simplicity Requires Defense** | Complexity is the default outcome of every design process. Every meeting adds a feature; every developer adds an abstraction. Simplicity requires active, continuous defense. | Challenge every abstraction layer, every indirection, every "just in case" component. Demand justification. |
| 10 | **Evidence Over Intuition** | "I think this will be fast enough" is not evidence. "We benchmarked this at 2400 RPS with p99 latency of 45ms on hardware similar to production" is evidence. | For every performance, scalability, or reliability claim, ask: "How do you know? What is the evidence?" |

## Knowledge Base Lookups

Search at the start of each category to calibrate questioning depth and terminology. Cite the source in the vulnerability report.

| Query | When to Call |
|-------|--------------|
| `search_knowledge("SOLID principles architecture diagnostic")` | During ATTEMPT phase -- ground SOLID diagnostic questions in authoritative principles |
| `search_knowledge("coupling afferent efferent stability metrics")` | During ATTEMPT phase -- ground coupling-revealing questions in Martin's metrics |
| `search_knowledge("failure modes distributed systems resilience")` | During ATTEMPT phase -- inform failure mode questioning with real distributed failure patterns |
| `search_knowledge("scalability bottleneck architecture tradeoffs")` | During ATTEMPT phase -- ground scalability boundary questions in evidence |
| `search_knowledge("STRIDE threat modeling security architecture")` | During security boundary questioning |
| `search_knowledge("architecture decision records ADR tradeoffs")` | During REFLECT phase -- guide ADR creation from accepted tradeoffs |
| `search_knowledge("12 factor app operational complexity")` | During operational readiness questioning |

## Anti-Patterns

| Anti-Pattern | Why It Fails | What to Do Instead |
|--------------|-------------|-------------------|
| **Rubber Stamping** | Misses hidden assumptions, coupling, and failure modes. Creates false confidence. | Ask at least 3 questions per category, even for architectures that look solid. |
| **Astronaut Architecture** | Ignores team size, budget, timeline, and operational capability. Produces architectures the team cannot maintain. | Always ask: "What is your team size? What is your deployment infrastructure? What is your timeline?" |
| **Analysis Paralysis** | If everything is a problem, nothing gets fixed. The architect freezes. | Identify the 2-3 critical items. Make everything else medium or low. Give a clear first step. |
| **SOLID Dogmatism** | SOLID principles are diagnostic tools, not laws. A small class with two responsibilities in a 3-person CRUD app is not the same problem as a god class in a distributed system. | Apply SOLID violations as observations, then ask: "Given your team size and rate of change, is this a problem now or later?" |
| **Failure Mode Blindness** | Production systems spend more time in degraded states than on whiteboards. | For every integration point, ask: "What happens when this is slow? Down? Returns garbage?" |
| **Scalability Theater** | Adds operational complexity and real costs for hypothetical growth. | Ask: "What is your current load? Projected load in 12 months? Cost of adding scalability later?" |
| **Coupling Blindness** | Microservices in name only -- the overhead of distribution without the benefits of independence. | Map the actual dependency graph: shared databases, shared schemas, deployment dependencies, temporal coupling. |
| **Security Afterthought** | Trust boundaries and authorization models are architectural decisions. Adding them later requires redesigning the architecture. | Include at least 3 security questions in every review: trust boundaries, data flows, authentication model. |

## Error Recovery

**Architect becomes defensive** (short answers, "Are you saying our design is wrong?"): Pause questioning immediately. Reaffirm purpose: "I am stress-testing the design, not criticizing you." Acknowledge specific strengths. Ask what the architect thinks is the riskiest part. Reduce challenge depth by one level.

**Incomplete architecture presented** ("We haven't decided that yet," many vague diagram boxes): Do not attempt a full review. Shift to exploration mode: help the architect identify the decisions that constrain everything else. Offer a surface-level review now and a deeper review later.

**Architect overwhelmed by findings**: Immediately prioritize: "Of these [N] findings, only [2-3] are critical. Let me walk you through just those." Separate must-fix from nice-to-fix. Give a concrete first step. Offer to re-review after critical items are addressed.

**Known pattern with known tradeoffs**: Acknowledge the pattern and its standard concerns. Focus on implementation-specific details: "The interesting questions are not about the pattern itself but about how you have applied it to your specific context."

## State Block — Worked Example

```
<arch-review-state>
mode: compare
architecture_description: E-commerce platform with 4 microservices, shared PostgreSQL, Redis cache, RabbitMQ messaging
challenge_depth: moderate
vulnerabilities_found: 14
categories_examined: assumptions, SOLID, coupling, failure_modes, scalability, operations
last_action: Vulnerability report delivered -- 2 critical, 4 high, 5 medium, 3 low
next_action: Walk through vulnerabilities with architect for tradeoff acceptance
</arch-review-state>
```
