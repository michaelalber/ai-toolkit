# Technical Debt Taxonomy

This reference provides the classification framework for technical debt identification, categorization, and interest rate estimation.


## The Technical Debt Quadrant

Martin Fowler's adaptation of Ward Cunningham's metaphor organizes debt along two axes: deliberate vs inadvertent, and prudent vs reckless. The quadrant is not a judgment -- it is a diagnostic tool that determines the appropriate response.

```
                        Prudent                          Reckless
              +-----------------------------+-----------------------------+
              |                             |                             |
              |  "We must ship now and      |  "We don't have time for    |
 Deliberate   |   deal with consequences"   |   design"                   |
              |                             |                             |
              |  Known tradeoff.            |  Known shortcut with no     |
              |  Repayment plan exists.     |  plan to repay.             |
              |  Interest rate: estimated.  |  Interest rate: unknown     |
              |                             |  and likely high.           |
              +-----------------------------+-----------------------------+
              |                             |                             |
              |  "Now we know how we        |  "What's a design           |
 Inadvertent  |   should have done it"      |   pattern?"                 |
              |                             |                             |
              |  Learned through            |  Did not know enough to     |
              |  experience. Natural.       |  recognize the debt.        |
              |  Repayment is improvement.  |  Repayment requires         |
              |                             |  education + refactoring.   |
              +-----------------------------+-----------------------------+
```

### Quadrant Details

#### Deliberate + Prudent

**Definition:** The team knowingly took a shortcut, understood the cost, and has a plan to address it.

**Example scenario:** A startup building an MVP chooses to hardcode the payment provider integration rather than building a payment abstraction layer. The team documents the decision: "We are coupling directly to Stripe. When we add a second payment provider (projected Q3), we will introduce the abstraction. Estimated cost to refactor at that time: 2 sprints. Cost saved now: 3 weeks."

**Characteristics:**
- Decision is documented
- Cost is estimated at time of decision
- Trigger for repayment is defined
- Interest rate is known and accepted

**Appropriate response:** Monitor. Repay when the trigger condition is met. This is good debt management.

#### Deliberate + Reckless

**Definition:** The team knowingly took a shortcut but without understanding or caring about the cost.

**Example scenario:** A team lead says "we don't have time for unit tests on this module" with no plan to add them later and no estimate of the cost. The module ships without tests and without any documentation of the decision.

**Characteristics:**
- Decision is made consciously but without analysis
- No cost estimate
- No repayment trigger
- Interest rate is unknown and unmonitored

**Appropriate response:** Assess immediately. Quantify the actual cost-to-carry. This debt often has a higher interest rate than anyone expected because nobody estimated it.

#### Inadvertent + Prudent

**Definition:** The team built something the best way they knew how, and later realized a better approach exists.

**Example scenario:** A team implements a monolithic event processing system. After 18 months of production experience, they realize that the event types have diverged enough that separate processing pipelines per event category would be simpler, faster, and more maintainable. The original design was not wrong at the time -- the insight came from experience.

**Characteristics:**
- No conscious decision was made to take a shortcut
- The team's understanding has grown
- The debt was invisible until experience revealed it
- Repayment is a form of improvement, not error correction

**Appropriate response:** This is the type of debt Cunningham originally described. Assess the cost-to-carry. If the system is actively changing in the affected area, the interest rate may justify refactoring. If the area is stable, the interest rate may be near zero.

#### Inadvertent + Reckless

**Definition:** The team did not know enough to recognize they were creating debt. Poor practices due to lack of skill or knowledge.

**Example scenario:** A junior developer builds a data access layer that opens a new database connection for every query, never uses connection pooling, and catches all exceptions with empty catch blocks. The developer did not know these were problems.

**Characteristics:**
- No awareness that debt was being created
- Often widespread rather than localized
- Frequently compounds across categories
- Requires education alongside remediation

**Appropriate response:** This is the most expensive quadrant because the debt is typically systemic (the same lack of knowledge affects many areas) and the team may not recognize the cost until it becomes severe. Address through education plus targeted refactoring of the highest-impact areas.


## Debt Categories

Technical debt manifests in six categories. Each has different characteristics, interest rates, and remediation approaches.

### 1. Architecture Debt

**Definition:** Structural decisions that constrain the system's ability to evolve.

