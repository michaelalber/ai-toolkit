---
name: edge-cv-pipeline
description: Build OpenCV + TFLite computer vision pipelines for Jetson and Raspberry Pi. Use when deploying real-time inference on edge devices with camera capture, model optimization, and result publishing.
---

# Edge CV Pipeline Builder

> "In computer vision, the best algorithm is useless if it can't run in real-time on the hardware you have."
> -- Pete Warden, TinyML

## Core Philosophy

This skill builds end-to-end computer vision pipelines for edge devices. The pipeline spans camera capture, preprocessing, inference, postprocessing, and result publishing. **Every decision is constrained by the target hardware.**

**Non-Negotiable Constraints:**
1. **Profile before optimizing** -- measure actual latency on the target device before changing anything. Assumptions about bottlenecks are wrong more often than they are right.
2. **Match resolution to model input** -- never capture at 1080p when the model expects 320x320. Wasted pixels are wasted cycles.
3. **Handle frame drops gracefully** -- edge devices will drop frames under load. The pipeline must degrade without crashing or corrupting state.
4. **Separate capture from inference** -- camera I/O and model inference run at different rates. Decoupling them prevents the slower stage from starving the faster one.
5. **Test on the target device** -- x86 profiling numbers are meaningless for ARM/GPU inference. Always validate on the actual hardware.

## Domain Principles Table

| Principle | Description | Priority |
|-----------|-------------|----------|
| **Latency Budget** | Allocate a per-stage ms budget (capture, preprocess, infer, postprocess, publish) and enforce it | Critical |
| **Resolution Matching** | Capture resolution matches model input dimensions; resize only when unavoidable | Critical |
| **Model Size Awareness** | Track model file size, RAM footprint, and inference time as first-class constraints | Critical |
| **Frame Pipeline Isolation** | Capture thread, inference thread, and publish thread operate independently with queues | High |
| **Thermal Headroom** | Sustained workloads throttle; design for 80% of peak throughput to avoid thermal cliffs | High |
| **Graceful Degradation** | Skip frames, reduce resolution, or switch models rather than crash or hang | High |
| **Format Portability** | Prefer ONNX as interchange format; convert to device-specific formats (TFLite, TensorRT) at deploy time | Medium |
| **Reproducible Capture** | Lock exposure, white balance, and gain for consistent inference inputs across runs | Medium |
| **Observable Pipeline** | Expose FPS, latency, temperature, and memory metrics at all times | Medium |
| **Power Efficiency** | Minimize unnecessary wakeups, batch when possible, sleep between inference cycles for battery-powered deployments | Low |

## Workflow

### Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   ┌─────────┐    ┌────────────┐    ┌───────┐    ┌──────────┐   │
│   │ CAPTURE │───>│ PREPROCESS │───>│ INFER │───>│POSTPROCESS│   │
│   └─────────┘    └────────────┘    └───────┘    └──────────┘   │
│       │                                              │          │
│       │              ┌─────────┐                     │          │
│       └─────────────>│ PUBLISH │<────────────────────┘          │
│                      └─────────┘                                │
│                                                                 │
│   Frame Queue        NumPy Arrays      Detections    MQTT/HTTP  │
│   (threaded)         (resized, norm)   (boxes, cls)  (JSON out) │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Pre-Flight Checklist

Before writing any pipeline code, verify:

```
┌─────────────────────────────────────────────────────────────┐
│ Pre-Flight Checklist                                        │
├─────────────────────────────────────────────────────────────┤
│ [ ] Target device identified (Jetson Orin Nano / RPi 5 / 4)│
│ [ ] Camera module confirmed (CSI / USB / IP stream)         │
│ [ ] Model format selected (TFLite / ONNX / TensorRT)       │
│ [ ] Model input dimensions known (e.g., 320x320x3)         │
│ [ ] FPS target defined (e.g., 15 fps for detection)         │
│ [ ] Output destination defined (MQTT / HTTP / file / display│
│ [ ] Power source confirmed (wall / battery / PoE)           │
│ [ ] Storage budget confirmed (SD card / NVMe / RAM disk)    │
└─────────────────────────────────────────────────────────────┘
```

