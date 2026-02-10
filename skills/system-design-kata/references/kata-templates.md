# Kata Templates

Domain-specific system design exercises with realistic constraints. Each kata is structured for the CACR loop: the problem statement and constraints form the Challenge phase, the expected components inform the Compare phase, and the common mistakes guide targeted critique.

These katas are NOT interview questions. They are domain-calibrated exercises drawn from real engineering problems.

---

## Kata 1: Security Event Pipeline (SIEM-Like)

### Problem Statement

Your organization operates 200+ data sources (firewalls, endpoint agents, cloud audit logs, application logs, network flow data). The security operations team needs a centralized pipeline that ingests, normalizes, correlates, and stores security events for real-time alerting and historical investigation. The current system (a legacy SIEM appliance) cannot keep up with event volume and has a 6-hour search latency for historical queries.

### Functional Requirements

1. Ingest events from 200+ heterogeneous sources with different formats (syslog, JSON, CEF, Windows Event Log).
2. Normalize all events to a common schema (OCSF or ECS) within the pipeline.
3. Correlate events across sources within a 5-minute sliding window to detect multi-stage attacks.
4. Trigger alerts within 2 seconds of correlation match (P99).
5. Store events for 90-day hot retention (searchable < 5 seconds) and 1-year cold retention.
6. Support ad-hoc investigation queries across the full retention window.

### Non-Functional Requirements

| NFR | Target |
|-----|--------|
| Ingestion throughput | 50,000 events/sec sustained, 200K burst |
| Ingestion latency (source to searchable) | P99 < 30 seconds |
| Alert latency (correlation match to notification) | P99 < 2 seconds |
| Query latency (last 24 hours) | P95 < 5 seconds |
| Query latency (90-day window) | P95 < 30 seconds |
| Availability | 99.9% (8.7 hours downtime/year) |
| Storage (hot, 90 days) | ~35 TB (estimated at 1 KB avg event size) |

### Constraints

- Must integrate with existing Kubernetes infrastructure (EKS).
- Team of 4 engineers, no dedicated data engineering role.
- GDPR applies: PII fields must be pseudonymized before storage, audit log of all data access.
- Monthly infrastructure budget: $25,000.

### Expected Components (for Compare phase)

- Ingestion layer: message broker with partitioning (Kafka, Redpanda, or equivalent)
- Normalization: stream processing (Flink, Kafka Streams, or equivalent)
- Correlation engine: windowed stateful processing with rule evaluation
- Hot storage: search-optimized store (Elasticsearch/OpenSearch, ClickHouse)
- Cold storage: object store with compressed columnar format (S3 + Parquet)
- Alert routing: notification service with deduplication and escalation

### Common Mistakes

- Using a single Elasticsearch cluster for both ingestion and querying without index lifecycle management.
- No backpressure handling between ingestion and normalization -- when normalization is slow, the broker fills up.
- Correlation engine that loads all events into memory -- does not scale beyond a few thousand events/sec.
- Ignoring the GDPR pseudonymization requirement until after designing the storage layer.
- No dead-letter queue for events that fail normalization (data loss).

---

## Kata 2: Edge Device Fleet Management (OTA Updates + Telemetry)

### Problem Statement

Your company manufactures industrial IoT sensors deployed in factories, warehouses, and outdoor installations. You manage a fleet of 50,000 devices running a custom Linux-based firmware. Devices report telemetry (health metrics, sensor readings) and must receive over-the-air (OTA) firmware updates. Connectivity is unreliable: devices may be offline for hours or days. A bad firmware update last quarter bricked 2,000 devices and cost $400K in field service visits.

### Functional Requirements

1. Push firmware updates to the fleet with staged rollout (canary -> 10% -> 50% -> 100%).
2. Automatic rollback if device failure rate exceeds 1% during any rollout stage.
3. Collect device telemetry (CPU, memory, temperature, sensor readings) at 1-minute intervals.
4. Device health dashboard with fleet-wide aggregation and per-device drill-down.
5. Support offline devices: updates and telemetry sync when connectivity resumes.
6. Device provisioning: new devices register automatically on first boot.

### Non-Functional Requirements

| NFR | Target |
|-----|--------|
| Fleet size | 50,000 devices, growing 20%/year |
| Telemetry ingestion | ~50K messages/min at steady state |
| OTA update delivery | Full fleet within 48 hours (connectivity permitting) |
| Rollback detection | Failure rate threshold evaluated every 5 minutes |
| Dashboard latency | Aggregated views < 10 seconds, per-device < 3 seconds |
| Availability (cloud platform) | 99.95% |

