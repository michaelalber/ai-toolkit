---
title: AI Toolkit Audit Remediation Plan
status: approved
created: 2026-04-19
source-audit: docs/audit-remediation-plan.md
phases: 3
---

# AI Toolkit Audit Remediation Plan

> Source: Full suite audit of 67 skills + 67 agents (2026-04-19).
> Scope: CRITICAL and HIGH issues only.
> Execution: Run `/rpi-implement docs/audit-remediation-plan.md` to begin.

## Summary

| Phase | Focus | Files Changed | Blocking? |
|-------|-------|---------------|-----------|
| 1 | CRITICAL — broken references and missing files | ~7 | Yes — Phase 2 depends on Phase 1 |
| 2 | HIGH — structural skill defects | ~8 | No |
| 3 | HIGH — systemic negative trigger gaps (25 skills) | 25 | No |

**Acceptance criteria (suite-level):**

- [ ] `skills/skill-creator/SKILL.md` exists and passes 10-section structural check
- [ ] All files linked from skill `references/` sections resolve on disk
- [ ] `opencode/agents/confluence-guide-writer.md` exists with correct OpenCode frontmatter
- [ ] `confluence-guide-writer` SKILL.md is ≤ 400 lines; staleness detection language removed
- [ ] `environment-health` and `anomaly-detection` each have a labeled **AI Discipline Rules** section with ≥ 1 CRITICAL rule and WRONG/RIGHT example
- [ ] `nuget-package-scaffold` and `dotnet-architecture-checklist` each have ≥ 2 code-level WRONG/RIGHT examples in AI Discipline Rules
- [ ] `jira-review` has a 10-row Domain Principles Table and ≥ 1 WRONG/RIGHT code block in AI Discipline Rules
- [ ] All 25 skills listed in Phase 3 have an explicit "do NOT use when…" clause in their frontmatter `description:` field
- [ ] No regressions: all state block XML tags remain unique across the suite after edits

---

## Phase 1 — CRITICAL: Broken References and Missing Files

**Exit criteria:** All broken links resolve. `skill-creator` SKILL.md exists. Platform parity restored.

---

### P1.1 — Create `skills/skill-creator/SKILL.md`

**Why:** Listed in the Claude Code system prompt as an available skill (`skill-creator:skill-creator: Create new skills, modify and improve existing skills, and measure skill effectiveness`), but no SKILL.md exists. Broken reference at the platform level.

**Files to create:**
- `skills/skill-creator/SKILL.md`
- `skills/skill-creator/references/skill-template.md`
- `skills/skill-creator/references/scoring-rubric.md`

**Spec for `skills/skill-creator/SKILL.md`:**

The skill must follow the 10-section gold standard (`skills/architecture-review/SKILL.md`).

```
name: skill-creator
description: >
  Create, modify, and audit AI agent skills in this toolkit. Use when scaffolding
  a new SKILL.md from the 10-section template, revising an existing skill to fix
  structural defects, or scoring a skill against the 10-dimension rubric. Trigger
  phrases: "create skill", "new skill", "scaffold skill", "write skill", "revise
  skill", "update skill", "score skill", "audit skill quality".
  Do NOT use when the goal is to run a skill (invoke the skill directly); do NOT
  use when the goal is to create an agent definition (use AGENTS.md conventions).
```

> **Invocation name:** `skill-creator:skill-creator` (slash command: `/skill-creator`). The `skill-creator:` prefix is the plugin namespace; the command name is `skill-creator`.

**Section content spec:**

1. **Title + Epigraph** — "Skill Creator" with one quote on the craft of writing precise instructions for machines.

2. **Core Philosophy** — Non-negotiable constraints:
   - A skill that does not trigger reliably is worthless regardless of its internal quality.
   - Every new skill must have a `references/` directory with ≥ 2 supporting files before it is considered complete.
   - Revisions must not change state block XML tags (breaking change for in-flight sessions).
   - The 10-section template is the contract. Sections may be extended but not removed.

