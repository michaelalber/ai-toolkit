# Refactoring Priorities

## Overview

This reference provides a structured framework for prioritizing refactoring work by business impact rather than aesthetic preference. Use it to evaluate candidate refactorings, build business cases, and make defensible decisions about where to invest limited refactoring time.

---

## 1. Priority Framework

### The Three Axes

Every refactoring candidate is evaluated on three axes:

```
Priority Score = Severity x Change Frequency x Risk of Bug

Where:
  Severity:         How bad is this smell? (1-5 scale)
  Change Frequency: How often does this code change? (1-5 scale)
  Risk of Bug:      How likely is this smell to cause a defect? (1-5 scale)

Adjusted Priority = Priority Score x (1 - Test Coverage Factor)

Where:
  Test Coverage Factor: 0.0 (no tests) to 0.5 (comprehensive tests)
  Tests reduce risk but never eliminate it -- max reduction is 50%.
```

### Severity Scale

| Level | Score | Definition | Example |
|-------|-------|------------|---------|
| Critical | 5 | Actively causes or will imminently cause production defects. Data corruption, race conditions, security vulnerabilities. | Shared mutable state accessed concurrently without synchronization in a payment handler. |
| High | 4 | Significantly impedes development velocity or causes intermittent defects. Changes to this code regularly produce bugs. | Shotgun Surgery: every pricing rule change requires modifying 4 files, and 1 in 5 changes misses a file. |
| Medium | 3 | Slows development and increases cognitive load. New team members struggle with this code. Bugs are possible but not frequent. | Long Parameter List of 8 parameters on a method called from 12 places. Adding a parameter requires updating all call sites. |
| Low | 2 | Minor inconvenience. Code works correctly but is not as clean as it could be. Impact is limited to readability. | Comments explaining "what" the code does rather than "why." Redundant but not harmful. |
| Cosmetic | 1 | Style preference. No measurable impact on correctness, velocity, or maintainability. Reasonable engineers would disagree on whether this is even a problem. | Variable named `dt` instead of `dateTime` in a 10-line method where context is unambiguous. |

### Change Frequency Scale

| Level | Score | Definition | How to Measure |
|-------|-------|------------|----------------|
| Hot | 5 | Modified multiple times per sprint. Active development area. | `git log --since="3 months ago" --oneline -- [file]` shows 15+ commits |
| Warm | 4 | Modified every sprint or two. Regular feature work touches this code. | 8-14 commits in 3 months |
| Occasional | 3 | Modified once a month or quarterly. Changes happen but are not frequent. | 3-7 commits in 3 months |
| Rare | 2 | Modified once or twice a year. Stable code that works. | 1-2 commits in 3 months |
| Cold | 1 | Has not been modified in over a year. Effectively frozen. | 0 commits in 3 months. Last change was 12+ months ago. |

### Risk of Bug Scale

| Level | Score | Definition | Indicators |
|-------|-------|------------|------------|
| Near-Certain | 5 | This smell has already caused bugs or will cause bugs on the next change. The defect is latent. | Past incidents traced to this code. Race conditions. Incorrect assumptions baked into logic. |
| Likely | 4 | A developer making a reasonable change to this code has a high probability of introducing a defect. | Complex branching without tests. Implicit ordering dependencies. Hidden side effects. |
| Possible | 3 | A defect could result from changes, especially by developers unfamiliar with the codebase. | Moderate complexity. Some test coverage but gaps in edge cases. Non-obvious coupling. |
| Unlikely | 2 | A defect is possible but would require an unusual or careless change. | Well-tested code with a structural smell. The smell is real but well-contained. |
| Remote | 1 | A defect from this smell is theoretically possible but practically implausible. | Cosmetic smell in stable, well-tested code. The "defect" would be a style violation, not a behavior change. |

---

## 2. Priority Matrix with Examples

### Critical Priority (Score 50-125)

These refactorings prevent production incidents. Do them immediately.

