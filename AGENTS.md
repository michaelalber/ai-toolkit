# AI Toolkit — Project Context

> **Mirror pair — edit both copies together.** This repository keeps `CLAUDE.md` and `AGENTS.md`
> byte-for-byte identical. Claude Code reads `CLAUDE.md`; OpenCode and Pi read `AGENTS.md`. They are
> the same document under two filenames — any change to one MUST be made to the other. (Verify with
> `diff CLAUDE.md AGENTS.md` — it should print nothing.)

This is the **project-level** context file. It *supplements*, and does not replace, the global
standards installed at `~/.claude/` (Claude Code), `~/.config/opencode/` (OpenCode), and
`~/.pi/agent/` (Pi). Global standards — coding style, security rules, quality gates, the
grounding/MCP workflow, and the Session Boot Ritual — live in those global files and are not
repeated here. Related project context files: `intent.md` (goals, values, tradeoff hierarchy),
`constraints.md` (musts, must-nots, escalation triggers), `evals.md` (test cases and CI gates).

---

## Project Overview

- **Name:** AI Toolkit
- **Purpose:** A collection of 87 shareable skills and autonomous agents for AI-assisted software development. Supports Claude Code, OpenCode, and Pi. Edge AI, ML, robotics, and industrial-automation skills live in the companion `edge-ai-robotics-automation-toolkit`.
- **Phase:** Maintain — stable toolkit; work consists of adding new skills/agents, fixing existing ones, and keeping platform parity.
- **Jira project key:** N/A — task specs are tracked in conversation context or ad hoc
- **Definition of success:** Every skill and agent installs cleanly, follows its template (skills: the 5-section lean layout; agents: the agent section template), and works out of the box without requiring external documentation.

---

## Technology Stack

- **Content format:** Markdown + YAML frontmatter — no compiled language, no build system
- **Agent platforms:** Claude Code (claude.ai/code), OpenCode, and Pi (pi.dev / Ollama local models)
- **Global install targets:** `~/.claude/` (Claude Code), `~/.config/opencode/` (OpenCode), `~/.pi/agent/` (Pi)
- **Package manager:** None for skills/agents; `bun` used in `opencode/global/` for OpenCode config dependencies

---

## Architecture

- **Pattern:** Flat directories by domain — skills, agents, global config, and project templates are siblings, not layers
- **Two-level context stack:**
  - `claude/global/CLAUDE.md` + `opencode/global/AGENTS.md` + `pi/global/AGENTS.md` — universal standards, installed once globally
  - `CLAUDE.md` (root) + `AGENTS.md` (root) — this repo's context only (this mirrored file)
- **Key directories:**
  - `skills/{team,professional}/<name>/` — skill definition (`SKILL.md`) + supporting docs (`references/`); the `team`/`professional` subdirectory is selected by the skill's `audience:` frontmatter
  - `claude/agents/{team,professional}/` — Claude Code agent definitions (`.md` with `skills:` frontmatter array)
  - `opencode/agents/{team,professional}/` — OpenCode agent definitions (`.md` with boolean tool flags + `skill()` body calls)
  - `claude/commands/` — Claude Code user-invoked slash commands with shell injection (flat, no audience subdir)
  - `opencode/commands/` — OpenCode command equivalents with agent routing and subtask isolation (flat)
  - `claude/global/` — global Claude Code files installed to `~/.claude/`
  - `claude/global/settings.json` — hook wiring: PreToolUse credential + shell-exec-chain stops, PostToolUse bash audit log + build/lint gates
  - `claude/global/hooks/` — hook script bodies (`*.sh`), installed to `~/.claude/hooks/`; `settings.json` references them by path
  - `claude/global/settings.local.json` — permissions: bash allow/deny arrays, read allow/deny arrays
  - `opencode/global/` — global OpenCode files installed to `~/.config/opencode/`
  - `pi/global/` — global Pi files installed to `~/.pi/agent/`; `SYSTEM.md` is a per-project template
  - `project-templates/` — context file templates users copy into their own project roots (do not edit globally)
  - `tools/` — standalone runnable utilities that are not skills/agents/commands (e.g. `tools/pdf2md/`, `tools/web2md/`, `tools/ollama-evals/`); excluded from primitive counts and parity checks
- **Non-obvious constraints:** `claude/global/`, `opencode/global/`, and `pi/global/` files affect every project on the user's machine — changes require explicit human approval before committing

---

## Quick Reference

- **Skills:** `skills/team/<n>/SKILL.md` or `skills/professional/<n>/SKILL.md` — subdir chosen by `audience:` frontmatter. 5-section lean layout (depth → `references/`), gold standard: `skills/team/cargo-package-scaffold/SKILL.md`
- **Agents:** `claude/agents/{team,professional}/<n>.md` (Claude Code) | `opencode/agents/{team,professional}/<n>.md` (OpenCode) — must stay in parity
- **Commands:** `claude/commands/<n>.md` (Claude Code) | `opencode/commands/<n>.md` (OpenCode) — flat, no audience subdir
- **Global files:** `claude/global/` → installs to `~/.claude/` | `opencode/global/` → installs to `~/.config/opencode/` | `pi/global/` → installs to `~/.pi/agent/`
- **Hooks:** `claude/global/settings.json` (wiring) + `claude/global/hooks/*.sh` (bodies) — credential + shell-exec-chain stops (PreToolUse), bash audit log + post-write build/lint gates (PostToolUse)
- **Permissions:** `claude/global/settings.local.json` — bash allow/deny arrays, read allow/deny arrays
- **Project templates:** `project-templates/` — copy into target project roots, do not edit globally

---

## Key Files

| File | Why It Matters |
|---|---|
| `skills/team/cargo-package-scaffold/SKILL.md` | Gold standard for the 5-section lean skill layout (depth in `references/`) |
| `project-templates/AGENTS.md` | Template pattern this file follows |
| `claude/global/CLAUDE.md` | Global Claude Code standards — do not duplicate here |
| `opencode/global/AGENTS.md` | Global OpenCode standards — do not duplicate here |
| `pi/global/AGENTS.md` | Global Pi standards — do not duplicate here |
| `pi/global/SYSTEM.md` | Per-project Pi system prompt template — users copy to project root |
| `intent.md` | Goals, values, tradeoff hierarchy, and persistent decisions for this repo |
| `constraints.md` | Contribution constraints — read before any task |
| `tools/pdf2md/` | Standalone Python utility (not a skill/agent/command): converts PDFs to RAG-ready Markdown. Self-contained `pyproject.toml` + tests; see its `README.md`. |
| `tools/web2md/` | Standalone Python utility: converts web pages and documentation sites to RAG-ready Markdown via docling. Supports single-page, crawl, and sitemap modes. Self-contained `pyproject.toml` + tests; see its `README.md`. |
| `tools/ollama-evals/` | Standalone Python utility: evaluates and regression-tests local Ollama models (coding via code-execution, chat via LLM-as-judge, tool-use, structured JSON-schema). Frontend-agnostic — measures the model behind Pi / Goose / Open WebUI once at the `/v1` API. Model-vs-model comparison matrix + non-zero-exit regression gate; local rubric judge (offline) with optional DeepEval/remote. Self-contained `pyproject.toml` + tests; see its `README.md`. |