3. **Domain Principles Table** — 10 rows covering: trigger-first design, negative example mandate, scope discipline (single responsibility), AI-first phrasing, token budget discipline, state block uniqueness, references directory hygiene, WRONG/RIGHT evidence pattern, interop declaration, currency maintenance.

4. **Workflow** — Three modes:
   - `CREATE`: scaffold a new skill from template → DRAFT → VERIFY sections → create references/ → REPORT
   - `REVISE`: read existing skill → identify defects → patch minimally → verify no regressions → REPORT
   - `SCORE`: read existing skill → apply 10-dimension rubric → emit scorecard → classify issues → REPORT

5. **State Block** — XML tag: `<skill-creator-state>`. Fields: `mode` (create/revise/score), `target_skill`, `sections_complete`, `references_count`, `last_action`, `next_action`.

6. **Output Templates** — Three templates:
   - New skill scaffold (complete SKILL.md shell with all 10 sections labeled as stubs)
   - Revision diff summary (what changed and why)
   - Scorecard (10-dimension table matching the audit rubric)

7. **AI Discipline Rules** — CRITICAL rules:
   - WRONG: creating a skill without reading `skills/architecture-review/SKILL.md` first. RIGHT: always load the gold standard before scaffolding.
   - WRONG: changing a state block XML tag during revision. RIGHT: preserve the existing tag; only add fields.
   - WRONG: writing a description without a negative trigger. RIGHT: every description ends with "Do NOT use when…".

8. **Anti-Patterns Table** — 10 rows: skipping references/ creation, copying sections verbatim from another skill, using "helpful/useful/powerful/comprehensive" in description, writing narrative instead of imperatives, omitting WRONG/RIGHT examples, exceeding 300 lines without justification, bundling multiple responsibilities, writing a description that triggers on everything, using hedging language ("you could", "consider"), missing Knowledge Base Lookups when grounded-code-mcp is available.

9. **Error Recovery** — 3 scenarios: existing skill has no state block (add one, derive tag from skill name), revision breaks a reference path (restore original path, add redirect note), score reveals score < 20/50 (flag for DEPRECATE, draft replacement spec).

10. **Integration** — Links to `agent-spec-writer` (for agent creation vs. skill creation), `architecture-review` (gold standard), `automated-code-review` (post-creation quality check), `session-context` (for understanding existing skill suite state).

**References files:**
- `references/skill-template.md` — complete blank SKILL.md template with all 10 section headers and placeholder content
- `references/scoring-rubric.md` — the 10-dimension rubric (1–5 per dimension) as a standalone reference table

**Verification:**
```bash
# Confirm file exists
test -f skills/skill-creator/SKILL.md && echo "PASS" || echo "FAIL"
# Confirm references exist
test -f skills/skill-creator/references/skill-template.md && echo "PASS" || echo "FAIL"
test -f skills/skill-creator/references/scoring-rubric.md && echo "PASS" || echo "FAIL"
# Confirm frontmatter has name and description
grep -q "^name: skill-creator" skills/skill-creator/SKILL.md && echo "PASS" || echo "FAIL"
# Confirm all 10 section headers present
for header in "Core Philosophy" "Domain Principles" "Workflow" "State Block" "Output Templates" "AI Discipline Rules" "Anti-Patterns" "Error Recovery" "Integration"; do
  grep -q "## $header" skills/skill-creator/SKILL.md && echo "PASS: $header" || echo "FAIL: $header"
done
```

---

### P1.2 — Verify and restore missing reference files

**Why:** Two skills link to reference files that do not appear in the filesystem. Broken links make the `references/` contract unreliable.

**Files to verify, then create if missing:**

