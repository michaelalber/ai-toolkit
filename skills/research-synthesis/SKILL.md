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

Research synthesis is the discipline of combining information from multiple sources into coherent, credible, and actionable knowledge. Raw information is not knowledge -- it becomes knowledge only when it is verified, contextualized, and presented with honest confidence assessments. This skill provides the frameworks for doing that rigorously.

**The three pillars of research synthesis:**

1. **Source Assessment** -- Not all sources are equal. A primary source (original code, official documentation, RFC) carries more weight than a blog post summarizing someone else's findings. Credibility must be assessed per-topic, not globally -- a source may be authoritative on one subject and unreliable on another.

2. **Cross-Referencing** -- A fact corroborated by independent sources is stronger than a fact from a single source, regardless of that source's general credibility. Cross-referencing is the mechanism that transforms individual claims into verified findings.

3. **Structured Delivery** -- How findings are presented determines whether they are actionable. A wall of text with no confidence indicators, no citations, and no structure is research theater -- it looks like knowledge but cannot be acted upon with confidence.

**The credibility hierarchy:**
```
Primary Sources (highest credibility)
  |-- Source code, configuration files, test suites
  |-- Official documentation, RFCs, specifications
  |-- Commit history, changelogs, release notes
  |-- Author statements, design documents
  |
Secondary Sources (moderate credibility)
  |-- Technical blog posts by practitioners
  |-- Conference talks and presentations
  |-- Peer-reviewed analysis and benchmarks
  |-- Documentation aggregators (wikis, guides)
  |
Tertiary Sources (lowest credibility)
  |-- Forum answers (Stack Overflow, Reddit)
  |-- AI-generated summaries
  |-- Undated or unattributed content
  |-- Marketing materials
```

**Non-Negotiable Constraints:**
1. Source credibility MUST be assessed per-topic, not assigned globally
2. Cross-referencing MUST happen before synthesis -- never synthesize unchecked claims
3. Confidence levels MUST be assigned based on evidence, not intuition
4. Every briefing MUST include a limitations section -- perfection signals dishonesty
5. Conflicting sources MUST be surfaced, never silently resolved

## Domain Principles Table

| # | Principle | Description | Priority |
|---|-----------|-------------|----------|
| 1 | **Source Primacy** | Primary sources trump secondary sources. Secondary sources trump tertiary sources. When sources conflict, credibility hierarchy determines the default position, but the conflict itself is always reported. | Critical |
| 2 | **Recency Weighting** | In fast-moving domains (software, AI, cloud), recency is a credibility factor. A 2-year-old blog post about a framework's API may be obsolete. Always check the source date against the topic's rate of change. | Critical |
| 3 | **Independence Requirement** | Corroboration only counts from independent sources. If Source B cites Source A, they are not independent -- finding the same claim in both is not cross-referencing, it is counting the same source twice. | Critical |
| 4 | **Confidence Calibration** | Confidence levels must map to specific evidence thresholds, not to how confident the researcher "feels." High confidence requires 2+ independent credible sources. Anything less is medium or low. | Critical |
| 5 | **Structured Output** | Every research deliverable follows a defined format. The format is chosen at scope time based on the audience and purpose. Ad-hoc formatting signals ad-hoc thinking. | High |
| 6 | **Gap Honesty** | What you did NOT find is as important as what you did find. Every briefing must document known gaps, searched-but-empty sources, and questions that remain unanswered. | High |
| 7 | **Inference Transparency** | When connecting facts to reach a conclusion, the reasoning chain must be visible. The reader must be able to see which facts led to which conclusion, and decide whether the inference is warranted. | High |
| 8 | **Conflict as Signal** | Contradictory sources are not a problem to solve -- they are information to report. A contradiction may indicate version differences, scope differences, or genuine disagreement in the field. All of these are valuable findings. | High |
| 9 | **Audience Awareness** | The same research may need different briefing formats for different audiences. An executive summary for a manager, a technical deep-dive for an engineer, a comparison matrix for a decision-maker. Format serves the reader. | Medium |
| 10 | **Reproducibility** | Another researcher following the same source list should reach the same conclusions. If the synthesis depends on unstated assumptions or invisible reasoning, it is not reproducible. | Medium |

## Workflow

### Research Synthesis Pipeline