---

## Skill Conventions

Each skill lives in `skills/team/<name>/` or `skills/professional/<name>/` with a `SKILL.md` and a
`references/` directory. The `team` vs. `professional` subdirectory is selected by the `audience:`
frontmatter field and applied by `scripts/add_frontmatter.py` (which walks `skills/{team,professional}/*/`).

### SKILL.md Frontmatter

```yaml
---
name: skill-name
audience: team  # team | professional — selects the skills/<audience>/ install subdirectory
description: >
  What the skill does. Trigger phrases like "keyword1", "keyword2".
disable-model-invocation: true  # optional: prevents auto-invocation; use for interactive or conversational skills
---
```

### Skill Tiers

| Tier | When to use | SKILL.md size | References required |
|------|------------|--------------|---------------------|
| **Minimal** | Mode switches, conversational tools, single-instruction skills, thin workflow-phase drivers (≤ ~40 imperative directives) | ≤ 100 lines | ≥ 1 file |
| **Full-template** | Domain-expert skills with workflow, state tracking, and output templates | ≤ 200 lines (depth → `references/`) | ≥ 2 files |

Minimal-tier skills have no prescribed section structure — just focused instructions.
Full-template skills follow the **5-section lean layout** below. Every always-loaded section is a
per-invocation token tax, so depth — principle tables, anti-patterns, discipline rules, recovery
steps, and code/report templates — lives in `references/` and loads just-in-time, not in SKILL.md.

### Description Format

The description field is the **only thing the model sees when deciding which skill to load**. Quality here determines trigger reliability.

- Max 1024 chars
- Third person: "Scaffolds...", "Audits...", "Extracts..." — not "I will..." or "You can..."
- First sentence: what the skill does
- Second sentence: "Use when [specific trigger scenarios]"
- Include "Do NOT use when..." for negative triggers

**Good:**
```yaml
description: >
  Scaffolds NuGet package metadata, CI/CD pipeline, and test harness.
  Use when publishing a new library to NuGet.org. Do NOT use for
  internal workspace-only libraries; use dotnet-vertical-slice instead.
```

**Bad (too vague — triggers on everything):**
```yaml
description: >
  A comprehensive and powerful tool for NuGet package management.
  Very useful for .NET developers.
```

### 5-Section Lean Layout (in order)

A full-template SKILL.md carries only what the model needs to *act*. Everything else is depth that
loads on demand from `references/`.

1. **Title + Epigraph** -- `# Skill Name` with 1 relevant quote
2. **Core Philosophy** -- design rationale + a numbered **Non-Negotiable Constraints** list. The
   Critical/High principles live here as constraints; the full principle table goes to `references/`.
3. **Workflow** -- phased lifecycle (e.g., DETECT, SCAN, REPORT, RECOMMEND) in one compact block,
   with exit criteria. Decision trees and long step prose go to `references/`.
4. **State Block** -- unique XML tag (e.g., `<tdd-state>`, `<arch-review-state>`) for multi-turn tracking
5. **Output Template** -- **pointers** to the report/code templates in `references/`, not the
   templates inline
6. **Integration with Other Skills** -- a table cross-referencing related skills

**Pushed to `references/` (depth, loaded just-in-time):** the full Domain Principles table,
Anti-Patterns table, AI Discipline (WRONG/RIGHT) rules, Error Recovery scenarios, and all
code/report templates. These remain authoritative — they are relocated, not deleted, and every
reference file is named by a pointer in SKILL.md so nothing becomes undiscoverable.

Gold-standard lean examples: `skills/team/qraspi-skeleton/SKILL.md` (phase driver) and
`skills/team/cargo-package-scaffold/SKILL.md` (domain scaffolder with `references/` depth).

### References Directory

Each `references/` directory contains 2-5 supporting files: code examples, decision matrices, checklists, configuration templates.

### When Adding a Skill

**Choose a tier first** (see the Skill Tiers table above). Set `audience:` in the frontmatter
(`team` | `professional`) — it selects the `skills/<audience>/` install subdir, applied by
`scripts/add_frontmatter.py`.

**Minimal-tier steps:**
1. Create `skills/<audience>/<new-name>/SKILL.md` with focused instructions (no template to copy)
2. Add `disable-model-invocation: true` for interactive or conversational skills
3. Create `skills/<audience>/<new-name>/references/` with ≥ 1 supporting file
4. Skip the agent/command/registration steps below unless the skill is user-invocable

**Full-template steps:**
1. Copy the gold standard: `cp -r skills/team/cargo-package-scaffold skills/<audience>/<new-name>`
2. 5-section lean layout — keep Core Philosophy / Workflow / State / Output Template / Integration in SKILL.md; push depth to `references/`; ≥ 2 reference files
3. Add agent entries in **both** `claude/agents/<audience>/` and `opencode/agents/<audience>/`
4. Add command entries in **both** `claude/commands/` and `opencode/commands/` if user-invocable
5. Update counts and tables: README.md badge + at-a-glance + structure comments; this file's Purpose line + Open Loops + Skill Suites table
6. Add a Green / Yellow / Red entry for the new skill in `pi/SKILLS-local.md`

---

## Agent Conventions

Agents exist in two flavors with identical behavior but different formats:

### Claude Code (`claude/agents/<name>.md`)

```yaml
---
name: agent-name
description: What the agent does
tools: Read, Edit, Write, Bash, Glob, Grep
model: inherit
skills:
  - skill-name-1
  - skill-name-2
---
```

### OpenCode (`opencode/agents/<name>.md`)

```yaml
---
description: What the agent does
mode: subagent
tools:
  read: true
  edit: true
  write: true
  bash: true
  glob: true
  grep: true
---
```

Key difference: Claude uses `skills:` array in frontmatter; OpenCode uses `skill({ name: "..." })` calls in the body.

### 10 Mandatory Agent Sections (in order)

1. Title + Epigraph
2. Core Philosophy
3. Guardrails
4. Autonomous Protocol
5. Self-Check Loops
6. Error Recovery
7. AI Discipline Rules
8. Session Template
9. State Block (unique XML tag per agent, e.g., `<tdd-state>`, `<code-review-state>`)
10. Completion Criteria

---

## Command Conventions

Commands are user-invoked (typed as `/command-name`). Use `!` shell injection to give the agent
live state before it acts. Skills are model-invoked — different primitive, different directory.

**Claude Code format:**
```markdown
---
description: What it does. Trigger phrase for slash-command discovery.
allowed-tools: Bash(dotnet test:*), Read, Edit
---

<live_state>
!`command that captures current state`
</live_state>

Instruction using the injected state above.
```

