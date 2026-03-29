# Subagent Delegation Guide

How to craft effective prompts for the three RPI research subagents, and how to synthesize their outputs.

## Overview

The three subagents have complementary, non-overlapping jobs:

| Subagent | Job | Key Output |
|----------|-----|------------|
| `@rpi-file-locator` | Find all relevant files | Categorized file listing with line counts and key exports |
| `@rpi-code-analyzer` | Understand how the code works | Type signatures, data/control flow, integration points |
| `@rpi-pattern-finder` | Understand how new code should be written | Naming conventions, DI patterns, test patterns, precedents |

## Parallel Spawning (Task Tool)

Always spawn all three concurrently. In OpenCode, use the Task tool with the agent name:

```
Task(@rpi-file-locator, "Find all files related to: [topic]")
Task(@rpi-code-analyzer, "Analyze the implementation of: [topic]")
Task(@rpi-pattern-finder, "Find patterns and conventions related to: [topic]")
```

Wait for all three before synthesizing.

## Writing Effective Prompts

### For @rpi-file-locator

The prompt should specify the topic clearly. Include domain vocabulary if available.

**Better prompts:**
```
"Find all files related to: annual review notifications and email delivery"
"Find all files related to: JWT token validation and authentication middleware"
"Find all files related to: EF Core migrations and database schema versioning"
```

**Weaker prompts:**
```
"Find notification files"          ← too vague
"Find everything about auth"       ← too broad
```

### For @rpi-code-analyzer

The prompt should specify the implementation aspect to analyze. Reference the file-locator output if sequential, but usually run in parallel with a topic-based prompt.

**Better prompts:**
```
"Analyze the implementation of: the annual review workflow from request entry to database persistence"
"Analyze the implementation of: JWT token validation — trace the flow from HTTP request to claims extraction"
"Analyze the implementation of: how EF Core migrations are created and applied in this project"
```

**Weaker prompts:**
```
"Analyze the notification system"  ← too vague about what to trace
```

### For @rpi-pattern-finder

The prompt should specify the type of change being researched (new feature, migration, refactor, etc.) so the agent knows what analogues to look for.

**Better prompts:**
```
"Find patterns for: adding a new notification type — how are similar notifications structured, tested, and registered?"
"Find patterns for: adding a new CQRS command handler — naming, folder structure, DI registration, test patterns"
"Find patterns for: database schema migrations — how are EF Core migrations named, applied, and rolled back in this project?"
```

**Weaker prompts:**
```
"Find patterns"                     ← no target
"Find notification patterns"        ← unclear what type of change
```

## Synthesizing Subagent Outputs

After all three return, combine their findings into the research artifact:

### Step 1: De-duplicate file references
Both file-locator and code-analyzer may reference the same files. Use the code-analyzer's detailed analysis as the canonical source; use file-locator for files the analyzer didn't cover.

### Step 2: Organize by component/area
Group related files into logical sections (e.g., "Authentication", "Notification Service", "Tests"). Don't just dump three separate lists.

### Step 3: Extract open questions
Look for:
- Files the analyzer couldn't find (from "UNKNOWN" notations)
- Convention inconsistencies flagged by the pattern-finder
- Integration points with unclear contracts
- Missing infrastructure (a handler references a service that doesn't exist)

### Step 4: Apply the compaction check
Before writing:
- Can any section be shortened without losing information the plan needs?
- Are there repeated file references that can be consolidated?
- Are any findings obvious from context and not worth including?

Target ≤ 250 lines total.

### Step 5: Verify citations
Every type name, method signature, and file path in the artifact should trace to a subagent output. If you're writing something that none of the subagents found, mark it as inference or omit it.

## Common Synthesis Patterns

### When file-locator finds files that code-analyzer didn't analyze
Add them to the "Code references" section without the deep analysis:
```
### Additional files (not deeply analyzed)
- `path/to/file.cs` (89 lines) — [brief description from file-locator]
```

### When pattern-finder finds inconsistencies
Surface them as open questions:
```
## Open questions
3. Two naming patterns observed: `{Entity}Service.cs` (8 files) and `{Entity}Manager.cs` (3 files).
   AGENTS.md does not specify which to use. Which convention should the plan follow?
```

### When code-analyzer can't find an entry point
```
## Open questions
2. Could not locate the entry point for [area]. Searched for route attributes and command handlers
   but found no match. The feature may not be implemented yet or may use unconventional wiring.
```
