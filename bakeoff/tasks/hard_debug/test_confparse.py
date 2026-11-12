# <AI-Generated START>
import pytest

from confparse import load
from confparse.coerce import coerce
from confparse.lexer import strip_comment


def test_comment_stripped():
    assert strip_comment("a = 1 # note") == "a = 1 "


def test_hash_in_double_quotes_kept():
    assert strip_comment('a = "x#y" # c') == 'a = "x#y" '


def test_hash_in_single_quotes_kept():
    assert strip_comment("a = 'x#y'") == "a = 'x#y'"


def test_bool_values():
    assert coerce("false") is False
    assert coerce("TRUE") is True


def test_numbers():
    assert coerce("42") == 42 and isinstance(coerce("42"), int)
    assert coerce("-5") == -5
    assert coerce("3.14") == 3.14


@pytest.mark.parametrize("raw", ["nan", "inf", "1_000", "1e3", "0x10"])
def test_non_plain_numbers_stay_strings(raw):
    assert coerce(raw) == raw


def test_quoted_string_unquoted():
    assert coerce('"hi"') == "hi"


def test_nested_sections():
    assert load("[a.b]\nx = 1\n") == {"a": {"b": {"x": 1}}}


def test_section_header_with_trailing_comment():
    assert load("[db] # primary\nport = 5432\n") == {"db": {"port": 5432}}


DOC = """
# top comment
name = "a#b"   # trailing
debug = false
[db.primary] # main
host = 'h#1'
port = 5432
ratio = 0.5
nan = nan
"""


def test_full_document():
    assert load(DOC) == {
        "name": "a#b",
        "debug": False,
        "db": {"primary": {"host": "h#1", "port": 5432, "ratio": 0.5, "nan": "nan"}},
    }
# <AI-Generated END>
