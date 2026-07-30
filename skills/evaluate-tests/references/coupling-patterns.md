# Coupling Patterns

Language-specific examples of implementation-coupled tests and their behavioral rewrites.
Canonical source for the evaluate-tests skill.

---

## Python (pytest)

### Coupled: Mock call assertion
```python
# WRONG
def test_creates_user():
    db = MagicMock()
    service = UserService(db)
    service.create_user("alice@example.com")
    db.execute.assert_called_once_with(
        "INSERT INTO users (email) VALUES (?)", ("alice@example.com",)
    )
```
*Coupled to SQL string and parameter format. Breaks if ORM is swapped.*

```python
# RIGHT
def test_creates_user():
    db = InMemoryUserStore()
    service = UserService(db)
    service.create_user("alice@example.com")
    assert db.find_by_email("alice@example.com") is not None
```

### Coupled: Private attribute access
```python
# WRONG
def test_order_total():
    order = Order()
    order.add_item(Item(price=50))
    assert order._items[0].price == 50   # reads internal list
    assert order._total_cache == 50      # reads private cache field
```

```python
# RIGHT
def test_order_total():
    order = Order()
    order.add_item(Item(price=50))
    assert order.total() == 50           # asserts through public API
```

### Coupled: Internal call order
```python
# WRONG
def test_payment_flow():
    with patch.object(service, '_validate') as mock_v, \
         patch.object(service, '_charge') as mock_c:
        service.process_payment(100)
        mock_v.assert_called_before(mock_c)  # tests internal call order
```

```python
# RIGHT
def test_payment_accepted_when_valid():
    result = service.process_payment(valid_card, amount=100)
    assert result.status == "accepted"
    assert result.amount_charged == 100
```

---

## C# (.NET / xUnit + NSubstitute)

### Coupled: Verify internal method call
```csharp
// WRONG
[Fact]
public async Task Handle_SavesOrder()
{
    var repo = Substitute.For<IOrderRepository>();
    var handler = new CreateOrderHandler(repo);
    await handler.Handle(new CreateOrderCommand(...), CancellationToken.None);
    await repo.Received(1).AddAsync(Arg.Any<Order>(), Arg.Any<CancellationToken>());
    // Breaks if AddAsync is renamed to SaveAsync or implementation changes
}
```

```csharp
// RIGHT
[Fact]
public async Task Handle_WithValidCommand_ReturnsSavedOrderId()
{
    var repo = new InMemoryOrderRepository();
    var handler = new CreateOrderHandler(repo);
    var result = await handler.Handle(new CreateOrderCommand(...), CancellationToken.None);
    var saved = await repo.GetByIdAsync(result.OrderId);
    saved.Should().NotBeNull();
    saved!.CustomerId.Should().Be(command.CustomerId);
}
```

### Fragile: Private field assertion
```csharp
// WRONG
var order = new Order();
var field = typeof(Order).GetField("_status", BindingFlags.NonPublic | BindingFlags.Instance);
field!.GetValue(order).Should().Be(OrderStatus.Pending);
```

```csharp
// RIGHT
var order = new Order();
order.Status.Should().Be(OrderStatus.Pending);
```

---

## TypeScript (Jest / Vitest)

### Coupled: Spy on internal method
```typescript
// WRONG
it('logs the error', () => {
  const logSpy = jest.spyOn(service as any, '_logError');
  service.process({ invalid: true });
  expect(logSpy).toHaveBeenCalled();
  // Breaks if _logError is renamed or inlined
});
```

```typescript
// RIGHT
it('returns error result when input is invalid', async () => {
  const result = await service.process({ invalid: true });
  expect(result.success).toBe(false);
  expect(result.error).toMatch(/invalid/i);
});
```

### Coupled: Implementation detail in assertion
```typescript
// WRONG
it('formats the name', () => {
  const user = new User('alice', 'smith');
  expect(user['_firstName']).toBe('Alice');   // accesses private property
  expect(user['_lastName']).toBe('Smith');
});
```

```typescript
// RIGHT
it('displays formatted full name', () => {
  const user = new User('alice', 'smith');
  expect(user.displayName()).toBe('Alice Smith');
});
```

---

## Detection Heuristics

| Pattern in test | Likely classification |
|----------------|-----------------------|
| `mock.assert_called` / `mock.Received()` / `expect(spy).toHaveBeenCalled()` | COUPLED (unless testing a pure side-effect at the system boundary) |
| `_private_field` access | FRAGILE |
| `reflection` / `BindingFlags.NonPublic` | FRAGILE |
| No `assert` / `expect` statement | THEATER |
| `assert True` / `expect(true).toBe(true)` | THEATER |
| `result.Should().NotThrow()` with no further assertion | THEATER |
| Assertion on return value or observable state | PASS candidate |
