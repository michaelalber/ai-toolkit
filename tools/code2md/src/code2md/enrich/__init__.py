"""LLM enrichment for code2md scan output (Phase 1: summaries + questions).

Build-time generation of retrieval *bridges* — natural-language summaries and the
questions each file answers — that improve recall for NL queries against code. The
generated docs carry provenance and point back to the real code (the authority);
they never replace it. grounded-code-mcp ingest stays LLM-free.
"""
