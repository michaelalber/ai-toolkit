# AI Toolkit — Evals
<!-- Discipline 4: Specification Engineering — Primitive 5: Evaluation Design
     Framework: Four Prompt Disciplines & Five Primitives (Nate B. Jones, v2026.03.2)

     PROJECT-LEVEL FILE — supplements claude/global/CLAUDE.md and opencode/global/AGENTS.md.
     Evals are safety infrastructure. Write them before the agent starts.
     A skill that "looks complete" is not done until it passes these checks. -->

---

## Eval Philosophy

Evals answer: *"Is the output actually good?"* — not *"does it look reasonable?"*

For this project, "good" means: a skill or agent that any developer can install, invoke, and get
correct, consistent, professional output from — without reading the source or asking questions.

A passing eval would survive scrutiny from a developer seeing the skill for the first time.

---

## Test Cases

### Test Case 1: New Skill Completeness

- **Input:** A newly created or modified skill in `skills/<name>/SKILL.md`
- **Known-Good Output:** `skills/architecture-review/SKILL.md` — the gold standard
- **Pass Criteria:**
  - [ ] All 10 sections present and in order (Title+Epigraph, Philosophy, Principles, Workflow, State Block, Templates, Rules, Anti-Patterns, Error Recovery, Integration)
  - [ ] Frontmatter has `name` and `description` with at least 2 trigger phrases
  - [ ] State block XML tag is unique — not used by any other skill or agent
  - [ ] `references/` directory exists with at least 2 files
  - [ ] No placeholder text remaining (`TODO`, `[fill in]`, `[e.g., ...]`)
- **Last Run:** — | **Result:** —
- **Notes:** —

---

### Test Case 2: Agent Parity

- **Input:** A newly created or modified agent (Claude Code or OpenCode version)
- **Known-Good Output:** Matching agent in the other platform directory with identical behavior
- **Pass Criteria:**
  - [ ] Both `claude/agents/<name>.md` and `opencode/agents/<name>.md` exist (unless single-platform with documented reason)
  - [ ] Claude Code frontmatter uses `tools:` as a list and `skills:` array; `model: inherit`
  - [ ] OpenCode frontmatter uses `tools:` as boolean map and `mode: subagent`; no model field
  - [ ] OpenCode body uses `skill({ name: "..." })` calls where Claude Code uses `skills:` frontmatter
  - [ ] All 10 agent sections present in both versions
  - [ ] State block XML tag is unique across all skills and agents
- **Last Run:** — | **Result:** —
- **Notes:** —

---

### Test Case 3: Project Template Usability

- **Input:** Any file in `project-templates/`
- **Known-Good Output:** A file a developer can copy to a new project root and fill in within 15 minutes without external documentation
- **Pass Criteria:**
  - [ ] Prominent "PROJECT-LEVEL — NOT GLOBAL" warning at the top
  - [ ] Every placeholder is clearly marked and explains what to put there
  - [ ] File references are consistent (`AGENTS.md` for OpenCode, `CLAUDE.md` for Claude Code)
  - [ ] No content duplicated from `claude/global/CLAUDE.md` or `opencode/global/AGENTS.md`
  - [ ] The file architecture table (global vs. project level) is present in `CLAUDE.md` and `AGENTS.md` templates
- **Last Run:** — | **Result:** —
- **Notes:** —

---

### Test Case 4: Repository Metadata Sync

- **Input:** Any commit that adds or removes a skill or agent
- **Pass Criteria:**
  - [ ] Skill count in `AGENTS.md` (root) matches actual count in `skills/`
  - [ ] Agent count in `README.md` matches actual count in `claude/agents/` and `opencode/agents/`
  - [ ] New skill appears in the correct suite table in `README.md`
  - [ ] New agent appears in the correct category table in `README.md`
- **Last Run:** — | **Result:** —
- **Notes:** —

---

### Test Case 5: Global Config File Integrity

- **Input:** Any commit that modifies `claude/global/CLAUDE.md`, `opencode/global/AGENTS.md`, `claude/global/settings.local.json`, or either `README.md` under `claude/global/` or `opencode/global/`
- **Known-Good Output:** Both global files retain all expected top-level sections; installation instructions in READMEs match actual platform paths; optional sections remain properly marked
- **Pass Criteria:**
  - [ ] `claude/global/CLAUDE.md` still contains all mandatory sections: Session Boot Ritual, Core Philosophy, Intent Engineering, Prompting Patterns, Context Management, Project File Architecture, AI Agent Obligations, Evaluation Design, Security-By-Design, Code Quality Gates, and all language-standard sections
  - [ ] `opencode/global/AGENTS.md` structure mirrors `claude/global/CLAUDE.md` in intent and coverage — no section present in one and absent in the other without documented rationale
  - [ ] Install paths in both READMEs (`~/.claude/` and `~/.config/opencode/`) are current and accurate for the respective platforms
  - [ ] Optional-dependency sections (Snyk, grounded-code-mcp, Jira) remain clearly marked as optional with removal instructions
  - [ ] No instruction in either global file contradicts a convention defined in `project-templates/CLAUDE.md` or `project-templates/AGENTS.md`
  - [ ] Human explicitly approved the change before it was committed (per `constraints.md`)
- **Last Run:** — | **Result:** —
- **Notes:** These files install globally and affect every project on the user's machine. A silent structural regression here is the highest blast-radius change this repo can make.

---

### Test Case 6: Behavioral Correctness (Skill Invocation)

