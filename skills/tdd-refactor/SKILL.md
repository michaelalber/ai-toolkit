---
name: tdd-refactor
description: Safely refactor code while keeping tests green (REFACTOR phase). Use when tests pass and you want to improve code structure without changing behavior.
---

# TDD Refactor (REFACTOR Phase)

> "Refactoring is a disciplined technique for restructuring an existing body of code, altering its internal structure without changing its external behavior."
> — Martin Fowler

## Core Philosophy

The REFACTOR phase improves code quality while maintaining behavior. Tests are your safety net — if they stay green, the behavior is preserved.

**The Green-to-Green Rule:**
- Start with all tests passing
- Make one small change
- Run tests
- If green, continue or commit
- If red, immediately revert

## Kent Beck's 12 Test Desiderata (REFACTOR Phase Focus)

| Property | REFACTOR Phase Application |
|----------|---------------------------|
| **Structure-insensitive** | Tests should survive refactoring |
| **Behavioral** | Tests verify behavior, not implementation |
| **Fast** | Quick feedback for rapid refactor cycles |
| **Isolated** | Changes shouldn't cascade test failures |
| **Inspiring** | Confidence to make changes |

## Pre-Flight Check

**BEFORE any refactoring:**

```
Pre-Flight Verification:
├── All tests passing?
│   └── NO → STOP. Still in GREEN phase.
│   └── YES → Continue
├── Tests cover the code being refactored?
│   └── NO → Consider adding characterization tests first
│   └── YES → Continue
├── Working state committed/saved?
│   └── NO → Commit or stash current state
│   └── YES → Proceed to refactor
```

## The Refactoring Rhythm

```
1. Identify smell or improvement
2. Plan smallest step
3. Make the change
4. Run tests
5. If GREEN: commit (optional) or continue
6. If RED: revert immediately
7. Repeat until satisfied
```

## Code Smell Catalog

### Smells to Look For

| Smell | Description | Refactoring |
|-------|-------------|-------------|
| **Duplication** | Same code in multiple places | Extract Method/Function |
| **Long Method** | Method doing too much | Extract Method |
| **Long Parameter List** | Too many parameters | Introduce Parameter Object |
| **Feature Envy** | Method uses another class's data extensively | Move Method |
| **Data Clumps** | Same data groups appear together | Extract Class |
| **Primitive Obsession** | Overuse of primitives | Replace with Value Object |
| **Divergent Change** | One class changed for multiple reasons | Extract Class |
| **Shotgun Surgery** | One change requires many class edits | Move Method/Field |
| **Magic Numbers** | Unexplained numeric literals | Extract Constant |
| **Dead Code** | Unused code | Delete it |

### When NOT to Refactor

- When tests are failing
- When you don't understand the code
- When refactoring would change behavior
- When under time pressure (do it later)
- When the code will be deleted soon

## Safe Refactoring Recipes

### Extract Method/Function

**Before:**
```python
def process_order(order):
    # validate
    if order.total < 0:
        raise ValueError("Invalid total")
    if not order.items:
        raise ValueError("No items")

    # calculate tax
    tax = order.total * 0.1

    # apply discount
    if order.total > 100:
        discount = order.total * 0.05
    else:
        discount = 0

    return order.total + tax - discount
```

**After (one step at a time):**
```python
def process_order(order):
    validate_order(order)
    tax = calculate_tax(order)
    discount = calculate_discount(order)
    return order.total + tax - discount

def validate_order(order):
    if order.total < 0:
        raise ValueError("Invalid total")
    if not order.items:
        raise ValueError("No items")

def calculate_tax(order):
    return order.total * 0.1

def calculate_discount(order):
    if order.total > 100:
        return order.total * 0.05
    return 0
```

**Key:** Extract one function at a time, run tests between each.

### Rename

**Before:**
```typescript
function calc(x: number, y: number): number {
    return x + y;
}
```

**After:**
```typescript
function calculateSum(firstNumber: number, secondNumber: number): number {
    return firstNumber + secondNumber;
}
```

**Key:** Use IDE refactoring tools when available. Run tests after.

### Extract Variable

**Before:**
```python
if user.age >= 18 and user.country == "US" and user.has_id:
    allow_purchase()
```

