# Skeleton output -- `skeleton.md` structure and the recipe-not-rigid principle

The Skeleton phase produces two things: a **runnable repo** (the walking skeleton itself) and a
`skeleton.md` artifact in the project folder that records what stood up and what comes next. The repo
is the deliverable; `skeleton.md` is the index QRASPI Plan reads to grow the next slice.

## Walking skeleton -- the definition that sets the exit gate

A walking skeleton (Cockburn) / tracer bullet (Hunt & Thomas) is a thin end-to-end thread through
**every architectural layer**, doing minimal real work, kept and grown -- not a prototype thrown away.
It is "walking" because it runs end-to-end from day one and "skeleton" because it has minimal flesh.
This is *why* the exit gate is a real CI run: a skeleton that does not execute is not a skeleton, it
is a wish. The phase carries the build/test/deploy harness, not features.

## Recipe, not rigid repo

The `references/archetypes/<archetype>.md` files are **instructions you adapt to the accepted ADRs**,
never copy-paste templates. Over-constraining the scaffold (a fixed repo you must reproduce verbatim)
re-introduces the magic-words / over-fit trap QRASPI exists to remove. Read the ADR stack declaration,
pick the matching archetype recipe, and generate a repo that honors *those* decisions. If no archetype
matches, fall back to the generic recipe below.

## Two-layer composition

1. **Repo layer (archetype recipe):** project layout, CI workflow, health check, observability hook,
   secure-by-default config. This is the gap the `*-feature-slice` scaffolders do NOT fill -- they
   scaffold a feature, not a full repo + CI + observability.
2. **Slice layer (feature-slice scaffolder):** invoke `dotnet-vertical-slice` / `python-feature-slice`
   / `rust-feature-slice` for the ONE vertical slice the skeleton walks
   end-to-end. One slice only -- breadth is later QRASPI Plan increments.

## Generic recipe (no archetype match)

1. Read the ADR stack declaration; name the layers the slice must walk (e.g. entrypoint -> handler
   -> domain -> persistence/external -> response).
2. Scaffold the minimal repo: package manifest, source layout, one health/smoke entrypoint, a CI
   workflow file (`.github/workflows/ci.yml` or the target's convention).
3. Walk one slice end-to-end doing minimal real work.
4. Wire every fitness function from `architecture.md` via the `fitness-functions` skill.
5. Run CI; require exit 0.

## `skeleton.md` structure

```markdown
---
date: YYYY-MM-DD
project: <slug>
phase: Skeleton (S)
status: complete
archetype: <archetype | generic>
ci_green: true
---

# Skeleton -- <project>

## Archetype & stack
<which archetype recipe, and the ADR-declared stack it instantiates>

## What the walking skeleton instantiates
- Layers walked end-to-end: <entrypoint -> ... -> response>
- The one walking slice: <name + the real-but-minimal function it performs>
- Health check / observability hook: <where>
- Secure-by-default config: <what>

## CI status
- Command run: `<exact CI/test command>`  ->  exit 0 (green)
- Build · unit · lint · fitness gates: all green
- Hardware manual gate (if any): <documented device-deploy step, not auto-run>

## Fitness gates landed
| Gate | Enforces ADR | CI step |
|------|--------------|---------|
| <FF-1> | <ADR id> | <job/step> |

## Slice backlog (for /qraspi-plan)
1. <next vertical slice -- the first real feature increment>
2. <...>
> Each backlog item is one vertical slice. /qraspi-plan plans the next unbuilt one;
> /qraspi-implement grows it with Red-Green-Refactor on top of this skeleton.

## Graduation note
V0 walking skeleton is green. Real features now grow via QRASPI Plan/Implement on this repo;
once V1 ships, /qraspi-graduate hands the repo to QRSPI for ongoing feature work.
```

## Authoring rules

- **CI green is a command result.** Paste the exit status. "It should pass" is not an exit gate.
- **One slice, every layer.** The walking slice must touch each layer the ADRs name -- depth over
  breadth. A slice that skips a layer is not a *walking* skeleton.
- **Enumerate the backlog.** `/qraspi-plan` needs the slice backlog to exist; an empty backlog means
  Plan has nothing to plan. List the real feature increments the skeleton will grow into.
- **Hand the gates off, don't re-derive them.** The `fitness-functions` skill owns the per-stack
  tooling; this phase tells it what to wire (from `architecture.md`) and confirms it gates CI.
