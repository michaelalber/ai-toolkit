# Output Templates

## Feature Slice Scaffold: [Feature Name]

```markdown
## Feature Slice Scaffold: [Feature Name]

### Files Created
- [ ] `src/features/<name>/components/<Name>List.vue` (container)
- [ ] `src/features/<name>/components/<Name>ListView.vue` (presentational)
- [ ] `src/features/<name>/components/<Name>Form.vue`
- [ ] `src/features/<name>/composables/use<Name>sQuery.ts` (read)
- [ ] `src/features/<name>/composables/useCreate<Name>.ts` (write)
- [ ] `src/features/<name>/data/api.ts`
- [ ] `src/features/<name>/data/schema.ts`
- [ ] `src/features/<name>/types.ts`
- [ ] `src/features/<name>/index.ts` (barrel)
- [ ] `src/features/<name>/<Name>List.test.ts`
- [ ] `src/features/<name>/composables/useCreate<Name>.test.ts`

### Wiring
- [ ] Route registered via the barrel import
- [ ] `provide`/`inject` added only if prop-drilling warranted it

### Verification
- [ ] `vue-tsc --noEmit` clean
- [ ] `eslint` clean (vue + a11y)
- [ ] `vitest` green for the slice
- [ ] No cross-feature imports detected
```

## Feature Folder Diagram

```
src/
├── features/
│   └── orders/
│       ├── components/
│       │   ├── OrderList.vue        ← container: composable → view
│       │   ├── OrderListView.vue    ← presentational (pure)
│       │   └── OrderForm.vue        ← boundary validation
│       ├── composables/
│       │   ├── useOrdersQuery.ts     ← read
│       │   └── useCreateOrder.ts     ← write (invalidates cache)
│       ├── data/
│       │   ├── api.ts                ← the only I/O
│       │   └── schema.ts             ← zod + inferred types
│       ├── types.ts
│       └── index.ts                  ← barrel (public surface)
├── shared/                           ← cross-cutting code & UI primitives
└── app/routes.ts                     ← imports feature barrels only
```
