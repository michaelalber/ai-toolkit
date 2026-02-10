---
name: anomaly-detection
description: Statistical anomaly detection for sensor data streams. Use when implementing outlier detection, drift monitoring, anomaly classification, and alert/recalibration decision trees for time-series sensor data.
---

# Anomaly Detection for Sensor Data

> "The goal is not to eliminate anomalies. The goal is to understand them faster than they can cause harm."
> -- W. Edwards Deming (paraphrased)

## Core Philosophy

This skill provides the statistical methods, drift detection algorithms, and decision frameworks needed to detect, classify, and respond to anomalies in sensor data streams. It assumes sensor data arrives as a time series of numeric readings with associated timestamps.

**Non-Negotiable Constraints:**
1. **Baseline first** -- no detection algorithm produces meaningful results without a valid baseline for comparison.
2. **Multiple methods** -- never rely on a single statistical test. Use at least two independent methods for consensus before classifying an anomaly.
3. **Context matters** -- a reading that is anomalous for one sensor may be normal for another. Detection thresholds must be tuned per sensor and environment.
4. **Log everything** -- every anomaly event, every threshold crossing, every suppression decision must be recorded with full context.
5. **Distinguish fault from signal** -- a sensor reporting an unusual value may be broken, or the environment may have genuinely changed. The detection system must help discriminate between these cases.

## Domain Principles Table

| Principle | Description | Priority |
|-----------|-------------|----------|
| **Baseline Validity** | Detection thresholds are only meaningful relative to a valid, stable baseline | Critical |
| **Statistical Consensus** | Multiple independent methods must agree before declaring an anomaly | Critical |
| **Temporal Context** | A single outlier is less significant than a sustained deviation | High |
| **Physical Plausibility** | Anomaly classification must consider what is physically possible for the sensor | Critical |
| **Adaptive Thresholds** | Static thresholds fail as sensor behavior drifts; thresholds must adapt | High |
| **Alert Hygiene** | Too many false positives cause alert fatigue; too few false negatives miss real events | High |
| **Drift Awareness** | Gradual drift is harder to detect than spikes but often more consequential | High |
| **Recalibration Discipline** | Recalibration is an invasive action that requires evidence and approval | Critical |

## Workflow

### Anomaly Detection Pipeline

```
┌──────────────────────────────────────────────────────────────────────────┐
│                                                                          │
│  ┌──────────┐    ┌─────────┐    ┌────────┐    ┌──────────┐    ┌───────┐ │
│  │ BASELINE │───>│ MONITOR │───>│ DETECT │───>│ CLASSIFY │───>│RESPOND│ │
│  └──────────┘    └─────────┘    └────────┘    └──────────┘    └───────┘ │
│       │               ^              │                            │      │
│       │               │              │                            │      │
│       │               └──────────────┘                            │      │
│       │                (no anomaly)                               │      │
│       │                                                           │      │
│       └───────────────────────────────────────────────────────────┘      │
│                        (re-baseline after drift correction)              │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

### Detection Method Selection Guide

```
                     ┌──────────────────────────┐
                     │ What kind of anomaly are  │
                     │ you looking for?          │
                     └────────────┬─────────────┘
                                  │
              ┌───────────────────┼───────────────────┐
              │                   │                   │
         Point outliers     Gradual drift        Distribution
              │                   │               change
              v                   v                   v
       ┌────────────┐    ┌──────────────┐    ┌──────────────┐
       │ Z-score     │    │ CUSUM        │    │ ADWIN        │
       │ IQR         │    │ Page-Hinkley │    │ Kolmogorov-  │
       │ Grubbs test │    │ EWMA drift   │    │ Smirnov      │
       └────────────┘    └──────────────┘    └──────────────┘
