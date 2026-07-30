# Craft Principles

The editorial standard for portfolio posts. This is a distilled checklist, not a
corpus — it exists to be injected into context, not searched. Consult it at the
outline stage and again, explicitly and line-by-line, at the critique stage.

The through-line of everything below: **respect the reader's time and prove you know
the thing.** A technical portfolio post earns credibility by being specific,
compressed, and honest about tradeoffs. It loses credibility the instant it reads
like it could have been written by someone who hadn't done the work.

## The hook (first two sentences)

- Open on the payoff, the tension, or the surprising result — not the setup. The
  reader decides whether to continue in the first two sentences.
- Ban throat-clearing: "In this post I'll…", "We live in a world where…", "As
  developers, we all know…". Delete these on sight; the real first sentence is
  usually the third one.
- A concrete detail beats a general claim as an opener. "The credential wipe took
  three hours to diagnose because Windows caches NuGet auth in two places" beats
  "Authentication issues can be frustrating."
- State the stakes early: why should the reader care, and what will they be able to
  do or understand by the end.

## Structure

- One idea per paragraph. If a paragraph does two jobs, split it.
- Order for the reader, not for the timeline. Lead with the conclusion or the
  tension; supply the backstory only where it's load-bearing.
- Use the inverted pyramid for technical posts: the "what and why it matters" up
  top, the "how" in the middle, the caveats and edge cases toward the end. A reader
  who bails halfway should still have gotten the point.
- Section headers should be informative, not cute. A reader skimming headers should
  get the argument.
- Short posts that fully land beat long posts that pad. Length is not a quality
  signal.

## Sentences

- Prefer short, declarative sentences. Vary length for rhythm, but the default is
  tight.
- Cut hedging: "I think", "sort of", "it seems", "arguably", "in my opinion" — the
  byline already establishes it's your opinion.
- Cut filler connectives: "it's worth noting that", "needless to say", "at the end
  of the day", "when it comes to".
- Active voice and concrete subjects. "EF Core caches the query plan" beats "the
  query plan is cached by the framework."
- Kill adverb-padding. "Very", "really", "quite", "extremely" usually signal a weak
  noun or verb that should be replaced instead.

## Specificity (the credibility engine)

- Replace every abstraction with the concrete thing. Not "improved performance" but
  "cut cold-start from 4.2s to 1.8s". Not "a modern stack" but "".NET 10, EF Core
  10, vertical slice".
- Show the work: the command you ran, the error you hit, the config that fixed it.
  Specifics are what prove you actually did this and let a reader reproduce it.
- One good example is worth three sentences of explanation. Reach for the example.
- Name the tradeoff. Every real engineering decision has one; naming it is what
  separates an experienced voice from a tutorial voice. "FreeMediator over MediatR
  because the license terms changed and the indirection wasn't earning its keep."

## Honesty

- Include what didn't work. The failed approach is often the most useful and most
  credible part of a technical post.
- Don't oversell. No "revolutionary", "game-changing", "the one weird trick".
  Overselling reads as inexperience.
- Scope the claim. "This worked for a read-only reference API on SQL Server" is
  stronger than an unbounded "this is the right way to do APIs."
- Cite when you're standing on someone else's work; link the source. Don't
  paraphrase a spec or a paper as if it's your own finding.

## The ending

- Land, don't restate. A conclusion that summarizes the post is dead weight; the
  reader just read it.
- End on the implication, the next question, or the one thing you'd want the reader
  to take away and use. Earn the closing line.
- If there's a natural call to action (the repo, the follow-up post, the thing to
  try), make it concrete and singular. One ask, not three.

## The don't-list (model-default tics to strip)

These are the tells that a post was written by an LLM in default mode. Strip them:

- Tricolon overload: "It's fast, it's clean, and it's maintainable."
- "In today's fast-paced / ever-evolving / rapidly-changing world of…"
- "Whether you're a beginner or a seasoned pro…"
- "Let's dive in" / "Let's unpack this" / "Buckle up".
- Empty transitions: "That said," "With that in mind," "Now, here's the thing".
- Symmetrical hedged conclusions: "Ultimately, the right choice depends on your
  specific needs and requirements."
- Bolded key-phrase spam mid-paragraph for no structural reason.
- Em-dash overuse as a substitute for sentence structure.

## The critique-stage question set

At stage 4, answer these explicitly for the draft in hand:

1. Is the payoff in the first two sentences? If not, where is it, and can it move up?
2. Which sentences could be deleted with no loss? (Delete them.)
3. Which abstract claim most needs a concrete number or example the author has?
4. Where is the voice model-default rather than the author's? (Flag for stage 6.)
5. Does the ending land or restate?
