# Plan: Agent-Safe Global Instructions (Claude Code · OpenCode · Pi)

**Status:** Draft — awaiting owner review · **Date:** 2026-11-09 · **Owner:** Michael K. Alber

## Problem

The three global instruction files were written for an *interactive chat with a frontier model*.
They are now also used by *agent loops on local models* (Pi `-p`, OpenCode `run` and subagents,
Claude Code `-p`), where they fail in measurable ways:

| Evidence (Pi guardrails test, 2026-11-09) | Cause in the global file |
|---|---|
| Guarded C# runs stalled >10 min where bare runs passed | "One logical unit per response … stop … until confirmed" |
| Non-interactive runs need a prompt workaround to start | "Do NOT begin work until context is confirmed" |
| 0 grounding calls in guarded runs | Grounding rule buried at ~80% of a 13–23 KB file, no trigger |
| Replies cut off, run ends early (`stopReason: length`) | 8192 output cap (config, fixed for Pi) |

Plus drift: three files that started from one source have diverged (`think:` vs reasoning-effort
wording, language sections, collection maps), the repo templates disagree with installed copies,
and docs describe behavior the tools do not have (`router-config`, per-request `num_ctx`).

## Goals

1. **Works in both modes** on every harness: interactive sessions keep the human-in-the-loop
   rules; non-interactive runs proceed to green tests without waiting.
2. **One shared core**, byte-identical across the three files, plus a short harness section each.
3. **Public templates stay generic**; personal enrichment lives only in installed copies.
4. **Every claim verified** against the tool's docs or a run — no invented features.
5. **Measured before and after** with the existing bake-off harness.

Non-goals: changing skills/agents/commands; changing hooks or permission semantics beyond the
specific fixes listed; publishing anything.

## Design

```
<global file> = CORE (shared, identical)  +  HARNESS section  +  (installed copy only) PERSONAL overlay
```

| | Claude Code | OpenCode | Pi |
|---|---|---|---|
| Target model | Frontier (+ local) | Local + frontier | Local |
| Size budget | ≤ 8 KB | ≤ 6 KB | ≤ 4 KB (done: 3.7 KB) |
| Grounding call | MCP `search_knowledge` | MCP `search_knowledge` | CLI `grounded-code-mcp search` |
| Extra sections | Microsoft Learn MCP, Jira (optional) | Microsoft Learn MCP | — |
| Personal overlay mechanism (to verify) | `@path` import in `~/.claude/CLAUDE.md` | `instructions` array in `opencode.json` | parent-dir `AGENTS.md` merge, or kept out |

**CORE contents** (from the Pi file, which is the tested baseline): mode rule (interactive vs
non-interactive), read-before-edit, look-it-up trigger, tests-define-done, smallest change, run
tests after each change, never claim unverified, two-failures-then-stop, design line, language
defaults (overridable, Laravel conditional), boundaries (git/delete/public API/irreversible ask
in both modes), security incl. never-resolve-a-secret, output rules, ponytail precedence.

**Moves out of the globals** into `project-templates/` or skill `references/`: SOLID/Clean
Architecture tables, quality-gate tables, Session Boot ritual (→ project `AGENTS.md`/`CLAUDE.md`
template, where it applies), Jira workflow detail, the full collection map (→ one line +
`list-sources`).

## Acceptance criteria (written first; binary)

**A. Structural — automated (new lint rule in `tools/skill-evals`, run in CI):**
- A1 The CORE block (between `<!-- core:start -->` / `<!-- core:end -->`) is byte-identical in all three files.
- A2 Size ≤ budget per file.
- A3 No unconditional confirmation gate: no `Do NOT begin` / `until confirmed` outside the Interactive bullet.
- A4 No personal strings in repo templates (blocklist: project names, book titles, hostnames/IPs, employer names).
- A5 Every referenced file/tool/feature exists (`router-config`, `SYSTEM.md`-style regressions).

**B. Behavioral — bake-off harness, local model `flint:40b-a2b-qat-int4`, 3 hard tasks × 3 runs:**
- B1 Pi `-p`, OpenCode `run`, Claude Code `-p` each: guarded pass rate ≥ bare pass rate.
- B2 No guarded run ends by waiting for confirmation or by `stopReason: length`.
- B3 Grounding called in ≥ 1 guarded run per harness.
- B4 0 test-tamper flags.

