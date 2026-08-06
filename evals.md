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
- **Known-Good Output:** `skills/cargo-package-scaffold/SKILL.md` — the gold standard
- **Pass Criteria:**
  - [ ] The 5 lean sections present and in order (Core Philosophy, Workflow, State Block, Output Template, Integration), after the title + epigraph
  - [ ] SKILL.md ≤ 200 lines; no inline principle/anti-pattern/error-recovery tables (depth lives in `references/`)
  - [ ] Core Philosophy includes a numbered Non-Negotiable Constraints list (the Critical/High principles)
  - [ ] Output Template names each report/code template with a `references/...` pointer
  - [ ] Frontmatter has `name` and `description` with at least 2 trigger phrases and a "Do NOT use when..." clause
  - [ ] State block XML tag is unique — not used by any other skill or agent
  - [ ] `references/` directory exists with at least 2 files, each named by a pointer in SKILL.md
  - [ ] `references/conventions.md` (or equivalents) carries the depth: principle table, ≥ 3 WRONG/RIGHT rules, ≥ 8-row anti-patterns table, ≥ 3 error-recovery scenarios
  - [ ] No placeholder text remaining (`TODO`, `[fill in]`, `[e.g., ...]`)
- **Automated by:** `tools/skill-evals` — SK001–SK010 (frontmatter), SK020–SK027 (layout), SK030–SK033 (state), SK040–SK044 (references). Run `skill-evals lint`.
- **Last Run:** 2026-08-02 (`skill-evals lint`) | **Result:** PASS — 0 error(s), 394 warning(s) over 94 skills
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
- **Automated by:** `tools/skill-evals` — SK033 (state-tag collisions across skills and agents), SK058 (Claude/OpenCode agent parity). The per-platform frontmatter shape is still a manual check.
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
  - [ ] Skill count in `AGENTS.md` (root) Purpose line and Open Loops entry matches actual `find skills/ -maxdepth 2 -name SKILL.md | wc -l`
  - [ ] Agent count in `README.md` at-a-glance table and `AGENTS.md` matches actual `find claude/agents opencode/agents -name '*.md' | wc -l`
  - [ ] `README.md` badge counts (skills, agents) match the at-a-glance table
  - [ ] `README.md` repo-structure comments (team agent counts, command counts) are current
  - [ ] New skill appears in the correct suite row in **both** `README.md` and `AGENTS.md` Skill Suites table
  - [ ] New agent appears in the correct category table in `README.md`
  - [ ] New skill has a Green / Yellow / Red entry in `pi/SKILLS-local.md` with a one-line rationale
- **Automated by:** `tools/skill-evals` — SK053–SK057 (Pi triage coverage and counts, README listings and badges, CLAUDE.md/AGENTS.md counts), SK059 (the mirror pair). Counts are read from the tree, never hardcoded.
- **Last Run:** — | **Result:** —
- **Notes:** Count drift is the most common regression here. The constraints.md now lists every exact location to update; this test case verifies they were all hit.

---

### Test Case 5: Global Config File Integrity

- **Input:** Any commit that modifies `claude/global/CLAUDE.md`, `opencode/global/AGENTS.md`, `claude/global/settings.local.json`, any file under `pi/global/`, or either `README.md` under `claude/global/` or `opencode/global/`
- **Known-Good Output:** Both global files retain all expected top-level sections; installation instructions in READMEs match actual platform paths; optional sections remain properly marked
- **Pass Criteria:**
  - [ ] `claude/global/CLAUDE.md` still contains all mandatory sections: Session Boot Ritual, Core Philosophy, Intent Engineering, Prompting Patterns, Context Management, Project File Architecture, AI Agent Obligations, Evaluation Design, Security-By-Design, Code Quality Gates, and all language-standard sections
  - [ ] `opencode/global/AGENTS.md` structure mirrors `claude/global/CLAUDE.md` in intent and coverage — no section present in one and absent in the other without documented rationale
  - [ ] Install paths in both READMEs (`~/.claude/` and `~/.config/opencode/`) are current and accurate for the respective platforms
  - [ ] Optional-dependency sections (Snyk, grounded-code-mcp, Jira) remain clearly marked as optional with removal instructions
  - [ ] No instruction in either global file contradicts a convention defined in `project-templates/CLAUDE.md` or `project-templates/AGENTS.md`
  - [ ] `pi/global/AGENTS.md`, `pi/global/settings.json`, and `pi/global/models.json` are internally consistent — model IDs in `models.json` match Modelfile `FROM` lines; `settings.json` compaction values are within the context windows declared in `models.json`
  - [ ] `pi/global/README.md` install steps match what `scripts/install-pi.sh` actually does
  - [ ] Human explicitly approved the change before it was committed (per `constraints.md`)