**Examples:**
- Monolithic design when the team and problem domain have outgrown it
- Circular dependencies between services
- Shared databases between services that should be independent
- Missing service boundaries (the "big ball of mud")
- Synchronous communication chains where async would be appropriate

**Typical interest rate:** HIGH and INCREASING. Architecture debt compounds because every new feature must work around the structural constraints. As the system grows, the workarounds become more elaborate and fragile.

**Cost-to-carry indicators:**
- Features that should take 1 sprint take 3+ sprints due to cross-cutting concerns
- Changes in one area cause unexpected failures in unrelated areas
- Deployment of one component requires deployment of many components
- New team members take 3+ months to become productive

**Cost-to-fix characteristics:** High principal. Architecture changes are expensive because they touch many components, require data migration, and carry deployment risk. However, the high interest rate often means the breakeven period is short.

### 2. Code Debt

**Definition:** Implementation-level issues within modules, classes, and functions.

**Examples:**
- Functions exceeding 200+ lines with deeply nested conditionals
- Duplicated business logic across multiple locations
- God classes that aggregate unrelated responsibilities
- Stringly-typed interfaces where structured types are needed
- Missing error handling in critical paths
- Inconsistent naming conventions that slow comprehension

**Typical interest rate:** MEDIUM and STABLE. Code debt is painful but usually localized. It slows work in the affected area but does not propagate as aggressively as architecture debt.

**Cost-to-carry indicators:**
- Bug investigation in the affected module takes 2-3x longer than average
- New developers ask "what does this do?" about the same code repeatedly
- Code reviews for changes in the area take significantly longer
- The team avoids modifying certain files because "they are fragile"

**Cost-to-fix characteristics:** Low to medium principal per item. Code debt can often be addressed incrementally -- one function at a time, one class at a time -- without system-wide coordination.

### 3. Test Debt

**Definition:** Gaps or problems in the test suite that increase risk and slow delivery.

**Examples:**
- Missing unit tests for critical business logic
- Integration tests that are flaky (pass/fail randomly)
- Tests that are so tightly coupled to implementation that every refactor breaks them
- Missing edge case coverage in areas with known production bugs
- Test suites that take 45+ minutes to run, causing developers to skip them
- No tests at all for a significant portion of the codebase

**Typical interest rate:** HIGH and INCREASING. Test debt is a multiplier. It makes every other category of debt riskier to address (you cannot safely refactor code without tests) and slows every deployment (flaky tests block pipelines).

**Cost-to-carry indicators:**
- Developers skip running tests locally because they take too long
- CI pipeline failures are routinely ignored ("oh, that test is always flaky")
- Bugs in production trace back to untested code paths
- Refactoring proposals are rejected because "we cannot test the changes"
- Deployment frequency is limited by test reliability

**Cost-to-fix characteristics:** Medium principal, but test debt is the prerequisite for addressing other debt safely. Paying down test debt first has a multiplier effect on all subsequent debt reduction.

### 4. Documentation Debt

**Definition:** Missing, outdated, or misleading documentation that slows understanding.

**Examples:**
- API documentation that does not match current behavior
- Architecture decision records that were never written
- Onboarding guides that reference deprecated tools or processes
- Code comments that describe what the code used to do, not what it does
- Missing runbooks for operational procedures

**Typical interest rate:** LOW and STABLE. Documentation debt has a low interest rate for experienced team members (they carry the knowledge in their heads) but a very high interest rate for new team members (onboarding time multiplied).

**Cost-to-carry indicators:**
- New developer onboarding takes 2+ months
- The same questions get asked repeatedly in team channels
- Tribal knowledge concentrates in 1-2 team members (bus factor)
- Incident response is slow because runbooks are missing or wrong

**Cost-to-fix characteristics:** Low principal per item but time-consuming in aggregate. Documentation debt is often best addressed incrementally using a "document what you learn" policy.

### 5. Infrastructure Debt

**Definition:** Build systems, deployment pipelines, monitoring, and operational tooling that impede velocity.

**Examples:**
- Manual deployment processes that take 2+ hours
- Missing monitoring and alerting for critical services
- Build times that exceed 15 minutes
- No staging environment (deploying directly to production)
- Logging that is insufficient for debugging production issues
- Infrastructure-as-code that has drifted from actual infrastructure

