---
name: sensor-integration
description: Build sensor data pipelines with I2C, SPI, UART, and GPIO protocols. Use when integrating sensors with Raspberry Pi, Jetson, or other SBCs for data collection, calibration, and anomaly detection.
---

# Sensor Integration Pipeline

> "In embedded systems, the sensor is the source of truth. If you don't trust your sensor, you don't trust your system."
> -- Jack Ganssle, The Art of Designing Embedded Systems

## Core Philosophy

This skill coordinates the full lifecycle of sensor integration: from physical wiring and protocol configuration through calibration, validation, and data publishing. Sensors produce raw analog or digital signals that must be treated with skepticism until proven reliable.

**Non-Negotiable Constraints:**
1. **Calibrate before trusting** -- raw sensor data is meaningless without a known reference frame. Never ship uncalibrated readings to downstream consumers.
2. **Validate data at the source** -- reject impossible values at the driver layer, not in the application. A temperature sensor reading -459.68 F (below absolute zero) is a fault, not a data point.
3. **Handle sensor failure gracefully** -- sensors fail, wires disconnect, buses lock up. Every read operation must have a timeout, a retry policy, and a fallback behavior.
4. **Respect the electrical domain** -- software cannot fix wiring errors. Verify voltage levels, pull-up resistors, and pin assignments before writing a single line of code.
5. **Log everything, trust nothing** -- every calibration event, anomaly, and bus error must be recorded with timestamps. Silent failures are the enemy of reliable embedded systems.

## Domain Principles Table

| Principle | Description | Priority |
|-----------|-------------|----------|
| **Data Integrity** | Every reading must include timestamp, sensor ID, and validity flag | Critical |
| **Calibration First** | No sensor enters production without a documented calibration procedure | Critical |
| **Protocol Selection** | Choose the simplest protocol that meets bandwidth and latency requirements | High |
| **Sample Rate Management** | Match sample rate to the physical phenomenon; oversampling wastes resources, undersampling loses data | High |
| **Fault Tolerance** | Every sensor read must handle timeout, CRC error, and bus conflict | Critical |
| **Wiring Verification** | Confirm physical connections before software debugging | Critical |
| **Power Budget** | Account for sensor current draw, especially on battery-powered systems | High |
| **Noise Reduction** | Apply hardware filtering (decoupling caps) before software filtering | Medium |
| **Reproducibility** | Same hardware + same code = same readings within tolerance | High |
| **Documentation** | Every sensor integration must include wiring diagram, calibration data, and protocol configuration | Medium |

## Workflow

### Pipeline State Machine

```
┌────────────────────────────────────────────────────────────────────────┐
│                                                                        │
│  ┌──────────┐    ┌─────────┐    ┌───────────┐    ┌───────────┐        │
│  │ IDENTIFY │───>│ CONNECT │───>│ CONFIGURE │───>│ CALIBRATE │──┐     │
│  └──────────┘    └─────────┘    └───────────┘    └───────────┘  │     │
│                                                                  │     │
│       ┌──────────────────────────────────────────────────────────┘     │
│       │                                                                │
│       v                                                                │
│  ┌──────────┐    ┌─────────┐                                          │
│  │ VALIDATE │───>│ PUBLISH │──────────────────────────────────────┐    │
│  └──────────┘    └─────────┘                                     │    │
│       ^                                                          │    │
│       └──────────────────────────────────────────────────────────┘    │
│                        (continuous monitoring loop)                    │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

### Pre-Flight Checklist

Before writing any sensor code, verify:

```
┌─────────────────────────────────────────────────────────┐
│ Pre-Flight Checklist                                    │
├─────────────────────────────────────────────────────────┤
│ □ Sensor datasheet downloaded and reviewed              │
│ □ Operating voltage confirmed (3.3V vs 5V)              │
│ □ Protocol identified (I2C / SPI / UART / GPIO)         │
│ □ Pin assignments documented                            │
│ □ Pull-up / pull-down resistors installed if needed      │
│ □ Decoupling capacitor placed near sensor VCC            │
│ □ I2C address confirmed (no conflicts on bus)            │
│ □ Python libraries installed (smbus2 / spidev / etc.)   │
│ □ User has permission to access /dev/ devices            │
│ □ Test harness ready (known reference values available)  │
└─────────────────────────────────────────────────────────┘
```

### Protocol Selection Decision Tree

```
                    ┌─────────────────────┐
                    │ How many sensors on  │
                    │ the same bus?        │
                    └────────┬────────────┘
                             │
              ┌──────────────┴──────────────┐
              │                             │
         1 sensor                     2+ sensors
              │                             │
              v                             v
    ┌─────────────────┐         ┌──────────────────┐
    │ Need high speed  │         │ Each sensor has   │
    │ (>1 MHz)?        │         │ unique address?   │
    └───────┬─────────┘         └────────┬─────────┘
            │                            │
     ┌──────┴──────┐             ┌───────┴──────┐
     │             │             │              │
    Yes           No            Yes            No
     │             │             │              │
     v             v             v              v
  ┌─────┐    ┌─────────┐    ┌─────┐      ┌─────┐
  │ SPI │    │ Simple   │    │ I2C │      │ SPI │
  └─────┘    │ digital? │    └─────┘      │(CS) │
             └────┬────┘                  └─────┘
              ┌───┴───┐
              │       │
             Yes     No
              │       │
              v       v
          ┌──────┐ ┌──────┐
          │ GPIO │ │ UART │
          └──────┘ └──────┘
