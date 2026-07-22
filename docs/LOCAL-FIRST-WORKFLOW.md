# Local-First Development Workflow

> Route work to a self-hosted model by default; reach for a larger cloud model only when a
> named trigger fires. This is a methodology for an **80/20 split** — roughly 80% of coding
> work on a local ~30B model, 20% on a frontier cloud model — using local-first agents
> (Pi, OpenCode, Continue, or any Ollama-backed client).

The single most useful reframe:

> **"80% local" is not a tool switch — it is a routing discipline plus a prompting change.**
> Most local-first setups already *default* to the local model. What actually drives the split
> is (a) not reflexively reaching for a big model, and (b) shaping tasks so a 30B model can
> succeed. Get those two right and the ratio takes care of itself.

---

## 1. Why local-first, and why keep a 20%

Local execution buys you cost (near-zero marginal), privacy (nothing leaves your network),
low latency on short tasks, and offline capability. A frontier cloud model still wins decisively
on a specific class of hard problems — so the goal is not *100% local*, it is **local by default
with a deliberate escape hatch**. The 20% is a feature, not a failure.

**The premise to get right.** Don't architect around token prices — per-token API prices have
been falling, not rising. The subsidy sits in *flat-rate* coding subscriptions, and that is the
fragile product: it gets rate-limited, tiered, or converted to metered billing. So the exposure
worth hedging is not cost, it is **dependency** — your daily throughput riding on one vendor's
pricing decision, rate limiter, and deprecation schedule.

The second premise is verifiable and does the real work: **the gap is closing from below.**
Open-weight coders now land within a few points of the best closed models on public coding
benchmarks. Whether the frontier plateaus is unknowable and irrelevant — what matters is that
the *marginal* value of a frontier call on routine work keeps shrinking. That is the arbitrage.

---

## 1a. Route on cost-of-being-wrong, not on "which model is best"

AI is cheap exactly where verification is cheap. A repository method with a passing integration
test is nearly free to validate; a concurrency model in a long-lived server circuit is not — that
failure surfaces in production three weeks later. That asymmetry, not benchmark rank, decides
where tokens go.

|                          | Cheap to verify                   | Expensive to verify                |
| ------------------------ | --------------------------------- | ---------------------------------- |
| **Cheap to be wrong**    | Local, always. Full autonomy.     | Local + the test suite as verifier |
| **Expensive to be wrong**| Local draft → human review        | Frontier, or no AI at all          |

---

## 2. The capability envelope of a ~30B local model

A 30B model at a 32K–65K context window is genuinely strong, but it fails in *predictable* ways.
Route on those failure modes, not on vibes.

| Local handles well (the 80%)                    | Escalate to cloud (the 20%)                          |
| ----------------------------------------------- | ---------------------------------------------------- |
| Bounded, well-specified single tasks            | Long-horizon reasoning across many files             |
| Refactors within one or two files               | Anything needing more context than the window holds  |
| Boilerplate, scaffolding, test writing          | Subtle cross-cutting bugs you cannot localize        |
| "Explain / summarize / what's wrong here"       | Novel architecture decisions with real tradeoffs     |
| One vertical slice at a time (RED→GREEN→REFACTOR) | A task where local has stalled after ~2 honest tries |
| Mechanical edits, format conversions, regex     | Comprehension of a large unfamiliar codebase         |

**Heuristic:** if you cannot state the task in one paragraph and point at the specific files,
it is probably a 20% task.

---

## 3. The routing rule

**Default to local. Escalate only on a named trigger.** Decide task-first, not model-first, and
let the trigger fire.

Escalation triggers — any one is sufficient:

1. Context needed exceeds the local window (you are near the model's ceiling).
2. Two genuine local attempts failed to converge.
3. You are spending more time re-prompting than a cloud round-trip would cost.

**Two amendments that matter more than the triggers themselves:**

- **"3+ files in concert" is not an escalation trigger.** It is a *harness* failure. A modern
  local coder inside a proper agent loop with a repo map handles multi-file edits fine. Fix the
  retrieval and the loop before spending the token.
- **Architecture and security decisions do not escalate to a bigger model — they escalate to
  *you*.** Using a frontier model to settle an authn boundary is the same abdication as using a
  30B; it just sounds more authoritative. Frontier models are for *breadth of options and
  adversarial critique*, never for the decision.

Make escalation a **deliberate, named act** — a dedicated agent, alias, or flag — so cloud is
never the path of least resistance.

---

## 3a. Where AI does not belong (either tier)

Codify these as refusals in your `AGENTS.md` / `constraints.md`, not as vibes. None of them are
fixed by escalating to a better model.

1. **Anything whose acceptance criteria you cannot state.** If you can't write the test, you
   can't grade the output. Highest-value rule on this list — the QRSPI Spec gate *is* the
   AI-eligibility gate.
2. **Cross-cutting architectural change.** Slice boundaries, handler decomposition, aggregate
   design. These compress *your* domain knowledge; an agent produces plausible slices that
   fracture along the wrong seams and bills you six months later.
3. **Security boundaries and CUI handling.** Not because the model is wrong — because you must
   defend the reasoning to a reviewer, and "the model produced it" is not a defense.
4. **Legacy-runtime migration semantics** (e.g. .NET Framework `SynchronizationContext`,
   `ConfigureAwait`, binding redirects). Training data is polluted with a decade of confident,
   wrong answers.
5. **Debugging you have not reproduced yet.** You will get five hypotheses and a patch for each.
   Reproduce first, then bring AI in.
6. **Performance work without a profiler run.** Same failure mode.
7. **Non-determinism in build / CI / release paths**, where a subtly wrong generated script fails
   silently and irreversibly.

The inverse — the highest-yield AI work — is deliberately unglamorous: tests from a written spec,
mechanical refactors under green tests, boilerplate slices from an established pattern, schema
migrations, DTO/mapper plumbing, docs and ADRs from diffs, SBOM and vetting first passes, log and
telemetry analysis, and translation between languages you already review fluently.

---

## 4. Prompting for small local models

**At this point the harness matters more than the model.** A local model failing a task is
usually context starvation, not incapacity — every open-weight model performs markedly better
inside a structured agent loop than in raw chat. Three levers, in order of leverage:

- **Retrieval is the quality multiplier.** A 30B with the right five files beats a 200B with the
  wrong fifty. Call-graph and type-hierarchy edges are what let a small model reason about a
  change *set* rather than a file.
- **Spend context on constraints, not prose.** Your `AGENTS.md` should read like a lint config:
  allowed directories, forbidden patterns, the exact test command, the slice template. Small
  models degrade fast under rambling instructions and do well under machine-checkable ones.
- **TDD is not a nicety here.** The test suite is how a weaker model's output becomes
  *verifiable*, which is what converts it from a liability into 80% of your throughput.

Then, six concrete prompt shifts:

1. **Feed less, more precisely.** Frontier models tolerate "here's the repo, figure it out";
   local models degrade as the window fills. Point at one to three specific files. If a coding
   standard matters, paste the relevant excerpt rather than hoping the model recalls it.
2. **One task per prompt.** Split "add the endpoint, wire validation, write tests, update docs"
   into separate prompts. Local models lose the thread on multi-goal instructions much faster.
3. **Vertical slice, not feature.** One RED→GREEN→REFACTOR turn per prompt keeps each step
   inside the model's competence.
4. **Show the pattern.** Local models imitate better than they infer. Paste an existing
   handler or test as a template: "make this new one match that shape." One example beats three
   paragraphs of description.
5. **Verify harder — assume hallucinated signatures.** Local models invent APIs and method
   names more often. Keep build/lint/test hooks hot and confirm real signatures against source.
6. **Constrain the output shape.** "Return only the diff for `foo.py`, no prose" lands better
   than trusting the model to infer scope.

Before → after, concretely:

- ❌ "Add JWT auth to the API and update the tests."
- ✅ *(turn 1)* "Here is `auth/router.py` and an existing route as a pattern. Add **one** POST
  `/login` route that validates `LoginRequest` and returns a token. Return only the new route."
  → *(turn 2)* the test → *(turn 3)* the next slice.

---

## 5. Cloud escalation and model provenance

A subtle but important point: **local execution neutralizes data-residency and telemetry
concerns**, because nothing leaves your machine — only the model's *training* provenance remains.
Where provenance actually bites is **cloud escalation**, where the request leaves your network.

So make the escalation ladder honor whatever policy you hold:

- Choose local weights on capability and hardware fit; origin matters little when it runs on
  your own hardware.
- Route *cloud* escalation to providers that meet your data-residency, compliance, or
  provenance requirements — that is the point at which the choice has real consequences.

The result: any model that leaves your machine is one you have consciously vetted; everything
else stays local.

---

## 6. Rollout and measuring the split

1. **Confirm the local default.** Set your primary agent's default model to the local provider.
2. **Set the escalation reflex, not just config.** Decide there is exactly one way to reach
   cloud, and that you must name a trigger from §3 before using it.
3. **Provision a named escalation agent** (or alias/flag) pointing at your chosen cloud model —
   so local stays the default and escalation is one deliberate keystroke away.
4. **Keep the escalation triggers visible** — pin the five triggers where you will see them.
5. **Instrument the split — log every escalation with its trigger.** Once a month, read the
   distribution. If "2 failed local tries" dominates, that's a prompt/context problem you can
   fix. If "context ceiling" dominates, that's a retrieval problem. If it's genuinely
   "architecture decision," the discipline is working. Without this the ratio silently drifts to
   50/50, because frontier is more pleasant.
6. **Keep a ~20-task eval set drawn from your own repos** — not a public benchmark. Run it
   against your local model and one frontier model each quarter. It is the only way to know when
   the gap has actually closed enough to drop a tier, and the only defensible way to claim it.
7. **Treat your local tier as the floor, not the ceiling.** Re-benchmark when a new open-weight
   coder lands; memory capacity, not raw FLOPs, is what MoE architectures reward, so that is
   where the next hardware dollar goes.

---

## 7. Portability discipline — the actual hedge

The point is not to avoid frontier models. It is that switching should be a config change, not a
migration.

- **No vendor-proprietary agent format as the source of truth.** Define skills and agents once,
  emit per harness — which is exactly what this repo's Claude Code / OpenCode / Pi parity is for.
- **Everything through an OpenAI-compatible endpoint** (Ollama, LiteLLM, or a thin router). Never
  let a harness hard-bind to a vendor SDK.
- **Prompts, specs, and evals live in git next to the code**, not in a vendor's cloud workspace.
- **Methodology is the portable asset.** On a managed corporate stack you control neither tooling
  nor budget — but QRSPI, spec-gated AI eligibility, and the refusal list above travel with you
  unchanged. The stack stays home; the discipline goes to work.

---

## The one-sentence version

**Start every task on the local model; escalate to your named cloud agent only when a trigger
fires; and shrink each prompt to one file-scoped slice with an example to imitate** — do that,
and the 80/20 split is the natural equilibrium.
