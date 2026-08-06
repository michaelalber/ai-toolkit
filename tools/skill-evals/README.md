# skill-evals

Executable evaluation for the `skills/` corpus. Answers three questions with an exit code
instead of prose:

| Layer | Question | Needs a model? |
|---|---|---|
| **L1 lint** | Are the skills structurally sound? | no |
| **L2 routing** | Does the model pick the *right* skill for a real prompt? | yes |
| **L3 quality** | Does invoking a skill produce good output? | yes |
| **L4 scorecard** | Which skills are weak, on the 10-dimension rubric? | yes |

`evals.md` at the repo root defines the test cases this tool automates. It is the
specification; this is the implementation.

---

## Why L1 exists

The repo's quality system was entirely doc-encoded and never executed. Every `Last Run`
field in `evals.md` was empty, and its "CI gate" was six manual greps — one of which
matched nothing at all because it assumed backticked table rows that `pi/SKILLS-local.md`
does not have. It silently reported every skill as missing.

The defects that survived are the argument for the tool:

- `skills/tdd-agent/SKILL.md:103` points at two `references/` files that live under
  `tdd-loop/` — fallout from the `tdd` → `tdd-loop` rename. The skill still "loads"; the
  model just fetches nothing.
- `pi/SKILLS-local.md` carries three mutually inconsistent count sets.
- 128 non-canonical `##` sections remain in full-template skills — `AI Discipline Rules`,
  `Error Recovery`, `Anti-Patterns`, `Domain Principles` — the exact four the lean-layout
  decision said must move to `references/`.

---

## Install

L1 needs no LLM stack at all — that is deliberate, because it is the layer you run daily.

```bash
cd tools/skill-evals
uv run skill-evals lint
```

The LLM layers pull in `tools/ollama-evals` for its client, judge, scorer registry,
compare gate, and report renderers:

```bash
uv sync --extra llm
```

`[tool.uv.sources]` resolves it as an editable path dependency. With plain pip:

```bash
pip install -e ../ollama-evals && pip install -e '.[llm]'
```

---

## Use

```bash
skill-evals lint                          # the gate — exits 1 on any ERROR
skill-evals lint --format json            # machine-readable, for diffing
skill-evals lint --rule SK042 --rule SK050
skill-evals lint --strict                 # warnings fail too (the ratchet)
skill-evals list-rules
```

### Exit codes

| Code | Meaning |
|---|---|
| 0 | Clean — no ERROR findings, no regression |
| 1 | Gate failure — an ERROR finding, routing below floor, or a scorecard regression |
| 2 | Usage or environment — bad path, unknown rule, unreachable Ollama |
| 3 | Judge unusable — so "the model is broken" never reads as "the skills are bad" |

Warnings never affect the exit code unless `--strict`. That flag is the **ratchet**:
promote a warning class to error once the corpus is clean on it.

---

## The rules

Errors gate; warnings inform. Severity is chosen from what the corpus can actually pass
today — a lint that fails on 43% of skills on day one gets switched off rather than fixed.

| Group | Rules | Covers |
|---|---|---|
| Frontmatter | SK001–SK010 | schema, description length, trigger and boundary clauses |
| Structure | SK020–SK027 | line budget, the 5 canonical sections, epigraph, constraints, placeholders |
| State | SK030–SK033 | block presence, balanced tags, family ownership, agent collisions |
| References | SK040–SK044 | directory presence, count per tier, **pointer resolution**, reachability, stubs |
| Cross-reference | SK050–SK059 | Integration targets, Pi triage coverage and counts, README listings, published counts, agent parity, the CLAUDE.md/AGENTS.md mirror |

`SK050`–`SK059` replace the six manual grep bullets in `evals.md`'s CI Gate. Nothing
hardcodes a corpus size — every count is compared against the tree, so the rules stay
correct as skills are added and removed.

Two scope notes worth knowing before you read the output:

- **SK051** (Integration symmetry) is informational and fires ~100 times. One-directional
  references are the norm here — a scaffolder points at a security review without the
  review pointing back at every scaffolder. `evals.md` TC7 asks for the check, so it
  exists; it is a warning and never gates.
- **SK052** only considers *hyphenated* backticked tokens. A single word would
  prefix-match far too eagerly (a backticked `python` "resembles" `python-feature-slice`),
  burying the real hits. Single-word stale names are still caught by SK050 wherever they
  appear in an Integration table, which is where they do damage.

### Tiers

Which rules apply depends on the tier, decided before any structural rule runs:

- **EXEMPT** — under 20 lines. No sections, no `references/` required. A 19-line skill has
  no depth to relocate, and a filler reference file satisfies the letter of the rule while
  defeating its purpose.
