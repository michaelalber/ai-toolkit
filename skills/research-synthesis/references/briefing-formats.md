# Research Briefing Formats

## Overview

The format of a research deliverable determines whether the findings are actionable. The same research can be presented as a one-page executive summary for a time-constrained decision-maker, a multi-page technical deep-dive for an implementing engineer, or a comparison matrix for someone evaluating options. The format is not cosmetic -- it is a communication design choice that should be made at research scope time.

**Format Selection Principle:** Ask "Who will read this, and what will they do with it?" before choosing a format. If the reader is going to make a yes/no decision, they need a decision brief, not a literature review. If the reader is going to implement something, they need a technical deep-dive, not an executive summary.

---

## Format 1: Executive Summary

### When to Use

- The reader is a decision-maker or manager who needs the bottom line
- Time is constrained -- the reader has 2-5 minutes
- The research question has a clear answer (or a clear "we cannot determine yet")
- The reader will delegate the details to someone else

### When NOT to Use

- The reader needs to implement something based on the findings
- The topic has significant nuance that cannot be compressed without distortion
- Multiple viable options exist and the reader must choose between them (use Decision Brief instead)

### Structure Template

```markdown
## Executive Summary: [Topic]

**Date**: [date]
**Research Question**: [one-sentence question]
**Overall Confidence**: [HIGH | MEDIUM | LOW]

### Bottom Line

[1-3 sentences answering the research question directly. Lead with the
conclusion, not the process. If confidence is LOW or MEDIUM, state that
here.]

### Key Findings

1. **[Finding 1]** [Confidence: HIGH]
   [1-2 sentences with inline citation]

2. **[Finding 2]** [Confidence: MEDIUM]
   [1-2 sentences with inline citation]

3. **[Finding 3]** [Confidence: HIGH]
   [1-2 sentences with inline citation]

### Risks and Caveats

- [Risk or caveat 1]
- [Risk or caveat 2]

### Recommendation

[1-2 sentences: what should the reader do based on these findings?]

### Sources

[Numbered source list -- keep to essential sources only]
```

### Writing Guidelines

- Lead with the answer, not the journey
- Maximum 1 page (roughly 400-500 words)
- No more than 5 key findings
- Every finding has a confidence level
- Recommendation is actionable and specific
- If the answer is "we do not know yet," say so in the bottom line

---

## Format 2: Technical Deep-Dive

### When to Use

- The reader is an engineer who will act on the findings
- The reader needs enough detail to implement, configure, or debug
- The topic requires showing evidence, code examples, or configuration details
- Accuracy and completeness matter more than brevity

### When NOT to Use

- The reader does not have technical context for the topic
- A high-level answer is sufficient
- The research covers multiple unrelated topics (split into multiple deep-dives)

### Structure Template

```markdown
## Technical Deep-Dive: [Topic]

**Date**: [date]
**Research Question**: [precise question]
**Overall Confidence**: [HIGH | MEDIUM | LOW]
**Scope**: [what is covered and what is excluded]

### Summary

[3-5 sentence summary for readers who may not read the full document.
Include the key conclusion and confidence level.]

### Background

[Context the reader needs to understand the findings. What is the
technology/system? What problem does it solve? What is the current state?]

### Findings

#### [Sub-Question 1]

**Confidence**: [level]

[Detailed findings with evidence. Include code examples, configuration
snippets, benchmark data, or architecture diagrams as appropriate.]

**Evidence:**
- [Source 1] states: "[relevant quote or data]"
- [Source 2] corroborates: "[relevant quote or data]"

**Analysis:**
[Your reasoning connecting the evidence to the conclusion. Make the
inference chain visible.]

#### [Sub-Question 2]

**Confidence**: [level]

[Same structure as above]

#### [Sub-Question N]

...

### Conflicts and Uncertainties

[Any points where sources disagree or where confidence is below HIGH.
Present both sides of conflicts.]

| Topic | Position A | Position B | Assessment |
|-------|-----------|-----------|------------|
| [topic] | [source] says [X] | [source] says [Y] | [which is stronger and why] |

### Practical Implications

[What does this mean for the reader? How should they apply these findings?
Include specific, actionable guidance.]

- **Do**: [specific action]
- **Do Not**: [specific anti-pattern to avoid]
- **Watch For**: [risks or edge cases]

### Limitations

- [What was not investigated]
- [Sources that could not be accessed]
- [Time-sensitive findings that may change]
- [Assumptions made during research]

### Complete Source List

| # | Source | Type | Credibility | Date | Relevance |
|---|--------|------|------------|------|-----------|
| 1 | [ref]  | [P/S/T] | [1-5] | [date] | [which findings] |

### Suggested Follow-Up

- [Topic that warrants deeper investigation]
- [Question that emerged but was out of scope]
```

### Writing Guidelines

- Be thorough but organized -- use clear headings and sub-sections
- Show evidence, not just conclusions
- Include code examples or configuration snippets where relevant
- Make the reasoning chain visible (Source says X, therefore Y)
- No length limit, but every section should earn its place
- Separate facts from inferences explicitly