### Model Format Decision Tree

```
Is target device a Jetson?
├── YES → Does the model need INT8 quantization?
│         ├── YES → TensorRT (use trtexec or torch2trt)
│         └── NO  → TensorRT FP16 (default for Jetson)
└── NO  → Is target device a Raspberry Pi?
          ├── YES → TFLite with XNNPACK delegate
          │         └── Does RPi have Coral TPU attached?
          │               ├── YES → TFLite with Edge TPU delegate
          │               └── NO  → TFLite CPU (ARM NEON)
          └── NO  → Is target an Intel device?
                    ├── YES → OpenVINO IR format
                    └── NO  → ONNX Runtime (portable fallback)
```

### Step-by-Step Workflow

**Step 1: CAPTURE** -- Acquire frames from the camera source.

```python
import cv2
from threading import Thread
from queue import Queue

class FrameCapture:
    def __init__(self, source, queue_size=2):
        self.cap = cv2.VideoCapture(source)
        self.queue = Queue(maxsize=queue_size)
        self.stopped = False

    def start(self):
        Thread(target=self._reader, daemon=True).start()
        return self

    def _reader(self):
        while not self.stopped:
            ret, frame = self.cap.read()
            if not ret:
                self.stopped = True
                break
            if not self.queue.full():
                self.queue.put(frame)
            # Drop frame if queue is full (graceful degradation)

    def read(self):
        return self.queue.get(timeout=5.0)

    def stop(self):
        self.stopped = True
        self.cap.release()
```

**Step 2: PREPROCESS** -- Resize, normalize, format for model input.

```python
import numpy as np

def preprocess_frame(frame, input_size=(320, 320), normalize=True):
    """Resize and normalize frame for model input."""
    resized = cv2.resize(frame, input_size, interpolation=cv2.INTER_LINEAR)
    if normalize:
        input_data = resized.astype(np.float32) / 255.0
    else:
        input_data = resized.astype(np.uint8)
    return np.expand_dims(input_data, axis=0)
```

**Step 3: INFER** -- Run the model on the preprocessed frame.

```python
import tflite_runtime.interpreter as tflite

def load_tflite_model(model_path, num_threads=4):
    """Load TFLite model with optimal thread count for edge device."""
    interpreter = tflite.Interpreter(
        model_path=model_path,
        num_threads=num_threads
    )
    interpreter.allocate_tensors()
    return interpreter

def infer(interpreter, input_data):
    """Run inference and return output tensors."""
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()
    return [interpreter.get_tensor(d['index']) for d in output_details]
```

**Step 4: POSTPROCESS** -- Parse detections, apply NMS, threshold.

```python
def postprocess_detections(outputs, confidence_threshold=0.5,
                           input_size=(320, 320), original_size=(640, 480)):
    """Parse SSD-style detection outputs."""
    boxes, classes, scores = outputs[0][0], outputs[1][0], outputs[2][0]
    detections = []
    scale_x = original_size[0] / input_size[0]
    scale_y = original_size[1] / input_size[1]
    for i, score in enumerate(scores):
        if score < confidence_threshold:
            continue
        ymin, xmin, ymax, xmax = boxes[i]
        detections.append({
            "class_id": int(classes[i]),
            "confidence": float(score),
            "bbox": [
                int(xmin * input_size[0] * scale_x),
                int(ymin * input_size[1] * scale_y),
                int(xmax * input_size[0] * scale_x),
                int(ymax * input_size[1] * scale_y),
            ]
        })
    return detections
```

**Step 5: PUBLISH** -- Send results to MQTT, HTTP, or display.

```python
import json
import paho.mqtt.client as mqtt

class MQTTPublisher:
    def __init__(self, broker="localhost", port=1883, topic="cv/detections"):
        self.client = mqtt.Client()
        self.client.connect(broker, port)
        self.topic = topic
        self.client.loop_start()

    def publish(self, detections, frame_id=None):
        payload = json.dumps({
            "frame_id": frame_id,
            "detections": detections,
        })
        self.client.publish(self.topic, payload)

    def stop(self):
        self.client.loop_stop()
        self.client.disconnect()
```

