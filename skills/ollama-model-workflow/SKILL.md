---
name: ollama-model-workflow
description: Local LLM management with Ollama, Modelfile creation, and benchmarking. Use when pulling models, creating custom Modelfiles, or evaluating model performance locally.
---

# Ollama Model Workflow

> "The best model is the one that runs reliably on the hardware you actually have."
> -- Practical AI Engineering Proverb

## Core Philosophy

This skill manages the full lifecycle of local LLMs through Ollama: selection, pulling, configuration, testing, benchmarking, and deployment. Every decision is grounded in **hardware reality** and **measurable performance**.

**Non-Negotiable Constraints:**
1. Every model selection MUST begin with a VRAM/hardware assessment
2. Every Modelfile MUST be version-controlled with documented parameter rationale
3. Every model MUST be benchmarked before deployment to any workflow
4. Every recommendation MUST include quantization-aware resource estimates
5. Never pull a model without first confirming sufficient disk space and VRAM

## Domain Principles

| # | Principle | Description | Priority |
|---|-----------|-------------|----------|
| 1 | **VRAM-Aware Selection** | Always check available VRAM before recommending or pulling a model. Match model size to hardware capacity with a safety margin. | Critical |
| 2 | **Quantization Tradeoffs** | Understand and communicate the quality/speed/size tradeoff for each quantization level. Lower quantization is not always better. | Critical |
| 3 | **System Prompt Engineering** | Craft SYSTEM prompts that constrain the model to its intended role. Keep prompts concise and unambiguous. | High |
| 4 | **Temperature Tuning** | Match temperature to task type: low for deterministic tasks (code, extraction), higher for creative tasks. Always document the rationale. | High |
| 5 | **Context Window Management** | Set `num_ctx` deliberately. Larger contexts consume more VRAM and slow inference. Size to actual need, not maximum. | High |
| 6 | **Model Comparison Methodology** | Compare models using identical prompts, parameters, and hardware conditions. Never compare across different quantization levels without noting it. | High |
| 7 | **Modelfile Reproducibility** | Every Modelfile must be self-contained and reproducible. Pin base model tags, document all parameter choices. | Critical |
| 8 | **Inference Performance** | Measure tokens/sec, time to first token, and total generation time. Track these across model updates. | High |
| 9 | **Model Versioning** | Tag and track model versions. When Ollama updates a model tag, re-benchmark before adopting. | Medium |
| 10 | **Hardware Matching** | Different hardware (Jetson, consumer GPU, Mac M-series, CPU-only) requires different model choices. Never assume one config fits all. | Critical |

## Workflow

### Ollama Model Lifecycle

```
┌─────────────────────────────────────────────────────────────────┐
│                  OLLAMA MODEL WORKFLOW                          │
│                                                                 │
│  ┌──────────┐   ┌──────┐   ┌───────────┐   ┌──────┐           │
│  │ 1.SELECT │──>│2.PULL│──>│3.CONFIGURE│──>│4.TEST│           │
│  └──────────┘   └──────┘   └───────────┘   └──────┘           │
│       │                          │               │              │
│       │                          │               v              │
│       │                          │         ┌───────────┐        │
│       │                          │         │5.BENCHMARK│        │
│       │                          │         └───────────┘        │
│       │                          │               │              │
│       │                          │               v              │
│       │                          │         ┌──────────┐         │
│       │                          └────────>│ 6.DEPLOY │         │
│       │                                    └──────────┘         │
│       │                                         │               │
│       └─────────────────────────────────────────┘               │
│                    (iterate if needed)                           │
└─────────────────────────────────────────────────────────────────┘
```

### Step 1: Model Selection Decision Tree