| Skill | Missing file | Content spec |
|-------|-------------|--------------|
| `skills/legacy-migration-analyzer/references/` | `api-replacement-patterns.md` | Table mapping deprecated .NET Framework APIs to their .NET 10 equivalents (e.g., `HttpWebRequest` → `HttpClient`, `Thread.Abort` → `CancellationToken`, `AppDomain.CreateDomain` → removed). Minimum 20 rows. |
| `skills/legacy-migration-analyzer/references/` | `aspnet-to-blazor-patterns.md` | Pattern mapping from ASP.NET Web Forms / MVC to Blazor equivalents: page lifecycle, code-behind to component model, UpdatePanel to Blazor re-render, GridView to TelerikGrid/QuickGrid. |
| `skills/dotnet-architecture-checklist/references/` | `cqrs-patterns.md` | CQRS reference: correct command/query handler structure, FreeMediator pipeline configuration, anti-patterns (fat handlers, shared base classes, cross-feature coupling). |
| `skills/dotnet-architecture-checklist/references/` | `red-flags.md` | Enumerated list of code-level red flags the checklist detects: static state in handlers, `new` keyword in handlers, DbContext as singleton, missing `CancellationToken`, synchronous I/O in async methods. |

**Verification:**
```bash
for f in \
  "skills/legacy-migration-analyzer/references/api-replacement-patterns.md" \
  "skills/legacy-migration-analyzer/references/aspnet-to-blazor-patterns.md" \
  "skills/dotnet-architecture-checklist/references/cqrs-patterns.md" \
  "skills/dotnet-architecture-checklist/references/red-flags.md"; do
  test -f "$f" && echo "PASS: $f" || echo "FAIL: $f"
done
```

---

### P1.3 — Create missing OpenCode `confluence-guide-writer` agent

**Why:** `claude/agents/confluence-guide-writer.md` exists but `opencode/agents/confluence-guide-writer.md` does not. This is the only platform parity gap in the suite (34 Claude vs. 33 OpenCode agents). AGENTS.md open loop acknowledges the count discrepancy.

**File to create:** `opencode/agents/confluence-guide-writer.md`

**Format:** Follow the OpenCode agent convention exactly:
- Frontmatter: `description:` + `mode: subagent` + boolean tool flags (no `name:`, no `model:`)
- Body: same 10-section structure as the Claude counterpart
- Replace `skills:` frontmatter array with `skill({ name: "..." })` inline calls in body
- Source content: mirror `claude/agents/confluence-guide-writer.md`, converting only the format

**Verification:**
```bash
test -f opencode/agents/confluence-guide-writer.md && echo "PASS" || echo "FAIL"
grep -q "mode: subagent" opencode/agents/confluence-guide-writer.md && echo "PASS format" || echo "FAIL format"
# Confirm no 'model:' or 'name:' fields (OpenCode convention)
grep -q "^model:" opencode/agents/confluence-guide-writer.md && echo "FAIL: model field present" || echo "PASS: no model field"
grep -q "^name:" opencode/agents/confluence-guide-writer.md && echo "FAIL: name field present" || echo "PASS: no name field"
```

---

## Phase 2 — HIGH: Structural Skill Defects

**Exit criteria:** All five defects corrected. No section additions or removals in other sections of affected files.

---

### P2.1 — Revise `skills/confluence-guide-writer/SKILL.md`

**Why:** Lowest-scoring skill (35/50). Verdict: REVISE. Three defects: (1) 730 lines with significant repetition, (2) mentions detecting stale pages — `doc-sync`'s responsibility, (3) mid-workflow `search_knowledge` calls create non-deterministic execution paths.

**Changes required:**

1. **Remove staleness detection language.** Find and delete any sentence that describes this skill as responsible for detecting when Confluence pages are out of date relative to code. Replace with: "If existing Confluence pages are stale relative to code changes, exit and invoke `doc-sync` first."

2. **Remove mid-workflow KB lookups.** The `search_knowledge` calls in the STRUCTURE and DRAFT phases should move to an upfront **Knowledge Base Lookups** section (same pattern as `architecture-review` lines 49–63). They must execute once during INTAKE, not per-page.

3. **Compress repetition of "One Task Per Page".** This principle appears in: Domain Principles, Anti-Patterns, Workflow (STRUCTURE phase), and AI Discipline Rules. Keep the authoritative statement in Domain Principles. Replace the other three with a single cross-reference line.