### Constraints

- Devices have 256 MB RAM, 1 GB flash storage, ARM Cortex-A7 processor.
- Cellular connectivity (LTE-M) with 100 KB/s average bandwidth and per-MB cost.
- Firmware images are 50-80 MB; delta updates reduce this to 5-10 MB.
- Devices run a lightweight MQTT client; no HTTP stack on device.
- Team of 6 engineers (2 firmware, 2 backend, 1 infra, 1 QA).

### Expected Components

- Device registry / shadow service (device state management)
- MQTT broker cluster (for device communication)
- OTA update orchestrator (staged rollout, rollback logic)
- Firmware artifact storage (versioned, signed binaries)
- Telemetry ingestion pipeline (time-series storage)
- Fleet dashboard (aggregated and per-device views)
- Offline reconciliation service (sync queue for disconnected devices)

### Common Mistakes

- No delta update mechanism -- pushing 80 MB over cellular at $0.10/MB costs $4/device ($200K for full fleet).
- Rollback logic that depends on the device phoning home -- if the bad firmware crashes the MQTT client, no rollback signal is sent.
- Single MQTT broker without clustering -- 50K persistent connections with keepalive overwhelms a single instance.
- Telemetry pipeline that stores raw messages without pre-aggregation -- query performance degrades rapidly at fleet scale.
- No firmware signature verification on device -- supply chain attack vector.

---

## Kata 3: Hybrid Cloud Deployment Orchestrator

### Problem Statement

Your organization runs workloads across an on-premises Kubernetes cluster (bare metal, 200 nodes) and two cloud providers (AWS and Azure). Regulatory requirements mandate that certain workloads (processing PII for EU customers) run on-premises in the EU data center. Other workloads can run in any region for cost optimization. The current deployment process is manual: teams submit tickets to the platform team, who manually configure deployments across environments. Average deployment lead time is 3 days.

### Functional Requirements

1. Unified deployment interface: teams describe WHAT to deploy, the orchestrator decides WHERE based on policies.
2. Policy engine: workload placement rules based on data residency, cost, latency, and compliance tags.
3. Multi-cluster deployment: deploy the same service to multiple clusters with environment-specific configuration.
4. Progressive rollout: canary deployments with automated promotion/rollback based on health signals.
5. Drift detection: alert when running state diverges from declared state.
6. Cost allocation: track per-team, per-workload infrastructure cost across all environments.

### Non-Functional Requirements

| NFR | Target |
|-----|--------|
| Deployment latency (submit to running) | < 15 minutes (automated), < 5 minutes for rollback |
| Policy evaluation | < 2 seconds per deployment decision |
| Drift detection interval | Every 5 minutes |
| Platform availability | 99.9% (the orchestrator itself) |
| Supported clusters | 5 today, scaling to 20 within 2 years |

### Constraints

- On-premises cluster has no direct internet access; communication via VPN to cloud.
- GitOps is the desired deployment model (Flux or ArgoCD already used by some teams).
- 15 application teams, each deploying 3-10 services, averaging 5 deployments/day total.
- Platform team is 3 engineers.
- Existing CI/CD: GitHub Actions for build, no standardized deployment pipeline.

### Expected Components

- Deployment API / CLI (unified interface for teams)
- Policy engine (OPA/Rego or equivalent for placement rules)
- GitOps controller per cluster (ArgoCD/Flux with multi-cluster support)
- Configuration management (per-environment overlays, secrets management)
- Health signal aggregation (metrics from all clusters for rollout decisions)
- Drift detection agent (compares declared vs. running state)
- Cost aggregation service (cloud provider billing APIs + on-prem allocation model)

### Common Mistakes

- Building a custom orchestrator from scratch instead of composing existing tools (ArgoCD + OPA + Crossplane).
- Policy engine that does not account for resource availability -- placing a workload on-prem when the cluster is at 90% capacity.
- No offline mode for the on-premises cluster -- if the VPN to cloud is down, on-prem deployments should still work.
- Secrets management that differs per environment -- leads to configuration drift and security incidents.
- Drift detection that alerts but does not reconcile -- alert fatigue without remediation.

---

## Kata 4: Real-Time Sensor Data Aggregation

### Problem Statement

