---
name: research-synthesis
description: Multi-source cross-referencing, source credibility scoring, and structured briefing formats. Use when synthesizing research findings from multiple sources into evidence-based deliverables with confidence levels and citations.
---

# Research Synthesis

> "The greatest enemy of knowledge is not ignorance, it is the illusion of knowledge."
> -- Daniel J. Boorstin

> "Science is the belief in the ignorance of experts."
> -- Richard Feynman

## Core Philosophy

Research synthesis is the discipline of combining information from multiple sources into coherent, credible, and actionable knowledge. Raw information becomes knowledge only when it is verified, contextualized, and presented with honest confidence assessments.

**The three pillars:** (1) **Source Assessment** — primary sources (original code, official docs, RFCs) outweigh secondary sources (blog posts, talks), which outweigh tertiary sources (forum answers, AI summaries, marketing materials). Credibility is assessed per-topic, not globally. (2) **Cross-Referencing** — a fact corroborated by independent sources is stronger than any single source. If Source B cites Source A, they are not independent. (3) **Structured Delivery** — how findings are presented determines whether they are actionable. Every deliverable follows a defined format with confidence levels and citations.

**Non-Negotiable Constraints:**
1. Source credibility MUST be assessed per-topic, not assigned globally
2. Cross-referencing MUST happen before synthesis — never synthesize unchecked claims
3. Confidence levels MUST be assigned based on evidence, not intuition
4. Every briefing MUST include a limitations section — perfection signals dishonesty
5. Conflicting sources MUST be surfaced, never silently resolved

## Domain Principles Table

| # | Principle | Description | Priority |
|---|-----------|-------------|----------|
| 1 | **Source Primacy** | Primary sources trump secondary. Secondary trump tertiary. When sources conflict, the credibility hierarchy determines the default position — but the conflict itself is always reported. | Critical |
| 2 | **Recency Weighting** | In fast-moving domains (software, AI, cloud), recency is a credibility factor. A 2-year-old blog post about a framework's API may be obsolete. Check source date against topic's rate of change. | Critical |
| 3 | **Independence Requirement** | Corroboration only counts from independent sources. If Source B cites Source A, they are not independent — finding the same claim in both is not cross-referencing, it is counting the same source twice. | Critical |
| 4 | **Confidence Calibration** | Confidence levels map to specific evidence thresholds, not to how confident the researcher feels. HIGH requires 2+ independent credible sources. | Critical |
| 5 | **Structured Output** | Every research deliverable follows a defined format chosen at scope time based on audience and purpose. Ad-hoc formatting signals ad-hoc thinking. | High |
| 6 | **Gap Honesty** | What you did NOT find is as important as what you did find. Every briefing must document known gaps, searched-but-empty sources, and unanswered questions. | High |
| 7 | **Inference Transparency** | When connecting facts to reach a conclusion, the reasoning chain must be visible. The reader must be able to see which facts led to which conclusion. | High |
| 8 | **Conflict as Signal** | Contradictory sources are not a problem to solve — they are information to report. A contradiction may indicate version differences, scope differences, or genuine field disagreement. | High |
| 9 | **Audience Awareness** | An executive summary for a manager, a technical deep-dive for an engineer, a comparison matrix for a decision-maker. Format serves the reader. | Medium |
| 10 | **Reproducibility** | Another researcher following the same source list should reach the same conclusions. Unstated assumptions or invisible reasoning are not reproducible. | Medium |

## Workflow

The synthesis pipeline flows: **ASSESS → CROSS-REFERENCE → SCORE → ORGANIZE → FORMAT → REVIEW**.

### Step 1: ASSESS — Evaluate Source Quality

For each source, determine: source type (primary/secondary/tertiary), author authority (domain expert/practitioner/unknown), date (current/recent/dated/unknown), cross-referenceability, and bias indicators (marketing language, vendor affiliation, self-promotion).

**Credibility scores:** 5 = primary source, domain authority, current, no bias | 4 = primary or authoritative secondary, recent, minimal bias | 3 = secondary, practitioner author, reasonably current | 2 = secondary/tertiary, unknown author, or dated | 1 = tertiary, undated, anonymous, or significant bias indicators

```markdown
| Source | Type | Authority | Date | Bias Risk | Score |
|--------|------|-----------|------|-----------|-------|
| [ref]  | P/S/T | H/M/L | [date] | none/low/high | 1–5 |
```

Full credibility framework: `references/source-credibility.md`

### Step 2: CROSS-REFERENCE — Verify Across Sources

For each key finding, check whether independent sources corroborate, contradict, or are silent. "Silent" means a source that could have mentioned this but did not — which is itself information. Two sources citing each other count as ONE source.

```markdown
### Cross-Reference Matrix

| Finding | Source 1 | Source 2 | Source 3 | Corroboration | Notes |
|---------|----------|----------|----------|---------------|-------|
| [claim] | Supports (P, 5) | Supports (S, 3) | Silent | Strong | Two independent sources |
| [claim] | Supports (P, 4) | Contradicts (S, 3) | Silent | Conflicted | Version difference? |
| [claim] | Supports (S, 2) | N/A | N/A | Weak | Single source, unverified |
```

### Step 3: SCORE — Assign Confidence Levels

**HIGH**: 2+ independent sources corroborate, at least one primary, no contradicting sources, average score ≥ 3.

**MEDIUM**: Single credible primary source (score 4–5), OR 2+ secondary sources corroborate (average ≥ 3), no direct contradictions.

**LOW**: Single secondary source (score 2–3), OR contradicting sources with no clear resolution, OR significantly dated primary source.

**UNVERIFIED**: Single tertiary source only, OR no cross-reference possible, OR all sources have significant bias indicators.

### Step 4: ORGANIZE — Structure Findings

