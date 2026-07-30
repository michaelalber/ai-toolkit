# React version & pattern migration reference

Breaking-change and pattern detail behind the ASSESS phase. Use to map each path against what the SCAN
greps found. Cite **react.dev** upgrade guides as the authority; this is a planning summary, not a substitute.

## React 17 → 18

| Change | Impact | Detection |
|--------|--------|-----------|
| `ReactDOM.render` → `createRoot` | Required entry-point change; enables concurrent features | `grep -rn "ReactDOM.render" src/` |
| Automatic batching | State updates in promises/timeouts now batch — can change render timing | review code relying on multiple sync re-renders |
| `StrictMode` double-invokes effects (dev) | Surfaces missing effect cleanup as double-fires | `grep -rn "useEffect" src/` then audit cleanups |
| Enzyme has **no** React 18 adapter | Hard blocker | `grep -rln "from 'enzyme'" src/` |
| Dependency peer ranges | Libs pinned to `react@17` block the bump | check each dep's `peerDependencies` |

## React 18 → 19

| Change | Impact | Detection |
|--------|--------|-----------|
| `propTypes` / `defaultProps` removed for function components | Runtime/prop defaults must move to JS default params | `grep -rn "defaultProps\|propTypes" src/` |
| String refs removed | Must use callback/`useRef` | `grep -rn 'ref="' src/` |
| Legacy context (`childContextTypes`) removed | Migrate to `createContext` | `grep -rn "childContextTypes\|contextTypes" src/` |
| New: Actions, `useActionState`, `use()`, `ref` as a prop | Opportunities post-upgrade — do not recommend before the bump | n/a |

## Class → function + hooks (lifecycle map)

| Class lifecycle | Hook equivalent |
|-----------------|-----------------|
| `constructor` state | `useState` / `useReducer` |
| `componentDidMount` | `useEffect(() => {…}, [])` |
| `componentDidUpdate` | `useEffect(() => {…}, [deps])` |
| `componentWillUnmount` | cleanup returned from `useEffect` |
| `shouldComponentUpdate` | `React.memo` + stable props |
| `componentDidCatch` / `getDerivedStateFromError` | **stay a class** — error boundaries have no hook yet |

Notes:
- `UNSAFE_componentWillMount/ReceiveProps/Update` have no direct hook — they need genuine refactoring,
  not a mechanical swap. Flag components using them as higher effort.
- Error boundaries remain class components even in modern React — do not "migrate" them to hooks.
- `componentDidMount` + `fetch` should become a query hook, not just a `useEffect` — fold this into the
  data-layer phase, not the class→hooks phase.

## CRA → Vite

| CRA concept | Vite equivalent |
|-------------|-----------------|
| `react-scripts start/build` | `vite` / `vite build` |
| `REACT_APP_*` env vars | `VITE_*` (and `import.meta.env`) |
| `public/index.html` | root `index.html` with `<script type="module" src="/src/main.tsx">` |
| Jest (built in) | Vitest (`test` block in `vite.config.ts`) |
| SVG-as-component, asset imports | `vite-plugin-svgr`, native asset handling |
| Proxy in `package.json` | `server.proxy` in `vite.config.ts` |
| Ejected webpack config | map loaders/plugins to Vite plugins — **blocker if no equivalent** |

## JS → TS (gradual)

1. Add `typescript` + `tsconfig` with `allowJs: true`, `checkJs: false`, `strict: true`.
2. New files are `.tsx`/`.ts`; existing `.jsx` keep working.
3. Rename leaf modules first (fewest dependents), add types, move up the graph.
4. Turn off `allowJs` only when the last `.js` is gone.
5. Track progress with the `find … -name '*.js*' | wc -l` count from SCAN.

## Enzyme → RTL (test by test)

| Enzyme idiom | RTL idiom |
|--------------|-----------|
| `shallow`/`mount` + `.find('.cls')` | `render` + `screen.getByRole/Text/Label` |
| `wrapper.state()` / `.instance()` | assert behavior, not internals (no state access) |
| `wrapper.setProps` | `rerender` |
| simulate events | `userEvent` |

RTL tests assert user-visible behavior, so they double as characterization tests for the version/hooks
migrations — prioritize converting the highest-traffic flows first.
