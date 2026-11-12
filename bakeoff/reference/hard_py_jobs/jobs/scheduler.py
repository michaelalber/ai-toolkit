"""Run jobs in dependency order with retries."""
import time

from .graph import topo_order
from .retry import backoff


def run(deps, execute, *, max_attempts=3, priority=None, sleep=time.sleep, base=1.0, cap=30.0):
    if max_attempts < 1:
        raise ValueError("max_attempts must be >= 1")
    report = {}
    for name in topo_order(deps, priority):
        if any(report[d][0] != "ok" for d in deps[name]):
            report[name] = ("skipped", 0)
            continue
        for attempt in range(1, max_attempts + 1):
            try:
                execute(name)
                report[name] = ("ok", attempt)
                break
            except Exception:
                report[name] = ("failed", attempt)
                if attempt < max_attempts:
                    sleep(backoff(attempt, base, cap))
    return report
