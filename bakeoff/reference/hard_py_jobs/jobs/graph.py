"""Dependency ordering for jobs."""


class CycleError(ValueError):
    """Dependencies form a cycle. `cycle` is the path with the first job repeated at the end."""

    def __init__(self, cycle):
        self.cycle = list(cycle)
        super().__init__("dependency cycle: " + " -> ".join(self.cycle))


def _find_cycle(remaining):
    """Every remaining job has an unresolved dependency inside `remaining`, so a walk must revisit a job."""
    path, seen = [], {}
    node = min(remaining)
    while node not in seen:
        seen[node] = len(path)
        path.append(node)
        node = min(remaining[node])
    cycle = path[seen[node]:]
    start = cycle.index(min(cycle))
    cycle = cycle[start:] + cycle[:start]
    return cycle + [cycle[0]]


def topo_order(deps, priority=None):
    priority = priority or {}
    for name, d in deps.items():
        if unknown := sorted(set(d) - deps.keys()):
            raise ValueError(f"{name} depends on unknown job(s): {', '.join(unknown)}")
    remaining = {name: set(d) for name, d in deps.items()}
    order = []
    while remaining:
        ready = [n for n, d in remaining.items() if not d]
        if not ready:
            raise CycleError(_find_cycle(remaining))
        ready.sort(key=lambda n: (-priority.get(n, 0), n))
        nxt = ready[0]
        order.append(nxt)
        del remaining[nxt]
        for d in remaining.values():
            d.discard(nxt)
    return order
