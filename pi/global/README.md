# Pi + Ollama Setup Guide

Pi ([pi.dev](https://pi.dev)) is a minimal, privacy-first terminal coding agent. Unlike Claude Code (Anthropic subscription) or OpenCode (cloud providers), Pi's sweet spot is **local inference via Ollama** — zero API cost, fully offline, no data leaves your machine.

This guide configures Pi for the best local experience at two model tiers: 7B (8 GB VRAM) and 20B (16–24 GB VRAM).

---

## Quick Start

```bash
# From the ai-toolkit repo root
bash scripts/install-pi.sh          # 7B-safe default
bash scripts/install-pi.sh --full   # 20B variant
```

Then follow the five steps below.

---

## Step 1 — Install Ollama and Pull a Model

```bash
# Install Ollama (Linux/macOS)
curl -fsSL https://ollama.com/install.sh | sh

# Required: enable KV cache quantization before starting the server
export OLLAMA_KV_CACHE_TYPE=q8_0
export OLLAMA_KEEP_ALIVE=30m
ollama serve &

# Pull your model
ollama pull qwen2.5-coder:7b    # 7B — 8 GB VRAM
ollama pull devstral:24b         # 20B+ — 16–24 GB VRAM
```

**Why `OLLAMA_KV_CACHE_TYPE=q8_0`?** It halves KV cache VRAM, letting you run a 32K context window on 8 GB instead of needing 16 GB. Without it you're stuck at Ollama's 4K default — too small for reliable tool calling.

To persist via systemd:

```bash
sudo systemctl edit ollama
# Add under [Service]:
# Environment="OLLAMA_KV_CACHE_TYPE=q8_0"
# Environment="OLLAMA_KEEP_ALIVE=30m"
sudo systemctl restart ollama
```

---

## Step 2 — Create a Custom Model with the Right Context Window

**This step is critical.** Ollama's default context is 4,096 tokens. Pi injects tool schemas + system prompt + conversation history on every request — this saturates 4K before you type a single prompt. Tool calls silently fail.

```bash
# 7B model with 32K context
ollama create my-coder-7b -f pi/global/Modelfile-7b

# 20B+ model with 64K context
ollama create my-coder-20b -f pi/global/Modelfile-20b
```

The Modelfiles set `num_ctx`, cap output tokens, and tune temperature for code. Edit the `FROM` line to swap models.

---

## Step 3 — Configure Pi's Model Provider

The install script copies `models.json` to `~/.pi/agent/models.json`. Pi reads this at startup and via the `/model` command (reloads dynamically — no restart needed).

Edit `~/.pi/agent/models.json` to match the models you actually pulled:

```json
{
  "providers": {
    "ollama": {
      "baseUrl": "http://localhost:11434/v1",
      "api": "openai-completions",
      "apiKey": "ollama",
      "compat": {
        "supportsDeveloperRole": false,
        "supportsReasoningEffort": false
      },
      "models": [
        {
          "id": "my-coder-7b",
          "name": "Qwen 2.5 Coder 7B",
          "input": ["text"],
          "contextWindow": 32768,
          "maxTokens": 2048
        }
      ]
    }
  }
}
```

Use the model `id` you gave `ollama create` (e.g., `my-coder-7b`), not the base model name.

---

## Step 4 — Install AGENTS.md and settings.json

`install-pi.sh` handles this. What gets installed:

| File | Destination | Purpose |
|------|-------------|---------|
| `AGENTS-lite.md` (default) or `AGENTS.md` (--full) | `~/.pi/agent/AGENTS.md` | Global coding rules |
| `models.json` | `~/.pi/agent/models.json` | Ollama provider config |
| `settings.json` | `~/.pi/agent/settings.json` | Compaction tuned for local models |

**Why custom `settings.json`?** Pi's default compaction settings (`reserveTokens: 16384`, `keepRecentTokens: 20000`) were designed for cloud models with 200K+ context windows. On a 32K window they exceed the total available context — compaction triggers immediately and loops. The included settings correct this:

| Model tier | reserveTokens | keepRecentTokens |
|------------|---------------|-----------------|
| 7B (32K ctx) | 2,048 | 8,192 |
| 20B (128K ctx) | 4,096 | 24,576 |

For 20B models, manually update `~/.pi/agent/settings.json` to the 20B values above.

---

## Step 5 — Per-Project Context Stack

Pi reads the following files from the project root automatically. Copy and fill in the ones that apply:

```bash
# Pi-specific system prompt (required — delete the 7B or 20B variant you don't need)
cp pi/global/SYSTEM.md /path/to/your-project/SYSTEM.md

# Project context stack (from project-templates/ — see project-templates/README.md)
cp project-templates/AGENTS.md      /path/to/your-project/AGENTS.md
cp project-templates/intent.md      /path/to/your-project/intent.md
cp project-templates/constraints.md /path/to/your-project/constraints.md
cp project-templates/evals.md       /path/to/your-project/evals.md

# Multi-session / dark factory work only
cp project-templates/domain-memory.md /path/to/your-project/domain-memory.md
```

Pi's Session Boot ritual (in `AGENTS-lite.md`) checks for `intent.md` and `constraints.md` by name — fill them in or the agent will ask on every session start.

**7B token budget:** Strip all comment blocks from these files before committing. Every token in every file loads on session boot. Lean files = more context left for actual work.

---

## Model Selection

| Model | Tier | VRAM (Q4 + 32K) | Context | Tool Calling | Best for |
|-------|------|-----------------|---------|-------------|----------|
| `qwen2.5-coder:7b` | 7B | ~5.5 GB | 32K | Good | Code edits, targeted changes |
| `granite3.3:8b` | 7B | ~6.0 GB | 32K | Excellent | Agentic, tool-heavy workflows |
| `devstral:24b` | 20B+ | ~15 GB | 128K | Excellent | Multi-step agentic workflows |
| `qwen2.5-coder:32b` | 20B+ | ~20 GB | 128K | Excellent | Best code quality locally |
| `phi4-reasoning:14b` | 14B | ~9 GB | 32K | Good | Reasoning tasks (add `"reasoning": true` in models.json) |

**Minimum for reliable tool calling: 7B (8B recommended).** Models under 7B have <60% tool selection accuracy — not suitable for agentic coding.

---

## Layered AGENTS.md Architecture

Pi merges `AGENTS.md` files from three locations (global → parent dirs → current dir). This toolkit uses this to layer instructions by model tier:

```
~/.pi/agent/AGENTS.md        ← Global baseline (AGENTS-lite.md)
                                ~25 rules, 7B-safe, always loaded

./AGENTS.md (project root)   ← Project overlay (AGENTS.md)
                                ~50 rules, 20B-tier, merged on top
```

**7B workflow:** Install the lite version globally. Use only the global file.

**20B workflow:** Install the lite version globally. Copy `AGENTS.md` to your project root — Pi merges both automatically.

**Switching models mid-session:** Use Pi's `/model` command (`Ctrl+L`) or `Ctrl+P` to cycle favorites. AGENTS.md is loaded once at session start and does not reload when you switch models. The lite global file is safe for any model size.

---

## VRAM Quick Reference

For Q4_K_M models with `OLLAMA_KV_CACHE_TYPE=q8_0`. Includes ~0.8 GB overhead.

| Context | 7B model | 14B model | 24B model |
|---------|----------|-----------|-----------|
| 8K | ~5.2 GB | ~9.5 GB | ~15.5 GB |
| 32K | ~5.9 GB | ~10.5 GB | ~17.0 GB |
| 64K | ~7.0 GB | ~12.5 GB | ~20.0 GB |

`q8_0` KV cache roughly doubles your usable context at the same VRAM budget compared to FP16.

---

## Pi File Reference

| File | Location | Purpose |
|------|----------|---------|
| `AGENTS.md` | `~/.pi/agent/` or project root | Agent instructions (merged from all levels) |
| `SYSTEM.md` | Project root | Replaces or appends to Pi's default system prompt |
| `models.json` | `~/.pi/agent/` or `.pi/` | Provider and model definitions |
| `settings.json` | `~/.pi/agent/` or `.pi/` | Compaction, thinking level, default model |
| `Modelfile-*` | (copy to use with `ollama create`) | Context window and parameter templates |

---

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| Tool calls silently fail | Ollama 4K context overflows on first request | Use Modelfile with `num_ctx 32768` |
| `max_tokens` error | `maxTokens` in models.json too high for model | Set `maxTokens: 2048` for 7B |
| Compaction loops immediately | Default `reserveTokens` exceeds context window | Use the included `settings.json` |
| Model not found in `/model` | `id` in models.json doesn't match `ollama create` name | Use the custom model name, not the base model id |
| Streaming stops mid-output | `num_predict` cap hit | Increase in Modelfile |