4. **Remove GATE clauses that require synchronous human approval mid-workflow.** GATE instructions are incompatible with autonomous execution. Convert each GATE to a conditional: "If hierarchy is ambiguous, emit the draft with a `[VERIFY]` annotation and stop. Do not wait for input."

5. **Target length:** ≤ 400 lines after changes.

**Rollback:** The original file should be preserved in git history. If the revised file introduces new trigger failures, revert and address separately.

**Verification:**
```bash
wc -l skills/confluence-guide-writer/SKILL.md
# Must be ≤ 400
grep -i "stale\|staleness\|out of date\|detect.*change" skills/confluence-guide-writer/SKILL.md
# Must return 0 matches (or only the handoff line)
grep -c "One Task Per Page" skills/confluence-guide-writer/SKILL.md
# Must return ≤ 2 (definition + one cross-reference)
```

---

### P2.2 — Add AI Discipline Rules to `environment-health` and `anomaly-detection`

**Why:** Both skills contain disciplinary guidance scattered in other sections but lack a dedicated, labeled **AI Discipline Rules** section. The gold standard requires this section with explicit CRITICAL rules and WRONG/RIGHT code examples.

**Changes required for `skills/environment-health/SKILL.md`:**

Insert a new `## AI Discipline Rules` section after the Anti-Patterns table. Minimum content:

- `CRITICAL: Probe Before Diagnosing` — WRONG: assume a container is unhealthy without reading `docker inspect` output. RIGHT: run `docker inspect <id>` and parse `State.Health.Status` before forming any diagnosis.
- `CRITICAL: Never Modify Production Resources` — WRONG: running `docker restart` on a container without confirming it is in the local dev environment. RIGHT: verify `DOCKER_HOST` and container labels confirm dev scope before any mutating command.
- `CRITICAL: Verify After Every Remediation` — WRONG: reporting "fixed" after running a remediation command. RIGHT: re-run the same probe that detected the problem and confirm the symptom is gone.

**Changes required for `skills/anomaly-detection/SKILL.md`:**

Insert a new `## AI Discipline Rules` section after the Anti-Patterns table. Minimum content:

- `CRITICAL: Baseline Before Detection` — WRONG: calling `detect_anomaly()` on a stream with no established baseline. RIGHT: call `establish_baseline()` with ≥ 100 samples before any detection run.
- `CRITICAL: Multiple Methods Must Agree` — WRONG: flagging an anomaly on a single Z-score threshold breach. RIGHT: require ≥ 2 independent detection methods (e.g., Z-score + CUSUM) to agree before raising an alert.
- `CRITICAL: Distinguish Fault from Signal` — WRONG: treating a sensor dropout (null/zero reading) the same as a statistical outlier. RIGHT: check for sensor fault indicators first; only run anomaly scoring on readings that pass the fault filter.

**Verification:**
```bash
grep -q "## AI Discipline Rules" skills/environment-health/SKILL.md && echo "PASS" || echo "FAIL"
grep -q "## AI Discipline Rules" skills/anomaly-detection/SKILL.md && echo "PASS" || echo "FAIL"
grep -q "WRONG:" skills/environment-health/SKILL.md && echo "PASS: WRONG/RIGHT present" || echo "FAIL"
grep -q "WRONG:" skills/anomaly-detection/SKILL.md && echo "PASS: WRONG/RIGHT present" || echo "FAIL"
```

---

### P2.3 — Add code-level WRONG/RIGHT examples to `nuget-package-scaffold` and `dotnet-architecture-checklist`

**Why:** Both skills have prose-only anti-patterns. The gold standard requires code evidence in AI Discipline Rules.

**Changes required for `skills/nuget-package-scaffold/SKILL.md`:**

In the existing **AI Discipline Rules** section, add two code-level WRONG/RIGHT blocks:

1. *Metadata completeness* — WRONG `.csproj` missing `<Description>`, `<Authors>`, `<PackageLicenseExpression>`. RIGHT `.csproj` with all required NuGet metadata fields.

