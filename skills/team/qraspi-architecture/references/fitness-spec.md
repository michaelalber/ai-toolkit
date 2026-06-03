# Fitness-Function Spec -- the contract Architecture hands to Skeleton

Architecture **specifies** fitness functions; it does not author or wire them. The contract is a
table in `architecture.md`. The `fitness-functions` primitive (a separate skill) authors the actual
checks and wires them into CI as merge-blocking gates when the walking skeleton stands up (Slice 4 /
`qraspi-skeleton`). Keeping the spec here and the authoring there preserves the edit boundary: the
orchestrator writes the spec (markdown); the builder lands the gate (source).

## Why this is a required output

A fitness function is the executable memory of an ADR: the ADR records *why* a boundary exists; the
fitness function makes crossing it *fail the build* (Ford/Parsons/Kua, *Building Evolutionary
Architectures*). An accepted ADR that names a measurable quality attribute but specifies no fitness
function is an intention with no enforcement -- it will decay silently between reviews. The phase
exit gate therefore requires `fitness_functions_specified > 0`.

## The spec table (goes in `architecture.md`)

```markdown
## Fitness functions (spec)

| # | Quality attribute | Measurable threshold | Candidate tool/stack | Gates ADR |
|---|-------------------|----------------------|----------------------|-----------|
| FF-1 | Layer direction | UI never imports persistence directly | NetArchTest / import-linter | 0002 |
| FF-2 | Test coverage (business logic) | >= 80% line coverage | coverage gate in CI | 0003 |
| FF-3 | Dependency policy | no GPL transitive deps | cargo-deny / Conftest | 0004 |
| FF-4 | API latency (p95) | < 200ms on the skeleton's one slice | k6 smoke gate | 0005 |
```

## What to specify (and what NOT to)

- **Specify:** the quality attribute, a *measurable* threshold (a number or a binary rule), the
  candidate tool/stack, and the ADR id it traces to. One row per measurable decision.
- **Do NOT specify:** the implementation. The `fitness-functions` primitive selects the exact tool
  from `references/<stack>.md` and writes the check. Naming a candidate tool is a hint, not a lock.
- **Coverage:** every accepted ADR whose decision is measurable gets >= 1 row. Qualitative ADRs
  (e.g. "use vertical slice architecture for legibility") may have no measurable threshold -- mark
  them `n/a -- qualitative` in the ADR's `gated_by` and do not invent a metric.

## Authoring rules

- **Measurable or omitted.** "Good performance" is not a fitness function; "p95 < 200ms" is. If you
  cannot state a threshold, it is an open question, not a fitness function.
- **Trace both ways.** Every row names its ADR; every measurable ADR appears in at least one row.
- **Hand off cleanly.** The spec is the contract. Do not author or wire the gate here -- that is
  `fitness-functions` in the Skeleton phase. Reference `dependency-mapper` for coupling metrics
  rather than re-deriving Martin's Ca/Ce/I/A/D.