**Typical interest rate:** MEDIUM to HIGH and INCREASING. Infrastructure debt directly impacts deployment frequency and incident response time. As the system grows, manual processes scale linearly while automated ones scale sublinearly.

**Cost-to-carry indicators:**
- Deployment frequency is less than once per week due to process overhead
- Mean time to recovery (MTTR) exceeds 1 hour for common failure modes
- Developers spend 2+ hours per week on build/deploy issues
- Production incidents require SSH access and manual investigation

**Cost-to-fix characteristics:** Medium principal with high leverage. Infrastructure improvements benefit every developer on every deployment, so the per-sprint savings compound across the team.

### 6. Dependency Debt

**Definition:** Outdated, vulnerable, or overly-coupled external dependencies.

**Examples:**
- Framework versions more than 2 major versions behind current
- Libraries with known security vulnerabilities (CVEs)
- Dependencies that are no longer maintained
- Tight coupling to a specific version of a dependency with breaking changes pending
- Transitive dependency conflicts that prevent upgrading anything

**Typical interest rate:** LOW but PUNCTUATED. Dependency debt has near-zero interest most of the time, then spikes dramatically when a security vulnerability is disclosed or a critical upgrade becomes unavailable due to version distance.

**Cost-to-carry indicators:**
- Security scanning reports known vulnerabilities
- New libraries cannot be adopted because they conflict with pinned old versions
- Framework upgrades require rewriting significant amounts of code due to version distance
- The team avoids updating anything because "the last update broke everything"

**Cost-to-fix characteristics:** Variable. Small dependency updates have low principal. Major version upgrades (especially frameworks) can have very high principal due to breaking API changes, deprecation removals, and behavioral differences.


## Interest Rate Estimation Guide

| Category | Typical Rate | Rate Trend | Key Indicator |
|----------|-------------|------------|---------------|
| Architecture | 4-8 hrs/sprint | Increasing | Feature delivery time as % of estimate |
| Code | 2-4 hrs/sprint | Stable | Bug investigation time in affected module |
| Test | 3-6 hrs/sprint | Increasing | CI pipeline reliability, deployment frequency |
| Documentation | 1-2 hrs/sprint | Stable | New developer onboarding time |
| Infrastructure | 2-5 hrs/sprint | Increasing | Deployment frequency, MTTR |
| Dependency | 0-1 hrs/sprint (punctuated) | Spiking | Security scan results, version distance |

**How to estimate interest rate for a specific item:**

1. Identify who interacts with this debt item (which developers, on which tasks)
2. Estimate how many hours per sprint those developers lose due to this specific item
3. Determine whether the rate is increasing (more people touching the area, more complexity being added), stable (consistent usage pattern), or decreasing (area becoming less active)
4. Factor in compounding: does this debt item make other debt items more expensive?


## Cross-Category Compounding

Debt does not exist in isolation. Debt in one category increases the effective interest rate of debt in other categories.

**Test debt amplifies all other debt:**
Without adequate tests, every other form of debt remediation becomes riskier. Architecture refactoring without tests is dangerous. Code cleanup without tests may introduce regressions. Test debt is a prerequisite multiplier.

**Architecture debt amplifies code debt:**
When the architecture does not provide clear boundaries, code debt becomes harder to isolate and fix. A function with 300 lines in a well-architected module is unpleasant but fixable. The same function in a module with circular dependencies and shared state is a minefield.

**Infrastructure debt amplifies test debt:**
If the CI pipeline is slow or unreliable, developers skip tests. If deployments are manual and risky, teams deploy less frequently, which means larger changesets, which means more risk, which means more need for tests, which are being skipped because the pipeline is slow. This is a compounding cycle.

**Documentation debt amplifies onboarding cost of all other debt:**
When documentation is missing, new team members cannot distinguish deliberate-prudent debt from inadvertent-reckless debt. They do not know which patterns are intentional and which are accidental. They spend time investigating decisions that should be documented, and they may "fix" deliberate tradeoffs that were made for good reasons.

**When assessing a system, always map these compounding relationships.** A debt item with a 2 hrs/sprint direct cost may have a 6 hrs/sprint effective cost when its amplification of other debt is included. The compounding analysis often changes the priority order.
