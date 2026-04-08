from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path

from pdf2md.models import Block, ExtractedPage, Span, Table

_HEADING_PREFIX = {1: "# ", 2: "## ", 3: "### "}


def _table_to_markdown(table: Table) -> str:
    """Render a :class:`~pdf2md.models.Table` as a Markdown pipe table."""
    if not table.cells:
        return ""

    rows = table.cells
    # Sanitize: replace None with empty string, strip newlines inside cells
    clean_rows: list[list[str]] = [
        [re.sub(r"\s+", " ", (cell or "").replace("\n", " ")).strip() for cell in row]
        for row in rows
    ]

    # Determine column count from widest row
    col_count = max(len(row) for row in clean_rows) if clean_rows else 0
    if col_count == 0:
        return ""

    # Pad rows to uniform width
    padded = [row + [""] * (col_count - len(row)) for row in clean_rows]

    lines: list[str] = []
    header = padded[0]
    lines.append("| " + " | ".join(header) + " |")
    lines.append("| " + " | ".join(["---"] * col_count) + " |")
    for row in padded[1:]:
        lines.append("| " + " | ".join(row) + " |")

    return "\n".join(lines)


def _render_span_inline(span: Span) -> str:
    text = span.text
    if span.is_monospace:
        text = f"`{text}`"
    elif span.is_bold and span.is_italic:
        text = f"***{text}***"
    elif span.is_bold:
        text = f"**{text}**"
    elif span.is_italic:
        text = f"*{text}*"
    return text


def _render_block(block: Block) -> str:
    if not block.spans:
        return ""

    text = " ".join(span.text for span in block.spans).strip()
    if not text:
        return ""

    # Code block: wrap in fenced block
    if block.is_code_block:
        code = "\n".join(span.text for span in block.spans)
        return f"```\n{code}\n```"

    # Heading
    if block.heading_level is not None:
        prefix = _HEADING_PREFIX.get(block.heading_level, "### ")
        return f"{prefix}{text}"

    # Mixed inline: render spans individually
    all_same_style = len({(s.is_bold, s.is_italic, s.is_monospace) for s in block.spans}) == 1
    if all_same_style and block.spans:
        # Apply uniform decoration to the whole paragraph
        s = block.spans[0]
        if s.is_bold and s.is_italic:
            return f"***{text}***"
        if s.is_bold:
            return f"**{text}**"
        if s.is_italic:
            return f"*{text}*"
        return text

    # Per-span rendering for mixed styles
    return " ".join(_render_span_inline(s) for s in block.spans).strip()


def _build_front_matter(source_path: Path, total_pages: int) -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return (
        "---\n"
        f"source: {source_path.name}\n"
        f"pages: {total_pages}\n"
        f"extracted_at: {timestamp}\n"
        f"tool: pdf2md/0.1.0\n"
        "---\n\n"
    )


def build_markdown(
    pages: list[ExtractedPage],
    source_path: Path,
    total_pages: int,
    include_metadata: bool = False,
) -> str:
    """Assemble extracted page data into a single Markdown string."""
    parts: list[str] = []

    if include_metadata:
        parts.append(_build_front_matter(source_path, total_pages))

    # Build a lookup: (page_number, table_index) → Table for ordered insertion
    # Tables are inserted after all text blocks on their page by default,
    # unless a suppressed text block marks the insertion point.
    for page in pages:
        rendered_tables: dict[int, str] = {
            i: _table_to_markdown(t) for i, t in enumerate(page.tables)
        }
        table_inserted = [False] * len(page.tables)

        for block in page.blocks:
            if block.block_type == "image":
                for img_path in page.image_paths:
                    rel = img_path.name
                    parts.append(f"![image]({img_path})\n")
                continue

            if block.block_type == "table":
                # Insert the table that occupies this block's position
                for i, table in enumerate(page.tables):
                    if not table_inserted[i]:
                        md = rendered_tables[i]
                        if md:
                            parts.append(md + "\n")
                        table_inserted[i] = True
                        break
                continue

            rendered = _render_block(block)
            if rendered:
                parts.append(rendered + "\n")

        # Append any tables not yet inserted (e.g. on pages with no overlapping text blocks)
        for i, md in rendered_tables.items():
            if not table_inserted[i] and md:
                parts.append(md + "\n")

    return "\n".join(parts)
