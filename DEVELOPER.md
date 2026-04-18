# Developer Setup

Prerequisites and tooling required to work with this repository.

---

## Git

**Install**

```bash
# macOS
brew install git

# Linux (apt)
sudo apt install git

# Linux (dnf)
sudo dnf install git

# Windows (winget)
winget install --id Git.Git
```

**Docs**

- [Git downloads](https://git-scm.com/downloads)
- [Reference manual](https://git-scm.com/docs)

---

## Node.js

Node.js is required for Claude Code, OpenCode, Gemini CLI, and Copilot CLI. Use [nvm](https://github.com/nvm-sh/nvm) to manage versions.

**Install nvm**

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
```

**Install Node.js**

```bash
nvm install --lts
nvm use --lts
```

**Docs**

- [Node.js homepage](https://nodejs.org)
- [nvm repository](https://github.com/nvm-sh/nvm)

---

## Python

Python 3.10+ is required for local ML tooling, RAG pipelines, and automation scripts.

**Install**

```bash
# macOS
brew install python@3.13

# Linux (apt)
sudo apt install python3 python3-pip python3-venv

# Linux (dnf)
sudo dnf install python3 python3-pip

# Windows (winget)
winget install --id Python.Python.3
```

**Docs**

- [Python downloads](https://www.python.org/downloads/)
- [Python docs](https://docs.python.org/3/)

---

## Docker

Docker is used for containerized services, local environments, and deployment targets.

**Install**

```bash
# macOS / Windows
# Download Docker Desktop from https://www.docker.com/products/docker-desktop/

# Linux
curl -fsSL https://get.docker.com | sh
```

**Docs**

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Docker Engine (Linux)](https://docs.docker.com/engine/install/)
- [Docker Compose](https://docs.docker.com/compose/)

---

## Ollama

Ollama runs large language models locally — used by skills and agents that target local inference.

**Install**

```bash
# macOS / Linux
curl -fsSL https://ollama.com/install.sh | sh

# Windows
# Download the installer from https://ollama.com/download
```

**Pull a model**

```bash
ollama pull llama3.2
```

**Docs**

- [Ollama homepage](https://ollama.com)
- [Model library](https://ollama.com/library)
- [GitHub repository](https://github.com/ollama/ollama)

---

## Claude Code

Claude Code is Anthropic's official CLI for Claude — used to run agents and skills in this toolkit.

**Install**

```bash
npm install -g @anthropic-ai/claude-code
```

**Authenticate**

```bash
claude login
```

**Docs**

- [Claude Code overview](https://docs.anthropic.com/en/claude-code/overview)
- [Getting started](https://docs.anthropic.com/en/claude-code/getting-started)

---

## OpenCode

OpenCode is an open-source, terminal-based AI coding assistant that supports multiple providers including Anthropic.

**Install**

```bash
npm install -g opencode-ai
```

Or via the install script:

```bash
curl -fsSL https://opencode.ai/install | bash
```

**Docs**

- [OpenCode repository](https://github.com/sst/opencode)
- [OpenCode docs](https://opencode.ai/docs)

---

## GitHub Copilot CLI

GitHub Copilot provides AI-assisted code completions and chat in the terminal.

**Install**

```bash
npm install -g @github/copilot
```

**Authenticate**

```bash
gh auth login
gh extension install github/gh-copilot
```

**Docs**

- [GitHub Copilot](https://github.com/features/copilot)
- [Copilot in the CLI](https://docs.github.com/en/copilot/using-github-copilot/using-github-copilot-in-the-command-line)

---

## Gemini CLI

Google's Gemini CLI provides terminal access to Gemini models for coding assistance and agentic tasks.

**Install**

```bash
npm install -g @google/gemini-cli
```

**Authenticate**

```bash
gemini auth login
```

**Docs**

- [Gemini CLI repository](https://github.com/google-gemini/gemini-cli)
- [Google AI Studio](https://aistudio.google.com/)

---

## GitHub CLI

The GitHub CLI (`gh`) is used for PR creation, issue management, and repository operations.

**Install**

```bash
# macOS
brew install gh

# Linux (apt)
sudo apt install gh

# Linux (dnf)
sudo dnf install gh

# Windows (winget)
winget install --id GitHub.cli
```

**Authenticate**

```bash
gh auth login
```

**Docs**

- [GitHub CLI homepage](https://cli.github.com/)
- [Manual](https://cli.github.com/manual/)
- [Installation guide](https://github.com/cli/cli#installation)

---

## Snyk

Snyk scans code and dependencies for security vulnerabilities — integrated into the development workflow via Claude Code hooks.

**Install**

```bash
npm install -g snyk
```

**Authenticate**

```bash
snyk auth
```

**Docs**

- [Snyk homepage](https://snyk.io)
- [Snyk CLI docs](https://docs.snyk.io/snyk-cli)

---

## Pyright

Pyright is a fast static type checker for Python — used to enforce type safety in Python projects.

**Install**

```bash
npm install -g pyright
```

**Docs**

- [Pyright repository](https://github.com/microsoft/pyright)
- [Configuration reference](https://github.com/microsoft/pyright/blob/main/docs/configuration.md)

---

## Neovim

Neovim is a hyperextensible terminal editor used as a development environment in this project.

**Install**

```bash
# macOS
brew install neovim

# Linux (apt)
sudo apt install neovim

# Linux (dnf)
sudo dnf install neovim

# Windows (winget)
winget install --id Neovim.Neovim
```

**Docs**

- [Neovim homepage](https://neovim.io)
- [Documentation](https://neovim.io/doc/)
- [GitHub repository](https://github.com/neovim/neovim)
