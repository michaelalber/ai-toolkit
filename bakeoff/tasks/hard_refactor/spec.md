Global state (`store.DB`, the `users._ids` counter) makes this code untestable. Refactor to dependency injection, keeping behaviour the same:
- `store.InMemoryRepo` class with `next_id(table)` (1-based, per table), `put(table, key, value)`, `get(table, key)` (KeyError if missing) and `rows(table)` (returns a copy of the table dict).
- Every function in `users`, `orders` and `reports` takes a `repo` as its FIRST argument and uses only those four methods: `create_user(repo, name)`, `get_user(repo, uid)`, `place_order(repo, user_id, items)`, `user_order_totals(repo)`. Order and user ids come from `repo.next_id(table)`.
- No module-level mutable state may remain in `store`, `users`, `orders` or `reports`.
All tests in `test_di.py` must pass. Do not edit the tests.
