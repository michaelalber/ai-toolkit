The `jobs` package runs named jobs in dependency order with retries. Intended behavior:

- `topo_order(deps, priority=None)`: `deps` maps every job name to the set of job names it depends on. Return all jobs so each comes after its dependencies. When several jobs are ready, the one with the **highest** `priority` (default 0) goes first; ties go to the alphabetically smallest name.
- A dependency that is not a key of `deps` raises `ValueError` naming the unknown job. This must not be a `CycleError`.
- A dependency cycle raises `CycleError` whose `.cycle` lists the cycle path along dependency edges (`a` depends on `b` gives `a -> b`), starting and ending at the alphabetically smallest job in the cycle, e.g. `["b", "c", "b"]`. A job depending on itself gives `["a", "a"]`. Jobs outside the cycle are not in the path.
- `backoff(attempt, base, cap)`: delay before retry `attempt` (1-based) is `base`, `2*base`, `4*base`, ..., never more than `cap`.
- `run(deps, execute, ...)` calls `execute(name)` in `topo_order`; an exception means the attempt failed. Each job gets up to `max_attempts` attempts, with `sleep(backoff(n))` after failed attempt `n` only if another attempt follows. Returns `{name: (status, attempts)}`, where status is `"ok"`, `"failed"` or `"skipped"`. A job is skipped (0 attempts, never executed) if any of its direct or transitive dependencies failed or was skipped. Unrelated jobs still run.

Several tests in `test_jobs.py` fail. Find and fix the root causes across the package and implement the missing cycle reporting. Do not edit the tests.
