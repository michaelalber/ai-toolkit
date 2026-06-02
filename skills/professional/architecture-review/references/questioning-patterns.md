# Questioning Patterns Reference

This document catalogs the questions used during architecture reviews, organized by category. Each question is designed to reveal a specific class of architectural vulnerability. The questions are ordered from broad to specific within each category.

## How to Use This Catalog

Do not ask every question in every review. Select questions based on:

1. **Challenge depth:** Surface reviews use 1-2 questions per category. Deep reviews use 5-8. Adversarial reviews use all of them plus follow-ups.
2. **Architecture type:** A stateless API needs different questions than an event-driven system. Skip questions that do not apply.
3. **Architect's responses:** When the architect gives a strong answer, move on. When the answer is weak or uncertain, ask follow-ups from the same category before moving to the next.

## Assumption-Surfacing Questions

These questions uncover what the architecture depends on but does not state. Unstated assumptions are the most dangerous architectural vulnerabilities because nobody plans for their failure.

1. "What assumptions about user behavior does this architecture depend on? What happens if users do something unexpected -- like submitting a form twice, or opening 50 tabs simultaneously?"
2. "What assumptions about data volume does this design make? What is the largest table or collection you expect in 12 months? In 36 months? Are those numbers based on data or intuition?"
3. "What assumptions about network reliability does this design make? Are there calls between components that assume the network is always available and always fast?"
4. "What third-party services does this architecture depend on? What are their SLAs? Have you verified those SLAs, or are you assuming they match your requirements?"
5. "What assumptions about team size and skill set does this architecture make? Could a new developer, unfamiliar with the system, deploy a change safely within their first week?"
6. "What assumptions about consistency does this design make? When data is written in one component, how quickly must it be visible in other components? What happens if there is a delay?"
7. "What assumptions about ordering does this design make? If two events arrive out of order, does the system handle it correctly or produce corrupt state?"
8. "What assumptions about deployment does this architecture make? Does it assume zero-downtime deployments? Does it assume all services are deployed simultaneously? What happens during a rolling deployment when old and new versions coexist?"
9. "What assumptions about security does this architecture make? Does it assume the internal network is trusted? Does it assume tokens cannot be forged? Does it assume input from internal services is validated?"
10. "What assumptions about infrastructure does this architecture make? Does it assume specific cloud provider features? Does it assume specific hardware capabilities? What is the portability story if you need to change providers?"
11. "What assumptions about time does this design make? Does it assume clocks are synchronized across services? Does it assume operations complete within a specific time window? What happens if a process that usually takes 100ms takes 10 seconds?"
12. "What is the single assumption that, if wrong, would cause the most damage to this architecture? How would you detect that it is wrong before it causes damage?"

## Coupling-Revealing Questions

These questions map hidden dependencies between components. Coupling is the primary constraint on system evolution -- tightly coupled systems resist change, and changes propagate unpredictably.

1. "Can you deploy Service A without deploying Service B? If not, why not? What shared artifacts or configurations prevent independent deployment?"
2. "If you change the database schema for Service A, which other services are affected? Do they query the same tables directly, or do they go through Service A's API?"
3. "Draw the dependency graph. Now draw the deployment graph. Do they match? If services that are architecturally independent are deployed together, you have deployment coupling."
4. "How many services share the same database? For each shared table, who owns the schema? What is the process for making a schema change?"
5. "If you need to change the format of a message on the message bus, how many consumers need to be updated? Can you make the change backward-compatible, or must all consumers update simultaneously?"
6. "What happens if you change the API contract for your most heavily consumed service? How many consumers break? Is there a versioning strategy, or does every change require coordinating with all consumers?"
7. "Are there any shared libraries used by multiple services? If you update the shared library, do all services need to rebuild and redeploy? Can different services use different versions?"
8. "Does any service call another service synchronously during request processing? If the called service is slow, does the caller become slow? If the called service is down, does the caller fail?"
9. "Are there temporal dependencies between services? Does Service A need to complete before Service B can start? What happens if Service A is delayed?"
10. "Do any services share configuration values (database connection strings, API keys, feature flags)? If a configuration value changes, how many services are affected? Is the change atomic or rolling?"
11. "If you wanted to rewrite Service A from scratch in a different language, what would you need to replicate? Is it just the API contract, or are there implicit behavioral dependencies (ordering guarantees, timing assumptions, error code conventions)?"
12. "How do you handle cross-cutting concerns -- logging, authentication, rate limiting? Are they implemented independently in each service, or is there a shared infrastructure dependency? What happens if the shared infrastructure changes?"

## Failure Mode Questions

These questions walk through specific failure scenarios to determine whether the architecture has answers or merely hopes. Every component will eventually fail. The question is whether the failure is graceful or catastrophic.

