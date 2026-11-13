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
`/skill:<name> <args>` — which is exactly what this toolkit's 4 non-injecting commands do (they are
four-line wrappers reading "use the X skill, subject: $ARGUMENTS"). Porting those would duplicate a
built-in. The other 18 commands inject live shell state with `` !`cmd` ``, and Pi prompt templates
take arguments only, so a port would ship them degraded: a template can *ask* the model to run
`git diff` first, but injection exists for determinism — the state is guaranteed present before the
model reasons — and a local model is likelier to skip or truncate that step. Closing that gap needs
a Pi extension registering a command with real injected state, not a template.

This guide configures Pi for the **20B+ tier** (24–32B dense or a comparable MoE). Smaller models
are below the floor for agentic coding — keep them for non-agentic roles (FIM, autocomplete).

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

# Recommended before starting the server
export OLLAMA_CONTEXT_LENGTH=131072   # see Step 2 — Pi cannot set the context per request
export OLLAMA_KV_CACHE_TYPE=q8_0      # roughly halves KV-cache memory vs FP16
export OLLAMA_KEEP_ALIVE=30m
ollama serve &

# Pull the default model (Apple Silicon build) and, optionally, the Gemma fallback
ollama pull flint:40b-a2b-qat-int4
ollama pull gemma4:31b-nvfp4
```

**Pick the build the vendor recommends for your hardware.** The same model can differ ~9× in
speed between builds: on an M4 Pro, Flint's `gguf-nvfp4` build ran ~11 tok/s and its `qat-int4`
build ~95 tok/s. Hub labels can mislead — check the vendor's README.

To persist the environment via systemd (Linux):

```bash
sudo systemctl edit ollama
# Add under [Service]:
# Environment="OLLAMA_CONTEXT_LENGTH=131072"
# Environment="OLLAMA_KV_CACHE_TYPE=q8_0"
# Environment="OLLAMA_KEEP_ALIVE=30m"
sudo systemctl restart ollama
```

---

## Step 2 — Give the Models the Right Context Window

**This step is critical.** Pi talks to Ollama through its OpenAI-compatible `/v1` endpoint, which
**cannot set the context window per request**. Without an override the model runs at Ollama's
small default, which tool schemas plus the system prompt fill before you type anything — tool
calls then fail or the agent "forgets" files it just read.

**Recommended — server-wide:** set `OLLAMA_CONTEXT_LENGTH=131072` on the server (Step 1). Every
model, including the base tags the shipped `models.json` lists, then runs at 128K. Nothing to build.

**Alternative — per model:** if you can't change the server, bake `num_ctx` (plus vendor sampling)
into an `-agent` variant, and add its id to `models.json`:

```bash
ollama create flint-agent      -f pi/global/Modelfile-flint-agent
ollama create gemma4-31b-agent -f pi/global/Modelfile-gemma4-agent
```

`contextWindow` in `models.json` tells Pi how much context to budget for; it does **not** change
the context the Ollama server allocates.

**Do not add a `TEMPLATE` block** to a Modelfile. `FROM` inherits the model's own renderer/parser,
which handles thinking blocks and tool-call parsing; a hand-written template breaks tool calling.

---

## Step 3 — Configure Pi's Model Provider

The install script copies `models.json` to `~/.pi/agent/models.json` (fresh installs only). Pi
reads it at startup and via `/model`.

It defines two providers — `ollama` (your local/LAN host) and `ollama-cloud` (escalation /
fallback; prompts leave your network). **Set `baseUrl` on `ollama` to your Ollama host and
delete entries for models you have not pulled.** A minimal local entry:

```json
{
  "providers": {
    "ollama": {
      "baseUrl": "http://YOUR-OLLAMA-HOST:11434/v1",
      "api": "openai-completions",
      "apiKey": "ollama",
      "compat": {
        "supportsDeveloperRole": false,
        "supportsReasoningEffort": true,
        "supportsUsageInStreaming": false,
        "maxTokensField": "max_tokens"
      },
      "models": [
        {
          "id": "flint:40b-a2b-qat-int4",
          "name": "Flint 40B-A2B qat-int4",
          "reasoning": true,
          "input": ["text"],
          "contextWindow": 131072,
          "maxTokens": 32768
        }
      ]
    }
  }
}
```

- The `id` must match `ollama list` exactly (the base tag with the server-wide setting, or the
  `-agent` name if you built one in Step 2).
- Cloud entries without `contextWindow` / `maxTokens` fall back to Pi's defaults (128000 / 16384).
- **`maxTokens` is the per-reply output cap. Keep it at 32768 for reasoning models.** At 8192,
  replies that think and then write a whole file get cut off (`stopReason: "length"`), and in a
  non-interactive run that ends the session early — it looks like the model gave up.

---

## Step 4 — Install AGENTS.md and settings.json

`install-pi.sh` handles this (copy-if-absent — existing files are never overwritten). What gets
installed:

| File | Destination | Purpose |
|------|-------------|---------|
| `AGENTS.md` | `~/.pi/agent/AGENTS.md` | Global coding rules — short and agent-loop-safe |
| `models.json` | `~/.pi/agent/models.json` | Ollama provider config |
| `settings.json` | `~/.pi/agent/settings.json` | Default model, thinking level, compaction tuned for local models |

`AGENTS.md` is deliberately short (~3.7 KB) because it is sent with every request: interactive vs
non-interactive mode, when to search the knowledge base, tests-define-done, boundaries, and
language defaults. It has no "wait for confirmation" gate, so `pi -p` runs and scripts don't stall.
Pi merges it with any project-root `AGENTS.md` (global → parent dirs → current dir).

**Thinking level:** `settings.json` ships `"defaultThinkingLevel": "medium"` (Pi's own default).
The shipped models are reasoning models; set `"off"` only for a model that should not think.

**Why custom compaction?** Pi's default compaction settings (`reserveTokens: 16384`,
`keepRecentTokens: 20000`) were designed for cloud models with 200K+ windows. On a small window
they exceed the available context and compaction loops. The included settings correct this:

| Context window | reserveTokens | keepRecentTokens |
|----------------|---------------|-----------------|
| 128K — **shipped** | 4,096 | 24,576 |
| 32–40K | 2,048 | 8,192 |

---

## Step 5 — Per-Project Context Stack

Pi reads `AGENTS.md` from the project root automatically. Copy and fill in the files that apply:

```bash
# Project context stack (from project-templates/ — see project-templates/README.md)
cp project-templates/AGENTS.md      /path/to/your-project/AGENTS.md
cp project-templates/intent.md      /path/to/your-project/intent.md
cp project-templates/constraints.md /path/to/your-project/constraints.md
cp project-templates/evals.md       /path/to/your-project/evals.md

