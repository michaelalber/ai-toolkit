# `spec.md` Template

The Spec phase writes this to the feature folder
`thoughts/shared/qrspi/YYYY-MM-DD-{feature-slug}/spec.md`. It is written in **two movements**: the
Design Brain-Dump (written first, then redirected by the human until approved), then the Structure
Outline (added only once `design_approved: true`). The Structure Outline section stays empty in the
`draft` artifact and is filled in for `ready-for-review`.

```markdown
---
date: YYYY-MM-DDTHH:MM:SS
repository: [repo name]
topic: "[feature, one line]"
tags: [qrspi, spec, relevant-tag]
git_commit: [short hash]
phase: Spec (S)
qrspi_feature: [feature-slug]
research_artifact: thoughts/shared/qrspi/YYYY-MM-DD-{slug}/research.md
design_approved: false        # flipped to true once the human approves the Brain-Dump
status: draft                 # draft -> ready-for-review -> approved
---

# Spec: [feature]

## Movement 1 — Design Brain-Dump  (source stage 3)
<!-- ~200 lines. Written first; revised in the brain-surgery loop until the human approves.
     Present this and STOP before writing Movement 2. -->

### Current state
[What the codebase does today, grounded in research.md with file:line citations.]

### Desired end state
[What it should do after this feature. Observable behavior, not implementation.]

### Design decisions & tradeoffs
1. [Decision] — [why; what was rejected; the tradeoff accepted]
2. [Decision] — [why; what was rejected; the tradeoff accepted]

### Risks & dependencies
- [Risk or external dependency the design takes on]

## Movement 2 — Structure Outline  (source stage 4 — only after design_approved: true)
<!-- A "C header file": signatures and types, NO bodies. Slices are VERTICAL. -->

### Type & signature sketch
```text
[NewType { field: Type, ... }]
[fn / method signature -> ReturnType]
```

### Vertical slices
| # | Slice (end-to-end increment) | Checkpoint (how it is verified) |
|---|------------------------------|----------------------------------|
| 1 | Mock API / contract          | [test or call that proves the contract] |
| 2 | Front-end against the mock   | [observable UI/behavior check] |
| 3 | Real database / persistence  | [integration check] |

Each slice goes all the way through (request -> behavior -> store); none is "all models" or
"all UI". Each is independently testable and maps to one fresh implementation session.
```

## Authoring rules
- **Research-grounded:** every "current state" claim cites `research.md` or a file path.
- **Brain-dump before outline:** never fill Movement 2 until the human approves Movement 1.
- **Header file, not source:** signatures and types only — no method bodies in the outline.
- **Vertical, not horizontal:** if a slice completes a whole layer (all models, then all UI),
  re-slice it before setting `status: ready-for-review`.
- **Lifecycle:** `draft` (Brain-Dump only) -> `ready-for-review` (outline added, design approved)
  -> `approved` (the human's gate before `/qrspi-plan` consumes it).
