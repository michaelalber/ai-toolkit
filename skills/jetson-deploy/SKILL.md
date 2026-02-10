---
name: jetson-deploy
description: Deploy and optimize applications on Jetson Orin Nano with TensorRT. Use when setting up Jetson environments, converting models to TensorRT, managing power modes, and containerizing edge AI applications.
---

# Jetson Orin Nano Deployment & TensorRT Optimization

> "The future of AI is at the edge. Every robot, every camera, every sensor will have AI processing locally."
> — Dustin Franklin, NVIDIA Jetson AI Developer

## Core Philosophy

This skill orchestrates the full lifecycle of deploying AI applications to NVIDIA Jetson Orin Nano devices. Every decision is constrained by **thermal limits, power budgets, and memory ceilings** that do not exist in cloud or desktop environments.

**Non-Negotiable Constraints:**
1. **Power budget is law** — The Orin Nano runs at 7W, 15W, or MAXN. Every model, every pipeline, every container must fit within the active power envelope. Ignoring this causes thermal throttling, silent performance degradation, or hardware shutdown.
2. **TensorRT for production inference** — Raw PyTorch or ONNX Runtime is acceptable for prototyping. Production inference MUST use TensorRT-optimized engines. The performance gap is 2-10x; skipping this step is not optional.
3. **Profile on the actual device** — Desktop GPU benchmarks are meaningless. A model that runs at 60 FPS on an RTX 4090 may run at 3 FPS on an Orin Nano. Always benchmark on target hardware.
4. **JetPack version determines everything** — CUDA version, TensorRT version, cuDNN version, and supported container base images all flow from the JetPack release. Verify JetPack version before any other step.
5. **Containers are mandatory for reproducibility** — Use `jetson-containers` from dustynv to build reproducible deployment environments. Bare-metal installs create fragile, unreproducible setups.

## Domain Principles Table

| Principle | Description | Priority |
|-----------|-------------|----------|
| **Power Mode Awareness** | Select and validate power mode before benchmarking or deploying; results are meaningless without a fixed power profile | Critical |
| **TensorRT First** | Convert all inference models to TensorRT engines before deployment; never ship raw ONNX or PyTorch models to production | Critical |
| **JetPack Compatibility** | Verify JetPack version, L4T version, and CUDA version before installing any package or building any container | Critical |
| **Container Reproducibility** | Use jetson-containers for all deployments; pin base images to specific L4T versions; never rely on bare-metal installs | High |
| **Thermal Management** | Profile thermal behavior under sustained load; set power mode and fan policy before benchmarking; monitor with tegrastats | High |
| **Memory Budget Discipline** | The Orin Nano has 8GB unified memory shared between CPU and GPU; always account for OS overhead (~1.5GB), display server, and framework footprint | High |
| **On-Device Validation** | Never trust desktop or cloud benchmarks; always validate latency, throughput, and accuracy on the target Jetson device | High |
| **Precision-Accuracy Tradeoff** | FP16 is the default for Orin Nano; INT8 requires calibration data and accuracy validation; never assume precision reduction is lossless | Medium |
| **Incremental Deployment** | Deploy one component at a time; validate each stage before adding the next pipeline element | Medium |
| **Telemetry from Day One** | Instrument with tegrastats and jtop from the first deployment; do not wait for production to add monitoring | Medium |

## Workflow

### Deployment Pipeline

