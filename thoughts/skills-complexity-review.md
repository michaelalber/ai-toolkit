# Skills Complexity Review Plan

## Context

The user wants a strategic assessment: are the 89 skills overly complicated, are SKILL.md files too long, and are modern models (Sonnet 4.6 / Opus 4.7) now capable enough that verbose skills constrain rather than guide them?

The answer to all three questions is **yes** — and the data is unambiguous.

---

## Findings

### Scale of violations

| Metric | Value |
|--------|-------|
| Total skills | 89 |
| Full-template tier (stated limit: ≤ 400 lines) | 74 |
| Skills **exceeding** 400 lines | 37+ |
| Gold standard (architecture-review) | 611 lines (53% over limit) |
| Worst offender (dotnet-vertical-slice) | 907 lines (127% over limit) |
| Minimal tier (≤ 100 lines) | 11 |
| Skills within the 400-line limit | ~37 full-template skills |

The limit is violated by roughly half the full-template tier. The gold standard is itself non-compliant.

### Top 15 most bloated (primary targets)

| Skill | Lines | Over by |
|-------|-------|---------|
| dotnet-vertical-slice | 907 | +507 |
| rag-pipeline-python | 779 | +379 |
| legacy-migration-analyzer | 775 | +375 |
| spec-coach | 758 | +358 |
| python-arch-review | 729 | +329 |
| dotnet-security-review-federal | 706 | +306 |
| rag-pipeline-dotnet | 657 | +257 |
| technical-debt-assessor | 632 | +232 |
| architecture-journal | 624 | +224 |
| security-review-trainer | 618 | +218 |
| architecture-review | 611 | +211 |
| pr-feedback-writer | 600 | +200 |
| spec-implement | 590 | +190 |
| refactor-challenger | 590 | +190 |
| code-review-coach | 574 | +174 |

### Primary bloat categories (identified from detailed reads)

From reading `dotnet-vertical-slice` (907 lines) and `architecture-review` (611 lines), the bloat falls into five distinct categories:

#### 1. Embedded code templates (biggest driver)
Complete Razor/C#/Python code inline in the skill body that belongs in `references/`.

`dotnet-vertical-slice` example:
- Telerik Blazor list page template: ~100 lines of `.razor`
- Telerik Blazor edit page template: ~100 lines of `.razor`
- Handler test templates: ~60 lines of C#
- DTO and mapping config templates: ~63 lines of C#
- Bash scaffold commands: ~20 lines

**Total: ~343 lines of code inline** in a skill that already has `references/` files. These should be in `references/dotnet-vertical-testing.md` (which already exists) and new `references/` files.

Skills most affected: `dotnet-vertical-slice`, `rag-pipeline-python`, `rag-pipeline-dotnet`, all `-scaffolder` skills.

#### 2. Multiple state block progression examples
3–4 fully filled-in `<state>` examples showing conversation progression. One canonical example with placeholder values is sufficient — models understand progression without seeing it played out.

`architecture-review` shows 4 filled examples (challenge → attempt → compare → reflect): ~75 lines.

**Savings: ~40–70 lines per skill.** Skills most affected: all multi-phase skills with workflow loops.

#### 3. Redundant output templates
Full markdown report templates for every session phase (session opening, session closing, phase transitions, mid-review check-ins). Sonnet 4.6 does not need to be shown what a markdown heading looks like.

`architecture-review`: Session Opening + Category Transition + Mid-Review Check-In + Session Closing = ~95 lines of template scaffolding.

**Savings: ~50–100 lines per skill.** Skills most affected: `-coach`, `-trainer`, `-review`, `-analyzer` skills.

#### 4. WRONG/RIGHT examples for obvious principles
Explicit code examples demonstrating well-established OOP/design patterns the model already knows. The principle is captured in the Core Philosophy; the example adds tokens without adding knowledge.

`dotnet-vertical-slice`: WRONG/RIGHT examples for "don't create shared base handlers," "don't import from other features," "pipeline behaviors are infrastructure" = ~136 lines of C# examples.

Modern models don't need `// WRONG: shared base handler` followed by 20 lines of C# to understand the principle.

**Savings: ~80–140 lines for heavily documented skills.** Skills most affected: all full-template scaffolding/architecture skills.

#### 5. Decision trees and ASCII workflow diagrams
Command/Query/Notification decision trees and ASCII art workflow diagrams add visual polish but consume tokens. Modern models can hold workflow logic from prose descriptions.

**Savings: ~20–50 lines per skill.**

---

## What still earns its tokens for modern models

These sections should be kept intact regardless of line count:

| Section | Why it still adds value |
|---------|------------------------|
| **Core Philosophy + Non-Negotiables** | Domain-specific constraints the model can't infer |
| **Domain Principles Table** | Non-obvious invariants with Priority ratings |
| **Knowledge Base Lookups table** | Explicit `grounded-code-mcp` routing — models don't auto-route |
| **State Block definition** (one example) | Multi-turn coherence anchor |
| **AI Discipline Rules** (kept for non-obvious violations only) | Guards where domain expertise differs from general intuition |
| **Error Recovery** (domain-specific scenarios) | Failure modes specific to the tool/framework |
| **Integration with Other Skills** | Cross-skill routing that models don't know without being told |