```

**Quick Protocol Summary:**

| Protocol | Speed | Wires | Multi-Device | Best For |
|----------|-------|-------|-------------|----------|
| I2C | 100-400 kHz (std) | 2 (SDA, SCL) | Yes (addressing) | Low-speed sensors, config registers |
| SPI | 1-50 MHz | 4+ (MOSI, MISO, SCLK, CS) | Yes (chip select) | High-speed, ADCs, displays |
| UART | 9600-115200 baud | 2 (TX, RX) | No (point-to-point) | GPS, serial sensors |
| GPIO | N/A | 1 per signal | No | Digital on/off, triggers, PWM |

### Step-by-Step Workflow

#### Step 1: IDENTIFY

Determine sensor type, part number, protocol, operating voltage, and required libraries.

```python
# Document sensor identity
sensor_manifest = {
    "name": "BME280",
    "type": "Environmental",
    "measures": ["temperature", "humidity", "pressure"],
    "protocol": "i2c",
    "address": 0x76,  # or 0x77 with SDO high
    "voltage": 3.3,
    "library": "adafruit-circuitpython-bme280",
    "datasheet": "https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bme280-ds002.pdf",
}
```

#### Step 2: CONNECT

Wire the sensor. Verify physical connections.

```python
# Verify I2C device is detected
import subprocess

def scan_i2c_bus(bus_number: int = 1) -> list[int]:
    """Scan I2C bus and return list of detected addresses."""
    import smbus2
    bus = smbus2.SMBus(bus_number)
    devices = []
    for addr in range(0x03, 0x78):
        try:
            bus.read_byte(addr)
            devices.append(addr)
        except OSError:
            pass
    bus.close()
    return devices

detected = scan_i2c_bus()
assert 0x76 in detected, f"BME280 not found! Detected: {[hex(a) for a in detected]}"
```

#### Step 3: CONFIGURE

Set sample rate, resolution, filtering, and operating mode.

```python
import adafruit_bme280.advanced as adafruit_bme280
import board
import busio

i2c = busio.I2C(board.SCL, board.SDA)
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=0x76)

# Configure oversampling and filter
bme280.overscan_temperature = adafruit_bme280.OVERSCAN_X16
bme280.overscan_humidity = adafruit_bme280.OVERSCAN_X16
bme280.overscan_pressure = adafruit_bme280.OVERSCAN_X16
bme280.iir_filter = adafruit_bme280.IIR_FILTER_X16
bme280.mode = adafruit_bme280.MODE_NORMAL
bme280.standby_period = adafruit_bme280.STANDBY_TC_500
```

#### Step 4: CALIBRATE

Compare sensor readings against known reference values and compute correction factors.

```python
import numpy as np