A smart building management company instruments commercial buildings with environmental sensors (temperature, humidity, CO2, occupancy, light level). Each building has 500-2,000 sensors reporting at 10-second intervals. The platform serves building managers (dashboard and alerting), HVAC control systems (real-time data feed), and a data science team (historical analysis for energy optimization models). The current system uses a single PostgreSQL database and is hitting performance limits at 50 buildings.

### Functional Requirements

1. Ingest sensor readings from 500 buildings (averaging 1,000 sensors each) at 10-second intervals.
2. Real-time dashboard: per-building, per-floor, per-zone aggregated views with < 5-second data freshness.
3. Alerting: threshold-based alerts (e.g., CO2 > 1000 ppm) with < 30-second detection latency.
4. HVAC integration: publish real-time aggregated zone data via API with P99 < 200ms.
5. Historical queries: data science team queries spanning months of data for energy modeling.
6. Multi-tenant: each building owner sees only their data; the platform operator sees all.

### Non-Functional Requirements

| NFR | Target |
|-----|--------|
| Sensor count | 500,000 sensors (500 buildings x 1,000) |
| Ingestion rate | 50,000 readings/sec sustained |
| Data freshness (dashboard) | < 5 seconds |
| Alert detection latency | < 30 seconds |
| API latency (HVAC feed) | P99 < 200ms |
| Historical query (1-month window, single building) | < 10 seconds |
| Data retention | 2 years hot, 7 years cold (regulatory) |
| Availability | 99.9% for ingestion and alerting |

### Constraints

- Sensors use MQTT with a lightweight JSON payload (~200 bytes per reading).
- Buildings are distributed globally; latency to the cloud platform varies from 20ms to 200ms.
- Monthly infrastructure budget: $20,000.
- Team of 5 engineers.
- Must support retroactive alert rule changes (re-evaluate historical data against new rules).

### Expected Components

- MQTT broker cluster (per-region or global with bridging)
- Stream processing layer (pre-aggregation by zone/floor/building)
- Time-series database (hot storage for dashboards and alerting)
- Object store + columnar format (cold storage for historical analysis)
- Real-time alerting engine (threshold evaluation on streaming data)
- REST API (HVAC integration, dashboard backend)
- Tenant isolation layer (data partitioning or row-level security)

### Common Mistakes

- Storing every raw reading in a relational database -- 50K writes/sec overwhelms PostgreSQL without partitioning.
- No pre-aggregation -- dashboards that query raw data at zone/floor level are too slow at scale.
- Single MQTT broker for all buildings -- 500K persistent connections requires clustering.
- Ignoring the retroactive alert requirement -- this implies the ability to replay historical data through new rules.
- Tenant isolation implemented only at the API layer, not at the storage layer -- a query bug exposes cross-tenant data.

---

## Kata 5: Multi-Tenant SaaS Platform

### Problem Statement

You are designing the backend platform for a B2B SaaS application that provides project management tools to mid-market companies (100-5,000 employees). Each tenant (customer) has their own workspace with projects, tasks, users, files, and integrations. The sales team is closing deals with larger enterprises that require data isolation guarantees, custom SLAs, and SSO integration. The current single-database architecture cannot provide the isolation or performance guarantees these customers demand.

### Functional Requirements

1. Tenant provisioning: new tenants are operational within 5 minutes of signup.
2. Data isolation: tenant data must be logically or physically separated per customer contract tier.
3. Per-tenant customization: custom fields, workflow rules, and branding without code changes.
4. SSO integration: SAML 2.0 and OIDC for enterprise tenants.
5. Usage metering: track API calls, storage, and active users per tenant for billing.
6. Tenant admin portal: self-service user management, SSO configuration, and usage dashboards.

### Non-Functional Requirements

| NFR | Target |
|-----|--------|
| Tenant count | 500 today, scaling to 5,000 in 2 years |
| Users per tenant | 10-5,000 (wide variance) |
| API latency | P99 < 300ms for CRUD operations |
| Availability | 99.95% (4.3 hours downtime/year) |
| Data isolation (enterprise tier) | Dedicated database per tenant |
| Data isolation (standard tier) | Shared database with row-level security |
| Provisioning time | < 5 minutes for standard, < 30 minutes for enterprise |

### Constraints

