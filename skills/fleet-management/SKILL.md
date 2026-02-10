---
name: fleet-management
description: Rolling deployment strategies, multi-device coordination, and rollback triggers for edge device fleets. Use when managing fleet-wide deployments, configuring rollout strategies, building device registries, or implementing rollback automation.
---

# Fleet Management for Edge Device Deployments

> "In a fleet of a thousand devices, you do not fear the one that fails -- you fear the
> nine hundred and ninety-nine that fail silently."
> -- Kelsey Hightower, Principal Engineer, Google

## Core Philosophy

This skill provides the operational knowledge for managing deployments across fleets of heterogeneous edge devices. It covers rolling deployment strategies, device registry management, health-gated rollouts, and automatic rollback triggers. Every pattern assumes that edge devices are remote, resource-constrained, and potentially unreliable -- the opposite of cloud servers.

**Non-Negotiable Constraints:**
1. **Never deploy to the entire fleet at once** -- Staged rollouts are mandatory. A single bad deployment to an entire fleet can take weeks to recover from when devices are physically distributed.
2. **Rollback must be independent of the new version** -- If the new version crashes on startup, the rollback mechanism must still function. Rollback cannot depend on the application being healthy.
3. **Device state is the source of truth** -- The registry says what you expect. The device says what is real. When they disagree, trust the device.
4. **Offline devices are not failed devices** -- Edge devices go offline for legitimate reasons (power cycles, network outages, maintenance windows). The deployment system must handle offline devices gracefully and catch them up later.
5. **Health checks must be application-aware** -- A device that responds to ping but serves garbage results is not healthy. Health checks must verify actual application correctness.

## Domain Principles Table

| Principle | Description | Priority |
|-----------|-------------|----------|
| **Canary First** | Every deployment begins with a canary subset; never skip canary even for hotfixes | Critical |
| **Health-Gated Waves** | Each rollout wave must pass health checks before the next wave begins | Critical |
| **Rollback Independence** | Rollback mechanism must work even if the new version is completely non-functional | Critical |
| **Device Registry Accuracy** | Maintain an up-to-date inventory of device capabilities, versions, and health status | High |
| **Offline Tolerance** | The system must gracefully handle devices that are offline during deployment and catch them up later | High |
| **Percentage-Based Rollout** | Define rollout stages as fleet percentages, not absolute device counts, for scalability | High |
| **Automatic Rollback Triggers** | Define measurable failure thresholds that trigger automatic rollback without human intervention | High |
| **Deployment Atomicity** | A deployment to a single device either fully succeeds or fully rolls back; no partial states | Medium |
| **Heterogeneous Fleet Support** | Support mixed device types (Jetson, RPi, gateways) in a single coordinated deployment | Medium |
| **Audit Trail** | Every deployment action must be logged with timestamp, device ID, actor, and outcome | Medium |

## Workflow

### Fleet Deployment Pipeline

```
                    +-----------+
                    |  PREPARE  |
                    |  Artifact |
                    +-----+-----+
                          |
                          v
                    +-----+-----+
                    |  VALIDATE |
                    |  Manifest |
                    +-----+-----+
                          |
                          v
                  +-------+-------+
                  |    CANARY     |
                  |  (1-5% fleet) |
                  +-------+-------+
                          |
                     Health Gate
                          |
                          v
               +----------+----------+
               |   HUMAN APPROVAL    |
               | (fleet-wide rollout)|
               +----------+----------+
                          |
                          v
                  +-------+-------+
                  |    WAVE 1     |
                  | (10-25% fleet)|
                  +-------+-------+
                          |
                     Health Gate
                          |
                          v
                  +-------+-------+
                  |    WAVE 2     |
                  | (25-50% fleet)|
                  +-------+-------+
                          |
                     Health Gate
                          |
                          v
                  +-------+-------+
                  |    WAVE 3     |
                  | (remaining)   |
                  +-------+-------+
                          |
                     Health Gate
                          |
                          v
                    +-----+-----+
                    |  CONFIRM  |
                    | Full Fleet|
                    +-----------+
```

### Deployment Strategy Selection

Choose the right strategy based on fleet characteristics:

