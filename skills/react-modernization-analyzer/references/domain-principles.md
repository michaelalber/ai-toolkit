# Domain Principles

The ten principles that drive every assessment and recommendation.

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
