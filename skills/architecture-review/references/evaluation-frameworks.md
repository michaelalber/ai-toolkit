# Evaluation Frameworks Reference

This document provides the diagnostic frameworks used during architecture reviews. Each framework is a lens -- a structured way of looking at an architecture to reveal specific categories of problems. No single framework is complete. Used together, they provide comprehensive coverage.

## SOLID as Diagnostic Lenses

SOLID principles are not rules to enforce. They are diagnostic questions. Each principle, when applied as a question, reveals a specific category of architectural problem.

### Single Responsibility Principle (SRP) -- Change Axis Diagnostic

**The diagnostic question:** "How many independent reasons does this component have to change?"

**What it reveals:**
- Components that will become bottlenecks for multiple teams
- Classes or services that accumulate unrelated responsibilities over time
- Deployment coupling: when unrelated changes force the same component to redeploy

**How to apply at the architecture level:**
- For each service or module, list the business capabilities it supports
- If a service supports more than one business capability, ask: "Do these capabilities change at the same rate, for the same reasons, by the same team?"
- If the answer is no, the component has multiple change axes and will likely become a coordination bottleneck

**Example diagnostic conversation:**
- "Your OrderService handles order creation, payment processing, and inventory reservation. Those are three different business capabilities. If the payment provider changes their API, why does the inventory logic need to be redeployed?"

### Open/Closed Principle (OCP) -- Extension Point Diagnostic

**The diagnostic question:** "Can this component accommodate new behavior without modifying existing code?"

**What it reveals:**
- Components that will require shotgun surgery when requirements change
- Missing abstraction points where new behavior types are likely
- Fragile areas where adding a feature risks breaking existing features

**How to apply at the architecture level:**
- Identify the most likely axes of change (new payment methods, new report types, new user roles)
- For each axis, trace the code path: how many files or services need to change to add a new variant?
- If adding a new variant requires modifying existing components rather than extending them, the design is closed for extension

**Example diagnostic conversation:**
- "You support three payment providers today. When you add a fourth, how many services need to change? Is it just configuration, or does it require code changes in the order flow?"

### Liskov Substitution Principle (LSP) -- Contract Diagnostic

**The diagnostic question:** "Can consumers of this interface rely on consistent behavior from all implementations?"

**What it reveals:**
- Interface implementations that violate caller expectations
- API versioning problems where new versions break old consumers
- Service replacements that subtly change behavior (e.g., caching layer that changes consistency semantics)

**How to apply at the architecture level:**
- For each interface or API contract, list all implementations or service versions
- For each implementation, verify that it satisfies the same postconditions, handles the same error cases, and respects the same invariants
- Pay special attention to error handling: does the fallback service throw the same exceptions as the primary?

**Example diagnostic conversation:**
- "Your caching layer implements the same interface as your database repository. When the cache returns a result, is it guaranteed to be as fresh as the database result? If not, callers that assume freshness will have subtle bugs."

### Interface Segregation Principle (ISP) -- Dependency Surface Diagnostic

**The diagnostic question:** "Does this consumer depend on capabilities it does not use?"

**What it reveals:**
- Fat interfaces that create unnecessary coupling
- Services that expose too many operations, forcing consumers to know about capabilities they do not need
- API designs that make versioning and evolution difficult

**How to apply at the architecture level:**
- For each service API, list all consumers
- For each consumer, identify which operations it actually calls
- If consumers use less than half the API surface, the interface is too broad and changes to unused operations will create unnecessary deployment dependencies

**Example diagnostic conversation:**
- "Your UserService API has 14 endpoints. The notification system only calls getUserEmail. But because it depends on the UserService client library, it gets recompiled and potentially broken when you change the user profile endpoints. Should the notification system really depend on the full UserService?"

### Dependency Inversion Principle (DIP) -- Direction of Control Diagnostic

**The diagnostic question:** "Do high-level policies depend on low-level details, or is it the other way around?"

**What it reveals:**
- Business logic contaminated with infrastructure concerns
- Components that cannot be tested without infrastructure (databases, queues, external services)
- Vendor lock-in at the architecture level

**How to apply at the architecture level:**
- Trace the dependency arrows in the architecture diagram
- High-level business logic should not depend on low-level infrastructure
- If your order processing logic imports your PostgreSQL driver, the dependency is in the wrong direction
- At the service level: does your service API definition depend on the message broker implementation, or is the broker an implementation detail behind an abstraction?

**Example diagnostic conversation:**
- "Your business rules for fraud detection directly reference your Kafka topic names and AWS SQS queue URLs. If you switch message brokers, you need to modify fraud detection logic. Should the fraud detection rules know about the transport mechanism at all?"

