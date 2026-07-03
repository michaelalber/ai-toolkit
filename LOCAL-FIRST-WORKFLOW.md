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
2. Three or more files must change *in concert*.
3. Two genuine local attempts failed to converge.
4. An architecture or security-critical decision is on the line.
5. You are spending more time re-prompting than a cloud round-trip would cost.

Make escalation a **deliberate, named act** — a dedicated agent, alias, or flag — so cloud is
never the path of least resistance.

---

## 4. Prompting for small local models

A 30B local model needs a different prompt than a frontier model. Six concrete shifts:

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
5. **Instrument the split.** For the first week, tally "local" or "cloud" per task. If you land
   below 80% local, the fix is almost always §4 (tasks too big), not a weaker model.

---

## The one-sentence version

**Start every task on the local model; escalate to your named cloud agent only when a trigger
fires; and shrink each prompt to one file-scoped slice with an example to imitate** — do that,
and the 80/20 split is the natural equilibrium.
