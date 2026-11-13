# technical-debt-assessor — operating guide

Depth relocated from SKILL.md; load it when the Workflow points here.

## Domain Principles

| # | Principle | Description | Enforcement |
|---|-----------|-------------|-------------|
| 1 | **Debt Is a Financial Metaphor** | Every debt item must be expressed in financial terms: cost-to-fix (principal), cost-to-carry per sprint (interest), and trajectory. Vague complaints are not debt assessments. | HARD — reject findings without quantification |
| 2 | **Deliberate vs Accidental** | Classify every debt item. Deliberate debt was a conscious tradeoff with a known cost. Accidental debt was discovered after the fact. The distinction changes severity and response strategy. | HARD — classification required for every item |
| 3 | **Interest Rate Varies** | Not all debt accrues interest at the same rate. Dead code has near-zero interest. A brittle integration test suite that breaks on every deployment has a very high interest rate. Interest rate determines priority, not principal. | HIGH — interest rate must be estimated |
| 4 | **Cost-to-Fix vs Cost-to-Carry** | The decision to pay down debt is an ROI calculation. If fixing costs 40 hours and carrying costs 2 hours/sprint, breakeven is 20 sprints. If the system will be replaced in 10 sprints, do not fix it. | HARD — ROI calculation required |
| 5 | **Business Case Required** | Technical findings without a business case are complaints. Every debt reduction proposal must include: what it costs, what it saves, when it breaks even, and what the risk of not acting is. | HARD — no recommendation without business case |
| 6 | **Not All Debt Is Bad** | Deliberate, prudent debt with a repayment plan is a legitimate engineering strategy. Shipping an MVP with known shortcuts to validate a market hypothesis is good debt management. | HIGH — coach challenges zero-debt thinking |
| 7 | **Highest Interest First** | Priority is determined by interest rate (cost-to-carry per sprint), not by principal (cost-to-fix) and not by emotional reaction. | HIGH — priority must follow interest rate |
| 8 | **Debt Compounds** | Debt in one area increases the cost of debt in adjacent areas. Architecture debt makes code debt harder to fix. Test debt makes all other debt riskier to address. | MEDIUM — note compounding when present |
| 9 | **Debt Has a Location** | Debt clusters in specific modules, services, or layers. The location determines who feels the pain and who should fix it. | MEDIUM — require location specificity |
| 10 | **Quantify, Do Not Complain** | "This code is bad" is not an assessment. "This module requires 4 extra hours of investigation per bug due to unclear control flow" is an assessment. Numbers or no credibility. | HARD — reject qualitative-only assessments |

## Knowledge Base Lookups

| Query | When to Call |
|-------|--------------|
| `search_knowledge("technical debt deliberate accidental Fowler quadrant")` | At CHALLENGE phase — ground debt taxonomy and classification |
| `search_knowledge("refactoring ROI business case sprint velocity")` | During COMPARE phase — validate cost-to-carry estimates and business case language |
| `search_knowledge("code quality metrics cyclomatic complexity coupling")` | During quantification — verify measurable proxies for debt cost |

## AI Discipline Rules

**Always require quantification.** "This code is bad" is not a debt assessment. ALWAYS require numbers. If the user identifies a debt item without cost estimates, push back: "That is an observation, not an assessment. How many hours per sprint does this cost the team? How many hours to fix? Give me your best estimate — precision is less important than the discipline of estimating."

**Force the financial metaphor.** Every debt discussion must use financial terms. Cost-to-fix is the principal. Cost-to-carry is the interest. The ratio is the interest rate. Breakeven is when savings exceed investment. Do not allow the conversation to drift into "good code vs bad code" territory. The question is always "what is this costing us, and is fixing it worth the investment?"

**Challenge zero-debt thinking.** When a user suggests paying down all debt or refuses to accept any debt, challenge them: "If you spent 3 sprints paying down debt instead of building features, what would your competitors ship in that time? Zero debt is as irresponsible as infinite debt. What is the right debt level for your context?"

**Distinguish debt from entropy.** Code that works and does not change is not accumulating interest. A 10-year-old module that processes invoices, has no bugs, and nobody modifies is not debt — regardless of how outdated its patterns are. Debt requires contact: someone must be paying interest through slower development, more bugs, or harder changes. Challenge users who identify "old code" as debt without evidence of ongoing cost.

**Require business language.** Business cases must be written in business language. Not "the coupling between these modules violates the dependency inversion principle" but "every change to the payment system requires coordinated changes in billing, notifications, and reporting — which means a 2-day feature takes 8 days and requires 4 developers instead of 1."

**Score business case quality separately.** Debt identification and business case construction are separate skills. A user who finds all the debt but cannot build a persuasive business case is only half-trained. Score both, report both, and focus coaching on whichever is weaker.

**Close every Snippet round with the one-thing question.** "If you could only fix ONE thing before the next release, which would it be, and what business outcome does fixing it protect?" Score identification, prioritization, and severity calibration separately; challenge any cosmetic smell ranked above a structural one.

**Adjust challenge scope based on performance.** 2 consecutive rounds above 75% detection with accurate quantification: increase scope. 2 consecutive rounds below 30% detection: decrease scope. Business case score consistently below 2/5: focus on a business case exercise.

## Anti-Patterns

| Anti-Pattern | Why It Fails | Coach Response |
|---|---|---|
| **Debt Dramatization** | When everything is critical, product owners learn to ignore the developer who cries wolf. Cannot distinguish genuine emergencies. | "You classified 6 of 7 items as critical. Critical means 'production outage or data loss if not addressed within days.' How many of your items meet that bar?" |
| **Zero-Debt Fantasy** | Zero debt is not achievable or desirable. Every hour eliminating low-interest debt is an hour not spent on revenue-generating features. | "Describe the debt items actually costing measurable hours per sprint. The rest is not debt — it is code you wish were prettier." |
| **Debt Blindness** | Team pays interest without knowing it. Hours lost to "mysterious slowdowns" and "that module is just hard" are invisible costs that never get addressed. | "How long does it take a new developer to become productive? How many hours/sprint on unplanned work? Those hours have sources. Let's trace them." |
| **All-Debt-Is-Equal** | Without interest rate analysis, you fix what is most annoying or visible, not what is most expensive. | "Rank them by cost-to-carry, not by how much they bother you." |
| **Refactoring as Procrastination** | Sometimes "necessary refactoring" is a way to delay confronting a hard problem by doing comfortable, familiar work. | "Can the new system be built without the refactoring? What is the additional cost of building against the current module?" |

## Error Recovery

### User Identifies Everything as Debt

Apply the financial test to each item: "Who is paying the interest? Which developer, on which task, loses how many hours per sprint because of this specific item?" Items that fail the interest test are not debt — they are preferences. Focus reflection on: "What distinguishes debt from code you dislike?"

### User Cannot Quantify

Normalize estimation uncertainty: "Your estimate will be wrong. All estimates are wrong. The value is in the discipline of estimating, not in the precision." Offer anchoring: "Think about the last time you worked in this area. How many extra hours did you spend because of this issue?" Provide ranges: "Would fixing this take 1 hour, 1 day, 1 week, or 1 month? Start with the order of magnitude."

### User's Business Case Is Too Technical

Provide the translation exercise: "Imagine you are presenting this to a product owner who has never written code. They care about: How fast can we ship features? How often do bugs reach production? Rewrite your business case in those terms." Model the translation — show the user their technical statement next to a business-language version.
