# <AI-Generated START>
"""IFEval-subset scorer: verifiable instruction following, checked by code, no judge.

Prompts and instruction ids come from IFEval (Zhou et al., 2023, arXiv:2311.07911; dataset
google/IFEval, Apache-2.0). The checks are re-implemented here from IFEval's published
instruction definitions -- not copied from Google's verifier -- for the 20 instruction types
that need no NLP library. The 5 that need language detection or sentence/word tokenisation
(language:response_language, length_constraints:number_sentences, change_case:*) are not
supported, and prompts using them are not imported. Strict mode only (IFEval also reports a
"loose" mode). Scores are for comparing models with each other here, not with published
IFEval numbers.
"""

from __future__ import annotations

import json
import re
from collections.abc import Callable

from .base import ScoreResult, register


def _compare(count: int, target: int, relation: str) -> bool:
    if relation == "less than":
        return count < target
    if relation == "at least":
        return count >= target
    raise ValueError(f"unknown relation: {relation!r}")


def _paragraphs_ok(text: str, num_paragraphs: int) -> bool:
    parts = re.split(r"\s?\*\*\*\s?", text)
    count = len(parts)
    for i, part in enumerate(parts):
        if not part.strip():
            if i in (0, len(parts) - 1):
                count -= 1  # a divider at the very start or end is not an empty paragraph
            else:
                return False
    return count == num_paragraphs


def _nth_first_word(text: str, num_paragraphs: int, nth_paragraph: int, first_word: str) -> bool:
    parts = re.split(r"\n\n", text)
    count = sum(1 for p in parts if p.strip())
    if nth_paragraph > len(parts) or count != num_paragraphs:
        return False
    paragraph = parts[nth_paragraph - 1].strip()
    if not paragraph:
        return False
    word = paragraph.split()[0].lstrip("'\"")
    got = ""
    for ch in word:
        if ch in ".,?!'\"":
            break
        got += ch.lower()
    return got == first_word.lower()


def _postscript(text: str, postscript_marker: str) -> bool:
    if postscript_marker == "P.P.S":
        pattern = r"\s*p\.\s?p\.\s?s.*$"
    elif postscript_marker == "P.S.":
        pattern = r"\s*p\.\s?s\..*$"
    else:
        pattern = r"\s*" + re.escape(postscript_marker.lower()) + r".*$"
    return bool(re.findall(pattern, text.lower(), flags=re.MULTILINE))


def _highlights(text: str, num_highlights: int) -> bool:
    found = re.findall(r"\*[^\n\*]*\*", text) + re.findall(r"\*\*[^\n\*]*\*\*", text)
    return sum(1 for h in found if h.strip("*").strip()) >= num_highlights


def _json(text: str) -> bool:
    body = text.strip()
    for prefix in ("```json", "```Json", "```JSON", "```"):
        if body.startswith(prefix):
            body = body[len(prefix):]
            break
    body = body.removesuffix("```").strip()
    try:
        json.loads(body)
    except ValueError:
        return False
    return True


def _two_responses(text: str) -> bool:
    parts = text.split("******")
    kept = []
    for i, part in enumerate(parts):
        if not part.strip():
            if i not in (0, len(parts) - 1):
                return False
        else:
            kept.append(part)
    return len(kept) == 2 and kept[0].strip() != kept[1].strip()


CHECKS: dict[str, Callable[..., bool]] = {
    "keywords:existence": lambda t, keywords: all(
        re.search(re.escape(k), t, flags=re.IGNORECASE) for k in keywords),
    "keywords:frequency": lambda t, keyword, frequency, relation: _compare(
        len(re.findall(re.escape(keyword), t, flags=re.IGNORECASE)), frequency, relation),
    "keywords:forbidden_words": lambda t, forbidden_words: not any(
        re.search(r"\b" + re.escape(w) + r"\b", t, flags=re.IGNORECASE) for w in forbidden_words),
    "keywords:letter_frequency": lambda t, letter, let_frequency, let_relation: _compare(
        t.lower().count(letter.lower()), let_frequency, let_relation),
    "length_constraints:number_paragraphs": lambda t, num_paragraphs: _paragraphs_ok(
        t, num_paragraphs),
    "length_constraints:number_words": lambda t, num_words, relation: _compare(
        len(re.findall(r"\w+", t)), num_words, relation),
    "length_constraints:nth_paragraph_first_word": _nth_first_word,
    "detectable_content:number_placeholders": lambda t, num_placeholders: len(
        re.findall(r"\[.*?\]", t)) >= num_placeholders,
    "detectable_content:postscript": _postscript,
    "detectable_format:number_bullet_lists": lambda t, num_bullets: len(
        re.findall(r"^\s*\*[^\*].*$", t, flags=re.MULTILINE)
        + re.findall(r"^\s*-.*$", t, flags=re.MULTILINE)) == num_bullets,
    "detectable_format:constrained_response": lambda t: any(
        o in t.strip() for o in ("My answer is yes.", "My answer is no.", "My answer is maybe.")),
    "detectable_format:number_highlighted_sections": _highlights,
    "detectable_format:multiple_sections": lambda t, section_spliter, num_sections: len(
        re.split(r"\s?" + re.escape(section_spliter) + r"\s?\d+\s?", t)) - 1 >= num_sections,
    "detectable_format:json_format": _json,
    "detectable_format:title": lambda t: any(
        m.lstrip("<").rstrip(">").strip() for m in re.findall(r"<<[^\n]+>>", t)),
    "combination:two_responses": _two_responses,
    "combination:repeat_prompt": lambda t, prompt_to_repeat: t.strip().lower().startswith(
        prompt_to_repeat.strip().lower()),
    "startend:end_checker": lambda t, end_phrase: t.strip().strip('"').lower().endswith(
        end_phrase.strip().lower()),
    "startend:quotation": lambda t: len(t.strip()) > 1 and t.strip()[0] == t.strip()[-1] == '"',
    "punctuation:no_comma": lambda t: "," not in t,
}


def check(instruction_id: str, kwargs: dict, response: str) -> bool:
    """True if `response` follows the instruction. KeyError for an unsupported instruction."""
    return bool(CHECKS[instruction_id](response, **kwargs))


@register("ifeval")
def ifeval(output: str, spec: dict, context: dict) -> ScoreResult:
    instructions = spec["instructions"]
    missed = [i["id"] for i in instructions if not check(i["id"], i.get("kwargs") or {}, output)]
    score = 1 - len(missed) / len(instructions)
    return ScoreResult(score, not missed, f"not followed: {missed}" if missed else "")
# <AI-Generated END>