## State Block Format

Maintain state across conversation turns using this block:

```
<edge-cv-state>
step: [CAPTURE | PREPROCESS | INFER | POSTPROCESS | PUBLISH]
target_device: [jetson-orin-nano | raspberry-pi-5 | raspberry-pi-4]
model_format: [tflite | onnx | tensorrt | openvino]
fps_target: [number]
latency_ms: [number or "unmeasured"]
last_action: [what was just done]
next_action: [what should happen next]
blockers: [any issues]
</edge-cv-state>
```

**Example:**

```
<edge-cv-state>
step: INFER
target_device: raspberry-pi-5
model_format: tflite
fps_target: 15
latency_ms: 45
last_action: Converted MobileNetV2 to TFLite with float16 quantization
next_action: Profile inference latency on RPi 5 with XNNPACK delegate
blockers: none
</edge-cv-state>
```

## Output Templates

### Pipeline Scaffold Report

```markdown
## Edge CV Pipeline: [Project Name]

**Target Device**: [device]
**Camera**: [CSI / USB / IP] at [resolution] @ [fps]
**Model**: [name] ([format], [size] MB)
**Input**: [width]x[height]x[channels]
**Output**: [description of model output]
**Publish**: [MQTT / HTTP / file / display]

### Latency Budget

| Stage       | Budget (ms) | Measured (ms) | Status |
|-------------|-------------|---------------|--------|
| Capture     | [n]         | [n]           | [ok/over] |
| Preprocess  | [n]         | [n]           | [ok/over] |
| Inference   | [n]         | [n]           | [ok/over] |
| Postprocess | [n]         | [n]           | [ok/over] |
| Publish     | [n]         | [n]           | [ok/over] |
| **Total**   | **[n]**     | **[n]**       | **[ok/over]** |

### Dependencies

```bash
pip install opencv-python-headless numpy tflite-runtime paho-mqtt
```

### Files Created

- `capture.py` -- Camera capture with threading
- `preprocess.py` -- Frame resize and normalization
- `infer.py` -- Model loading and inference
- `postprocess.py` -- Detection parsing and NMS
- `publish.py` -- MQTT/HTTP result publishing
- `pipeline.py` -- Main loop connecting all stages
- `tests/` -- pytest test suite
```

### Profiling Report

```markdown
## Profiling Report: [Pipeline Name]

**Device**: [device]
**Model**: [model name] ([format])
**Date**: [date]

### Per-Stage Latency (averaged over 100 frames)

| Stage       | Mean (ms) | P95 (ms) | P99 (ms) |
|-------------|-----------|----------|----------|
| Capture     | [n]       | [n]      | [n]      |
| Preprocess  | [n]       | [n]      | [n]      |
| Inference   | [n]       | [n]      | [n]      |
| Postprocess | [n]       | [n]      | [n]      |
| Publish     | [n]       | [n]      | [n]      |
| **Total**   | **[n]**   | **[n]** | **[n]** |

### Resource Usage

- **RAM**: [n] MB (peak: [n] MB)
- **GPU/NPU**: [utilization %]
- **CPU**: [utilization %]
- **Temperature**: [n] C (throttle threshold: [n] C)
- **FPS**: [measured] / [target]

### Recommendations

- [optimization suggestions based on profiling data]
```

## AI Discipline Rules

### CRITICAL: Always Profile on Target Hardware

Before claiming any performance number:
1. The pipeline MUST be running on the actual target device (Jetson, RPi)
2. x86/x64 development machine numbers are for debugging only
3. Profile with `time.perf_counter_ns()` per stage, not wall-clock guesses
4. Report P95 latency, not just mean -- edge devices have variance from thermal throttling