---

## Format 3: Comparison Matrix

### When to Use

- The reader is evaluating 2-5 options (technologies, approaches, vendors)
- The evaluation criteria are known or can be defined
- A side-by-side view will aid decision-making
- The reader wants to see tradeoffs, not just a winner

### When NOT to Use

- Only one option is being investigated (use Deep-Dive instead)
- The options are not comparable on the same criteria
- The reader needs a recommendation, not a comparison (use Decision Brief instead)

### Structure Template

```markdown
## Comparison: [Topic]

**Date**: [date]
**Question**: [what is being compared and why]
**Options Evaluated**: [Option A], [Option B], [Option C]
**Overall Confidence**: [level]

### Evaluation Criteria

| Criterion | Weight | Why It Matters |
|-----------|--------|----------------|
| [criterion 1] | Critical | [explanation] |
| [criterion 2] | High | [explanation] |
| [criterion 3] | Medium | [explanation] |
| [criterion 4] | Low | [explanation] |

### Comparison Matrix

| Criterion | [Option A] | [Option B] | [Option C] | Notes |
|-----------|-----------|-----------|-----------|-------|
| [criterion 1] | [rating + evidence] | [rating + evidence] | [rating + evidence] | [key differentiator] |
| [criterion 2] | [rating + evidence] | [rating + evidence] | [rating + evidence] | [key differentiator] |
| [criterion 3] | [rating + evidence] | [rating + evidence] | [rating + evidence] | [key differentiator] |
| [criterion 4] | [rating + evidence] | [rating + evidence] | [rating + evidence] | [key differentiator] |

**Rating Scale**: Strong / Adequate / Weak / Unknown

### Option Profiles

#### [Option A]

**Best For**: [scenario where this option excels]
**Strengths**: [1-3 bullet points with citations]
**Weaknesses**: [1-3 bullet points with citations]
**Confidence in Assessment**: [level]

#### [Option B]

[Same structure]

#### [Option C]

[Same structure]

### Tradeoff Analysis

[Which tradeoffs matter most? What does the reader gain and lose with each option?]

- Choosing [A] over [B] gains [X] but loses [Y]
- Choosing [B] over [A] gains [Y] but loses [X]
- [C] is the middle ground on [criteria], but weaker on [criteria]

### Gaps in Comparison

- [criterion] could not be compared because [reason]
- [Option X] lacks data on [criterion] -- [what was searched]
- Confidence on [Option Y] is lower because [reason]

### Sources

| # | Source | Type | Credibility | Date | Relevant To |
|---|--------|------|------------|------|-------------|
| 1 | [ref]  | [type] | [score] | [date] | [which option/criterion] |
```

### Writing Guidelines

- Define criteria before comparing -- do not let the comparison drive the criteria
- Rate each cell with evidence, not just opinion
- Use consistent rating scale across all options
- Show tradeoffs, not just scores -- "best" depends on context
- Acknowledge gaps in the comparison honestly
- Do NOT declare a winner unless asked for a recommendation (use Decision Brief for that)

---

## Format 4: Decision Brief

### When to Use

- The reader must make a specific decision
- There are defined options with different tradeoffs
- The research should culminate in a recommendation
- The reader wants guidance, not just information

### When NOT to Use

- The research is exploratory (no decision pending)
- The reader wants to evaluate options themselves (use Comparison Matrix)
- The topic is informational, not decisional (use Executive Summary or Deep-Dive)

### Structure Template

```markdown
## Decision Brief: [Decision Statement]

**Date**: [date]
**Decision Required**: [what specifically must be decided]
**Deadline**: [if applicable]
**Stakeholders**: [who is affected]
**Overall Confidence**: [level]

### Context

[Why does this decision need to be made now? What is the current state?
What triggered this investigation?]

### Options

#### Option 1: [Name]

**Description**: [what this option entails]
**Pros**:
- [pro with citation and confidence]
- [pro with citation and confidence]
**Cons**:
- [con with citation and confidence]
- [con with citation and confidence]
**Estimated Effort**: [if applicable]
**Estimated Risk**: [low | medium | high]

#### Option 2: [Name]

[Same structure]

#### Option 3: [Name / "Do Nothing"]

[Same structure -- always include a "do nothing" or "status quo" option]

### Recommendation

**Recommended Option**: [Option N]
**Confidence in Recommendation**: [level]

**Rationale**:
[Why this option? Connect the recommendation to the evaluation criteria
and evidence. Make the reasoning chain explicit.]

**Key Assumption**:
[What must be true for this recommendation to be correct? If this
assumption is wrong, which option should be reconsidered?]

### Risks of Recommended Option

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| [risk 1] | [H/M/L] | [H/M/L] | [how to mitigate] |
| [risk 2] | [H/M/L] | [H/M/L] | [how to mitigate] |

### Dissenting Considerations

[Arguments against the recommendation. What would make someone choose
a different option? This section prevents groupthink and shows the
recommendation was reached through balanced analysis.]

### Limitations

- [What was not investigated]
- [Assumptions that were not validated]
- [Time-sensitive factors]

### Sources

[Source list with credibility scores]
```