- **Last Run:** — | **Result:** —
- **Notes:** These files install globally and affect every project on the user's machine. A silent structural regression here is the highest blast-radius change this repo can make. `pi/global/` is a third install target alongside `claude/global/` and `opencode/global/` with identical blast radius.

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
- **Partially automated by:** `tools/skill-evals` — `skill-evals quality` injects a SKILL.md as the system prompt and judges the output against that skill's own acceptance criteria, over the curated set in `tools/skill-evals/datasets/quality.jsonl`. Still a manual spot-check for skills outside that set.
- **Last Run:** — | **Result:** —
- **Notes:** This is a manual spot-check, not automated. Run it on the gold-standard skill (`cargo-package-scaffold`) after any structural template change to confirm baseline behavior holds, then run it on any new skill before marking it done. Structural completeness (TC1) is necessary but not sufficient — a skill can pass TC1 and still produce incoherent output.

---

### Test Case 7: Link and Cross-Reference Integrity

- **Input:** Any commit that adds, renames, removes, or moves a skill or agent
- **Pass Criteria:**
  - [ ] Every skill name in `README.md` suite tables matches an actual directory in `skills/`
  - [ ] Every skill name cited in an Integration section (`skills/*/SKILL.md`) resolves to a real `skills/<name>/SKILL.md`
  - [ ] Every agent name in `README.md` category tables matches an actual file in `claude/agents/` and `opencode/agents/`
  - [ ] No `references/` file mentions a skill or agent by name that no longer exists
  - [ ] The skill-to-skill cross-references in Integration sections are symmetric: if Skill A lists Skill B, Skill B's Integration section lists Skill A (or documents why the relationship is one-directional)
- **Automated by:** `tools/skill-evals` — SK042 (references/ pointers resolve), SK050 (Integration targets exist), SK051 (symmetry, informational), SK052 (stale renames), SK054/SK056 (Pi and README entries resolve).
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

### Test Case 9: Skill Rubric Scorecard

- **Input:** All `skills/*/SKILL.md`
- **Known-Good Output:** `skills/skill-creator/references/scoring-rubric.md` — parsed at run time, so the rubric file stays the single source of truth
- **Pass Criteria:**
  - [ ] No skill lands a DEPRECATE verdict (< 25 / 50)
  - [ ] The REVISE count has not increased against the committed baseline in `tools/skill-evals/baselines/`
  - [ ] Judge parse-failure rate < 10% — above that the judge is broken and the scores say nothing about the skills
- **Command:** `cd tools/skill-evals && uv run skill-evals scorecard --gate`
- **Automated by:** `tools/skill-evals` — one judge call per dimension, with deterministic overrides on the mechanical dimensions (layout, state uniqueness, reference hygiene) so roughly 3 of 10 are fully reproducible.
- **Last Run:** — | **Result:** —
- **Notes:** Baselines are produced with `--samples 3` and median aggregation. Run the first baseline three times and publish the per-dimension variance before treating this as a gate — an uncalibrated judge is worse than none.

---

### Test Case 10: Trigger Precision and Description Collisions

- **Input:** `tools/skill-evals/datasets/routing.jsonl` (60 cases) against the live roster built from `skills/`
- **Pass Criteria:**
  - [ ] Top-1 accuracy at or above the committed floor
  - [ ] No new collision pair at or above 20% — a pair the model confuses that it did not before
  - [ ] Every `disable-model-invocation` skill records zero auto-selections
  - [ ] Judge/model parse-failure rate < 10%
- **Command:** `cd tools/skill-evals && uv run skill-evals route --floor 0.85`
- **Automated by:** `tools/skill-evals` — the roster is rebuilt from the corpus each run and its sha256 recorded, so a description change visibly invalidates a baseline instead of silently shifting it.
- **Last Run:** — | **Result:** —
- **Notes:** Cases are stratified: canonical trigger, confusion pair (chosen mechanically by description similarity, not taste), negative, boundary, and non-invocable.

---

## Local Gate (no CI)

There is no CI in this repo, by design. The gate is a command you run before committing, and
it exits non-zero.