2. *Multi-target verification* — WRONG: `<TargetFramework>net10.0</TargetFramework>` when the package claims netstandard2.0 compatibility. RIGHT: `<TargetFrameworks>net10.0;netstandard2.0</TargetFrameworks>` with a build matrix test that confirms both TFMs compile.

**Changes required for `skills/dotnet-architecture-checklist/SKILL.md`:**

In the existing **AI Discipline Rules** section, add two code-level WRONG/RIGHT blocks:

1. *Shared base handler* — WRONG: `public abstract class BaseHandler<TRequest, TResponse>` with shared state. RIGHT: independent `public sealed class CreateOrderHandler : IRequestHandler<CreateOrderCommand, Result>` with no inheritance.

2. *Fat endpoint* — WRONG: endpoint delegate containing validation, business logic, and persistence inline. RIGHT: endpoint delegate of ≤ 5 lines that sends a command through FreeMediator and returns a typed result.

**Verification:**
```bash
grep -c "WRONG:" skills/nuget-package-scaffold/SKILL.md
# Must be ≥ 3 (pre-existing + 2 new)
grep -c "WRONG:" skills/dotnet-architecture-checklist/SKILL.md
# Must be ≥ 3 (pre-existing + 2 new)
```

---

### P2.4 — Fix `skills/jira-review/SKILL.md`

**Why:** Scores 38/50. Two HIGH defects: (1) missing 10-row Domain Principles Table (has narrative Core Philosophy only), (2) AI Discipline Rules section has no WRONG/RIGHT code examples.

**Changes required:**

1. **Add Domain Principles Table.** Replace or supplement the Core Philosophy narrative with a formal `## Domain Principles` table (10 rows, columns: `# | Principle | Description | Applied As`). Suggested principles:

   | # | Principle | Description | Applied As |
   |---|-----------|-------------|------------|
   | 1 | Completeness Before Clarity | A vague issue blocks implementation regardless of its clarity. | Flag missing acceptance criteria before assessing description quality. |
   | 2 | Ambiguity Is Blocking | Ambiguous requirements produce wrong implementations. | Any requirement that admits two interpretations must be flagged as a blocker. |
   | 3 | Complexity Is Measurable | Implementation complexity can be estimated from signal density, not intuition. | Apply the complexity scoring formula; do not guess. |
   | 4 | Testability Is a Gate | An issue without acceptance criteria cannot be verified as done. | No issue passes review without at least one testable criterion. |
   | 5 | Size Predicts Risk | Large issues (high complexity score) correlate with planning failures. | Flag issues scoring ≥ 8 for decomposition before sprint commitment. |
   | 6 | Context Reduces Rework | Missing context forces implementers to make assumptions. | Every assumption the implementer must make is a required clarification. |
   | 7 | Dependencies Must Be Explicit | Undeclared dependencies cause cascading delays. | Flag any issue that implies another issue's completion without linking it. |
   | 8 | Reproducibility Is Non-Negotiable | A bug report that cannot be reproduced cannot be fixed. | Any bug issue missing reproduction steps fails review unconditionally. |
   | 9 | UI Issues Require Visuals | Describing a visual problem in text produces ambiguous fixes. | Flag UI/UX issues lacking screenshots or mockups. |
   | 10 | Estimates Are Evidence-Based | Story point estimates without complexity signals are fiction. | Require complexity scoring before accepting an estimate. |

2. **Add WRONG/RIGHT examples to AI Discipline Rules.** Add at minimum:
   - WRONG: flagging an issue as "vague" without citing the specific missing element. RIGHT: "Missing: acceptance criteria. The description says 'fix the login page' but does not state what 'fixed' means."
   - WRONG: recommending a complexity score of 8 without showing the signal count. RIGHT: cite the exact signals detected (API calls: 2, new table: 1, auth change: 1 → score: 7).

**Verification:**
```bash
grep -q "## Domain Principles" skills/jira-review/SKILL.md && echo "PASS" || echo "FAIL"
# Count table rows (lines starting with | followed by a digit)
grep -c "^| [0-9]" skills/jira-review/SKILL.md
# Must be ≥ 10
grep -q "WRONG:" skills/jira-review/SKILL.md && echo "PASS: WRONG/RIGHT present" || echo "FAIL"
```