# Multi-session / dark factory work only
cp project-templates/domain-memory.md /path/to/your-project/domain-memory.md
```

The global `AGENTS.md` has no session-boot gate (it would stall non-interactive `pi -p` runs). If a
project needs `intent.md` / `constraints.md` read first, say so in that project's `AGENTS.md`.

**Token budget:** Strip all comment blocks from these files before committing. Every token in
every file loads on session boot. Lean files = more context left for actual work.

---

## Model Selection — You Pick the Model

**Pi runs one model that you choose — there is no automatic per-task model switching.**
The model Pi launches with is `defaultModel` (+ `defaultProvider`) in
`~/.pi/agent/settings.json` (shipped default: `ollama/flint:40b-a2b-qat-int4`). Change it during a session
with `/model` (Ctrl+L), or cycle favorites with Ctrl+P. Start with a specific model from the shell
with `pi --model <provider>/<id>`.

Shipped local models — measured in the author's bake-off (M4 Pro, 48 GB; six hard multi-file
tasks in C#, Python and PHP; 30 runs each at temperature 0, November 2026):

| Model | Type | Passed | Speed | Peak memory (32K ctx) | Best for |
|-------|------|--------|-------|-----------------------|----------|
| `flint:40b-a2b-qat-int4` (Flint 40B-A2B, Recursive) | MoE, ~2.5B active | 30/30 | ~95 tok/s | ~29 GB | **Default** — agentic coding |
| `gemma4:31b-nvfp4` (Google) | 31B dense | 30/30 | ~33 tok/s | ~30 GB | Reliable, slower fallback |
| `gemma4:26b-nvfp4` (Google) | 26B | 28/30 | ~65 tok/s | ~25 GB | Image input (screenshots, diagrams) |

These are a starting point, not a ranking — the field moves monthly. Benchmark candidates on your
own tasks and hardware (`tools/ollama-evals/` helps), and swap the `models.json` entries (and any
Modelfile `FROM` line) for whatever wins.

**The agentic floor is 20B+.** Under 7B, tool-selection accuracy collapses; 7B itself picks tools
acceptably but cannot sustain a multi-step loop.

---

## AGENTS.md Architecture — one global + a project overlay

This toolkit ships **one self-contained global file**, installed as `~/.pi/agent/AGENTS.md`. Pi
merges it with any project-root `AGENTS.md` (global → parent dirs → current dir):

```
pi/global/AGENTS.md  ──→  ~/.pi/agent/AGENTS.md   ← global baseline (always loaded)