```
+-----------------------------------------------------------------------+
|                    RESEARCH SYNTHESIS WORKFLOW                          |
|                                                                       |
|  +--------+   +---------+   +-----------+   +----------+             |
|  |1.ASSESS|-->|2.CROSS- |-->|3.SCORE    |-->|4.ORGANIZE|             |
|  | SOURCES|   |REFERENCE|   |CONFIDENCE |   | FINDINGS |             |
|  +--------+   +---------+   +-----------+   +----------+             |
|                                                   |                   |
|                                                   v                   |
|                                             +-----------+             |
|                                             |5.FORMAT   |             |
|                                             | BRIEFING  |             |
|                                             +-----------+             |
|                                                   |                   |
|                                                   v                   |
|                                             +-----------+             |
|                                             |6.REVIEW & |             |
|                                             | DELIVER   |             |
|                                             +-----------+             |
+-----------------------------------------------------------------------+
```

### Step 1: ASSESS -- Evaluate Source Quality

For each source gathered during research, apply the credibility scoring framework. See [Source Credibility Reference](references/source-credibility.md) for the complete framework.

**Quick Assessment Checklist:**

```
For each source, determine:
[ ] Source type: primary / secondary / tertiary
[ ] Author authority: domain expert / practitioner / unknown
[ ] Date: current / recent / dated / unknown
[ ] Cross-referenceability: can findings be verified elsewhere?
[ ] Bias indicators: marketing language / vendor affiliation / self-promotion
```

**Source Assessment Record:**

```markdown
| Source | Type | Authority | Date | Bias Risk | Credibility Score |
|--------|------|-----------|------|-----------|-------------------|
| [ref]  | [P/S/T] | [H/M/L] | [date] | [none/low/high] | [1-5] |
```

Credibility scores:
- **5**: Primary source, domain authority, current, no bias
- **4**: Primary source or authoritative secondary, recent, minimal bias
- **3**: Secondary source, practitioner author, reasonably current
- **2**: Secondary/tertiary, unknown author, or somewhat dated
- **1**: Tertiary, undated, anonymous, or significant bias indicators

### Step 2: CROSS-REFERENCE -- Verify Across Sources

For each key finding, check whether independent sources corroborate, contradict, or are silent.

```markdown
### Cross-Reference Matrix

| Finding | Source 1 | Source 2 | Source 3 | Corroboration | Notes |
|---------|----------|----------|----------|---------------|-------|
| [claim] | Supports (P, 5) | Supports (S, 3) | Silent | Strong | Two independent sources |
| [claim] | Supports (P, 4) | Contradicts (S, 3) | Silent | Conflicted | Version difference? |
| [claim] | Supports (S, 2) | N/A | N/A | Weak | Single source, unverified |
```

**Cross-Reference Rules:**
- Two sources that cite each other count as ONE source, not two
- "Silent" means a source that could have mentioned this but did not -- which is itself information
- Contradictions require explicit investigation before synthesis
- A single credible primary source outweighs multiple tertiary sources

### Step 3: SCORE -- Assign Confidence Levels

Based on the cross-reference results, assign confidence levels to each finding.

```
HIGH CONFIDENCE:
- 2+ independent sources corroborate
- At least one primary source
- No contradicting sources
- Source credibility scores average >= 3

MEDIUM CONFIDENCE:
- Single credible primary source (score 4-5)
- OR 2+ secondary sources corroborate (average score >= 3)
- No direct contradictions (silence is acceptable)

LOW CONFIDENCE:
- Single secondary source (score 2-3)
- OR contradicting sources with no clear resolution
- OR primary source that is significantly dated

UNVERIFIED:
- Single tertiary source only
- OR no cross-reference possible
- OR all sources have significant bias indicators
```

### Step 4: ORGANIZE -- Structure Findings

Group findings by sub-question and order by confidence level within each group.

```markdown
### Sub-Question 1: [question]

**High Confidence Findings:**
- [finding] [Source 1, Source 3] -- Confidence: HIGH
- [finding] [Source 2, Source 4] -- Confidence: HIGH

**Medium Confidence Findings:**
- [finding] [Source 1] -- Confidence: MEDIUM (single primary source)

**Low Confidence / Unverified:**
- [finding] [Source 5] -- Confidence: LOW (single dated secondary source)

**Conflicts:**
- [topic]: Source 1 states [X], Source 3 states [Y]. Assessment: [analysis]

**Gaps:**
- [what was searched for but not found]
```

### Step 5: FORMAT -- Choose and Apply Briefing Template

Select the appropriate briefing format based on the research purpose and audience. See [Briefing Formats Reference](references/briefing-formats.md) for complete templates.

**Format Selection Guide:**