```

### Anomaly Type Decision Tree

```
        ┌─────────────────────────────────────────┐
        │ Anomalous reading detected               │
        └───────────────────┬─────────────────────┘
                            │
              ┌─────────────┴──────────────┐
              │                            │
        Single reading              Multiple readings
              │                            │
              v                            v
    ┌─────────────────┐        ┌─────────────────────┐
    │ Return to normal │        │ What is the pattern? │
    │ within 1-3       │        └──────────┬──────────┘
    │ readings?        │                   │
    └────────┬────────┘        ┌───────────┼───────────┐
             │                 │           │           │
            Yes              Trend      Constant    Erratic
             │                 │           │           │
             v                 v           v           v
         ┌───────┐       ┌───────┐   ┌──────────┐ ┌───────┐
         │ SPIKE │       │ DRIFT │   │ FLATLINE │ │ NOISE │
         └───────┘       └───────┘   └──────────┘ └───────┘
```

## Step-by-Step Workflow

### Step 1: Establish Baseline

Collect a representative sample of normal sensor operation and compute reference statistics.

```python
import numpy as np
from scipy import stats


def establish_baseline(readings: list[float],
                       min_samples: int = 100) -> dict:
    """
    Compute baseline statistics from a sample of normal sensor readings.

    Args:
        readings: List of sensor readings during known-normal operation.
        min_samples: Minimum number of samples required.

    Returns:
        Dict with baseline statistics and quality metrics.

    Raises:
        ValueError: If insufficient samples provided.
    """
    if len(readings) < min_samples:
        raise ValueError(
            f"Need >= {min_samples} samples, got {len(readings)}"
        )

    arr = np.array(readings)
    q1, q3 = np.percentile(arr, [25, 75])
    iqr = q3 - q1

    # Stationarity check: split in half and compare means
    mid = len(arr) // 2
    first_half_mean = np.mean(arr[:mid])
    second_half_mean = np.mean(arr[mid:])
    mean_drift = abs(second_half_mean - first_half_mean) / np.std(arr)

    # Normality check
    if len(arr) <= 5000:
        _, normality_p = stats.shapiro(arr[:min(len(arr), 5000)])
    else:
        _, normality_p = stats.normaltest(arr)

    return {
        "mean": float(np.mean(arr)),
        "std": float(np.std(arr)),
        "median": float(np.median(arr)),
        "min": float(np.min(arr)),
        "max": float(np.max(arr)),
        "q1": float(q1),
        "q3": float(q3),
        "iqr": float(iqr),
        "count": len(arr),
        "is_normal": bool(normality_p > 0.05),
        "normality_p": float(normality_p),
        "is_stationary": bool(mean_drift < 0.5),
        "mean_drift_sigma": float(mean_drift),
    }
```

### Step 2: Configure Detection Methods

Select and configure detection methods based on the baseline characteristics and the types of anomalies you need to detect.

```python
def configure_detectors(baseline: dict) -> dict:
    """
    Configure detection thresholds based on baseline statistics.

    Returns configuration for z-score, IQR, and EWMA detectors.
    """
    config = {
        "zscore": {
            "enabled": baseline["is_normal"],
            "threshold": 3.0,
            "mean": baseline["mean"],
            "std": baseline["std"],
        },
        "iqr": {
            "enabled": True,  # Works for any distribution
            "factor": 1.5,
            "q1": baseline["q1"],
            "q3": baseline["q3"],
            "iqr": baseline["iqr"],
            "lower": baseline["q1"] - 1.5 * baseline["iqr"],
            "upper": baseline["q3"] + 1.5 * baseline["iqr"],
        },
        "ewma": {
            "enabled": True,
            "alpha": 0.3,
            "sigma_threshold": 3.0,
            "initial_mean": baseline["mean"],
        },
        "cusum": {
            "enabled": True,
            "target": baseline["mean"],
            "threshold": 5.0 * baseline["std"],
            "drift_allowance": 0.5 * baseline["std"],
        },
    }
    return config