- Existing application is a monolithic Python/Django application with a single PostgreSQL database.
- Team of 8 engineers (3 backend, 2 frontend, 1 infra, 1 QA, 1 PM).
- Enterprise customers require SOC 2 Type II compliance and annual penetration testing.
- Must support tenant data export (GDPR right to portability) within 24 hours of request.
- Monthly infrastructure budget scales with tenant count; target $50/month per standard tenant, $500/month per enterprise tenant.

### Expected Components

- Tenant routing layer (maps request to correct database/schema)
- Database-per-tenant for enterprise tier (automated provisioning)
- Shared database with tenant_id partitioning for standard tier
- Identity provider integration (SAML/OIDC broker)
- Configuration service (per-tenant customization without code changes)
- Usage metering pipeline (event-driven, near-real-time aggregation)
- Tenant lifecycle management (provisioning, suspension, data export, deletion)

### Common Mistakes

- Trying to migrate the monolith to microservices AND add multi-tenancy simultaneously -- too many moving parts.
- Tenant isolation that relies solely on application-level filtering (WHERE tenant_id = X) without database-level enforcement.
- No noisy-neighbor protection -- one large tenant's bulk export saturates shared database IOPS.
- SSO integration bolted on as an afterthought, requiring custom code per identity provider.
- No automated tenant provisioning -- enterprise tier requires manual DBA intervention for database creation.
- Data export that requires engineering involvement -- GDPR portability requests become engineering tickets.

---

## Kata 6: API Gateway with Rate Limiting and Authentication

### Problem Statement

Your platform exposes a public API used by 2,000+ third-party integrators (partners, customers building custom integrations, and internal services). The current architecture has each backend service implementing its own authentication and rate limiting, leading to inconsistent behavior, security gaps, and duplicated code. A recent incident caused by an integrator sending 10x normal traffic took down a critical backend service because there was no centralized rate limiting.

### Functional Requirements

1. Centralized authentication: validate API keys, OAuth 2.0 tokens, and mutual TLS certificates.
2. Rate limiting: per-client, per-endpoint, and global rate limits with configurable burst allowances.
3. Request routing: route to appropriate backend service based on path, headers, and client tier.
4. Request/response transformation: add headers, strip internal fields, format conversion.
5. Analytics: per-client usage tracking for billing and capacity planning.
6. Developer portal: self-service API key management, documentation, and usage dashboards.

### Non-Functional Requirements

| NFR | Target |
|-----|--------|
| Request throughput | 15,000 req/sec sustained, 50K burst |
| Added latency (gateway overhead) | P99 < 10ms |
| Rate limit accuracy | Within 5% of configured limit (distributed counting) |
| Availability | 99.99% (52 minutes downtime/year) |
| Configuration propagation | Rate limit changes effective within 30 seconds |
| Backend services | 25 services, 150 endpoints |

### Constraints

- Must support graceful degradation: if the rate limiter is unavailable, requests pass through (fail-open) with logging.
- Rate limit state must survive individual node failures without resetting counters.
- API keys must be revocable with immediate effect (< 5 seconds to propagate).
- Monthly infrastructure budget: $8,000 for the gateway layer.
- Team of 3 engineers (shared with other platform work).

### Expected Components

- API gateway (envoy, Kong, or custom based on constraints)
- Distributed rate limiter (token bucket or sliding window with shared state)
- Auth service (token validation, certificate verification, key lookup)
- Configuration store (rate limit rules, routing rules, with change propagation)
- Analytics pipeline (request logging, aggregation, billing integration)
- Developer portal (key management, docs, usage dashboard)
- Health check / circuit breaker (per-backend health tracking)

### Common Mistakes

- Rate limiting with local counters per gateway node -- clients distribute across nodes and effectively get N x the limit.
- Centralized rate limiter (single Redis) becomes a SPOF violating the 99.99% availability requirement.
- Token validation that calls the auth database on every request -- adds 5-20ms latency per request.
- No circuit breaker to backend services -- a slow backend causes the gateway to exhaust its connection pool.
- Fail-closed rate limiter -- when Redis is down, all traffic is rejected, causing a self-inflicted outage.
- Configuration changes that require gateway restarts -- violates the 30-second propagation requirement.

---

## Kata 7: Disaster Recovery Orchestrator

### Problem Statement

Your organization runs its primary workloads in a single cloud region. After a recent 4-hour regional outage that cost $2M in lost revenue, leadership has mandated a disaster recovery capability with a 1-hour Recovery Time Objective (RTO) and 15-minute Recovery Point Objective (RPO). The system includes stateful services (databases, message queues), stateless services (API servers, workers), and external integrations (payment processors, email providers). The DR plan must be testable without impacting production.

