# pdf2md

Convert PDF files (eBooks, papers, reports) to **AI-agent-friendly Markdown** — structured
output suitable for ingestion into a RAG knowledge base such as
[grounded-code-mcp](https://codeberg.org/michaelkalber/grounded-code-mcp).

It preserves the structure that matters for retrieval: headings become `#`/`##`/`###`,
monospace runs become fenced code blocks, tables become Markdown pipe tables, and an
optional YAML front-matter block records provenance.

---

## Features

- **Two engines, auto-selected**
  - `fast` — PyMuPDF + pdfplumber. Lightweight, fast, ideal for digital (text-layer) PDFs.
  - `docling` — IBM Docling ML pipeline. For scanned, multi-column, or formula-heavy PDFs.
  - `auto` (default) — samples the first 3 pages; if the average extractable text per page
    falls below a threshold (a likely scanned PDF), it switches to `docling`, otherwise `fast`.
- **Heading detection** from relative font sizes (median-based thresholds → H1–H3).
- **Code-block detection** from monospace font runs → fenced ``` blocks, with **automatic
  language tagging** (` ```java `, ` ```sql `, ` ```bash `, ` ```json `, ` ```yaml `, ` ```xml `,
  ` ```http `, …) via a heuristic classifier; `--code-lang` sets a fallback for ambiguous blocks.
- **Artifact cleanup for clean RAG text** (fast engine): de-hyphenates words split
  across line breaks (`neces- sary` → `necessary`), strips running headers/footers even
  when they embed a varying page number, collapses letter-spaced text and dropped
  small-caps capitals in headings (`M A N N I N G` → `MANNING`, `C HAPTER` → `CHAPTER`),
  and removes table-of-contents folios/dotted leaders from headings.
- **Table extraction** via pdfplumber → Markdown pipe tables, with shredded-diagram and
  empty-grid tables filtered out (single-column / mostly-empty "tables" are dropped).
- **Image extraction** to sidecar files (`<name>_images/`), referenced inline.
- **YAML front-matter** (on by default; `--no-metadata` to disable): `source`, `pages`,
  `extracted_at`, `tool` — provenance for RAG ingestion.
- **Heading chunking** (`--chunk-by-heading`): one `.md` file per top-level (H1) section —
  convenient for chunked RAG ingestion.
- **Page ranges**, **batch mode** (directory → directory), and password-protected-PDF skipping.

---

## Installation

