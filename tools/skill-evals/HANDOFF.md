# skill-evals — session handoff

**Written:** 2026-08-02 · **HEAD at handoff:** `9ab9590` · **Branch:** `main` · **Tree:** clean

This file exists to let a fresh session finish the outstanding work without re-deriving the
design. Delete it once the open items are closed.

---

## What exists now

`tools/skill-evals/` — an executable eval harness for the `skills/` corpus, in four layers.
It implements `evals.md`, which until now was a specification nobody could run.

| Layer | Command | Model? | State |
|---|---|---|---|
| L1 lint | `skill-evals lint` | no | **Done.** 39 rules, gate passes |
| L2 routing | `skill-evals route` | yes | **Done.** Baseline committed |
| L3 quality | `skill-evals quality` | yes | **Done.** 12 cases, smoke-tested on 2 |
| L4 scorecard | `skill-evals scorecard` | yes | **Built and unit-tested; no corpus baseline yet** |

399 tests, 91% coverage. `ruff`, `mypy`, `bandit` clean (bandit's 3 Low findings are the
`git diff` subprocess in `scorecard_run.py`, which validates its ref against `_GIT_REF`).

### Eight commits landed

```
9ab9590 docs: make evals.md executable and record the skill-evals decision
bc2584d fix(docs): correct skill counts and Pi triage tallies
77a394a fix(skills,agents): give every state block a distinct owner
93b9137 fix(skills): complete the tdd -> tdd-loop rename
69819b4 feat(tools): add skill-evals, an executable eval harness for skills/
fa7559f refactor(ollama-evals): widen reuse seams for external scorers
1a5dfd6 fix(ollama-evals): distinguish a judge parse failure from a genuine zero
f9bf035 feat(ollama-evals): support per-case system prompts and record prompt identity
```

**Nothing is pushed.** `git push` has not been run and was not authorised.

---

## Open items, in priority order

### 1. Produce an L4 scorecard baseline — and measure its variance first

This is the only layer without corpus-wide evidence. **Do not treat `scorecard --gate` as a
gate until the variance is known** — an uncalibrated judge is worse than none, and the README
says so in print.

```bash
cd tools/skill-evals
export OLLAMA_BASE_URL=http://ollama-host.local:11434/v1

# a) variance: same 3 skills, three times, compare per-dimension scores
for i in 1 2 3; do
  uv run skill-evals scorecard --models gpt-oss:20b --judge-model gpt-oss:20b \
    --only cargo-package-scaffold --only tdd-loop --only para-file --out runs
done
# then diff the three runs/*.run.json on metadata.raw_score per (case_id, category)

# b) the full sweep, once variance is acceptable. ~2.5 min/skill => ~4 hours for 94.
uv run skill-evals scorecard --models gpt-oss:20b --judge-model gpt-oss:20b --samples 3 --out runs
cp runs/<id>.run.json baselines/scorecard-<date>.run.json
```

For (a), `cd ../ollama-evals && uv run ollama-evals report ../skill-evals/runs/<id>.run.json`
renders each run as a per-dimension table — see item 5. Comparing those three tables is the
variance measurement.

Publish the per-dimension variance in `README.md` under the L4 section (there is a paragraph
telling you to; replace it with the numbers).

**A 15-skill sweep was left running when this session ended** (started 10:48, 50-minute
timeout). If it completed, its artifact is the newest file in `tools/skill-evals/runs/` —
check timestamps before starting a fresh run. Its stdout went to a scratchpad that is gone;
only the artifact survives.

### 2. Decide the 8 baselined lint findings

`skill-evals lint` (no `--baseline`) reports 8 errors. All are content decisions deferred to
you, with rationale in `baselines/known-defects.yaml`:

| Rule | Skills | The decision |
|---|---|---|
| SK021 + SK030 | `evaluate-tests`, `substack-writer` | They never adopted the 5-section lean layout (163 and 134 lines, bespoke headings, no state block). Convert them, or record an explicit exemption. |
| SK041 | `qraspi-graduate` (102), `qrspi-research` (102), `qraspi-implement` (107), `qraspi-plan` (110) | Declared minimal-tier by the 2026-06-02 decision (≤100 lines, ≥1 reference) but 2–10 lines over. Trim under 100, or accept as full-tier and add a second reference file. |