---

## Phase 3 — HIGH: Systemic Negative Trigger Gaps

**Context:** Negative trigger precision is the highest-leverage property for correct skill selection. An agent that invokes the wrong skill wastes the entire session. The fix in every case is a single-sentence addition to the frontmatter `description:` field.

**Format:** For each skill, append to the end of the existing `description:` value (before the closing `---`):
```
Do NOT use when <scenario>; use <alternative> instead.
```

**Exit criteria:** Every skill below has the "Do NOT use when…" clause visible in its frontmatter.

**Verification (run once after all 25 edits):**
```bash
skills=(
  tdd-cycle tdd-implementer tdd-refactor tdd-pair tdd-verify
  edge-cv-pipeline jetson-deploy sensor-integration picar-x-behavior
  rag-pipeline-python rag-pipeline-dotnet mcp-server-scaffold ollama-model-workflow
  rust-architecture-checklist rust-security-review rust-feature-slice
  rust-migration-analyzer axum-scaffolder cargo-package-scaffold
  dotnet-vertical-slice ef-migration-manager nuget-package-scaffold minimal-api-scaffolder
  jira-review jira-comment-writer
)
for skill in "${skills[@]}"; do
  if grep -q "Do NOT use when" "skills/$skill/SKILL.md"; then
    echo "PASS: $skill"
  else
    echo "FAIL: $skill"
  fi
done
```

---

### P3 Tasks — One per skill

| # | Skill | Recommended negative trigger clause |
|---|-------|--------------------------------------|
| 1 | `tdd-cycle` | Do NOT use when TDD discipline is optional or exploratory; do NOT use when a failing test does not yet exist — create the test first. |
| 2 | `tdd-implementer` | Do NOT use when no failing test exists; do NOT use for refactoring — use `tdd-refactor` instead. |
| 3 | `tdd-refactor` | Do NOT use when tests are red; do NOT use to fix bugs or add new behavior — return to RED phase first. |
| 4 | `tdd-pair` | Do NOT use for autonomous solo work; do NOT use when no human partner is actively present in the session. |
| 5 | `tdd-verify` | Do NOT use on legacy code written before TDD was applied without first establishing a baseline; do NOT use as a hard gate without understanding project history. |
| 6 | `edge-cv-pipeline` | Do NOT use for cloud-based inference pipelines; do NOT use when the target hardware is a general-purpose server rather than an edge device. |
| 7 | `jetson-deploy` | Do NOT use for non-Jetson hardware; do NOT use for Raspberry Pi deployments — use `edge-cv-pipeline` and `sensor-integration` instead. |
| 8 | `sensor-integration` | Do NOT use for software-only data pipelines with no physical sensor hardware; do NOT use for cloud telemetry ingestion. |
| 9 | `picar-x-behavior` | Do NOT use for non-SunFounder Picar-X platforms without first adapting the API references; do NOT use for general robotics outside the Picar-X hardware profile. |
| 10 | `rag-pipeline-python` | Do NOT use when the application stack is .NET — use `rag-pipeline-dotnet` instead; do NOT use for full-text search without semantic retrieval requirements. |
| 11 | `rag-pipeline-dotnet` | Do NOT use when the application stack is Python — use `rag-pipeline-python` instead; do NOT use outside federal or .NET-primary environments. |
| 12 | `mcp-server-scaffold` | Do NOT use for synchronous REST-only integrations; do NOT use when the tool surface is a single function that does not benefit from the MCP protocol. |
| 13 | `ollama-model-workflow` | Do NOT use when the target runtime is a cloud provider API (OpenAI, Anthropic, Azure OpenAI); do NOT use when VRAM is unavailable on the target machine. |
| 14 | `rust-architecture-checklist` | Do NOT use as a substitute for `rust-security-review` — this checklist covers correctness and structure, not security implications. |
| 15 | `rust-security-review` | Do NOT use as a substitute for `rust-architecture-checklist` — security review does not cover ownership patterns, module structure, or API design. |
| 16 | `rust-feature-slice` | Do NOT use for microservice boundaries or inter-process architecture — this skill scopes to module organization within a single Rust binary. |
| 17 | `rust-migration-analyzer` | Do NOT use to execute the migration — this skill produces an assessment artifact only; do NOT use on a codebase that is already on current stable Rust with no legacy patterns. |
| 18 | `axum-scaffolder` | Do NOT use when the existing codebase uses Actix-web — scaffolding Axum into an Actix project requires manual integration not covered here. |
| 19 | `cargo-package-scaffold` | Do NOT use for internal workspace-only crates not intended for crates.io publication; do NOT use for binary applications — this skill targets library crates. |
| 20 | `dotnet-vertical-slice` | Do NOT use for layer-based (N-tier) architecture projects — this skill enforces feature folder structure and will conflict with existing layer conventions. |
| 21 | `ef-migration-manager` | Do NOT use for initial schema design or ad-hoc SQL management; do NOT use for Dapper or raw SQL projects without an EF Core DbContext. |
| 22 | `nuget-package-scaffold` | Do NOT use for internal workspace-only libraries not intended for NuGet publication; do NOT use for application projects. |
| 23 | `minimal-api-scaffolder` | Do NOT use for controller-based MVC projects — use `dotnet-vertical-slice` for handler architecture instead. |
| 24 | `jira-review` | Do NOT use after implementation is complete — this skill reviews issues for implementation readiness, not post-implementation accuracy; do NOT use on non-Jira issue trackers. |
| 25 | `jira-comment-writer` | Do NOT use when the audience is engineers or technical peers — use `pr-feedback-writer` instead; this skill targets non-technical stakeholders only. |