```
┌──────────────────────────────────────────────────────────────────────┐
│                                                                      │
│   ┌───────┐    ┌─────────────┐    ┌─────────┐    ┌──────────┐       │
│   │ SETUP │───>│ CONTAINERIZE│───>│ CONVERT │───>│ OPTIMIZE │       │
│   └───────┘    └─────────────┘    └─────────┘    └──────────┘       │
│                                                       │              │
│                                                       v              │
│                                   ┌────────┐    ┌───────────┐       │
│                                   │ DEPLOY │<───│ BENCHMARK │       │
│                                   └────────┘    └───────────┘       │
│                                       │                              │
│                                       └──── (iterate if needed) ──┐ │
│                                                                   │ │
│                                   ┌──────────┐                    │ │
│                                   │ OPTIMIZE │<───────────────────┘ │
│                                   └──────────┘                      │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

### Pre-Flight Checklist

Before beginning any deployment workflow, verify:

```
PRE-FLIGHT VERIFICATION
┌──────────────────────────────────────────────────────────────────┐
│ □ JetPack version confirmed (cat /etc/nv_tegra_release)         │
│ □ L4T version matches expected (dpkg -l nvidia-l4t-core)        │
│ □ CUDA version confirmed (nvcc --version)                       │
│ □ TensorRT version confirmed (dpkg -l tensorrt)                 │
│ □ Available disk space > 10GB (df -h)                           │
│ □ Docker runtime is nvidia (docker info | grep -i runtime)      │
│ □ Power mode is set (sudo nvpmodel -q)                          │
│ □ Fan mode is set (sudo jetson_clocks --show)                   │
│ □ Network access for container pulls (if needed)                │
│ □ Model files are accessible on device                          │
└──────────────────────────────────────────────────────────────────┘

If ANY checkbox is unchecked → STOP. Resolve before proceeding.
```

### Step 1: SETUP

**Objective**: Confirm the Jetson device is properly configured for deployment.

**Actions:**
1. SSH into the Jetson device or open local terminal
2. Run `cat /etc/nv_tegra_release` to confirm L4T version
3. Run `sudo nvpmodel -q` to check current power mode
4. Run `sudo nvpmodel -m <MODE>` to set target power mode (0=MAXN, 1=15W, 2=7W for Orin Nano)
5. Run `sudo jetson_clocks` to lock clock frequencies for consistent benchmarking
6. Install jtop: `sudo pip3 install jetson-stats`
7. Verify Docker nvidia runtime: `docker run --rm --runtime nvidia --gpus all nvidia/cuda:12.2.0-base-ubuntu22.04 nvidia-smi`

**Exit Criteria:**
- JetPack version documented
- Power mode set and confirmed
- Docker nvidia runtime functional
- jtop installed and running

### Step 2: CONTAINERIZE

**Objective**: Build a reproducible container environment using jetson-containers.

**Actions:**
1. Clone jetson-containers: `git clone https://github.com/dusty-nv/jetson-containers`
2. Select appropriate base image for JetPack version
3. Define container requirements (TensorRT, OpenCV, model framework)
4. Build container using `jetson-containers build` or `docker build`
5. Test container starts with GPU access
6. Mount model directory and data directory as volumes

**Exit Criteria:**
- Container builds without errors
- Container runs with `--runtime nvidia`
- GPU is accessible inside container (`python3 -c "import tensorrt; print(tensorrt.__version__)"`)
- Model files accessible via volume mount

### Step 3: CONVERT

**Objective**: Convert model from training format to TensorRT engine.

**Actions:**
1. Export model to ONNX format (if not already ONNX)
2. Validate ONNX model: `python3 -c "import onnx; model = onnx.load('model.onnx'); onnx.checker.check_model(model)"`
3. Convert ONNX to TensorRT engine using `trtexec` or Python API
4. Specify target precision (FP16 default for Orin Nano)
5. Handle dynamic shapes if needed
6. Verify engine loads and produces output

**Exit Criteria:**
- TensorRT engine file created (`.engine` or `.trt`)
- Engine loads without errors
- Engine produces output on sample input
- Output shape matches expected dimensions

### Step 4: OPTIMIZE

**Objective**: Tune the TensorRT engine and pipeline for target performance.

**Actions:**
1. Profile with trtexec: `trtexec --loadEngine=model.engine --iterations=100 --avgRuns=50`
2. Try INT8 quantization if FP16 does not meet latency target (requires calibration)
3. Experiment with workspace size: `--memPoolSize=workspace:1024MiB`
4. Optimize input preprocessing (use GPU-accelerated resize, normalize)
5. Add CUDA streams for async execution if pipeline allows

**Exit Criteria:**
- Latency meets target at specified power mode
- Memory usage leaves headroom for OS and other processes
- No thermal throttling under sustained load

### Step 5: BENCHMARK

