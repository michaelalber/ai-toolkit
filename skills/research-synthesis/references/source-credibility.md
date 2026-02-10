# Source Credibility Scoring Framework

## Overview

Source credibility is not a fixed property of a source -- it is a per-topic assessment. The New York Times is a credible source for current events but not for kernel compilation flags. A Stack Overflow answer may be the most credible source for a specific niche library bug and completely wrong about distributed systems architecture. Always assess credibility in context.

**The fundamental question:** "Is this source likely to be correct about this specific claim?"

---

## Source Type Classification

### Primary Sources

Primary sources are the original artifacts -- the thing itself, not someone's description of it.

| Source | Example | Credibility Basis |
|--------|---------|-------------------|
| Source code | The actual implementation in the repository | It IS the truth for what the code does (not what it should do) |
| Official documentation | API reference authored by the maintainers | Written by those who built it, though may lag behind code |
| RFCs and specifications | IETF RFCs, W3C specs, language standards | Normative documents that define correct behavior |
| Configuration files | `.env.example`, `docker-compose.yml`, CI configs | Show actual operational parameters |
| Commit history | Git log, blame, changelogs | Timestamped record of what changed and why |
| Test suites | Unit tests, integration tests, e2e tests | Encode expected behavior as executable specifications |
| Design documents | ADRs, RFDs, design proposals | Capture intent and reasoning at decision time |

**Default credibility score: 4-5**

**Caveats:**
- Source code shows what IS, not what SHOULD BE -- bugs are primary sources too
- Official documentation may be outdated if the project moves faster than docs
- Design documents capture intent at a point in time; the implementation may have diverged

### Secondary Sources

Secondary sources describe, analyze, or interpret primary sources.

| Source | Example | Credibility Basis |
|--------|---------|-------------------|
| Technical blog posts | Practitioner writing about their experience | First-hand experience, but single perspective |
| Conference talks | Speaker presenting research or case study | Curated content, but may simplify for audience |
| Tutorials and guides | Step-by-step walkthroughs | Practical validation, but may cover only happy path |
| Peer-reviewed benchmarks | Independent performance comparisons | Methodology-backed, but specific to test conditions |
| Technical books | Published reference material | Thoroughly reviewed, but may be dated by publication time |
| Documentation aggregators | Community wikis, unofficial guides | Wider contributor base, but variable quality |

**Default credibility score: 2-4** (varies significantly by author and context)

**Assessment criteria for secondary sources:**
1. **Author authority**: Does the author have demonstrated expertise in this domain?
2. **Publication venue**: Peer-reviewed > curated blog > personal blog > anonymous
3. **Evidence basis**: Does the source cite primary sources or provide reproducible evidence?
4. **Date**: Is the content current relative to the topic's rate of change?
5. **Bias indicators**: Is the author selling something? Affiliated with a competitor?

### Tertiary Sources

Tertiary sources compile, summarize, or aggregate other sources without original analysis.

| Source | Example | Credibility Basis |
|--------|---------|-------------------|
| Forum answers | Stack Overflow, Reddit, Discord | Community-validated but variable quality |
| AI-generated content | ChatGPT summaries, AI documentation | May be plausible but fabricated; no ground truth |
| Wikipedia | General encyclopedia entries | Good starting point but not authoritative for technical detail |
| Comparison websites | "Top 10 frameworks" listicles | Often SEO-optimized, not accuracy-optimized |
| Marketing materials | Vendor whitepapers, product pages | Inherent bias toward the vendor's product |
| Undated/unattributed content | Anonymous blog posts, undated guides | No accountability, no recency signal |

**Default credibility score: 1-2**

**When tertiary sources are acceptable:**
- As a starting point to identify primary sources to consult
- When no primary or secondary sources exist (flag this prominently)
- For establishing that a question is commonly asked (social proof)
- Stack Overflow answers with high vote counts AND linked primary sources

---

## Recency Weighting

Information has a half-life that depends on the domain's rate of change.

### Recency Categories

