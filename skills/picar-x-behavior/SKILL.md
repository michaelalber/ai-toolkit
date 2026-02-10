---
name: picar-x-behavior
description: Build composable robot behaviors for SunFounder Picar-X. Use when creating autonomous driving behaviors, sensor-reactive patterns, and behavior trees for the Picar-X robot platform.
---

# Picar-X Behavior Composer

> "The world is its own best model. The trick is to sense it appropriately and often enough."
> -- Rodney Brooks, *Intelligence Without Representation*

## Core Philosophy

This skill builds composable, safe robot behaviors for the SunFounder Picar-X platform. Behaviors are small, testable units of reactive control that combine into complex autonomous systems through well-defined composition patterns.

**Non-Negotiable Constraints:**
1. **Safety First** -- Every behavior tree MUST include an emergency stop at the highest priority level. No exceptions.
2. **Test Incrementally** -- Validate each behavior in static tests (no motors) before any dynamic test (real hardware). Never skip static testing.
3. **Compose From Simple** -- Build complex behaviors by composing verified simple behaviors. Never write a monolithic control loop.
4. **Bound All Outputs** -- Motor speeds, servo angles, and timing must have hard limits enforced at the driver layer, not just at the behavior layer.
5. **Fail Safe** -- Any unhandled exception, sensor timeout, or communication failure MUST result in a full stop, not continued operation.

## Domain Principles Table

| Principle | Description | Priority |
|-----------|-------------|----------|
| **Safety Constraints** | Hard limits on speed, servo range, and runtime; emergency stop always accessible | Critical |
| **Behavior Isolation** | Each behavior reads sensors and produces actuator commands independently; no hidden shared state | Critical |
| **Composability** | Behaviors combine through priority, sequence, and parallel patterns with predictable results | Critical |
| **Reactive Control** | Sense-act loops run at fixed frequency; behaviors respond to current sensor state, not stale data | High |
| **Graceful Degradation** | If a sensor fails, the robot reduces capability rather than crashing or acting on garbage data | High |
| **Deterministic Startup** | Robot always starts in a known safe state: speed zero, servos centered, sensors polled | High |
| **Timeout Watchdogs** | Every motor command expires after a bounded interval; no "set and forget" drive commands | High |
| **Testability** | Every behavior can be tested with mocked hardware; real-hardware tests are optional second pass | High |
| **Observability** | Behaviors log decisions, sensor readings, and actuator commands for post-run analysis | Medium |
| **Resource Awareness** | Respect Raspberry Pi CPU/memory limits; camera processing and control loops share resources | Medium |

## Workflow

### Behavior Development Pipeline

```
┌──────────────────────────────────────────────────────────────────┐
│                                                                  │
│   ┌────────┐   ┌───────────┐   ┌─────────────┐   ┌───────────┐ │
│ ─>│ DEFINE │──>│ IMPLEMENT │──>│ TEST_STATIC │──>│TEST_DYNAMIC│ │
│   └────────┘   └───────────┘   └─────────────┘   └───────────┘ │
│                                                        │        │
│        ┌─────────┐      ┌────────┐                     │        │
│        │ DEPLOY  │<─────│COMPOSE │<────────────────────┘        │
│        └─────────┘      └────────┘                              │
│             │                ▲                                   │
│             └────────────────┘ (add more behaviors)             │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### Pre-Flight Checklist

Before ANY dynamic test or deployment, verify:

```
┌─────────────────────────────────────────────────┐
│ Pre-Flight Hardware Safety Check                │
├─────────────────────────────────────────────────┤
│ [ ] Battery charged and securely connected      │
│ [ ] Wheels off ground OR in bounded test area   │
│ [ ] Emergency stop mechanism verified working   │
│ [ ] Servo range calibration confirmed           │
│ [ ] Ultrasonic sensor returning valid readings  │
│ [ ] Camera stream active (if vision behavior)   │
│ [ ] Max speed set to TEST level (<=30)          │
│ [ ] Watchdog timeout configured (<2 seconds)    │
│ [ ] Clear path / no obstacles in test zone      │
│ [ ] Operator within physical reach of robot     │
└─────────────────────────────────────────────────┘
```

### Step-by-Step Workflow

#### DEFINE
1. Name the behavior and describe its goal in one sentence
2. List sensor inputs required (ultrasonic, grayscale, camera)
3. List actuator outputs produced (drive motors, steering servo, camera servos)
4. Define safety constraints: max speed, servo bounds, timeout
5. Describe the expected sense-act loop at a high level

#### IMPLEMENT
1. Create a class inheriting from `Behavior` base class
2. Implement `setup()`, `update()`, and `teardown()` methods
3. Add safety bounds checking inside `update()`
4. Ensure `teardown()` always stops motors and centers servos
5. Add logging for sensor reads and actuator writes

#### TEST_STATIC
1. Mock all hardware interfaces (motors, servos, sensors)
2. Test that `update()` produces correct actuator commands for given sensor inputs
3. Test boundary conditions: sensor min/max, obstacle at threshold distance
4. Test that `teardown()` issues stop commands
5. Test that safety limits are enforced (speed clamping, servo range)
6. Run with `pytest` -- all tests must pass before proceeding

#### TEST_DYNAMIC
1. Complete pre-flight checklist
2. Set speed to minimum test level (10-15)
3. Run behavior for bounded duration (5-10 seconds)
4. Observe and log actual robot motion
5. Verify sensor readings match expected environment
6. Gradually increase speed if behavior is correct
7. Test edge cases in physical environment (close obstacles, sharp turns)

#### COMPOSE
1. Define behavior priority order (highest priority = safety behaviors)
2. Wire behaviors into a behavior tree or priority-based selector
3. Test composed system in static tests first (mocked hardware)
4. Verify that higher-priority behaviors suppress lower-priority ones
5. Run composed system in dynamic test with low speed

#### DEPLOY
1. Set operational speed limits
2. Configure watchdog timeouts for production
3. Enable logging for post-run analysis
4. Monitor first full run with operator present
5. Iterate on tuning parameters (speeds, thresholds, timing)

## State Block Format

Maintain state across conversation turns using this block:

```
<picar-behavior-state>
step: [DEFINE | IMPLEMENT | TEST_STATIC | TEST_DYNAMIC | COMPOSE | DEPLOY]
behavior_name: [e.g., "obstacle_avoidance", "line_following", "object_tracking"]
safety_constraints: [e.g., "max_speed=30, emergency_stop=enabled"]
control_loop_hz: [number, e.g., 20]
last_action: [what was just done]
next_action: [what should happen next]
blockers: [any issues]
</picar-behavior-state>
```

**Example:**

```
<picar-behavior-state>
step: TEST_STATIC
behavior_name: obstacle_avoidance
safety_constraints: max_speed=30, emergency_stop=enabled, min_distance=25cm
control_loop_hz: 20
last_action: Implemented ObstacleAvoidance.update() with ultrasonic threshold logic
next_action: Write pytest tests with mocked ultrasonic sensor
blockers: none
</picar-behavior-state>
```

## Output Templates

### Behavior Definition Report

```markdown
## Behavior: [Name]

