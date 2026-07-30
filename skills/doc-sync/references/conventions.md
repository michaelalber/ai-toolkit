# Doc Sync Conventions

Depth behind the Core Philosophy constraints: the principle set, discipline rules, anti-patterns,
and recovery steps. C# tag patterns are in `xml-doc-patterns.md`; staleness heuristics in
`staleness-detection.md`.

## Domain Principles

| # | Principle | Rationale | Violation Signal |
|---|-----------|-----------|------------------|
| 1 | **Code Is Truth** | When docs and code disagree, code wins; update docs to match, never the reverse | Docs describe behavior the code does not exhibit |
| 2 | **Detect Before Generating** | Audit for staleness before writing; you may be duplicating or contradicting existing material | New XML docs added alongside stale existing docs |
| 3 | **Minimal Accurate Over Maximal Stale** | A correct one-line summary beats an incorrect three-paragraph description | Long doc comments describing historical behavior |
| 4 | **Signature-Driven Documentation** | Generate XML docs from the actual signature, not assumptions about intent | Param docs that don't match parameter names; return docs on void methods |
| 5 | **Staleness Has a Half-Life** | Accuracy decays exponentially since last verification; prioritize recently changed code | Six-month-old docs on active code treated as current |
| 6 | **README Is the Front Door** | READMEs are read first and most often; they must reflect current state | Setup steps referencing removed dependencies |
| 7 | **Document the Why, Not the What** | Code shows what happens; docs explain why it matters and what callers must know | Summaries that restate the method name |
| 8 | **Exceptions Are Contract** | Exception docs are part of the public API contract; undocumented exceptions are doc bugs | Methods that throw without doc |
| 9 | **Examples Must Compile** | Examples that don't compile teach the wrong thing | Pseudocode in `<example>`; renamed classes; wrong parameter counts |
| 10 | **Cross-Reference Aggressively** | Related types/members link to each other; isolated docs force readers to search | Missing `<see also>`; overloads not linking to each other |

## Discipline Rules

- **Read before writing.** Always read the full implementation before documenting a member. The
  signature gives types; the implementation gives behavior, edge cases, and exceptions. A doc
  generated from the signature alone is a guess, and guesses become lies.
- **Verify every reference.** Every `<see cref>`, `<paramref>`, `<typeparamref>` must resolve to
  actual code. A broken cref is a broken link in generated API docs. Confirm the target exists
  before writing, verify it resolves after.
- **Do not hallucinate APIs.** If you can't find a member via Grep/Glob, it doesn't exist — don't
  document it. Check the access modifier; when in doubt whether something is public, leave it out.
- **Preserve voice and convention.** Match the project's existing documentation voice exactly
  (formal third person vs. imperative vs. casual). Inconsistent voice erodes trust.
- **Staleness is the default state.** Assume all docs are stale until proven otherwise. First
  instinct is to verify (git history, signature compare, read implementation), not trust.

## Anti-Patterns

**The Parrot Summary** — `/// <summary>Gets the user.</summary>` on `GetUser()`. Adds nothing
beyond the name, so developers learn to ignore all doc comments. *Fix:* summaries answer "why would
I call this?" and "what should I know first?" — e.g. "Retrieves the user by ID from cache, falling
back to the database; returns null if the user does not exist."

**The Stale README** — references `dotnet 6.0` after migrating to `8.0`; setup mentions removed
packages; diagrams show deleted components. Every new member wastes time and loses trust. *Fix:*
run README sync after every significant change; diff dependency lists against manifests and setup
against the actual build.

**The Missing Exception Doc** — a method throws `ArgumentNullException`,
`InvalidOperationException`, `HttpRequestException` but docs mention only the return value; callers
discover exceptions at runtime and catch too broadly or too narrowly. *Fix:* trace every throwing
path; add `<exception cref="T">` for each with its triggering condition; verify caller catch blocks.

## Error Recovery

**Git history unavailable** (can't compare doc vs. code dates):
1. Fall back to file modification timestamps (less reliable)
2. If timestamps are unreliable, do a full signature comparison instead
3. Compare every XML doc param/return against the actual signature
4. Flag the session "timestamp-unavailable" in the report; recommend full git history for audits

**Ambiguous code behavior** (can't determine what a method does):
1. Document what you can verify (signature, parameter types, return type)
2. Add `<remarks>` noting behavior analysis was inconclusive
3. Flag for human review with a TODO; do not guess (a doc with a TODO beats a confident wrong doc)
4. Check whether tests clarify expected behavior

**Conflicting doc sources** (XML, README, wiki disagree):
1. Read the implementation — code is the source of truth
2. Update XML comments first (closest to code), then README (most visible)
3. Flag other sources (wiki, external docs) for manual update; log conflicts in the report
