# React Component Scaffolder — Conventions, Discipline & Recovery

Depth relocated from `SKILL.md`: domain principles, KB lookups, AI discipline rules,
anti-patterns, and error-recovery procedures.

## Domain Principles

| # | Principle | Description | Applied As |
|---|-----------|-------------|------------|
| 1 | **Explicit Props Contract** | Every component declares a `Props` type. Optional props have defaults; callbacks are typed. | `type ButtonProps = { label: string; onClick: () => void; disabled?: boolean }` |
| 2 | **Presentational vs Container** | A presentational component is pure (props in, JSX out). A container wires data/state to a presentational child. Default to presentational. | `UserCard` (pure) vs `UserCardContainer` (uses a query hook) |
| 3 | **Accessibility Baseline** | Semantic element first; interactive elements are real `<button>`/`<a>`; images have `alt`; inputs have labels. | `<button type="button">` not `<div role="button">` |
| 4 | **Controlled by Default** | Form inputs are controlled (value + onChange) unless there is a measured reason to use uncontrolled refs. | `<input value={value} onChange={…} />` |
| 5 | **Composition over Props Explosion** | When a component sprouts many boolean props, prefer `children`/slots or splitting it. | `<Card><Card.Header/>…</Card>` over 8 `show*` flags |
| 6 | **Stable Identity** | Callbacks/objects passed to memoized children are stabilized; list items use stable keys. | `useCallback`/`useMemo` only where a memoized child needs it |
| 7 | **Test the Behavior** | The RTL test renders the component and asserts user-visible behavior via roles/text, not implementation. | `screen.getByRole("button", { name: /save/ })` |
| 8 | **Story for the Surface** | A Storybook story (optional) documents the props surface and edge states (loading, empty, error). | `Default`, `Loading`, `Empty`, `Error` stories |
| 9 | **No Silent `any`** | Props, event handlers, and refs are typed. `any` requires a written justification. | `(e: React.ChangeEvent<HTMLInputElement>) => void` |
| 10 | **Errors Surface** | Async/container components render an error and (where relevant) sit under an error boundary. | `if (isError) return <p role="alert">…</p>` |

## Knowledge Base Lookups

Use `search_knowledge` (grounded-code-mcp). No React corpus — these cover TS + accessible UI; cite **react.dev**.

| Query | When to Call |
|-------|--------------|
| `search_knowledge("WCAG button link semantics keyboard", collection="ui_ux")` | At SCAFFOLD — confirm the accessible element for the interaction |
| `search_knowledge("WCAG form label error association", collection="ui_ux")` | When the component is a form/input |
| `search_knowledge("TypeScript React event handler types props", collection="javascript")` | When typing props and handlers |
| `search_code_examples("react testing library user event", language="typescript")` | When generating the RTL test |

## AI Discipline Rules

### CRITICAL: Typed Props, No Implicit `any`

**WRONG:**
```tsx
export function Badge(props) {                 // implicit any props
  return <span>{props.text}</span>;
}
```

**RIGHT:**
```tsx
export type BadgeProps = { text: string; tone?: "info" | "warn" };
export function Badge({ text, tone = "info" }: BadgeProps) {
  return <span className={`badge badge--${tone}`}>{text}</span>;
}
```

### REQUIRED: Accessible Interactive Elements

**WRONG:**
```tsx
<div onClick={onSave}>Save</div>             // not keyboard/AT reachable
```

**RIGHT:**
```tsx
<button type="button" onClick={onSave}>Save</button>
```

### CRITICAL: A Test Ships With the Component

The `*.test.tsx` is created in the same step as the component. A component without a co-located test is
an incomplete scaffold — never defer it.

## Anti-Patterns Table

| # | Anti-Pattern | Why It Fails | Correct Approach |
|---|-------------|-------------|-----------------|
| 1 | **Untyped / implicit `any` props** | No compile-time safety; bad autocomplete | Declare an explicit `Props` type |
| 2 | **`<div onClick>` for actions** | Not keyboard/screen-reader reachable | Use `<button>`/`<a>` |
| 3 | **No co-located test** | Behavior unverified; regressions slip in | Create `*.test.tsx` with the component |
| 4 | **Data fetching in a presentational component** | Couples UI to transport; hard to test | Fetch in a container/hook; pass data as props |
| 5 | **Boolean-prop explosion** | Unreadable, combinatorial states | Compose with `children`/slots or split |
| 6 | **Uncontrolled inputs by default** | State drifts from the DOM | Controlled inputs (value + onChange) |
| 7 | **Testing implementation details** | Brittle tests break on refactor | Query by role/text; assert user-visible behavior |
| 8 | **`key={index}` on dynamic lists** | Wrong reconciliation | Stable id key |
| 9 | **New literals to memoized children** | Defeats memo | `useMemo`/`useCallback` the value |
| 10 | **Missing error/empty states** | Blank UI on failure | Render explicit empty/error states |

## Error Recovery

### `jsx-a11y` flags an interactive element

```
Symptoms: eslint-plugin-jsx-a11y errors on a clickable div/span.

Recovery:
1. Replace with the semantic element (<button>/<a>).
2. If a non-semantic element is truly required, add role + tabIndex + onKeyDown and document why.
3. Re-run eslint until clean.
```

### RTL test cannot find an element

```
Symptoms: getByRole/getByLabelText throws "unable to find".

Recovery:
1. Prefer getByRole with an accessible name — if it is missing, the component has an a11y gap, not just a test gap.
2. Add the label/aria-label to the component (fixes both the test and accessibility).
3. Use screen.debug() to inspect the rendered tree.
```

## Output: Scaffold Checklist

```markdown
## React Component Scaffold: [Component Name]

### Contract
- [ ] `Props` type/interface declared (no implicit `any`)
- [ ] Optional props have defaults; callbacks typed
- [ ] Kind chosen: presentational / container / form / route

### Accessibility
- [ ] Semantic element used (button/link/heading/list)
- [ ] Labels / `alt` / ARIA where needed
- [ ] Keyboard reachable; focus visible
- [ ] `eslint-plugin-jsx-a11y` clean

### Tests
- [ ] RTL test co-located; asserts behavior via roles/text
- [ ] Edge states covered (empty / loading / error) where relevant

### Story (optional)
- [ ] Default + edge-state stories

### Verification
- [ ] `tsc --noEmit` clean
- [ ] `eslint` clean
- [ ] `vitest` green
```