**Goal**: [One sentence description]

**Inputs**:
| Sensor | Read Method | Expected Range |
|--------|------------|----------------|
| [sensor] | [method] | [range] |

**Outputs**:
| Actuator | Write Method | Bounded Range |
|----------|-------------|---------------|
| [actuator] | [method] | [range] |

**Safety Constraints**:
- Max speed: [value]
- Servo bounds: [min, max]
- Timeout: [seconds]
- Emergency stop: [trigger condition]

**Control Loop**:
1. Read [sensors]
2. Compute [decision]
3. Write [actuators]
4. Repeat at [Hz]

<picar-behavior-state>
step: DEFINE
behavior_name: [name]
safety_constraints: [constraints]
control_loop_hz: [hz]
last_action: Behavior defined
next_action: Implement behavior class
blockers: none
</picar-behavior-state>
```

### Test Results Report

```markdown
## Test Results: [Behavior Name]

**Test Type**: [Static | Dynamic]
**Date**: [date]

### Static Tests
| Test | Description | Result |
|------|-------------|--------|
| [test_name] | [what it checks] | PASS/FAIL |

### Dynamic Tests (if applicable)
| Test | Environment | Speed | Duration | Result | Notes |
|------|-------------|-------|----------|--------|-------|
| [test_name] | [description] | [value] | [seconds] | PASS/FAIL | [observations] |

**Safety Verification**:
- [ ] Emergency stop triggered correctly
- [ ] Speed limits respected
- [ ] Servo bounds enforced
- [ ] Timeout watchdog fired on stall

