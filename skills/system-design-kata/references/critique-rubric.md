# Critique Rubric

Consistent, calibrated scoring for system design kata critiques. Every critique uses the same nine dimensions with the same 1-5 scale. Dimension weighting varies by domain to reflect which aspects matter most for a given problem type.

---

## Scoring Dimensions

### 1. Requirements Coverage

Does the design address every stated functional requirement?

| Score | Descriptor |
|-------|-----------|
| 1 | Multiple functional requirements are not addressed. The design solves a different problem than the one stated. |
| 2 | Most requirements are mentioned but 2-3 are only partially addressed. Key capabilities are missing or hand-waved. |
| 3 | All requirements are addressed at a high level. 1-2 requirements lack sufficient detail to evaluate correctness. |
| 4 | All requirements are addressed with clear component-to-requirement mapping. Minor gaps in edge case handling. |
| 5 | Every requirement has a specific component responsible for it, with clear data flow and explicit handling of edge cases. |

### 2. NFR Compliance

Do the back-of-envelope numbers support the stated performance, availability, and capacity targets?

| Score | Descriptor |
|-------|-----------|
| 1 | No quantitative analysis. NFRs are acknowledged but not validated against the design. |
| 2 | Some numbers are provided but key calculations are missing or incorrect. Design likely violates 2+ NFR targets. |
| 3 | Core throughput and storage calculations are present. Latency analysis is superficial. 1 NFR target is likely violated. |
| 4 | All NFR targets have supporting calculations. Assumptions are stated. Minor gaps in burst capacity or tail latency analysis. |
| 5 | Comprehensive quantitative analysis with stated assumptions. Throughput, latency (P50/P95/P99), storage growth, and cost are all validated against targets. |

### 3. Component Selection

Are the chosen technologies appropriate for the domain, scale, and constraints?

| Score | Descriptor |
|-------|-----------|
| 1 | Components are listed without rationale. Selections are inappropriate for the stated scale or constraints. |
| 2 | Components are reasonable but alternatives are not considered. 1-2 components are over-engineered or under-powered for the stated requirements. |
| 3 | Components are appropriate for the stated scale. Rationale is provided for major choices. 1 component selection has a significant tradeoff that is not acknowledged. |
| 4 | All components have clear rationale. Alternatives are mentioned for key decisions. Components match the team's stated capacity to operate them. |
| 5 | Every component has rationale tied to a specific requirement or constraint. Alternatives are evaluated. Operational complexity is factored into selections. Team capability is explicitly considered. |

### 4. Data Flow Coherence

Does data flow logically from source to sink without bottlenecks, unnecessary hops, or consistency gaps?

| Score | Descriptor |
|-------|-----------|
| 1 | Data flow is not described. Components are listed but connections between them are unclear or absent. |
| 2 | Data flow is described at a high level but has logical gaps. 2+ points where data format, serialization, or protocol is unspecified. |
| 3 | Data flow is complete from ingestion to output. 1 bottleneck or unnecessary hop exists. Data formats are mostly specified. |
| 4 | Data flow is complete and efficient. Formats, protocols, and serialization are specified at each boundary. Minor optimization opportunities exist. |
| 5 | Data flow is complete, efficient, and annotated with throughput expectations at each stage. Serialization boundaries are explicit. No unnecessary hops. Back-pressure is addressed. |

### 5. Failure Handling

What happens when each major component fails? Is there a single point of failure?

| Score | Descriptor |
|-------|-----------|
| 1 | Failure modes are not discussed. The design assumes all components are always available. |
| 2 | Failure is mentioned for 1-2 components but most failure modes are not addressed. At least one obvious SPOF exists and is not acknowledged. |
| 3 | Major component failures are addressed (database, message broker, API server). 1-2 failure modes are missing. Recovery strategy is described but not detailed. |
| 4 | All major failure modes are addressed with specific recovery strategies. Blast radius is discussed. Minor gaps in partial failure scenarios (e.g., network partition between two specific components). |
| 5 | Comprehensive failure analysis covering component failure, network partition, data corruption, and cascading failure. Recovery strategies are specific with expected recovery times. No unacknowledged SPOFs. Graceful degradation is described. |

### 6. Scalability Approach

Does the scaling strategy actually work? Are there hidden bottlenecks?

| Score | Descriptor |
|-------|-----------|
| 1 | No scaling strategy. The design handles the stated load but has no path to 10x. |
| 2 | Scaling is mentioned ("we can add more instances") without analysis of what actually limits scale. Hidden bottleneck exists (shared state, single database, unpartitioned data). |
| 3 | Horizontal scaling strategy is described for stateless components. Stateful component scaling is acknowledged but not fully detailed. 1 hidden bottleneck remains. |
| 4 | Scaling strategy covers both stateless and stateful components. Partitioning and sharding strategies are described. Cost of scaling is estimated. Minor gaps in 100x scenario. |
| 5 | Comprehensive scaling analysis for 10x and 100x. Bottleneck identification at each stage. Partitioning strategy is explicit. Scaling triggers and procedures are described. Cost projection at scale is included. |