```
                    ┌─────────────────┐
                    │ What is the task?│
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              v              v              v
         ┌────────┐    ┌─────────┐    ┌──────────┐
         │ Coding │    │  Chat/  │    │ RAG/Tool │
         │        │    │ General │    │   Use    │
         └───┬────┘    └────┬────┘    └────┬─────┘
             │              │              │
             v              v              v
     codellama/       llama3.1/       mistral/
     deepseek-coder   phi3            nomic-embed
     qwen2.5-coder    gemma2          mxbai-embed
```

### Step 2: Quantization Decision Tree

```
                ┌──────────────────────┐
                │ Available VRAM (GB)? │
                └──────────┬───────────┘
                           │
         ┌─────────┬───────┼────────┬──────────┐
         v         v       v        v          v
      < 4 GB    4-8 GB   8-16 GB  16-24 GB  24+ GB
         │         │       │        │          │
         v         v       v        v          v
     Q4_K_M     Q4_K_M  Q5_K_M   Q8_0      FP16
     (small     (7B     (7-13B   (7-13B    (7-13B
      models)   models)  models)  models)   models)
```

### Steps 3-6: Detailed Phases

**Step 3 - Configure Modelfile:**
1. Choose base model with explicit tag
2. Set PARAMETER values appropriate to task
3. Write SYSTEM prompt constraining behavior
4. Set TEMPLATE if using a non-default chat format

**Step 4 - Test:**
1. Run representative prompts through the model
2. Verify output quality matches expectations
3. Check for instruction following and format compliance

**Step 5 - Benchmark:**
1. Measure tokens/sec with standardized prompts
2. Record time to first token
3. Test at target context window size
4. Compare against baseline or alternative models

**Step 6 - Deploy:**
1. Commit Modelfile to version control
2. Document model selection rationale
3. Record benchmark results for future reference

## State Block Format

Maintain state across conversation turns using this block:

```
<ollama-state>
step: [SELECT | PULL | CONFIGURE | TEST | BENCHMARK | DEPLOY]
model_name: [name]
quantization: [Q4_K_M | Q5_K_M | Q6_K | Q8_0 | FP16]
vram_available_gb: [number]
tokens_per_second: [number or untested]
last_action: [what was done]
next_action: [what's next]
blockers: [issues]
</ollama-state>
```

**Example:**

```
<ollama-state>
step: BENCHMARK
model_name: llama3.1:8b-instruct-q5_K_M
quantization: Q5_K_M
vram_available_gb: 12
tokens_per_second: untested
last_action: Created Modelfile with coding-focused system prompt
next_action: Run benchmark suite with standardized prompts
blockers: none
</ollama-state>
```

## Output Templates

### Model Selection Report

```markdown
## Model Selection Report

**Task**: [description of intended use]
**Hardware**: [GPU model, VRAM, RAM, CPU]

### Hardware Assessment

| Resource | Available | Required (est.) | Status |
|----------|-----------|-----------------|--------|
| VRAM     | [X] GB    | [Y] GB          | OK/WARN|
| Disk     | [X] GB    | [Y] GB          | OK/WARN|
| RAM      | [X] GB    | [Y] GB          | OK/WARN|

### Candidates

| Model | Params | Quantization | VRAM Est. | Fit |
|-------|--------|-------------|-----------|-----|
| [name]| [size] | [quant]     | [GB]      | Y/N |

### Recommendation

**Selected**: [model:tag]
**Rationale**: [why this model for this task and hardware]
```

### Modelfile Creation

```markdown
## Modelfile: [name]

**Base Model**: [FROM value]
**Purpose**: [what this configuration is for]

### Parameters

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| temperature | [val] | [why] |
| top_p | [val] | [why] |
| num_ctx | [val] | [why] |

### Modelfile

\```
FROM [model:tag]

PARAMETER temperature [value]
PARAMETER top_p [value]
PARAMETER num_ctx [value]

SYSTEM """
[system prompt]
"""
\```

### Verification

- [ ] Model created successfully
- [ ] Test prompt produces expected output
- [ ] VRAM usage within budget
```

### Benchmark Results

