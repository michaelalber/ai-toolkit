# <AI-Generated START>
import pytest

from cache import TTLCache


class Clock:
    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t


def test_basic_get_put():
    c = TTLCache(2, 10, Clock())
    c.put("a", 1)
    assert c.get("a") == 1
    assert c.get("x") is None


def test_lru_eviction_respects_get_recency():
    c = TTLCache(2, 10, Clock())
    c.put("a", 1)
    c.put("b", 2)
    c.get("a")
    c.put("c", 3)
    assert c.get("b") is None
    assert c.get("a") == 1
    assert c.get("c") == 3


def test_expires_exactly_at_ttl():
    clk = Clock()
    c = TTLCache(2, 10, clk)
    c.put("a", 1)
    clk.t = 9.9
    assert c.get("a") == 1
    clk.t = 10
    assert c.get("a") is None


def test_get_does_not_refresh_ttl():
    clk = Clock()
    c = TTLCache(2, 10, clk)
    c.put("a", 1)
    clk.t = 6
    c.get("a")
    clk.t = 10
    assert c.get("a") is None


def test_put_existing_updates_value_and_ttl():
    clk = Clock()
    c = TTLCache(2, 10, clk)
    c.put("a", 1)
    clk.t = 6
    c.put("a", 2)
    clk.t = 12
    assert c.get("a") == 2


def test_len_excludes_expired():
    clk = Clock()
    c = TTLCache(5, 10, clk)
    c.put("a", 1)
    clk.t = 5
    c.put("b", 2)
    clk.t = 10
    assert len(c) == 1


def test_expired_entries_purged_before_evicting_live_ones():
    clk = Clock()
    c = TTLCache(2, 10, clk)
    c.put("a", 1)
    clk.t = 5
    c.put("b", 2)
    clk.t = 10
    c.put("c", 3)
    assert c.get("b") == 2
    assert c.get("c") == 3


@pytest.mark.parametrize("cap", [0, -1])
def test_invalid_capacity(cap):
    with pytest.raises(ValueError):
        TTLCache(cap, 10)
# <AI-Generated END>
