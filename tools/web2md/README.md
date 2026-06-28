# web2md

[![Tests](https://img.shields.io/badge/tests-49-green)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-92%25-green)](tests/)

Convert web pages and documentation sites to **AI-agent-friendly Markdown** — structured output
suitable for ingestion into a RAG knowledge base such as
[grounded-code-mcp](https://codeberg.org/michaelkalber/grounded-code-mcp).

Uses [IBM Docling](https://github.com/DS4SD/docling) as its conversion engine, which preserves
semantic structure: headings, code blocks, tables, and lists render faithfully even from
JavaScript-heavy or CSS-heavy documentation pages.

---

## Features

- **Single-page** — convert one URL to a `.md` file
- **Crawl mode** (`--crawl`) — BFS-crawl all internally-linked pages from a root URL, same domain
- **Sitemap mode** (`--sitemap`) — parse a `sitemap.xml` (including sitemap index files) and
  convert every listed page; follows nested sitemap indexes up to 3 levels deep
- **`--same-prefix`** — restrict crawl to URLs under the start URL (e.g. `/docs/` subtree only)
- **`--max-depth`** — cap how many link-hops the crawl follows from the start URL
- **`--max-pages`** — cap the number of pages converted in batch modes
- **YAML front-matter** (`--metadata`): `source`, `extracted_at`, `tool`
- **Heading chunking** (`--chunk-by-heading`): one `.md` file per top-level (H1) section —
  optimal chunk granularity for RAG ingestion
- **`--no-images`** / **`--no-tables`** — strip image references or tables from output

---

## Installation

Requires Python ≥ 3.10. Use [`uv`](https://docs.astral.sh/uv/) (recommended) or `pip`.

```bash
cd tools/web2md

# Run directly with uv — resolves deps into an ephemeral environment
uv run web2md --help

# Or install into the current environment
pip install -e .

# Dev extras (pytest, respx for HTTP mocking)
pip install -e '.[dev]'
```

> **Docling is heavy on first run** — it downloads layout models (~500 MB) and may pull in
> `torch`. Subsequent runs use the cached models. Set `DOCLING_HOME` to control the cache path.

---

## Usage

### Single page

```bash
# Output defaults to <url-slug>.md in the current directory
uv run web2md https://docs.example.com/guide/intro

# Explicit output path
uv run web2md https://docs.example.com/guide/intro guide-intro.md

# With provenance front-matter
uv run web2md https://docs.example.com/guide/intro guide-intro.md --metadata --verbose
```

### Crawl mode

BFS-crawl all internally-linked pages starting from the given URL. Stays on the same domain by
default; use `--same-prefix` to restrict to the URL subtree.

```bash
# Crawl up to 100 pages under the docs site
uv run web2md https://docs.example.com/ ./output/ --crawl --max-pages 100

# Only follow links under /guide/ (not the rest of the domain)
uv run web2md https://docs.example.com/guide/ ./output/ --crawl --same-prefix --max-pages 50

# Convert only the root page and the pages it links to directly (one hop)
uv run web2md https://docs.example.com/ ./output/ --crawl --max-depth 1
```

### Sitemap mode

Parse a `sitemap.xml` and convert every listed page.

```bash
uv run web2md https://docs.example.com/sitemap.xml ./output/ --sitemap

# Cap at 200 pages
uv run web2md https://docs.example.com/sitemap.xml ./output/ --sitemap --max-pages 200
```

### Recommended for RAG ingestion

```bash
uv run web2md https://docs.example.com/sitemap.xml ./markdown-out/ \
    --sitemap \
    --metadata \
    --chunk-by-heading \
    --max-pages 500
```

`--chunk-by-heading` writes `<slug>_<section>.md` files split at every H1 — feeds well into
chunk-based retrieval. Feed the resulting directory to your RAG ingestion pipeline.

---

## CLI reference

| Argument / Option | Default | Description |
|---|---|---|
| `URL` | — | URL to convert; crawl root with `--crawl`; sitemap URL with `--sitemap`. |
| `OUTPUT` | `<url-slug>.md` (single) / `./output/` (batch) | Output file or directory. |
| `--crawl` | off | BFS-crawl all internal pages from URL. |
| `--sitemap` | off | Treat URL as a `sitemap.xml` and convert all listed pages. |
| `--max-pages INT` | `50` | Cap on pages to convert in crawl / sitemap mode. |
| `--same-prefix` | off | Crawl only: restrict to URLs starting with the given URL. |
| `--max-depth INT` | unlimited | Crawl only: max link-hops from the start URL (root = 0, direct links = 1, ...). |
| `--no-images` | off | Strip image references from output. |
| `--no-tables` | off | Strip table markup from output. |
| `--chunk-by-heading` | off | Write one `.md` file per top-level (H1) heading. |
| `--metadata` | off | Prepend a YAML front-matter block. |
| `--verbose` / `--quiet` | quiet | Show per-page progress. |
| `--version` | — | Print version and exit. |

`--crawl` and `--sitemap` are mutually exclusive.

### Output example (single page, `--metadata`)

```markdown
---
source: https://docs.example.com/guide/intro
extracted_at: 2026-06-28T14:32:00Z
tool: web2md/0.1.0
---

# Introduction

This is the introduction section.

## Prerequisites

- Python 3.10+
- A running database

```python
pip install mylib
```
```

---

## How it works

```
URL ──▶ mode?
         │ single ──▶ DocumentConverter(url) ──▶ export_to_markdown() ──▶ .md
         │ --crawl ──▶ BFS crawler (httpx + bs4) ──▶ URL list
         │ --sitemap ──▶ sitemap.xml parser (xml.etree) ──▶ URL list
         └──────────────────────────────────────────────────────────────────
                        URL list ──▶ DocumentConverter(url) × N ──▶ output/
```

Module map (`src/web2md/`):

| Module | Responsibility |
|---|---|
| `cli.py` | Typer command surface; mode routing; batch loop. |
| `converter.py` | Docling wrapper; front-matter; chunk-by-heading splitting. |
| `crawler.py` | BFS crawler using `httpx` + `beautifulsoup4`. |
| `sitemap.py` | `sitemap.xml` / sitemap-index parser using `xml.etree`. |
| `models.py` | `ConversionConfig` dataclass; `url_to_slug` helper. |

---

## Development

```bash
cd tools/web2md
uv run --extra dev pytest                   # run the full test suite (HTTP calls mocked)
uv run --extra dev pytest --cov --cov-report=html  # coverage report
```

Tests use `respx` to mock all `httpx` calls and `unittest.mock.patch` for Docling — no network
access required.

---

## Limitations

- **JavaScript-rendered content:** Docling fetches and processes the raw HTML response. Pages that
  require JavaScript execution to render their content (single-page apps, lazy-loaded docs) may
  produce sparse output. For those sites, prefer `--sitemap` over `--crawl` and verify a sample
  page before bulk conversion.
- **Rate limiting:** Crawl and sitemap modes issue one sequential HTTP request per page with no
  delay between requests. For large sites, add `--max-pages` to stay polite, or run during
  off-peak hours.
- **Login-gated content:** Docling uses an unauthenticated HTTP client. Pages behind a login wall
  will return login-page HTML, not the actual content.
- **`--chunk-by-heading` splits on H1 only.** Verify that the page's top-level sections render
  as `# Heading` before relying on this flag for retrieval.
