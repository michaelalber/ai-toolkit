# Refactoring Catalog

## Composing Methods

### Extract Method/Function

**Situation**: A code fragment that can be grouped together.

**Mechanics**:
1. Create new method with intention-revealing name
2. Copy extracted code to new method
3. Identify local variables used (become parameters)
4. Identify local variables modified (become return values)
5. Replace original code with call to new method
6. Run tests

**Example**:
```python
# Before
def print_owing(self):
    # print banner
    print("*" * 20)
    print("Customer Owes")
    print("*" * 20)

    # calculate outstanding
    outstanding = 0
    for order in self.orders:
        outstanding += order.amount

    # print details
    print(f"name: {self.name}")
    print(f"amount: {outstanding}")

# After
def print_owing(self):
    self.print_banner()
    outstanding = self.calculate_outstanding()
    self.print_details(outstanding)

def print_banner(self):
    print("*" * 20)
    print("Customer Owes")
    print("*" * 20)

def calculate_outstanding(self):
    return sum(order.amount for order in self.orders)

def print_details(self, outstanding):
    print(f"name: {self.name}")
    print(f"amount: {outstanding}")
```

### Inline Method/Function

**Situation**: A method's body is as clear as its name.

**Mechanics**:
1. Check method isn't polymorphic
2. Find all calls to the method
3. Replace each call with method body
4. Delete the method
5. Run tests

### Extract Variable

**Situation**: An expression is complex or repeated.

**Mechanics**:
1. Declare a variable with clear name
2. Set it to the expression
3. Replace original expression with variable
4. Run tests

### Inline Variable

**Situation**: Variable name doesn't say more than the expression.

**Mechanics**:
1. Verify expression has no side effects
2. Replace variable uses with expression
3. Remove declaration
4. Run tests

### Replace Temp with Query

**Situation**: A temporary variable holds a calculation result.

**Mechanics**:
1. Extract the calculation to a method
2. Replace temp reads with method calls
3. Remove temp declaration
4. Run tests

## Moving Features

### Move Method

**Situation**: A method uses more features of another class.

**Mechanics**:
1. Examine features used by the method
2. Check if method should move with subclass overrides
3. Create new method in target class
4. Copy code, adjusting for new context
5. Decide how to reference target from source
6. Turn source into delegation
7. Consider removing source entirely
8. Run tests

### Move Field

**Situation**: A field is used more by another class.

**Mechanics**:
1. Create field in target class
2. Change source field to delegate
3. Update readers and writers
4. Run tests

### Extract Class

**Situation**: One class is doing work that should be two.

**Mechanics**:
1. Decide how to split responsibilities
2. Create new class
3. Create link from old to new class
4. Move fields one at a time, testing after each
5. Move methods one at a time, testing after each
6. Review interfaces, reduce if possible
7. Decide on exposure of new class

### Inline Class

**Situation**: A class isn't doing very much.

**Mechanics**:
1. Identify calls to methods on victim class
2. Create methods on target for each
3. Change all callers to use target
4. Move methods and fields, testing after each
5. Delete victim class

## Organizing Data

### Replace Primitive with Object

**Situation**: A primitive has behavior associated with it.

**Mechanics**:
1. Create class with value and getter
2. Change field to use new class
3. Create methods for behavior
4. Run tests

**Example**:
```python
# Before
class Order:
    def __init__(self):
        self.customer_name: str = ""

# After
class Customer:
    def __init__(self, name: str):
        self._name = name

    @property
    def name(self) -> str:
        return self._name

class Order:
    def __init__(self):
        self.customer: Customer = None
```

### Replace Data Value with Object

**Situation**: A data item needs additional data or behavior.

### Change Value to Reference

**Situation**: Many equal instances should be single shared instance.

### Change Reference to Value

**Situation**: Reference object is small, immutable, and awkward to manage.

### Replace Array with Object

**Situation**: An array contains different types of data.

## Simplifying Conditionals

### Decompose Conditional

**Situation**: Complex conditional expression.

**Mechanics**:
1. Extract condition to method
2. Extract then-branch to method
3. Extract else-branch to method
4. Run tests

**Example**:
```python
# Before
if date < SUMMER_START or date > SUMMER_END:
    charge = quantity * self.winter_rate + self.winter_service_charge
else:
    charge = quantity * self.summer_rate

# After
if self.is_winter(date):
    charge = self.winter_charge(quantity)
else:
    charge = self.summer_charge(quantity)
```

### Consolidate Conditional Expression

**Situation**: Multiple conditionals yield the same result.

**Mechanics**:
1. Combine conditions with logical operators
2. Extract to method with intention-revealing name
3. Run tests

### Replace Nested Conditional with Guard Clauses

**Situation**: Method has conditional behavior that doesn't clarify normal path.

**Example**:
```python
# Before
def get_pay_amount(self):
    if self.is_dead:
        result = 0
    else:
        if self.is_separated:
            result = self.separated_amount()
        else:
            if self.is_retired:
                result = self.retired_amount()
            else:
                result = self.normal_amount()
    return result

# After
def get_pay_amount(self):
    if self.is_dead:
        return 0
    if self.is_separated:
        return self.separated_amount()
    if self.is_retired:
        return self.retired_amount()
    return self.normal_amount()
```

### Replace Conditional with Polymorphism

**Situation**: Conditional that chooses different behavior based on type.

**Mechanics**:
1. Create subclasses for each leg
2. Create polymorphic method in superclass
3. Copy conditional leg to appropriate subclass
4. Replace conditional with polymorphic call
5. Run tests

## Simplifying Method Calls

### Rename Method

**Situation**: Method name doesn't reveal its purpose.

**Mechanics**:
1. Create new method with new name
2. Copy old body to new method
3. Change old method to delegate to new
4. Find all callers, change to use new name
5. Remove old method
6. Run tests

### Add Parameter

**Situation**: Method needs more information from caller.

### Remove Parameter

**Situation**: Parameter is no longer used.

### Separate Query from Modifier

**Situation**: Method returns value but also changes state.

**Mechanics**:
1. Create query method returning the value
2. Modify original to call query
3. Change callers that want value to use query
4. Remove return from modifier
5. Run tests

### Introduce Parameter Object

**Situation**: Group of parameters naturally go together.

**Example**:
```python
# Before
def amount_invoiced(start_date, end_date): ...
def amount_received(start_date, end_date): ...
def amount_overdue(start_date, end_date): ...

# After
class DateRange:
    def __init__(self, start, end):
        self.start = start
        self.end = end

def amount_invoiced(date_range): ...
def amount_received(date_range): ...
def amount_overdue(date_range): ...
```

## Dealing with Generalization

### Pull Up Method

**Situation**: Methods with identical results on subclasses.

### Push Down Method

**Situation**: Behavior only relevant to some subclasses.

### Extract Superclass

**Situation**: Classes with similar features.

### Extract Interface

**Situation**: Several clients use same subset of a class's interface.

### Collapse Hierarchy

**Situation**: Superclass and subclass are not very different.