**OpenCode additions** — `agent:`, `subtask:`, optional `model:`:
```markdown
---
description: What it does.
agent: build
subtask: true
---
```

Use `subtask: true` for read-heavy commands (review, research, context-prime).
Use `subtask: false` for commands that write files (new-feature, migrate) — they need primary context.

---

## Hook Enforcement (settings.json)

`claude/global/settings.json` installs deterministic hooks that run outside the LLM:

| Hook | Matcher | Action |
|------|---------|--------|
| PreToolUse | `^Bash$` | Shell-exec-chain scan (pipe-to-shell, `find -exec sh`) — exit 2 blocks the call |
| PreToolUse | `^(Write\|Edit\|NotebookEdit)$` | Credential pattern scan of the content being written — exit 2 blocks the call |
| PostToolUse | `^Bash$` | Appends the command to `~/.claude/logs/bash-audit.log` |
| PostToolUse | `^(Write\|Edit)$` | Dispatches by extension: `.cs` → build the owning `.csproj`, `.csproj` → restore it, `.py` → `ruff check` (advisory) |

Hook bodies live in `claude/global/hooks/*.sh` and install to `~/.claude/hooks/`; `settings.json`
only references them by path. Three rules govern whether a hook works at all — each has silently
disabled these hooks before:

- **`matcher` matches the tool NAME only**, as a literal or unanchored regex. Permission-rule
  syntax (`Bash(*)`, `Write(*.cs)`) does **not** work here and matches nothing. Filter by file
  extension inside the script, not in the matcher.
- **Tool input arrives as JSON on stdin** — read it with `jq` (`.tool_input.command`,
  `.tool_input.file_path`). There are no `CLAUDE_TOOL_INPUT_*` environment variables; referencing
  them yields an empty string and the hook fails **open**, silently allowing what it should block.
- **Exit 2 blocks only on PreToolUse.** PostToolUse runs after the tool call and cannot block —
  its output is advisory. Messages must go to **stderr** to be surfaced.

A misconfigured hook produces no error — it simply never runs. Verify with the checks in
`claude/global/README.md` rather than assuming.

These run regardless of model instruction and cannot be bypassed by prompt injection. Permissions
(interactive allow/deny) live separately in `claude/global/settings.local.json` — hooks for
deterministic enforcement, permissions for interactive approval; keep them in separate files.

---

## Contributor Validation

No compiled artifacts. Validation is structural.

```bash
# Count skills
find skills -name "SKILL.md" | wc -l

# Verify a full-template skill has the 5 lean sections (in-fence template headers may push this higher)
grep -c "^## " skills/{team,professional}/<n>/SKILL.md

# Check agent parity (counts must match) — agents live under team/ and professional/ subdirs
find claude/agents -name "*.md" | wc -l
find opencode/agents -name "*.md" | wc -l

# Check command parity (counts must match) — commands are flat
ls claude/commands/*.md | wc -l
ls opencode/commands/*.md | wc -l

# Confirm this mirror pair is in sync (should print nothing)
diff CLAUDE.md AGENTS.md
```

---

## Editing Guidelines

- Follow the 5-section lean layout when creating or modifying skills; push depth to `references/`.
- Keep both `claude/agents/` and `opencode/agents/` versions in sync.
- Every full-template skill must have a `references/` directory with at least 2 supporting files (minimal-tier: ≥ 1).
- State block XML tags must be unique across all skills and agents.
- Frontmatter `description` fields must include trigger phrases for slash-command discovery.
- In Python code examples, avoid PyTorch evaluation mode calls that trigger security hooks. Use `model.train(False)` instead.
- **Keep `CLAUDE.md` and `AGENTS.md` byte-identical** — any edit to one must be made to the other; confirm with `diff CLAUDE.md AGENTS.md`.

---

## Global File Caution

Files in `claude/global/`, `opencode/global/`, and `pi/global/` affect **every project on the user's machine** after install.
Changes to any global file require explicit review before committing.
Do not batch-edit them alongside skill or agent changes.

**These files are public templates.** Never embed specific book titles, personal document names,
personal file paths, or user-specific tool references in them. Collection descriptions must describe
topic domains only (e.g., "Rust language: ownership, async, Tokio"), not the specific documents a
particular user has ingested. Personal enrichment belongs in the installed copies
(`~/.claude/CLAUDE.md`, `~/.config/opencode/AGENTS.md`, `~/.pi/agent/AGENTS.md`), not the repo source.

---

## Persistent Decisions