def calibrate_temperature(sensor_readings: list[float],
                          reference_readings: list[float]) -> tuple[float, float]:
    """Two-point linear calibration. Returns (offset, gain)."""
    sensor_arr = np.array(sensor_readings)
    ref_arr = np.array(reference_readings)
    gain, offset = np.polyfit(sensor_arr, ref_arr, 1)
    return offset, gain

# Example: ice water (0C) and boiling water (100C)
raw_readings = [1.2, 99.5]
reference = [0.0, 100.0]
offset, gain = calibrate_temperature(raw_readings, reference)
print(f"Calibration: corrected = {gain:.4f} * raw + {offset:.4f}")
```

#### Step 5: VALIDATE

Run the sensor under controlled conditions and verify readings fall within expected tolerance.

```python
import time

def validate_sensor(sensor, calibration, tolerance: float = 0.5,
                    num_samples: int = 100) -> dict:
    """Collect samples and validate statistical properties."""
    readings = []
    for _ in range(num_samples):
        raw = sensor.temperature
        corrected = calibration["gain"] * raw + calibration["offset"]
        readings.append(corrected)
        time.sleep(0.1)

    arr = np.array(readings)
    return {
        "mean": float(np.mean(arr)),
        "std": float(np.std(arr)),
        "min": float(np.min(arr)),
        "max": float(np.max(arr)),
        "range_ok": bool(np.std(arr) < tolerance),
        "num_samples": num_samples,
    }
```

#### Step 6: PUBLISH

Push validated data to downstream consumers (MQTT, database, file, etc.).

```python
import json
import time

def publish_reading(sensor_id: str, value: float, unit: str,
                    calibrated: bool = True) -> dict:
    """Format a sensor reading for downstream consumption."""
    return {
        "sensor_id": sensor_id,
        "timestamp": time.time(),
        "value": round(value, 4),
        "unit": unit,
        "calibrated": calibrated,
        "quality": "valid",
    }

reading = publish_reading("bme280-01", 22.35, "celsius")
print(json.dumps(reading, indent=2))
```

## State Block Format

Maintain state across conversation turns using this block:

```
<sensor-state>
step: [IDENTIFY | CONNECT | CONFIGURE | CALIBRATE | VALIDATE | PUBLISH]
sensor_type: [e.g., "IMU", "LiDAR", "Ultrasonic", "Camera", "Temperature"]
protocol: [i2c | spi | uart | gpio]
calibrated: [true | false]
sample_rate_hz: [number]
last_action: [what was just done]
next_action: [what should happen next]
blockers: [any issues]
</sensor-state>
```

**Example:**

```
<sensor-state>
step: CALIBRATE
sensor_type: Environmental (BME280)
protocol: i2c
calibrated: false
sample_rate_hz: 2
last_action: Configured oversampling and IIR filter
next_action: Run two-point temperature calibration against reference thermometer
blockers: Need reference thermometer readings at 0C and 25C
</sensor-state>
```

## Output Templates

### Sensor Setup Report

```markdown
## Sensor Setup: [Sensor Name]

**Hardware:**
- Part: [part number]
- Protocol: [I2C / SPI / UART / GPIO]
- Address / CS Pin: [value]
- Operating Voltage: [3.3V / 5V]
- Wiring: [pin mapping]

**Software:**
- Library: [pip package name]
- Install: `pip install [package]`
- Bus: [/dev/i2c-1, /dev/spidev0.0, /dev/ttyUSB0, etc.]

**Configuration:**
- Sample Rate: [Hz]
- Resolution: [bits]
- Filter: [type and setting]
- Operating Mode: [normal / forced / sleep]

<sensor-state>
step: CONFIGURE
sensor_type: [type]
protocol: [protocol]
calibrated: false
sample_rate_hz: [rate]
last_action: Hardware configured and verified
next_action: Begin calibration procedure
blockers: none
</sensor-state>
```

### Calibration Report

```markdown
## Calibration Report: [Sensor Name]

**Date:** [ISO 8601]
**Technician / Agent:** [name]

**Reference Standard:** [instrument name, last cal date]