```markdown
## Benchmark: [model name]

**Date**: [date]
**Hardware**: [specs]
**Quantization**: [level]

### Performance

| Metric | Value |
|--------|-------|
| Tokens/sec (generation) | [X] |
| Time to first token (ms) | [X] |
| Total generation time (s) | [X] |
| Context window tested | [X] |
| VRAM usage (GB) | [X] |

### Quality Assessment

| Test Case | Expected | Actual | Pass |
|-----------|----------|--------|------|
| [case 1]  | [expected]| [actual]| Y/N |

### Comparison (if applicable)

| Model | Tokens/sec | Quality Score | VRAM |
|-------|-----------|---------------|------|
| [A]   | [X]       | [X/10]        | [X]  |
| [B]   | [X]       | [X/10]        | [X]  |
```

## AI Discipline Rules

### CRITICAL: Always Check VRAM Before Pulling

Before recommending or pulling ANY model:

```
STOP! Verify:
1. Available VRAM has been assessed (nvidia-smi, system_profiler, or user-reported)
2. Model VRAM requirement is estimated for the chosen quantization
3. A safety margin of at least 1-2 GB exists
4. Disk space is sufficient for the model download

If VRAM is unknown, ASK before proceeding.
```

Checking VRAM in Python:

```python
import subprocess
import json

def get_vram_info() -> dict:
    """Get GPU VRAM information using nvidia-smi."""
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,memory.total,memory.used,memory.free",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True, check=True
        )
        lines = result.stdout.strip().split("\n")
        gpus = []
        for line in lines:
            name, total, used, free = [x.strip() for x in line.split(",")]
            gpus.append({
                "name": name,
                "total_mb": int(total),
                "used_mb": int(used),
                "free_mb": int(free),
                "free_gb": round(int(free) / 1024, 1)
            })
        return {"gpus": gpus}
    except FileNotFoundError:
        return {"error": "nvidia-smi not found. Check for Mac M-series or CPU-only setup."}
```

### CRITICAL: Never Skip Benchmarking

Every model must be benchmarked before deployment:

```
MANDATORY before deployment:
1. Tokens/sec measured with representative prompts
2. Time to first token recorded
3. Quality verified with task-specific test cases
4. VRAM usage confirmed under budget
5. Results documented in benchmark report

Skipping benchmarks leads to production surprises.
```

### CRITICAL: Always Document Modelfile Parameters

Every PARAMETER in a Modelfile must have a documented rationale:

```
WRONG:
  PARAMETER temperature 0.3

RIGHT:
  # temperature 0.3: Low value chosen for deterministic code generation.
  # Higher values (0.7+) caused inconsistent formatting in testing.
  PARAMETER temperature 0.3
```

### CRITICAL: Never Recommend Models Without Hardware Context

Before any model recommendation:

```
REQUIRED context:
1. Target hardware (GPU model, VRAM, RAM)
2. Task description (coding, chat, RAG, embeddings)
3. Latency requirements (interactive vs batch)
4. Quality requirements (precision needed)

If any context is missing, ASK before recommending.
```

## Anti-Patterns

| Anti-Pattern | Why It Fails | Correct Approach |
|--------------|-------------|------------------|
| Pulling largest model without checking VRAM | OOM crashes, swapping to disk destroys performance | Always assess VRAM first, pick the largest model that fits with margin |
| Using default parameters for all tasks | Temperature 0.8 is wrong for code; num_ctx 2048 is wrong for RAG | Tune parameters to the specific task and document rationale |
| Comparing models at different quantization levels | Q4_K_M vs Q8_0 comparison is meaningless for quality assessment | Compare at same quantization, then compare quantization tradeoffs separately |
| Skipping system prompt in Modelfile | Model behaves unpredictably, inconsistent outputs | Always include a SYSTEM prompt that constrains the model role |
| Not pinning model tags | `ollama pull llama3.1` may get different versions over time | Use explicit tags like `llama3.1:8b-instruct-q5_K_M` |
| Benchmarking with trivial prompts | "Hello world" does not represent production workload | Use representative prompts that match actual deployment scenarios |
| Ignoring time to first token | High tokens/sec means nothing if TTFT is 5 seconds for interactive use | Measure and report TTFT alongside generation speed |