### Functional Requirements

1. Automated failover: detect regional failure and initiate DR within 5 minutes of detection.
2. Data replication: continuous replication of all stateful services to the DR region.
3. DNS failover: redirect traffic to the DR region with minimal client disruption.
4. DR testing: monthly DR drills that validate the full failover process without impacting production.
5. Failback: controlled return to primary region after recovery with data reconciliation.
6. Runbook automation: step-by-step procedures encoded as executable scripts, not wiki documents.

### Non-Functional Requirements

| NFR | Target |
|-----|--------|
| RTO (recovery time objective) | < 1 hour |
| RPO (recovery point objective) | < 15 minutes |
| DR test frequency | Monthly, fully automated |
| Failover detection time | < 5 minutes |
| DNS propagation | < 5 minutes (TTL management) |
| DR environment cost | < 40% of production cost (warm standby) |

### Constraints

- Primary region: us-east-1. DR region: us-west-2.
- Stateful services: PostgreSQL (2 TB), Redis (50 GB), Kafka (200 GB retention).
- 15 stateless services running on Kubernetes.
- External integrations (payment, email, SMS) have region-specific endpoints.
- Team of 2 SREs responsible for DR (not full-time on this).
- DR budget: $30,000/month for standby infrastructure.

### Expected Components

- Health monitoring and failure detection (synthetic probes, cloud health APIs)
- Database replication (cross-region read replicas or logical replication)
- Message queue mirroring (Kafka MirrorMaker or equivalent)
- DNS failover controller (Route 53 health checks or equivalent)
- Kubernetes cluster in DR region (warm standby with scaled-down replicas)
- Runbook engine (automated failover steps with human approval gates)
- DR test harness (isolated test that simulates failover without impacting production)
- Data reconciliation service (handles conflicts during failback)

### Common Mistakes

- Asynchronous database replication without monitoring replication lag -- RPO is violated silently.
- DR Kubernetes cluster with stale container images -- failover succeeds but services crash on startup.
- DNS TTL set to 24 hours -- clients continue hitting the failed region for up to a day after failover.
- No DR testing -- the first time the failover runs is during an actual disaster, and it fails.
- External integrations hardcoded to primary region endpoints -- DR services cannot reach payment processors.
- Failback that does not reconcile data written to DR during the outage -- data loss on return to primary.

---

## Customizing Katas for a Specific Domain

### Step 1: Identify the Domain Context

Before generating a custom kata, gather:

- **Industry**: What industry does the user work in? (fintech, healthcare, industrial IoT, e-commerce, etc.)
- **Scale**: What is the current and projected scale? (users, requests, data volume)
- **Constraints**: What technology, regulatory, team, or budget constraints exist?
- **Pain points**: What has broken recently? What keeps the team up at night?

### Step 2: Calibrate the Problem Statement

Write the problem statement as if a real stakeholder is describing the need:

- Use domain-specific terminology (not generic CS vocabulary).
- Include the backstory: what exists today, what is broken, why change is needed.
- Ground the NFRs in real numbers from the user's domain.

### Step 3: Set Constraints That Force Real Tradeoffs

The best constraints are ones that conflict with each other:

- "99.99% availability AND $5K/month budget" forces creative cost-performance tradeoffs.
- "PII encryption at rest AND sub-second query latency" forces decisions about encryption strategies.
- "3-person team AND 20 services" forces prioritization of automation.

### Step 4: Anticipate Common Mistakes

For each custom kata, list 4-6 mistakes that are specific to the domain, not generic:

- Domain-specific anti-patterns (e.g., in fintech: not considering idempotency for payment operations).
- Scale-specific traps (e.g., strategies that work at 1K req/sec but collapse at 100K).
- Operational blind spots (e.g., "who pages when this breaks at 3 AM?").

### Step 5: Define the Critique Calibration

Weight the critique dimensions for the domain:

- Security-heavy domains (fintech, healthcare): weight Security Posture and Compliance higher.
- Latency-sensitive domains (trading, gaming): weight NFR Compliance and Data Flow Coherence higher.
- Cost-constrained domains (startups, non-profits): weight Cost Awareness higher.
- Operational-heavy domains (SRE, platform): weight Operational Readiness and Failure Handling higher.

See [critique-rubric.md](critique-rubric.md) for the full dimension weighting matrix.
