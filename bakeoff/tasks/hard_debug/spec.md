`confparse` parses INI-like text. Intended format:
- `key = value` lines; `[a.b]` section headers create nested dicts.
- `#` starts a comment unless inside single or double quotes. Comments may also follow section headers.
- Values: quoted strings (quotes removed); `true`/`false` (case-insensitive) become bool; plain decimal numbers (optional leading `-`, optional fractional part; no underscores, exponents, `nan` or `inf`) become int or float; anything else stays a str.

Several tests in `test_confparse.py` fail. Find and fix the root causes in the package. Do not edit the tests.