**Objective**: Produce reliable, reproducible performance measurements.

**Actions:**
1. Set power mode explicitly: `sudo nvpmodel -m <MODE>`
2. Lock clocks: `sudo jetson_clocks`
3. Run warm-up iterations (50+) before measuring
4. Record latency (mean, P50, P95, P99) across 1000+ iterations
5. Monitor with tegrastats during benchmark: `tegrastats --interval 1000`
6. Record GPU utilization, memory usage, temperature, power draw
7. Validate accuracy against reference outputs

**Exit Criteria:**
- Benchmark results documented with power mode and clock state
- Latency distribution captured (not just mean)
- Thermal behavior stable (no throttling during measurement)
- Accuracy validated against golden reference

### Step 6: DEPLOY

**Objective**: Finalize the deployment for production operation.

**Actions:**
1. Create Docker Compose or systemd service for auto-start
2. Configure restart policies for resilience
3. Set up logging and monitoring (tegrastats, jtop, application logs)
4. Configure watchdog for thermal protection
5. Validate end-to-end pipeline with production data
6. Document deployment configuration

**Exit Criteria:**
- Application starts automatically on boot
- Restart policy handles crashes gracefully
- Monitoring is active and accessible
- End-to-end pipeline validated with real data

## State Block Format

Maintain state across conversation turns using this block:

```
<jetson-deploy-state>
step: [SETUP | CONTAINERIZE | CONVERT | OPTIMIZE | BENCHMARK | DEPLOY]
jetpack_version: [e.g., "6.0", "5.1.2"]
power_mode: [MAXN | 15W | 7W]
inference_engine: [tensorrt | onnxruntime | tflite]
last_action: [what was just done]
next_action: [what should happen next]
blockers: [any issues]
</jetson-deploy-state>
```

**Example:**

```markdown
<jetson-deploy-state>
step: CONVERT
jetpack_version: 6.0
power_mode: 15W
inference_engine: tensorrt
last_action: Exported YOLOv8n to ONNX format
next_action: Convert ONNX to TensorRT FP16 engine
blockers: none
</jetson-deploy-state>
```

## Output Templates

### Deployment Report

```markdown
## Jetson Deployment Report

**Device**: Jetson Orin Nano 8GB
**JetPack**: [version]
**L4T**: [version]
**Power Mode**: [MAXN | 15W | 7W]

### Model
- **Name**: [model name]
- **Source Format**: [PyTorch | ONNX | TensorFlow]
- **TensorRT Engine**: [filename, size]
- **Precision**: [FP32 | FP16 | INT8]
- **Input Shape**: [dimensions]
- **Output Shape**: [dimensions]

### Container
- **Base Image**: [image:tag]
- **Key Packages**: [TensorRT version, CUDA version, OpenCV version]
- **Total Image Size**: [size]

### Performance
| Metric | Value |
|--------|-------|
| Mean Latency | [ms] |
| P95 Latency | [ms] |
| P99 Latency | [ms] |
| Throughput | [fps] |
| GPU Utilization | [%] |
| Memory Usage | [MB / 8192 MB] |
| Peak Temperature | [C] |
| Power Draw | [W] |

### Deployment Configuration
- **Auto-start**: [systemd | docker-compose]
- **Restart Policy**: [always | on-failure]
- **Monitoring**: [tegrastats | jtop | custom]
```

### Benchmark Results

```markdown
## Benchmark: [Model Name] on Jetson Orin Nano

**Date**: [date]
**JetPack**: [version]
**Power Mode**: [mode]
**Clocks**: [locked | dynamic]

### Latency Distribution (N=[iterations])

| Percentile | Latency (ms) |
|------------|-------------|
| P50 | [value] |
| P90 | [value] |
| P95 | [value] |
| P99 | [value] |
| Min | [value] |
| Max | [value] |

### Precision Comparison

| Precision | Mean Latency | Throughput | Accuracy |
|-----------|-------------|------------|----------|
| FP32 | [ms] | [fps] | [mAP/acc] |
| FP16 | [ms] | [fps] | [mAP/acc] |
| INT8 | [ms] | [fps] | [mAP/acc] |

### System Metrics (Sustained Load)

| Metric | Mean | Peak |
|--------|------|------|
| GPU Temp | [C] | [C] |
| CPU Temp | [C] | [C] |
| Power Draw | [W] | [W] |
| GPU Util | [%] | [%] |
| Memory Used | [MB] | [MB] |

### Notes
- [observations about thermal behavior]
- [observations about performance stability]
- [any throttling events]
```