---

### P2.5 — Move inline comment templates out of `skills/jira-comment-writer/SKILL.md`

**Why:** The audit found `skills/jira-comment-writer/references/` contains only 1 file. The four comment templates (client-formal, client-friendly, pm-formal, pm-friendly) are currently inlined in the SKILL.md body, which inflates its token footprint and puts content in the wrong layer. Reference files are the correct location for reusable templates.

**Changes required:**

1. **Create `skills/jira-comment-writer/references/comment-templates.md`** containing the four comment templates extracted verbatim from the SKILL.md body. Format each template with a level-2 header matching its audience type:
   ```
   ## Client — Formal
   ## Client — Friendly
   ## PM — Formal
   ## PM — Friendly
   ```

2. **Replace the inline template blocks in SKILL.md** with a single cross-reference line per template:
   ```
   See [Comment Templates](references/comment-templates.md) — <audience-type> template.
   ```

3. **Verify `references/` now has ≥ 2 files** (the existing file + the new `comment-templates.md`).

**Rollback:** `git restore skills/jira-comment-writer/SKILL.md` and delete `skills/jira-comment-writer/references/comment-templates.md`.

**Verification:**
```bash
test -f skills/jira-comment-writer/references/comment-templates.md && echo "PASS" || echo "FAIL"
# Confirm 4 template headers present in the new file
for t in "Client — Formal" "Client — Friendly" "PM — Formal" "PM — Friendly"; do
  grep -q "## $t" skills/jira-comment-writer/references/comment-templates.md \
    && echo "PASS: $t" || echo "FAIL: $t"
done
# Confirm inline blocks removed from SKILL.md (no raw template bodies remain)
grep -c "## Client —" skills/jira-comment-writer/SKILL.md
# Must return 0
ls skills/jira-comment-writer/references/ | wc -l
# Must be ≥ 2
```

---

## Rollback Plan

| Phase | Rollback action |
|-------|----------------|
| 1 | Delete created files. No existing files modified in P1.1–P1.3. |
| 2 | `git diff` before editing; `git restore <file>` to revert any Phase 2 edit individually. |
| 3 | Each Phase 3 edit touches only the frontmatter `description:` field. `git restore skills/<name>/SKILL.md` reverts any individual skill. |

## Open Questions

None — all open questions resolved.