- **Input:** A newly created or significantly modified skill, invoked on a representative prompt in Claude Code or OpenCode
- **Known-Good Output:** The skill's own Workflow section — the phases, exit criteria, and output templates define what correct behavior looks like
- **Pass Criteria:**
  - [ ] The agent follows the skill's defined workflow phases in order and does not skip phases
  - [ ] The output matches the Output Templates section (correct headings, table structure, checklist format)
  - [ ] State block XML tag is emitted and populated when the skill is multi-turn
  - [ ] No phase produces output that contradicts the skill's Core Philosophy or AI Discipline Rules
  - [ ] The skill reaches a natural conclusion (does not stall, loop, or produce an empty final report)
- **Last Run:** — | **Result:** —
- **Notes:** This is a manual spot-check, not automated. Run it on the gold-standard skill (`architecture-review`) after any structural template change to confirm baseline behavior holds, then run it on any new skill before marking it done. Structural completeness (TC1) is necessary but not sufficient — a skill can pass TC1 and still produce incoherent output.

---

### Test Case 7: Link and Cross-Reference Integrity

- **Input:** Any commit that adds, renames, removes, or moves a skill or agent
- **Pass Criteria:**
  - [ ] Every skill name in `README.md` suite tables matches an actual directory in `skills/`
  - [ ] Every skill name cited in an Integration section (`skills/*/SKILL.md`) resolves to a real `skills/<name>/SKILL.md`
  - [ ] Every agent name in `README.md` category tables matches an actual file in `claude/agents/` and `opencode/agents/`
  - [ ] No `references/` file mentions a skill or agent by name that no longer exists
  - [ ] The skill-to-skill cross-references in Integration sections are symmetric: if Skill A lists Skill B, Skill B's Integration section lists Skill A (or documents why the relationship is one-directional)
- **Last Run:** — | **Result:** —
- **Notes:** Silent link rot is common in fast-growing skill suites. Check manually after any rename or removal, or automate with a simple grep against the `skills/` directory listing.

---

### Test Case 8: Project Template vs. Actual File Parity

- **Input:** Any commit that changes the section structure of root `CLAUDE.md`, `AGENTS.md`, `intent.md`, `constraints.md`, or `evals.md`
- **Pass Criteria:**
  - [ ] `project-templates/CLAUDE.md` reflects any new mandatory section added to the root `CLAUDE.md`
  - [ ] `project-templates/AGENTS.md` reflects any new mandatory section added to the root `AGENTS.md`
  - [ ] `project-templates/evals.md` Test Case structure matches the current test case format in this file
  - [ ] No placeholder in `project-templates/` references a toolkit-specific convention without explaining it to the user
  - [ ] `claude/global/README.md` file-template block for `evals.md` reflects the current section structure
- **Last Run:** — | **Result:** —
- **Notes:** Templates that drift from the real files mislead developers who copy them into their own projects.

---

## CI Gate

This is a Markdown-only repo — there is no build or test runner. The CI gate consists of manual verification steps that must pass before any PR is merged.

- **Frontmatter validation:** All `SKILL.md` and agent `.md` files have `name` and `description` fields with non-empty values
- **State block uniqueness:** `grep -r "<.*-state>" skills/ claude/agents/ opencode/agents/` — every tag must appear exactly once across all files
- **Link integrity (README):** All skill names in `README.md` suite tables resolve to actual `skills/<name>/` directories
- **References population:** Every `skills/<name>/` has a `references/` subdirectory with ≥ 2 files
- **No placeholder text:** `grep -r "TODO\|\[fill in\]\|\[e\.g\." skills/ claude/agents/ opencode/agents/` — must return no results in committed files

> Append CI gate results as a sub-item of each Test Case entry on every run.

---

## Taste Rules (Encoded Rejections)

| # | Pattern to Reject | Why It Fails | Rule |
|---|---|---|---|
| 1 | Skill with fewer than 10 sections | Incomplete skills produce inconsistent agent behavior | Always verify against the gold standard before considering a skill done |
| 2 | Agent added to Claude only, no OpenCode version | Breaks parity; users on OpenCode get no equivalent | Always create both versions in the same task |
| 3 | State block XML tag reused from another skill | Two skills competing for the same state tag corrupts multi-turn sessions | Search all `SKILL.md` and agent files for the tag before using it |
| 4 | Project-template file that omits the global vs. project-level distinction | Users copy templates without understanding what the file replaces | Every CLAUDE.md and AGENTS.md template must include the file architecture note |
| 5 | PyTorch evaluation mode method call in Python code examples | Triggers the security hook even in documentation context | Use `model.train(False)` or describe the call in prose only |
| 6 | Modifying `claude/global/CLAUDE.md` or `opencode/global/AGENTS.md` without running TC5 | These files install globally — a silent structural regression affects every project the user opens | Always run TC5 checks and get explicit human approval before committing global config changes |
| 7 | Declaring a new skill "done" based on TC1 alone | Structural completeness does not mean behavioral correctness — a 10-section skill can still produce incoherent output | Run TC6 (manual invocation spot-check) on any new or significantly revised skill before marking it done |
| 8 | Renaming or removing a skill without checking Integration sections | Cross-references in Integration sections silently break; other skills point to a name that no longer exists | After any rename or removal, grep `skills/*/SKILL.md` for the old name and update all references |

---

## Rejection Log

<!-- Append entries as outputs are rejected. Never delete. -->

### 2026-04-18 — Initial project-template set

- **What was generated:** `templates/` directory with 5 files (no CLAUDE.md, no AGENTS.md templates)
- **What was wrong:** Missing the foundational context engineering file; all other templates referenced it but it didn't exist as a template
- **Why it was wrong:** Templates were derived from Nate's framework without adapting for the two-level (global / project) file architecture used in this toolkit
- **Rule extracted:** Any template set must include the context engineering file (CLAUDE.md / AGENTS.md) with the global-vs-project distinction prominently documented → added as Taste Rule 4 above
