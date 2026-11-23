# <AI-Generated START>
"""Held-out tests: same spec as test_jobs.py, new inputs. Never copied into the model's workdir."""
import pytest

from jobs import CycleError, backoff, run, topo_order


def test_diamond():
    assert topo_order({"d": {"b", "c"}, "b": {"a"}, "c": {"a"}, "a": set()}) == ["a", "b", "c", "d"]


def test_priority_applies_each_time_jobs_become_ready():
    assert topo_order({"a": set(), "b": set(), "c": {"a"}}, {"c": 10, "b": 1}) == ["b", "a", "c"]


def test_negative_priority_goes_last():
    assert topo_order({"x": set(), "y": set()}, {"x": -1}) == ["y", "x"]


def test_empty_graph():
    assert topo_order({}) == []


def test_unknown_dependency_on_a_later_job():
    with pytest.raises(ValueError, match="phantom") as e:
        topo_order({"a": set(), "b": {"a", "phantom"}})
    assert not isinstance(e.value, CycleError)


def test_three_cycle_follows_edges_from_smallest():
    with pytest.raises(CycleError, match="x -> z -> y -> x") as e:
        topo_order({"z": {"y"}, "y": {"x"}, "x": {"z"}})
    assert e.value.cycle == ["x", "z", "y", "x"]


def test_cycle_reached_through_a_tail():
    with pytest.raises(CycleError) as e:
        topo_order({"a": {"b"}, "b": {"c"}, "c": {"d"}, "d": {"c"}})
    assert e.value.cycle == ["c", "d", "c"]


@pytest.mark.parametrize("attempt,base,cap,expected", [
    (1, 2, 100, 2), (3, 2, 100, 8), (6, 0.25, 3, 3), (1, 5, 3, 3)])
def test_more_backoff(attempt, base, cap, expected):
    assert backoff(attempt, base=base, cap=cap) == expected


class Flaky:
    def __init__(self, fails=None, exc=RuntimeError):
        self.fails, self.exc, self.calls = dict(fails or {}), exc, []

    def __call__(self, name):
        self.calls.append(name)
        if self.fails.get(name, 0) > 0:
            self.fails[name] -= 1
            raise self.exc(name)


def test_single_attempt_never_sleeps():
    sleeps = []
    assert run({"a": set()}, Flaky({"a": 9}), max_attempts=1, sleep=sleeps.append) == {"a": ("failed", 1)}
    assert sleeps == []


def test_sleeps_are_capped():
    sleeps = []
    report = run({"a": set()}, Flaky({"a": 3}), max_attempts=4, sleep=sleeps.append, base=1, cap=2)
    assert report == {"a": ("ok", 4)}
    assert sleeps == [1, 2, 2]


def test_any_exception_type_is_a_failed_attempt():
    report = run({"a": set()}, Flaky({"a": 1}, exc=ValueError), sleep=lambda s: None)
    assert report == {"a": ("ok", 2)}


def test_skip_propagates_through_a_diamond():
    ex = Flaky({"a": 9})
    deps = {"a": set(), "b": {"a"}, "c": {"a"}, "d": {"b", "c"}, "e": set()}
    report = run(deps, ex, max_attempts=2, sleep=lambda s: None)
    assert report == {"a": ("failed", 2), "b": ("skipped", 0), "c": ("skipped", 0),
                      "d": ("skipped", 0), "e": ("ok", 1)}
    assert ex.calls == ["a", "a", "e"]
# <AI-Generated END>