./AGENTS.md (project root)                            ← project overlay (from project-templates/)
                                                         project-specific context, merged on top
```

- **`AGENTS.md`** — short, agent-loop-safe rules (~3.7 KB): interactive vs non-interactive mode, grounding trigger, tests-define-done, boundaries, language defaults. Target tier 20B+.

**Workflow:** `install-pi.sh` installs `AGENTS.md`. Add a project-root `AGENTS.md` (copy from
`project-templates/AGENTS.md`) for repo-specific context — language versions, framework rules, which
knowledge-base collections apply.

The global file is loaded once at session start and does not reload when you switch models with
`/model` mid-session.

---

## Memory Planning

Measured peak memory at a 32K context is in the model table above. A larger `num_ctx` adds
KV cache on top: plan headroom, raise the macOS GPU memory limit on Apple Silicon if needed, and
lower `OLLAMA_CONTEXT_LENGTH` (or a Modelfile's `num_ctx`) if a model at 131072 does not fit. `OLLAMA_KV_CACHE_TYPE=q8_0`
roughly halves KV-cache memory compared to FP16.

---

## Pi File Reference

| File | Location | Purpose |
|------|----------|---------|
| `AGENTS.md` | `~/.pi/agent/` or project root | Agent instructions (merged from all levels) |
| `models.json` | `~/.pi/agent/` or `.pi/` | Provider and model definitions |
| `settings.json` | `~/.pi/agent/` or `.pi/` | Default model, thinking level, compaction |
| `Modelfile-flint-agent` | (optional, `ollama create`) | Flint 40B-A2B: 128K context + vendor sampling, when the server context can't be set |
| `Modelfile-gemma4-agent` | (optional, `ollama create`) | Gemma 4 31B/26B: 128K context + vendor sampling, when the server context can't be set |

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
| Tool calls fail; agent forgets files it just read | Model running at Ollama's small default context | Set `OLLAMA_CONTEXT_LENGTH` on the server, or `num_ctx` in a Modelfile (Step 2). `contextWindow` in models.json does not change it |
| Run ends early mid-task; replies cut off mid-file | `maxTokens` too low (`stopReason: "length"`) | Raise `maxTokens` in models.json (32,768 shipped) |
| `max_tokens` error | `maxTokens` above what the model or server accepts | Lower it for that model |
| Very slow generation (~10 tok/s on a 30B-class MoE) | Wrong build for your hardware | Use the vendor's recommended build (e.g. `qat-int4` on Apple Silicon) |
| Agent loops — many turns, little output, no progress | Model-specific failure mode | Stop it, narrow the prompt, or switch models; more turns rarely help |
| Unwanted thinking blocks | Thinking enabled for a model that shouldn't think | Set `defaultThinkingLevel` (or `modelThinkingLevels` per model) to `"off"` — never hand-roll a TEMPLATE |
| Tool calls malformed after a rebuild | A custom `TEMPLATE` block overrode the model's renderer/parser | Drop the `TEMPLATE` block and rebuild; `FROM` inherits the correct one |
| Compaction loops immediately | Default `reserveTokens` exceeds the context window | Use the included `settings.json` |
| Model not found in `/model` | `id` in models.json doesn't match `ollama list` | Use the exact name, including `:latest` |

---

## Upstream Docs

Pi is the authority on its own config surface — this guide only covers the Ollama-local setup.
When the two disagree, upstream wins; open an issue here so this guide gets corrected.

| Page | Covers | Used by this guide |
|------|--------|--------------------|
| [Settings](https://pi.dev/docs/latest/settings) | `settings.json` schema, global vs. project precedence | Step 4 (compaction, `defaultModel`, thinking) |
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
