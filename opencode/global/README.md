# OpenCode Global Config

## What this is

| File | Installs to | Purpose |
|---|---|---|
| `AGENTS.md` | `~/.config/opencode/AGENTS.md` | Global instructions, sent with every request in every project |
| `opencode.json` | `~/.config/opencode/opencode.json` | Permissions, MCP servers, agent temperatures |

## Installation

The script installs agents, skills and commands; copy the global config yourself so you can edit
it before it takes effect.

```bash
# 1. Agents, skills and commands (idempotent — re-run to refresh)
bash ../../scripts/install-opencode.sh

# 2. Global config (one-time; review before copying over an existing file)
cp AGENTS.md ~/.config/opencode/AGENTS.md
cp opencode.json ~/.config/opencode/opencode.json
```

Then add your providers to `~/.config/opencode/opencode.json` and enable the MCP servers you use
(all ship commented out). Replace `YOUR_USERNAME` in the Snyk block if you enable it.

## What's in AGENTS.md

A short file (~4.4 KB) because it is sent with every request — at local-model context sizes, every
token the instructions spend is taken from the work.

- **Knowledge base (OpenCode)** — how to search `grounded-code-mcp` through its MCP tools, and when
  to prefer the Microsoft Learn MCP.
- **Shared core** — byte-identical with the Claude Code and Pi globals (checked by
  `tools/skill-evals` rule SK061): interactive vs non-interactive mode, read-before-edit, look APIs
  up instead of recalling them, tests define done, boundaries, security, language defaults.
- **Git** — read-only is fine; every state-changing command is proposed and waits for a yes.

There is deliberately **no "wait for confirmation before starting" gate**: `opencode run` and
subagents have no human to answer it, so they would stall. Interactive sessions still state the task
and constraints first. Session-boot steps a project needs (read `intent.md`, `constraints.md`) belong
in that project's `AGENTS.md` — see `project-templates/`.

## opencode.json highlights

- **Permissions** — secrets, keys, certificates and production config are denied for read; `bash`
  defaults to `ask`, with build/test and read-only git pre-allowed; privilege escalation, `curl`,
  `wget`, inline interpreters (`python -c`, `bash -c`) and destructive commands are denied.
- **Known limit** — permission patterns match by prefix and do not parse `|`, `;` or `&&`, so a
  command chained inside an allowed prefix is not caught. Read proposed commands before approving.
- **MCP servers** — Microsoft Learn, grounded-code-mcp (local or remote), Playwright, Semgrep, Snyk
  and Atlassian, all commented out; enable what you use.
- **Agent temperatures** override each model's recommended sampling; remove a line to use the
  model's default. `plan` and `explore` cap `steps` so a looping local model stops.
- **Optional agent routing** (commented out) — pin a cloud model to an `escalate` primary agent so
  reaching cloud is a deliberate Tab switch, and send the hidden `title` / `summary` / `compaction`
  calls to a small, cheap model.
- **Personal additions** — keep machine- or person-specific instructions out of the shared
  `AGENTS.md`; add `"instructions": ["/path/to/your/personal.md"]` to your installed config.

**Scripting `opencode run`:** OpenCode takes its project directory from the `PWD` environment
variable, not the process's working directory. A script that changes directory without updating
`PWD` (for example Python's `subprocess.run(cwd=...)`) makes OpenCode read and **edit files in the
caller's directory**. Set `PWD` to the target directory in the child environment.

## Local models (Ollama)

Use the Pi guide, [`pi/global/README.md`](../../pi/global/README.md) — the Ollama setup is the same
for every harness: pick the vendor's build for your hardware, and set the context window on the
server (`OLLAMA_CONTEXT_LENGTH`, recommended) or in a Modelfile (`num_ctx`). OpenCode reaches Ollama
through the OpenAI-compatible `/v1` endpoint, which cannot set the context window per request.

OpenCode provider entries for a local Ollama host and Ollama Cloud:

```jsonc
"provider": {
  "ollama-local": {
    "npm": "@ai-sdk/openai-compatible",
    "name": "Local Ollama",
    "options": { "baseURL": "http://YOUR-OLLAMA-HOST:11434/v1", "apiKey": "ollama" },
    "models": {
      "flint:40b-a2b-qat-int4": {
        "name": "Flint 40B-A2B qat-int4",
        "tool_call": true,
        "reasoning": true,
        "limit": { "context": 131072, "output": 32768 }
      }
    }
  },
  "ollama-cloud": {
    "npm": "@ai-sdk/openai-compatible",
    "name": "Ollama Cloud",
    "options": { "baseURL": "https://ollama.com/v1", "apiKey": "{env:OLLAMA_API_KEY}" }
  }
}
```

Then pin models per agent, e.g. `"build": { "model": "ollama-local/flint:40b-a2b-qat-int4" }`.

Set `limit.output` explicitly (32768 for reasoning models): too low and replies are cut off
mid-file; unset and OpenCode may request more than a local server accepts. `limit.context` is
OpenCode's own budget — it does not change the server's context window.

## Optional dependencies

| Feature | What you need |
|---|---|
| Knowledge grounding | [grounded-code-mcp](https://github.com/michaelalber/grounded-code-mcp) running locally |
| Microsoft docs | Microsoft Learn MCP (public endpoint; uncomment it in `opencode.json`) |
| Security scanning | [Snyk CLI](https://docs.snyk.io/snyk-cli/install-or-update-the-snyk-cli) or Semgrep |