| Date | Decision | Rationale |
|---|---|---|
| 2026-03-01 | 10-section template for skills and agents | Enforces completeness; gold standard is `skills/professional/architecture-review/SKILL.md` |
| 2026-03-01 | Claude Code uses `skills:` frontmatter array; OpenCode uses `skill()` body calls | Platform format requirements differ; behavior must be identical |
| 2026-04-18 | Specs live in Jira / Confluence, not local `spec.md` | Professional dev workflow; `spec.md` creates stale duplicates |
| 2026-04-18 | `project-templates/` renamed from `templates/` | "project-templates" makes the scope explicit — these are not global files |
| 2026-04-18 | Global files live in `claude/global/` and `opencode/global/` | Separates global standards from project-level context; aligns with install script targets |
| 2026-04-24 | Pi global files live in `pi/global/`; AGENTS.md installs to `~/.pi/agent/`; SYSTEM.md is a per-project template | Pi's `SYSTEM.md` is project-scoped (not a global config file); keeping it in `pi/global/` as a user-copyable template matches Pi's per-project design |
| 2026-04-24 | Commands layer added alongside agents | Commands are user-invoked (typed as `/command-name`); skills are model-invoked (autonomous). Different primitives, same platform directory scope. |
| 2026-04-24 | Hooks in `settings.json`, permissions in `settings.local.json` | Separation of concerns — deterministic enforcement (hooks) vs. interactive approval (permissions). Keep in separate files. |
| 2026-04-25 | Two-tier skill system: minimal (≤ 100 lines, ≥ 1 reference) and full-template (10 sections, ≤ 400 lines, ≥ 2 references) | Ported from mattpocock/skills — minimal tier handles mode switches, conversational tools, and single-instruction skills without the overhead of the 10-section template. |
| 2026-04-25 | `disable-model-invocation: true` frontmatter for interactive/conversational skills | Ported from mattpocock/skills — prevents auto-invocation by the model; grill-me, domain-model, zoom-out use this. |
| 2026-04-26 | Global template files (`claude/global/`, `opencode/global/`) must contain only generic, domain-level descriptions — no specific book titles, personal document names, or user-specific tool references | These files are public templates installable by any user. Personal enrichment belongs in the installed copies (`~/.claude/CLAUDE.md`, `~/.config/opencode/AGENTS.md`), not the repo source. |
| 2026-06-02 | QRSPI replaces RPI: deprecate the 4 rpi-* skills + `rpi-planner`/`rpi-implement` agents now (`disable-model-invocation: true` on skills + `DEPRECATED` description prefix); remove all rpi-* files at sunset ~2026-09-01 (Slice 7). The 3 read-only subagents were renamed `research-*` (workflow-neutral) and kept. | RPI delivered poor results (instruction-budget overflow, magic-words dependency, plan-reading illusion). Coexistence leaves the poor-outcome path discoverable; QRSPI is its replacement, so RPI is deprecated then removed. |
| 2026-06-02 | QRSPI vendors **0 new primitive skills** — `qrspi-implement` references the existing `tdd` skill as its inner loop; `qrspi-spec`/`qrspi-plan` carry the vertical-slice gate in their own content; all five cross-link `tdd` and the `*-feature-slice` scaffolders via Integration | `tdd` already IS the canonical RED-GREEN-REFACTOR loop purpose-built as a shared inner loop; a new `red-green-refactor` skill would be ~100% duplication. Honors DRY and the "Companion Skills" non-overlap doctrine. |
| 2026-06-02 | Minimal-tier definition broadened to include **thin, self-sufficient workflow-phase drivers (≤ ~40 imperative directives)**. All five `qrspi-*` phase skills use the minimal tier (≤ 100 lines, ≥ 1 reference), self-sufficient when invoked directly, overflow pushed to `references/` loaded just-in-time | QRSPI exists because prompts past ~150–200 instructions degrade; the full 10-section template reproduces the exact bloat QRSPI was created to fix, and is worst on smaller local models. Every section is an always-on per-invocation token tax. |
| 2026-06-02 | QRSPI artifacts co-locate in a per-feature folder `thoughts/shared/qrspi/YYYY-MM-DD-{slug}/` (`questions.md`, `research.md`, `spec.md`, `plan.md`, `implementation/slice-NN-*.md`) rather than scattering across `thoughts/shared/research|plans/` | QRSPI produces five tightly-coupled artifacts per feature; co-locating them makes a fresh session cheap (read the folder, not the transcript) and gives each slice log a clean resumption point. `spec.md`/`plan.md` carry a lifecycle `status:` (the `approved` gate blocks `qrspi-implement`). |
| 2026-06-03 | QRASPI greenfield workflow added: six phases Q→R→A→S→P→I + a terminal graduation handoff, the greenfield (V0/V1) counterpart to QRSPI. **2-agent topology split by edit access**: `qraspi-orchestrator` (no-Edit: Questions/Research/Architecture/Plan/Graduate) + `qraspi-builder` (Edit: Skeleton/Implement). | Greenfield's edit boundary differs from QRSPI's (Skeleton and Implement write source; Q/R/A/P/graduate are markdown), but it still splits cleanly into who-may-edit. A 3rd agent buys nothing — Skeleton and Implement share tools and the green-gate philosophy. QRASPI maps a problem domain; QRSPI maps an existing codebase. |
| 2026-06-03 | QRASPI extracts **one** new primitive skill, `fitness-functions` — the first new primitive since the QRSPI "vendored 0 primitives" decision. ADR-writing, C4, and walking-skeleton scaffolding were instead **folded** into the phase skills + `references/`. | `fitness-functions` has ≥2 callers (`qraspi-architecture` specifies them, `qraspi-skeleton` lands them as CI gates) and cross-workflow reuse (a brownfield QRSPI feature can add a CI-gate fitness function); no existing skill covers the surface (`dependency-mapper` covers only the coupling-metric category). The doctrine holds in spirit: extract only at ≥2 callers with no existing cover. |
| 2026-06-03 | QRASPI artifacts co-locate per project in `thoughts/shared/qraspi/YYYY-MM-DD-{slug}/` with **per-slice** `plan-{slice}.md` + `implementation-log-{slice}.md` (vs QRSPI's single `plan.md` + `implementation/slice-NN-*.md`); accepted ADRs live in the **target repo's** `docs/adr/NNNN-*.md`. | Greenfield grows slice-by-slice on the skeleton, so Plan/Implement run once per slice (default: the next unbuilt backlog slice from `skeleton.md`). ADRs are project artifacts QRSPI later reads, so they belong in the repo, not the qraspi feature folder. |
| 2026-06-03 | QRASPI ADRs use the **MADR** template (Title/Status/Context/Considered Options/Decision/Consequences) with **≥2 alternatives required** and an align-before-lock gate (proposed → human aligns → accepted). | "Alternatives Considered" is a MADR/Tyree addition, not original Nygard; QRASPI requires alternatives so a fait-accompli ADR cannot reach WRITE, and MADR carries them natively. `architecture-journal` keeps its own ADR variant; QRASPI's MADR template lives in `qraspi-architecture/references/adr-template.md`. |
| 2026-06-03 | QRASPI C4 diagrams use **Mermaid** `C4Context`/`C4Container` (Context + Container levels only). | The repo is markdown-native with no build system; Mermaid renders inline in GitHub/Codeberg/VS Code, is diffable, and is AI-generatable. Structurizr DSL is richer but needs tooling the repo lacks. |
| 2026-06-03 | QRASPI Skeleton's exit gate is **CI green** — a real CI/test run (build + unit + lint + fitness gates) exiting 0, captured as `ci_green`, never a claim. Hardware archetypes: host gates green + device-deploy as a documented manual gate. | A walking skeleton is executable by definition; an aspirational scaffold defeats the phase. The fitness functions `qraspi-architecture` specified are wired by `fitness-functions` and must pass as part of CI green; `qraspi-implement` keeps them green per slice. |
| 2026-06-03 | Deprecate `spec-implement` alongside RPI (`disable-model-invocation: true` + `DEPRECATED` description prefix; removal at sunset ~2026-09-01). Its `rpi-*` pointers in `spec-implement`, `tdd`, and `spec-coach` were scrubbed to QRSPI/QRASPI. | `spec-implement` was branded "the greenfield counterpart to RPI" and routed to the now-deprecated `/rpi-research` in five places; QRASPI (greenfield) and QRSPI (brownfield) subsume its spec → criteria → per-slice TDD flow with artifact-gated phases. Leaving it live keeps a stale path to a sunset workflow discoverable. |
| 2026-06-03 | Cross-language **architecture + security parity** for .NET/Python/PHP/Rust. Architecture: four `<lang>-architecture-checklist` skills sharing an identical Core Values + `DETECT→SCAN→REPORT(A–F)→RECOMMEND` workflow + output, differing only in language checks/tooling; `python-arch-review` (a misfit TDD-authoring hybrid) renamed/re-scoped to `python-architecture-checklist`; `php-architecture-checklist` created. Security: four `<lang>-security-review` bases share an OWASP core; **gov collapses to ONE language-agnostic `security-review-federal` overlay** (NIST 800-53 · CUI · DOE · POA&M · EO 14028 + per-language FIPS table), replacing `dotnet-security-review-federal` + `python-security-review-federal`. All trimmed lean; depth in `references/`. | User wants the four languages "in sync" (same workflow/values, language-specific specifics) and lean. Per-language skills (not one detecting skill) preserve trigger routing and match every other family. The federal overlay is ~80% language-agnostic policy, so one shared skill gives gov parity for all four languages at once and one place to keep NIST/CUI/POA&M in sync — far leaner than duplicating it 4×. `python-arch-review` was the lone misfit whose triggers collided with `tdd`/`python-feature-slice`/`python-security-review`. |
| 2026-06-03 | **React skill family** added (first frontend family), mirroring the .NET/Python/PHP/Rust families: `react-architecture-checklist`, `react-security-review`, `react-feature-slice`, `react-component-scaffolder`, `react-app-scaffolder`, `react-modernization-analyzer` (6 skills) + 6 agents in both runtimes (`react-feature-slice-agent`, `react-component-scaffold-agent`, `react-app-scaffold-agent`, `react-security-agent`, `react-modernization-agent`, `react-arch-checklist-agent`). React is a frontend library, so two backend archetypes were **remapped**: the HTTP `api-scaffolder` slot → `react-component-scaffolder` + `react-app-scaffolder` (the component/app is the front-end "unit"), and the DB `migration-manager` slot → `react-modernization-analyzer` (class→hooks, CRA→Vite, 17→18→19, JS→TS); the `*-package-scaffold` (npm) archetype was **dropped** to keep the family at the standard 6 skills. Federal overlay gained a React/TS FIPS row; `security-review` command dispatch adds `react`. | User asked for React "to mirror the php, python, etc." The remapping keeps the family the same size and shape while respecting that a frontend library has no HTTP endpoint or DB migration. **Grounding gap noted:** the KB has no React corpus (`grounded_javascript` is JS/TS + Vue, not React), so every React skill grounds TS via `collection="javascript"`, a11y via `collection="ui_ux"`, OWASP via `collection="internal"`, and cites **react.dev** as the primary authority. Follow-up (separate repo): add a `grounded_react` collection to grounded-code-mcp. |
| 2026-06-03 | Consolidate the TDD cluster 8→5. **Delete** `tdd-implementer` and `tdd-refactor` — their per-phase content folds into the canonical `tdd` skill's GREEN/REFACTOR sections + `references/` (green idioms, `code-smells`, `refactoring-catalog`, loaded on demand). **Merge** `tdd-verify` into `evaluate-tests` as a second "TDD compliance" mode (commit-history scorecard + AI anti-patterns). **Keep** `tdd` (the one loop), `tdd-agent` + `tdd-pair` (operating modes that defer to `tdd`), `evaluate-tests`, `test-scaffold`. Agents `tdd-agent`/`test-generation-agent` updated; no agent/command count change. | Eight overlapping TDD skills created an unanswerable routing question ("for GREEN, use `tdd` or `tdd-implementer`?"). The per-phase skills re-derived single phases of the loop `tdd` already owned whole, and the two auditors (`tdd-verify`, `evaluate-tests`) overlapped. One loop + modes + one auditor is focused and token-efficient; depth moved to load-on-demand `references/`. TDD/RGR is critical to AI-agent coding — clarity of "which skill" matters most here. |
| 2026-06-03 | **Full-template tier adopts the 5-section lean layout**, retiring the "10 Mandatory Sections" standard. SKILL.md keeps only Title+Epigraph · Core Philosophy (with a Non-Negotiable Constraints list) · Workflow · State Block · Output Template (pointers) · Integration. The four heavy sections — Domain Principles table, AI Discipline (WRONG/RIGHT), Anti-Patterns table, Error Recovery — plus all code/report templates move to `references/`, loaded just-in-time. Size budget drops 400 → 200 lines. Gold standard moves from `architecture-review` (10-section) to `qraspi-skeleton` + `cargo-package-scaffold`. Rollout migrates the heaviest full-template skills first (Tier A); pilot `cargo-package-scaffold` went 367 → 103 lines with zero information loss. | The 10-section template "reproduces the exact bloat QRSPI was created to fix" (2026-06-02 decision): every always-loaded section is a per-invocation token tax, worst on smaller local models. The qraspi/qrspi family proved the 5-section shape in production. Depth is preserved (relocated, not deleted) and stays discoverable via mandatory pointers in SKILL.md, so trigger reliability and authority are unaffected while the always-on token cost drops ~60–70%. |
| 2026-06-19 | **RPI sunset executed early (Slice 7, originally scheduled ~2026-09-01).** Deleted the 4 `rpi-*` skill dirs + `spec-implement`, and the `rpi-planner`/`rpi-implement` agents in both runtimes; scrubbed all live `rpi-*` references from README, `pi/SKILLS-local.md`, `docs/`, and the `qrspi-*`/`session-context`/`spec-coach` skills. Counts: skills 103→98, agents 49/49→47/47, commands unchanged. The 3 read-only `research-*` subagents stay. | Both workflows were already deprecated (`disable-model-invocation: true` + `DEPRECATED` prefix); pulling the sunset forward removes the dead path now instead of carrying it to September. QRSPI (brownfield) + QRASPI (greenfield) fully subsume RPI and `spec-implement`. Historical `thoughts/` logs left intact as records. |
| 2026-06-20 | **Quality prune: dropped 8 skills + 2 paired agents.** Removed the device-specific edge/IoT/robotics cluster — `picar-x-behavior`, `jetson-deploy`, `sensor-integration`, `edge-cv-pipeline`, `fleet-management`, `anomaly-detection` (professional) — plus `caveman` (communication-mode gimmick, Pocock port) and `tdd-pair` (over-segmented third TDD variant; `tdd` + `tdd-agent` cover the loop + autonomous mode). Deleted paired agents `sensor-anomaly-agent` + `fleet-deployment-agent` in both runtimes; scrubbed README (badges, stats table, prose, suite tables, tree), `pi/SKILLS-local.md`, and `.matt-pocock-attribution.yml` (caveman entry). Counts: skills 98→90 (team 80→78, professional 18→12), agents 47/47→45/45, commands unchanged. Kept `model-optimization` + `model-optimization-agent` (quantization/ONNX is reusable beyond edge) and `ollama-model-workflow` (general local-LLM). | Toolkit targets general software teams; the hardware cluster requires specific boards (Jetson/Picar-X/SBC sensors) and delivers no value without that hardware. `caveman`/`tdd-pair` were thin/redundant. QRASPI/QRSPI retained in full — actively used. |
| 2026-06-25 | **`tools/` houses standalone utilities** — runnable programs that are not skills, agents, or commands. First entry: `tools/pdf2md/` (Python CLI, PDF → RAG-ready Markdown), self-contained with its own `pyproject.toml`, tests, and `README.md`. These do not count toward skill/agent/command tallies and are excluded from platform-parity checks. | The toolkit's three primitives (skills/agents/commands) are prompt artifacts; a PDF converter is executable code with its own dependency graph and test suite, so it does not belong under `skills/`. A dedicated `tools/` directory keeps executable utilities discoverable without polluting the primitive counts or the Claude/OpenCode parity invariant. |
| 2026-06-28 | **`tools/web2md/` added and committed** (commit `2aa467e` on `main`) — Python CLI that converts web pages and documentation sites to RAG-ready Markdown using docling. Three modes: single-page (default), `--crawl` (BFS from a root URL, same-domain), and `--sitemap` (parse sitemap.xml including sitemap index files). Supports `--chunk-by-heading`, `--metadata`, `--max-pages`, `--same-prefix`, `--max-depth` (bounds crawl link-hops from the start URL; root = 0, unlimited by default). 49 tests, 92% coverage. | Companion to `tools/pdf2md/`; docling handles HTML natively so no custom extraction pipeline is needed — the tool is mostly orchestration (crawler + sitemap parser + mode routing). Same `tools/` conventions: self-contained `pyproject.toml` + tests, excluded from skill/agent/command counts. |
| 2026-07-05 | **`tools/ollama-evals/` added** — Python CLI that evaluates and regression-tests local Ollama models across four suites: coding (code-execution against hidden tests), chat (LLM-as-judge rubric), tool-use (trajectory), and structured output (JSON-schema). Frontend-agnostic: Pi, Goose, and Open WebUI share the Ollama backend, so model quality is measured once at the OpenAI-compatible `/v1` endpoint (LAN host via `OLLAMA_BASE_URL` / gitignored `models.local.yaml`, never committed). Ships a model-vs-model comparison matrix, pairwise win/loss/tie, and a `compare` regression gate that exits non-zero (CI-usable). Judge is a local Ollama rubric by default (offline, zero extra deps) with an optional DeepEval/remote path. 79 tests, 98% coverage (code-exec sandbox 100%, exceeding the 95% security-critical gate). | User wanted to confirm local Ollama models perform well and compare new models against previous ones across their Pi/Goose/Open WebUI setups. Because all three share the Ollama backend, one API-level harness covers all three; hand-rolled Python core (matches `tools/pdf2md` + `tools/web2md`) owns the comparison/regression report and the execution sandbox, with DeepEval folded in only for the optional judge. Excluded from skill/agent/command counts and parity checks per the `tools/` convention. |
| 2026-06-20 | **Spun out the edge-AI/robotics/automation supplement repo.** Created `edge-ai-robotics-automation-toolkit` (sibling repo) for Local AI, Edge AI, ML, Robotics, and Industrial Automation. Moved the remaining AI/edge skills out of ai-toolkit into it: `model-optimization` (+ `model-optimization-agent`, both runtimes), `ollama-model-workflow`, `rag-pipeline-python`, `rag-pipeline-dotnet`, `mcp-server-scaffold`. These join the 6 edge skills (`picar-x-behavior`, `jetson-deploy`, `sensor-integration`, `edge-cv-pipeline`, `fleet-management`, `anomaly-detection`) + 2 agents (`sensor-anomaly-agent`, `fleet-deployment-agent`) pruned earlier the same day — all now live in the supplement. Scrubbed README (badges, stats, AI/ML Bridge Suite, professional agent section, tree, prose), `pi/SKILLS-local.md`, and skill Integration cross-refs. The supplement does **not** duplicate global config — it layers on ai-toolkit. Counts: skills 90→85 (team 78→74, professional 12→11), agents 45/45→44/44, commands unchanged. | This earlier-kept cluster ("reusable beyond edge") is, in practice, the AI/ML/local-inference domain the new toolkit is built to own. Consolidating all AI/edge/robotics/automation skills in one supplement gives a clean two-repo portfolio split: ai-toolkit = general software engineering; the supplement = the physical/edge/AI stack. Single-homed skills, no duplication. |
| 2026-06-26 | **Lean-layout migration completed across all oversized full-template skills.** 25 SKILL.md files brought under the 200-line ceiling (21 in a batch + the 4 stragglers `rust-migration-analyzer`, `rust-feature-slice`, `spec-coach`, `architecture-review`); `oss-vetting` refactored to the 5-section layout; the architecture-checklist/security-review families and `task-decomposition` had non-canonical headings normalized (`Output Templates`→`Output Template`, `Core *Values`→`Core Philosophy`, descriptive `Workflow:` headings→`Workflow`). Depth relocated to `references/`, never deleted; pre-existing dangling `references/` pointers fixed. No skill/agent/command count change. | Closes the 2026-06-03 lean-layout decision: every full-template skill now follows the 5-section layout with depth in `references/` and ≥2 reference files. Verified structurally — every `SKILL.md` is ≤200 lines with the 5 canonical sections and no dangling reference pointers. |
| 2026-06-26 | **`CLAUDE.md` and `AGENTS.md` made a byte-identical mirror pair.** The two root context files now carry the same union of content (project overview, architecture, skill/agent/command conventions, hooks, validation, decisions, open loops, skill suites). Claude Code reads `CLAUDE.md`; OpenCode and Pi read `AGENTS.md`. Kept in sync manually with a banner + `diff CLAUDE.md AGENTS.md` check. | Whichever agent opens the project must get the same project context. Previously `CLAUDE.md` was a thin pointer to `AGENTS.md`, so a Claude Code session and an OpenCode session saw materially different guidance. Two real files (not a symlink) keep it portable across tools that don't follow symlinks. |
| 2026-07-11 | **`code-review-agent` slimmed to defer to the `automated-code-review` engine (both runtimes); Fowler code smell catalog added.** The agent (394 → ~160 lines in each runtime) previously re-inlined the skill's entire SCAN→ANALYZE→SYNTHESIZE→REPORT workflow, five-category checklist, self-checks, and output template while also declaring the skill as a dependency. It now keeps only the autonomous-specific parts (guardrails, KB grounding, session lifecycle, its own unique `<code-review-state>` block) and defers the engine to `automated-code-review`. Landed Martin Fowler's *Refactoring* smell catalog as `automated-code-review/references/code-smells.md` — the canonical checklist for the maintainability category, carrying Matt Pocock's "repo overrides" suppression rule; the agent and `/code-review` command inherit it via deferral. No skill/agent/command count change. | Same smell the 2026-06-03 TDD consolidation fixed: an operating-mode agent re-deriving a loop the canonical skill already owns whole. Deferral removes ~250 duplicated lines with zero information loss (the engine holds all of it) and gives one place to maintain the review workflow. The Fowler catalog was the reusable nugget from mattpocock's `code-review` skill; folding it into the existing maintainability category (not a new 6th category or a competing skill) honors the five-category invariant and the non-overlap doctrine. Agent state tag kept distinct from the skill's `<automated-review-state>` per the uniqueness invariant. |
| 2026-07-19 | **Vue skill family added** (second frontend family, mirroring React exactly): `vue-architecture-checklist`, `vue-security-review`, `vue-feature-slice`, `vue-component-scaffolder`, `vue-app-scaffolder`, `vue-modernization-analyzer` (6 skills) + 6 agents in both runtimes (`vue-arch-checklist-agent`, `vue-security-agent`, `vue-modernization-agent`, `vue-feature-slice-agent`, `vue-component-scaffold-agent`, `vue-app-scaffold-agent`). Same shape/doctrine as the 2026-06-03 React decision: 5-section lean layout, structural CQRS via composables instead of hooks, `<script setup lang="ts">` + `defineProps`/`defineEmits` for type safety, Composition API reactivity discipline (no destructured `reactive()`) in place of hooks-rules checks, Vite + Vue Router + Vitest + Vue Testing Library skeleton, Options→Composition/Vue-CLI→Vite/Vue-2→3/Vuex→Pinia modernization paths. Counts: skills 87→93 (team 75→81), agents 45/45→51/51. | User asked for a Vue family alongside the existing React one — the toolkit's other major frontend framework was otherwise unrepresented (`grounded_javascript` already carries a Vue 2/3 corpus, unlike the React gap noted in the 2026-06-03 decision, so Vue skills ground TS/Vue idioms directly via `collection="javascript"` rather than falling back to an external-authority note only). Mirroring React's exact shape (not inventing a new pattern) keeps the two frontend families symmetric and keeps routing simple: same 6-skill/6-agent shape, same Integration cross-reference style, same no-commands-layer precedent. |

---

## Open Loops

- [ ] Skill count (currently 93) — update this file and README when skills are added or removed. Vue family added 2026-07-19 (was 87 → 93, team 75 → 81): 6 skills (`vue-architecture-checklist`, `vue-security-review`, `vue-feature-slice`, `vue-component-scaffolder`, `vue-app-scaffolder`, `vue-modernization-analyzer`), mirroring the React family exactly; no commands (React has none either). Product & GitHub suite retired 2026-07-11 (was 90 → 87, team 78 → 75): dropped `to-prd` + `to-issues` (mattpocock PRD writer + PRD→GitHub-issues decomposer), then `triage-issue` (GitHub/Jira bug triage) — all as out-of-scope for the engineering-workflow toolkit: specs live in Jira/Confluence and the QRSPI/QRASPI workflows own technical spec/plan. All three skill-only, no agents/commands. `to-prd`/`to-issues` attribution entries removed from `.matt-pocock-attribution.yml`; the Product & GitHub suite row removed from the Skill Suites table. `codebase-design` added 2026-07-11 (was 89 → 90): the mattpocock deep-module vocabulary skill (team, team 77 → 78) — glossary of module/interface/depth/seam/adapter/leverage/locality + `references/DEEPENING.md` + `references/DESIGN-IT-TWICE.md`; `disable-model-invocation` vocabulary provider, no agent/command. Fills the APOSD vocabulary dependency the earlier `improve-codebase-architecture` port assumed but never imported; cross-linked from that skill's intro + Integration. `substack-writer` added 2026-07-04 (was 88 → 89): multi-pass editorial pipeline turning raw technical notes into publication-quality Substack/blog posts (professional); skill-only, no agent/command (professional 11 → 12, team unchanged at 77). `oss-vetting` added 2026-06-25 (was 87 → 88): federal OSS/SBOM vetting assessment skill (team), with paired `oss-vetting-agent` in both runtimes (agents 44/44 → 45/45) and `/oss-vetting` command in both runtimes (commands 24/24 → 25/25). PARA knowledge-management pair added 2026-06-20 (was 85 → 87): `para-file` + `para-review` (team), each with `/para-file` + `/para-review` commands in both runtimes (commands 22 → 24); no agents. Edge supplement spin-out 2026-06-20 moved 5 more out (was 90 → 85): `model-optimization`, `ollama-model-workflow`, `rag-pipeline-python`, `rag-pipeline-dotnet`, `mcp-server-scaffold` → `edge-ai-robotics-automation-toolkit`. Quality prune 2026-06-20 dropped 8 (was 98 → 90): the edge/IoT/robotics cluster (`picar-x-behavior`, `jetson-deploy`, `sensor-integration`, `edge-cv-pipeline`, `fleet-management`, `anomaly-detection`) + `caveman` + `tdd-pair`. `dotnet-controller-api-scaffolder` added 2026-06-03 (was 102 → 103): controller-based Web API scaffolder that conforms to existing conventions; skill-only, no agent/command (matches the .NET family convention — `minimal-api-scaffolder` et al. have no agents). Same change made `dotnet-architecture-checklist` style-aware (layered/N-tier controller branch via `references/layered-ntier.md`) — no count change. QRSPI added 5 phase skills 2026-06-02 (was 81); QRASPI added 8 (`fitness-functions` + the 7 phase/graduate skills) 2026-06-03 (was 86, → 94); TDD cluster consolidated 8→5 on 2026-06-03 (→ 91); cross-language architecture+security parity 2026-06-03 (renamed `python-arch-review`→`python-architecture-checklist`; +`php-architecture-checklist`, +`php-security-review`, +`security-review-federal`; −`dotnet-security-review-federal`, −`python-security-review-federal` → 92); PHP family parity 2026-06-03 (+`php-feature-slice`, +`php-api-scaffolder`, +`php-package-scaffold`, +`php-migration-manager` → 96); React family parity 2026-06-03 (+`react-architecture-checklist`, +`react-security-review`, +`react-feature-slice`, +`react-component-scaffolder`, +`react-app-scaffolder`, +`react-modernization-analyzer` → 102 → 103 with `dotnet-controller-api-scaffolder`); RPI sunset 2026-06-19 removed the 4 `rpi-*` skills + `spec-implement` (→ 98).
- [x] Agent count parity — Claude Code (51) vs. OpenCode (51) — Vue family added `vue-arch-checklist-agent`, `vue-security-agent`, `vue-modernization-agent`, `vue-feature-slice-agent`, `vue-component-scaffold-agent`, `vue-app-scaffold-agent` in both runtimes 2026-07-19 (was 45/45 → 51/51); `oss-vetting-agent` added in both runtimes 2026-06-25 (was 44/44 → 45/45); edge supplement spin-out 2026-06-20 moved `model-optimization-agent` to `edge-ai-robotics-automation-toolkit` in both runtimes (was 45/45 → 44/44); quality prune 2026-06-20 removed `sensor-anomaly-agent` + `fleet-deployment-agent` in both runtimes (was 47/47 → 45/45); QRSPI added `qrspi-orchestrator` + `qrspi-implement` 2026-06-02 (was 35/35, resolved 2026-05-19); QRASPI added `qraspi-orchestrator` + `qraspi-builder` 2026-06-03 (was 37/37); PHP family parity 2026-06-03 added `php-feature-slice-agent`, `php-api-scaffold-agent`, `php-package-agent`, `php-migration-agent` in both runtimes (was 39/39, → 43/43); React family parity 2026-06-03 added `react-feature-slice-agent`, `react-component-scaffold-agent`, `react-app-scaffold-agent`, `react-security-agent`, `react-modernization-agent`, `react-arch-checklist-agent` in both runtimes (was 43/43, → 49/49); RPI sunset 2026-06-19 removed `rpi-planner`/`rpi-implement` in both runtimes (→ 47/47).
- [x] Commands layer — `claude/commands/` (25 commands) and `opencode/commands/` (25 commands) — `/oss-vetting` added in both runtimes 2026-06-25 (was 24/24 → 25/25) — PARA pair added `/para-file` + `/para-review` 2026-06-20 (was 22/22) — QRSPI added 5 (`/qrspi-questions`…`/qrspi-implement`) 2026-06-02 (was 10/10); QRASPI added 7 (`/qraspi-questions`…`/qraspi-graduate`) 2026-06-03 (was 15/15). No `rpi-*` commands, so sunset leaves commands at 22.
- [x] Lean-layout migration — every full-template `SKILL.md` is ≤ 200 lines with the 5 canonical sections and ≥ 2 reference files (completed 2026-06-26). Re-verify with the Contributor Validation commands after adding or editing a skill.

---

## Skill Suites

| Suite | Skills | Focus |
|-------|--------|-------|
| TDD | tdd (the canonical loop) + tdd-agent (autonomous operating mode) + evaluate-tests (quality & compliance audit) | Test-Driven Development lifecycle |
| Enterprise .NET | dotnet-vertical-slice, ef-migration-manager, nuget-package-scaffold, legacy-migration-analyzer, dotnet-architecture-checklist, dotnet-controller-api-scaffolder, dotnet-security-review, minimal-api-scaffolder, 4d-schema-migration | .NET patterns, migrations, security |
| Security (cross-language) | security-review-federal, oss-vetting | Shared language-agnostic federal/gov work. `security-review-federal` is the overlay (NIST 800-53, FIPS, CUI, POA&M, EO 14028, DOE 205.1B) applied on top of any base `<lang>-security-review`; `oss-vetting` produces a structured OSS/SBOM assessment for federal contractor environments (LANL/DOE/CUI) — security posture, supply chain risk, license compliance, CUI suitability against four governing frameworks; Confluence-ready report. |
| Coaching | architecture-review, pattern-tradeoff-analyzer, system-design-kata, dependency-mapper, code-review-coach, refactor-challenger, security-review-trainer, pr-feedback-writer, technical-debt-assessor, architecture-journal, grill-me, zoom-out, improve-codebase-architecture, codebase-design | Engineering judgment and communication modes. `codebase-design` supplies the deep-module vocabulary `improve-codebase-architecture` applies. |
| DDD | domain-model | Domain-Driven Design vocabulary and modeling |
| Agent Support | automated-code-review, test-scaffold, doc-sync, supply-chain-audit, environment-health, research-synthesis, session-context, task-decomposition | Domain knowledge for agents |
| Agent Design | spec-coach | Interactive spec design coach — skills, agents, PRDs, and GitHub Spec Kit |
| QRSPI Workflow | qrspi-questions, qrspi-research, qrspi-spec, qrspi-plan, qrspi-implement | Questions-Research-Spec-Plan-Implement: instruction-budget-disciplined replacement for RPI. No-magic-words artifact gates, ticket-hidden research, Design Brain-Dump → Structure Outline, vertical-slice plans, per-slice Red-Green-Refactor. Driven by the `qrspi-orchestrator` (alignment) + `qrspi-implement` (execution) agents and the renamed `research-*` read-only subagents. For an EXISTING codebase / adding a feature. |
| QRASPI Workflow | fitness-functions, qraspi-questions, qraspi-research, qraspi-architecture, qraspi-skeleton, qraspi-plan, qraspi-implement, qraspi-graduate | Questions-Research-Architecture-Skeleton-Plan-Implement for a NEW system (greenfield V0/V1), then graduation to QRSPI. Locks path-dependent decisions as MADR ADRs with alternatives + Mermaid C4, lands a runnable walking skeleton with fitness functions as merge-blocking CI gates (CI-green exit gate), grows it slice-by-slice with Red-Green-Refactor, then hands off to QRSPI. Driven by `qraspi-orchestrator` (no-edit Q/R/A/P/graduate) + `qraspi-builder` (edit Skeleton/Implement); `fitness-functions` is the one extracted primitive. For a NEW system from scratch — the greenfield counterpart to QRSPI. |
| Python | python-architecture-checklist, python-security-review, python-feature-slice, alembic-migration-manager, python-modernization-analyzer, fastapi-scaffolder, pypi-package-scaffold | Python patterns, migrations, security, packaging |
| PHP | php-architecture-checklist, php-security-review, php-feature-slice, php-api-scaffolder, php-package-scaffold, php-migration-manager | PHP/Laravel architecture, security, scaffolding, migrations |
| Rust | rust-architecture-checklist, rust-security-review, rust-feature-slice, sqlx-migration-manager, rust-migration-analyzer, axum-scaffolder, cargo-package-scaffold | Rust architecture, security, migrations, API scaffolding, packaging |
| Vue | vue-architecture-checklist, vue-security-review, vue-feature-slice, vue-component-scaffolder, vue-app-scaffolder, vue-modernization-analyzer | Vue architecture, security, feature scaffolding, component/app scaffolding, modernization — second frontend family, mirrors the React suite |
| Knowledge Management (PARA) | para-file, para-review | The PARA method (Tiago Forte) applied to documents across local folders, OneDrive/Teams synced paths, and Confluence/Jira. `para-file` captures/classifies/files one item by actionability (scaffolding the P/A/R/Archive tree if missing); `para-review` runs the hygiene audit + weekly ritual + summarization + safe reversible archiving. Share a per-project `.para.yml`. User-invocable via `/para-file` and `/para-review`. No agents. |
| Writing & Portfolio | substack-writer | Editorial pipeline for professional portfolio writing — turns the author's raw technical notes into publication-quality Substack/blog posts through a multi-pass revision loop; the human stays the source of technical substance. Professional track, no agent/command. |
| Other | jira-review, jira-comment-writer, confluence-guide-writer | Language/tool-specific reviews and documentation generation |

---

## Team

| Name | Role | Notes |
|---|---|---|
| Michael K. Alber | Owner / Primary contributor | Reviews all changes to global files and project-templates |

---

## Project Boot Ritual

Follow the global Session Boot Ritual (see global `CLAUDE.md` / `AGENTS.md`). Repo-specific deltas:
read this file plus `intent.md` and `constraints.md`, and confirm the **Persistent Decisions** and
**Open Loops** above before starting. Tooling (grounded-code-mcp, Microsoft Learn MCP, grounding
workflow) is defined globally — not repeated here.
