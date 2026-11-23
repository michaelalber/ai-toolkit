# <AI-Generated START>
"""Held-out tests: same spec as test_confparse.py, new inputs. Never copied into the model's workdir."""
import pytest

from confparse import load
from confparse.coerce import coerce
from confparse.lexer import strip_comment


def test_quote_of_other_kind_inside_quotes_does_not_close_them():
    assert strip_comment("k = \"a'#b\" # c") == "k = \"a'#b\" "
    assert strip_comment("k = 'a\"#b' # c") == "k = 'a\"#b' "


def test_whole_line_comment():
    assert strip_comment("# only a comment") == ""


@pytest.mark.parametrize("raw,expected", [("False", False), ("tRuE", True)])
def test_bool_any_case(raw, expected):
    assert coerce(raw) is expected


def test_negative_float():
    assert coerce("-0.25") == -0.25 and isinstance(coerce("-0.25"), float)


@pytest.mark.parametrize("raw", ["+5", "1.", ".5", "-inf", "NaN", "1e-3", "-", "12abc"])
def test_more_non_plain_numbers_stay_strings(raw):
    assert coerce(raw) == raw


def test_single_quotes_and_empty_quotes_removed():
    assert coerce("'x y'") == "x y"
    assert coerce('""') == ""


def test_sibling_and_parent_sections():
    assert load("[a.b]\nx = 1\n[a.c]\ny = 2\n[a]\nz = 3\n") == {"a": {"b": {"x": 1}, "c": {"y": 2}, "z": 3}}


def test_value_may_contain_equals():
    assert load('url = "a=b"\n') == {"url": "a=b"}


def test_quoted_hash_in_section_body():
    assert load("[s] # c\nk = 'v # kept' # dropped\n") == {"s": {"k": "v # kept"}}
# <AI-Generated END>
