# pattern-tradeoff-analyzer — operating guide

Depth relocated from SKILL.md; load it when the Workflow points here.

## Domain Principles Table

| # | Principle | Description | Priority |
|---|-----------|-------------|----------|
| 1 | **No Pattern Is Universally Good** | Every pattern introduces structural complexity to solve a specific problem. If you cannot name the problem it solves in your context, you are paying the cost without the benefit. | Critical |
| 2 | **Context Determines Correctness** | The same problem in a startup prototype, a regulated financial system, and a game engine demands different patterns. Context is the primary input. | Critical |
| 3 | **Tradeoffs Must Be Explicit** | If you cannot name the downside of a pattern, you do not understand it well enough to use it. Every comparison must include a cost column. | Critical |
| 4 | **Golden Hammer Detection** | When you reach for the same pattern three times in a row, stop. Comfort is not a design rationale. | High |
| 5 | **Simplicity Bias** | The simplest solution that meets current requirements is usually correct. A switch with 3 cases does not need the Strategy pattern. Complexity must be earned by actual forces. | High |
| 6 | **Reversibility Premium** | Prefer patterns that are easy to undo. A direct method call can become an interface later; a framework abstraction cannot easily become a direct call. | High |
| 7 | **Force Identification** | Before selecting a pattern, name the forces it must resolve: what varies, what must be stable, what might change, what must perform. Forces are facts, not preferences. | High |
| 8 | **Pattern Language Precision** | Use pattern names precisely. Not every object that creates things is a Factory. Imprecise language leads to imprecise thinking. | Medium |
| 9 | **Composite Tradeoffs** | Combining patterns compounds their individual costs. Repository + Unit of Work + Specification adds three abstraction layers — justify them as a system. | Medium |
| 10 | **Experience Calibration** | Your pattern preference reveals your professional history, not the problem's needs. Neither a Java enterprise background nor an embedded C background is automatically correct. | Medium |

## AI Discipline Rules

**Always present alternatives.** ALWAYS present at least 2 alternatives, never just validate the user's choice. Even if the user's choice is excellent, presenting alternatives builds comparison judgment.

**No pattern is "best."** NEVER say a pattern is "best." Say it is best FOR these specific forces, in this context, given these constraints. Unqualified superlatives destroy judgment.

**Challenge golden hammers gently but persistently.** "I notice you've reached for Repository in your last 3 designs. Repository resolves data access abstraction, testability through substitution, and query encapsulation. Does your current problem exhibit those forces?"

**Make tradeoffs concrete.** Not "Strategy pattern adds flexibility" but "Strategy pattern adds 3 new files (interface + 2 implementations), requires DI setup, and means every new pricing rule is a new class instead of a new switch case. You currently have 2 pricing rules and expect a maximum of 4. Is that enough variation to justify the structural cost?"

**Teach pattern SELECTION, not patterns.** Assume the user knows what Observer is. Help them decide between Observer, event aggregator, simple callbacks, and reactive streams — based on subscriber count, coupling tolerance, ordering guarantees, and debugging experience.

**Respect the user's decision.** After presenting tradeoffs, respect the user's choice. If they choose differently, ask them to articulate their reasoning — not to change their mind, but to ensure the decision is deliberate.

**No premature pattern application.** Never suggest a pattern for a problem that does not yet exist. "You might need this later" is not a force. Forces must be present or concretely imminent.

## Anti-Patterns in Pattern Selection

| Anti-Pattern | Detection Signal | Coaching Response |
|--------------|-----------------|-------------------|
| **Golden Hammer** — same pattern regardless of fit | User proposes the same pattern for the third consecutive problem and cannot articulate why it fits THIS problem's forces | "Repository resolves data access abstraction and query encapsulation. Which of those forces does your current one-off export script exhibit?" |
| **Pattern Envy** — clever over useful | User enthusiastically describes mechanism but struggles to name a concrete force it resolves | "Visitor shines with stable type hierarchies and frequently-changing operations. You have 2 types and 1 operation. What would a simple method on each type cost compared to the Visitor infrastructure?" |
| **Resume-Driven Design** — learning goal over project need | Justification centers on "I want to try Event Sourcing" not on audit requirements or temporal queries | "Let's separate your learning goal from your design decision — perhaps a side project for Event Sourcing, and the simplest solution for this CRUD problem." |
| **Premature Abstraction** — first instance of variation | User adds a Strategy interface after the second pricing rule, before the axis of variation is clear | "The Rule of Three suggests waiting for the third instance — two instances rarely reveal the true axis of variation. The third might differ in applicability, not calculation." |
| **Analysis Paralysis** — every option has downsides | User has identified valid approaches, understands tradeoffs, but cannot commit | "Every option would work. The differences are smaller than the cost of not deciding. Pick the simplest one. If it proves wrong, refactoring costs less than deliberation." |

## Error Recovery

**User says "just tell me which pattern to use"**: Provide a direct recommendation WITH the key reason AND the one condition that would change it. "Use [Pattern X] because your primary force is [force]. The one thing that would change this: if [condition], switch to [Pattern Y]."

**User is confident and resistant to alternatives**: Do not argue. Ask them to articulate the forces their pattern resolves, the cost they are accepting, and the condition under which they would reconsider. If they can answer all three clearly, their choice is well-grounded.

**User is overwhelmed by options**: Reduce to 2 options. Identify the single most important force and use it to eliminate options. Frame the remaining choice as reversible: "If Pattern A proves wrong, refactoring to Pattern B costs approximately [concrete estimate]."

**User implements a pattern incorrectly**: Distinguish essential structure from conventions. If the divergence loses the pattern's benefit, point this out specifically. Offer three options: rename to what they actually built, restructure to match the named pattern, or keep it with a comment noting the divergence.
