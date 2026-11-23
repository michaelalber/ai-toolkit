# <AI-Generated START>
"""Held-out tests: same spec as test_di.py, new inputs. Never copied into the model's workdir."""
import pytest

import orders
import reports
import store
import users


class StrictRepo:
    """Only the four protocol methods exist; any other attribute access fails the test."""

    def __init__(self):
        self.t, self.n, self.calls = {}, {}, []

    def next_id(self, table):
        self.calls.append(("next_id", table))
        self.n[table] = self.n.get(table, 0) + 1
        return self.n[table]

    def put(self, table, key, value):
        self.calls.append(("put", table))
        self.t.setdefault(table, {})[key] = value

    def get(self, table, key):
        return self.t[table][key]

    def rows(self, table):
        return dict(self.t.get(table, {}))

    def __getattr__(self, name):
        raise AssertionError(f"repo.{name} is not part of the protocol")


@pytest.fixture(params=[store.InMemoryRepo, StrictRepo])
def repo(request):
    return request.param()


def test_ids_are_per_table():
    r = store.InMemoryRepo()
    assert [r.next_id("users"), r.next_id("orders"), r.next_id("users")] == [1, 1, 2]


def test_rows_of_unknown_table_is_empty():
    assert store.InMemoryRepo().rows("nothing") == {}


def test_order_ids_are_per_repo(repo):
    other = type(repo)()
    a, b = users.create_user(repo, "ann"), users.create_user(other, "bob")
    assert orders.place_order(repo, a, [(1, 1)]) == 1
    assert orders.place_order(other, b, [(1, 1)]) == 1


def test_ids_come_from_next_id():
    r = StrictRepo()
    uid = users.create_user(r, "ann")
    orders.place_order(r, uid, [(1, 1)])
    assert ("next_id", "users") in r.calls and ("next_id", "orders") in r.calls


def test_get_unknown_user_raises(repo):
    with pytest.raises(KeyError):
        users.get_user(repo, 5)


def test_failed_order_stores_nothing(repo):
    with pytest.raises(KeyError):
        orders.place_order(repo, 1, [(1, 1)])
    assert repo.rows("orders") == {}


def test_totals_sum_across_orders(repo):
    ann = users.create_user(repo, "ann")
    cy = users.create_user(repo, "cy")
    orders.place_order(repo, ann, [(2, 3)])
    orders.place_order(repo, cy, [(7, 1)])
    orders.place_order(repo, ann, [(1, 4), (0, 9)])
    assert reports.user_order_totals(repo) == {"ann": 10, "cy": 7}
# <AI-Generated END>
