# Output Templates

## Feature Slice Scaffold: [Feature Name]

```markdown
## Feature Slice Scaffold: [Feature Name]

### Files Created
- [ ] `src/features/<name>/components/<Name>List.tsx` (container)
- [ ] `src/features/<name>/components/<Name>ListView.tsx` (presentational)
- [ ] `src/features/<name>/components/<Name>Form.tsx`
- [ ] `src/features/<name>/hooks/use<Name>sQuery.ts` (read)
- [ ] `src/features/<name>/hooks/useCreate<Name>.ts` (write)
- [ ] `src/features/<name>/data/api.ts`
- [ ] `src/features/<name>/data/schema.ts`
- [ ] `src/features/<name>/types.ts`
- [ ] `src/features/<name>/index.ts` (barrel)
- [ ] `src/features/<name>/<Name>List.test.tsx`
- [ ] `src/features/<name>/hooks/useCreate<Name>.test.ts`

### Wiring
- [ ] Route registered via the barrel import
- [ ] Provider added only if prop-drilling warranted it

### Verification
- [ ] `tsc --noEmit` clean
- [ ] `eslint` clean (hooks + a11y)
- [ ] `vitest` green for the slice
- [ ] No cross-feature imports detected
```

## Feature Folder Diagram

```
src/
├── features/
│   └── orders/
│       ├── components/
│       │   ├── OrderList.tsx        ← container: hook → view
│       │   ├── OrderListView.tsx    ← presentational (pure)
│       │   └── OrderForm.tsx        ← boundary validation
│       ├── hooks/
│       │   ├── useOrdersQuery.ts     ← read
│       │   └── useCreateOrder.ts     ← write (invalidates cache)
│       ├── data/
│       │   ├── api.ts                ← the only I/O
│       │   └── schema.ts             ← zod + inferred types
│       ├── types.ts
│       └── index.ts                  ← barrel (public surface)
├── shared/                           ← cross-cutting code & UI primitives
└── app/routes.tsx                    ← imports feature barrels only
```
