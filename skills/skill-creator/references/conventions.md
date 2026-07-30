# Skill Creator Conventions

Depth behind the Core Philosophy constraints: the principle set, discipline rules, anti-patterns,
and recovery. The blank 5-section scaffold is in `skill-template.md`; the SCORE rubric in
`scoring-rubric.md`; revision/scorecard output templates in `templates.md`.

## Domain Principles

| # | Principle | Description | Applied As |
|---|-----------|-------------|------------|
| 1 | **Trigger-First Design** | The description is the skill's contract with the dispatch layer. A poor description causes false positives or false negatives. Trigger precision is the most valuable property a skill can have. | Write the description last, after the body. Read it in isolation; if it triggers on scenarios the skill cannot handle, narrow it. |
| 2 | **Negative Example Mandate** | Without WRONG/RIGHT examples an agent drifts toward plausible-but-incorrect behavior under ambiguous inputs. | Every discipline rule (in `conventions.md`) has ≥ 1 WRONG and 1 RIGHT block. Rules without examples are incomplete. |
| 3 | **Scope Discipline** | A skill that does three things does none reliably. One user goal, one workflow, one state machine. | If the workflow has > 3 modes that cannot share one state block, flag for decomposition. |
| 4 | **AI-First Phrasing** | Skills are read by agents, not humans. "Use your best judgment" produces inconsistent behavior; deterministic decision trees produce consistent behavior. | Every conditional has an explicit branch: "If X then Y, else Z." No open-ended conditionals. |
| 5 | **Token Budget Discipline** | A skill that grows without bound overflows the context of the agents that load it. Every always-loaded line is a per-invocation tax. | Target SKILL.md ≤ 200 lines. Depth (tables, templates, recovery) lives in `references/`, loaded on demand. |
| 6 | **State Block Uniqueness** | State blocks use XML-style tags; two skills sharing a tag cannot be distinguished by an agent running both. Collisions are silent bugs. | Before finalizing, grep `skills/` for the tag name; if it exists, rename. |
| 7 | **References Directory Hygiene** | Reference files keep SKILL.md lean by externalizing reusable tables, templates, and catalogs. | Every skill gets `references/` with ≥ 2 descriptively named files (`scoring-rubric.md`, not `refs.md`), each named by a pointer in SKILL.md. |
| 8 | **WRONG/RIGHT Evidence Pattern** | The most effective format for anchoring AI behavior: show the failure mode concretely, name it, follow with the correct behavior. | Use fenced or prose blocks with explicit `WRONG:`/`RIGHT:` labels in `conventions.md`. Never bury them in narrative. |
| 9 | **Interop Declaration** | Agents combine skills and skills reference each other; undeclared interop breaks when names change. | The Integration table names every skill this one references, depends on, or hands off to. No implicit dependencies. |
| 10 | **Currency Maintenance** | A skill written for one version of a tool degrades silently as the tool evolves. Stale skills produce confident wrong answers. | Note version-sensitive content explicitly; add `# VERIFY:` on any API/library/framework behavior that may change. |

## Discipline Rules

- **Always load a gold standard before scaffolding.** Read a lean exemplar
  (`skills/team/cargo-package-scaffold/SKILL.md` or `skills/team/qraspi-skeleton/SKILL.md`) for the
  5-section structure, description format, and state-block style before writing.
  *Wrong:* writing a SKILL.md from memory → wrong section shape, depth inlined, weak trigger.
  *Right:* read the exemplar, note structure + pointer pattern, then scaffold to match.
- **Never change a state block XML tag during revision.** Tags are session identifiers; renaming
  `<old-state>` to `<new-state>` silently loses the state of any in-flight session. To evolve:
  add new fields with defaults, comment deprecated ones — never rename the tag.
- **Every description must have a negative trigger.** A description that only says what the skill
  does triggers in every adjacent scenario. The `Do NOT use when...` clause prevents inappropriate
  invocation. *Right:* "Scaffolds NuGet packages… Do NOT use for internal workspace-only libraries
  or application projects — use dotnet-vertical-slice instead."
- **Push depth to references, don't inline it.** When scaffolding or revising, the Domain Principles
  table, anti-patterns, discipline rules, error recovery, and code/report templates go to
  `references/`. SKILL.md keeps only the 5 sections, with the Critical/High principles folded into
  Non-Negotiable Constraints.

## Anti-Patterns

| # | Anti-Pattern | Why It Fails | Correct Approach |
|---|-------------|-------------|-----------------|
| 1 | **Skipping `references/` creation** | Inline depth bloats the skill and must be maintained in-place | Create `references/` (≥ 2 files) before marking complete |
| 2 | **Inlining the principle/anti-pattern/recovery tables** | Every always-loaded section is a per-invocation token tax; worst on small local models | Move them to `references/conventions.md`; fold Critical/High principles into constraints |
| 3 | **Copying sections verbatim from another skill** | Copied sections carry the source's context and domain assumptions | Read the gold standard for structure only; write every sentence for the target domain |
| 4 | **"helpful/useful/powerful/comprehensive" in the description** | Fillers add no trigger signal; the description is for routing, not evaluation | Domain-specific nouns + action verbs: "scaffolds", "audits", "generates" |
| 5 | **Narrative instead of imperatives** | Narrative is ambiguous to an agent | "Read X. If Y, do Z. Otherwise W." |
| 6 | **Exceeding 200 lines without justification** | Long skills load slowly and often hide redundancy that degrades reliability | Audit for repetition; extract tables/templates to `references/`; target ≤ 200 lines |
| 7 | **Bundling multiple responsibilities** | One skill doing three things is unreliable at all three | > 3 modes or > 1 state machine → split into separate skills |
| 8 | **A description that triggers on everything** | "use when working with .NET" wins every race and fails every task | Narrow to the specific output produced |
| 9 | **Hedging language** | "You could consider…", "It may help to…" gives the agent permission to skip | Declarative: "Do X", "Run Y", "If Z, stop and report" |
| 10 | **Missing Knowledge Base Lookups when grounded-code-mcp applies** | Code generated without authoritative grounding relies on possibly-stale training data | Any code-generating skill in a covered domain includes KB lookups (in references) |

## Error Recovery

**Existing skill has no state block:**
1. Derive the tag from the name: `skills/<name>/SKILL.md` → `<<name>-state>`
2. Grep `skills/` to confirm the tag is unused
3. Add the State Block section (after Workflow); populate fields from the workflow phases
4. Note in the revision summary that it was added (not changed)

**Revision breaks a reference path:**
1. Do not delete the original — restore the original reference path
2. If moved, add a redirect note atop the new file: "# Redirected from references/old-name.md"
3. Update the SKILL.md pointer to the new path
4. Verify: `test -f skills/<name>/references/<new-file>.md && echo PASS`

**Score reveals total < 25/50 (DEPRECATE threshold):**
1. Flag DEPRECATE — do not attempt in-place revision
2. Draft a replacement spec: what the skill should do and what the current one fails to do
3. Present the spec to the user before writing any of the new skill
4. Keep the old skill in place (DEPRECATED header) until the replacement scores ≥ 40

**Skill is still on the legacy 10-section shape:**
1. Keep the title/epigraph, Core Philosophy, Workflow, State Block, and Integration
2. Move Domain Principles, AI Discipline, Anti-Patterns, Error Recovery to `references/conventions.md`
3. Move inline code/report templates to a `references/*-templates.md`; replace Output Templates with pointers
4. Fold the Critical/High principles into Non-Negotiable Constraints; verify SKILL.md ≤ 200 lines
5. Never change the state block XML tag during the migration
