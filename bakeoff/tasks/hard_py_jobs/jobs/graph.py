"""Dependency ordering for jobs."""


class CycleError(ValueError):
    """Dependencies form a cycle. `cycle` is the path with the first job repeated at the end."""

    def __init__(self, cycle):
        self.cycle = list(cycle)
        super().__init__("dependency cycle: " + " -> ".join(self.cycle))


def topo_order(deps, priority=None):
    priority = priority or {}
    remaining = {name: set(d) for name, d in deps.items()}
    order = []
    while remaining:
        ready = [n for n, d in remaining.items() if not d]
        if not ready:
            raise CycleError([])
        ready.sort(key=lambda n: (priority.get(n, 0), n))
        nxt = ready[0]
        order.append(nxt)
        del remaining[nxt]
        for d in remaining.values():
            d.discard(nxt)
    return order