| Smell | Context | Severity | Frequency | Risk | Score | Business Impact |
|-------|---------|----------|-----------|------|-------|-----------------|
| Feature Envy with mutation | Payment service, changes weekly | 5 | 5 | 5 | 125 | Method in OrderService mutates PaymentDetails fields directly. Last month a developer changed PaymentDetails validation and did not know OrderService was bypassing it. Result: $12K in incorrect charges before detection. |
| Circular dependency | Auth module <-> User module, both change frequently | 5 | 4 | 4 | 80 | Cannot deploy auth changes without deploying user changes simultaneously. Deployment coupling caused 2-hour rollback last quarter when a user module change broke auth. |
| Long Method with branching | Discount calculation, changes quarterly for promotions | 5 | 3 | 5 | 75 | 200-line method with 14 branches. Cyclomatic complexity of 22. Every promotion change is a 3-day effort with mandatory manual testing because automated tests cannot isolate branches. |

### High Priority (Score 20-49)

These refactorings significantly improve development velocity. Schedule them within 1-2 sprints.

| Smell | Context | Severity | Frequency | Risk | Score | Business Impact |
|-------|---------|----------|-----------|------|-------|-----------------|
| Shotgun Surgery | Pricing rules spread across 4 files | 4 | 4 | 3 | 48 | Every pricing change requires modifying PriceCalculator, DiscountEngine, TaxService, and InvoiceGenerator. Average PR for a pricing change: 340 lines. Average review time: 4 hours. Localized change would be 60 lines, 45-minute review. |
| Divergent Change | UserService handles auth, profile, preferences, notifications | 4 | 5 | 2 | 40 | Four developers frequently have merge conflicts in UserService. Average conflict resolution time: 30 minutes per instance, happening 3x per sprint. Total: 6 hours/sprint of wasted team time. |
| Inappropriate Intimacy | ReportGenerator directly accesses OrderRepository internals | 4 | 3 | 3 | 36 | ReportGenerator breaks every time OrderRepository's internal data structure changes. This has caused 3 bug tickets in the last 2 quarters. |

### Medium Priority (Score 8-19)

These refactorings are worth doing when working in the area. Do not schedule dedicated time.

| Smell | Context | Severity | Frequency | Risk | Score | Business Impact |
|-------|---------|----------|-----------|------|-------|-----------------|
| Long Parameter List | CreateOrder(customerId, items, discount, tax, shipping, currency, locale, warehouse) | 3 | 3 | 2 | 18 | 8 parameters. Every new order option requires adding a parameter to 12 call sites. Developers occasionally swap parameters of the same type. |
| Data Clumps | (firstName, lastName, email) passed together to 6 methods | 3 | 2 | 2 | 12 | Mild inconvenience. Extract a CustomerInfo value object when next modifying these methods. |
| Primitive Obsession | Money represented as decimal throughout financial calculations | 3 | 3 | 3 | 27 | Rounding errors in currency conversion. Not yet caused a production issue but accumulated discrepancies appear in monthly reconciliation reports. |

### Low Priority (Score 3-7)

Address only if you are already modifying the code for another reason.

| Smell | Context | Severity | Frequency | Risk | Score | Business Impact |
|-------|---------|----------|-----------|------|-------|-----------------|
| Comments explaining "what" | Migration script run once during deployment | 2 | 1 | 1 | 2 | No impact. This script runs once and is archived. |
| Switch statement (3 cases) | Enum-based routing in a stable utility | 2 | 1 | 2 | 4 | Works correctly. Three cases are manageable. If it grows to 8+ cases, revisit. |

### Do Not Refactor (Score 1-2)

The cost of the refactoring exceeds the cost of the smell.

| Smell | Context | Why Not | Score |
|-------|---------|---------|-------|
| Naming preference | `dt` vs `dateTime` in a 10-line helper method | Context makes the meaning clear. Renaming provides zero measurable benefit. | 1 |
| Import ordering | Alphabetical vs. grouped imports | Automate with a formatter. Never spend human time on this. | 1 |
| Formatting variation | Braces on same line vs. next line in a legacy module | Apply a formatter once if it bothers you. Do not review or discuss it. | 1 |

---

## 3. Business Impact Categories

### Bugs (Defect Rate)

**Measurement**: Number of bug tickets per quarter traced to this module.