## ATAM: Architecture Tradeoff Analysis Method (Simplified)

ATAM is a structured method for evaluating architecture against quality attribute requirements. The full ATAM process involves multiple stakeholders over several days. This is a simplified version suitable for a single review session.

### Step 1: Identify Quality Attribute Scenarios

Quality attributes are the "-ilities": availability, scalability, performance, security, modifiability, testability, deployability.

For each relevant quality attribute, define a concrete scenario:

| Quality Attribute | Scenario | Response Measure |
|-------------------|----------|-----------------|
| Availability | Primary database fails during peak hours | System continues serving read requests within 5 seconds of failover |
| Performance | 1000 concurrent users submit orders simultaneously | 95th percentile response time under 2 seconds |
| Modifiability | Add a new payment provider | Requires changes to fewer than 3 files, deployable within 1 sprint |
| Scalability | Traffic increases 10x over 6 months | System handles increased load with horizontal scaling, no architecture changes |
| Security | Attacker gains access to a single service's credentials | Blast radius limited to that service's data; no lateral movement possible |
| Deployability | Deploy a critical bug fix to production | Deployable within 30 minutes, affects only the changed service |

### Step 2: Map Scenarios to Architecture Decisions

For each scenario, identify which architectural decisions enable or prevent the desired response:

- Which components are involved?
- What is the current design's response to this scenario?
- Where does the design fall short?
- What tradeoffs were made that affect this scenario?

### Step 3: Identify Sensitivity Points and Tradeoff Points

**Sensitivity points:** Architecture decisions that significantly affect a single quality attribute. "If we change the database replication strategy, availability changes dramatically."

**Tradeoff points:** Architecture decisions that affect multiple quality attributes in opposite directions. "The caching layer improves performance but reduces consistency."

These are the most important findings of the analysis. They represent decisions that require conscious tradeoff acceptance.

### Step 4: Catalog Risks and Non-Risks

**Risks:** Architecture decisions that create the potential for undesirable outcomes, given the quality attribute scenarios.

**Non-risks:** Architecture decisions that are demonstrably safe for the specified scenarios.

Documenting non-risks is as important as documenting risks. It prevents re-litigating settled decisions.

## FMEA for Software: Failure Mode and Effects Analysis

FMEA is borrowed from manufacturing and adapted for software architecture. It systematically walks through each component and asks: "How can this fail, and what happens when it does?"

### FMEA Table Structure

| Component | Failure Mode | Effect on System | Severity (1-10) | Probability (1-10) | Detection (1-10) | RPN | Mitigation |
|-----------|-------------|-----------------|-----------------|--------------------|--------------------|-----|------------|
| [component] | [how it fails] | [what happens] | [impact] | [likelihood] | [how hard to detect] | [S x P x D] | [what to do] |

**Severity** (1-10): How bad is it when this failure occurs?
- 1-3: Minor inconvenience, user can work around it
- 4-6: Significant degradation, some users affected, data intact
- 7-8: Major outage, many users affected, potential data inconsistency
- 9-10: Complete system failure, data loss, safety or financial impact

**Probability** (1-10): How likely is this failure to occur?
- 1-3: Rare (once per year or less)
- 4-6: Occasional (monthly)
- 7-8: Frequent (weekly)
- 9-10: Near certain (daily or continuous)

**Detection** (1-10): How hard is it to detect this failure before it impacts users?
- 1-3: Automatically detected and alerted within seconds
- 4-6: Detected by monitoring within minutes
- 7-8: Detected by user reports or manual checks
- 9-10: Silent failure, not detected until downstream consequences appear

**Risk Priority Number (RPN):** Severity x Probability x Detection. Higher is worse. Anything above 200 demands immediate mitigation.

### Common Software Failure Modes

Use this checklist to systematically walk through failure modes:

- **Crash failure:** Component stops completely
- **Omission failure:** Component fails to respond to a request
- **Timing failure:** Component responds too slowly
- **Response failure:** Component responds incorrectly
- **Byzantine failure:** Component behaves unpredictably or maliciously
- **Resource exhaustion:** Memory, connections, disk, file handles
- **Dependency failure:** A component this depends on fails
- **Data corruption:** Bad data enters the system and propagates
- **Split brain:** Distributed components disagree on system state
- **Cascading failure:** One component's failure causes others to fail

## Scalability Analysis Framework

### Step 1: Identify the Load Profile

Before analyzing scalability, understand the current and projected load:

- **Throughput:** Requests per second, messages per second, transactions per hour
- **Data volume:** Records per table, storage per month, growth rate
- **Concurrency:** Simultaneous users, concurrent connections, parallel processes
- **Load pattern:** Steady, bursty, time-of-day, seasonal, event-driven