- **MINIMAL** — ≤ 100 lines, ≥ 1 reference file, no prescribed structure.
- **FULL** — ≥ 3 canonical sections, or over 100 lines. ≤ 200 lines, all 5 sections,
  ≥ 2 reference files.

### State-tag families

`constraints.md` says state tags must be unique. Taken literally that fails 14 skills whose
sharing is deliberate: all six `*-security-review` use `<security-review-state>` because
they run *one* workflow over different languages.

The rule is therefore **unique across families, shareable within one**, with every family
declared in `baselines/state-tag-families.yaml` next to a written rationale. Under it the
corpus has exactly one real violation: `<tdd-state>`, shared by `tdd-loop` and `tdd-agent`
— a loop and an operating mode of that loop, not peers.

---

## L2 — routing: does the model pick the right skill?

Builds a roster of every skill's name and description from the live corpus, puts it in front
of the model with a realistic user prompt, and scores the choice.

```bash
skill-evals route --models <model> --floor 0.85 --confusion
```

The roster is rebuilt each run and its sha256 recorded in the manifest, so a description
change visibly invalidates a baseline instead of silently shifting the numbers. Skills with
`disable-model-invocation: true` are **withheld**, because that is what the harness does —
including them would measure a scenario that cannot occur.

60 cases across five strata. Which confusion pairs to test is a measurement, not a matter of
taste: `roster.candidate_pairs()` ranks all C(94,2) pairs by trigram similarity of their
descriptions and the top ones get cases written.

| Stratum | n | What it measures |
|---|---|---|
| Canonical trigger | 20 | The skill fires on its own territory |
| Confusion pair | 15 | React vs Vue, python vs rust vs dotnet, qrspi vs qraspi |
| Negative | 10 | No skill fires on "what's the capital of Peru" |
| Boundary | 10 | A "Do NOT use when" clause routes to the named alternative |
| Non-invocable | 5 | Vague prompts do not drag an unrelated skill in |

Three outcomes stay distinct: a **wrong choice** is a routing failure, an **unparseable
reply** is an endpoint failure counted separately, and a **runner-up hit** earns half credit.
Folding the second into the first would blame your descriptions for a broken server.

### Measured, 2026-08-02 (`qwen3-coder-30b-agent`, 91-skill roster)

| | Result |
|---|---|
| Top-1 accuracy | **0.88** (53/60) |
| Positive cases — a skill *should* fire | **45/45 (100%)** |
| Abstain cases — no skill should fire | **8/15 (53%)** |
| Description collisions ≥ 20% | **none** |
| Parse failures | 0 |

The discrimination is excellent — every confusion pair routed correctly, including all five
React/Vue pairs. **The weakness is abstention**: every single miss was the model firing a
skill on a prompt where none should have. `architecture-review` (×3) and `grilling` (×2) are
the biggest over-triggerers, plus `session-context` on "what did I commit yesterday" and
`doc-sync` on "fix this typo". If you want one number to improve, it is that 53%.

---

## L3 — output quality: is the skill actually followed?

Injects a SKILL.md as the system prompt, gives it a realistic task, and judges the reply
against **that skill's own acceptance criteria**.

```bash
skill-evals quality --skill tdd-loop --models <model>
```

The criteria are what keep this honest. `quality-scaffold` derives them mechanically from the
skill's own Non-Negotiable Constraints, workflow phase names, and state-block fields; you
then edit them into the dataset:

```bash
skill-evals quality-scaffold --skill cargo-package-scaffold --task "Create a crate for crates.io."
```

Without that step an output eval degenerates into asking a model "is this good?", which
measures the judge's mood. One judge call **per criterion**, averaged — so the report tells
you *which* constraint was ignored, not just that the score was 0.58.

Alongside the judged score sits a deterministic `structural` sub-score — did the reply emit
the skill's state tag, name its workflow phases, or invent a `references/` filename? Reported
beside the judged score, never averaged into it. Measured facts and opinions do not mix.

### Measured, 2026-08-02 (`gpt-oss:20b`)

| Case | Score | What it found |
|---|---|---|
| `q-tdd-loop` | 0.58 | Never emitted the `<tdd-state>` block |
| `q-para-file` | 0.69 | Emitted state, but named **none** of its six workflow phases |

Both fall under the 0.7 threshold on a 20B model. That is the point of running at this tier:
`pi/SKILLS-local.md` triages these skills for local inference, and this is the evidence for
that triage. Thresholds are per-case in the dataset — raise them for a frontier model.

---

## L4 — rubric scorecard: which skills are weak?