| Strategy | Best For | Tradeoff | Risk Level |
|----------|----------|----------|------------|
| **Canary + Rolling** | Most edge fleets | Balanced speed and safety | Low |
| **Blue-Green** | Fleets with hot-standby capacity | Fast rollback, double resources | Low |
| **Rolling Update** | Homogeneous fleets with stateless apps | Simple, no extra resources | Medium |
| **A/B Deploy** | Feature testing across device subsets | Complex routing, useful metrics | Medium |
| **Big Bang** | Never for edge fleets | -- | Unacceptable |

### Pre-Deployment Checklist

```
FLEET DEPLOYMENT PRE-FLIGHT
+------------------------------------------------------------------+
| [ ] Deployment artifact built, tested, and checksummed            |
| [ ] Deployment manifest validated against device registry         |
| [ ] Architecture compatibility confirmed for all device groups    |
| [ ] Resource requirements fit within device constraints           |
| [ ] Rollback artifact available and tested                        |
| [ ] Canary devices selected with coverage across device types     |
| [ ] Health check endpoints defined and baseline metrics captured  |
| [ ] Soak periods defined for canary and each wave                 |
| [ ] Failure thresholds defined for automatic rollback             |
| [ ] Communication plan for deployment window                      |
| [ ] Network connectivity verified to fleet (heartbeat check)      |
| [ ] Disk space verified on target devices                         |
+------------------------------------------------------------------+

If ANY checkbox is unchecked -> STOP. Resolve before deploying.
```

## Rollout Strategies -- Detailed

### Canary + Staged Rolling Deployment

The recommended strategy for most edge fleets.

**Phase 1: Canary (1-5% of fleet)**
```
Selection criteria:
  - At least one device per hardware type
  - At least one device per geographic region / deployment group
  - Prefer devices with highest monitoring fidelity
  - NEVER select single points of failure
  - NEVER select devices with known issues

Deployment:
  1. Snapshot current state on canary devices
  2. Deploy new artifact to canary devices
  3. Run smoke tests immediately after deployment
  4. Enter soak period (15-60 minutes, configurable)
  5. Run comprehensive health checks after soak
  6. Compare metrics against pre-deployment baseline
  7. Determine canary verdict: PASS or FAIL
```

**Phase 2: Staged Waves**
```
Wave sizing (percentage of remaining fleet):
  Wave 1:  10-25%  (catch issues missed by canary)
  Wave 2:  25-50%  (build confidence at scale)
  Wave 3:  remaining (complete the rollout)

Between each wave:
  1. Health check ALL deployed devices (not just current wave)
  2. Compare fleet-wide error rate against baseline
  3. Verify resource utilization trends
  4. Wait for inter-wave soak period (5-15 minutes)
  5. Evaluate go/no-go for next wave
```

**Automatic Rollback Triggers:**
```
Trigger immediate rollback of current wave if:
  - Error rate increases > 5% above baseline
  - P95 latency increases > 50% above baseline
  - Any device enters crash loop (3+ restarts in 5 minutes)
  - Memory usage exceeds 90% on any deployed device
  - Health endpoint becomes unreachable on > 10% of wave devices

Trigger full fleet rollback if:
  - Error rate increases > 10% above baseline across all deployed devices
  - Multiple waves show increasing degradation trend
  - Rollback of a single wave does not restore baseline metrics
```

### Blue-Green for Edge Fleets

Requires double the deployment capacity on each device.

```
Setup:
  - Each device runs two deployment slots: BLUE and GREEN
  - One slot is active (serving traffic), the other is standby
  - Load balancer or service router directs traffic to active slot

Deployment:
  1. Identify inactive slot on all devices (e.g., GREEN is standby)
  2. Deploy new artifact to GREEN slot on canary devices
  3. Verify GREEN health on canary
  4. Switch canary traffic from BLUE to GREEN
  5. Verify canary health under live traffic
  6. Deploy GREEN slot on remaining fleet in waves
  7. Switch traffic to GREEN on each wave after verification

Rollback:
  - Instant: switch traffic back from GREEN to BLUE
  - No redeployment needed
  - BLUE slot remains untouched until next deployment cycle
```

**When to Use:**
- Devices have sufficient disk and memory for two deployment slots
- Zero-downtime deployment is required
- Instant rollback is a hard requirement
- Fleet size is manageable (blue-green at scale doubles infrastructure cost)

### Rolling Update (Stateless Applications)

Simplest strategy, suitable for homogeneous fleets with stateless workloads.

