import pytest

from jobs import CycleError, backoff, run, topo_order


# --- topo_order ---------------------------------------------------------------

def test_dependencies_come_first():
    order = topo_order({"build": {"fetch"}, "fetch": set(), "test": {"build"}})
    assert order == ["fetch", "build", "test"]


def test_ties_break_alphabetically():
    assert topo_order({"c": set(), "a": set(), "b": set()}) == ["a", "b", "c"]


def test_higher_priority_runs_first_among_ready():
    assert topo_order({"a": set(), "b": set(), "c": set()}, {"c": 5, "a": 1}) == ["c", "a", "b"]


def test_priority_never_overrides_dependencies():
    assert topo_order({"a": {"b"}, "b": set()}, {"a": 100}) == ["b", "a"]


def test_unknown_dependency_is_value_error_naming_it():
    with pytest.raises(ValueError, match="ghost") as e:
        topo_order({"a": {"ghost"}})
    assert not isinstance(e.value, CycleError)


def test_self_cycle():
    with pytest.raises(CycleError) as e:
        topo_order({"a": {"a"}})
    assert e.value.cycle == ["a", "a"]


def test_cycle_path_excludes_jobs_outside_cycle():
    with pytest.raises(CycleError) as e:
        topo_order({"a": {"b"}, "b": {"c"}, "c": {"b"}, "d": set()})
    assert e.value.cycle == ["b", "c", "b"]


def test_cycle_path_starts_at_smallest_and_follows_edges():
    with pytest.raises(CycleError) as e:
        topo_order({"m": {"c"}, "c": {"q"}, "q": {"m"}})
    assert e.value.cycle == ["c", "q", "m", "c"]


def test_cycle_error_message_shows_path():
    with pytest.raises(CycleError, match="x -> y -> x"):
        topo_order({"x": {"y"}, "y": {"x"}})


# --- backoff ------------------------------------------------------------------

@pytest.mark.parametrize("attempt,expected", [(1, 0.5), (2, 1.0), (3, 2.0), (4, 4.0)])
def test_backoff_doubles_from_base(attempt, expected):
    assert backoff(attempt, base=0.5, cap=60) == expected


def test_backoff_is_capped():
    assert backoff(10, base=1, cap=5) == 5


# --- run ----------------------------------------------------------------------

class Flaky:
    """execute() stand-in: fails the first `fails[name]` calls for each job."""

    def __init__(self, fails=None):
        self.fails = dict(fails or {})
        self.calls = []

    def __call__(self, name):
        self.calls.append(name)
        if self.fails.get(name, 0) > 0:
            self.fails[name] -= 1
            raise RuntimeError(name)


def test_all_ok_runs_in_order():
    ex = Flaky()
    report = run({"b": {"a"}, "a": set()}, ex, sleep=lambda s: None)
    assert ex.calls == ["a", "b"]
    assert report == {"a": ("ok", 1), "b": ("ok", 1)}


def test_retry_then_succeed_sleeps_between_attempts():
    sleeps = []
    report = run({"a": set()}, Flaky({"a": 2}), sleep=sleeps.append, base=1, cap=30)
    assert report == {"a": ("ok", 3)}
    assert sleeps == [1, 2]


def test_no_sleep_after_final_failed_attempt():
    sleeps = []
    report = run({"a": set()}, Flaky({"a": 99}), max_attempts=3, sleep=sleeps.append, base=1, cap=30)
    assert report == {"a": ("failed", 3)}
    assert sleeps == [1, 2]


def test_failure_skips_transitive_dependents_but_not_unrelated():
    ex = Flaky({"a": 99})
    deps = {"a": set(), "b": {"a"}, "c": {"b"}, "d": set()}
    report = run(deps, ex, max_attempts=2, sleep=lambda s: None)
    assert report == {"a": ("failed", 2), "b": ("skipped", 0), "c": ("skipped", 0), "d": ("ok", 1)}
    assert "b" not in ex.calls and "c" not in ex.calls


def test_job_with_one_failed_and_one_ok_dependency_is_skipped():
    report = run({"a": set(), "b": set(), "c": {"a", "b"}}, Flaky({"b": 99}), max_attempts=1,
                 sleep=lambda s: None)
    assert report["c"] == ("skipped", 0)


def test_max_attempts_must_be_positive():
    with pytest.raises(ValueError):
        run({"a": set()}, Flaky(), max_attempts=0)


def test_cycle_propagates_before_any_execution():
    ex = Flaky()
    with pytest.raises(CycleError):
        run({"a": {"b"}, "b": {"a"}, "z": set()}, ex)
    assert ex.calls == []
