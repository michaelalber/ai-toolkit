from __future__ import annotations

import re
import unicodedata
from collections import Counter
from dataclasses import replace

from pdf2md.models import Block, ExtractedPage, Span

# Patterns for artifacts that should be removed
_PAGE_NUMBER_RE = re.compile(r"^\s*\d+\s*$")
_PAGE_OF_RE = re.compile(r"^\s*[Pp]age\s+\d+\s+of\s+\d+\s*$")
_MIN_PAGES_FOR_HEADER_DETECTION = 3
# Running headers/footers are short lines; never treat a long paragraph as one.
_MAX_HEADER_WORDS = 12

# A word wrapped across a line break ends in "<letter>-"; the continuation
# starts with a lowercase letter (prose) — for monospace identifiers the
# continuation may be upper-case (camelCase), handled separately.
_HYPHEN_BREAK_RE = re.compile(r"[A-Za-z]-$")
# Same wrap, but both fragments landed inside one span as "<letter>- <lower>".
# Mid-line compound hyphens ("object-relational") have no following space, so
# they are unaffected.
_INTRA_HYPHEN_RE = re.compile(r"([A-Za-z])- ([a-z])")

# Small-caps text loses the first capital to its own span: "C HAPTER" → "CHAPTER".
# Exclude the only single-letter English words (A, I) so "A JSON" / "I GET" survive.
_SMALL_CAPS_RE = re.compile(r"\b([B-HJ-Z]) ([A-Z]{2,})\b")


def _block_text(block: Block) -> str:
    return " ".join(span.text for span in block.spans).strip()


def _normalize_header_key(text: str) -> str:
    """Collapse a header/footer line to a page-number-independent key.

    Running headers embed the folio (page number) at the start or end of the
    line, so the raw strings differ on every page.  Stripping a leading and/or
    trailing number group lets the same header be detected across pages.
    """
    t = re.sub(r"^\s*\d+\s+", "", text)
    t = re.sub(r"\s+\d+\s*$", "", t)
    t = re.sub(r"\s+", " ", t).strip().lower()
    return t


def _detect_running_headers_footers(pages: list[ExtractedPage]) -> set[str]:
    """Return normalized keys that appear as a short first/last block on 3+ pages."""
    if len(pages) < _MIN_PAGES_FOR_HEADER_DETECTION:
        return set()

    first_keys: list[str] = []
    last_keys: list[str] = []

    for page in pages:
        text_blocks = [b for b in page.blocks if b.block_type == "text" and b.spans]
        if not text_blocks:
            continue
        for candidate, bucket in (
            (text_blocks[0], first_keys),
            (text_blocks[-1], last_keys),
        ):
            text = _block_text(candidate)
            if text and len(text.split()) <= _MAX_HEADER_WORDS:
                bucket.append(_normalize_header_key(text))

    recurring: set[str] = set()
    for key, count in (Counter(first_keys) + Counter(last_keys)).items():
        if key and count >= _MIN_PAGES_FOR_HEADER_DETECTION:
            recurring.add(key)
    return recurring


def _normalize_text(text: str) -> str:
    """Apply Unicode NFKC normalization to resolve ligatures, smart quotes, etc."""
    return unicodedata.normalize("NFKC", text)


def _dehyphenate_spans(spans: list[Span]) -> list[Span]:
    """Rejoin words split across a line break (``neces-`` + ``sary`` → ``necessary``).

    A merge fires when a span ends with ``<letter>-`` and the next span begins
    with a lower-case letter (prose) or, for two monospace spans, any letter
    (camelCase identifiers).  Merges chain so ``devel-`` ``op-`` ``ers`` collapse
    to ``developers``.  The hyphen is dropped and no space is inserted.
    """
    if not spans:
        return spans

    result: list[Span] = [spans[0]]
    for nxt in spans[1:]:
        cur = result[-1]
        cur_text = cur.text.rstrip()
        nxt_lead = nxt.text.lstrip()[:1]
        is_break = bool(_HYPHEN_BREAK_RE.search(cur_text)) and bool(nxt_lead)
        prose_join = nxt_lead.islower()
        mono_join = cur.is_monospace and nxt.is_monospace and nxt_lead.isalpha()
        if is_break and (prose_join or mono_join):
            result[-1] = replace(cur, text=cur_text[:-1] + nxt.text.lstrip())
        else:
            result.append(nxt)
    return result


def _collapse_letterspacing(text: str) -> str:
    """Rejoin letter-spaced words: ``M A N N I N G`` → ``MANNING``.

    Only runs of **three or more** single-character tokens collapse, so ordinary
    two-word fragments (``I a``) are never corrupted.
    """
    tokens = text.split(" ")
    out: list[str] = []
    i = 0
    while i < len(tokens):
        if len(tokens[i]) == 1 and tokens[i].isalnum():
            j = i
            while j < len(tokens) and len(tokens[j]) == 1 and tokens[j].isalnum():
                j += 1
            run = tokens[i:j]
            out.append("".join(run) if len(run) >= 3 else " ".join(run))
            i = j
        else:
            out.append(tokens[i])
            i += 1
    return " ".join(out)