**Calibration Points:**

| Reference Value | Raw Reading | Corrected Reading | Error |
|----------------|-------------|-------------------|-------|
| [val] | [val] | [val] | [val] |

**Calibration Coefficients:**
- Offset: [value]
- Gain: [value]
- R-squared: [value]

**Pass / Fail:** [PASS if all errors within tolerance]

<sensor-state>
step: VALIDATE
sensor_type: [type]
protocol: [protocol]
calibrated: true
sample_rate_hz: [rate]
last_action: Calibration complete, coefficients stored
next_action: Run validation suite under controlled conditions
blockers: none
</sensor-state>
```

## AI Discipline Rules

### CRITICAL: Always Verify Physical Wiring Before Software

Before writing driver code or debugging software issues:
1. Confirm the sensor is powered (measure VCC with multimeter)
2. Confirm the correct I2C/SPI/UART bus is being accessed
3. Confirm pull-up resistors are present for I2C (4.7k ohm typical)
4. Confirm pin assignments match the code

If the sensor is not detected on the bus, **it is a wiring problem until proven otherwise**. Do NOT attempt software workarounds for hardware issues.

### CRITICAL: Calibrate Before Collecting Production Data

Raw sensor readings have manufacturing offsets and gain errors. Before any data is treated as "real":
1. Define calibration reference points
2. Collect raw readings at reference points
3. Compute correction coefficients
4. Validate corrected readings against reference
5. Store calibration coefficients with sensor metadata

Shipping uncalibrated data is equivalent to shipping broken code.

### CRITICAL: Handle I2C Bus Conflicts

I2C is a shared bus. Multiple devices can conflict:
1. Always scan the bus before adding a new device
2. Check for address collisions (many sensors use 0x68, 0x76, etc.)
3. Use address selection pins (A0, A1) to resolve conflicts
4. If conflicts cannot be resolved, use an I2C multiplexer (TCA9548A)
5. Never assume a device is the only one on the bus

```python
def check_address_conflict(bus_number: int, expected_addr: int) -> bool:
    """Check if the expected address is already occupied."""
    import smbus2
    bus = smbus2.SMBus(bus_number)
    try:
        bus.read_byte(expected_addr)
        return True  # Device responded -- may be a conflict
    except OSError:
        return False  # Address free
    finally:
        bus.close()
```

### CRITICAL: Never Ignore Anomalous Readings

When a sensor returns unexpected values:
1. **Log the anomaly** with full context (timestamp, raw value, expected range)
2. **Do not silently clamp or discard** -- downstream consumers must know data quality degraded
3. **Check the physical environment** -- the "anomaly" might be real
4. **Check bus health** -- corrupted reads often indicate wiring or timing issues
5. **Increment an anomaly counter** -- patterns of anomalies indicate systemic problems

```python
import logging

logger = logging.getLogger("sensor")

def read_with_validation(sensor, min_valid: float, max_valid: float,
                         sensor_id: str) -> dict:
    """Read sensor with range validation and anomaly logging."""
    raw = sensor.read()
    if raw < min_valid or raw > max_valid:
        logger.warning(
            "Anomalous reading from %s: %.4f (valid range: %.1f to %.1f)",
            sensor_id, raw, min_valid, max_valid,
        )
        return {"value": raw, "quality": "anomalous", "sensor_id": sensor_id}
    return {"value": raw, "quality": "valid", "sensor_id": sensor_id}