### 7. Operational Readiness

Can this system be deployed, monitored, and debugged? Is the Day 2 story credible?

| Score | Descriptor |
|-------|-----------|
| 1 | No mention of deployment, monitoring, or operational concerns. The design exists only as an architecture diagram. |
| 2 | Deployment is mentioned but not detailed. Monitoring is vague ("we will use CloudWatch"). No runbooks or alerting strategy. |
| 3 | Deployment strategy is described (CI/CD, rolling updates). Key metrics are identified. Alerting is mentioned. Log aggregation is acknowledged. Gaps in debugging workflow. |
| 4 | Deployment is automated with rollback capability. Key metrics, alerts, and dashboards are defined. Log aggregation and tracing are addressed. On-call implications are discussed. |
| 5 | Full operational picture: automated deployment with canary/blue-green, comprehensive observability (metrics, logs, traces), runbooks for common failure scenarios, on-call rotation considerations, capacity planning process. |

### 8. Security Posture

Are authentication, authorization, encryption, and audit concerns addressed?

| Score | Descriptor |
|-------|-----------|
| 1 | Security is not mentioned. No authentication, no encryption, no access control. |
| 2 | Authentication is mentioned for external interfaces. Internal service-to-service communication is unsecured. No encryption at rest. No audit logging. |
| 3 | Authentication and authorization are addressed for external and internal interfaces. Encryption in transit is specified. Encryption at rest is mentioned. Audit logging gaps exist. |
| 4 | Comprehensive auth/authz model. Encryption in transit and at rest. Audit logging for data access. Secrets management is addressed. Minor gaps in least-privilege or network segmentation. |
| 5 | Defense in depth: network segmentation, mutual TLS for service-to-service, encryption at rest with key rotation, comprehensive audit trail, least-privilege access, vulnerability management, compliance controls mapped to requirements. |

### 9. Cost Awareness

Is the design cost-efficient for the stated constraints?

| Score | Descriptor |
|-------|-----------|
| 1 | No cost analysis. The design may be wildly over- or under-budget. |
| 2 | Cost is mentioned but not estimated. Major cost drivers (compute, storage, egress) are not identified. |
| 3 | Monthly cost estimate is provided for major components. 1-2 cost drivers are underestimated or missing. Estimate is within 2x of the stated budget. |
| 4 | Detailed cost breakdown by component. Estimate is within 20% of the stated budget. Cost optimization strategies are mentioned (reserved instances, tiered storage, etc.). |
| 5 | Comprehensive cost model with per-component breakdown. Estimate is within budget with identified optimization opportunities. Cost at 10x scale is projected. Cost-performance tradeoffs are explicit. |

---

## Common Design Smells

Design smells are recurring patterns in submitted designs that indicate a deeper issue. When you spot a smell, trace it back to the underlying gap.

| Smell | What It Indicates | Probe Question |
|-------|-------------------|----------------|
| **Every component is "highly available" with no specifics** | The designer is hand-waving availability instead of designing for it. | "Walk me through what happens when your primary database node fails at 3 AM. What is the sequence of events, and how long is the system degraded?" |
| **A single database serves all read and write patterns** | The designer has not considered access pattern divergence. Dashboards, transactions, and analytics have fundamentally different requirements. | "Your dashboard queries a 90-day window while your API serves real-time writes. What happens to dashboard latency when write throughput doubles?" |
| **Message broker appears but message contract is unspecified** | The designer is using the broker as a magic decoupling layer without thinking about schema evolution, ordering guarantees, or failure semantics. | "What is the schema of the messages in this topic? What happens when you need to add a field next month? What ordering guarantees do consumers depend on?" |
| **"Microservices" without service boundaries justified** | The designer is defaulting to microservices as a pattern without identifying which boundaries reduce coupling and which create distributed monolith problems. | "Why are these two services separate rather than one? What would break if they were combined? What coupling exists between them?" |
| **No mention of data consistency model** | The designer has not decided between strong and eventual consistency, or does not realize the components they chose have different consistency models. | "Your API reads from a cache that is populated asynchronously from the database. What does the user see if they write and then immediately read?" |
| **Scaling strategy is "add more instances"** | The designer has not identified the stateful bottleneck. Stateless scaling is trivial; stateful scaling is the hard problem. | "When you add more API instances, what happens to your database connection count? What happens to your cache hit rate? What is the actual bottleneck?" |
| **Monitoring is an afterthought (listed last, no specifics)** | The designer treats observability as a checkbox rather than a load-bearing requirement. | "Your correlation engine is slow. How do you know? What metric alerts you? What dashboard do you open first? What log do you search?" |
| **Security section says "use HTTPS and OAuth"** | The designer is listing technologies instead of designing a security model. Authentication is not authorization. HTTPS is not a security architecture. | "A compromised internal service sends requests to your data store. What prevents it from reading another tenant's data? What audit trail exists?" |

---