**How to build the case**: Query your issue tracker for bugs tagged to the module. Calculate the average time to diagnose and fix. Multiply by developer hourly cost.

```
Example:
  Module: OrderDiscountCalculator
  Bugs in last 4 quarters: 2, 3, 1, 4 (average: 2.5/quarter)
  Average time to diagnose + fix: 6 hours
  Developer hourly cost (loaded): $85/hour
  Quarterly cost of bugs: 2.5 * 6 * $85 = $1,275/quarter
  Annual cost: $5,100

  Refactoring cost: 16 hours * $85 = $1,360
  Payback period: ~3.2 months
```

### Onboarding Time

**Measurement**: How long it takes a new team member to make their first change to this module.

**How to build the case**: Track the time from "new developer assigned first task in this module" to "PR merged." Compare with the team average for other modules.

```
Example:
  Module: LegacyAuthService
  Average time for new developer to complete first task: 3 days
  Average across other modules: 0.5 days
  Excess onboarding cost per developer: 2.5 days * 8 hours * $85 = $1,700
  New developers per year touching this module: 4
  Annual cost: $6,800

  Refactoring cost: 24 hours * $85 = $2,040
  Payback period: ~3.6 months
```

### Development Velocity

**Measurement**: Average time to complete a change in this module vs. team baseline.

**How to build the case**: Compare PR cycle time (open to merge) for this module vs. the team average. Multiply the excess by the number of changes per quarter.

```
Example:
  Module: PricingEngine
  Average PR cycle time: 12 hours (team average: 3 hours)
  Excess per change: 9 hours
  Changes per quarter: 8
  Quarterly cost: 8 * 9 * $85 = $6,120
  Annual cost: $24,480

  Refactoring cost: 40 hours * $85 = $3,400
  Payback period: ~2 months
```

### Incident Rate

**Measurement**: Production incidents caused by or related to this module.

**How to build the case**: Count incidents, categorize by severity, and calculate the cost including engineer on-call time, customer impact, and reputation damage.

```
Example:
  Module: PaymentGatewayAdapter
  Incidents in last year: 3 (1 Sev-1, 2 Sev-2)
  Average Sev-1 cost (including customer impact): $15,000
  Average Sev-2 cost: $3,000
  Annual incident cost: $15,000 + (2 * $3,000) = $21,000

  Refactoring cost: 32 hours * $85 = $2,720
  Payback period: ~1.6 months
```

---

## 4. Building a Refactoring Business Case

### The One-Page Format

```
REFACTORING PROPOSAL: [Module Name]

PROBLEM:
[One sentence describing the smell and its measurable business impact.]

COST OF INACTION (annual):
  - Bug rate: [N] bugs/quarter, costing $[X]/year
  - Velocity tax: [N] extra hours/change, costing $[X]/year
  - Incident risk: [N] incidents/year at $[X] average cost
  TOTAL ANNUAL COST OF INACTION: $[X]

COST OF REFACTORING:
  - Estimated effort: [N] hours
  - Estimated cost: $[X]

PAYBACK PERIOD: [N] months

PLAN:
  - Step 1: [action] ([N] hours)
  - Step 2: [action] ([N] hours)
  - Step 3: [action] ([N] hours)

RISK: [Low/Medium/High]
  Mitigated by: [test coverage / incremental approach / feature flag]

MEASUREMENT:
  Before: [metric = current value]
  After (expected): [metric = target value]
  Measured at: [date, 1 month after completion]
```

### What Makes a Business Case Fail

| Failure Mode | Example | Fix |
|-------------|---------|-----|
| No data | "This code is bad and should be refactored." | Attach bug counts, PR cycle times, incident reports. |
| No comparison | "This refactoring will cost 20 hours." | "This refactoring costs 20 hours. Not refactoring costs 50 hours/year in excess development time." |
| No measurement plan | "After refactoring, the code will be cleaner." | "After refactoring, average PR cycle time for this module should drop from 12 hours to 4 hours. We will measure this 4 weeks post-refactoring." |
| Scope undefined | "We need to refactor the auth module." | "We will extract the token validation logic from AuthService into a dedicated TokenValidator class. Scope: 3 methods, estimated 8 hours." |
| No risk assessment | "Let's refactor it next sprint." | "Risk: Medium. This code has 45% test coverage. Step 1 is adding characterization tests (4 hours) before structural changes." |

