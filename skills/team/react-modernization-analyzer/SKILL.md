---
name: react-modernization-analyzer
audience: team
description: Analyzes legacy React codebases and produces actionable modernization plans. Primary migration paths include class components to function components + hooks, Create React App to Vite, React 16/17 to 18 to 19, JavaScript to TypeScript, Enzyme to React Testing Library, legacy Redux to Redux Toolkit / Zustand / Context, and deprecated lifecycle/API removal. Does NOT perform the migration — assesses, quantifies risk, and plans. Triggers on phrases like "modernize react", "class to hooks", "upgrade react", "migrate CRA to vite", "react legacy migration", "react 17 to 18", "react js to typescript", "react technical debt", "enzyme to RTL".
---

# React Modernization Analyzer

> "The best time to modernize was five years ago. The second best time is now."
> -- Adapted from software engineering practice

> "Big bang rewrites fail. Incremental migration succeeds."
> -- Martin Fowler, *Refactoring*

## Core Philosophy

Legacy React codebases accumulate technical debt in predictable patterns: class components with lifecycle
methods that hooks express more clearly, Create React App's unmaintained and slow build, React versions
behind on concurrent features and security patches, untyped JavaScript where TypeScript would catch whole
bug classes, Enzyme tests coupled to implementation, and god-object Redux stores that predate Redux
Toolkit.

This skill assesses, quantifies, and plans — it does NOT perform the migration. The output is a
prioritized modernization plan with risk scores, effort estimates, and a recommended sequence. The plan
is the deliverable; execution is a separate task (often via `react-feature-slice` / `react-app-scaffolder`).

> **Grounding note:** the KB has no React corpus. Use `collection="javascript"` for the JS→TS path and
> cite **react.dev** (upgrade guides) + Vite/RTL docs for version-specific detail. Never invent a `react` collection.

**Non-Negotiable Constraints:**
1. **Assess before acting** — never recommend a migration path without evidence from the codebase
2. **Incremental over big-bang** — every recommendation must be achievable in phases, not a single rewrite
3. **Preserve behavior unchanged** — modernization, not reimplementation; the UI behaves identically after
4. **Dependencies are the real blockers** — a React 19 upgrade blocked by an unmaintained UI library is not viable
5. **Every recommendation must cite evidence** — "this looks like class components" is not evidence; `grep -rn "extends React.Component"` is

**What this skill is NOT:**
- It is NOT a migration execution tool — it produces a plan, not code
- It is NOT a code quality review — use `react-architecture-checklist` for that
- It is NOT a security review — use `react-security-review` for that

## Domain Principles

| # | Principle | Description | Applied As |
|---|-----------|-------------|------------|
| 1 | **Risk Assessment First** | Every modernization carries risk; quantify it before recommending. A class→hooks migration on 400 components with no tests differs from 40 components at 80% coverage. | Score every path: Effort (S/M/L/XL), Risk (Low/Med/High/Critical), Blocker potential |
| 2 | **Incremental Migration** | React supports class and function components side by side; TS and JS coexist; CRA→Vite can be staged. Every path must decompose into phases that each leave the app working. | Each recommendation has a phased approach with working checkpoints |
| 3 | **Dependency Compatibility** | The migration is only as viable as its dependencies. A UI library with no React 18 peer support blocks the upgrade; an unmaintained `react-router@5` blocks routing changes. | Audit `react`/`react-dom` peer ranges of every dependency before recommending a version bump |
| 4 | **Test Coverage Gate** | Characterization tests (RTL tests that document current behavior) must exist before risky migrations. Without them you cannot prove behavior was preserved. | Assess RTL coverage; recommend characterization tests as Phase 0 — especially before class→hooks |
| 5 | **Tooling Before Framework** | CRA→Vite and JS→TS are tooling migrations that unblock everything else (fast feedback, type safety). Usually the highest-value early wins. | Sequence CRA→Vite and TS adoption early; they de-risk later phases |
| 6 | **Strangler for State** | Legacy Redux → RTK/Zustand/Context is migrated slice by slice, not all at once. Server state moves to a query cache separately from client state. | Recommend per-slice store migration; split server-state extraction into its own phase |
| 7 | **Version Gating** | React 18 (concurrent, automatic batching, `StrictMode` double-invoke) and 19 (Actions, `use()`, ref-as-prop) change behavior. Identify what each bump enables and breaks. | Map each version jump's breaking changes against the codebase |
| 8 | **Test Framework Migration** | Enzyme has no React 18 adapter — it is a hard blocker for the version upgrade, migrated to RTL test by test. | Flag Enzyme as a React 18 blocker; plan Enzyme→RTL before/with the bump |
| 9 | **Effects & Data Layer** | `componentDidMount`+`fetch` and `useEffect`+`useState` server-state patterns are fragile under concurrent React. Recommend a query cache as part of modernization. | Identify ad-hoc fetching; recommend TanStack/RTK Query migration as a phase |
| 10 | **Build & Deploy Maturity** | Webpack ejected configs, Node-version pinning, and missing CI are modernization blockers. Assess them as prerequisites. | Flag ejected/aging build config and missing CI as prerequisites |

