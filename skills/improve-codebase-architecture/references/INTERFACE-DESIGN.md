# Interface Design Patterns

Refactoring patterns for improving module interfaces, from *A Philosophy of Software
Design* (APOSD) and related sources.

## Pattern: General-Purpose Interface

**Problem:** Interface designed for one specific use case is called everywhere, forcing
callers to adapt to its specific assumptions.

**Solution:** Redesign as a general-purpose interface. The most powerful interfaces
are simple and general — they can be used in ways their authors didn't anticipate.

```python
# Too specific: assumes files always have a path
def save_document_to_file(doc: Document, path: str) -> None: ...

# General-purpose: works with any output stream
def serialize_document(doc: Document, output: IO[bytes]) -> None: ...
```

---

## Pattern: Information Hiding at Module Boundary

**Problem:** Module exposes internal data structures; callers depend on them.
Any internal change breaks callers.

**Solution:** Define a stable interface in terms of domain concepts, not implementation types.

```python
# Leaks internal: OrderLine is an internal detail
def get_order_lines(order_id: str) -> list[OrderLine]: ...

# Hides internal: returns value objects callers actually need
def get_order_summary(order_id: str) -> OrderSummary: ...
```

---

## Pattern: Error Abstraction

**Problem:** Exceptions from third-party libraries leak through module boundary.
Callers must import and handle library-specific errors.

**Solution:** Catch and translate all external errors at the module boundary.
Only emit domain errors.

---

## Pattern: Composable Operations

**Problem:** A single large method does too much; callers can't reuse parts of it.

**Solution:** Break into small, composable operations with a high-level orchestrator.
Expose the orchestrator; make the components internal unless separately useful.

---

## Pattern: Idempotent Interface

**Problem:** Calling a method twice has different results from calling it once.
Callers must track whether they've already called the method.

**Solution:** Make operations idempotent where possible. "Create if not exists" instead
of "create" and "exists". "Apply migration" instead of "apply only if not applied".

---

## Checklist

Before finalizing an interface, verify:

- [ ] Can the interface be explained in one sentence?
- [ ] Does any parameter require the caller to know implementation details?
- [ ] Are there error types that reveal the storage backend, framework, or library?
- [ ] Must callers call methods in a specific order?
- [ ] Could two methods be merged into one without losing flexibility?
- [ ] Does the interface use domain vocabulary from CONTEXT.md?
