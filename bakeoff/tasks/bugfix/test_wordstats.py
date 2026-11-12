# <AI-Generated START>
from wordstats import top_n


def test_case_insensitive():
    assert top_n("The the THE cat", 1) == [("the", 3)]


def test_punctuation_ignored():
    assert top_n("hi, hi! hi.", 1) == [("hi", 3)]


def test_ties_alphabetical():
    assert top_n("b a c", 3) == [("a", 1), ("b", 1), ("c", 1)]


def test_n_zero():
    assert top_n("a b", 0) == []


def test_apostrophe_kept():
    assert top_n("don't don't stop", 1) == [("don't", 2)]
# <AI-Generated END>