## Knowledge Base Lookups

Use `search_knowledge` (grounded-code-mcp). No React corpus — cover TS; cite **react.dev** upgrade guides for the rest.

| Query | When to Call |
|-------|--------------|
| `search_knowledge("TypeScript migration from JavaScript gradual", collection="javascript")` | At ASSESS — confirm JS→TS gradual-adoption tooling |
| `search_knowledge("TypeScript strict any incremental adoption", collection="javascript")` | When scoring the JS→TS path |
| `search_knowledge("WCAG keyboard accessibility audit", collection="ui_ux")` | When the modernization should also close a11y gaps |
| `search_code_examples("react class component to hooks", language="typescript")` | When estimating the class→hooks effort |

## Workflow

### Phase 1: SCAN

**Objective:** Inventory the codebase to understand its current state.

```bash
# React + tooling versions
grep -E '"(react|react-dom|react-scripts|typescript|vite|enzyme|redux|@reduxjs/toolkit)"' package.json

# Class components (class→hooks surface)
grep -rln "extends React.Component\|extends Component\|extends PureComponent" src/ | wc -l

# JavaScript vs TypeScript surface
find src -name "*.jsx" -o -name "*.js" | wc -l        # JS to migrate
find src -name "*.tsx" -o -name "*.ts" | wc -l        # already TS

# Build tooling
grep -l "react-scripts" package.json && echo "CRA — migrate to Vite"

# Deprecated lifecycles / APIs
grep -rn "componentWillMount\|componentWillReceiveProps\|UNSAFE_\|defaultProps" src/ | head

# Test framework
grep -rln "from 'enzyme'\|require('enzyme')" src/ | wc -l      # Enzyme = React 18 blocker
grep -rln "@testing-library/react" src/ | wc -l

# Ad-hoc data fetching
grep -rn "componentDidMount" src/ | wc -l
grep -rn "useEffect" src/ | grep -c "fetch\|axios"
```

### Phase 2: ASSESS

**Objective:** Score each migration path by effort, risk, and blocker potential.

| Path | Tool / Signal | Assessment Method |
|------|---------------|-------------------|
| Class → function + hooks | `grep extends Component` count | Count class components; weight by lifecycle complexity |
| CRA → Vite | `react-scripts` present | Check custom webpack/ejected config; map env vars (`REACT_APP_` → `VITE_`) |
| React 16/17 → 18 → 19 | `react` version | Map breaking changes; check every dep's peer range; find Enzyme |
| JS → TS | `.js/.jsx` count | Gradual adoption viability; `allowJs` staging |
| Enzyme → RTL | `enzyme` import count | Test-by-test; hard blocker for React 18 |
| Legacy Redux → RTK / Zustand | store/reducer count | Per-slice migration; separate server-state extraction |
| Ad-hoc fetch → query cache | `useEffect`+fetch / `componentDidMount` count | Identify fragile fetching under concurrent React |

Use `references/migration-risk-matrix.md` for scoring guidance.

### Phase 3: PLAN

**Objective:** Produce a prioritized, phased modernization plan.

1. **Phase 0: Prerequisites** — RTL characterization tests, CI, Node/version pinning (if missing)
2. **Phase 1: Tooling wins** — CRA → Vite; introduce TypeScript with `allowJs`
3. **Phase 2: Test framework** — Enzyme → RTL (unblocks the version bump)
4. **Phase 3: Version** — React 17 → 18 (then → 19), fixing breaking changes
5. **Phase 4: Components** — class → hooks, slice by slice
6. **Phase 5: State & data** — legacy Redux → RTK/Zustand; ad-hoc fetch → query cache
7. **Phase 6: Types** — finish JS → TS; turn on `strict`

### Phase 4: REPORT

**Objective:** Deliver the plan with evidence, risk scores, and effort estimates.

Use `references/migration-risk-matrix.md` for the risk scoring table.

## State Block

```xml
<react-modernization-state>
  phase: SCAN | ASSESS | PLAN | REPORT | COMPLETE
  react_version: [16 / 17 / 18 / 19 / unknown]
  bundler: cra | vite | webpack-custom | next | unknown
  language: js | mixed | ts
  ts_strict: true | false | n/a
  class_components: [count]
  test_framework: enzyme | rtl | mixed | none
  state_lib: legacy-redux | rtk | zustand | context | none
  migration_paths_identified: 0
  blockers_identified: 0
  last_action: [description]
  next_action: [description]
</react-modernization-state>
```

