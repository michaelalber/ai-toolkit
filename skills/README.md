# Skills

Shareable Claude Code skills for the AI Toolkit.

## Installation

Skills must be installed in `~/.claude/skills/` to be available in Claude Code.

### Option 1: Symlink (Recommended)

Symlinks keep the skills in sync with the repository:

```bash
# Create the skills directory if it doesn't exist
mkdir -p ~/.claude/skills

# Symlink all skill folders
ln -sf /path/to/ai-toolkit/skills/* ~/.claude/skills/
```

### Option 2: Copy

Copy folders directly (won't auto-update when repo changes):

```bash
mkdir -p ~/.claude/skills
cp -r /path/to/ai-toolkit/skills/* ~/.claude/skills/
```

**Note:** When copying, exclude this README to avoid confusion:

```bash
cp -r /path/to/ai-toolkit/skills/!(README.md) ~/.claude/skills/
```

## Verification

After installation, verify the skills are available:

1. Open Claude Code
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

### Other Skills

| Skill | Description |
|-------|-------------|
| `jira-review` | Automated Jira issue analysis and improvement suggestions |

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
/tdd-cycle
/tdd-verify
/jira-review
```

Or referenced by agents that depend on them.