Group findings by sub-question. Within each group, order: High Confidence → Medium Confidence → Low/Unverified → Conflicts → Gaps. Document what was searched for but not found.

### Step 5: FORMAT — Choose and Apply Briefing Template

| Situation | Format |
|-----------|--------|
| Decision-maker needs a quick answer | Executive Summary |
| Engineer needs implementation details | Technical Deep-Dive |
| Comparing options or technologies | Comparison Matrix |
| Recommending a course of action | Decision Brief |
| Surveying a broad topic area | Literature Review |

Full templates: `references/briefing-formats.md`

### Step 6: REVIEW — Final Quality Check

Before delivery, verify: every claim has an inline citation, confidence levels are assigned to all findings, facts and inferences are clearly distinguished, conflicts are surfaced (not hidden), limitations section is present and honest, the original research question is answered.

## State Block Format

```
<research-state>
phase: ASSESS | CROSS-REFERENCE | SCORE | ORGANIZE | FORMAT | REVIEW
sources_assessed: [N of M]
cross_references_complete: [N of M findings]
confidence_distribution: [high: N, medium: N, low: N, unverified: N]
conflicts_found: [N]
gaps_identified: [N]
briefing_format: [chosen format]
last_action: [what was just done]
next_action: [what should happen next]
</research-state>
```

## Output Templates

```markdown
## Research Briefing: [Topic]
**Date**: [date] | **Format**: [type] | **Overall Confidence**: [high/medium/low]

[Formatted briefing content per chosen template]

### Source List
| # | Source | Type | Score | Date | Used For |

### Limitations
- [what was not investigated and why]
- [sources that could not be accessed]
- [time-sensitive findings that may change]

### Suggested Follow-Up
- [topics warranting deeper investigation]
```

Full templates (Source Assessment Report, Cross-Reference Summary, Executive Summary, Technical Deep-Dive, Comparison Matrix, Decision Brief, Literature Review): `references/briefing-formats.md`

## AI Discipline Rules

**Never synthesize without cross-referencing.** Cross-referencing is not optional. Skipping it produces research theater — output that looks authoritative but has no more integrity than a single search. Every key finding must be checked against at least one other source. Single-source findings must be flagged as such.

**Confidence levels are evidence thresholds, not feelings.** HIGH confidence requires 2+ independent credible sources corroborating. MEDIUM requires a single credible primary source or 2+ corroborating secondary sources. "I'm fairly sure this is correct" maps to MEDIUM or LOW, never HIGH. Cite the sources that earn the confidence level.

**Limitations are mandatory.** A briefing with no limitations is either dishonest or superficial. Every briefing must include sources that could not be accessed, topics out of scope but adjacent, findings that are time-sensitive, potential biases in source selection, and questions that emerged but were not pursued.

**Format serves the reader.** An executive summary for an engineer wastes their time. A technical deep-dive for a decision-maker wastes theirs. Choose the format at scope time and follow it consistently.

## Anti-Patterns Table

| Anti-Pattern | Why It Fails | Correct Approach |
|--------------|-------------|------------------|
| **Single-source synthesis** | Presenting one source's claims as verified findings | Cross-reference against independent sources; flag single-source claims |
| **Citation laundering** | Citing Source B which cites Source A, claiming two sources | Trace claims to origin; count dependent sources as one |
| **Confidence inflation** | Assigning HIGH confidence based on plausibility, not evidence | Use evidence thresholds: HIGH requires 2+ independent credible sources |
| **Silent conflict resolution** | Choosing one source over another without disclosing the conflict | Present both positions, assess credibility, let the reader see the disagreement |
| **Gap hiding** | Omitting unanswered questions to make the briefing look complete | Include a limitations section; list what was searched but not found |
| **Recency bias** | Favoring recent sources regardless of authority or accuracy | Assess recency as ONE factor alongside type, authority, and independence |
| **Authority worship** | Accepting claims from authoritative sources without verification | Even primary sources can be wrong; cross-reference everything |
| **Format neglect** | Dumping findings in a wall of text with no structure | Choose an appropriate briefing format at scope time |

## Error Recovery

**All sources agree but seem wrong**: Check if all "agreeing" sources actually trace to the same origin. Search specifically for contradicting sources and criticism. Check the date — consensus may reflect an outdated understanding. If evidence genuinely supports an unexpected conclusion, report it and note the surprise. Never override evidence with intuition.

**Source credibility is ambiguous**: Check the author's other work for domain expertise. Check if other credible sources cite this source. Check the publication venue (peer-reviewed vs. self-published). Default to a conservative score (2–3). Flag the ambiguity and weight findings as MEDIUM confidence at best.

**Research question is too broad**: Decompose into sub-questions. Prioritize by importance to the original question. Research the highest-priority sub-questions thoroughly. Note remaining sub-questions as "suggested follow-up." Deliver a partial briefing with clear scope boundaries. Do NOT try to cover everything superficially.

**No sources found for a sub-question**: Verify search terms (try synonyms and alternative phrasings). Check adjacent domains. Check if the question assumes something false (XY problem). Mark the sub-question as UNRESOLVED and document exactly what was searched and where. Do NOT speculate to fill the gap.

## Integration with Other Skills

- **`rag-pipeline-python`** — When research involves large document corpora, use this skill to build a searchable knowledge base. Cross-reference retrieved passages against direct source consultation.
- **`research-agent`** — This skill is designed to be loaded by the `research-agent`. The agent handles SCOPE and GATHER; this skill provides frameworks for CROSS-REFERENCE, SYNTHESIZE, and DELIVER.

Reference files: `references/source-credibility.md` (complete credibility scoring framework, recency weighting, authority evaluation) | `references/briefing-formats.md` (five structured output formats with templates and audience guidance)
