# ADR Templates Reference

## Standard ADR Template

The standard template is for significant decisions that affect system architecture, cross multiple components, or are difficult to reverse.

### Template

```markdown
# ADR-[NUMBER]: [Short Descriptive Title]

**Date**: YYYY-MM-DD
**Status**: Proposed | Accepted | Deprecated | Superseded by ADR-XXXX
**Deciders**: [Names or roles of people involved]
**Related ADRs**: [ADR numbers, or "none"]

## Context

[Describe the situation that requires a decision. Include:
- The problem or opportunity
- Technical constraints (existing systems, performance requirements, SLAs)
- Business constraints (deadlines, budget, team capacity)
- Organizational constraints (team skills, vendor relationships, compliance)

Be specific. Use numbers, dates, and measurable criteria.]

## Decision

We will [clear statement of the decision].

[One to three sentences. If you need more, the decision may be too broad.]

## Alternatives Considered

### [Alternative A Name]

- **Description**: [What this involves]
- **Pros**: [Specific advantages]
- **Cons**: [Specific disadvantages]
- **Why rejected**: [The decisive factor against this option]

### [Alternative B Name]

- **Description**: [What this involves]
- **Pros**: [Specific advantages]
- **Cons**: [Specific disadvantages]
- **Why rejected**: [The decisive factor against this option]

## Consequences

### Expected Positive
- [Observable, measurable prediction]
- [Observable, measurable prediction]

### Expected Negative
- [Observable, measurable prediction]
- [Observable, measurable prediction]

### Risks
- [What could go wrong and under what conditions]

## Review Schedule

- 30-day review: YYYY-MM-DD
- 90-day review: YYYY-MM-DD
- 180-day review: YYYY-MM-DD

## Notes

[Links to design docs, meeting notes, relevant PRs, or external references]
```

## Lightweight ADR Template

For smaller decisions that still warrant recording -- API naming conventions, library choices within an established category, configuration decisions, internal protocol choices.

### Template

```markdown
# ADR-[NUMBER]: [Title]

**Date**: YYYY-MM-DD | **Status**: Accepted
**Context**: [Two to four sentences describing the situation and constraints]
**Decision**: We will [decision].
**Alternatives**: [Alternative A] rejected because [reason]. [Alternative B] rejected because [reason].
**Consequences**: Expect [positive]. Risk [negative].
**Review**: 90-day review on YYYY-MM-DD.
```

### When to Use Lightweight vs Standard

Use **standard** when:
- The decision affects multiple teams or components
- The decision is expensive to reverse (data storage, communication protocols, API contracts)
- The decision involves significant trade-offs that need explanation
- Multiple stakeholders have opinions

Use **lightweight** when:
- The decision is scoped to a single component
- The decision is relatively easy to reverse
- The trade-offs are straightforward
- The decision follows an established pattern

## ADR Status Lifecycle

```
Proposed
    |
    v
Accepted -----> Deprecated (no longer relevant)
    |
    v
Superseded by ADR-XXXX (replaced by a new decision)
```

**Proposed**: Decision is drafted but not yet agreed upon. Used when the decision requires review from others before adoption.

**Accepted**: Decision is active and in effect. The team is expected to follow it.

**Deprecated**: Decision is no longer relevant because the context has changed (e.g., the system it applied to was decommissioned). No replacement decision needed.

**Superseded**: Decision has been replaced by a new decision. The superseding ADR must be referenced. The old ADR stays in the journal for historical context.

## Naming Conventions and Numbering

### File Naming

```
docs/adr/
  0001-use-postgresql-for-order-service.md
  0002-adopt-event-sourcing-for-inventory.md
  0003-choose-grpc-for-internal-services.md
  0004-implement-circuit-breaker-pattern.md
```

**Rules**:
- Four-digit zero-padded sequential numbers
- Lowercase with hyphens
- Verb-noun format when possible ("use", "adopt", "choose", "implement", "replace")
- Keep titles under 60 characters
- Never renumber existing ADRs