### Step 2: Find the First Bottleneck

Every system has a bottleneck. The question is not "does it scale?" but "what breaks first?"

Walk through the request path from user to response:

1. Load balancer / API gateway (connection limits, TLS termination cost)
2. Application servers (CPU, memory, thread pool)
3. Database (connection pool, query performance, lock contention, replication lag)
4. Cache (memory limits, eviction rate, thundering herd on miss)
5. External services (rate limits, latency, availability)
6. Message queues (consumer throughput, queue depth, ordering guarantees)
7. Storage (IOPS, bandwidth, consistency model)

For each component, ask: "At what load does this component's response time or error rate degrade unacceptably?"

### Step 3: Analyze Scaling Strategy for Each Bottleneck

| Bottleneck | Horizontal Scaling | Vertical Scaling | Cost | Complexity |
|-----------|-------------------|-----------------|------|------------|
| [component] | [how to scale out] | [how to scale up] | [relative cost] | [operational complexity added] |

### Step 4: Identify Scaling Cliffs

A scaling cliff is a load level where a component's behavior changes discontinuously. Examples:
- Database connection pool exhausted: response time jumps from 50ms to 30s
- Cache eviction rate exceeds fill rate: every request hits the database
- Single-node limit reached: must re-architect to distribute

These are the most dangerous scalability risks because they are not gradual degradation -- they are sudden failure.

## Operational Complexity Assessment

### Operational Complexity Score

For each component in the architecture, score the operational burden:

| Factor | Score (1-5) | Description |
|--------|-------------|-------------|
| Deployment frequency | [1-5] | 1=yearly, 5=multiple times daily |
| Deployment risk | [1-5] | 1=zero-downtime automated, 5=manual with downtime |
| Monitoring coverage | [1-5] | 1=comprehensive dashboards, 5=no monitoring |
| Debugging difficulty | [1-5] | 1=centralized logs with tracing, 5=SSH into boxes and grep |
| Configuration management | [1-5] | 1=automated and versioned, 5=manual edits on servers |
| Dependency management | [1-5] | 1=automated updates with tests, 5=manual, fear-driven |
| Incident response | [1-5] | 1=runbooks and automation, 5=hero culture |
| Scaling operations | [1-5] | 1=auto-scaling, 5=manual provisioning |

**Total operational complexity:** Sum of all factors. Higher is harder to operate.

- 8-16: Low operational burden. Team can manage alongside development.
- 17-24: Moderate. Requires dedicated operational practices.
- 25-32: High. Requires dedicated operations staff or significant automation investment.
- 33-40: Extreme. Reconsider the architecture's operational feasibility.

**Key question:** Multiply the number of components by their average operational complexity score. This is the total operational surface area. Can your team handle it?

## Security Threat Modeling: STRIDE

STRIDE is a threat classification model developed at Microsoft. Each letter represents a category of security threat. Apply it to every trust boundary in the architecture.

### STRIDE Categories

| Threat | Description | Architecture Question |
|--------|-------------|----------------------|
| **S**poofing | Pretending to be someone or something else | "How does each component verify the identity of its callers? What happens if a caller forges an authentication token?" |
| **T**ampering | Modifying data in transit or at rest | "What data flows between components? Is it signed or encrypted? What happens if someone modifies a message in the queue?" |
| **R**epudiation | Denying an action was taken | "Can a user or service deny performing an action? Is there an immutable audit log? Who has access to modify the logs?" |
| **I**nformation Disclosure | Exposing data to unauthorized parties | "What sensitive data exists in the system? Where is it stored, how is it transmitted, and who can access it? What happens if a database backup is leaked?" |
| **D**enial of Service | Making the system unavailable | "Can an unauthenticated user consume enough resources to degrade service for others? Are there rate limits? What is the cost of processing a single malicious request versus a legitimate one?" |
| **E**levation of Privilege | Gaining unauthorized capabilities | "If an attacker compromises a single service, what can they access? Can they move laterally? Are service accounts scoped to minimum required permissions?" |

### Applying STRIDE to Architecture

1. Draw a data flow diagram of the architecture
2. Identify every trust boundary (where data crosses between different security domains)
3. For each trust boundary, apply all six STRIDE categories
4. For each applicable threat, assess: is there a mitigation in the current design?
5. Document unmitigated threats as security vulnerabilities in the review

### Trust Boundary Examples

- Between the user's browser and the API gateway
- Between the API gateway and internal services
- Between services and the database
- Between services and external third-party APIs
- Between the application and the message broker
- Between different deployment environments (staging, production)
- Between different tenants in a multi-tenant system
