---
name: substack-writer
description: >-
  Structured multi-pass pipeline for turning raw technical notes into
  publication-quality Substack/blog posts for a professional software-engineering
  portfolio. Use whenever the user wants to draft, outline, revise, or polish a
  Substack post, technical blog article, or portfolio writing piece — especially
  anything about AI-augmented development, edge AI, RAG, .NET/C#, Python, Rust,
  APIs, or industrial automation. Trigger even if they just say "help me write a
  post about X" or paste raw notes to turn into an article. Keeps the human as the
  source of technical substance and applies editorial craft rather than generating
  generic filler.
---

# Substack Writer

A repeatable editorial pipeline for professional portfolio writing. The purpose of
this skill is **not** to generate posts from a topic string — that produces generic,
AI-flavored filler that damages a technical portfolio. The purpose is to take the
author's real technical substance and shape it into a tight, credible, well-crafted
post through a disciplined multi-pass process, with human gates at the points that
matter.

## Core principle: the human owns the substance

The model does not invent technical claims, benchmarks, war stories, or opinions.
Those come from the author. If a draft needs a fact, a number, or a concrete
example that the author has not supplied, **stop and ask** — do not fabricate it.
Fabricated specifics are the fastest way to destroy the credibility a portfolio
exists to build. The model's job is structure, flow, compression, and craft applied
to material the author provides.

## Reference files — read these before drafting

- `references/craft-principles.md` — the distilled writing craft. Load this before
  the outline stage and consult it explicitly during the critique stage. It is the
  editorial standard the draft is measured against.
- `references/voice.md` — the author's voice profile (do/don't rules + samples).
  Load this before the voice pass. If it is still a template with unfilled
  placeholders, ask the author for 2–3 existing posts and populate it first — the
  voice pass is worthless against an empty profile.

## The pipeline

Run these stages in order. Do not collapse them into one shot; the quality comes
from the passes being separate. Announce which stage you are entering so the author
can follow along.

### 1. Capture (human-led)

Collect the raw substance from the author: notes, the actual insight or lesson, code
snippets, the specific problem that motivated the post, any numbers or results. Ask
targeted questions to fill gaps — *what surprised you, what did you try that failed,
what would you tell a peer about this.* Do not proceed until there is enough real
material to write from. This is the stage that separates a portfolio post from a
content-mill post.

### 2. Outline (human gate)

Propose a structure: a working title, the hook angle, 3–6 section headers, and a
one-line note on what each section does. Order for the reader, not for chronology —
lead with the payoff or the tension, not the setup. **Present the outline and wait
for approval or edits before drafting.** Reordering at the outline stage costs
seconds; reordering a full draft costs an afternoon.

### 3. Draft

Write the post section by section from the approved outline and the captured
material. Prose only — no invented facts, no filler transitions, no throat-clearing
intros. Keep it slightly long here; compression happens next. Route this stage to
the local draft model (see Model routing).

### 4. Critique (against the standard)

Re-read the draft *against* `references/craft-principles.md` and produce an explicit
critique — not a rewrite yet. Flag, by location:
- weak or buried hook (is the payoff in the first two sentences?)
- hedging, throat-clearing, and filler ("in this post I will…", "it's worth noting")
- abstract claims that need a concrete example or number
- paragraphs doing more than one job
- a conclusion that restates instead of landing

This self-critique pass is where most of the quality is created. Treat it as the
editorial gate a good draft has to survive.

### 5. Revise

Apply the critique. Cut hard — deleting a good sentence that doesn't earn its place
improves the post. Tighten sentences, front-load paragraphs, replace abstractions
with the concrete material from stage 1.

### 6. Voice pass

Rewrite through `references/voice.md`. This is the pass that makes it read as the
author rather than as a model: their cadence, their vocabulary, their do/don't
rules. Apply the don't-list aggressively — killing model-default tics (marketing
gloss, "fast-paced world", em-dash overuse, LinkedIn voice) does most of the work.
This is the stage to consider escalating to the larger local model for a final
polish (see Model routing).

### 7. Handoff (human owns the last mile)

Deliver the post as a clean markdown file plus a short changelog of the significant
editorial decisions (what was cut and why, where a claim still needs the author's
verification). The author always does the final edit and owns publication. Flag any
remaining spots where a specific fact or number is still the author's to confirm.

## Model routing

Follow local-first discipline; escalate deliberately, not by default.

- **Draft + critique + revise (stages 3–5):** the local ~32B general model via the
  Mac Mini Ollama host (`http://michaels-mac-mini.cosmach.net:11434`). Fast
  iteration matters more than peak quality here, and these stages are structural.
- **Voice pass / final polish (stage 6):** optionally escalate to the larger local
  model (Llama 3.3 70B Q4) for a single pass when the post is worth it — it holds
  voice more consistently. Named trigger, not the default; ~40GB at Q4 is tight on
  48GB and runs at ~8–15 tok/s, so reserve it for the finish, not the draft loop.
- **Cloud escalation:** only on the standard named triggers (a genuinely
  architecture/strategy-critical framing decision, or two real local attempts
  failed). Drafting prose is not a cloud task.

Sampling for prose lives at temperature ~0.85–0.95 / top-p ~0.9. Below 0.7 the prose
goes flat; the tuned Modelfile in `assets/` bakes this in.

## Anti-patterns (reject these in your own output)

- Generating a full post from just a topic with no captured substance.
- Inventing benchmarks, quotes, dates, or "studies show" claims.
- Skipping the outline gate and drafting straight through.
- Merging critique and revision — the critique has to be explicit and separate to be
  useful.
- Shipping without running the voice pass, leaving the post in model-default voice.