def _collapse_small_caps(text: str) -> str:
    """Rejoin a dropped small-caps capital: ``C HAPTER`` → ``CHAPTER``.

    Applied to headings only.  The single-letter English words ``A`` and ``I``
    are excluded so ``A JSON`` and ``I GET`` are preserved.
    """
    return _SMALL_CAPS_RE.sub(lambda m: m.group(1) + m.group(2), text)


def _collapse_letterspaced_spans(spans: list[Span]) -> list[Span]:
    """Merge runs of 3+ single-character spans (cross-span letter-spacing).

    PDFs sometimes emit each tracked glyph as its own span, so ``M A N N I N G``
    arrives as seven single-char spans joined by the renderer.  A run of three
    or more is collapsed into one span with the spacing removed.
    """
    result: list[Span] = []
    i = 0
    while i < len(spans):
        token = spans[i].text.strip()
        if len(token) == 1 and token.isalnum():
            j = i
            while j < len(spans):
                t = spans[j].text.strip()
                if len(t) == 1 and t.isalnum():
                    j += 1
                else:
                    break
            run = spans[i:j]
            if len(run) >= 3:
                result.append(replace(run[0], text="".join(s.text.strip() for s in run)))
            else:
                result.extend(run)
            i = j
        else:
            result.append(spans[i])
            i += 1
    return result


def _dehyphenate_text(text: str) -> str:
    """Rejoin a word wrapped within a single span: ``authoriza- tion`` → ``authorization``."""
    return _INTRA_HYPHEN_RE.sub(r"\1\2", text)


def _collapse_spaces(text: str) -> str:
    return re.sub(r"[ \t]{2,}", " ", text)


def _clean_heading_text(text: str) -> str:
    """Clean a heading's fully-joined text (letter-spacing + small caps)."""
    text = _normalize_text(text)
    text = _collapse_spaces(text)
    text = _dehyphenate_text(text)
    text = _collapse_letterspacing(text)
    text = _collapse_small_caps(text)
    return text.strip()


def _clean_span(span: Span, *, is_code: bool) -> Span:
    """Normalize and de-noise a single body span's text."""
    text = _normalize_text(span.text)
    if not is_code:
        text = _collapse_spaces(text)
        text = _dehyphenate_text(text)
        text = _collapse_letterspacing(text)
    return replace(span, text=text)


def clean_pages(pages: list[ExtractedPage]) -> list[ExtractedPage]:
    """Remove artifacts and normalize text across all pages.

    Mutations performed:
    - Strip running headers and footers (page-number-normalized match on 3+ pages).
    - Remove lone page-number lines.
    - Apply Unicode NFKC normalization to all span text.
    - Rejoin words hyphenated across line breaks.
    - Collapse letter-spaced words and dropped small-caps capitals (headings).
    - Drop blocks that become empty after cleaning.
    """
    recurring = _detect_running_headers_footers(pages)

    cleaned: list[ExtractedPage] = []
    for page in pages:
        clean_blocks: list[Block] = []
        for block in page.blocks:
            if block.block_type != "text":
                clean_blocks.append(block)
                continue

            text = _block_text(block)

            # Remove page numbers and running headers/footers
            if _PAGE_NUMBER_RE.match(text) or _PAGE_OF_RE.match(text):
                continue
            if _normalize_header_key(text) in recurring:
                continue

            is_heading = block.heading_level is not None
            is_code = block.is_code_block

            if is_heading and not is_code:
                # Headings are rendered as a single joined line, so clean the
                # joined text once — this also collapses cross-span letter-spacing
                # ("M A N N I N G") and dropped small-caps capitals ("C HAPTER").
                heading_text = _clean_heading_text(_block_text(block))
                if not heading_text:
                    continue
                normalized_spans = [replace(block.spans[0], text=heading_text)]
            else:
                spans = block.spans
                if not is_code:
                    spans = _dehyphenate_spans(spans)
                    spans = _collapse_letterspaced_spans(spans)
                normalized_spans = [_clean_span(s, is_code=is_code) for s in spans]
                # Drop spans that became empty after cleaning
                normalized_spans = [s for s in normalized_spans if s.text.strip()]
            if not normalized_spans:
                continue

            clean_block = Block(
                spans=normalized_spans,
                block_type=block.block_type,
                bbox=block.bbox,
                page_number=block.page_number,
                heading_level=block.heading_level,
                is_code_block=block.is_code_block,
                language=block.language,
            )
            clean_blocks.append(clean_block)

        cleaned.append(
            ExtractedPage(
                page_number=page.page_number,
                blocks=clean_blocks,
                tables=page.tables,
                image_paths=page.image_paths,
                raw_font_sizes=page.raw_font_sizes,
            )
        )

    return cleaned