### Category Prefixes (Optional)

For large projects, consider category prefixes in the title:

```
0001-data-use-postgresql-for-order-service.md
0002-messaging-adopt-event-sourcing-for-inventory.md
0003-api-choose-grpc-for-internal-services.md
0004-resilience-implement-circuit-breaker-pattern.md
```

## Example ADRs

### Example 1: Database Choice

```markdown
# ADR-0001: Use PostgreSQL for Order Service

**Date**: 2024-03-15
**Status**: Accepted
**Deciders**: Backend team lead, DBA, CTO
**Related ADRs**: none

## Context

The order service currently uses an in-memory store (development only) and
needs a production database. Requirements:

- ACID transactions for order state changes (orders cannot be partially created)
- Query patterns include both point lookups by order ID and range queries by
  customer ID with date filtering
- Expected volume: 50k orders/day initially, scaling to 500k/day within 18 months
- Team has strong PostgreSQL experience (4 of 5 backend engineers)
- Budget constraint: managed service preferred, under $2k/month at initial scale
- Must support JSON fields for order metadata (variable schema per product type)

## Decision

We will use PostgreSQL (AWS RDS) for the order service data store.

## Alternatives Considered

### MySQL (AWS RDS)

- **Description**: MySQL 8.x on RDS with InnoDB
- **Pros**: Lower cost at small scale, team has some experience
- **Cons**: Weaker JSON support, less mature window functions, partial index
  support not as flexible
- **Why rejected**: JSON query support is materially weaker, and the team is
  more productive with PostgreSQL

### DynamoDB

- **Description**: AWS DynamoDB with single-table design
- **Pros**: Managed scaling, pay-per-request pricing, predictable latency
- **Cons**: No ACID transactions across items (only within 25-item transaction
  limit), complex access patterns require careful key design, team has no
  DynamoDB experience
- **Why rejected**: ACID transaction requirement across order + line items
  exceeds DynamoDB transaction limits for large orders. Team ramp-up time
  estimated at 4-6 weeks.

## Consequences

### Expected Positive
- Order creation with 10+ line items will have ACID guarantees
- Team can be productive immediately (no learning curve)
- JSON fields allow flexible order metadata without schema migrations

### Expected Negative
- RDS requires capacity planning; scaling beyond 500k orders/day will need
  read replicas or sharding
- Monthly cost estimated $800-1200 at initial scale

### Risks
- If order volume exceeds projections, RDS vertical scaling has limits;
  migration to a sharded solution would be a significant effort

## Review Schedule

- 30-day review: 2024-04-15
- 90-day review: 2024-06-15
- 180-day review: 2024-09-15

## Notes

- Profiling data from load test: https://internal.wiki/load-test-2024-03
- RDS sizing calculations: https://internal.wiki/rds-sizing
```

### Example 2: Authentication Approach