## Output Templates

### Modernization Assessment Summary

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

## AI Discipline Rules

### CRITICAL: Evidence Before Recommendation

**WRONG:**
```
This looks like an old React app. I recommend upgrading to React 19.
```

**RIGHT:**
```
Version detection:
  package.json → "react": "^17.0.2"
  grep "extends Component" → 128 class components across 94 files
  grep "from 'enzyme'" → 60 test files use Enzyme (no React 18 adapter)

React 17 → 18 is viable but Enzyme is a hard blocker. Sequence Enzyme → RTL first.
```

### REQUIRED: Quantify Before Scoring

**WRONG:** "The class→hooks migration is large."

**RIGHT:** "128 class components (grep count); 41 use `componentDidMount` data fetching; test coverage 18%. Effort: XL. Risk: Med — raised by low coverage. Recommend characterization tests first."

### CRITICAL: Incremental Plans Only

**WRONG:** "Rewrite the app in Vite + TypeScript + hooks."

**RIGHT:** "Phase 1: CRA→Vite (1wk). Phase 2: add TS via allowJs (ongoing). Phase 3: Enzyme→RTL (2wk). Phase 4: React 18 (1wk). Phase 5: class→hooks, ~15 components/week."

## Anti-Patterns Table

| # | Anti-Pattern | Why It Fails | Correct Approach |
|---|-------------|-------------|-----------------|
| 1 | **Big-bang rewrite recommendation** | Rewrites fail; behavior is lost; timeline explodes | Incremental migration with working checkpoints |
| 2 | **Recommending class→hooks without tests** | Cannot verify behavior preserved | RTL characterization tests as Phase 0 |
| 3 | **Ignoring dependency peer ranges** | A lib with no React 18 peer blocks the bump | Audit every dep's react peer range first |
| 4 | **Missing the Enzyme blocker** | Enzyme has no React 18 adapter; the bump fails | Flag Enzyme → RTL as a prerequisite to React 18 |
| 5 | **Combining version + class→hooks + JS→TS at once** | Unmanageable, untestable change set | Sequence: tooling → tests → version → components → state → types |
| 6 | **No effort estimates** | A plan without estimates can't be scheduled | Every phase has S/M/L/XL or a day estimate |
| 7 | **Assessing without running greps** | Counts are evidence; intuition is not | Always run the SCAN greps before scoring |
| 8 | **Recommending React 19 features pre-upgrade** | Actions/`use()` don't exist on 17/18.0 | Gate feature recommendations to the post-upgrade version |
| 9 | **Treating server state like client state in the plan** | Moving fetch into a store reinvents caching | Plan server-state → query cache as its own phase |
| 10 | **Skipping the CRA→Vite tooling win** | Slow builds drag every later phase | Do the tooling migration early to speed feedback |

## Error Recovery

### Cannot determine a dependency's React peer support

```
Symptoms: a UI library's React 18/19 compatibility is unclear.

Recovery:
1. Check package.json peerDependencies on react/react-dom.
2. Check the package's repo for recent releases and React 18/19 issues.
3. Check for a maintained fork or a modern replacement.
4. If unknown, mark "Unknown — manual investigation required" in the blockers table; do not assume.
```

### Test coverage is zero

```
Symptoms: no RTL/Jest tests found.

Recovery:
1. Document: "Coverage 0% — no behavioral tests."
2. Phase 0 becomes mandatory: RTL characterization tests on critical flows before any risky migration.
3. Flag this as the highest-risk factor; do not recommend class→hooks until Phase 0 is done.
```

### Build config is ejected / custom webpack

```
Symptoms: `npm run eject` was run, or a hand-rolled webpack config exists.

Recovery:
1. Inventory the custom webpack needs (loaders, aliases, env injection, proxies).
2. Map each to its Vite equivalent (plugins, resolve.alias, define, server.proxy).
3. Flag any need without a Vite equivalent as a blocker to resolve before the tooling migration.
```

## Integration with Other Skills

| Skill | Relationship |
|-------|-------------|
| `react-app-scaffolder` | When the plan includes CRA → Vite, scaffold the target Vite + TS skeleton and migrate into it. |
| `react-feature-slice` | Modernized components are reorganized into feature slices; use during the component phase. |
| `react-architecture-checklist` | Run after modernization to verify the new structure meets quality gates. |
| `react-security-review` | Run after the upgrade — new React/deps have different security characteristics. |
| `python-modernization-analyzer` / `rust-migration-analyzer` | Sibling analyzers; identical assess-don't-execute philosophy, different stacks. |
