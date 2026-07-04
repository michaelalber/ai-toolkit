# 🧰 Local AI Toolkit Cheatsheet

> An example **local-first AI stack**, all backed by a single **local Ollama host**
> (`http://<your-ollama-host>:11434` — a Mac Mini, a spare workstation, or any always-on box on your LAN).
> Tools: VibeTyper · Open WebUI · Pi · OpenCode · Goose
>
> Companion: [`LOCAL-FIRST-WORKFLOW.md`](LOCAL-FIRST-WORKFLOW.md) — the routing rule, escalation
> triggers, and prompting shifts behind the local/cloud split this cheatsheet assumes.

## The one-line mental model

**VibeTyper is *input*. The other four are *where the work happens*** — split by interaction
style: chat, interactive coding, a scoped project, and autonomous doing.

## ⚡ Quick decision guide

| I want to…                                                | Use                              |
| --------------------------------------------------------- | -------------------------------- |
| **Talk instead of type** (into *any* app)                 | **VibeTyper**                    |
| **Chat / ask / brainstorm / compare**                     | **Open WebUI**                   |
| **Write, refactor, debug code** interactively             | **Pi** (or Continue in JetBrains) |
| Code on a **scoped project** (isolated toolchain/billing) | **OpenCode**                     |
| **"Go *do* this multi-step task on my machine"**          | **Goose**                        |

---

## 🎙️ VibeTyper — voice dictation (the input layer)

Speech-to-text that pastes into whatever app is focused. **Not an Ollama client** — it has its own
transcription + formatter, so no local model applies. It *feeds* the other tools.

- Dictate a chat/email message hands-free → auto-formatted text pasted in.
- Speak a long prompt **into your coding agent or chat UI** instead of typing.
- Real-time transcription with grammar auto-clean while you talk.

## 💬 Open WebUI — chat & Q&A

Browser chat UI (default `http://127.0.0.1:3000`). Best for exploration, explanations, and
comparisons — not editing your codebase.

- **Good models:** a general tool-capable chat model (e.g. `gpt-oss:20b`, `gemma4:31b`); a
  domain-tuned model for a specific stack (e.g. `phi4:14b` for .NET/Microsoft Q&A).
- **Examples:**
  - "Compare Postgres partitioning strategies for a 500M-row table."
  - Paste a stack trace → "what are the likely causes?"

## 🤖 Pi — primary coding agent

Your main in-terminal dev agent: interactive coding, refactors, debugging in a repo.

- **Config:** `~/.pi/agent/` — set the default provider to your local Ollama host and pick a
  coder model as the default; keep thinking off for the tool loop.
- **Good models:** a ~30B coder for building, a ~32B general model for planning.
- **Suggested shell aliases** (define your own in your shell rc — keep personal ones out of a
  shared repo): a short alias for local Pi, one for a cloud-escalation model, and helpers that
  query your knowledge base / RAG and paste the results in as grounding context.
- **Examples:**
  - In a repo: "refactor this module to async, keep the tests green."
  - Hand a big multi-file task to a larger cloud model via your escalation alias.

## 🏛️ OpenCode — scoped-project agent

Handy when you want to **scope an agent to a single project** — an isolated toolchain, or a
separate billing boundary (e.g. a work project on its own subscription-backed cloud model).

- **Config:** `~/.config/opencode/opencode.json`.
- **Agent → model:** route `build`/`plan`/`general`/`explore` to local models by default;
  reserve a named `escalate` agent on a larger cloud model for the hard 20% (multi-file,
  architecture, hard debugging). See [`LOCAL-FIRST-WORKFLOW.md`](LOCAL-FIRST-WORKFLOW.md).

## 🪿 Goose — autonomous task runner

Give it a *goal*; it plans and executes across shell + files + tools (with approval each step).
This is the "do-er," not a code-completer — keep it out of the interactive-coding lane.

- **Config:** `~/.config/goose/config.yaml` → a ~32B reasoning model, `approve` mode.
- **Good model:** a ~32B general model (reasoning + clean tool-calls); swap to a coder model for
  code-heavy runs.
- **Invoke:** desktop app · `goose session` (interactive) · `goose run -t "…"` (one-shot).
- **Examples:**
  - `goose session` → "set up this project, install deps, run the test suite, fix failures."
  - `goose run -t "reorganize the files in ./exports by month into subfolders."`

---

## 🧠 Model quick-reference

Roles and representative open models — substitute equivalents that fit your hardware and policy.

| Model (example)                              | Sweet spot                              |
| -------------------------------------------- | --------------------------------------- |
| `qwen3-coder:30b` (or an agent-tuned variant) | Coding agent                            |
| `qwen3:32b`                                  | Planning / orchestration                |
| `qwen3:30b-a3b`                              | Fast general / explore                  |
| `gpt-oss:20b` · `gemma4:31b` · `granite4.1:30b` | Tool-capable general models (chat or agent) |
| `phi4:14b`                                   | Domain chat, no tools (e.g. .NET/MS Q&A) |
| `devstral-small:24b`                         | Titles / summaries / compaction         |
| `qwen2.5-coder:7b`                           | Fast autocomplete / FIM (Continue, IDE) |
| `snowflake-arctic-embed2`                    | Embeddings (RAG / grounding)            |

> Check each model's licence and provenance against your own organisation's policy before use.

---

**Rule of thumb:** *Dictate with VibeTyper → think in Open WebUI → build in Pi (scoped project →
OpenCode) → let Goose do the multi-step chores.*