```markdown
# ADR-0005: Adopt OAuth 2.0 with JWT for API Authentication

**Date**: 2024-04-20
**Status**: Accepted
**Deciders**: Security team, API team lead, Platform architect
**Related ADRs**: ADR-0003 (gRPC for internal services)

## Context

The public API currently uses API keys with no expiration. Security audit
(2024-04-01) flagged this as a high-severity finding. Requirements:

- Support for third-party integrations (B2B partners need scoped access)
- Token expiration and rotation without client coordination
- Compatible with gRPC services (ADR-0003) via metadata headers
- Must support machine-to-machine (client credentials) and user-delegated flows
- Compliance requires audit trail of token issuance and revocation
- Team has 6 weeks to implement before the Q3 partner launch

## Decision

We will implement OAuth 2.0 with JWT access tokens, using Auth0 as the
identity provider. Tokens will have a 15-minute expiry with refresh token
rotation.

## Alternatives Considered

### Self-hosted Keycloak

- **Description**: Deploy Keycloak on Kubernetes, manage identity in-house
- **Pros**: Full control, no per-user licensing costs, self-contained
- **Cons**: Operational burden (upgrades, HA, backup), 2-3 weeks additional
  setup versus managed service
- **Why rejected**: 6-week deadline does not accommodate the additional ops
  setup. Team has no Keycloak experience.

### API Keys with Expiration and Scoping

- **Description**: Extend current API key system with expiration dates and
  scope fields
- **Pros**: Minimal change to existing clients, simple implementation
- **Cons**: No standard protocol (custom auth), no delegation flow, audit
  flagged API keys specifically
- **Why rejected**: Does not address the security audit finding. Does not
  support user-delegated access for partner integrations.

## Consequences

### Expected Positive
- Third-party integrations can use standard OAuth 2.0 libraries
- 15-minute token expiry limits blast radius of compromised tokens
- Auth0 provides audit logging out of the box

### Expected Negative
- Auth0 cost: approximately $3k/month at projected user count
- Clients must implement token refresh logic
- Auth0 introduces an external dependency for all API access

### Risks
- Auth0 outage blocks all API authentication; need fallback strategy
- JWT validation adds 2-5ms per request (acceptable, but measurable)

## Review Schedule

- 30-day review: 2024-05-20
- 90-day review: 2024-07-20
- 180-day review: 2024-10-20
```

### Example 3: Caching Strategy (Lightweight)

```markdown
# ADR-0008: Use Redis for Product Catalog Cache

**Date**: 2024-06-10 | **Status**: Accepted
**Context**: Product catalog API averages 2000 req/sec with p99 of 180ms.
Database is the bottleneck (confirmed by tracing). Catalog data changes
infrequently (5-10 updates/day). Target p99 under 50ms.
**Decision**: We will use Redis (ElastiCache) as a read-through cache with
60-second TTL for product catalog queries.
**Alternatives**: Application-level in-memory cache rejected because we run
12 instances and cache coherence across instances adds complexity. CDN-level
caching rejected because authenticated users see personalized pricing.
**Consequences**: Expect p99 under 30ms for cached queries. Risk stale data
for up to 60 seconds after catalog update (acceptable per product team).
Redis adds $200/month and a new operational dependency.
**Review**: 90-day review on 2024-09-10.
```

## Organizing ADRs in a Project

### Recommended Directory Structure

```
project-root/
  docs/
    adr/
      0001-use-postgresql-for-order-service.md
      0002-adopt-event-sourcing-for-inventory.md
      0003-choose-grpc-for-internal-services.md
      INDEX.md                  # Decision inventory
      LEARNING-EXTRACTS.md      # Principles distilled from retrospectives
      templates/
        standard.md             # Copy-paste template
        lightweight.md          # Copy-paste template
        retrospective-30.md     # 30-day review template
        retrospective-90.md     # 90-day review template
        retrospective-180.md    # 180-day review template
```

### INDEX.md

Maintain a decision inventory file that lists all ADRs with their status and next review date. Update this file whenever you add, deprecate, or supersede a decision. This is the entry point for anyone wanting to understand the project's architectural history.

### Version Control

- ADRs should be committed to the same repository as the code they govern.
- ADRs should be reviewed in pull requests like any other code change.
- Retrospectives should be appended to or linked from the original ADR, not stored separately.
- Never delete an ADR. Mark it as deprecated or superseded instead.
- The git history of an ADR file is itself a valuable record of how thinking evolved.

### Multi-Repository Projects

For projects spanning multiple repositories:
- Keep a central ADR repository for cross-cutting decisions
- Keep repository-specific ADRs in each repository
- Cross-reference using full paths: "See platform-adr/0012 for the authentication decision"
- The central decision inventory should reference ADRs in all repositories

### Team Onboarding

New team members should read the decision inventory and the five most recent ADRs as part of onboarding. This provides more architectural context than any design document because it includes the reasoning, the rejected alternatives, and the expected consequences -- not just the final outcome.
