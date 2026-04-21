# Signal Types Reference — Transcript Capture

A reference for identifying and classifying signal types in meeting transcripts. Use during the FILTER phase to score and categorize blocks.

---

## The Four Signal Types

### Requirements

A **requirement** is a statement about what a system must do, must not do, or must be. Requirements are the primary target of capture.

**Strong signals (HIGH confidence):**
- "We need the system to..."
- "It must support..."
- "This has to work with..."
- "The requirement is..."
- Direct feature requests with a named actor and capability

**Weak signals (UNCERTAIN — flag, do not harden):**
- "It would be great if..."
- "Ideally we'd want..."
- "We might need..."
- "I think we should probably..."
- "At some point, maybe..."

**Traps to avoid:**
- Problem statements are not requirements: "Our reporting is broken" → extract as context, not as a requirement
- Brainstorming items are not requirements unless the meeting reaches a decision
- Questions ("Should we support SSO?") are open questions, not requirements

---

### Decisions

A **decision** is a resolution between alternatives. A meeting that produces decisions is valuable; one that only surfaces options has not yet produced requirements.

**Strong signals:**
- "We decided to go with X"
- "We're not doing Y"
- "The call is X, not Y"
- "Approved" / "confirmed" following a proposal
- "We'll use X for Z" (technology selection decisions)

**What to look for:**
- A proposal followed by consensus acknowledgment ("yes," "agreed," "sounds good," "let's do that")
- A prior alternative being explicitly closed: "We're not building a custom solution; we're integrating with [vendor]"

**Traps to avoid:**
- Proposals without acceptance are not decisions — they are open questions
- Tentative agreement ("I think we can do that") is not a decision — flag as UNCERTAIN

---

### Open Questions

An **open question** is something raised but not resolved. Capturing open questions is as valuable as capturing requirements — unresolved questions become risks.

**Signals:**
- Direct questions asked without an answer in the transcript
- "We still need to figure out..."
- "TBD"
- "Let's take that offline"
- "I'll follow up with..."
- Action items to investigate or decide ("John will check if the vendor supports X")

**Attribution matters:** Note who raised the question and whether it was assigned to someone for follow-up.

---

### Action Items

An **action item** is a commitment to do something specific, assigned to a person, usually with a timeframe.

**Signals:**
- "I'll send you..." / "She'll follow up with..."
- "By [date], we'll have..."
- Named owner + task: "Michael, can you check...?" + acknowledgment

**Traps:**
- Vague intentions ("we should look into that") are not action items unless someone accepts ownership
- Action items that are requirements in disguise: "Let's add reporting to the sprint" — capture as both an action item AND a potential requirement

---

## Uncertainty Spectrum

Use this spectrum when deciding whether to flag `[UNCERTAIN]`:

| Phrasing | Classification |
|----------|---------------|
| "The system must..." | Definite — no tag needed |
| "We need..." | Strong — no tag needed |
| "We want..." | Moderate — context-dependent; flag if speaker is non-authoritative |
| "It would be useful if..." | Weak — always flag `[UNCERTAIN]` |
| "Maybe we could..." | Very weak — flag `[UNCERTAIN]`, check capture sensitivity level |
| "Hypothetically..." | Brainstorming — use context; do not extract unless there is follow-up confirmation |

---

## Speaker Authority Heuristics

Not all speakers carry equal weight. Use these heuristics when assessing block relevance.

| Speaker Type | Weight | Notes |
|---|---|---|
| **Client decision-maker** (VP, Director, Product Owner) | Highest | Statements are likely binding |
| **Client subject matter expert** | High | Technical requirements carry authority; business decisions do not |
| **Client end user** | Medium | Preferences and pain points are valuable context; not always requirements |
| **Internal PM / BA** | Medium | Clarifications, paraphrases, summaries — verify against original stakeholder statement |
| **Internal technical lead** | Medium | Technical constraints and feasibility signals; rarely decision-authority for scope |
| **Meeting facilitator** | Low for content | Summarizations are paraphrases — prefer original speaker statements |

**Rule:** When an authoritative speaker confirms a statement made by a lower-authority speaker ("Yes, that's right, we need X"), the confirmation upgrades the signal strength.

---

## Transcript Noise Taxonomy

Categories of content to classify as SKIP:

| Noise Type | Examples | Why SKIP |
|---|---|---|
| **Small talk** | Weather, personal updates, meeting setup | No project content |
| **Logistics** | "Can you share your screen," "You're on mute," scheduling | Coordination, not content |
| **Tangents** | Discussion of unrelated projects, products, or teams | Out of scope by definition |
| **Repeated content** | Second statement of something already said | The first instance carries the signal |
| **AI summary headers** | "In this meeting we discussed..." | Paraphrase — prefer verbatim source |
| **Social coordination** | Thanks, sign-offs, pleasantries | No content |
| **Resolved disagreements** | A position that was proposed and explicitly rejected | The rejected position is not a requirement |