```python
import time

# CORRECT: Measure on target device per stage
t0 = time.perf_counter_ns()
preprocessed = preprocess_frame(frame)
t1 = time.perf_counter_ns()
outputs = infer(interpreter, preprocessed)
t2 = time.perf_counter_ns()
preprocess_ms = (t1 - t0) / 1_000_000
infer_ms = (t2 - t1) / 1_000_000

# WRONG: Guessing latency from model size
# "MobileNetV2 should run at about 30ms on RPi" -- NEVER assume this
```

### CRITICAL: Never Skip Preprocessing Validation

Before running inference, verify that the input tensor matches what the model expects:

```python
input_details = interpreter.get_input_details()[0]
expected_shape = input_details['shape']       # e.g., [1, 320, 320, 3]
expected_dtype = input_details['dtype']       # e.g., numpy.float32

assert input_data.shape == tuple(expected_shape), \
    f"Shape mismatch: got {input_data.shape}, expected {tuple(expected_shape)}"
assert input_data.dtype == expected_dtype, \
    f"Dtype mismatch: got {input_data.dtype}, expected {expected_dtype}"
```

Skipping this validation leads to silent wrong results (garbage detections that look plausible) or hard-to-debug segfaults in native inference backends.

### CRITICAL: Handle Camera Disconnection Gracefully

Edge deployments lose camera connections due to loose CSI ribbons, USB power issues, or thermal shutdowns. The pipeline must survive this:

```python
class ResilientCapture:
    def __init__(self, source, max_retries=5, retry_delay=2.0):
        self.source = source
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.cap = None
        self._connect()

    def _connect(self):
        self.cap = cv2.VideoCapture(self.source)
        if not self.cap.isOpened():
            raise RuntimeError(f"Cannot open camera: {self.source}")

    def read(self):
        ret, frame = self.cap.read()
        if not ret:
            for attempt in range(self.max_retries):
                print(f"Camera read failed, retry {attempt + 1}/{self.max_retries}")
                self.cap.release()
                time.sleep(self.retry_delay)
                try:
                    self._connect()
                    ret, frame = self.cap.read()
                    if ret:
                        return frame
                except RuntimeError:
                    continue
            raise RuntimeError("Camera permanently lost after retries")
        return frame
```

### CRITICAL: Match Model Input Resolution to Capture Resolution

Capturing at a higher resolution than the model needs wastes CPU on resize operations. Capturing at a lower resolution than the model needs degrades accuracy:

```python
# CORRECT: Configure capture to match model input (or close to it)
MODEL_INPUT_SIZE = (320, 320)
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 320)

# WRONG: Capture at 1080p and resize down
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)  # Wasting cycles
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
frame = cap.read()
resized = cv2.resize(frame, (320, 320))  # Expensive and unnecessary
```

**Exception**: When you need the full-resolution frame for annotation, recording, or multiple models at different scales, capture at the higher resolution and document the resize cost in the latency budget.

## Anti-Patterns Table

| Anti-Pattern | Why It Fails on Edge | Correct Approach |
|--------------|----------------------|------------------|
| Capturing at 1080p for a 320x320 model | Wastes 10x pixels in resize; burns CPU/memory | Set capture resolution to model input or nearest supported |
| Running inference on the main thread | Blocks frame capture, causes dropped frames and stalls | Separate capture and inference into threaded pipeline with queue |
| Loading model inside the frame loop | Model load takes 200ms-2s; doing it per frame kills FPS | Load model once at startup, reuse interpreter across frames |
| Using `cv2.imshow()` in headless deploy | X11 forwarding over SSH adds 50-100ms latency; crashes if no display | Publish via MQTT/HTTP; use `imshow` only for local debugging |
| Ignoring thermal throttling | Jetson/RPi throttle CPU/GPU at 80-85C; sustained load drops FPS 30-50% | Profile under sustained load for 5+ minutes; design for throttled throughput |
| Hardcoding camera index `0` | Multi-camera setups or USB re-enumeration changes indices | Use device path (`/dev/video0`) or GStreamer pipeline string |
| No frame drop policy | Queue fills, memory exhausts, OOM kill | Use bounded queue with drop-oldest policy |
| Float32 model on RPi without delegate | RPi 4/5 CPU is slow at float32; inference takes 500ms+ | Quantize to INT8 or use float16 with XNNPACK delegate |