```
Configuration:
  max_unavailable: 10%    # Maximum devices being updated simultaneously
  max_surge: 0            # No extra devices (not applicable for edge)
  health_check_interval: 30s
  health_check_timeout: 10s
  min_ready_seconds: 60   # Device must be healthy for 60s before proceeding

Execution:
  1. Select batch of devices (up to max_unavailable)
  2. Stop current application on batch
  3. Deploy new artifact
  4. Start new application
  5. Wait for min_ready_seconds
  6. Health check the batch
  7. If healthy -> proceed to next batch
  8. If unhealthy -> rollback batch, HALT

Rollback:
  - Stop new version on failed batch
  - Restore previous version from local snapshot
  - Verify batch health before proceeding
```

## Health Check Patterns

### Application Health Endpoint

```
GET /health HTTP/1.1

Response (healthy):
{
  "status": "healthy",
  "version": "2.3.1",
  "uptime_seconds": 3600,
  "checks": {
    "inference_engine": "ok",
    "model_loaded": "ok",
    "disk_space": "ok",
    "memory": "ok",
    "gpu": "ok"
  }
}

Response (degraded):
{
  "status": "degraded",
  "version": "2.3.1",
  "uptime_seconds": 120,
  "checks": {
    "inference_engine": "ok",
    "model_loaded": "ok",
    "disk_space": "warning",
    "memory": "ok",
    "gpu": "ok"
  },
  "warnings": ["disk_space below 20% threshold"]
}
```

### Multi-Layer Health Checks

```
Layer 1: Connectivity (fastest, coarsest)
  - Device responds to ICMP ping
  - SSH port is open
  - Deployment agent responds to heartbeat

Layer 2: System Health
  - CPU utilization below threshold
  - Memory usage below threshold
  - Disk space above minimum
  - Temperature below thermal limit
  - No OOM kills in last N minutes

Layer 3: Application Health
  - Health endpoint responds with 200
  - Application version matches expected
  - No crash loops detected
  - Error rate within bounds

Layer 4: Functional Verification (slowest, most thorough)
  - Inference produces correct output on test input
  - End-to-end pipeline latency within bounds
  - Output quality metrics meet threshold
```

## Rollback Patterns

### Snapshot-Based Rollback

```
Before deployment:
  1. Create filesystem snapshot or Docker image tag of current state
  2. Store snapshot locally on device (space permitting)
  3. Verify snapshot integrity (checksum)
  4. Record snapshot metadata in device registry

Rollback execution:
  1. Stop current (failed) application
  2. Restore from local snapshot
  3. Start restored application
  4. Verify health
  5. Report rollback outcome
```

### Dual-Slot Rollback

```
Device layout:
  /opt/app/active  -> symlink to current slot
  /opt/app/slot-a  -> previous version (known good)
  /opt/app/slot-b  -> new version (being deployed)

Deploy:
  1. Write new version to inactive slot
  2. Update symlink: active -> slot-b
  3. Restart application

Rollback:
  1. Update symlink: active -> slot-a
  2. Restart application
  3. Time to rollback: seconds (no file transfer needed)
```

### Container-Based Rollback

```
Deploy:
  docker pull registry.example.com/app:v2.3.1
  docker stop app-current
  docker tag app-current app-rollback
  docker run --name app-current registry.example.com/app:v2.3.1

Rollback:
  docker stop app-current
  docker rm app-current
  docker run --name app-current app-rollback
```

## State Block Format

Maintain state across conversation turns using this block:

```
<fleet-deploy-state>
phase: [PREPARE | CANARY | VERIFY | ROLLOUT | CONFIRM]
strategy: [canary-rolling | blue-green | rolling-update]
artifact: [name and version]
fleet_total: N
deployed_count: N
healthy_count: N
quarantined_count: N
skipped_count: N
rollback_available: [true | false]
current_wave: [N/M]
last_action: [description]
next_action: [description]
blockers: [any issues]
</fleet-deploy-state>
```

## Output Templates

### Deployment Summary Report

