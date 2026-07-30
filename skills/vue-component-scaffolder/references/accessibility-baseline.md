# Accessibility baseline for scaffolded components

Every scaffolded component must clear this baseline before VERIFY. It maps to WCAG 2.2 (ground deeper
detail with `collection="ui_ux"`). The goal: the accessible path is the default; the inaccessible path
requires written justification.

## The baseline checklist

- [ ] **Semantic element first** — `<button>` for actions, `<a href>` for navigation, `<h1–h6>` for
      headings, `<ul>/<ol>/<li>` for lists, `<nav>/<main>/<header>` for landmarks.
- [ ] **Accessible name** — every interactive element has a visible label or `aria-label`. Icon-only
      buttons need `aria-label`.
- [ ] **Form labels** — every input has an associated `<label for>` (or wraps the input). Errors are
      associated via `aria-describedby` and announced (`role="alert"`).
- [ ] **Keyboard reachable** — all interactions work with Tab/Enter/Space; focus order is logical; focus
      is visible (don't remove the outline without a replacement).
- [ ] **Images** — `alt` text that conveys meaning, or `alt=""` for decorative images.
- [ ] **Color is not the only signal** — state (error, selected) is conveyed by text/icon too.
- [ ] **No keyboard traps** — modals (e.g. via `<Teleport>`) trap focus *intentionally* and restore it on close.

## Common fixes

| Anti-pattern | Fix |
|--------------|-----|
| `<div @click>` | `<button type="button" @click>` |
| `<span>` link | `<a href>` |
| Icon button, no text | add `aria-label="Close"` |
| Input without label | `<label for="x">` + `id="x"` |
| Error shown only in red | add text + `role="alert"` + `aria-describedby` |
| `outline: none` | provide a visible `:focus-visible` style |

## Lint gate

```bash
npx eslint src/<path> --plugin vuejs-accessibility
```

`eslint-plugin-vuejs-accessibility` catches most static issues (missing alt, label, redundant roles,
non-interactive elements with handlers). A clean run is necessary but not sufficient — keyboard and
focus behavior still need a manual pass for interactive widgets.

## Quick manual pass

1. Tab through the component — can you reach and operate everything?
2. Is the focused element always visibly highlighted?
3. With a screen reader (VoiceOver/NVDA), does each control announce a meaningful name and role?

If any answer is no, the component has an accessibility finding — fix it before marking the scaffold
complete.