## AI Discipline Rules

### CRITICAL: Always Verify JetPack Version First

Before installing any package, building any container, or converting any model:

```
STOP! Verify:
1. JetPack version is known (cat /etc/nv_tegra_release)
2. L4T version is documented
3. CUDA version matches JetPack
4. TensorRT version matches JetPack

If ANY version is unknown → DO NOT PROCEED.
JetPack version mismatches cause silent failures, broken containers,
and wasted hours of debugging.
```

Mixing packages from different JetPack versions will corrupt the system. There is no recovery short of reflashing the device.

### CRITICAL: Never Deploy Without TensorRT Conversion

Before any deployment to production:

```
STOP! Verify:
1. Model has been converted to TensorRT engine
2. Engine was built ON the target device (or matching architecture)
3. Engine precision matches deployment requirements
4. Engine produces correct outputs on test inputs

If using raw ONNX or PyTorch for production → STOP.
Convert to TensorRT first. The 2-10x performance gap is not optional.
```

TensorRT engines are architecture-specific. An engine built on x86 will NOT run on ARM. An engine built on one JetPack version may not run on another. Always build engines on the target device.

### CRITICAL: Profile Thermal Behavior Under Load

Before declaring a deployment ready for production:

```
STOP! Verify:
1. Benchmark ran for at least 5 minutes sustained
2. tegrastats was running during the benchmark
3. No thermal throttling events were observed
4. Temperature stabilized below throttle threshold
5. Performance was consistent from start to finish

If temperatures exceed 80C or throttling was detected → STOP.
Adjust power mode, add cooling, or reduce model complexity.
```

The Orin Nano thermal throttles at approximately 85-90C depending on configuration. Passive cooling is insufficient for sustained MAXN workloads. Always verify thermal stability before production.

### CRITICAL: Use jetson-containers for Reproducibility

Before deploying any application:

```
STOP! Verify:
1. Application runs inside a container (not bare-metal)
2. Container base image is pinned to a specific L4T version
3. All dependencies are specified in the Dockerfile
4. Container was tested with --runtime nvidia
5. Volume mounts are documented for models, data, and devices

If deploying bare-metal → STOP.
Containerize first. Bare-metal installs are not reproducible
and create version conflicts that are nearly impossible to debug.
```

## Common Anti-Patterns to Avoid

| Anti-Pattern | Why It's Wrong | Correct Approach |
|--------------|----------------|------------------|
| Benchmarking on desktop GPU | Results are meaningless for edge deployment; different architecture, memory, and power | Always benchmark on the target Jetson device |
| Skipping TensorRT conversion | 2-10x performance left on the table; latency targets will not be met | Convert all production models to TensorRT engines |
| Building engine on x86 | TensorRT engines are architecture-specific; x86 engines do not run on ARM | Build engines on the Jetson device itself |
| Ignoring power mode during benchmark | Results are not reproducible; different runs use different power profiles | Set power mode explicitly before every benchmark |
| Installing pip packages bare-metal | Creates version conflicts with JetPack system packages; breaks CUDA/TensorRT | Use containers; never pip install on the host system |
| Using FP32 without trying FP16 | Orin Nano has dedicated FP16 tensor cores; FP32 wastes half the compute capability | Default to FP16; only use FP32 if accuracy requires it |
| Deploying without thermal profiling | Device throttles or shuts down under sustained load in production | Run sustained load test with tegrastats for 10+ minutes |
| Hardcoding paths in containers | Breaks when deploying to different devices or updating models | Use volume mounts for models, data, and configuration |

## Error Recovery

### CUDA Version Mismatch