| Domain | Half-Life | Explanation |
|--------|-----------|-------------|
| Cloud services (AWS, GCP, Azure) | 6-12 months | APIs change, services launch/deprecate, pricing shifts |
| JavaScript ecosystem | 6-12 months | Framework versions, tooling changes, package deprecations |
| AI/ML frameworks | 3-6 months | Rapid iteration, breaking changes, new paradigms |
| Language standards (Python, C++) | 2-5 years | Slow, deliberate evolution with long support cycles |
| Operating systems | 1-3 years | Release cycles, kernel changes, system calls |
| Networking protocols (TCP, HTTP) | 5-10+ years | RFCs evolve slowly; HTTP/2 to HTTP/3 took years |
| Algorithms and data structures | Decades | Fundamental CS rarely changes |
| Security vulnerabilities | Days to weeks | CVEs are time-critical; patching is immediate |

### Recency Scoring

Apply this modifier to the base credibility score:

| Source Age vs. Half-Life | Modifier | Rationale |
|--------------------------|----------|-----------|
| Within half-life | +0 (no penalty) | Source is current |
| 1-2x half-life | -1 | May be partially outdated |
| 2-3x half-life | -2 | Likely outdated; verify against current sources |
| Beyond 3x half-life | -3 (floor at 1) | Treat as historical context, not current reference |

**Example:**
- A 2024 blog post about AWS Lambda best practices (half-life: ~12 months)
  - In 2025: score modifier +0 (within half-life)
  - In 2026: score modifier -1 (1-2x half-life)
- A 2020 blog post about Python asyncio (half-life: ~3 years)
  - In 2025: score modifier -1 (approaching 2x half-life)
  - Core concepts still valid; API details may have changed

### When Older Sources Are More Credible

Not all recency favors newer sources:
- **Original design rationale**: A 2010 design document explaining why a system was built a certain way may be more valuable than a 2024 blog post guessing at the reasons
- **Foundational papers**: Dijkstra's shortest path paper is not "outdated"
- **Post-mortems**: An incident report from the time of the incident is primary; a later summary is secondary
- **Specifications**: The original RFC for a protocol is authoritative regardless of age (though amendments and errata apply)

---

## Authority Assessment

### Individual Authority

| Signal | Score Boost | Why |
|--------|-------------|-----|
| Core maintainer of the project in question | +2 | They built it; they know it |
| Recognized domain expert (conference speaker, book author) | +1 | Demonstrated expertise |
| Employed by the organization that created the technology | +1 | Institutional knowledge |
| Active contributor (frequent commits, issues, PRs) | +1 | Engaged and current |
| Unknown or anonymous author | -1 | No accountability |
| Author has a commercial interest in the topic | -1 | Potential bias |

### Organizational Authority

| Organization Type | Default Authority | Caveats |
|-------------------|-------------------|---------|
| Standards body (IETF, W3C, ISO) | Very High | Normative by definition |
| Project maintainers (official docs, repos) | High | May have documentation debt |
| Academic institutions | High (for research) | May lack practical context |
| Major tech companies | Medium-High | Authoritative for their own products; biased in comparisons |
| Independent research organizations | Medium-High | Check funding sources |
| Developer advocacy teams | Medium | Educational mission may simplify |
| Individual practitioners | Variable | Assess per-person |
| SEO-driven content farms | Low | Optimized for traffic, not accuracy |

---

## Cross-Reference Validation

### Independence Test

Two sources are independent if and only if neither derived its claim from the other.

```
INDEPENDENCE CHECK:
1. Does Source B cite Source A? -> NOT independent
2. Does Source B link to Source A? -> Probably NOT independent
3. Are Source A and Source B authored by the same person? -> NOT independent
4. Did Source A and Source B publish within days of a shared event?
   -> May be independently observing the same thing (independent)
5. Are Source A and Source B in different media/venues?
   -> More likely independent (but verify)

Two sources citing the same upstream primary source:
- They are NOT independent of each other for this claim
- They ARE independent observations that the upstream source exists
```

### Corroboration Scoring

| Corroboration Level | Evidence Pattern | Resulting Confidence |
|---------------------|------------------|---------------------|
| Strong | 2+ independent primary sources agree | HIGH |
| Moderate | 1 primary + 1 independent secondary agree | HIGH |
| Acceptable | 2+ independent secondary sources agree | MEDIUM-HIGH |
| Weak | 1 primary source, no contradictions | MEDIUM |
| Minimal | 1 secondary source, no contradictions | LOW-MEDIUM |
| None | 1 tertiary source only | LOW |
| Conflicted | Sources disagree | Depends on resolution |

