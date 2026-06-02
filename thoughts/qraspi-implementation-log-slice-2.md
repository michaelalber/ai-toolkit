---
date: 2026-06-02
repository: ai-toolkit
topic: "QRASPI Slice 2 — qraspi-questions + qraspi-research + orchestrator (RPI Implement phase)"
plan: thoughts/qraspi-plan.md
slice: 2
branch: qraspi-slice-2-questions-research
status: complete
---

# QRASPI Slice 2 — `qraspi-questions` + `qraspi-research` (greenfield entry point)

Implements Plan §6 Slice 2: the smallest viable QRASPI entry point. A user can now run
`/qraspi-questions` then `/qraspi-research` and get a balanced six-category `questions.md` plus a
factual landscape-map `research.md` in a per-project folder. Q→R works standalone.

## What was done

| File | Lines | Purpose |
|------|-------|---------|
| `skills/team/qraspi-questions/SKILL.md` | 94 | Minimal-tier Questions phase; fixed six-category greenfield checklist; STOPS for answers |
| `skills/team/qraspi-questions/references/questions-template.md` | 60 | `questions.md` structure — one heading per greenfield category, inline `**A:**` lines |
| `skills/team/qraspi-research/SKILL.md` | 112 | Minimal-tier Research phase; landscape-not-evaluation; `research_mode` switch (#10) |
| `skills/team/qraspi-research/references/research-template.md` | 66 | `research.md` structure — landscape findings + "options on the table" (NOT a pick) |
| `skills/team/qraspi-research/references/landscape-vs-codebase.md` | 62 | Mode detection + per-mode evidence rules (external-domain default / inherited-repo) |
| `claude/agents/team/qraspi-orchestrator.md` | full 10-section | Greenfield alignment orchestrator, `skills:[qraspi-questions, qraspi-research]`, **no Edit** |
| `opencode/agents/team/qraspi-orchestrator.md` | parity | OpenCode mirror — `edit: false`, `skill({ name })` calls |
| `claude/commands/qraspi-questions.md` | — | `/qraspi-questions <project>`, `!`-injected `ls` of `thoughts/shared/qraspi/`, routes to orchestrator |
| `claude/commands/qraspi-research.md` | — | `/qraspi-research <project>`, mode-aware routing, restates the landscape gate |
| `opencode/commands/qraspi-questions.md` | parity | `agent: qraspi-orchestrator`, `subtask: true` (read-heavy) |
| `opencode/commands/qraspi-research.md` | parity | `agent: qraspi-orchestrator`, `subtask: true` |

### Convention conformance (per session constraints)

- **Prose voice + frontmatter** match the landed `qrspi-questions` / `qrspi-research` skills exactly:
  block-scalar `description` with positive triggers + the phase-skill negative trigger
  `Do NOT use for QRSPI (an EXISTING codebase / adding a feature) -- that routes to qrspi-<phase>`
  (Plan §3) **and** the deprecated-RPI negative; an adapted-quote epigraph (Deming for Questions,
  Korzybski for Research); the verbatim 40%/60% **CONTEXT BUDGET** constraint as the last
  Non-Negotiable; the `Core Philosophy → Workflow (PRE-FLIGHT→steps→Exit criteria) → State Block →
  Output Template → Integration` 5-part shape; unique state tags `<qraspi-questions-state>`,
  `<qraspi-research-state>`.
- **Orchestrator** follows the full agent template, mirroring `qrspi-orchestrator.md`'s 10 sections
  (Core Philosophy, Available Skills, Guardrails, Autonomous Protocol, Self-Check Loops, Error
  Recovery, AI Discipline Rules, Session Template, State Block, Completion Criteria). Edit boundary
  drawn by access (#4): `tools: Read, Glob, Grep, Bash, Write` — **no Edit**; OpenCode `edit: false`.
- **Reused primitives referenced, not duplicated:** `research-synthesis` (external-domain engine)
  and the three read-only `research-*` subagents (inherited-repo mode) appear as references only —
  no content copied. The QRSPI-landed `research-*` subagents are reused as-is (Plan §6 Slice 2).
- **Matt Pocock attribution:** N/A — original work, nothing vendored (`.matt-pocock-attribution.yml`
  unchanged).

### Greenfield-specific defaults implemented (no magic words — Plan §4.1, §4.2)

- **§4.1 balanced cross-section by content:** `qraspi-questions` SURFACE step + template enumerate a
  question for **all six** categories (functional · quality-attributes · integration · compliance ·
  deployment · domain) whether or not the user named them; `areas_covered` must list all six before
  WRITE. The balance is structural, not user-requested.
- **§4.2 factual landscape, not premature recommendation:** `qraspi-research` Core Philosophy carries
  the verbatim landscape-not-evaluation rule; state flag `recommendations_made: false` must stay
  false (the greenfield analog of QRSPI's `ticket_loaded: false`); every comparative judgment is
  converted to an open question for Architecture.
- **#10 mode switch:** `research_mode` detected at PRE-FLIGHT (external-domain default vs
  inherited-repo); both modes carried in the skill body, with detection + evidence rules in
  `references/landscape-vs-codebase.md`. inherited-repo keeps the read-only-subagent + neutral-topic
  firewall; external-domain uses `research-synthesis` source-credibility discipline.

## Tests / verification that pass

This slice ships **no executable evals** (Plan §5: trigger evals are authored in a later
eval-harness session). Verification was structural, all green:

- `find skills -name SKILL.md | wc -l` → **89** (87 → 89; +2 skills this slice — see Plan-discrepancy note).
- `wc -l` new SKILLs → 94 / 112. Questions is within the ≤100 minimal-tier budget; Research is **112**
  — over by 12 because it carries the two-mode GATHER branch (external-domain + inherited-repo) inline.
  Held deliberately: the mode switch (#10) is the skill's behavioral core and splitting it would hurt
  legibility more than the 12 lines cost. Reference overflow already moved the mode *detail* to
  `landscape-vs-codebase.md`. Flagged here, not silently absorbed.
- `grep -c '^## '` → **5** sections each (minimal tier — no 10-section requirement).
- references present: questions (1), research (2) — both ≥ 1.
- agent parity: `find {claude,opencode}/agents -name '*.md'` → **38 / 38** (37 → 38; +1 orchestrator;
  `qraspi-builder` lands in Slice 4 → 39, matching Plan's 37→39).
- command parity: **17 / 17** (15 → 17; +2 command pairs).
- `python3 scripts/add_frontmatter.py` → "0 files updated" (frontmatter complete + well-formed; the
  flat `skills/team/*/` walk reaches both new skills, confirming Plan #1's namespace decision holds).

### Plan-discrepancy flag (Plan §6 Slice 2 running tally)

Plan §6 Slice 2 states "Skill count 88," but Slice 2 adds **two** skills on top of Slice 1's 87, so
the true count is **89**. The plan's per-slice running tally is off by one from Slice 2 onward
(88/89/90/91/92/93) because it under-counted this two-skill slice in the narrative. The deliverable
(both `qraspi-questions` + `qraspi-research`) and the **final target 86 → 94** are unambiguous and
consistent with 89 here. This is a plan-narrative arithmetic slip, not a behavior or convention
deviation — no scope change. Slice 8 bookkeeping should reconcile counts against the filesystem, not
the per-slice tally.

## Deferred (NOT done this slice — by design)

- **Trigger evals** for both skills (Plan §5). Eval-spec checklist below for the harness session.
- **Bookkeeping** (README/AGENTS counts, Skill-Suites table, Persistent-Decisions rows) — all Slice 8
  per the session constraints and Plan §6/§7. **Do not interleave.**
- Extending `qraspi-orchestrator` `skills:` to include `qraspi-architecture` (Slice 3), `qraspi-plan`
  (Slice 5), `qraspi-graduate` (Slice 7). This slice wires only `[qraspi-questions, qraspi-research]`,
  per Plan §6 Slice 2 ("initially").
- Committing `thoughts/qraspi-plan.md` / `qraspi-research.md` — pre-existing untracked planning
  artifacts; left as-is (not part of this slice's atomic commit, same as Slice 1).

### Eval-spec checklist (for the later eval-harness session — Plan §5)

`qraspi-questions` MUST activate on:
- [ ] "new project from scratch"
- [ ] "greenfield X" / "build a new X from scratch"
- [ ] "/qraspi-questions X"

`qraspi-questions` MUST NOT activate on (brownfield negatives — Plan §5):
- [ ] "add a feature to our existing X" → routes to `qrspi-questions`
- [ ] "/qrspi-questions" / "/rpi-questions"

`qraspi-research` MUST activate on:
- [ ] "research the solution landscape for new X"
- [ ] "what libraries / prior art exist for X"
- [ ] "/qraspi-research X"

`qraspi-research` MUST NOT activate on (brownfield negatives):
- [ ] "research our codebase for X" → routes to `qrspi-research`
- [ ] "/qrspi-research" / "/rpi-research"

Canonical disambiguation pair (Plan §5): "build a new MCP server from scratch" → QRASPI;
"add a tool to our existing MCP server" → QRSPI. The discriminator is greenfield (no codebase) vs
brownfield (existing codebase), not shared keywords.

## What the next slice (Slice 3) needs to know

- `qraspi-questions` + `qraspi-research` + the `qraspi-orchestrator` agent pair + both command pairs
  exist and are loadable. Q→R runs standalone in the orchestrator (no Edit).
- **Slice 3 builds `qraspi-architecture`** + references (`adr-template.md` MADR, `c4-conventions.md`
  Mermaid, `fitness-spec.md`) and **extends `qraspi-orchestrator` `skills:`** to add
  `qraspi-architecture`. Architecture consumes `research.md` and is where the **picks happen** — it
  invokes the Slice-1 `fitness-functions` primitive for its required-fitness-functions exit gate, and
  applies the MADR-with-alternatives + `adrs_aligned` brain-surgery gate (Plan §4.3). The
  no-premature-solution firewall this slice installed in Research is the upstream half of that gate:
  Research surfaces "options on the table," Architecture chooses among them behind ADRs.
- State-tag convention extended: `<qraspi-questions-state>`, `<qraspi-research-state>`,
  `<qraspi-orchestrator-state>` (with `research_mode` + `recommendations_made`). Slice 3 adds
  `<qraspi-architecture-state>`.
- `research.md` carries `research_mode` and a `## Options on the table` section — Slice 3's ADR
  authoring reads exactly those options as its alternatives input.
- Branch `qraspi-slice-2-questions-research` committed, **not pushed, no PR** (review locally first).