Dependencies are not vendored. Use [`uv`](https://docs.astral.sh/uv/) (recommended) or `pip`.

```bash
cd tools/pdf2md

# Run directly with uv — resolves deps into an ephemeral environment
uv run pdf2md --help

# Or install into the current environment
pip install -e .                 # fast engine only (PyMuPDF + pdfplumber)
pip install -e '.[docling]'      # adds the Docling ML engine
pip install -e '.[dev]'          # test/dev extras (pytest, reportlab)
```

> **The `docling` extra is heavy** — it pulls in `torch` and CUDA wheels (~130 packages).
> Install it only if you need to convert **scanned** PDFs. For digital eBooks, the default
> `fast` engine is all you need, and `--engine fast` skips the auto-detection sampling.
> Docling also downloads layout models (~500 MB) on first run; subsequent runs use the cache.

---

## Usage

> **Invocation note:** `pdf2md` is a single-command CLI, so you pass the input path
> **directly** — there is no `convert` sub-word:
>
> ```bash
> pdf2md input.pdf output.md      # ✅ correct
> pdf2md convert input.pdf …      # ❌ "convert" is read as the input path
> ```

### Single file

```bash
# Output defaults to the input name with a .md extension
uv run pdf2md book.pdf

# Explicit output path
uv run pdf2md book.pdf book.md

# With provenance front-matter and progress output
uv run pdf2md book.pdf book.md --metadata --verbose
```

### Batch (directory of PDFs)

```bash
# Every *.pdf in ./ebooks/ → ./markdown-out/  (one .md per PDF)
uv run pdf2md ./ebooks/ ./markdown-out/

# Output dir defaults to <input>/output/ when omitted
uv run pdf2md ./ebooks/
```

### Recommended for RAG ingestion

```bash
uv run pdf2md ./ebooks/ ./markdown-out/ \
    --chunk-by-heading \   # one .md per H1 section → better retrieval granularity
    --code-lang java \     # fallback fence tag for a single-language source
    --engine auto          # fast for digital, docling for scanned
```

Provenance front-matter is **on by default** (`--no-metadata` to disable). `--chunk-by-heading`
writes `<name>_<section-slug>.md` files (e.g. `book_chapter-1-introduction.md`), splitting at every
H1. `--code-lang` sets a default language tag for code fences whose language can't be auto-detected
(detected languages always win) — handy when a book is overwhelmingly one language. Feed the
resulting directory to your RAG ingestion pipeline.

---

## CLI reference

| Argument / Option | Default | Description |
|---|---|---|
| `INPUT_PATH` | — | PDF file or directory of PDFs (must exist). |
| `OUTPUT_PATH` | input `.md` (single) / `./output/` (batch) | File path for a single PDF; directory for batch mode. |
| `--engine {auto,fast,docling}` | `auto` | Extraction engine. `auto` samples to choose; `docling` requires the `[docling]` extra. |
| `--page-range` | all | Pages to extract, e.g. `"1-5"` or `"3,7,9-12"`. **Ignored by the `docling` engine.** |
| `--no-images` | off | Skip image extraction. |
| `--no-tables` | off | Skip table detection; rows render as plain text. |
| `--no-code-blocks` | off | Skip monospace detection; render as plain paragraphs. |
| `--image-format {png,jpg}` | `png` | Sidecar image format. |
| `--chunk-by-heading` | off | Write one `.md` file per top-level (H1) heading. |
| `--metadata` / `--no-metadata` | on | Prepend a YAML front-matter provenance block. |
| `--code-lang` | none | Default language tag for code fences when auto-detection is inconclusive (e.g. `java`). Detected languages take precedence. |
| `--verbose` / `--quiet` | quiet | Per-page progress and warnings. |
| `--version` | — | Print version and exit. |

### Output example

```markdown
---
source: book.pdf
pages: 312
extracted_at: 2026-06-25T21:13:16Z
tool: pdf2md/0.1.0
---

# Chapter 1: Introduction

This is a body paragraph extracted from the PDF.

```
def hello():
    return 42
```
```

---

## How it works

```
                       ┌─────────────┐
  PDF ──▶ select_engine │ auto / fast │
                       │  / docling  │
                       └──────┬──────┘
            fast │            │ docling
    ┌────────────▼─────────┐  └────────▶ Docling ML pipeline ──▶ Markdown
    │ extract  (PyMuPDF)   │
    │ headings (font size) │
    │ code     (monospace) │
    │ tables   (pdfplumber)│
    │ images   (PyMuPDF)   │
    │ clean    (de-header, │
    │  de-hyphenate, etc.) │
    └──────────┬───────────┘
               ▼
        markdown_builder ──▶ Markdown
```

Module map (`src/pdf2md/`):

| Module | Responsibility |
|---|---|
| `cli.py` | Typer command surface; flag validation. |
| `converter.py` | Orchestration: page-range parsing, batch loop, chunking, front-matter. |
| `engines/` | `select_engine` auto-detection + `FastEngine` / `DoclingEngine`. |
| `extractor.py` | PyMuPDF span/block extraction. |
| `heading_detector.py` | Median-font-size → heading-level annotation. |
| `code_detector.py` | Monospace-run → code-block annotation + language tagging. |
| `code_language.py` | Heuristic code-language classifier (`detect_language`, `tag_bare_fences`). |
| `table_detector.py` | pdfplumber table extraction + overlap suppression + diagram/empty-table filtering. |
| `image_extractor.py` | Sidecar image export. |
| `cleaner.py` | Header/footer removal, de-hyphenation, letter-spacing & small-caps collapse. |
| `markdown_builder.py` | Assembles annotated blocks into Markdown. |
| `models.py` | Dataclasses (`Span`, `Block`, `Table`, `ConversionConfig`, …). |

---

## Development

```bash
cd tools/pdf2md
uv run --extra dev pytest                 # run the test suite (fast engine only)
uv run --extra dev --extra docling pytest # include Docling-path tests
```

Tests generate their own PDF fixtures at runtime via `reportlab` (see `tests/conftest.py`),
so no binary assets are committed.

---

## Limitations

- The `docling` engine ignores `--page-range` (it always converts the full document).
- Scanned-PDF quality depends on Docling's OCR/layout models.
- **Heading detection is heuristic (font-size based).** A heading level is assigned by a
  block's max font size relative to the document **median** (H1 ≥ median × 1.4,
  H2 ≥ × 1.2, H3 ≥ × 1.05). This works well for body-text-dominated documents (real
  eBooks), where chapter titles clearly exceed the median. Documents with flat typography,
  very little body text, or several competing display fonts (e.g. a large cover/title font)
  may demote chapter headings to H2 — verify a sample before trusting `--chunk-by-heading`.
- **`--chunk-by-heading` splits on H1 (`#`) only.** Because heading level is font-relative
  (above), confirm chapter titles render as `#` first. When a document opens directly on a
  heading, that first section is written to `<name>_preamble.md` (there is no content
  preceding it to separate); every subsequent H1 is named from its heading text.
- Password-protected PDFs are skipped with a warning, not decrypted.
- **Cleanup passes are conservative by design** (fast engine). De-hyphenation rejoins on a
  trailing-`-` + lowercase-continuation heuristic, so a compound that legitimately wrapped at
  its hyphen (`well-` `known`) is merged to one word; small-caps collapse runs on headings
  only (body text keeps forms like `C HAPTER` so that `A JSON` / `I GET` are never corrupted);
  code blocks are never de-hyphenated. Multi-entry table-of-contents lines may still merge into a
  single heading.
- **Code-language tagging is heuristic.** The classifier scores a block against per-language signal
  patterns; short or ambiguous fragments may be mislabeled or fall back to `--code-lang`. It covers
  Java, Python, JavaScript, SQL, Bash, JSON, YAML, XML, and HTTP — other languages need
  `--code-lang` or land untagged.
