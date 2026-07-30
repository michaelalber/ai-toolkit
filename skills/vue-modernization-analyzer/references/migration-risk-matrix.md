# Migration risk matrix — Vue paths

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
| Vue CLI → Vite | M | Low–Med | custom `vue.config.js` webpack, env var rename, SVG/asset loaders |
| Introduce TypeScript (per-file `lang="ts"`) | M | Low | none; gradual |
| Finish JS → TS + `strict` | L–XL | Med | volume; `any` debt |
| Vue Test Utils v1 → Vitest + Vue Testing Library | L | Med | implementation-coupled tests (`.vm`, `.find('.cls')`); **mount API differs for Vue 3** |
| Vue 2 → Vue 3 | M–L | Med–High | removed filters, `$listeners`, global `Vue.use`; lib compat; Options API global mixins |
| Options → Composition API | XL | Med–High | low coverage; complex `watch`/`computed` graphs; `this`-bound patterns |
| Vuex → Pinia | L | Med | mapState/mapActions helpers, module namespacing assumptions |
| Ad-hoc fetch → query layer | L | Med | request waterfalls, manual cache code to retire |

## Risk multipliers

Raise the risk one level for each that applies:

- Test coverage < 40% on the affected surface
- A dependency has no Vue 3 build and no maintained alternative
- The path touches authentication/session handling
- No CI runs typecheck + tests on PRs
- The change cannot be feature-flagged or rolled back independently

## Recommended ordering heuristic

1. **Prerequisites** (tests, CI) — unblock everything, lower every later risk.
2. **Tooling** (Vue CLI→Vite, introduce TS) — faster feedback de-risks the rest.
3. **Test framework** (Vue Test Utils v1→Vitest + Vue Testing Library) — required before Vue 3.
4. **Version** (2→3) — one major, fully.
5. **Components** (Options→Composition) — slice by slice, highest volume.
6. **State & data** (Vuex→Pinia, fetch→query layer) — per module.
7. **Types** (finish JS→TS, enable strict) — last sweep.

Never combine 4, 5, and the JS→TS sweep in one change set — isolate each so a regression has one cause.

## Report this per path

```
Path: Vue 2 → 3
Evidence: vue@2.6.14; 60 Vue Test Utils v1 test files; lib "x" has no Vue 3 build
Effort: L   Risk: Med (raised to High by 18% coverage)
Blockers: Vue Test Utils v1 (migrate mount API first); lib "x" (upgrade to a Vue-3-compatible version)
Recommended order: 4 (after test-tooling migration)
```
