# AI Discipline, Anti-Patterns, and Error Recovery

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
