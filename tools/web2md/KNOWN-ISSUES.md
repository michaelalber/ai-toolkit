# web2md — Known Issues

## BUG-001 · Crawler mishandles document-relative links, and one bad `href` aborts the whole crawl

**Status:** ✅ RESOLVED 2026-07-13 — both defects fixed in `crawler.py` (`urljoin(url, href)`
against the current page, wrapped in `try/except ValueError`; the `base` line removed). Regression
tests `test_document_relative_link_resolves_against_current_page` and
`test_malformed_href_does_not_abort_crawl` added to `tests/test_crawler.py` (RED→GREEN).
**Filed:** 2026-07-05
**Severity:** High — silently loses most pages on many doc sites; hard-crashes on some.
**Affected:** `web2md 0.1.0`, `src/web2md/crawler.py:89` (both defects on the same line).
**Discovered during:** bulk ingest of library docs into `grounded-code-mcp`.

Two distinct defects both originate at the link-resolution line in `crawl()`:

```python
# crawler.py — inside crawl()
parsed = urlparse(start_url)
...
base = f"{parsed.scheme}://{parsed.netloc}"     # ← only scheme+netloc; PATH is dropped
for tag in soup.find_all("a", href=True):
    href: str = tag["href"].split("#")[0]
    if not href or href.startswith("mailto:") or href.startswith("javascript:"):
        continue
    absolute = urljoin(base, href)              # ← line 89: both bugs live here
    if is_allowed(absolute) and absolute not in visited:
        queue.append((absolute, depth + 1))
```

### Defect A — document-relative links resolve against the domain root

`base` is reconstructed from the **start URL** as `scheme://netloc`, discarding the path.
`urljoin()` is then given that path-less base, so a *document-relative* href resolves against
the site root instead of the current page's directory:

| Current page | `href` in HTML | Resolved (wrong) | Should be |
|---|---|---|---|
| `https://alembic.sqlalchemy.org/en/latest/` | `api/commands.html` | `https://alembic.sqlalchemy.org/api/commands.html` (404) | `…/en/latest/api/commands.html` |
| `https://docs.fluentvalidation.net/en/latest/` | `start.html` | `…/start.html` (404) | `…/en/latest/start.html` |

Because every discovered link 404s, the crawl visits **only the start page**. Observed on
FluentValidation, Alembic, and SQLAlchemy (`--crawl` returned exactly 1 page each). Sites that
emit root-relative (`/en/...`) or absolute (`https://...`) hrefs are unaffected — which is why
react.dev, PostgreSQL, Polly, xUnit, TanStack, etc. crawled correctly.

**Root cause:** `urljoin` must be called with the **current page's** URL as the base, not a
reconstructed origin. `urljoin` already handles relative, root-relative, and absolute hrefs
correctly when given the real page URL.

**Fix (one line):**

```python
absolute = urljoin(url, href)   # `url` = the page currently being parsed, not `base`
```

The `base = f"{parsed.scheme}://{parsed.netloc}"` line can then be deleted.

### Defect B — a single malformed `href` crashes the entire crawl

On `https://www.php.net/manual/en/funcref.php`, at least one anchor contains an unbalanced
`[` in its `href`. `urljoin` → `urllib.parse._urlsplit` raises:

```
ValueError: Invalid IPv6 URL
  at crawler.py:89  absolute = urljoin(base, href)
```

The link loop has no exception handling, so this propagates out of `crawl()` and aborts the
whole run. The CLI produced **zero** output — not even the start page (which had already been
appended to `result` but was discarded when the function raised). php.net uses absolute links,
so Defect A is *not* the cause here; this is an independent robustness gap.

**Fix:** guard per-link resolution so one bad href is skipped, not fatal:

```python
for tag in soup.find_all("a", href=True):
    href = tag["href"].split("#")[0]
    if not href or href.startswith(("mailto:", "javascript:")):
        continue
    try:
        absolute = urljoin(url, href)
    except ValueError:
        continue   # skip malformed hrefs (e.g. unbalanced brackets) instead of aborting
    if is_allowed(absolute) and absolute not in visited:
        queue.append((absolute, depth + 1))
```

### Reproduction

```bash
# Defect A — yields only 1 page instead of the whole subtree
uv run web2md https://alembic.sqlalchemy.org/en/latest/ ./out/ --crawl --max-pages 30

# Defect B — crashes with ValueError: Invalid IPv6 URL, 0 pages written
uv run web2md https://www.php.net/manual/en/funcref.php ./out/ --crawl --max-pages 50 --max-depth 2
```

### Suggested regression tests (`tests/test_crawler.py`)

- **Defect A:** mock a page at `/a/b/` whose HTML links `c.html`; assert the crawler queues
  `/a/b/c.html`, not `/c.html`.
- **Defect B:** mock a page whose HTML contains `<a href="foo[bar">`; assert `crawl()` returns
  the start page (and any valid links) instead of raising.

### Workaround used in the meantime

For the affected sites, page URLs were enumerated out-of-band (`curl` + `grep` the anchor list,
resolve against the page URL) and converted one at a time via single-page `web2md` calls,
bypassing `crawl()` entirely.

---
*Filed by Claude Code during a grounded-code-mcp docs-ingest session, 2026-07-05.*
