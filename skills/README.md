# Skills

Shareable skills for Claude Code and [OpenCode](https://opencode.ai/).

## Installation

### Claude Code

Skills must be installed in `~/.claude/skills/` to be available in Claude Code.

#### Option 1: Symlink (Recommended)

Symlinks keep the skills in sync with the repository:

```bash
# Create the skills directory if it doesn't exist
mkdir -p ~/.claude/skills

# Symlink all skill folders
ln -sf /path/to/ai-toolkit/skills/* ~/.claude/skills/

# Remove the README.md symlink
rm -f ~/.claude/skills/README.md
```

#### Option 2: Copy

Copy folders directly (won't auto-update when repo changes):

```bash
mkdir -p ~/.claude/skills
cp -r /path/to/ai-toolkit/skills/!(README.md) ~/.claude/skills/
```

#### Verification

After installation, verify the skills are available:

1. Open Claude Code
2. Type `/` to see available slash commands
3. Your installed skills should appear (e.g., `/tdd-cycle`, `/tdd-verify`)

### OpenCode

[OpenCode](https://opencode.ai/) supports Claude-compatible skill locations, so these skills work out of the box.

OpenCode searches for skills in these locations:

| Location | Path |
|----------|------|
| Project-local (OpenCode) | `.opencode/skills/<name>/SKILL.md` |
| Project-local (Claude) | `.claude/skills/<name>/SKILL.md` |
| Global (OpenCode) | `~/.config/opencode/skills/<name>/SKILL.md` |
| Global (Claude) | `~/.claude/skills/<name>/SKILL.md` |

#### Option 1: Symlink to OpenCode config (Recommended)

```bash
# Create the skills directory if it doesn't exist
mkdir -p ~/.config/opencode/skills

# Symlink all skill folders
ln -sf /path/to/ai-toolkit/skills/* ~/.config/opencode/skills/

# Remove the README.md symlink
rm -f ~/.config/opencode/skills/README.md
```

#### Option 2: Symlink to Claude location

If you already have skills installed for Claude Code, OpenCode will find them automatically:

```bash
# If you've already set up Claude Code skills, OpenCode will use them
# No additional setup required!
```

#### Option 3: Copy

```bash
mkdir -p ~/.config/opencode/skills
cp -r /path/to/ai-toolkit/skills/!(README.md) ~/.config/opencode/skills/
```

#### Verification

After installation, verify the skills are available:

1. Open OpenCode
2. Type `/` to see available slash commands
3. Your installed skills should appear (e.g., `/tdd-cycle`, `/tdd-verify`)

## Available Skills

### TDD Suite

| Skill | Description |
|-------|-------------|
| `tdd-agent` | Fully autonomous TDD with strict guardrails |
| `tdd-cycle` | Core RED-GREEN-REFACTOR cycle guidance |
| `tdd-implementer` | Minimal implementation strategies (Fake It, Obvious, Triangulation) |
| `tdd-pair` | Collaborative TDD pair programming mode |
| `tdd-refactor` | Safe refactoring patterns and code smell detection |
| `tdd-verify` | TDD compliance verification and scoring |

### Enterprise .NET Suite

| Skill | Description |
|-------|-------------|
| `dotnet-vertical-slice` | Scaffold vertical slice architecture with CQRS + FreeMediator |
| `ef-migration-manager` | EF Core migration lifecycle with safety checks and rollback |
| `nuget-package-scaffold` | NuGet package creation with CI/CD and test harness |
| `blazor-telerik-component` | Telerik Blazor UI patterns for grids, forms, dialogs |
| `legacy-migration-analyzer` | .NET Framework to .NET 10 migration analysis |

### Edge/IoT/Robotics Suite

| Skill | Description |
|-------|-------------|
| `edge-cv-pipeline` | OpenCV + TFLite computer vision pipeline for Jetson/Pi |
| `jetson-deploy` | Jetson Orin Nano deployment and TensorRT optimization |
| `sensor-integration` | Sensor data pipeline with I2C/SPI/UART/GPIO protocols |
| `picar-x-behavior` | Composable robot behaviors for SunFounder Picar-X |

### AI/ML Bridge Suite

| Skill | Description |
|-------|-------------|
| `rag-pipeline` | RAG scaffold with Ollama/cloud embeddings and vector stores |
| `mcp-server-scaffold` | Custom MCP server creation with FastMCP and testing |
| `ollama-model-workflow` | Local LLM management with Modelfile and benchmarking |

### Other Skills

| Skill | Description |
|-------|-------------|
| `python-arch-review` | Python architecture review and code quality analysis |

## Skill Structure

Each skill follows this structure:

```
skill-name/
├── SKILL.md           # Main skill definition with frontmatter
└── references/        # Supporting documentation
    ├── reference1.md
    └── reference2.md
```

## Usage

Skills can be invoked as slash commands:

```
/tdd-cycle                  # Start a TDD session
/dotnet-vertical-slice      # Scaffold a vertical slice feature
/ef-migration-manager       # Manage EF Core migrations safely
/edge-cv-pipeline           # Build an edge CV pipeline
/rag-pipeline               # Scaffold a RAG pipeline
/mcp-server-scaffold        # Create a custom MCP server
```

Or referenced by agents that depend on them.
