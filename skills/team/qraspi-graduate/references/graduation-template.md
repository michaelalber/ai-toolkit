# `graduation.md` Template -- the QRASPI → QRSPI handoff

The Graduate phase writes this to the project folder
`thoughts/shared/qraspi/YYYY-MM-DD-{slug}/graduation.md`. It is the **bootstrap artifact for the first
QRSPI feature**: QRSPI's Research assumes an existing codebase, and this file hands it the context
QRASPI produced so the very first `/qrspi-questions` run starts informed rather than cold. It captures
state that already exists -- it makes no new decisions.

## Why an explicit artifact (not just "start using QRSPI")

The seam between the workflows is conceptual -- both share `tdd`, vertical slices, and the read-only
`research-*` subagents. But QRSPI's inherited-repo Research maps a codebase without knowing *why* it
looks the way it does. `graduation.md` is the bridge: it points QRSPI at the accepted ADRs (the locked
decisions), the live fitness gates (the rules new features must keep green), and the stack -- so the
first feature does not re-litigate settled architecture.

## Structure

```markdown
---
date: YYYY-MM-DD
project: <slug>
phase: Graduation (QRASPI → QRSPI)
status: complete
target_repo: <path-or-url>
---

# Graduation — <project>: QRASPI → QRSPI

V0/V1 is shipped. This system is no longer greenfield. New features now use **QRSPI**.

## 1. Target repo + decision records
- Repo: `<path-or-url>`
- Accepted ADRs: `<target>/docs/adr/` — [list NNNN-*.md titles]
- These ADRs are the locked, path-dependent decisions. QRSPI features must respect them; a feature
  that needs to change one writes a NEW superseding ADR (it does not silently diverge).

## 2. Skeleton state
- Layers the walking skeleton exercises end-to-end: `<entrypoint → … → response>`
- Built slices (V0/V1): [from implementation-log-{slice}.md] — [slice names]
- Current CI status: green (`<ci command>` → exit 0)

## 3. Landed fitness functions (the live gates)
| Gate | Enforces ADR | CI step | What it forbids |
|------|--------------|---------|-----------------|
| <FF-1> | <ADR id> | <job/step> | <e.g. UI importing persistence> |
> New QRSPI features keep these green. They are the executable memory of the ADRs.

## 4. Stack declaration
- Language / runtime: <…>
- Framework / persistence / transport / auth: <… as locked by the ADRs>
- Test + lint + fitness tooling: <…>

## 5. Handoff to QRSPI
> **V0/V1 is shipped. New features now use QRSPI.**
> Run `/qrspi-questions` in this repo to start the next feature. QRSPI's Research (inherited-repo
> mode) will map the codebase with the `research-*` subagents; point it at this file and the ADRs
> for the "why" behind the structure. QRASPI is complete for this system.
```

## Authoring rules
- **Capture, don't decide.** Every section indexes something that already exists (the repo, the ADRs,
  `skeleton.md`, the fitness gates). Graduation invents nothing and re-opens nothing.
- **Name the gates.** The fitness-function table is the most load-bearing section -- it tells QRSPI
  features what they must not break. Copy it from `skeleton.md` / `architecture.md`, with ADR ids.
- **Point at the "why".** Always link the `docs/adr/` records; the handoff is useless if QRSPI cannot
  find the locked decisions.
- **End with the instruction.** The final block is the literal QRSPI bootstrap step (`/qrspi-questions`
  in this repo). `handoff_written` is not true until that block is present.
- **Terminal.** After `graduation.md` is written, QRASPI is done for this system. Do not loop back into
  QRASPI phases; the next work is a QRSPI feature.
