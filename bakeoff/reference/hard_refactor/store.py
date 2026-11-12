# <AI-Generated START>
class InMemoryRepo:
    def __init__(self):
        self._t, self._n = {}, {}

    def next_id(self, table):
        self._n[table] = self._n.get(table, 0) + 1
        return self._n[table]

    def put(self, table, key, value):
        self._t.setdefault(table, {})[key] = value

    def get(self, table, key):
        return self._t[table][key]

    def rows(self, table):
        return dict(self._t.get(table, {}))
# <AI-Generated END>
