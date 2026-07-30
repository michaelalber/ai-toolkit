# Research mode: landscape vs codebase

QRASPI Research runs in one of two modes. The skill detects the mode at PRE-FLIGHT and records it
in `research_mode`. The mechanism (produce a factual map, recommend nothing) is identical; the
**evidence source** differs.

## Detection

```
Is there a populated source tree at the target project (real code, not just thoughts/)?
   NO  -> external-domain   (default; pure greenfield -- nothing to Glob/Grep)
   YES -> inherited-repo    (greenfield component growing inside an existing repo)
```

When ambiguous, default to **external-domain** and note the assumption in `research.md`.

## external-domain (default)

Pure greenfield: there is no codebase, so the codebase-oriented `research-*` subagents do **not**
apply -- there is nothing for them to Glob or Grep. Map the **problem domain and solution
landscape** instead.

- **Engine:** invoke `research-synthesis` for source-credibility scoring and cross-referencing;
  gather with `WebSearch` / `WebFetch`.
- **Output:** a factual landscape -- libraries, frameworks, prior art, established patterns, and
  hard constraints -- each with a source and a credibility note.
- **Firewall:** the danger is a *premature solution*. Catalog options; never rank or pick one.
  Every "X beats Y" becomes an open question for Architecture. `recommendations_made` stays false.

## inherited-repo

A new component (V0/V1) is being grown inside a repo that already exists -- so the host repo's
conventions, hooks, and layout constrain the new system and must be mapped first. This is the
QRSPI mechanic applied to a greenfield component.

- **Engine:** derive a NEUTRAL topic string (areas/component names only, never the project goal);
  spawn `research-file-locator`, `research-code-analyzer`, and `research-pattern-finder` in
  PARALLEL via the Task tool, passing ONLY that string; wait for all three.
- **Output:** the host repo's conventions, integration seams, and constraints the new component
  must respect -- each cited `file:line`.
- **Firewall:** ticket-hidden (the project goal never reaches the subagents) AND
  no-premature-solution (still no stack pick). Both `recommendations_made` and the implicit
  ticket-leak stay false.

## Why the modes never recommend

In both modes, `research.md` is the *factual ground* the Architecture phase stands on. If Research
picks the stack, the ADRs become fait-accompli rationalizations instead of genuine
alternatives-weighed decisions -- the exact failure QRASPI's Architecture gate (`adrs_aligned`,
MADR-with-alternatives) exists to prevent. Keep the pick in Architecture, where the human aligns on
it before it locks.