---

## Trim protocol (per skill)

For each skill exceeding 400 lines, apply in this order:

1. **Move embedded code templates to `references/`** — create new reference files if needed, update the "Reference Files" section pointer. Do not delete — move.
2. **Reduce state progression examples to 1** — keep one canonical filled example, delete the rest.
3. **Cut or collapse output templates** — replace verbose templates with a brief structural skeleton (3–5 lines); remove the filled-out versions.
4. **Remove WRONG/RIGHT examples where the principle is well-established** — keep only where the wrong approach is domain-specific and non-obvious.
5. **Replace decision trees** with prose (2–3 sentences) in the Workflow section.
6. **Verify 10 mandatory sections still present** after trimming.

Expected result per skill: 200–400 line reduction for the most bloated; most should land under 400 after steps 1–3 alone.

---

## Modern model lens: are skills constraining Sonnet 4.6 / Opus 4.7?

**Yes, in three specific ways:**

### 1. Output template lock-in
When a skill provides a full markdown output template (with every heading, every table column, every bullet structure), the model fills in the template rather than structuring the output to fit the context. This produces formulaic, copy-paste responses that don't adapt to the actual conversation. Sonnet 4.6 generates appropriate structure without being shown the template — providing one constrains it.

### 2. Workflow rigidity
Phase-by-phase workflows with exit criteria and mandatory actions ("you MUST ask 3 questions per category before proceeding") treat the model as a state machine. Sonnet 4.6 handles multi-phase work well without explicit phase gating. The phase labels are useful; the mandatory step counts and transition conditions are noise.

### 3. Token budget on the wrong content
A skill loaded into context displaces conversation content. When 300 of 900 lines are Telerik Blazor Razor templates that are only relevant for one sub-use-case, every invocation pays for those tokens even when they're irrelevant. Moving conditional content to `references/` means the model loads it only when it searches for it, not unconditionally.

**What modern models gain from well-structured skills (worth keeping):**
- Explicit routing to `grounded-code-mcp` — the model does not know these collection names without being told
- Non-obvious domain constraints (e.g., "commands return at most an ID, never data") — saves multiple clarifying turns
- State block XML tags — crucial for multi-turn coherence without re-reading the full conversation

---

## Execution plan

### Step 1: Categorized audit of all 37+ over-limit skills
For each skill, identify primary bloat category (code templates / state examples / output templates / WRONG-RIGHT examples / decision trees). Estimate lines saved per category. This produces a prioritized trim list.

Tools: `wc -l` + `grep "^## "` across all over-limit skills; read the top 8 not yet read in this session.

### Step 2: Trim all 37+ over-limit skills
Apply the trim protocol above to each. Start with `dotnet-vertical-slice` (most bloated, most code template content). Create new `references/` files as needed.

Critical files to modify (top 15 shown; apply same protocol to the remaining 22+):
- `skills/dotnet-vertical-slice/SKILL.md` (907 → est. ~450 lines)
- `skills/rag-pipeline-python/SKILL.md` (779 → est. ~420 lines)
- `skills/legacy-migration-analyzer/SKILL.md` (775 → est. ~410 lines)
- `skills/spec-coach/SKILL.md` (758 → est. ~400 lines)
- `skills/python-arch-review/SKILL.md` (729 → est. ~400 lines)
- `skills/dotnet-security-review-federal/SKILL.md` (706 → est. ~400 lines)
- `skills/rag-pipeline-dotnet/SKILL.md` (657 → est. ~400 lines)
- `skills/technical-debt-assessor/SKILL.md` (632 → est. ~400 lines)
- `skills/architecture-journal/SKILL.md` (624 → est. ~400 lines)
- `skills/security-review-trainer/SKILL.md` (618 → est. ~400 lines)
- `skills/architecture-review/SKILL.md` (611 → est. ~400 lines) — gold standard, must comply
- `skills/pr-feedback-writer/SKILL.md` (600 → est. ~400 lines)
- `skills/spec-implement/SKILL.md` (590 → est. ~390 lines)
- `skills/refactor-challenger/SKILL.md` (590 → est. ~390 lines)
- `skills/code-review-coach/SKILL.md` (574 → est. ~380 lines)

New reference files likely needed:
- `skills/dotnet-vertical-slice/references/telerik-blazor-templates.md` (move Razor templates)
- `skills/dotnet-vertical-slice/references/scaffold-commands.md` (move bash mkdir scripts)
- Similar new reference files for other scaffolding/pipeline skills

### Step 3: Update AGENTS.md gold standard note
`architecture-review` is the stated gold standard and must comply with the 400-line limit. After trimming it, verify AGENTS.md still accurately describes it as the reference implementation.

### Step 4: Verification
```bash
# Check compliance after trimming
find skills -name "SKILL.md" | xargs wc -l | sort -rn | head -20

# Verify 10 mandatory sections still present in each trimmed skill
for f in skills/*/SKILL.md; do
  count=$(grep -c "^## " "$f")
  echo "$count $f"
done | sort -n | head -20
```

---

## Decisions

1. **Target**: 400-line limit — enforce it strictly
2. **Scope**: All 37+ over-limit skills
3. **Output templates**: Keep a 3–5 line skeleton as a style anchor; remove the verbose filled-out versions
