# Pi + Ollama Setup Guide

Pi ([pi.dev](https://pi.dev)) is a minimal, privacy-first terminal coding agent — *"a minimal
terminal coding harness… designed to stay small at the core while being extended through TypeScript
extensions, skills, prompt templates, themes, and pi packages."*

OpenCode can also be pointed at a local Ollama endpoint, and Claude Code technically can. Pi's
advantage isn't exclusivity, it's **prompt overhead**: at a 32K–128K window, every token the
harness spends on itself is taken from the work. A small core is the feature, which is why Pi is
this toolkit's first-class local harness.

**What Pi supports natively:** skills (the same `skills/` tree, invocable as `/skill:<name>`),
prompt templates (`~/.pi/agent/prompts/*.md`, arguments but no `!` shell injection), TypeScript
extensions with a deep event surface (`tool_call` can block a call, `tool_result` can rewrite its
output), session trees (`/tree`, `/fork`, `/clone`), and custom providers.

**What it does not:** subagents — the docs state extensions "cannot spawn child agent instances."
So this toolkit's 51 agents are Claude Code / OpenCode only. Multi-phase work is unaffected:
QRSPI and QRASPI phases are artifact-gated, so you drive phase-to-phase yourself. MCP is available
through community extensions; `grounded-code-mcp` also ships a CLI that Pi calls directly, which
is what the installed `AGENTS.md` uses.

**There is no `pi/commands/` directory, by design.** Pi already exposes every skill as
`/skill:<name> <args>` — which is exactly what this toolkit's non-injecting commands do (they are
four-line wrappers reading "use the X skill, subject: $ARGUMENTS"). Porting those would duplicate a
built-in. The other 20 commands inject live shell state with `` !`cmd` ``, and Pi prompt templates
take arguments only, so a port would ship them degraded: a template can *ask* the model to run
`git diff` first, but injection exists for determinism — the state is guaranteed present before the
model reasons — and a local model is likelier to skip or truncate that step. Closing that gap needs
a Pi extension registering a command with real injected state, not a template.

This guide configures Pi for the best local experience at the **20B+ tier** (24–32B dense or a
comparable MoE, 16–24 GB VRAM). Smaller models are below the floor for agentic coding — keep them
for the non-agentic roles (title, summary, FIM, autocomplete).

---

## Quick Start

```bash
# From the ai-toolkit repo root
bash scripts/install-pi.sh
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
ollama pull devstral-small-2:24b    # 20B+ — 16–24 GB VRAM
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
# Dense 20–32B model (Qwen3 32B / 14B — capped at the base model's 40K)
ollama create qwen3-32b-agent -f pi/global/Modelfile-20b

# MoE variant (qwen3:30b-a3b, qwen3-coder:30b — 128K+ context, cheap KV cache)
ollama create qwen3-30b-a3b-agent -f pi/global/Modelfile-moe-agent
```

The Modelfiles set `num_ctx`, cap output tokens, tune temperature for code, and override the Qwen3
chat template to actually honour `/no_think`. Edit the `FROM` line to swap models.

Small utility models (title, summary, FIM) need no Modelfile — `contextWindow` in `models.json`
sets `num_ctx` at request time.

---

## Step 3 — Configure Pi's Model Provider

The install script copies `models.json` to `~/.pi/agent/models.json`. Pi reads this at startup and via the `/model` command (reloads dynamically — no restart needed).

The installed file defines two providers — `ollama-lan` (your local/LAN host) and `ollama-cloud`
(fallback). **Set `baseUrl` on `ollama-lan` to your Ollama host and delete the entries for models
you have not pulled.** Pi passes `contextWindow` as `num_ctx` in the API call, so the 32K/128K
context is applied without a separate Modelfile:

```json
{
  "providers": {
    "ollama-lan": {
      "baseUrl": "http://YOUR-OLLAMA-HOST:11434/v1",
      "api": "openai-completions",
      "apiKey": "ollama",
      "compat": {
        "supportsDeveloperRole": false,
        "supportsReasoningEffort": false,
        "supportsUsageInStreaming": false,
        "maxTokensField": "max_tokens"
      },
      "models": [
        {
          "id": "qwen3-30b-a3b-agent:latest",
          "name": "Qwen3 30B-A3B Agent",
          "input": ["text"],
          "contextWindow": 131072,
          "maxTokens": 8192
        }
      ]
    }
  }
}
```

The `id` must match what `ollama list` shows. If you ran `ollama create qwen3-30b-a3b-agent -f
Modelfile-moe-agent` in Step 2, use that name; if you point at a base model instead, use the base
name. Both set `num_ctx` correctly — the Modelfile bakes it in, `contextWindow` passes it at
request time.

---

## Step 4 — Install AGENTS.md and settings.json

`install-pi.sh` handles this. What gets installed:

| File | Destination | Purpose |
|------|-------------|---------|
| `AGENTS.md` | `~/.pi/agent/AGENTS.md` | Global coding rules — one file, same shape as `claude/global/CLAUDE.md` and `opencode/global/AGENTS.md` |
| `models.json` | `~/.pi/agent/models.json` | Ollama provider config |
| `settings.json` | `~/.pi/agent/settings.json` | Compaction tuned for local models |

`AGENTS.md` is a **single self-contained global**, carrying the full rule set and the grounded-code-mcp collection map. Pi merges it with any project-root `AGENTS.md` (global → parent dirs → current dir).

**Why custom `settings.json`?** Pi's default compaction settings (`reserveTokens: 16384`, `keepRecentTokens: 20000`) were designed for cloud models with 200K+ context windows. On a 32K window they exceed the total available context — compaction triggers immediately and loops. The included settings correct this:

| Model tier | reserveTokens | keepRecentTokens |
|------------|---------------|-----------------|
| 20B+ (128K ctx) — **shipped** | 4,096 | 24,576 |
| 20B+ (40K ctx, dense Qwen3) | 2,048 | 8,192 |

The shipped values match the default `qwen3-coder-30b-agent:latest` (128K). If you switch
`defaultModel` to a 40K-context dense model, lower them to the second row.

---

## Step 5 — Per-Project Context Stack

Pi reads the following files from the project root automatically. Copy and fill in the ones that apply:

```bash
# Pi-specific system prompt (required)
cp pi/global/SYSTEM.md /path/to/your-project/SYSTEM.md

# Project context stack (from project-templates/ — see project-templates/README.md)
cp project-templates/AGENTS.md      /path/to/your-project/AGENTS.md
cp project-templates/intent.md      /path/to/your-project/intent.md
cp project-templates/constraints.md /path/to/your-project/constraints.md
cp project-templates/evals.md       /path/to/your-project/evals.md

# Multi-session / dark factory work only
cp project-templates/domain-memory.md /path/to/your-project/domain-memory.md
```

Pi's Session Boot ritual (in `AGENTS.md`) checks for `intent.md` and `constraints.md` by name — fill them in or the agent will ask on every session start.

**Token budget:** Strip all comment blocks from these files before committing. Every token in every file loads on session boot. Lean files = more context left for actual work.

---

## Model Selection — You Pick the Model

**Pi runs one model that you choose — there is no automatic per-task model switching.**
The model Pi launches with is `defaultModel` (+ `defaultProvider`) in
`~/.pi/agent/settings.json` (shipped default: `qwen3-coder-30b-agent:latest`). Change it
at any time during a session with `/model` (Ctrl+L), or cycle favorites with Ctrl+P. Start
with a specific model from the shell with `pi --model <provider>/<id>`.

> **Optional: automatic per-task routing.** Pi can auto-route each task role (`complex`,
> `plan`, `medium`, `explore`, `title`, `summary`) to a *different* model. That behavior is
> **off by default**. To turn it on, copy `pi/global/router-config.json.example` to
> `~/.pi/agent/router-config.json` (drop the `.example` suffix and the `_README` key). Leave
> it absent to keep single-model manual selection.

| Model | Tier | VRAM (Q4 + 32K) | Context | Tool Calling | Best for |
|-------|------|-----------------|---------|-------------|----------|
| `qwen3-30b-a3b-agent` | 30B MoE | ~18 GB | 128K | Excellent | Default — tool-heavy agentic loops |
| `qwen3-coder-30b-agent` | 30B MoE | ~18 GB | 128K | Excellent | Code generation, edits, completions |
| `qwen3-32b-agent` | 32B dense | ~20 GB | 40K | Excellent | Planning and reasoning-heavy work |
| `devstral-small-2:24b` | 24B | ~15 GB | 128K | Excellent | Multi-step agentic workflows, vision |
| `qwen2.5-coder:7b` | 7B | ~5.5 GB | 32K | Good | **Non-agentic only** — FIM, autocomplete |

**The agentic floor is 20B+.** Under 7B, tool-selection accuracy collapses (<60%); 7B itself picks
tools acceptably but cannot sustain a multi-step loop. Keep small models for the non-agentic roles
(title, summary, FIM, autocomplete).

---

## AGENTS.md Architecture — one global + a project overlay

This toolkit ships **one self-contained global file**, installed as `~/.pi/agent/AGENTS.md`. Pi
merges it with any project-root `AGENTS.md` (global → parent dirs → current dir):

```
pi/global/AGENTS.md  ──→  ~/.pi/agent/AGENTS.md   ← global baseline (always loaded)

./AGENTS.md (project root)                            ← project overlay (from project-templates/)
                                                         project-specific context, merged on top
```

- **`AGENTS.md`** — full rules, quality gates, and the complete grounded-code-mcp collection map. Target tier 20B+.

**Workflow:** `install-pi.sh` installs `AGENTS.md`. Add a project-root `AGENTS.md` (copy from `project-templates/AGENTS.md`) for repo-specific context — it is project context, not a tier overlay.

The global file is loaded once at session start and does not reload when you switch models with `/model` mid-session.

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
| `settings.json` | `~/.pi/agent/` or `.pi/` | Compaction, thinking level, **default model** (the one model Pi runs) |
| `router-config.json.example` | (opt-in — rename to `router-config.json` in `~/.pi/agent/`) | Per-task auto-routing map; **disabled by default** so you pick the model |
| `Modelfile-20b` | (use with `ollama create`) | Dense Qwen3 20–32B: context, params, `/no_think` template |
| `Modelfile-moe-agent` | (use with `ollama create`) | Qwen3 MoE (30b-a3b, coder:30b): 128K context variant |

---

## Project-Type Harnesses (pi-packages)

The global config in this directory installs Pi's **baseline rules and the full skill library**. For project-type harnesses — purpose-built skills, prompt templates, and Modelfiles tuned per language ecosystem — see the companion repo:

**[codeberg.org/michaelkalber/pi-packages](https://codeberg.org/michaelkalber/pi-packages)**

| Package | Stack |
|---------|-------|
| `pi-dotnet` | .NET / C# / ASP.NET Core / EF Core / SQL Server / React |
| `pi-php` | PHP / Laravel / Vue.js |
| `pi-python` | Python / FastAPI / SQLAlchemy / pytest |
| `pi-robotics` | ROS 2 / Python / C++ / edge AI / MuJoCo / Isaac Lab |
| `pi-industrial` | MODBUS / OPC UA / PLC (IEC 61131-3) / SCADA |

Each package adds a `/skill:<type>` command, five prompt templates (`/fix`, `/review`, `/generate`, `/explain`, `/decompose`), and a pre-tuned Modelfile for that stack. Install only what you need:

```bash
pi install git:codeberg.org/michaelkalber/pi-packages/packages/pi-python
pi install git:codeberg.org/michaelkalber/pi-packages/packages/pi-robotics
```

The `project-detect` extension in each package auto-loads the right skill from project signals (`.csproj`, `pyproject.toml`, `package.xml`, etc.).

---

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| Tool calls silently fail | Ollama 4K context overflows on first request | Set `contextWindow` in models.json, or `num_ctx` in a Modelfile |
| `max_tokens` error | `maxTokens` in models.json exceeds the model's limit | Lower it (8,192 for the 20B+ agents) |
| Model "thinks" despite `/no_think` | Base Qwen3 template opens `<think>` unconditionally | Rebuild from `Modelfile-20b` / `Modelfile-moe-agent` — they override the template |
| Compaction loops immediately | Default `reserveTokens` exceeds context window | Use the included `settings.json` |
| Model not found in `/model` | `id` in models.json doesn't match `ollama create` name | Use the custom model name, not the base model id |
| Streaming stops mid-output | `num_predict` cap hit | Increase in Modelfile |

---

## Upstream Docs

Pi is the authority on its own config surface — this guide only covers the Ollama-local setup.
When the two disagree, upstream wins; open an issue here so this guide gets corrected.

| Page | Covers | Used by this guide |
|------|--------|--------------------|
| [Settings](https://pi.dev/docs/latest/settings) | `settings.json` schema, global vs. project precedence | Step 4 (compaction, `defaultModel`) |
| [Custom models](https://pi.dev/docs/latest/models) | `models.json` providers, `compat`, model fields | Step 3 |
| [Custom providers](https://pi.dev/docs/latest/custom-provider) | Non-standard APIs and OAuth | — (Ollama uses `openai-completions`) |
| [Skills](https://pi.dev/docs/latest/skills) | Discovery paths, frontmatter, `/skill:<name>` | The installed `skills/` tree |
| [Prompt templates](https://pi.dev/docs/latest/prompt-templates) | Slash commands that expand to prompts | Why there is no `pi/commands/` |
| [Extensions](https://pi.dev/docs/latest/extensions) | TypeScript tools, commands, events (`tool_call`, `tool_result`) | MCP access; the shell-injection gap |
| [Session format](https://pi.dev/docs/latest/session-format) | JSONL sessions, `SessionManager` | `/tree`, `/fork`, `/clone` |
| [Keybindings](https://pi.dev/docs/latest/keybindings) | Rebinding shortcuts | `/model` (Ctrl+L), favorites (Ctrl+P) |
| [Themes](https://pi.dev/docs/latest/themes) | Terminal appearance | `theme` in `settings.json` |

Config paths (both from the Settings page): `~/.pi/agent/` global, `.pi/` project — project
overrides global, with nested objects merged rather than replaced.