1. "What are the single points of failure in this architecture? For each one, what is the impact of its failure and what is the recovery time?"
2. "If the primary database becomes unreachable for 2 minutes, what is the user experience? Do requests fail immediately, queue for later processing, serve stale data, or show an error page?"
3. "If one of your services starts responding slowly (10x normal latency instead of failing outright), what happens to its callers? Do they time out? Do they retry? Do they consume their own thread pools waiting?"
4. "What happens if your message queue fills up? Is there a back-pressure mechanism? Do producers block, drop messages, or write to a dead letter queue? How do you recover the lost messages?"
5. "If a downstream service returns an error, does the error propagate to the user or is it handled gracefully? Show me the error handling path for your most critical user flow."
6. "What happens during a partial deployment -- when half your instances are running the new version and half are running the old version? Can they coexist? What if the new version writes data in a format the old version cannot read?"
7. "If your cache becomes unavailable, what happens to your database? Have you calculated the load your database would receive if 100% of cache misses hit it simultaneously (thundering herd)?"
8. "What is your circuit breaker strategy? If a downstream service is failing, do you keep sending requests (and wasting resources), or do you fail fast and serve a degraded response?"
9. "What happens if bad data enters the system? If a service publishes a malformed message, what prevents it from propagating through the system and corrupting downstream data?"
10. "What is the blast radius of a single service failure? List every user-facing feature that becomes unavailable when each individual service goes down. Are there features that depend on ALL services being up?"
11. "If your system loses power during a write operation, what is the data state when it comes back up? Is the write atomic? Is there a transaction log? Can you recover to a consistent state?"
12. "What happens when an external API you depend on changes its behavior without warning -- not an outage, but a subtle change in response format, error codes, or rate limits? How would you detect it? How quickly could you adapt?"
13. "Have you tested any of these failure scenarios, or are the answers theoretical? What is your strategy for verifying failure handling before it matters in production (chaos engineering, fault injection, game days)?"

## Scalability Boundary Questions

These questions identify the load levels at which the architecture's behavior changes -- not just when it slows down, but when it fundamentally breaks.

1. "What is the first component that will fail under increased load? At what specific load level does it fail? How do you know -- is this measured or estimated?"
2. "What is the second bottleneck? After you fix the first, where does the load shift to? Systems often have cascading bottleneck chains."
3. "Are there any operations that scale non-linearly with data volume? Queries that are fast with 10,000 rows but unacceptable with 10 million? Joins that grow quadratically?"
4. "What is your horizontal scaling strategy? Can you add more instances of each component to handle more load? Are there components that cannot be horizontally scaled (stateful services, single-writer databases)?"
5. "What is the maximum throughput of your database connection pool? If all application instances share the same database, what is the total connection limit? At what application scale do you exhaust it?"
6. "How does your system handle a sudden 10x traffic spike (viral event, marketing campaign, DDoS)? Does it degrade gracefully, fail completely, or auto-scale? How long does auto-scaling take, and what happens to requests during the scaling period?"
7. "What are the data retention requirements? At your current growth rate, how much storage do you need in 1 year? 3 years? What is the cost? What is the archival or purge strategy?"
8. "If you need to partition or shard your data in the future, how would you do it? What is the partition key? Are there cross-partition queries that would become expensive or impossible?"
9. "What is the read-to-write ratio of your primary data store? If it shifts (more writes, more reads, more updates), how does performance change? Have you tested this?"
10. "Are there rate limits on your external dependencies (third-party APIs, cloud provider limits, DNS resolution limits)? At what load do you hit those limits? What is the cost of increasing them?"

## Operational Readiness Questions

These questions assess whether the architecture can be operated in production by real humans -- not just designed on a whiteboard.

1. "How do you deploy this system? Walk me through the steps from 'code merged' to 'running in production.' How long does it take? How many manual steps are involved?"
2. "What does your monitoring look like? For each service, what metrics do you collect? What are the alert thresholds? Who gets paged? What is the escalation path?"
3. "If a user reports that a specific transaction failed, how do you trace it? Can you follow a single request through all the services it touches? How long does that investigation take?"
4. "What happens when you need to roll back a deployment? Is it automated? How long does it take? What happens to data written by the new version -- is it compatible with the old version's schema?"
5. "How do you manage configuration across environments (dev, staging, production)? Where is configuration stored? How do you prevent a staging configuration value from leaking into production?"
6. "What is your on-call experience like? When someone gets paged at 3 AM for this system, what tools and documentation do they have? Are there runbooks? Have they been tested?"
7. "How do you handle database migrations in production? Can they run without downtime? What happens if a migration fails halfway through?"
8. "How do you manage secrets (API keys, database passwords, certificates)? Where are they stored? Who has access? How do you rotate them? What happens when a secret is accidentally committed to version control?"
9. "What is your disaster recovery plan? If you lose an entire availability zone or region, what is the recovery time objective (RTO) and recovery point objective (RPO)? Have you tested this?"
10. "How do you handle dependency updates? When a critical security patch is released for a library you depend on, how quickly can you assess, test, and deploy the update? What is the average time from CVE publication to production deployment?"

