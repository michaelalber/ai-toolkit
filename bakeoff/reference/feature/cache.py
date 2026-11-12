# <AI-Generated START>
import time
from collections import OrderedDict


class TTLCache:
    def __init__(self, capacity, ttl, clock=time.monotonic):
        if capacity < 1:
            raise ValueError("capacity must be >= 1")
        self.capacity, self.ttl, self.clock = capacity, ttl, clock
        self._d = OrderedDict()  # key -> (value, stored_at), LRU first

    def _purge(self):
        now = self.clock()
        for k in [k for k, (_, t) in self._d.items() if now - t >= self.ttl]:
            del self._d[k]

    def get(self, key):
        self._purge()
        if key not in self._d:
            return None
        self._d.move_to_end(key)
        return self._d[key][0]

    def put(self, key, value):
        self._purge()
        self._d[key] = (value, self.clock())
        self._d.move_to_end(key)
        while len(self._d) > self.capacity:
            self._d.popitem(last=False)

    def __len__(self):
        self._purge()
        return len(self._d)
# <AI-Generated END>