| Situation | Format | Why |
|-----------|--------|-----|
| Decision-maker needs a quick answer | Executive Summary | Prioritizes conclusion and recommendation |
| Engineer needs implementation details | Technical Deep-Dive | Prioritizes evidence and specifics |
| Comparing options or technologies | Comparison Matrix | Prioritizes side-by-side evaluation |
| Recommending a course of action | Decision Brief | Prioritizes options, tradeoffs, recommendation |
| Surveying a broad topic area | Literature Review | Prioritizes coverage and knowledge landscape |

### Step 6: REVIEW -- Final Quality Check

Before delivery, verify the briefing against quality criteria:

```
DELIVERY CHECKLIST:
[ ] Every claim has an inline citation
[ ] Every citation appears in the source list
[ ] Confidence levels are assigned to all findings
[ ] Facts and inferences are clearly distinguished
[ ] Conflicts are surfaced, not hidden
[ ] Limitations section is present and honest
[ ] Briefing follows the chosen format template
[ ] The original research question is answered
```

## State Block Format

Maintain synthesis state across conversation turns:

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

### Source Assessment Report

```markdown
## Source Assessment

| # | Source | Type | Authority | Recency | Bias Risk | Score |
|---|--------|------|-----------|---------|-----------|-------|
| 1 | [ref]  | Primary | High | Current | None | 5 |
| 2 | [ref]  | Secondary | Medium | Recent | Low | 3 |
| 3 | [ref]  | Tertiary | Unknown | Dated | Medium | 1 |

**Assessment Notes:**
- [Source 1] is the authoritative reference because [reason]
- [Source 3] should be used cautiously because [reason]
- [Source 2] and [Source 4] cite the same upstream source; treat as single source for cross-referencing
```

### Cross-Reference Summary

```markdown
## Cross-Reference Results

**Corroborated Findings** (2+ independent sources):
- [finding] -- Sources: [list], Confidence: HIGH

**Single-Source Findings** (credible but unverified):
- [finding] -- Source: [ref], Confidence: MEDIUM

**Conflicting Findings** (sources disagree):
- [topic]: [Source A position] vs [Source B position]
  - Assessment: [which has stronger evidence and why]
  - Confidence: LOW (pending resolution)

**Knowledge Gaps** (searched but not found):
- [topic] -- Searched: [sources checked], Result: no relevant information found
```

### Synthesis Deliverable

```markdown
## Research Briefing: [Topic]

**Date**: [date]
**Format**: [executive summary | deep-dive | comparison | decision brief | literature review]
**Overall Confidence**: [high | medium | low]

---

[Formatted briefing content per chosen template]

---

### Source List

| # | Source | Type | Credibility | Date | Used For |
|---|--------|------|------------|------|----------|
| 1 | [ref]  | [type] | [score/5] | [date] | [which findings] |

### Limitations

- [limitation 1: what was not investigated and why]
- [limitation 2: sources that could not be accessed]
- [limitation 3: time-sensitive findings that may change]

### Suggested Follow-Up

- [topic that warrants deeper investigation]
- [question that emerged but was out of scope]
```

## AI Discipline Rules

### CRITICAL: Never Synthesize Without Cross-Referencing

Cross-referencing is not optional. It is the difference between "I found this claim" and "I verified this claim." Skipping cross-referencing produces research theater -- output that looks authoritative but has no more integrity than a single Google search.

```
MANDATORY before synthesis:
1. Every key finding has been checked against at least one other source
2. Single-source findings are flagged as such
3. Contradictions are identified and recorded
4. Confidence levels are assigned based on evidence, not intuition

If cross-referencing was skipped -> the synthesis is unreliable.
```

### CRITICAL: Confidence Levels Are Not Feelings

"I feel pretty confident about this" is not a confidence level. Confidence levels map to specific evidence thresholds:

```
WRONG: "I'm fairly sure this is correct." -> Confidence: HIGH
RIGHT: "Corroborated by official documentation [1] and
        independent benchmark [3]." -> Confidence: HIGH

WRONG: "This seems right but I'm not sure." -> Confidence: MEDIUM
RIGHT: "Single primary source [2], no contradicting sources,
        but no independent corroboration." -> Confidence: MEDIUM
```

### CRITICAL: Limitations Are Mandatory

Every briefing must include a limitations section. A briefing with no limitations is either dishonest or superficial. Real research always has boundaries, gaps, and caveats. Reporting them is a sign of rigor, not weakness.

