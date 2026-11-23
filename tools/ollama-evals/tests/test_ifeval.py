"""IFEval-subset checks: one pass and one fail case per instruction type, plus the scorer."""

import pytest

from ollama_evals.scorers import score_output
from ollama_evals.scorers.ifeval import CHECKS, check

# (instruction id, kwargs, response that follows it, response that does not)
CASES = [
    ("keywords:existence", {"keywords": ["cache", "TTL"]},
     "A cache entry expires after its ttl.", "A cache entry expires."),
    ("keywords:frequency", {"keyword": "test", "frequency": 3, "relation": "at least"},
     "Test, test and TEST.", "One test only."),
    ("keywords:frequency", {"keyword": "bug", "frequency": 2, "relation": "less than"},
     "One bug.", "bug bug"),
    ("keywords:forbidden_words", {"forbidden_words": ["simply", "just"]},
     "Run the command; justification follows.", "Just run it."),
    ("keywords:letter_frequency", {"letter": "z", "let_frequency": 2, "let_relation": "at least"},
     "Zero zones.", "Zero."),
    ("length_constraints:number_paragraphs", {"num_paragraphs": 2},
     "First.\n***\nSecond.", "First.\n***\nSecond.\n***\nThird."),
    ("length_constraints:number_words", {"num_words": 5, "relation": "less than"},
     "Four words right here.", "This sentence has six words total."),
    ("length_constraints:number_words", {"num_words": 3, "relation": "at least"},
     "it's three words", "two words"),
    ("length_constraints:nth_paragraph_first_word",
     {"num_paragraphs": 2, "nth_paragraph": 2, "first_word": "however"},
     "Intro.\n\n\"However, the second.", "Intro.\n\nBut the second."),
    ("detectable_content:number_placeholders", {"num_placeholders": 2},
     "Dear [name], see [address].", "Dear [name]."),
    ("detectable_content:postscript", {"postscript_marker": "P.S."},
     "Body.\n\nP.S. one more thing", "Body only."),
    ("detectable_content:postscript", {"postscript_marker": "P.P.S"},
     "Body.\np.p.s. later", "Body.\nP.S. not it"),
    ("detectable_format:number_bullet_lists", {"num_bullets": 2},
     "* one\n- two", "* one\n* two\n* three"),
    ("detectable_format:constrained_response", {},
     "Thinking... My answer is maybe.", "Maybe."),
    ("detectable_format:number_highlighted_sections", {"num_highlights": 2},
     "*first* and **second**", "*first* and ** **"),
    ("detectable_format:multiple_sections", {"section_spliter": "Section", "num_sections": 2},
     "Section 1\nA\nSection 2\nB", "Section 1\nA"),
    ("detectable_format:json_format", {},
     "```json\n{\"a\": 1}\n```", "{a: 1}"),
    ("detectable_format:title", {},
     "<<Release notes>>\nBody", "<< >>\nBody"),
    ("combination:two_responses", {},
     "Answer one.\n******\nAnswer two.", "Same.\n******\nSame."),
    ("combination:repeat_prompt", {"prompt_to_repeat": "Explain DNS."},
     "explain dns. DNS maps names to addresses.", "DNS maps names to addresses."),
    ("startend:end_checker", {"end_phrase": "Any other questions?"},
     "Done. Any other questions?\"", "Any other questions? Done."),
    ("startend:quotation", {},
     "  \"Quoted answer.\"  ", "\"Unclosed"),
    ("punctuation:no_comma", {},
     "No commas here.", "Commas, here."),
]


@pytest.mark.parametrize("iid,kwargs,good,bad", CASES, ids=[c[0] for c in CASES])
def test_check_follows_and_violates(iid, kwargs, good, bad):
    assert check(iid, kwargs, good) is True
    assert check(iid, kwargs, bad) is False


def test_every_supported_check_has_a_case():
    assert {c[0] for c in CASES} == set(CHECKS)


def test_empty_paragraph_in_the_middle_fails():
    kw = {"num_paragraphs": 3}
    assert check("length_constraints:number_paragraphs", kw, "a\n***\n\n***\nb") is False


def test_nth_paragraph_beyond_the_response_fails():
    kw = {"num_paragraphs": 3, "nth_paragraph": 3, "first_word": "end"}
    assert check("length_constraints:nth_paragraph_first_word", kw, "a\n\nb") is False


def test_unsupported_instruction_raises():
    with pytest.raises(KeyError):
        check("language:response_language", {"language": "fr"}, "Bonjour")


def test_scorer_needs_every_instruction_followed_and_scores_the_fraction():
    spec = {"type": "ifeval", "instructions": [
        {"id": "punctuation:no_comma", "kwargs": {}},
        {"id": "startend:end_checker", "kwargs": {"end_phrase": "Bye."}},
    ]}
    ok = score_output("Hello. Bye.", spec, {})
    assert ok.passed and ok.score == 1.0
    half = score_output("Hello, there. Bye.", spec, {})
    assert not half.passed and half.score == 0.5
    assert "punctuation:no_comma" in half.detail
