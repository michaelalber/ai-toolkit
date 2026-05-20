# Behavioral Examples

Concrete before/after examples of tests that violate behavioral or structure-insensitive
properties, and their correct rewrites. Sourced from tdd-implementer patterns.

---

## Python

### Example: Repository Interaction

**WRONG — tests the how (implementation-coupled)**

```python
def test_saved_user_can_be_retrieved():
    repo = UserRepository(db_mock)
    user = User("alice")
    repo.save(user)
    db_mock.insert.assert_called_once_with("users", user)  # verifies the call, not the outcome
```

This test breaks if `insert` is renamed to `upsert` even though behavior is unchanged.

**RIGHT — tests the what (behavioral)**

```python
def test_saved_user_can_be_retrieved():
    repo = UserRepository(InMemoryDatabase())
    user = User("alice")
    repo.save(user)
    assert repo.find_by_name("alice") == user  # verifies the observable outcome
```

This test survives any internal rename. It can only fail if `save` stops persisting or
`find_by_name` stops finding.

---

## C# (.NET)

### Example: Order Handler

**WRONG — structure-coupled (reads private field)**

```csharp
[Fact]
public void Handle_CreatesOrder_SetsTotal()
{
    var handler = new CreateOrderHandler(repo);
    var command = new CreateOrderCommand(items: testItems);
    handler.Handle(command, CancellationToken.None);
    var order = handler._lastCreatedOrder;  // accesses private field
    order._total.Should().Be(100m);          // reads private backing field
}
```

**RIGHT — behavioral (asserts through public interface)**

```csharp
[Fact]
public async Task Handle_WithValidItems_ReturnsOrderWithCorrectTotal()
{
    var repo = new InMemoryOrderRepository();
    var handler = new CreateOrderHandler(repo);
    var command = new CreateOrderCommand(items: testItems);

    var result = await handler.Handle(command, CancellationToken.None);

    var saved = await repo.GetByIdAsync(result.OrderId);
    saved.Total.Should().Be(100m);  // asserts through the public API
}
```

---

## TypeScript

### Example: Event Publishing

**WRONG — verifies internal call (over-mocked)**

```typescript
it('publishes OrderCreated event after save', () => {
  const publisher = jest.fn();
  const handler = new CreateOrderHandler(repo, publisher);
  handler.handle(command);
  expect(publisher).toHaveBeenCalledWith(
    expect.objectContaining({ type: 'OrderCreated' })
  );  // tests that a specific internal method was called
});
```

If the handler is refactored to use an event bus instead of calling `publisher` directly,
this test breaks even if the event still gets published.

**RIGHT — tests the observable side effect**

```typescript
it('creates an OrderCreated event when order is saved', async () => {
  const eventStore = new InMemoryEventStore();
  const handler = new CreateOrderHandler(repo, eventStore);
  await handler.handle(command);
  const events = eventStore.getEventsFor(command.orderId);
  expect(events).toContainEqual(expect.objectContaining({ type: 'OrderCreated' }));
});
```

---

## The Mental Test

Before committing a test, ask: *"If I renamed every private method and field in the
class under test, would this test break?"*

- **YES** → The test is structure-coupled. Rewrite to assert on observable outcomes.
- **NO** → The test is structure-insensitive. Proceed.