```
MANDATORY limitations to check:
1. Sources that could not be accessed (paywalled, internal, etc.)
2. Topics that were out of scope but adjacent
3. Findings that are time-sensitive or may change
4. Potential biases in the source selection
5. Questions that emerged but were not pursued
```

### IMPORTANT: Format Serves the Reader

The briefing format is not a bureaucratic requirement -- it is a communication tool. An executive summary for an engineer wastes their time. A technical deep-dive for a decision-maker wastes theirs. Choose the format that serves the reader, and follow it consistently.

## Anti-Patterns Table

| Anti-Pattern | Why It Fails | Correct Approach |
|--------------|-------------|------------------|
| **Single-source synthesis** | Presenting one source's claims as verified findings | Cross-reference against independent sources; flag single-source claims |
| **Citation laundering** | Citing Source B which cites Source A, claiming two sources | Trace claims to their origin; count dependent sources as one |
| **Confidence inflation** | Assigning HIGH confidence based on plausibility, not evidence | Use evidence thresholds: HIGH requires 2+ independent credible sources |
| **Silent conflict resolution** | Choosing one source over another without disclosing the conflict | Present both positions, assess credibility, let the reader see the disagreement |
| **Gap hiding** | Omitting unanswered questions to make the briefing look complete | Include a limitations section; list what was searched but not found |
| **Recency bias** | Favoring recent sources regardless of authority or accuracy | Assess recency as ONE factor alongside type, authority, and independence |
| **Authority worship** | Accepting claims from authoritative sources without verification | Even primary sources can be wrong; cross-reference everything |
| **Format neglect** | Dumping findings in a wall of text with no structure | Choose an appropriate briefing format at scope time; follow the template |

## Error Recovery

### All Sources Agree But Seem Wrong

```
Problem: Cross-referencing shows agreement, but the consensus conflicts
  with your domain knowledge or seems implausible
Actions:
1. Check if all "agreeing" sources actually trace to the same origin
2. Look for contradicting sources specifically (search for criticism, alternatives)
3. Check the date -- consensus may reflect an outdated understanding
4. If the evidence genuinely supports an unexpected conclusion, report it
5. Note the surprise in the briefing -- the reader may share the concern
6. DO NOT override evidence with intuition
```

### Source Credibility Is Ambiguous

```
Problem: Cannot determine if a source is credible for this specific topic
Actions:
1. Check the author's other work -- do they have domain expertise?
2. Check if other credible sources cite this source
3. Check the publication venue -- peer-reviewed vs. self-published
4. Default to a conservative credibility score (2-3)
5. Flag the ambiguity in the source assessment
6. Weight findings from ambiguous sources as MEDIUM confidence at best
```

### Research Question Is Too Broad

```
Problem: The question cannot be answered in a single research session
Actions:
1. Decompose into sub-questions
2. Prioritize sub-questions by importance to the original question
3. Research the highest-priority sub-questions thoroughly
4. Note remaining sub-questions as "suggested follow-up"
5. Deliver a partial briefing with clear scope boundaries
6. DO NOT try to cover everything superficially
```

### No Sources Found for a Sub-Question

```
Problem: Exhaustive searching yields no relevant sources
Actions:
1. Verify search terms -- try synonyms, alternative phrasings
2. Check adjacent domains -- the answer may exist in a related field
3. Check if the question assumes something false (XY problem)
4. Mark the sub-question as UNRESOLVED in the briefing
5. Document exactly what was searched and where
6. DO NOT speculate to fill the gap
```

## Integration with Other Skills

### RAG Pipeline (`rag-pipeline-python`)

When research involves large document corpora (technical documentation sets, codebases, paper collections), use the `rag-pipeline-python` skill to build a searchable knowledge base:

- Ingest research documents into a vector store for semantic search
- Use retrieval to find relevant passages across large corpora
- Cross-reference retrieved passages against direct source consultation
- Evaluate retrieval quality to ensure research completeness

### Research Agent (`research-agent`)

This skill is designed to be loaded by the `research-agent` agent. The agent handles the SCOPE and GATHER phases; this skill provides the frameworks for CROSS-REFERENCE, SYNTHESIZE, and DELIVER.

## Reference Files

- [Source Credibility](references/source-credibility.md) -- Complete source credibility scoring framework with assessment criteria, recency weighting, authority evaluation, and cross-reference validation
- [Briefing Formats](references/briefing-formats.md) -- Five structured output formats with templates, usage guidelines, and audience-specific formatting