## Error Recovery

### OOM (Out of Memory) Errors

```
Problem: Model fails to load or crashes during inference with OOM
Actions:
1. Check actual VRAM usage: nvidia-smi or ollama ps
2. Reduce num_ctx (halving it roughly halves KV cache VRAM)
3. Switch to a smaller quantization (Q8_0 -> Q5_K_M -> Q4_K_M)
4. Switch to a smaller parameter count model
5. If on shared GPU, check for other processes consuming VRAM
```

### Slow Inference (< 5 tokens/sec)

```
Problem: Generation speed is unacceptably slow
Actions:
1. Verify model is running on GPU, not CPU (ollama ps shows GPU%)
2. Check if model is partially offloaded (too large for VRAM)
3. Reduce num_ctx to lower KV cache overhead
4. Switch to a more aggressive quantization
5. Check for thermal throttling on the GPU
6. On CPU-only: expect 1-5 tok/s for 7B models, this may be normal
```

### Model Corruption or Bad Output

```
Problem: Model produces garbled output, crashes, or behaves erratically
Actions:
1. Remove and re-pull the model: ollama rm [model] && ollama pull [model]
2. Check Modelfile TEMPLATE syntax matches the model's expected format
3. Verify SYSTEM prompt is not conflicting with the template
4. Test with the base model (no Modelfile) to isolate the issue
5. Check Ollama server logs: journalctl -u ollama or ~/.ollama/logs/
```

### Ollama Server Issues

```
Problem: Ollama server not responding, connection refused, or hanging
Actions:
1. Check server status: systemctl status ollama or ollama serve
2. Restart the server: systemctl restart ollama
3. Check port conflicts: lsof -i :11434
4. Review logs for errors: journalctl -u ollama --since "10 minutes ago"
5. Verify sufficient disk space for model storage (~/.ollama/models/)
6. If using API: confirm OLLAMA_HOST environment variable is set correctly
```

### Model Pull Failures

```
Problem: Model download fails, hangs, or produces checksum errors
Actions:
1. Check disk space: df -h ~/.ollama/
2. Retry the pull (network interruptions are common for large models)
3. Check Ollama version: ollama --version (update if outdated)
4. For checksum errors: ollama rm [model] and re-pull
5. Behind proxy: set HTTPS_PROXY environment variable
```

## Integration with Other Skills

- **RAG Pipeline** (`rag-pipeline`): Use this skill to select and configure embedding models (e.g., `nomic-embed-text`, `mxbai-embed-large`) and generation models for RAG workflows. Benchmark embedding throughput and generation quality before integrating into the RAG pipeline.
- **MCP Server Scaffold** (`mcp-server-scaffold`): When building MCP servers that expose LLM capabilities, use this skill to select, configure, and benchmark the backing Ollama model. Ensure the Modelfile is committed alongside the MCP server code.
- **Jetson Deploy** (`jetson-deploy`): For edge deployment on NVIDIA Jetson, use the hardware matching guide to select appropriately sized models and quantizations that fit Jetson VRAM constraints (typically 4-16 GB shared memory).
- **Edge CV Pipeline** (`edge-cv-pipeline`): When combining vision models with LLMs at the edge, use this skill to manage the LLM component while the edge-cv-pipeline handles the vision model. Coordinate VRAM budgets between both models.

## Reference Files

- [Modelfile Reference](references/modelfile-reference.md) - Complete Modelfile syntax, parameters, templates, and examples
- [Quantization and Benchmarks](references/quantization-benchmarks.md) - Quantization levels, VRAM tables, benchmarking methodology, and hardware guide
