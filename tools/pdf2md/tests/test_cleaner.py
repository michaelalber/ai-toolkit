"""Tests for cleaner module."""
from __future__ import annotations

from pdf2md.cleaner import (
    _collapse_letterspacing,
    _collapse_small_caps,
    _dehyphenate_spans,
    _dehyphenate_text,
    _normalize_header_key,
    clean_pages,
)
from pdf2md.models import Block, ExtractedPage, Span


def _span(text: str, mono: bool = False) -> Span:
    return Span(
        text=text,
        font_name="Courier" if mono else "Helvetica",
        font_size=12.0,
        is_bold=False,
        is_italic=False,
        is_monospace=mono,
    )


def _text_block(text: str, page: int = 1) -> Block:
    return Block(spans=[_span(text)], block_type="text", bbox=(0, 0, 100, 20), page_number=page)


def _multi_span_block(*texts: str, mono: bool = False, page: int = 1) -> Block:
    return Block(
        spans=[_span(t, mono=mono) for t in texts],
        block_type="text",
        bbox=(0, 0, 100, 20),
        page_number=page,
    )


class TestCleanPages:
    def test_removes_lone_page_numbers(self) -> None:
        block = _text_block("42")
        page = ExtractedPage(page_number=1, blocks=[block])
        cleaned = clean_pages([page])
        assert all(b.spans[0].text != "42" for b in cleaned[0].blocks if b.spans)

    def test_removes_page_of_pattern(self) -> None:
        block = _text_block("Page 3 of 10")
        page = ExtractedPage(page_number=1, blocks=[block])
        cleaned = clean_pages([page])
        assert len(cleaned[0].blocks) == 0

    def test_removes_running_header_appearing_on_3_plus_pages(self) -> None:
        pages = [
            ExtractedPage(
                page_number=i,
                blocks=[_text_block("Running Header", page=i), _text_block(f"Content {i}", page=i)],
            )
            for i in range(1, 6)
        ]
        cleaned = clean_pages(pages)
        for page in cleaned:
            texts = [" ".join(s.text for s in b.spans) for b in page.blocks]
            assert "Running Header" not in texts

    def test_preserves_unique_content(self) -> None:
        block = _text_block("Unique paragraph that appears once.")
        page = ExtractedPage(page_number=1, blocks=[block])
        cleaned = clean_pages([page])
        assert len(cleaned[0].blocks) == 1

    def test_unicode_normalization_resolves_ligatures(self) -> None:
        # 'ﬁ' is the fi ligature (U+FB01); NFKC should normalize it to 'fi'
        block = _text_block("\ufb01le")
        page = ExtractedPage(page_number=1, blocks=[block])
        cleaned = clean_pages([page])
        assert cleaned[0].blocks[0].spans[0].text == "file"

    def test_removes_running_header_with_varying_page_number(self) -> None:
        # Real running headers embed the page number, so the raw strings differ
        # per page. After digit-normalization they must still be detected.
        pages = [
            ExtractedPage(
                page_number=i,
                blocks=[
                    _text_block(f"{i} Wiring up the REST endpoints", page=i),
                    _text_block(f"Body paragraph number {i} continues here at length", page=i),
                ],
            )
            for i in range(30, 36)
        ]
        cleaned = clean_pages(pages)
        for page in cleaned:
            texts = [" ".join(s.text for s in b.spans) for b in page.blocks]
            assert not any("Wiring up the REST endpoints" in t for t in texts)

    def test_dehyphenates_line_broken_words_end_to_end(self) -> None:
        block = _multi_span_block("strictly neces-", "sary, but useful")
        page = ExtractedPage(page_number=1, blocks=[block])
        cleaned = clean_pages([page])
        joined = " ".join(s.text for s in cleaned[0].blocks[0].spans)
        assert "necessary" in joined
        assert "neces- sary" not in joined

    def test_collapses_letterspaced_heading_end_to_end(self) -> None:
        block = Block(
            spans=[_span("M A N N I N G")],
            block_type="text",
            bbox=(0, 0, 100, 20),
            page_number=1,
            heading_level=1,
        )
        page = ExtractedPage(page_number=1, blocks=[block])
        cleaned = clean_pages([page])
        assert cleaned[0].blocks[0].spans[0].text == "MANNING"


class TestDehyphenateSpans:
    def test_merges_lowercase_continuation(self) -> None:
        spans = [_span("neces-"), _span("sary")]
        result = _dehyphenate_spans(spans)
        assert len(result) == 1
        assert result[0].text == "necessary"

    def test_chains_multiple_breaks(self) -> None:
        spans = [_span("devel-"), _span("op-"), _span("ers")]
        result = _dehyphenate_spans(spans)
        assert result[0].text == "developers"

    def test_does_not_merge_uppercase_continuation_in_prose(self) -> None:
        # "the-" followed by "United" must not collapse (not a wrapped word)
        spans = [_span("the-"), _span("United")]
        result = _dehyphenate_spans(spans)
        assert len(result) == 2

    def test_merges_monospace_camelcase_identifier(self) -> None:
        spans = [_span("audit-", mono=True), _span("RequestEnd", mono=True)]
        result = _dehyphenate_spans(spans)
        assert result[0].text == "auditRequestEnd"

    def test_leaves_non_hyphenated_spans_untouched(self) -> None:
        spans = [_span("hello"), _span("world")]
        result = _dehyphenate_spans(spans)
        assert [s.text for s in result] == ["hello", "world"]


class TestDehyphenateText:
    def test_rejoins_word_wrapped_inside_one_span(self) -> None:
        assert _dehyphenate_text("authoriza- tion") == "authorization"

    def test_preserves_midline_compound_hyphen(self) -> None:
        # No following space → a real compound, must stay hyphenated.
        assert _dehyphenate_text("object-relational mapping") == "object-relational mapping"

    def test_does_not_join_when_continuation_is_uppercase(self) -> None:
        assert _dehyphenate_text("the- United States") == "the- United States"


class TestCollapseLetterspacing:
    def test_collapses_run_of_three_or_more_single_chars(self) -> None:
        assert _collapse_letterspacing("M A N N I N G") == "MANNING"

    def test_leaves_two_token_run_untouched(self) -> None:
        # Avoid corrupting "a b" style legitimate text; need 3+
        assert _collapse_letterspacing("I a") == "I a"

    def test_preserves_normal_words(self) -> None:
        assert _collapse_letterspacing("the quick brown fox") == "the quick brown fox"

    def test_collapses_run_inside_sentence(self) -> None:
        assert _collapse_letterspacing("see F O O bar") == "see FOO bar"


class TestCollapseSmallCaps:
    def test_merges_dropped_capital(self) -> None:
        assert _collapse_small_caps("C HAPTER 2") == "CHAPTER 2"

    def test_does_not_merge_article_a_before_acronym(self) -> None:
        # "A JSON web token" must stay intact
        assert _collapse_small_caps("A JSON web token") == "A JSON web token"

    def test_does_not_merge_pronoun_i(self) -> None:
        assert _collapse_small_caps("I GET the data") == "I GET the data"


class TestNormalizeHeaderKey:
    def test_strips_leading_page_number(self) -> None:
        assert _normalize_header_key("38 Wiring up the endpoints") == _normalize_header_key(
            "41 Wiring up the endpoints"
        )

    def test_strips_trailing_page_number(self) -> None:
        assert _normalize_header_key("Chapter title 12") == _normalize_header_key(
            "Chapter title 19"
        )