```

### Step 3: Run Detection

Process incoming readings through the detection pipeline.

```python
def detect_anomaly(value: float, config: dict) -> dict:
    """
    Run a single reading through all configured detectors.

    Returns detection results from each method plus a consensus verdict.
    """
    results = {}
    votes_anomaly = 0
    votes_total = 0

    # Z-score detection
    if config["zscore"]["enabled"]:
        z = abs(value - config["zscore"]["mean"]) / config["zscore"]["std"]
        is_anomaly = z > config["zscore"]["threshold"]
        results["zscore"] = {
            "z_score": float(z),
            "is_anomaly": is_anomaly,
        }
        votes_total += 1
        if is_anomaly:
            votes_anomaly += 1

    # IQR detection
    if config["iqr"]["enabled"]:
        below = value < config["iqr"]["lower"]
        above = value > config["iqr"]["upper"]
        is_anomaly = below or above
        results["iqr"] = {
            "is_anomaly": is_anomaly,
            "bound_violated": "lower" if below else ("upper" if above else "none"),
        }
        votes_total += 1
        if is_anomaly:
            votes_anomaly += 1

    # Consensus
    consensus = votes_anomaly >= max(1, votes_total // 2 + 1)
    results["consensus"] = {
        "is_anomaly": consensus,
        "votes_anomaly": votes_anomaly,
        "votes_total": votes_total,
        "agreement_ratio": votes_anomaly / votes_total if votes_total > 0 else 0,
    }

    return results
```

### Step 4: Classify Anomaly

Determine the anomaly type based on the temporal pattern.

```python
def classify_anomaly(recent_anomalies: list[dict],
                     baseline: dict,
                     window_readings: list[float]) -> dict:
    """
    Classify the anomaly type based on recent detection history.

    Args:
        recent_anomalies: List of recent anomaly detection records.
        baseline: Baseline statistics dictionary.
        window_readings: Recent sliding window of readings.

    Returns:
        Classification with type, severity, and evidence.
    """
    arr = np.array(window_readings)
    current_mean = np.mean(arr)
    current_std = np.std(arr)
    unique_values = len(set(window_readings[-10:]))

    # Flatline detection: very low variance or identical values
    if unique_values <= 2 and len(window_readings) >= 10:
        return {
            "type": "FLATLINE",
            "severity": "CRITICAL",
            "evidence": f"Only {unique_values} unique values in last 10 readings",
        }

    # Drift detection: sustained shift in mean
    drift_sigma = abs(current_mean - baseline["mean"]) / baseline["std"]
    if drift_sigma > 2.0 and len(recent_anomalies) >= 5:
        severity = "CRITICAL" if drift_sigma > 4.0 else "WARNING"
        return {
            "type": "DRIFT",
            "severity": severity,
            "evidence": f"Mean shifted {drift_sigma:.1f} sigma from baseline",
            "drift_magnitude": float(drift_sigma),
        }

    # Noise detection: increased variance
    noise_ratio = current_std / baseline["std"] if baseline["std"] > 0 else 0
    if noise_ratio > 2.0:
        severity = "CRITICAL" if noise_ratio > 4.0 else "WARNING"
        return {
            "type": "NOISE",
            "severity": severity,
            "evidence": f"Noise level {noise_ratio:.1f}x baseline",
        }

    # Spike detection: isolated outlier(s)
    if len(recent_anomalies) <= 3:
        return {
            "type": "SPIKE",
            "severity": "INFO" if len(recent_anomalies) == 1 else "WARNING",
            "evidence": f"{len(recent_anomalies)} spike(s) detected",
        }

    return {
        "type": "SPIKE",
        "severity": "WARNING",
        "evidence": "Recurring spikes detected, investigate root cause",
    }
```

### Step 5: Respond

Execute the appropriate response based on classification.

```python
import logging
import time

logger = logging.getLogger("anomaly.response")


def respond_to_anomaly(classification: dict, sensor_id: str,
                       value: float, baseline: dict) -> dict:
    """
    Execute the appropriate response for a classified anomaly.

    Returns response record for logging.
    """
    response = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "sensor_id": sensor_id,
        "anomaly_type": classification["type"],
        "severity": classification["severity"],
        "value": value,
        "baseline_mean": baseline["mean"],
        "baseline_std": baseline["std"],
        "evidence": classification["evidence"],
        "actions_taken": [],
    }

    severity = classification["severity"]

    # Always log
    response["actions_taken"].append("logged")
    logger.info(
        "Anomaly [%s/%s] on %s: value=%.4f, %s",
        classification["type"], severity, sensor_id,
        value, classification["evidence"],
    )

    # Alert for WARNING and above
    if severity in ("WARNING", "CRITICAL", "EMERGENCY"):
        response["actions_taken"].append("alert_sent")
        logger.warning(
            "ALERT [%s] %s: %s", severity, sensor_id,
            classification["evidence"],
        )

    # Recommend recalibration for drift
    if classification["type"] == "DRIFT" and severity in ("CRITICAL", "EMERGENCY"):
        response["actions_taken"].append("recalibration_recommended")
        response["requires_approval"] = True
        logger.warning(
            "RECALIBRATION RECOMMENDED for %s -- awaiting approval",
            sensor_id,
        )

    # Recommend replacement for flatline
    if classification["type"] == "FLATLINE":
        response["actions_taken"].append("replacement_recommended")
        response["requires_approval"] = True

    return response