---

## 5. When NOT to Refactor

### Stable Code

If the code has not changed in 6+ months, has no open bugs, and has no planned modifications, leave it alone. Ugly stable code is better than pretty unstable code. The act of refactoring introduces risk. That risk is only justified if the code is actively causing problems or will be modified soon.

**Exception**: If the stable code is about to enter a high-change period (e.g., a planned feature touches this module), refactor proactively before the feature work begins.

### Code Without Tests

Never refactor code that has no tests. The first refactoring of untested code is always "add tests." If there is no time for both tests and refactoring, add the tests and stop. Tests without refactoring are valuable (they enable future refactoring safely). Refactoring without tests is gambling (you cannot verify behavior is preserved).

**Exception**: If the refactoring IS adding tests (e.g., extracting a method to make it testable), that is the right first step.

### Code About to Be Replaced

If the module is scheduled for replacement within 2-3 sprints, do not refactor it. The refactoring effort will be thrown away when the replacement ships. Invest in the replacement instead.

**Exception**: If the replacement timeline is uncertain or the module is causing active production issues, minimal targeted refactoring to stop the bleeding is justified.

### When You Cannot Define "Done"

If you cannot articulate what the refactored code looks like, you are not ready to refactor. "Make it cleaner" is not a plan. "Extract the validation logic into a dedicated Validator class with these 4 methods" is a plan. Vague refactoring goals lead to scope creep.

### When the Team Disagrees on Approach

If the team cannot agree on the refactoring approach within a time-boxed discussion (15-30 minutes), postpone the refactoring. Refactoring by committee produces inconsistent code. Either one person owns the refactoring with a clear plan, or it waits until there is alignment.

---

## 6. Time-Boxing Refactoring Work

### The Time-Box Protocol

Every refactoring task must have a time-box defined before work begins:

```
REFACTORING TIME-BOX

Task: [specific refactoring action]
Budget: [N] hours
Hard stop: [date/time]

Scope:
  IN: [exactly what will be changed]
  OUT: [explicitly what will NOT be changed, even if tempting]

Checkpoint at 50% time:
  [ ] Am I on track to finish within budget?
  [ ] Has scope crept? If yes, what did I add that was not in the plan?
  [ ] Should I stop early and ship what I have?

Exit conditions:
  - All existing tests pass
  - No behavior changes (verified by tests)
  - PR is reviewable (under 400 lines changed)
  - If not complete at hard stop, ship what is done and file a follow-up ticket
```

### Recommended Time-Box Sizes

| Refactoring Type | Recommended Budget | Notes |
|-----------------|-------------------|-------|
| Rename (variable, method, class) | 30 minutes | Should be mostly automated. If it takes longer, coupling is the real problem. |
| Extract Method | 1-2 hours | Includes writing a test for the extracted method if one does not exist. |
| Extract Class | 2-4 hours | Includes moving tests and updating call sites. |
| Replace Conditional with Polymorphism | 4-8 hours | Includes creating the type hierarchy and updating all switch/if-else sites. |
| Break Circular Dependency | 4-16 hours | Highly variable. Requires introducing interfaces or reorganizing modules. |
| Introduce Parameter Object | 1-2 hours | Extract a value object for a long parameter list. Update call sites. |
| Remove Shotgun Surgery | 8-24 hours | Consolidate scattered logic. Requires understanding all touch points. |
| Decompose Large Module | 16-40 hours | Break a god class into cohesive smaller classes. High risk without tests. |

### What to Do When Time Runs Out

1. Stop. Do not extend the time-box.
2. Ensure all tests pass with the changes you have made so far.
3. Commit and create a PR for the completed portion.
4. File a follow-up ticket for the remaining work with the updated scope.
5. In the PR description, note what was completed and what remains.
6. Ship the partial improvement. Partial improvement is still improvement.