### Handling Conflicts

When sources disagree, follow this protocol:

```
1. CLASSIFY the conflict:
   - Factual disagreement (they make contradictory claims about the same thing)
   - Scope disagreement (they are talking about different versions/contexts)
   - Temporal disagreement (one is outdated, the other is current)
   - Perspective disagreement (different but not contradictory viewpoints)

2. ASSESS credibility per-source for this specific claim:
   - Which source is closer to the primary evidence?
   - Which source is more current?
   - Which source has more corroborating evidence?

3. REPORT the conflict:
   - State each source's position clearly
   - Explain the credibility assessment
   - If one position is stronger, note it
   - ALWAYS show both positions to the reader

4. ASSIGN confidence:
   - Resolved conflict (clear winner): MEDIUM (not HIGH -- the conflict itself is a caveat)
   - Unresolved conflict: LOW
   - Apparent conflict that is actually scope/temporal: note and resolve to MEDIUM-HIGH
```

---

## Confidence Level Assignment

### Decision Matrix

| Primary Sources | Secondary Sources | Tertiary Sources | Conflicts | Confidence |
|-----------------|-------------------|------------------|-----------|------------|
| 2+ agree | Any | Any | None | HIGH |
| 1 + corroboration | 1+ agrees | Any | None | HIGH |
| 1, no corroboration | 0 | 0 | None | MEDIUM |
| 0 | 2+ agree | Any | None | MEDIUM |
| 0 | 1 | 0 | None | LOW |
| Any | Any | Only | None | LOW |
| Any | Any | Any | Unresolved | LOW |
| 0 | 0 | 1 | N/A | UNVERIFIED |
| 0 | 0 | 0 | N/A | UNKNOWN |

### Confidence Labels for Briefings

Use these labels consistently in all research output:

```markdown
[HIGH] -- Corroborated by multiple independent credible sources
[MEDIUM] -- Supported by credible source(s) but not fully corroborated
[LOW] -- Limited evidence; treat with caution
[UNVERIFIED] -- Single low-credibility source; requires further investigation
[CONFLICTED] -- Sources disagree; both positions presented
[UNKNOWN] -- No evidence found; gap in available research
```

---

## Composite Credibility Score

For each source, compute a composite score:

```
Base Score (from source type):
  Primary: 4
  Secondary: 3
  Tertiary: 1

+ Authority Modifier: -1 to +2
+ Recency Modifier: -3 to +0
+ Bias Modifier: -2 to +0
  (no bias: 0, mild bias: -1, strong bias: -2)

= Composite Score (floor 1, ceiling 5)
```

**Example Calculations:**

```
Source: Official Python documentation for asyncio
  Base: 4 (primary)
  Authority: +1 (maintained by CPython core team)
  Recency: +0 (continuously updated)
  Bias: +0 (no commercial bias)
  Composite: 5

Source: Medium blog post about asyncio patterns (2022)
  Base: 3 (secondary)
  Authority: +0 (unknown author, reasonable content)
  Recency: -1 (approaching 2x half-life for Python ecosystem)
  Bias: +0 (no apparent bias)
  Composite: 2

Source: Stack Overflow answer about asyncio bug (2024, 150 upvotes)
  Base: 1 (tertiary)
  Authority: +1 (high community validation)
  Recency: +0 (current)
  Bias: +0 (no commercial bias)
  Composite: 2
```

---

## Quick Reference Card

```
SOURCE TYPE:       Primary (4) > Secondary (3) > Tertiary (1)
RECENCY:           Within half-life (+0) ... Beyond 3x (-3)
AUTHORITY:         Core maintainer (+2) ... Anonymous (-1)
BIAS:              None (+0) ... Strong vendor (-2)
COMPOSITE:         Sum all, floor 1, ceiling 5

CONFIDENCE:        HIGH = 2+ independent credible sources agree
                   MEDIUM = 1 credible source, no contradictions
                   LOW = 1 weak source, or unresolved contradictions
                   UNVERIFIED = tertiary only, needs investigation

INDEPENDENCE:      B cites A? NOT independent.
                   Same author? NOT independent.
                   Same upstream? NOT independent for that claim.

CONFLICT RULE:     Always report both sides. Never silently resolve.
```