```markdown
## Fleet Deployment Report

**Artifact**: [name] v[version]
**Date**: [date]
**Duration**: [start time] to [end time]
**Strategy**: [canary + staged rolling]

### Fleet Summary

| Status | Count | Percentage |
|--------|-------|------------|
| Deployed (healthy) | [N] | [%] |
| Skipped (unreachable) | [N] | [%] |
| Quarantined (failed) | [N] | [%] |
| Not targeted | [N] | [%] |
| **Total fleet** | [N] | 100% |

### Wave Summary

| Wave | Devices | Deployed | Failed | Soak Period | Verdict |
|------|---------|----------|--------|-------------|---------|
| Canary | [N] | [N] | [N] | [duration] | PASS |
| Wave 1 | [N] | [N] | [N] | [duration] | PASS |
| Wave 2 | [N] | [N] | [N] | [duration] | PASS |
| Wave 3 | [N] | [N] | [N] | [duration] | PASS |

### Health Metrics (Post-Deployment)

| Metric | Baseline | Current | Delta |
|--------|----------|---------|-------|
| Error rate | [%] | [%] | [+/- %] |
| P95 latency | [ms] | [ms] | [+/- ms] |
| Avg CPU | [%] | [%] | [+/- %] |
| Avg memory | [MB] | [MB] | [+/- MB] |

### Issues and Notes

- [any issues encountered]
- [quarantined devices and reasons]
- [skipped devices and reasons]
```

## Integration with Other Skills

- **jetson-deploy** -- When deploying to Jetson Orin Nano devices within the fleet, use `jetson-deploy` for device-specific configuration (TensorRT engine building, power mode setting, JetPack version verification). Fleet management handles the coordination; `jetson-deploy` handles the device-level deployment.
- **sensor-integration** -- When the fleet includes devices with sensor payloads, coordinate sensor configuration alongside application deployment. Sensor calibration may need to be re-validated after software updates.
- **edge-cv-pipeline** -- When deploying computer vision pipeline updates, health checks should include inference accuracy validation, not just application liveness. Use `edge-cv-pipeline` patterns for defining functional health checks.

## Common Anti-Patterns to Avoid

| Anti-Pattern | Why It's Wrong | Correct Approach |
|--------------|----------------|------------------|
| Deploying to all devices at once | A single bug bricks the entire fleet; recovery takes weeks | Use canary + staged waves with health gates |
| Skipping canary for "small" changes | Small changes cause production incidents too; one-line bugs exist | Always canary, regardless of change size |
| Health checks that only ping | A device can respond to ping while serving garbage results | Implement application-aware health checks |
| No soak period between waves | Issues that take minutes to manifest (memory leaks, thermal) are missed | Enforce minimum soak periods between waves |
| Rollback that depends on the new version | If the new version crashes on startup, the rollback mechanism fails too | Rollback must be independent of application health |
| Treating offline devices as failed | Edge devices go offline legitimately; marking them failed triggers false alarms | Track offline devices separately; catch them up later |
| Manual rollback procedures | Under pressure, humans skip steps; automated rollback is faster and more reliable | Define automatic rollback triggers with measurable thresholds |
| Deploying without a device registry | You cannot track what is deployed where, making rollback and auditing impossible | Maintain an accurate, up-to-date device registry |

## Error Recovery

### Deployment Wave Exceeds Failure Threshold

```
Problem: More than 20% of devices in a wave fail deployment.

Actions:
1. HALT current wave immediately
2. Rollback ALL devices in the failed wave
3. Verify rolled-back devices return to healthy
4. Collect deployment logs from failed devices
5. Analyze failure pattern:
   - Same failure on all devices? -> Artifact issue
   - Failure on specific device type? -> Compatibility issue
   - Random failures? -> Infrastructure issue (network, disk)
6. Do NOT proceed until root cause is identified
7. Report to user with analysis and recommendations
```

### Canary Shows Gradual Degradation

```
Problem: Canary device metrics slowly degrade during soak period
         (e.g., memory leak, increasing latency).

Actions:
1. Extend soak period to confirm the trend
2. Capture detailed metrics (1-second intervals)
3. If degradation continues:
   a. Rollback canary devices
   b. Verify metrics return to baseline
   c. Report the degradation pattern
4. Common causes:
   - Memory leak in new version
   - Resource contention with background processes
   - Thermal throttling under sustained load
5. Do NOT proceed to fleet rollout with gradual degradation
```

### Device Registry Out of Sync

```
Problem: Registry shows devices that don't exist, or devices report
         different capabilities than registry states.

Actions:
1. Run fleet-wide heartbeat scan
2. Compare heartbeat results against registry
3. For each discrepancy:
   - Device in registry but not responding: mark as OFFLINE
   - Device responding but not in registry: add to registry
   - Capability mismatch: update registry from device report
4. Do NOT deploy to devices with unresolved discrepancies
5. After sync, re-validate deployment manifest against updated registry
```