Raising the minimal ceiling to fit is moving the goalposts — say so if you're tempted.

Once resolved, delete the entry from `baselines/known-defects.yaml` and drop `--baseline`
from the documented gate.

### 3. Close the lean-layout gap (or amend the claim)

`CLAUDE.md`'s 2026-06-26 Persistent Decision records the lean-layout migration as complete.
It was verified on **line count only**. 125 non-canonical `##` sections remain:

```bash
uv run skill-evals lint --rule SK023 --format json
```

Top offenders: `AI Discipline Rules` (29), `Error Recovery` (15), `Knowledge Base Lookups`
(12), `Domain Principles` (8), `Anti-Patterns` (8) — the exact sections the 2026-06-03
decision said must move to `references/`. These are warnings, so they don't gate.

`tests/test_real_corpus.py::test_lean_layout_migration_is_incomplete_on_sections` asserts
SK023 still fires. **That test is designed to fail once you finish the migration** — its
message tells you to update the decision and delete it.

### 4. Improve abstention (the L2 finding worth acting on)

Routing measured **45/45 on positive cases but 8/15 on abstain cases**. The corpus
discriminates beautifully and abstains poorly. Every miss was a skill firing where none
should:

| Over-triggering skill | Fired on |
|---|---|
| `architecture-review` ×3 | "here's my plan, tell me what you think" / "ask me hard questions" |
| `grilling` ×2 | "interview me about this plan" / "help me think this through" |
| `session-context` | "what did I commit yesterday?" |
| `doc-sync` | "there's a typo in this README, fix it" |

Tightening those four descriptions' negative-boundary clauses is the highest-leverage change
available. Re-run `skill-evals route` after; the baseline to beat is in
`baselines/routing-2026-08-02.run.json`.

### 5. Optional: add `skill-evals compare` / `report` wrappers

The plan specified these; they were never built. **The capability is not missing** — run
artifacts share ollama-evals' format exactly, so its commands read them today, including the
per-dimension rubric categories:

```bash
cd tools/ollama-evals
uv run ollama-evals compare ../skill-evals/baselines/routing-2026-08-02.run.json \
                            ../skill-evals/runs/<new>.run.json      # exits 1 on regression
uv run ollama-evals report  ../skill-evals/runs/<scorecard>.run.json
# -> | Model | rubric-d1 | rubric-d2 | ... | Overall |
```

That is the reuse paying off, and it is how you compare a scorecard baseline in item 1. Thin
`skill-evals` wrappers would only save the `cd` and the relative path. Worth doing for
ergonomics, not for capability.

### 6. Push

Eight commits sit on local `main`. Not pushed, not authorised.

---

## Running it

```bash
cd tools/skill-evals

# L1 — no model needed, this is the daily driver
uv run skill-evals lint --baseline baselines/known-defects.yaml   # exits 0 today
uv run skill-evals lint                                            # exits 1, shows the backlog
uv run skill-evals list-rules

# LLM layers — need the LAN box
export OLLAMA_BASE_URL=http://ollama-host.local:11434/v1
uv run skill-evals list-models                                     # connectivity check first
uv run skill-evals route --models qwen3-coder-30b-agent:latest --confusion
uv run skill-evals quality --models gpt-oss:20b --judge-model gpt-oss:20b --skill tdd-loop
uv run skill-evals scorecard --models gpt-oss:20b --judge-model gpt-oss:20b --only <skill>

# tests
uv run --extra dev --extra llm pytest              # 399, hermetic
uv run --extra dev --extra llm pytest -m corpus    # acceptance against the real skills/ tree
```

**Exit codes** are uniform: `0` clean · `1` gate failure · `2` usage/environment · `3` the
judge is unusable. The last one exists so "the model is broken" never reads as "the skills
are bad" — preserve that distinction in anything you add.

---

## Things that will bite you

**The judge model must exist on the box.** `models.yaml` ships `qwen2.5:14b` as a public
default; it is not pulled on the LAN box. Always pass `--judge-model`, or put a real one in
`models.local.yaml` (gitignored). A wrong name now exits 2 with a clear message rather than a
traceback — that was a real fix, don't regress it.

