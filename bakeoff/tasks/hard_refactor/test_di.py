# <AI-Generated START>
import itertools

import pytest

import orders
import reports
import store
import users


class FakeRepo:
    """Independent implementation of the repo protocol: proves modules use only these 4 methods."""

    def __init__(self):
        self.t, self.n = {}, {}

    def next_id(self, table):
        self.n[table] = self.n.get(table, 0) + 1
        return self.n[table]

    def put(self, table, key, value):
        self.t.setdefault(table, {})[key] = value

    def get(self, table, key):
        return self.t[table][key]

    def rows(self, table):
        return dict(self.t.get(table, {}))


@pytest.fixture(params=[store.InMemoryRepo, FakeRepo])
def repo(request):
    return request.param()


def test_user_ids_start_at_one_per_repo(repo):
    other = type(repo)()
    assert users.create_user(repo, "ann") == 1
    assert users.create_user(other, "bob") == 1
    assert users.create_user(repo, "cy") == 2


def test_get_user(repo):
    uid = users.create_user(repo, "ann")
    assert users.get_user(repo, uid) == {"name": "ann"}


def test_place_order_unknown_user_raises(repo):
    with pytest.raises(KeyError):
        orders.place_order(repo, 99, [(1, 1)])


def test_order_ids_increment(repo):
    uid = users.create_user(repo, "ann")
    assert orders.place_order(repo, uid, [(2, 3)]) == 1
    assert orders.place_order(repo, uid, [(1, 1)]) == 2


def test_report_totals(repo):
    ann = users.create_user(repo, "ann")
    bob = users.create_user(repo, "bob")
    orders.place_order(repo, ann, [(10, 2), (5, 1)])
    orders.place_order(repo, bob, [(3, 1)])
    assert reports.user_order_totals(repo) == {"ann": 25, "bob": 3}


def test_report_empty(repo):
    assert reports.user_order_totals(repo) == {}


def test_inmemory_get_missing_raises_and_rows_is_copy():
    r = store.InMemoryRepo()
    with pytest.raises(KeyError):
        r.get("users", 1)
    r.put("users", 1, {"name": "a"})
    r.rows("users").clear()
    assert r.get("users", 1) == {"name": "a"}


@pytest.mark.parametrize("mod", [store, users, orders, reports])
def test_no_module_level_mutable_state(mod):
    bad = [n for n, v in vars(mod).items()
           if not n.startswith("__") and isinstance(v, (dict, list, set, itertools.count))]
    assert bad == []
# <AI-Generated END>
