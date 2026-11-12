# <AI-Generated START>
import pytest

from semver import compare, parse, satisfies

PRECEDENCE = ["1.0.0-alpha", "1.0.0-alpha.1", "1.0.0-alpha.beta", "1.0.0-beta",
              "1.0.0-beta.2", "1.0.0-beta.11", "1.0.0-rc.1", "1.0.0"]


def test_parse_basic():
    assert parse("1.2.3") == (1, 2, 3, ())


def test_parse_prerelease_and_build():
    assert parse("1.0.0-alpha.1+build.5") == (1, 0, 0, ("alpha", "1"))


@pytest.mark.parametrize("bad", ["1.2", "1.2.3.4", "01.2.3", "v1.2.3", "1.2.3-", "a.b.c", ""])
def test_parse_invalid(bad):
    with pytest.raises(ValueError):
        parse(bad)


@pytest.mark.parametrize("lo,hi", list(zip(PRECEDENCE, PRECEDENCE[1:])))
def test_precedence_chain(lo, hi):
    assert compare(lo, hi) == -1
    assert compare(hi, lo) == 1


def test_compare_numeric_not_lexical():
    assert compare("1.10.0", "1.9.0") == 1


def test_compare_ignores_build_metadata():
    assert compare("1.0.0+a", "1.0.0+b") == 0


CASES = [
    ("1.9.9", "^1.2.3", True), ("2.0.0", "^1.2.3", False), ("1.2.2", "^1.2.3", False),
    ("0.2.9", "^0.2.3", True), ("0.3.0", "^0.2.3", False),
    ("0.0.3", "^0.0.3", True), ("0.0.4", "^0.0.3", False),
    ("1.2.9", "~1.2.3", True), ("1.3.0", "~1.2.3", False),
    ("1.5.0", ">=1.0.0 <2.0.0", True), ("2.0.0", ">=1.0.0 <2.0.0", False),
    ("1.5.0", "<1.0.0 || >=2.0.0", False), ("2.5.0", "<1.0.0 || >=2.0.0", True),
    ("0.1.0", "<1.0.0 || >=2.0.0", True),
    ("1.2.3", "1.2.3", True), ("1.2.4", "1.2.3", False), ("1.2.3", "=1.2.3", True),
    ("1.2.3+build", "1.2.3", True),
    ("1.5.0-beta.1", ">=1.0.0", False),
    ("1.2.3-beta.4", ">=1.2.3-beta.2", True),
    ("1.2.4-beta.1", ">=1.2.3-beta.2", False),
    ("1.2.3-beta.1", ">=1.2.3-beta.2", False),
]


@pytest.mark.parametrize("version,rng,expected", CASES)
def test_satisfies(version, rng, expected):
    assert satisfies(version, rng) is expected


@pytest.mark.parametrize("rng", ["", ">=", "1.0.0 ||", ">= 1.0.0"])
def test_invalid_range_raises(rng):
    with pytest.raises(ValueError):
        satisfies("1.0.0", rng)


def test_invalid_version_raises():
    with pytest.raises(ValueError):
        satisfies("1.0", ">=1.0.0")
# <AI-Generated END>