```
Problem: "CUDA error: no kernel image is available for execution on the device"
         or "CUDA driver version is insufficient for CUDA runtime version"

Root Cause: Package was built against different CUDA version than installed.

Actions:
1. Check JetPack version: cat /etc/nv_tegra_release
2. Check CUDA version: nvcc --version
3. Identify the mismatched package
4. Reinstall package matching your JetPack/CUDA version
5. If using container, verify base image matches JetPack version
6. If bare-metal, strongly consider migrating to containers
```

### Out of Memory on Model Load

```
Problem: "CUDA out of memory" or "Failed to allocate memory for TensorRT engine"

Root Cause: Model + framework + OS exceed 8GB unified memory.

Actions:
1. Check memory usage: free -h and tegrastats
2. Kill unnecessary processes (desktop environment uses ~800MB)
3. Reduce TensorRT workspace size: --memPoolSize=workspace:512MiB
4. Use FP16 instead of FP32 (halves memory for weights)
5. Reduce batch size to 1
6. If still OOM, use a smaller model variant (e.g., YOLOv8n instead of YOLOv8l)
7. Consider running headless (disable GUI): sudo systemctl set-default multi-user.target
```

### Thermal Throttling

```
Problem: Performance degrades after running for several minutes.
         tegrastats shows temperature above 80C.

Root Cause: Insufficient cooling for the workload at current power mode.

Actions:
1. Check current temperature: cat /sys/devices/virtual/thermal/thermal_zone*/temp
2. Verify fan is running: sudo jetson_clocks --show
3. Lower power mode: sudo nvpmodel -m 1 (15W) or -m 2 (7W)
4. Add active cooling (fan, heatsink) if not present
5. Reduce model complexity or input resolution
6. Add thermal monitoring to application: poll tegrastats and throttle workload
7. Re-benchmark at the sustainable power mode
```

### Container Build Failures

```
Problem: Docker build fails with package conflicts or missing dependencies.

Root Cause: Base image L4T version does not match device JetPack version,
            or incompatible package versions specified.

Actions:
1. Verify device JetPack version: cat /etc/nv_tegra_release
2. Verify base image L4T tag matches: check Dockerfile FROM line
3. For JetPack 6.x use L4T r36.x base images
4. For JetPack 5.x use L4T r35.x base images
5. Use jetson-containers build system which handles compatibility automatically
6. Check dustynv/jetson-containers GitHub for known issues with your JetPack version
7. If building custom Dockerfile, pin all package versions explicitly
```

### TensorRT Engine Build Failures

```
Problem: trtexec or TensorRT Python API fails during engine build.
         "Unsupported ONNX opset" or "Layer not supported" errors.

Root Cause: ONNX model uses operations not supported by the installed TensorRT version.

Actions:
1. Check TensorRT version: dpkg -l tensorrt
2. Check ONNX opset version: python3 -c "import onnx; print(onnx.load('model.onnx').opset_import)"
3. Try simplifying ONNX model: python3 -m onnxsim model.onnx model_simplified.onnx
4. Check NVIDIA TensorRT support matrix for unsupported ops
5. Use ONNX-GraphSurgeon to replace unsupported operations
6. Try an older opset version when exporting from PyTorch
7. As last resort, use ONNX Runtime as fallback for specific unsupported layers
```

## Integration with Other Skills

- **edge-cv-pipeline** — After deploying a TensorRT engine, use `edge-cv-pipeline` to build the complete vision pipeline (camera capture, preprocessing, inference, postprocessing, output). The Jetson deployment handles the infrastructure; the CV pipeline handles the application logic.
- **sensor-integration** — When the Jetson deployment includes sensor inputs (GPIO, I2C, SPI, USB cameras, LiDAR), use `sensor-integration` for device configuration, data acquisition, and fusion. Mount device files (`/dev/video0`, `/dev/i2c-*`, `/dev/spidev*`) into containers as needed.
- **picar-x-behavior** — When deploying to a PiCar-X robot platform with a Jetson compute module, coordinate motor control and sensor fusion with inference deployment. The Jetson handles vision inference; PiCar-X behavior handles actuation and navigation.
