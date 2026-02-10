---
name: model-optimization
description: Optimize ML models for edge deployment through quantization, pruning, format conversion (TensorRT/TFLite/ONNX), and accuracy/latency benchmarking. Use when preparing models for resource-constrained devices.
---

# Model Optimization for Edge Deployment

> "Quantization is not about making models worse. It is about finding the representation that preserves what matters while discarding what does not."
> -- Benoit Jacob, Google Quantization Team

## Core Philosophy

This skill covers the complete model optimization pipeline: profiling baseline performance, applying quantization and pruning, converting between inference formats, and benchmarking the results. **Every optimization decision is driven by measurement, not intuition.**

**Non-Negotiable Constraints:**
1. **Baseline first** -- measure the original model before touching it. Without a baseline, you cannot quantify improvement or regression.
2. **Accuracy is the constraint, latency is the objective** -- optimize for speed subject to an accuracy floor, never the other way around.
3. **One change at a time** -- apply optimizations sequentially and benchmark after each. Compound changes make it impossible to attribute regressions.
4. **Target hardware determines the format** -- TensorRT for Jetson, TFLite for Raspberry Pi, ONNX Runtime for general CPU. Never deploy the wrong format to the wrong device.
5. **Preserve the original** -- never modify or delete the source model. All outputs are new files.

## Domain Principles Table

| Principle | Description | Priority |
|-----------|-------------|----------|
| **Measure Before Optimizing** | Profile the unmodified model for latency, accuracy, size, and memory before applying any optimization | Critical |
| **Accuracy Floor Enforcement** | Define an acceptable accuracy degradation threshold and reject any optimization that violates it | Critical |
| **Format-Device Alignment** | Match the inference format to the target hardware: TensorRT for NVIDIA GPU, TFLite for ARM CPU, ONNX for portable | Critical |
| **Calibration Data Quality** | INT8 quantization is only as good as the calibration dataset; use representative, domain-specific data | High |
| **Sequential Optimization** | Apply one optimization at a time, benchmark, then decide whether to keep or revert | High |
| **Reproducible Benchmarks** | Lock clock speeds, set power modes, run warmup iterations, and report percentile latencies | High |
| **Original Preservation** | Never modify, move, or delete the original model file; all outputs use new descriptive filenames | High |
| **Per-Layer Sensitivity** | Not all layers respond equally to quantization; identify and protect sensitive layers | Medium |
| **Mixed Precision** | When uniform INT8 fails accuracy, use FP16 for sensitive layers and INT8 for the rest | Medium |
| **Deployment Metadata** | Package optimized models with benchmark results, preprocessing config, and provenance information | Medium |

## Workflow

### Optimization Pipeline

```
+--------+     +----------+     +-----------+     +----------+     +---------+
| PROFILE|---->| OPTIMIZE |---->| BENCHMARK |---->| VALIDATE |---->| PACKAGE |
+--------+     +----------+     +-----------+     +----------+     +---------+
    |               |                 |                 |
    |               |                 |                 |
    v               v                 v                 v
 Baseline       Quantized/        Speedup/          Accuracy       Deploy-ready
 metrics        Converted         Compression       verified       artifact
                model             ratios            within tol.
```

### Pre-Flight Checklist

Before starting any optimization workflow, verify:

```
PRE-FLIGHT VERIFICATION
+--------------------------------------------------------------+
| [ ] Source model file exists and is loadable                  |
| [ ] Model framework identified (PyTorch / TensorFlow / ONNX) |
| [ ] Target device identified (Jetson / RPi / CPU)            |
| [ ] Test/validation dataset available                         |
| [ ] Accuracy metric defined (mAP / top-1 / F1 / custom)     |
| [ ] Accuracy tolerance defined (default: 2% relative drop)   |
| [ ] Latency target defined (optional but recommended)        |
| [ ] Calibration dataset available (for INT8 quantization)    |
| [ ] Disk space sufficient for multiple model variants        |
+--------------------------------------------------------------+
```

### Quantization Strategy Decision Tree

```
What is the target device?
+-- NVIDIA Jetson (GPU)
|   +-- Start with TensorRT FP16
|   +-- FP16 meets latency target?
|       +-- YES --> Ship FP16 (done)
|       +-- NO  --> Prepare calibration dataset (500-1000 images)
|                   +-- Apply TensorRT INT8 with calibration
|                   +-- Accuracy within tolerance?
|                       +-- YES --> Ship INT8
|                       +-- NO  --> Try mixed precision or smaller model
|
+-- Raspberry Pi / ARM CPU
|   +-- Start with TFLite float16 quantization
|   +-- Float16 meets latency target?
|       +-- YES --> Ship float16 (done)
|       +-- NO  --> Prepare calibration dataset (200-500 images)
|                   +-- Apply TFLite full INT8 PTQ
|                   +-- Accuracy within tolerance?
|                       +-- YES --> Ship INT8
|                       +-- NO  --> Try QAT or smaller model
|
+-- General CPU / Cloud
    +-- Start with ONNX Runtime graph optimizations
    +-- Apply dynamic range quantization
    +-- If needed, apply full INT8 with calibration
```