<picar-behavior-state>
step: [TEST_STATIC | TEST_DYNAMIC]
behavior_name: [name]
safety_constraints: [constraints]
control_loop_hz: [hz]
last_action: [tests completed]
next_action: [proceed to next step or fix failures]
blockers: [any test failures]
</picar-behavior-state>
```

## AI Discipline Rules

### CRITICAL: Always Implement Emergency Stop First

Before writing ANY behavior logic:
1. Verify the `EmergencyStop` behavior exists and is tested
2. Verify it is wired as the highest-priority behavior in any composition
3. Verify it triggers on: keyboard interrupt, sensor timeout, communication loss, speed limit exceeded
4. If emergency stop is missing or untested, STOP and build it first

No robot behavior is safe without a verified emergency stop.

### CRITICAL: Never Deploy Untested Motor Commands

Before sending ANY command to real motors or servos:
1. The behavior MUST have passing static tests with mocked hardware
2. The specific command sequence MUST appear in a test case
3. Speed values MUST be verified against safety limits in tests
4. Servo angles MUST be verified against calibrated range in tests

If static tests do not cover the command, DO NOT run it on hardware.

### CRITICAL: Test at Low Speed Before High Speed

When moving from static to dynamic testing:
1. First dynamic test MUST use speed <= 15 (out of 100)
2. Increase speed in increments of 10 only after clean runs
3. Never jump from static testing directly to operational speed
4. Document the speed at which each test was performed

Untested speed levels are forbidden in production.

### CRITICAL: Validate Sensor Readings Before Acting

Before using ANY sensor reading to make a control decision:
1. Check that the reading is within the sensor's valid range
2. Check that the reading is not stale (timestamp or poll freshness)
3. If reading is out of range or stale, trigger graceful degradation (slow down or stop)
4. Never act on a single anomalous reading -- use filtering or require N consecutive readings

Garbage-in-garbage-out kills robots. Validate first.

## Common Anti-Patterns to Avoid

| Anti-Pattern | Why It's Dangerous | Correct Approach |
|--------------|--------------------|------------------|
| Monolithic control loop | Untestable, fragile, cannot compose | Break into isolated behaviors with single responsibility |
| Set-and-forget motor commands | Robot runs away if control loop crashes | Use watchdog timeouts; motors stop if not refreshed |
| Raw sensor values in decisions | Noise causes erratic behavior | Apply filtering (moving average, median) before thresholds |
| Testing only on hardware | Slow iteration, risk of damage | Static tests with mocks first; hardware tests second |
| Shared mutable state between behaviors | Race conditions, unpredictable priority | Each behavior gets immutable sensor snapshot, produces commands |
| No speed ramp on startup | Sudden motion, wheel slip, mechanical stress | Ramp speed gradually over 0.5-1 second |
| Hardcoded calibration values | Different robots have different offsets | Load calibration from config file; provide calibration routine |
| Camera processing in control loop | Blocks the sense-act loop, drops control Hz | Run vision in separate thread/process; read latest result |

## Error Recovery

### Motor Stall Detected

```
Problem: Motor current draw spikes or robot is not moving despite speed > 0
Actions:
1. Immediately set speed to 0
2. Wait 1 second
3. Check ultrasonic for obstacle at contact distance (<5cm)
4. If obstacle: back up slowly, then re-plan
5. If no obstacle: possible mechanical jam -- stop and alert operator
6. Log the stall event with sensor snapshot
```

### Sensor Failure Mid-Behavior

```
Problem: Ultrasonic returns -1 or out-of-range, grayscale returns all zeros
Actions:
1. Mark sensor as unreliable in behavior state
2. Reduce speed to minimum (10)
3. If ultrasonic failed: stop forward motion, rely on other sensors or stop
4. If grayscale failed: abandon line following, switch to obstacle avoidance or stop
5. Log the failure with timestamp and last known good reading
6. Do NOT continue at full speed with degraded sensing
```

### Behavior Conflict in Composition

```
Problem: Two behaviors issue contradictory commands (e.g., turn left vs turn right)
Actions:
1. Priority system resolves: highest priority behavior wins
2. If same priority: stop and log the conflict
3. Review behavior conditions -- they should be mutually exclusive at same priority
4. Add guard conditions to prevent simultaneous activation
5. Re-test the composed system with the conflict scenario
```

### Runaway Robot

```
Problem: Robot moving unexpectedly or not responding to stop commands
Actions:
1. Physical intervention: pick up the robot or block its path
2. Kill the Python process (Ctrl+C or kill signal)
3. If software stop fails: disconnect battery
4. Post-mortem: check watchdog configuration, verify emergency stop wiring
5. Add the failure scenario to test suite before re-running
6. Never re-run without understanding why the runaway occurred
```

### Communication Loss (SSH/WiFi Drop)

```
Problem: Lost connection to Raspberry Pi during dynamic test
Actions:
1. Watchdog timeout MUST trigger automatic stop (this is why watchdogs exist)
2. If watchdog was not configured: physically stop the robot
3. Reconnect and check logs for what happened after disconnect
4. Verify watchdog timeout is set to <= 2 seconds for all future runs
5. Consider running critical behaviors locally on the Pi, not over network
```

## Integration with Other Skills

- **`sensor-integration`** -- Use for building and calibrating sensor pipelines (ultrasonic filtering, grayscale normalization, camera capture). Feed processed sensor data into Picar-X behaviors.
- **`edge-cv-pipeline`** -- Use for building computer vision pipelines (object detection, lane detection, sign recognition) that run on the Raspberry Pi. Vision behaviors consume CV pipeline outputs.
- **`tdd-cycle`** / **`tdd-agent`** -- Apply TDD discipline when implementing behavior classes. Write failing tests for sensor-to-actuator logic before implementing the behavior. Especially valuable for static tests with mocked hardware.
- **`jetson-deploy`** -- If offloading heavy CV inference to a Jetson device, use this skill for deployment. The Picar-X communicates with the Jetson over the network for inference results.