### Writing Guidelines

- State the decision clearly at the top -- what exactly must be decided?
- Always include a "do nothing" option for comparison
- Recommendation must be explicit -- do not hedge to the point of non-commitment
- State the key assumption -- what would change the recommendation?
- Include dissenting considerations -- this shows rigor, not weakness
- Risks should be specific and actionable, not generic

---

## Format 5: Literature Review

### When to Use

- The reader wants to understand the landscape of a topic
- The research is exploratory -- mapping what is known, not answering a specific question
- Multiple perspectives or approaches exist in the field
- The reader will use this as a foundation for further investigation

### When NOT to Use

- A specific question needs a direct answer (use Executive Summary or Deep-Dive)
- A decision must be made (use Decision Brief)
- Options are being compared (use Comparison Matrix)

### Structure Template

```markdown
## Literature Review: [Topic]

**Date**: [date]
**Scope**: [what is covered and what is excluded]
**Sources Surveyed**: [number and types]
**Overall Assessment**: [is the topic well-documented, emerging, or sparse?]

### Introduction

[What is this topic? Why does it matter? What is the current state of
knowledge? Frame the landscape the reader is about to explore.]

### Themes

#### Theme 1: [Name]

**Prevalence in Sources**: [how many sources discuss this]
**Key Positions**:
- [Position A, held by Source 1, Source 3]: [summary]
- [Position B, held by Source 2]: [summary]
- [Emerging view, held by Source 5]: [summary]

**Assessment**: [is there consensus? Is the topic settled or contested?]

#### Theme 2: [Name]

[Same structure]

#### Theme N: [Name]

[Same structure]

### Consensus and Contested Areas

**Areas of Consensus** (most sources agree):
- [topic]: [consensus position] [confidence: HIGH]
- [topic]: [consensus position] [confidence: HIGH]

**Areas of Active Debate** (sources disagree):
- [topic]: [summary of disagreement]
- [topic]: [summary of disagreement]

**Emerging Topics** (few sources, early signal):
- [topic]: [what is being said and by whom]

### Gaps in the Literature

[What topics are not well-covered? Where is the knowledge sparse?
What questions remain unanswered?]

- [gap 1]: [what is missing and why it matters]
- [gap 2]: [what is missing and why it matters]

### Annotated Source List

| # | Source | Type | Credibility | Date | Key Contribution |
|---|--------|------|------------|------|------------------|
| 1 | [ref]  | [type] | [score] | [date] | [what this source uniquely contributes] |

### Conclusion

[What does the reader now know that they did not before? What should
they investigate next? What is the state of knowledge on this topic?]

### Suggested Follow-Up

- [Specific topic that warrants dedicated research]
- [Question that emerged from the survey]
```

### Writing Guidelines

- Organize by theme, not by source -- synthesize across sources
- Show the landscape -- where is consensus, where is debate?
- Annotate sources -- do not just list them; explain what each contributes
- Identify gaps -- what is NOT known is as important as what IS known
- This is not a summary of each source; it is a synthesis of the field
- Keep an objective tone -- present positions, do not advocate

---

## Format Selection Quick Reference

| If the reader needs to... | Use | Length | Confidence Required |
|--------------------------|-----|--------|---------------------|
| Get a quick answer | Executive Summary | 1 page | Any |
| Implement or debug something | Technical Deep-Dive | 2-10 pages | HIGH preferred |
| Compare options side-by-side | Comparison Matrix | 2-5 pages | MEDIUM minimum |
| Make a specific decision | Decision Brief | 2-4 pages | MEDIUM minimum |
| Understand a topic landscape | Literature Review | 3-8 pages | Any |

## Citation Format

All briefing formats use the same citation style:

**Inline citations**: Use bracketed numbers `[1]`, `[2]`, `[3]` that correspond to the source list.

**Multiple sources**: `[1, 3]` when multiple sources support a claim.

**Conflicting sources**: `[1] vs [3]` when sources disagree.

**Confidence inline**: `[Confidence: HIGH]` at the end of each major finding.

**Source list entry format**:

```
| # | Source | Type | Credibility | Date | Relevance |
|---|--------|------|------------|------|-----------|
| 1 | [descriptive name or title] | Primary | 5 | 2025-01 | Findings 1.1, 2.3 |
```

---

## Anti-Patterns by Format

| Format | Anti-Pattern | Fix |
|--------|-------------|-----|
| Executive Summary | Burying the answer in paragraph 3 | Lead with the bottom line; first sentence answers the question |
| Technical Deep-Dive | Showing conclusions without evidence | Every finding must show the evidence chain |
| Comparison Matrix | Comparing on made-up criteria | Define criteria from the reader's actual needs, not from what is easy to compare |
| Decision Brief | Recommending without stating assumptions | Every recommendation rests on assumptions; state them so the reader can validate |
| Literature Review | Listing sources instead of synthesizing themes | Organize by theme, not by source; show the landscape |