```

## State Block Format

Maintain state across conversation turns using this block:

```
<anomaly-detection-state>
step: [BASELINE | CONFIGURE | DETECT | CLASSIFY | RESPOND]
sensor_id: [sensor identifier]
baseline_established: [true | false]
detection_methods: [z-score, IQR, EWMA, CUSUM]
anomaly_type: [SPIKE | DRIFT | FLATLINE | NOISE | none]
severity: [INFO | WARNING | CRITICAL | EMERGENCY | none]
readings_processed: [count]
anomalies_detected: [count]
last_action: [what was just done]
next_action: [what should happen next]
blockers: [any issues]
</anomaly-detection-state>
```

## Output Templates

### Anomaly Detection Report

```markdown
## Anomaly Detection Report: [Sensor ID]

**Date**: [ISO 8601]
**Analysis Period**: [start] to [end]
**Readings Analyzed**: [count]

**Baseline**:
- Mean: [value] [unit], Std: [value] [unit]
- Distribution: [normal / skewed]
- Quality: [excellent / acceptable / marginal]

**Anomalies Detected**: [count] ([percentage]% anomaly rate)

| Timestamp | Value | Type | Severity | Action |
|-----------|-------|------|----------|--------|
| [time] | [val] | [type] | [severity] | [action] |

**Summary**:
- Spikes: [count]
- Drift events: [count], magnitude: [sigma]
- Flatline events: [count]
- Noise events: [count]

**Recommendations**:
- [recommendation 1]
- [recommendation 2]
```

## Anti-Patterns Table

| Anti-Pattern | Why It Fails | Correct Approach |
|--------------|-------------|------------------|
| Detecting without a baseline | No reference for what is "normal" -- everything or nothing is anomalous | Always establish baseline before enabling detection |
| Using only z-score | Fails on non-normal distributions, sensitive to outliers in baseline | Combine z-score with IQR and EWMA for robustness |
| Static thresholds forever | Sensor behavior drifts over time; static thresholds accumulate false positives | Use adaptive methods (EWMA, ADWIN) that track evolving normal |
| Alerting on every single outlier | Single-sample spikes are often noise; alerting on each one causes fatigue | Require N consecutive violations or use a debounce window |
| Ignoring flatline as "stable" | A sensor reading the exact same value repeatedly is likely stuck | Monitor unique value count; flatline is always suspicious |
| Auto-recalibrating on drift | Drift may indicate a real environmental change, not sensor error | Require human approval and cross-sensor validation before recalibrating |
| Suppressing repeated alerts silently | Hides escalating problems; repeated anomalies may indicate worsening failure | Log all suppressions with rationale; escalate if pattern persists |
| Using training data with anomalies | Contaminated baseline produces thresholds that miss real anomalies | Curate baseline data carefully; validate stationarity and distribution |

## Integration with Other Skills

- **`sensor-integration`** -- Use for physical sensor setup, protocol configuration, and calibration procedures. Anomaly detection begins after `sensor-integration` has established a calibrated data pipeline.
- **`edge-cv-pipeline`** -- Camera frame drop detection and quality monitoring use similar statistical anomaly detection patterns. The frame rate monitoring in edge-cv-pipeline can leverage the EWMA and drift detection methods from this skill.
- **`jetson-deploy`** -- When deploying anomaly detection models on Jetson hardware, use this skill for the statistical methods and `jetson-deploy` for the containerized deployment pipeline.