```

## Anti-Patterns Table

| Anti-Pattern | Why It Fails | Correct Approach |
|--------------|-------------|------------------|
| Reading sensors without calibration | Raw values have unknown offset and gain errors | Always calibrate against a known reference before trusting data |
| Using `RPi.GPIO` for new projects | Deprecated, requires root, not portable across SBCs | Use `gpiod` (libgpiod) for modern, portable GPIO access |
| Ignoring I2C NAK errors | A NAK means the device did not respond; masking it hides wiring faults | Retry with backoff, then fail loudly if device is unresponsive |
| Polling sensors in a tight loop | Wastes CPU, may exceed sensor conversion time, causes self-heating | Use timers or `time.sleep()` matched to sensor sample rate |
| Hardcoding calibration coefficients | Calibration drifts over time and varies per unit | Store coefficients in config files, re-calibrate periodically |
| No timeout on bus reads | A stuck bus will hang the entire application | Always set a timeout; use `smbus2` with `force=False` and wrap in try/except |
| Sharing SPI bus without chip select management | Data corruption when multiple devices respond simultaneously | Assert CS low only for the active device; release immediately after transaction |
| Treating all sensor data as equally valid | Startup transients, out-of-range values, and CRC failures are not valid data | Tag every reading with a quality flag: valid, suspect, anomalous, error |

## Error Recovery

### Bus Conflict (I2C)

```
Problem: Multiple devices responding on the same I2C address
Symptoms: Corrupted reads, inconsistent data, OSError on read/write

Actions:
1. Run i2cdetect to list all devices: i2cdetect -y 1
2. Identify conflicting addresses
3. Use address selection pins to reassign one device
4. If not possible, install TCA9548A I2C multiplexer
5. Re-scan bus to verify conflict is resolved
6. Test each device independently before resuming pipeline
```

### Timing Issues (SPI)

```
Problem: Corrupted data on SPI bus
Symptoms: CRC failures, bit-shifted data, inconsistent reads

Actions:
1. Reduce SPI clock speed (start at 100 kHz, increase gradually)
2. Verify CPOL and CPHA mode match the sensor datasheet
3. Check wire length (keep SPI wires under 15 cm)
4. Add 100nF decoupling cap near sensor VCC pin
5. Verify chip select timing (CS must be asserted before clock)
6. Use a logic analyzer to inspect actual waveforms
```

### Noisy Readings

```
Problem: Sensor readings fluctuate excessively
Symptoms: High standard deviation, readings outside expected range

Actions:
1. Check power supply -- use a dedicated LDO regulator if possible
2. Add hardware filtering (100nF ceramic cap on VCC, 10uF bulk cap)
3. Apply software moving average filter (window of 5-20 samples)
4. Increase oversampling in sensor configuration
5. Check for ground loops if using long wires
6. Shield signal wires from motor or relay noise sources
```

### Sensor Not Responding

```
Problem: Sensor not detected on bus
Symptoms: OSError, empty i2cdetect scan, no response on UART

Actions:
1. Verify power: measure VCC at the sensor pin (not at the board header)
2. Verify ground: ensure common ground between sensor and SBC
3. Check wiring: SDA to SDA, SCL to SCL (not crossed)
4. Verify pull-ups: 4.7k ohm on SDA and SCL for I2C
5. Check voltage levels: 3.3V sensor on 3.3V bus (NOT 5V)
6. Try a different I2C bus or GPIO pin
7. Test the sensor on a breadboard with a known-good setup
8. If all else fails, the sensor may be damaged -- try a replacement
```

### UART Framing Errors

```
Problem: Garbled data from UART sensor
Symptoms: Unexpected bytes, partial packets, checksum failures

Actions:
1. Verify baud rate matches sensor datasheet exactly
2. Check data format: 8N1 is most common (8 data, no parity, 1 stop)
3. Ensure TX/RX are not swapped (sensor TX -> SBC RX)
4. Add a small delay between consecutive reads
5. Implement packet framing with start/end markers
6. Use a USB-to-serial adapter for debugging with a terminal emulator
```

## Integration with Other Skills

- **`picar-x-behavior`** -- PiCar-X uses ultrasonic, line-following, and camera sensors. Use this skill to calibrate distance readings, validate line sensor thresholds, and handle sensor dropout during autonomous navigation.
- **`edge-cv-pipeline`** -- Camera modules (Pi Camera, OAK-D, USB cameras) are sensors too. Use this skill for camera initialization, frame rate management, and handling camera disconnection or frame corruption.
- **`jetson-deploy`** -- Jetson boards have specific I2C bus mappings and GPIO pin numbering. Use this skill alongside `jetson-deploy` to configure sensor buses on Jetson Nano, Xavier NX, and Orin platforms, and to manage sensor data pipelines within containerized deployments.
