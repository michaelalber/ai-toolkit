# Design It Twice — Worked Example

A worked example of the comparison matrix using a file storage service interface.

## Problem

Design an interface for uploading a file and retrieving its URL.

## Design A — Narrow and deep

```python
class FileStore:
    def upload(self, content: bytes, filename: str) -> str:
        """Upload content and return its public URL."""
```

| Dimension | Score | Notes |
|-----------|-------|-------|
| Information hiding | 5 | Hides storage backend, URL format, retry logic |
| Method count | 1 | Maximally simple |
| Conceptual complexity | 1 | Upload bytes, get URL |
| Cohesion | 5 | One concern: file storage |
| Error surface | 2 | Can only pass wrong type (caught by types) |
| **Total** | **14/25** | |

## Design B — Explicit steps

```python
class FileStore:
    def create_upload_session(self, filename: str) -> UploadSession:
        """Create a session for multi-part upload."""

    def upload_chunk(self, session: UploadSession, chunk: bytes, part: int) -> None:
        """Upload a chunk of data."""

    def complete_upload(self, session: UploadSession) -> str:
        """Finalize upload and return URL."""

    def abort_upload(self, session: UploadSession) -> None:
        """Cancel and clean up a partial upload."""
```

| Dimension | Score | Notes |
|-----------|-------|-------|
| Information hiding | 2 | Caller must understand sessions, chunks, ordering |
| Method count | 4 | Each call site must orchestrate 4 steps |
| Conceptual complexity | 4 | Sessions, parts, lifecycle |
| Cohesion | 4 | All about uploads; session management is borderline |
| Error surface | 4 | Many ways to misuse ordering |
| **Total** | **14/25 raw, but inverted** | |

## Recommendation

**Design A wins.** It is deeper: hides the complexity of multi-part uploads behind
a single method. Design B exposes chunking as a caller concern — but chunking is
an implementation detail callers shouldn't need to know about.

**Exception:** Use Design B only if callers genuinely have multi-GB files that cannot
fit in memory. That's a real constraint, not a hypothetical one.
