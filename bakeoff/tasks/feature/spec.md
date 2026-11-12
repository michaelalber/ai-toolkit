Implement `TTLCache` in `cache.py` (currently a stub). Rules:
- `TTLCache(capacity, ttl, clock=time.monotonic)`; `capacity < 1` raises `ValueError`.
- `get(key)` returns the value or `None`; a successful get marks the key most-recently-used but does NOT extend its TTL.
- `put(key, value)` inserts or updates (update resets TTL and recency). When over capacity, evict the least-recently-used live entry, after purging expired entries.
- An entry expires when `clock() - stored_at >= ttl`.
- `len(cache)` counts only live (unexpired) entries.
All tests in `test_cache.py` must pass. Do not edit the tests.
