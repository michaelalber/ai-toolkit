# research-synthesis — operating guide

Depth relocated from SKILL.md; load it when the Workflow points here.

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
