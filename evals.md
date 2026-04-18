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

## Taste Rules (Encoded Rejections)

| # | Pattern to Reject | Why It Fails | Rule |
|---|---|---|---|
| 1 | Skill with fewer than 10 sections | Incomplete skills produce inconsistent agent behavior | Always verify against the gold standard before considering a skill done |
| 2 | Agent added to Claude only, no OpenCode version | Breaks parity; users on OpenCode get no equivalent | Always create both versions in the same task |
| 3 | State block XML tag reused from another skill | Two skills competing for the same state tag corrupts multi-turn sessions | Search all `SKILL.md` and agent files for the tag before using it |
| 4 | Project-template file that omits the global vs. project-level distinction | Users copy templates without understanding what the file replaces | Every CLAUDE.md and AGENTS.md template must include the file architecture note |
| 5 | PyTorch evaluation mode method call in Python code examples | Triggers the security hook even in documentation context | Use `model.train(False)` or describe the call in prose only |

---

## Rejection Log

<!-- Append entries as outputs are rejected. Never delete. -->

### 2026-04-18 — Initial project-template set

- **What was generated:** `templates/` directory with 5 files (no CLAUDE.md, no AGENTS.md templates)
- **What was wrong:** Missing the foundational context engineering file; all other templates referenced it but it didn't exist as a template
- **Why it was wrong:** Templates were derived from Nate's framework without adapting for the two-level (global / project) file architecture used in this toolkit
- **Rule extracted:** Any template set must include the context engineering file (CLAUDE.md / AGENTS.md) with the global-vs-project distinction prominently documented → added as Taste Rule 4 above
