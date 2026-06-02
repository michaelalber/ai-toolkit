---
date: 2026-06-02
repository: ai-toolkit
topic: "QRASPI Slice 1 — fitness-functions primitive (RPI Implement phase)"
plan: thoughts/qraspi-plan.md
slice: 1
branch: qraspi-slice-1-fitness-functions
status: complete
---

# QRASPI Slice 1 — `fitness-functions` primitive

Implements Plan §6 Slice 1 (the `#3` Option-A decision: extract `fitness-functions` as the one new
primitive). First new primitive since the AGENTS.md:89 "QRSPI vendored 0 new primitives" decision —
Slice 8 must log that exception (see Deferred, below).

## What was done

| File | Lines | Purpose |
|------|-------|---------|
| `skills/team/fitness-functions/SKILL.md` | 100 | Minimal-tier primitive; authors CI-gate fitness functions and proves they gate |
| `skills/team/fitness-functions/references/dotnet.md` | 60 | NetArchTest layer rule + `dotnet test` CI gate + violation proof |
| `skills/team/fitness-functions/references/python.md` | 51 | import-linter layered contract + `lint-imports` CI gate + violation proof |
| `skills/team/fitness-functions/references/rust.md` | 71 | cargo-deny policy + `cargo metadata` dependency-direction test + violation proof |
| `skills/team/fitness-functions/references/policy.md` | 52 | Conftest/OPA Rego policy gate over config + violation proof |

### Convention conformance (per session constraints)

- **Prose voice + frontmatter** match the landed `qrspi-*` minimal-tier skills exactly: block-scalar
  `description` with positive triggers + negative `Do NOT use ... that is X` clauses, the verbatim
  40%/60% **CONTEXT BUDGET** constraint as the last Non-Negotiable, the
  `Core Philosophy → Workflow (PRE-FLIGHT→steps→Exit criteria) → State Block → Output Template →
  Integration` shape, and a unique state tag `<fitness-functions-state>`.
- **Reused primitives referenced, not duplicated:** `dependency-mapper` (ready-made coupling fitness
  function, Martin Ca/Ce/I/A/D) and `tdd` (distinguished: tdd gates *behavior*, fitness functions
  gate *architecture*) appear in the Integration table as references only. No primitive content was
  copied.
- **Cross-workflow, not QRASPI-only:** unlike the phase skills, `fitness-functions` deliberately
  carries **no** "Do NOT use for QRSPI" negative trigger — it serves QRSPI brownfield features too
  (Plan #3 two-caller + cross-workflow-reuse rationale). Disambiguation is vs `tdd` and
  `dependency-mapper`, per Plan §5.
- **Matt Pocock attribution:** N/A — original work, nothing vendored (`.matt-pocock-attribution.yml`
  unchanged, per Plan §7).
- **Template evaluable contract:** each reference ships a working check, a CI-wiring snippet, and a
  mandatory deliberate-violation proof step — the "prove it gates" constraint is the primitive's
  evaluable core.

### Notable deviation handled

- The Plan's Rust reference originally implied the `cargo_metadata` crate's builder `.exec`-style
  call. The repo's PreToolUse security hook pattern-matches that token as Node's `child_process`
  shell-exec and **blocked the write**. Rewrote the example to call `cargo metadata` via
  `std::process::Command::…args([...]).output()` with **static** args (no injection surface) and
  parse with `serde_json`. Equally accurate and idiomatic; passes the hook. This is a hook
  false-positive accommodation, not a content compromise.

## Tests / verification that pass

This slice ships **no executable evals** (Plan §5: trigger evals are authored in a later
eval-harness session, not here). Verification was structural, all green:

- `find skills -name SKILL.md | wc -l` → **87** (86 → 87, matches Plan Slice 1 checkpoint).
- `wc -l skills/team/fitness-functions/SKILL.md` → **100** (≤ 100 minimal-tier budget).
- `ls skills/team/fitness-functions/references/` → 4 files (≥ 1 required).
- `python3 scripts/add_frontmatter.py` → "0 files updated" (frontmatter complete + well-formed).
- `grep -c '^## ' SKILL.md` → 5 sections (minimal tier — no 10-section requirement).

## Deferred (NOT done this slice — by design)

- **Trigger evals** for `fitness-functions` (Plan §5). Eval-spec checklist below for the harness session.
- **Bookkeeping** (README/AGENTS counts, Persistent-Decisions row for the new-primitive exception,
  Skill-Suites table) — all Slice 8 per the session constraints and Plan §6/§7. **Do not interleave.**
- Committing `thoughts/qraspi-plan.md` / `qraspi-research.md` — pre-existing untracked artifacts from
  the planning session; left as-is (not part of this slice's atomic commit).

### Eval-spec checklist (for the later eval-harness session — Plan §5)

`fitness-functions` MUST activate on:
- [ ] "add a fitness function"
- [ ] "wire an arch test as a CI gate"
- [ ] "enforce layering in CI"
- [ ] "fail the build when the dependency rule is violated"

`fitness-functions` MUST NOT activate on:
- [ ] "run the tests" / "run the test suite"  → routes to `tdd`
- [ ] "review the architecture" / "analyze our coupling"  → routes to `dependency-mapper` /
      `architecture-review` (uses dependency-mapper for *insight*, not a CI gate)

Cross-suite negatives required (Plan §5): a `tdd` negative and a `dependency-mapper` negative, since
`fitness-functions` *uses* dependency-mapper and is adjacent to tdd.

## What the next slice (Slice 2) needs to know

- `fitness-functions` exists, is loadable, and is **model-invocable** (no `disable-model-invocation`).
  Slice 3 (`qraspi-architecture`) will invoke it to satisfy its required-fitness-functions exit gate;
  Slice 4 (`qraspi-skeleton`/`qraspi-builder`) will land its output as CI gates. Slice 4's
  `qraspi-builder` agent lists `fitness-functions` in `skills:`.
- Slice 2 builds `qraspi-questions` + `qraspi-research` + the `qraspi-orchestrator` agent pair +
  command pairs. It does **not** touch `fitness-functions`.
- Established the QRASPI minimal-tier skill shape to copy (frontmatter block scalar, 5-part body,
  verbatim context-budget constraint, unique `<…-state>` tag). Phase skills additionally carry the
  `Do NOT use for QRSPI … that routes to qrspi-<phase>` negative trigger (Plan §3) — `fitness-functions`
  intentionally omits it because it is cross-workflow.
- Branch `qraspi-slice-1-fitness-functions` committed, **not pushed, no PR** (review locally first).
