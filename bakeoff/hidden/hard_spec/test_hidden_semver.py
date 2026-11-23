# <AI-Generated START>
"""Held-out tests: same spec as test_semver.py, new inputs. Never copied into the model's workdir."""
import pytest

from semver import compare, parse, satisfies


def test_parse_zero_and_hyphenated_prerelease():
    assert parse("0.0.0") == (0, 0, 0, ())
    assert parse("1.0.0-x-y.7+b.1") == (1, 0, 0, ("x-y", "7"))


@pytest.mark.parametrize("bad", ["1.2.03", "1.02.3", "1.2.3+", "1.2.-3", "-1.2.3", "1..3", "1.2.3-+b"])
def test_parse_more_invalid(bad):
    with pytest.raises(ValueError):
        parse(bad)


@pytest.mark.parametrize("lo,hi", [
    ("1.0.0-alpha.9", "1.0.0-alpha.10"),  # numeric, not lexical
    ("1.0.0-1", "1.0.0-a"),               # numeric < alphanumeric
    ("1.0.0-a", "1.0.0-a.b"),             # longer set wins
    ("1.0.0-Alpha", "1.0.0-alpha"),       # ASCII order
    ("1.99.99", "2.0.0"),
    ("2.0.0-rc.1", "2.0.0"),
])
def test_more_precedence(lo, hi):
    assert compare(lo, hi) == -1
    assert compare(hi, lo) == 1


def test_build_metadata_ignored_with_prerelease():
    assert compare("1.0.0-rc.1+x", "1.0.0-rc.1+y") == 0


CASES = [
    ("1.0.0", "^1.0.0", True), ("0.9.9", "^1.0.0", False),
    ("0.2.3", "^0.2.3", True), ("0.0.2", "^0.0.3", False),
    ("1.2.3", "~1.2.3", True), ("1.2.2", "~1.2.3", False),
    ("1.0.0", ">1.0.0", False), ("1.0.1", ">1.0.0", True), ("1.0.0", "<=1.0.0", True),
    ("3.0.0", "1.0.0 || 3.0.0", True),
    ("1.0.0-rc.1", "^1.0.0-rc.0", True),
    ("1.0.1-rc.1", "^1.0.0-rc.0", False),
    ("2.0.0-rc.1", "<2.0.0", False),
    ("1.2.3-beta", "1.2.3-beta || 2.0.0", True),
]


@pytest.mark.parametrize("version,rng,expected", CASES)
def test_more_satisfies(version, rng, expected):
    assert satisfies(version, rng) is expected


@pytest.mark.parametrize("rng", ["||", ">=1.0.0 ||", "^", "~ 1.2.3", ">=x.y.z", "1.0.0 || bad"])
def test_more_invalid_ranges(rng):
    with pytest.raises(ValueError):
        satisfies("1.0.0", rng)
# <AI-Generated END>