Scores every skill against `skill-creator/references/scoring-rubric.md`, parsed **at run
time** so the rubric file stays the single source of truth. Its sha256 enters the manifest, so
editing the rubric explicitly invalidates a baseline.

```bash
skill-evals scorecard --models <model> --judge-model <model> --gate
skill-evals scorecard --changed-since HEAD~20        # only what you touched
```

**One judge call per dimension, not per skill.** A single ten-score call anchors all ten on
one impression and separates poorly; per-dimension prompts fit a small context, a parse
failure costs one dimension instead of ten, and each dimension becomes independently
comparable for the regression gate.

Determinism comes in four layers, in increasing order of force:

1. temperature 0, fixed seed
2. a measured **evidence pack** — line count, section list, reference files, tag collisions —
   so the judge never has to count. Asking a local model to count is the single biggest source
   of run-to-run variance.
3. a response contract whose `evidence` field must quote the file verbatim
4. **deterministic overrides** on the mechanical dimensions — over 200 lines caps layout at 2,
   a tag collision outside a declared family forces state uniqueness to 2, no `references/`
   forces hygiene to 1. The computed value wins; the judge's opinion is discarded.

Roughly 3 of 10 dimensions become fully reproducible that way. A dimension that cannot be
parsed is **omitted from the total**, never scored 0 — a broken judge must not read as a bad
skill, which is what exit code 3 is for.

Persistence reuses ollama-evals wholesale: each dimension is a `CaseResult` with
`category="rubric-dN"`, so `compare_runs` works untouched and its existing any-category gate
fires when a single dimension degrades corpus-wide.

**Before trusting this as a gate**, run the first baseline three times and publish the
per-dimension variance — the same discipline `ollama-evals calibrate` already enforces for its
judge. Budget ~2.5 min/skill on a 20B model, so a full 94-skill sweep is ~4 hours; use
`--only` or `--changed-since` day to day.

**Measured (2026-08-02, `gpt-oss:20b`):** 3 skills (`cargo-package-scaffold`, `tdd-loop`,
`para-file`) scored 3 times each, back to back — 30 dimension-cases total. **Range = 0.0 and
stdev = 0.0 on every one.** This is the expected result, not a fluke: with temperature 0 and a
fixed seed, an unchanged skill file produces byte-identical judge prompts run to run, so the
four determinism layers above compound to zero drift. It confirms the mechanism does what it's
built to do — `scorecard --gate` differences reflect real content changes, not judge noise — but
it does **not** measure judge *accuracy* (whether a score is right), only run-to-run
*reproducibility* on unchanged input, and only for three strong, unambiguous full-tier skills.
A skill near a rubric boundary, or a genuinely revised skill, is the harder case and hasn't been
measured; if a future baseline ever shows non-zero variance, treat that as a signal something in
the four-layer determinism chain (e.g. the model's `seed` support) broke, not as normal noise.

---

## Baselines

`baselines/` holds the reviewable exceptions. Each is data, not a code change, so the
decision sits next to its rationale instead of inside a rule.

| File | Purpose |
|---|---|
| `state-tag-families.yaml` | Declared families for SK032 |
| `known-non-skills.yaml` | Backticked names that legitimately aren't skills |
| `known-defects.yaml` | Findings accepted at adoption; anything new still fails |

To snapshot the current state before a cleanup:

```bash
skill-evals write-baseline baselines/known-defects.yaml --note "accepted at adoption"
```

Never silence a finding by lowering its severity. Baseline it with a reason, or fix it.

---

## Development

```bash
uv run --extra dev pytest              # unit suite, hermetic
uv run --extra dev pytest -m corpus    # acceptance tests against the real skills/ tree
uv run --extra dev ruff check .
uv run --extra dev mypy src
uv run --extra dev bandit -c pyproject.toml -r src
```

Two kinds of test, deliberately:

- **Synthetic fixtures** (`tests/conftest.py`) build skill trees in `tmp_path`, one
  deviation per rule. Built rather than checked in, so a rule's red test shows the exact
  deviation instead of hiding it in a file you have to go open.
- **Real-corpus acceptance tests** (`tests/test_real_corpus.py`) pin the known defects by
  rule id and skill name. A linter validated only against synthetic fixtures has never
  been shown to find anything real.

One of those acceptance tests is a **negative**: SK005 must report
`confluence-guide-writer` and `jira-comment-writer` as clean. Both carry `audience: team`
in frontmatter *and* a free-form `audience:` line inside their state block, where it is a
legitimate state field. A grep-based implementation flags them; a frontmatter-parsing one
must not. That test fails if anyone ever rewrites SK005 as a grep.