**Don't let a rule become a grep.** `tests/test_real_corpus.py` has a *negative* test:
SK005 must report `confluence-guide-writer` and `jira-comment-writer` as **clean**. Both carry
`audience: team` in frontmatter and a free-form `audience:` line inside their state block,
where it is a legitimate field. A grep-based implementation flags them; the test fails if
anyone rewrites SK005 that way.

**Tier is decided by size, not section count.** The QRSPI/QRASPI phase drivers carry all five
sections but are minimal-tier by decision. An earlier version of `tier.py` promoted them on
section count and produced 8 false SK041 errors. `tests/test_tier.py` pins this.

**`REQ-XXX` is an ID format, not a TODO.** SK027's patterns use `(?<![\w-])XXX(?![\w-])` for
exactly this reason — `capture-consolidate` teaches `REQ-XXX` and `DRAFT-NNN` as ID formats.

**An unregistered scorer used to look like total failure.** The ollama-evals runner records a
per-case exception as score 0.0, so a typo'd scorer type reads as "the model got everything
wrong". `routing_run._require_scorers` pre-flights this. Keep that guard if you add a suite.

**Fixture bodies must clear 100 lines to be FULL tier.** `conftest.CANONICAL_BODY` is padded
for this. A fixture that quietly classifies MINIMAL exempts itself from the very rules it
exists to exercise.

---

## Design decisions — settled, don't re-litigate

| Decision | Why |
|---|---|
| L1 has **no** LLM dependency | It's the layer run daily; `ollama-evals` is an optional `[llm]` extra behind `_ollama.py`, the single import shim |
| State tags: unique **across** families, shareable **within** a declared one | Taking the old rule literally fails 14 skills whose sharing is deliberate. Families live in `baselines/state-tag-families.yaml` **with a rationale** — that field is the point |
| Rubric is parsed at **run time**, sha256 in the manifest | `scoring-rubric.md` stays the single source of truth; editing it visibly invalidates a baseline |
| **One judge call per dimension**, not per skill | A single 10-score call anchors on one impression; per-dimension isolates parse failures and makes each dimension independently comparable |
| Parse failure **omits** a dimension, never scores it 0 | A broken judge must not read as a bad skill |
| L2 roster **withholds** `disable-model-invocation` skills | That's what the harness does; including them measures a scenario that cannot occur |
| Structural sub-score reported **beside** the judged score, never averaged in | Measured facts and opinions do not mix |
| Confusion pairs chosen by **description similarity**, not taste | `roster.candidate_pairs()` ranks all C(94,2); which pairs to test is a measurement |
| Baseline is a **decision log**, not a mute button | Every entry carries a written reason. Taste Rule 10 in `evals.md` forbids lowering a severity to silence a finding |

---

## Where things live

```
tools/skill-evals/
├── src/skill_evals/
│   ├── corpus.py tier.py findings.py     # the model: parse, classify, report
│   ├── rules/{frontmatter,structure,state,references,crossref}.py
│   ├── lint.py                           # orchestration + evidence_for() (reused by L4)
│   ├── roster.py route.py routing_run.py # L2
│   ├── quality.py quality_run.py         # L3
│   ├── rubric.py scorecard.py scorecard_run.py  # L4
│   ├── scorers/{route_choice,skill_rubric}.py   # registered into ollama-evals' registry
│   ├── _ollama.py                        # the ONLY module importing ollama_evals
│   └── evalsmd.py                        # fills evals.md's Last Run / Result fields
├── baselines/    # state-tag-families, known-non-skills, known-defects, routing baseline
├── datasets/     # routing.jsonl (60), quality.jsonl (12)
└── tests/        # conftest builds synthetic skills; test_real_corpus.py pins real defects
```

Related, outside the tool: `evals.md` (the spec this implements, now with TC9/TC10 and a
corrected gate section), `constraints.md` (state-tag amendment), and the
`CLAUDE.md`/`AGENTS.md` mirror pair (Key Files row + a Persistent Decisions entry). Those two
must stay byte-identical — `SK059` checks it.
