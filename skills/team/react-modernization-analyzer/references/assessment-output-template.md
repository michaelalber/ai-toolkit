# Output Templates

## Modernization Assessment Summary

```markdown
## React Modernization Assessment: [Application Name]

**Date:** YYYY-MM-DD
**React Version:** [current]
**Bundler:** [CRA / Vite / custom webpack / Next]
**Language:** [JS / mixed / TS]   **Codebase Size:** [components, LOC]
**Test Coverage:** [%]   **Test Framework:** [Enzyme / RTL / none]

### Migration Paths Identified

| Path | Effort | Risk | Blockers | Recommended Order |
|------|--------|------|---------|------------------|
| CRA → Vite | M | Low | [ejected webpack config] | 1 |
| Introduce TypeScript (allowJs) | M | Low | None | 2 |
| Enzyme → RTL | L | Med | None | 3 (before React 18) |
| React 17 → 18 | M | Med | [Enzyme; lib X no 18 peer] | 4 |
| Class → hooks | XL | Med | [low test coverage] | 5 |
| Legacy Redux → RTK | L | Med | None | 6 |

### Blockers

| Blocker | Affected Path | Resolution |
|---------|--------------|-----------|
| Enzyme (no React 18 adapter) | React 17 → 18 | Migrate tests to RTL first |
| [UI lib] — no React 18 peer | React 17 → 18 | Upgrade/replace before the bump |

### Recommended Phased Plan

**Phase 0 (Prerequisites — 1–2 weeks):**
- [ ] Add RTL characterization tests on critical flows (≥ 60% on hot paths)
- [ ] Ensure CI runs typecheck + tests

**Phase 1 (Tooling — 1 week):**
- [ ] CRA → Vite; map REACT_APP_* → VITE_*
- [ ] Add TypeScript with allowJs; type new files going forward

[Continue for each phase...]
```