**After:**
```python
is_adult = user.age >= 18
is_us_resident = user.country == "US"
has_valid_id = user.has_id

if is_adult and is_us_resident and has_valid_id:
    allow_purchase()
```

### Inline Variable

**Before:**
```typescript
const basePrice = product.price;
const result = basePrice * quantity;
return result;
```

**After:**
```typescript
return product.price * quantity;
```

**Key:** Only inline if it improves clarity.

### Replace Conditional with Polymorphism

**Before:**
```python
def calculate_pay(employee):
    if employee.type == "hourly":
        return employee.hours * employee.rate
    elif employee.type == "salaried":
        return employee.salary / 12
    elif employee.type == "contractor":
        return employee.invoice_amount
```

**After:**
```python
class HourlyEmployee:
    def calculate_pay(self):
        return self.hours * self.rate

class SalariedEmployee:
    def calculate_pay(self):
        return self.salary / 12

class Contractor:
    def calculate_pay(self):
        return self.invoice_amount
```

**Key:** This is a larger refactoring. Do it in steps, with tests between each.

## Workflow

### Step 1: Verify Green State

Run all tests, confirm passing.

### Step 2: Identify One Improvement

Pick the smallest, most obvious improvement:
- Remove obvious duplication
- Improve a confusing name
- Extract a long method

### Step 3: Make the Change

Apply the refactoring. Be surgical.

### Step 4: Run Tests

Execute the full test suite immediately.

### Step 5: Evaluate

- **GREEN**: Change is safe. Commit or continue.
- **RED**: Revert immediately. Analyze what went wrong.

### Step 6: Repeat or Exit

Continue improving, or decide "good enough" and exit to next RED.

## Output Template

```markdown
### REFACTOR Phase

**Starting state**: All tests passing (N tests)

**Smell identified**: [e.g., Duplication in calculate methods]
**Refactoring**: [e.g., Extract Method - create shared calculation helper]

**Change made**:
[brief description or code diff]

**Verification**:
- Tests run: Yes
- Result: All passing (N tests)
- Behavior preserved: Yes

**Continue refactoring?**: [Yes - next smell | No - code is clean]

<tdd-state>
phase: REFACTOR  (or RED if done)
...
</tdd-state>
```

## AI Discipline Rules

### CRITICAL: Green-to-Green Only

Never make a change that breaks tests:
1. Run tests before refactoring
2. Make ONE small change
3. Run tests after
4. If red, REVERT (don't try to fix)

### CRITICAL: No Behavior Changes

During refactoring:
- Same inputs must produce same outputs
- No new features
- No bug fixes (those need tests first)
- No "improvements" to behavior

### CRITICAL: One Refactoring at a Time

Resist combining refactorings:
- Don't rename AND extract in one step
- Don't move AND modify
- Each change should be independently revertible

### CRITICAL: Tests Are the Arbiter

If tests pass, the refactoring is valid.
If tests fail, the refactoring is invalid (or tests are implementation-coupled).

### CRITICAL: Know When to Stop

Refactoring can continue indefinitely. Stop when:
- Code is "clean enough"
- Diminishing returns on improvements
- Ready to add new functionality

## Stack-Specific Guidance

See reference files for language-specific patterns:
- [Refactoring Catalog](references/refactoring-catalog.md) - Comprehensive refactoring list
- [Code Smells](references/code-smells.md) - Detailed smell descriptions

## Common Refactoring Errors

| Error | Why It's Wrong | Correct Approach |
|-------|----------------|------------------|
| Refactoring with red tests | No safety net | Fix tests first |
| Multiple changes at once | Can't isolate failures | One at a time |
| Fixing bugs during refactor | Changes behavior | Write test for bug first |
| Adding features during refactor | Changes behavior | Complete cycle, then new RED |
| Not running tests after each change | Delayed feedback | Test after every change |

## When Tests Break During Refactoring

If tests fail after a refactoring:

1. **First instinct: REVERT**
   - Use `git checkout` or undo
   - Return to green state

2. **Analyze why:**
   - Did you accidentally change behavior?
   - Is the test coupled to implementation?
   - Was the refactoring too large?

3. **If test is implementation-coupled:**
   - Consider if the test is testing the right thing
   - May need to refactor the test too
   - Do test refactoring in a separate step

4. **Try again with smaller steps:**
   - Break the refactoring into smaller pieces
   - Verify green after each piece