## Dimension Weighting by Domain

Not all dimensions are equally important for every kata. Weight the scoring to reflect what matters most in the problem domain. The weights below multiply the raw score (1-5) to produce a weighted total.

### Standard Weighting (default)

| Dimension | Weight | Max Weighted Score |
|-----------|--------|--------------------|
| Requirements Coverage | 1.0 | 5 |
| NFR Compliance | 1.0 | 5 |
| Component Selection | 1.0 | 5 |
| Data Flow Coherence | 1.0 | 5 |
| Failure Handling | 1.0 | 5 |
| Scalability Approach | 1.0 | 5 |
| Operational Readiness | 1.0 | 5 |
| Security Posture | 1.0 | 5 |
| Cost Awareness | 1.0 | 5 |
| **Total** | | **45** |

### Security-Heavy Domain (SIEM, fintech, healthcare, compliance)

| Dimension | Weight | Max Weighted Score |
|-----------|--------|--------------------|
| Requirements Coverage | 1.0 | 5 |
| NFR Compliance | 1.0 | 5 |
| Component Selection | 0.8 | 4 |
| Data Flow Coherence | 1.0 | 5 |
| Failure Handling | 1.2 | 6 |
| Scalability Approach | 0.8 | 4 |
| Operational Readiness | 1.0 | 5 |
| Security Posture | 1.5 | 7.5 |
| Cost Awareness | 0.7 | 3.5 |
| **Total** | | **45** |

### Latency-Sensitive Domain (trading, gaming, real-time control)

| Dimension | Weight | Max Weighted Score |
|-----------|--------|--------------------|
| Requirements Coverage | 1.0 | 5 |
| NFR Compliance | 1.5 | 7.5 |
| Component Selection | 1.0 | 5 |
| Data Flow Coherence | 1.5 | 7.5 |
| Failure Handling | 1.0 | 5 |
| Scalability Approach | 0.8 | 4 |
| Operational Readiness | 0.8 | 4 |
| Security Posture | 0.7 | 3.5 |
| Cost Awareness | 0.7 | 3.5 |
| **Total** | | **45** |

### Cost-Constrained Domain (startups, non-profits, small teams)

| Dimension | Weight | Max Weighted Score |
|-----------|--------|--------------------|
| Requirements Coverage | 1.0 | 5 |
| NFR Compliance | 0.8 | 4 |
| Component Selection | 1.2 | 6 |
| Data Flow Coherence | 0.8 | 4 |
| Failure Handling | 0.8 | 4 |
| Scalability Approach | 0.7 | 3.5 |
| Operational Readiness | 1.2 | 6 |
| Security Posture | 0.8 | 4 |
| Cost Awareness | 1.7 | 8.5 |
| **Total** | | **45** |

### Edge/IoT Domain (fleet management, sensor networks, embedded)

| Dimension | Weight | Max Weighted Score |
|-----------|--------|--------------------|
| Requirements Coverage | 1.0 | 5 |
| NFR Compliance | 1.0 | 5 |
| Component Selection | 1.0 | 5 |
| Data Flow Coherence | 1.2 | 6 |
| Failure Handling | 1.5 | 7.5 |
| Scalability Approach | 1.0 | 5 |
| Operational Readiness | 1.2 | 6 |
| Security Posture | 0.8 | 4 |
| Cost Awareness | 0.3 | 1.5 |
| **Total** | | **45** |

### Platform/SRE Domain (multi-tenant, deployment orchestration, infrastructure)

| Dimension | Weight | Max Weighted Score |
|-----------|--------|--------------------|
| Requirements Coverage | 1.0 | 5 |
| NFR Compliance | 0.8 | 4 |
| Component Selection | 1.0 | 5 |
| Data Flow Coherence | 0.8 | 4 |
| Failure Handling | 1.2 | 6 |
| Scalability Approach | 1.0 | 5 |
| Operational Readiness | 1.5 | 7.5 |
| Security Posture | 1.0 | 5 |
| Cost Awareness | 0.7 | 3.5 |
| **Total** | | **45** |

---

## Applying the Rubric

1. **Score each dimension independently.** Read the design submission, then evaluate each dimension against the 1-5 descriptors. Do not let a strong performance in one dimension inflate others.

2. **Select the domain weighting.** Based on the kata's domain, apply the appropriate weight to each raw score. If the kata spans multiple domains, use standard weighting or create a custom blend.

3. **Compute the weighted total.** This is the overall score. Report it as "X / 45" regardless of weighting scheme (the weights are calibrated so the maximum is always 45).

4. **Identify the bottom 3 dimensions.** These become the focus of the critique. The critique should spend 70% of its content on the weakest areas and 30% acknowledging strengths.

5. **Map smells to gaps.** If any design smells from the table above are present, reference them in the critique and connect them to the specific dimension they affect.

6. **Generate targeted questions.** For each dimension scoring 3 or below, generate a question that probes the gap without revealing the answer. The question should be one the user can reason through with the information in the problem statement.