**C. Interactive — manual checklist, one session per harness:**
- C1 States task/constraints before work. C2 Asks before `git commit`. C3 Asks before deleting a file.

**D. Install:** fresh install via each `install-*.sh` into a temp `HOME` yields a working config
(tool lists models / loads instructions without error); existing installs are not overwritten.

## Phases

| # | Phase | Output | Exit gate |
|---|---|---|---|
| 0 | **Housekeeping** — resolve pre-existing uncommitted `claude/global` changes (see D1); review + commit Pi work (2 commits) | Clean tree | Owner approval |
| 1 | **Evals first** — lint rule A1–A5 (TDD, in `tools/skill-evals`); `pi_bench.py` generalized to drive OpenCode and Claude Code headless | Failing A1–A3 on current files | Tests red for the right reason |
| 2 | **Baseline** — run B1–B4 on *current* globals for all three harnesses | `results-guardrails-before.md` | Numbers recorded |
| 3 | **CORE** — extract from Pi file, add markers; Pi file adopts markers (no content change) | Pi passes A1–A5 | Lint green for Pi |
| 4 | **OpenCode** — `AGENTS.md` = CORE + harness; `opencode.json` fixes (below); README cut to essentials, local-model setup points to the Pi guide | | A green; owner review |
| 5 | **Claude Code** — `CLAUDE.md` = CORE + harness; README sync; settings untouched except D1 | | A green; owner review |
| 6 | **Personal overlays** — verify each harness's include mechanism; rebuild installed copies on this PC + Gazelle; checksum match | | D green |
| 7 | **Verify** — rerun B on new globals (= guardrails4 + Claude Code headless baseline for the post); C manually | `results-guardrails-after.md` | B, C green |
| 8 | **Record + commit** — Persistent Decision rows (CLAUDE.md/AGENTS.md mirror), one commit per harness, push only on approval | | Owner approval |

### Specific fixes carried into phases 4–5

`opencode.json`: `opencode run*` allow → ask (spawns a new agent); `sudo systemctl stop/start*`
scoped to named units or → ask; comment that `make*` / `dotnet build|test` execute repo-defined
code; fix "pinned model versions" and "above/below" comments; note agent temperatures override
model sampling.

OpenCode README: drop stale `think:` / Core Philosophy / Snyk / provider-block text; replace
`spec.md` with the Jira/Confluence convention; correct the `options.num_ctx` claim (verify first);
drop sub-7B agent recommendations (contradict the 20B+ floor); fix the Modelfile template
(`num_predict 2048` cap; `SYSTEM` block overridden by the client).

CORE .NET line: "match the existing style (vertical slice for new code)" — aligns with the
2026-06-03 detect-and-match decision instead of mandating VSA/CQRS.

## Decisions needed from the owner

| # | Decision | Recommendation |
|---|---|---|
| D1 | Uncommitted change in `claude/global/settings.local.json` **removes** the `Write(//**/.claude/settings*.json)` deny (agent could then rewrite its own permissions via Write). Keep or revert? | **Revert** unless intentional |
| D2 | How far to trim `CLAUDE.md` (frontier models tolerate length) | Same CORE; keep git HITL + Microsoft Learn; target ≤ 8 KB |
| D3 | Personal overlay mechanism per harness | Verify each in Phase 6; fall back to hand-maintained installed copies |
| D4 | Public repo names an employer in several files (oss-vetting skill + suite table). Matters if the post links the repo | Generalize to "federal contractor / national lab" before linking |
| D5 | Behavioral eval for Claude Code uses a paid frontier model | Run once (9 runs) — doubles as the post's Claude Code baseline |

## Risks

| Risk | Mitigation |
|---|---|
| Shorter rules lose behavior that mattered | Phase 2 baseline vs Phase 7; C checklist; old files recoverable from git |
| Install scripts are copy-if-absent → existing machines silently keep old files | Phase 6 updates both machines explicitly; README states the manual sync |
| Small sample (3×3) can't show small effects | Report as directional; tasks where bare fails are the signal |
| Harness CLIs differ in JSON output (grounding detection) | Phase 1 adapter per harness, each with a fixture test |
