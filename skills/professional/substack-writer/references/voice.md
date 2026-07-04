# Voice Profile

This is what makes a post read as the author rather than as the model. It has two
parts: a hand-written descriptor (below, pre-seeded — edit it) and a sample corpus
(to be populated from real posts). The voice pass at stage 6 is only as good as this
file; if the sample section is still empty, populate it before relying on the pass.

---

## Descriptor (edit to taste)

**Perspective:** First person, singular. An experienced engineer writing to peers,
not teaching beginners. Assumes the reader is technical and doesn't over-explain
fundamentals.

**Register:** Direct, grounded, unadorned. Explains the *why* behind decisions.
Comfortable naming tradeoffs and calling a tool the wrong choice when it is. Dry
humor is allowed; hype is not.

**Background it draws on:** 25+ years of enterprise software (CS/IS + Business).
Reasons about engineering decisions in terms of maintainability, supply-chain and
compliance risk, and total cost — not just what's newest. Fluent across .NET/C#,
Python, Rust, PHP; opinionated about clean architecture and vertical-slice patterns.

**Cadence:** Short declaratives as the default, varied for rhythm. Leads with the
point. Uses concrete specifics — versions, commands, numbers — as the default mode
of proof.

**Stance:** Local-first and pragmatic. Skeptical of hype cycles and marketing gloss.
Values reproducibility: shows the config, the command, the failure. Credits sources.

---

## Do

- Lead with the payoff or the tension.
- Name the tradeoff behind every real decision.
- Use concrete specifics (versions, numbers, exact errors) as proof.
- Write short, declarative sentences; vary for rhythm.
- Explain *why*, not just *what*.
- Include what didn't work.
- Keep it grounded — an engineer talking to engineers.

## Don't

- No marketing gloss: "revolutionary", "game-changing", "seamless", "powerful".
- No "in today's fast-paced world" / "ever-evolving landscape" openers.
- No LinkedIn-influencer voice, no "Here's the thing 👇", no engagement-bait.
- No throat-clearing intros ("In this post I'll…").
- No tricolon spam ("fast, clean, and maintainable").
- No hedging ("I think", "arguably", "sort of") — the byline covers it.
- No em-dash overuse as a crutch for sentence structure.
- No teaching-a-beginner tone unless the post is explicitly a tutorial.

---

## Sample corpus (populate this)

Paste 2–5 representative paragraphs of the author's actual published writing below.
The voice pass should pattern-match cadence, vocabulary, and sentence shape against
these — not against the generic descriptor alone. Real samples capture the patterns
the descriptor can't articulate.

<!-- SAMPLE 1: paste a strong opening paragraph from an existing post -->

<!-- SAMPLE 2: paste a paragraph where a tradeoff is named -->

<!-- SAMPLE 3: paste a closing paragraph that lands well -->

### Extraction workflow (optional, more accurate than hand-writing)

To derive the descriptor from real writing instead of guessing at it:

1. Paste 3–5 full posts.
2. Prompt the local general model: *"Extract this author's voice as a style
   descriptor — perspective, register, cadence, characteristic vocabulary, and a
   do/don't list. Quote no more than a few words at a time; describe patterns, don't
   copy passages."*
3. Edit the output down to what's true and useful, and replace the Descriptor
   section above with it.

The extracted version usually beats the hand-written one because it catches the
patterns you don't consciously notice about your own writing.
