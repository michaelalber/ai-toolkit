# Module Deepening Strategies

How to take a shallow module and make it deeper — hiding more complexity behind a simpler interface.

## What makes a module shallow?

A shallow module has an interface that is nearly as complex as its implementation.
Callers must understand too much to use it correctly.

Test: could you replace this module with its implementation at every call site with
minimal refactoring? If yes, the module is too shallow.

## Deepening Strategies

### 1. Push sequencing down

**Symptom:** Callers must call methods in order (`init()` → `connect()` → `query()`).
**Fix:** The module manages its own lifecycle. Callers call one method.

```python
# Shallow: caller manages lifecycle
client = DbClient()
client.connect()  # must call before query
result = client.query(sql)
client.disconnect()  # must call after

# Deep: module manages lifecycle
with DbClient() as client:
    result = client.query(sql)
```

### 2. Absorb error handling

**Symptom:** Callers must handle internal error types that reveal implementation details.
**Fix:** Module translates internal errors to domain-appropriate errors.

```python
# Shallow: caller must know about S3Error
try:
    url = storage.upload(file)
except S3Error as e:  # leaks the storage backend
    ...

# Deep: caller sees only domain errors
try:
    url = storage.upload(file)
except StorageError as e:  # backend-agnostic
    ...
```

### 3. Merge related methods

**Symptom:** Two methods are always called together; callers must combine them.
**Fix:** Create a single method that does both.

```python
# Shallow: caller always does both
token = auth.create_token(user_id)
auth.store_token(user_id, token)

# Deep: one operation
token = auth.issue_token(user_id)
```

### 4. Internalize configuration

**Symptom:** Callers pass the same configuration boilerplate on every call.
**Fix:** Module reads config once at construction; callers pass only what varies.

### 5. Create a higher-level method

**Symptom:** A common workflow requires 5 method calls in the right order.
**Fix:** Add a method that encapsulates the workflow.

## When NOT to deepen

- When callers genuinely need different configurations per call
- When hiding the detail would make error debugging impossible
- When the module is already deep and adding more behavior would violate SRP