```bash
cd tools/skill-evals
uv run skill-evals lint --baseline baselines/known-defects.yaml   # structural — no model needed
uv run skill-evals route --floor 0.85                             # trigger precision
uv run skill-evals scorecard --gate                               # rubric verdicts
```

Exit codes are uniform: `0` clean · `1` gate failure · `2` usage or environment · `3` the
judge is unusable, so "the model is broken" never reads as "the skills are bad".

`skill-evals lint` replaces the six manual grep checks this section used to list. One of
those greps — the Pi triage coverage check — **matched nothing at all**, because it assumed
backticked table rows that `pi/SKILLS-local.md` does not have. It therefore reported every
skill as untriaged on every run, which is why nobody ran it twice. `SK053`/`SK054`/`SK055`
parse the table instead, and `tests/test_real_corpus.py` pins that the old grep finds
nothing so the mistake cannot be reintroduced.

> Record results with `skill-evals evals-md --date <today> --write`, which fills the
> Last Run / Result fields above and touches nothing else.

---

## Taste Rules (Encoded Rejections)

| # | Pattern to Reject | Why It Fails | Rule |
|---|---|---|---|
| 1 | Skill that inlines depth or breaks the 5-section lean layout | Every always-loaded section is a per-invocation token tax; bloated SKILL.md degrades reliability, worst on small local models | Keep SKILL.md to the 5 sections (≤ 200 lines); push principle tables, anti-patterns, discipline rules, error recovery, and templates to `references/` |
| 2 | Agent added to Claude only, no OpenCode version | Breaks parity; users on OpenCode get no equivalent | Always create both versions in the same task |
| 3 | State block XML tag reused outside a declared family | Two unrelated skills competing for the same state tag corrupts multi-turn sessions. A *family* may share one — all six `*-security-review` run one workflow over different languages, so the tag names the workflow — but the family must be declared in `tools/skill-evals/baselines/state-tag-families.yaml` with a written rationale | `skill-evals lint --rule SK032` before using a tag; add a family entry or rename |
| 4 | Project-template file that omits the global vs. project-level distinction | Users copy templates without understanding what the file replaces | Every CLAUDE.md and AGENTS.md template must include the file architecture note |
| 5 | PyTorch evaluation mode method call in Python code examples | Triggers the security hook even in documentation context | Use `model.train(False)` or describe the call in prose only |
| 6 | Modifying `claude/global/CLAUDE.md`, `opencode/global/AGENTS.md`, or any `pi/global/` file without running TC5 | These files install globally — a silent structural regression affects every project the user opens | Always run TC5 checks and get explicit human approval before committing global config changes |
| 7 | Declaring a new skill "done" based on TC1 alone | Structural completeness does not mean behavioral correctness — a structurally complete skill can still produce incoherent output | Run TC6 (manual invocation spot-check) on any new or significantly revised skill before marking it done |
| 8 | Renaming or removing a skill without checking Integration sections | Cross-references in Integration sections silently break; other skills point to a name that no longer exists | Run `skill-evals lint --rule SK050 --rule SK052 --rule SK054 --rule SK056` after any rename. The `tdd` → `tdd-loop` rename left 18 Integration rows, 2 reference pointers, a Pi triage row, and a README row pointing at a name that no longer existed — for months, silently |
| 9 | Adding or editing a skill without running `skill-evals lint` | Every structural invariant in this file is now executable. Not running it is choosing not to know | `cd tools/skill-evals && uv run skill-evals lint` before committing any change under `skills/` |
| 10 | Silencing a lint finding by lowering its severity | Severity records how bad a defect is, not how inconvenient it is today. Editing it to make the gate quiet destroys the signal for everyone afterwards | Either fix the finding, or add it to `baselines/known-defects.yaml` **with a written reason**. The baseline is a decision log, not a mute button |

---

## Rejection Log

<!-- Append entries as outputs are rejected. Never delete. -->

### 2026-04-18 — Initial project-template set

- **What was generated:** `templates/` directory with 5 files (no CLAUDE.md, no AGENTS.md templates)
- **What was wrong:** Missing the foundational context engineering file; all other templates referenced it but it didn't exist as a template
- **Why it was wrong:** Templates were derived from Nate's framework without adapting for the two-level (global / project) file architecture used in this toolkit
- **Rule extracted:** Any template set must include the context engineering file (CLAUDE.md / AGENTS.md) with the global-vs-project distinction prominently documented → added as Taste Rule 4 above
