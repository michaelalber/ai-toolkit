# Output Templates

## Modernization Assessment Summary

```markdown
## Vue Modernization Assessment: [Application Name]

**Date:** YYYY-MM-DD
**Vue Version:** [current]
**Bundler:** [Vue CLI / Vite / custom webpack / Nuxt]
**Language:** [JS / mixed / TS]   **Codebase Size:** [components, LOC]
**Test Coverage:** [%]   **Test Framework:** [Vue Test Utils v1 / Vitest+VTL / none]

### Migration Paths Identified

| Path | Effort | Risk | Blockers | Recommended Order |
|------|--------|------|---------|------------------|
| Vue CLI → Vite | M | Low | [custom vue.config.js webpack] | 1 |
| Introduce TypeScript (per-file) | M | Low | None | 2 |
| Vue Test Utils v1 → Vitest + VTL | L | Med | None | 3 (before Vue 3) |
| Vue 2 → 3 | M-L | Med | [lib X no Vue 3 build] | 4 |
| Options → Composition API | XL | Med | [low test coverage] | 5 |
| Vuex → Pinia | L | Med | None | 6 |

### Blockers

| Blocker | Affected Path | Resolution |
|---------|--------------|-----------|
| Vue Test Utils v1 (mount API differs on Vue 3) | Vue 2 → 3 | Migrate tests to Vitest + Vue Testing Library first |
| [UI lib] — no Vue 3 build | Vue 2 → 3 | Upgrade/replace before the bump |

### Recommended Phased Plan

**Phase 0 (Prerequisites — 1–2 weeks):**
- [ ] Add component characterization tests on critical flows (≥ 60% on hot paths)
- [ ] Ensure CI runs typecheck + tests

**Phase 1 (Tooling — 1 week):**
- [ ] Vue CLI → Vite; map VUE_APP_* → VITE_*
- [ ] Add TypeScript per-file; type new files going forward

[Continue for each phase...]
```