## How to Sequence Questions for Maximum Insight

The order in which you ask questions matters. The goal is to build understanding incrementally, so that later questions can reference earlier answers.

### Recommended Sequence

```
1. Assumption-Surfacing (questions 1-4)
   Purpose: Establish what the architecture depends on

2. Coupling-Revealing (questions 1-4)
   Purpose: Map the dependency structure

3. SOLID Diagnostics (from evaluation-frameworks.md)
   Purpose: Identify structural vulnerabilities

4. Failure Mode (questions 1-5)
   Purpose: Test the architecture against realistic failures

5. Scalability Boundary (questions 1-4)
   Purpose: Find the load limits

6. Operational Readiness (questions 1-4)
   Purpose: Verify the architecture can be operated

7. Security (STRIDE from evaluation-frameworks.md)
   Purpose: Identify trust boundary vulnerabilities
```

### Adaptive Sequencing

The sequence above is the default. Adapt it based on what you learn:

- **If early questions reveal heavy coupling**, expand the coupling category before moving to failure modes. Coupled systems have correlated failure modes, so understanding coupling first makes the failure mode questions more specific.
- **If the architecture is well-decomposed**, spend less time on coupling and more on operational readiness. Well-decomposed systems are harder to operate because there are more moving parts.
- **If the architect is defensive**, start with the categories where they are strongest. Early success builds trust for harder questions later.
- **If the architecture is a monolith**, de-emphasize coupling and deployment questions. Focus instead on SRP diagnostics, database scalability, and failure modes within the monolith.
- **If the system is greenfield**, spend more time on assumption-surfacing and scalability. There is no production data to validate assumptions against.
- **If the system is in production**, spend more time on operational readiness and failure modes. You can ask: "When was the last outage? What caused it? How long did it take to resolve?"

## How to Handle Defensive Responses

Defensiveness is a signal, not a problem. It usually means one of three things: the architect feels personally criticized, the architect knows there is a problem but does not want to admit it, or the question was asked in a way that felt like an accusation rather than a curiosity.

### Pattern: Redirect to Curiosity

When the architect is defensive, shift from challenging questions to curious questions.

```
Defensive trigger: "Why did you choose a shared database?"
Curious alternative: "I am interested in the database architecture.
                     What factors led to the shared database decision?
                     What alternatives did you consider?"
```

### Pattern: Acknowledge Then Probe

Validate the decision before exploring its consequences.

```
Instead of: "The synchronous calls between services are a problem."
Try:        "Synchronous calls give you strong consistency guarantees,
             which is clearly important for your use case. I am curious
             about the latency implications -- have you measured the
             end-to-end response time for the longest call chain?"
```

### Pattern: Use Scenarios Instead of Judgments

Defensive architects respond better to "what if" scenarios than to "this is wrong" statements.

```
Instead of: "Your error handling is insufficient."
Try:        "Walk me through what happens when a user submits an order
             and the payment service returns a 500 error. What does the
             user see? What happens to the order? What do the logs show?"
```

### Pattern: Ask for Help Understanding

Position yourself as trying to understand, not trying to find fault.

```
Instead of: "This coupling is going to cause deployment problems."
Try:        "Help me understand the deployment process. When you change
             Service A, do you also need to deploy Service B? I want
             to understand the deployment dependencies."
```

### Pattern: Offer Your Own Uncertainty

If you are not sure something is a problem, say so. It invites collaboration rather than defense.

```
Instead of: "This will not scale."
Try:        "I am not sure about the scalability characteristics here.
             My instinct says the join on these four tables will get
             expensive at higher volumes, but I could be wrong. Have
             you had a chance to benchmark it?"
```

### When to Stop Pushing

If the architect has answered a question and is visibly frustrated, do not ask follow-up questions in the same category. Make a note, move to a different category, and return to the sensitive area later if needed. The goal is insight, not compliance. An architect who shuts down provides no insight.

### Red Lines

Never:
- Say "you should have" or "you should not have"
- Compare the architect's design unfavorably to a "textbook" design
- Imply that the architect lacks skill or knowledge
- Continue pressing after the architect has explicitly accepted a tradeoff
- Make statements about the architect rather than about the architecture
