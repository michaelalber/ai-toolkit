# Migration risk matrix — React paths

Scoring guidance for the ASSESS phase. Score every identified path on **Effort**, **Risk**, and
**Blocker potential**, then order them. Risk is raised most by low test coverage and dependency
incompatibility.

## Effort scale

| Effort | Meaning | Rough signal |
|--------|---------|--------------|
| S | Hours–1 day | Config-only, few files |
| M | Days | One subsystem; mechanical but broad |
| L | 1–3 weeks | Many files; needs review per file |
| XL | 1+ month | Touches most components; staged over many PRs |

## Risk scale

| Risk | Meaning |
|------|---------|
| Low | Mechanical, reversible, well-tooled, easily tested |
| Med | Behavioral changes possible; needs tests to verify |
| High | User-facing behavior or auth affected; failure is visible |
| Critical | No rollback path, or affects every user with weak test cover |

## Per-path baseline scores

| Path | Typical Effort | Typical Risk | Common Blockers |
|------|----------------|--------------|-----------------|
| `requirements`/deps bump (patch/minor) | S | Low | breaking transitive CVE fixes |
| CRA → Vite | M | Low–Med | ejected webpack, env var rename, SVG/asset loaders |
| Introduce TypeScript (`allowJs`) | M | Low | none; gradual |
| Finish JS → TS + `strict` | L–XL | Med | volume; `any` debt |
| Enzyme → RTL | L | Med | implementation-coupled tests; **hard blocker for React 18** |
| React 17 → 18 | M | Med | Enzyme, lib peer ranges, StrictMode double-invoke surfacing effect bugs |
| React 18 → 19 | M | Med | removed `defaultProps` on functions, `propTypes` removal, string refs |
| Class → function + hooks | XL | Med–High | low coverage; complex lifecycles; `this`-bound patterns |
| Legacy Redux → RTK | L | Med | hand-rolled middleware, normalized-state assumptions |
| Legacy Redux → Zustand/Context | L | Med | global selectors, connect() sprawl |
| Ad-hoc fetch → query cache | L | Med | request waterfalls, manual cache code to retire |

## Risk multipliers

Raise the risk one level for each that applies:

- Test coverage < 40% on the affected surface
- A dependency in the path has no compatible peer range and no maintained alternative
- The path touches authentication/session handling
- No CI runs typecheck + tests on PRs
- The change cannot be feature-flagged or rolled back independently

## Recommended ordering heuristic

1. **Prerequisites** (tests, CI) — unblock everything, lower every later risk.
2. **Tooling** (CRA→Vite, introduce TS) — faster feedback de-risks the rest.
3. **Test framework** (Enzyme→RTL) — required before React 18.
4. **Version** (17→18→19) — one major at a time.
5. **Components** (class→hooks) — slice by slice, highest volume.
6. **State & data** (Redux→RTK, fetch→query cache) — per slice.
7. **Types** (finish JS→TS, enable strict) — last sweep.

Never combine 4, 5, and the JS→TS sweep in one change set — isolate each so a regression has one cause.

## Report this per path

```
Path: React 17 → 18
Evidence: react@17.0.2; 60 Enzyme test files; lib "x" peerDependencies react "^17"
Effort: M   Risk: Med (raised to High by 18% coverage)
Blockers: Enzyme (migrate to RTL first); lib "x" (upgrade to ^4 which adds 18 peer)
Recommended order: 4 (after Enzyme→RTL)
```