### Pruning Strategy Decision Tree

```
Is the model overparameterized for the task?
+-- YES (accuracy is well above requirements)
|   +-- Try structured pruning (remove entire channels/filters)
|   +-- Start with 20% pruning ratio
|   +-- Fine-tune for 5-10 epochs
|   +-- Accuracy still within tolerance?
|       +-- YES --> Increase pruning ratio (30%, 40%, ...)
|       +-- NO  --> Reduce pruning ratio or switch to unstructured
|
+-- NO (accuracy is near the floor already)
    +-- Do NOT prune; focus on quantization and format conversion instead
```

## State Block Format

Maintain state across conversation turns using this block:

```
<model-opt-state>
phase: [PROFILE | OPTIMIZE | BENCHMARK | VALIDATE | PACKAGE]
model_name: [name of the model being optimized]
source_format: [pytorch | tensorflow | onnx | tflite | tensorrt]
target_device: [jetson-orin-nano | raspberry-pi-5 | raspberry-pi-4 | cpu-generic]
baseline_latency_ms: [number or "unmeasured"]
baseline_accuracy: [number or "unmeasured"]
accuracy_tolerance: [percentage, e.g., "2%"]
optimizations_applied: [comma-separated list or "none"]
current_best_latency_ms: [number or "unmeasured"]
current_best_accuracy: [number or "unmeasured"]
original_model_path: [absolute path to original model file]
last_action: [what was just done]
next_action: [what should happen next]
blockers: [any issues]
</model-opt-state>
```

## Output Templates

### Optimization Summary Report

```markdown
## Model Optimization Report: [Model Name]

**Source**: [framework] [format] ([size] MB)
**Target Device**: [device]
**Optimization Pipeline**: [list of steps applied]
**Date**: [date]

### Baseline vs Optimized

| Metric | Baseline | Optimized | Change |
|--------|----------|-----------|--------|
| File Size | [MB] | [MB] | [ratio]x compression |
| Latency (mean) | [ms] | [ms] | [speedup]x faster |
| Latency (P95) | [ms] | [ms] | [speedup]x faster |
| Memory (peak) | [MB] | [MB] | [reduction]x smaller |
| Accuracy ([metric]) | [value] | [value] | [delta] ([status]) |
| Throughput | [fps] | [fps] | [improvement]x |

### Optimization Steps Applied

| Step | Input | Output | Size | Latency | Accuracy |
|------|-------|--------|------|---------|----------|
| 1. [step] | [file] | [file] | [MB] | [ms] | [value] |
| 2. [step] | [file] | [file] | [MB] | [ms] | [value] |

### Verdict

[PASS/FAIL]: Accuracy delta of [N]% is [within/outside] the [N]% tolerance.
Speedup: [N]x. Compression: [N]x.

### Deployment Artifact

- Model file: [path]
- Metadata: [path]
- Preprocessing config: [input_shape, dtype, normalization]
```

### Tradeoff Table

```markdown
## Optimization Tradeoff Analysis: [Model Name]

| Variant | Format | Precision | Size (MB) | Latency (ms) | Accuracy | Speedup | Acc. Delta |
|---------|--------|-----------|-----------|-------------|----------|---------|-----------|
| Baseline | [fmt] | FP32 | [size] | [lat] | [acc] | 1.0x | 0.0% |
| ONNX Simplified | ONNX | FP32 | [size] | [lat] | [acc] | [x] | [%] |
| TensorRT FP16 | TRT | FP16 | [size] | [lat] | [acc] | [x] | [%] |
| TensorRT INT8 | TRT | INT8 | [size] | [lat] | [acc] | [x] | [%] |
| TFLite Float16 | TFLite | FP16 | [size] | [lat] | [acc] | [x] | [%] |
| TFLite INT8 | TFLite | INT8 | [size] | [lat] | [acc] | [x] | [%] |

**Recommendation**: [variant] provides [speedup]x speedup with only [delta]% accuracy loss.
```

## AI Discipline Rules

### CRITICAL: Never Skip Baseline Profiling

Before applying any optimization:
1. The original model MUST be loaded and tested
2. Latency MUST be measured with 100+ inference iterations and warmup
3. Accuracy MUST be measured on the designated test dataset
4. All baseline numbers MUST be recorded in the state block

```
WRONG: "MobileNetV2 is typically about 30ms on this device, so let's quantize."
RIGHT: "Measured MobileNetV2 baseline: mean=34.2ms, P95=37.1ms, accuracy=71.8% top-1."
```

### CRITICAL: Validate Preprocessing Compatibility

After every format conversion, verify that preprocessing produces correct inputs:

```python
# ALWAYS verify after conversion
input_details = interpreter.get_input_details()[0]
expected_shape = tuple(input_details['shape'])
expected_dtype = input_details['dtype']

assert input_data.shape == expected_shape, \
    f"Shape mismatch: {input_data.shape} vs expected {expected_shape}"
assert input_data.dtype == expected_dtype, \
    f"Dtype mismatch: {input_data.dtype} vs expected {expected_dtype}"

# INT8 models: input is uint8 (0-255), NOT float32 (0.0-1.0)
# Float models: input is float32 (0.0-1.0) unless model-specific
```

### CRITICAL: Report Accuracy Degradation Immediately

If accuracy drops beyond the stated tolerance:

```
1. STOP the optimization pipeline
2. Report the exact numbers to the user
3. Present alternatives (less aggressive quantization, mixed precision, QAT)
4. Let the user decide whether to accept the tradeoff
5. NEVER proceed silently past an accuracy violation
```

### CRITICAL: Benchmark on Target Hardware When Available

```
Host machine numbers are estimates, NOT deployment metrics.

If target hardware is available:
  - ALL latency benchmarks MUST run on the target device
  - Set power mode explicitly (Jetson: nvpmodel, RPi: governor)
  - Lock clock frequencies for reproducibility
  - Run sustained load test (5+ minutes) to catch thermal throttling

If target hardware is unavailable:
  - Label ALL results as "Host Estimate (not target hardware)"
  - Accuracy measurements are still valid (platform-independent)
  - Latency numbers may differ 2-10x on actual target hardware
```

## Anti-Patterns Table

| Anti-Pattern | Why It Fails | Correct Approach |
|--------------|-------------|------------------|
| Optimizing without baseline measurement | Cannot quantify improvement; may ship a regression | Always profile the original model first |
| Stacking multiple optimizations at once | Cannot attribute accuracy loss to a specific change | Apply one optimization, benchmark, then decide |
| Using random data for INT8 calibration | Quantization ranges will not match real data distribution | Use 500-1000 representative samples from the target domain |
| Reporting mean latency only | Hides tail latency spikes from thermal throttling | Report P50, P95, P99, and run sustained load tests |
| Assuming FP16 is lossless | Some models with large dynamic ranges lose accuracy at FP16 | Always validate accuracy after FP16 conversion |
| Deleting the original model after optimization | Cannot re-optimize or debug accuracy issues later | Keep original model; use descriptive names for variants |
| Building TensorRT engine on x86 for ARM target | TensorRT engines are architecture-specific | Build engines on the target device or matching architecture |
| Quantizing the entire model uniformly to INT8 | Some layers (attention, final classifier) are INT8-sensitive | Run per-layer sensitivity analysis; use mixed precision |

## Error Recovery

### Calibration Dataset Too Small

```
Problem: INT8 quantization produces inconsistent or degraded accuracy.
Actions:
1. Increase calibration dataset to 500-1000 samples
2. Ensure samples cover the full input distribution (all classes, lighting conditions, etc.)
3. Avoid using training data augmentations in calibration data
4. Try a different calibration algorithm (Entropy vs MinMax)
5. Compare INT8 outputs against FP32 outputs on calibration samples
```

### ONNX Export Produces Invalid Model

```
Problem: ONNX model fails validation or produces wrong outputs.
Actions:
1. Run onnx.checker.check_model() for structural validation
2. Compare ONNX output against original framework output on same input
3. Try a different opset version (lower is more compatible, higher has more ops)
4. Simplify with onnxsim before further conversion
5. Check for unsupported dynamic operations and replace with static alternatives
```

### Latency Target Not Met After All Optimizations

```
Problem: Model is still too slow after quantization and conversion.
Actions:
1. Review the profiling breakdown -- which stage is the bottleneck?
2. Reduce model input resolution (e.g., 640x640 to 320x320)
3. Switch to a smaller model architecture (e.g., YOLOv8n instead of YOLOv8s)
4. Apply structured pruning to reduce channel counts
5. Consider model distillation to a smaller student architecture
6. Accept a lower FPS target if accuracy requirements are non-negotiable
```

## Integration with Other Skills

- **`edge-cv-pipeline`** -- After optimizing a model, use `edge-cv-pipeline` to build the complete inference pipeline with camera capture, preprocessing, postprocessing, and result publishing. The optimized model from this skill becomes the inference engine in the CV pipeline.

- **`jetson-deploy`** -- After optimizing a model for Jetson, use `jetson-deploy` to containerize the deployment, manage TensorRT engine building on-device, configure power modes, and set up monitoring with tegrastats and jtop.

## Reference Files

- [Quantization Workflows](references/quantization-workflows.md) -- INT8/FP16 quantization strategies, PTQ vs QAT, calibration dataset requirements, per-layer sensitivity analysis
- [Conversion Pipelines](references/conversion-pipelines.md) -- Model conversion pipelines: PyTorch to ONNX to TensorRT, TensorFlow to TFLite, ONNX Runtime optimization, dynamic batching