## Error Recovery

### Camera Fails to Open

```
Problem: cv2.VideoCapture returns False on isOpened()
Actions:
1. Verify camera hardware connection (CSI ribbon seated, USB plugged)
2. Check /dev/video* exists: ls /dev/video*
3. For Jetson CSI: verify nvarguscamerasrc works: gst-launch-1.0 nvarguscamerasrc ! fakesink
4. For RPi CSI: verify libcamera works: libcamera-hello --list-cameras
5. Check permissions: sudo usermod -aG video $USER
6. Reboot if camera was hot-plugged on CSI interface
```

### Model Inference Returns Garbage

```
Problem: Detections are random or all zeros
Actions:
1. Verify preprocessing matches training pipeline exactly (RGB vs BGR, normalize range)
2. Check input tensor shape and dtype against interpreter.get_input_details()
3. Verify model file is not corrupted (compare checksum)
4. Test with a known-good image from the training dataset
5. Print raw output tensor values before postprocessing
6. Check if quantized model needs different input scaling (0-255 vs 0.0-1.0)
```

### FPS Below Target

```
Problem: Pipeline cannot sustain target FPS
Actions:
1. Profile each stage to find the bottleneck (see profiling reference)
2. If capture is slow: reduce resolution, check GStreamer pipeline
3. If preprocess is slow: use cv2.resize with INTER_NEAREST, avoid float conversion
4. If inference is slow: quantize model, reduce input size, try hardware delegate
5. If postprocess is slow: vectorize with numpy, reduce detection count
6. If publish is slow: switch from HTTP to MQTT, batch results
7. If ALL stages are slow: the model is too large for this device
```

### Out of Memory (OOM)

```
Problem: Pipeline killed by OOM on edge device
Actions:
1. Check frame queue size (reduce maxsize to 1-2)
2. Verify model is not loaded multiple times
3. Use uint8 instead of float32 where possible
4. Reduce capture resolution
5. Monitor with: watch -n 1 free -m
6. For Jetson: check tegrastats for GPU memory usage
7. For RPi: reduce GPU memory split in /boot/config.txt
```

### Thermal Throttling

```
Problem: FPS degrades after sustained operation
Actions:
1. Monitor temperature: cat /sys/class/thermal/thermal_zone*/temp
2. Add heatsink and fan (passive cooling is insufficient for sustained load)
3. Reduce inference frequency (process every Nth frame)
4. Lower clock speeds proactively to avoid thermal cliff
5. For Jetson: sudo jetson_clocks --show to check governor settings
6. For RPi: check vcgencmd measure_temp and throttle status
```

## Integration with Other Skills

- **`jetson-deploy`** -- After building the CV pipeline, use `jetson-deploy` to containerize it with NVIDIA L4T base images, configure JetPack dependencies, and deploy with `jetson-containers` or Docker Compose. The pipeline code from this skill becomes the application layer inside the Jetson container.

- **`sensor-integration`** -- When the CV pipeline needs to fuse camera data with other sensors (IMU, LIDAR, ultrasonic), use `sensor-integration` to handle multi-sensor synchronization. The CV pipeline publishes detections via MQTT; `sensor-integration` subscribes and correlates with other sensor streams.

- **`picar-x-behavior`** -- For PiCar-X robotics projects, this skill provides the vision layer. The CV pipeline detects objects, lanes, or signs, and publishes results that `picar-x-behavior` consumes to make driving decisions. Use shared MQTT topics for the interface between vision and behavior.

## Reference Files

- [Model Conversion](references/model-conversion.md) -- TFLite, ONNX, TensorRT conversion recipes with quantization
- [Capture and Publish Patterns](references/capture-publish-patterns.md) -- Camera capture, threading, and result publishing patterns
- [Edge Profiling](references/edge-profiling.md) -- Per-stage profiling, memory measurement, thermal monitoring
