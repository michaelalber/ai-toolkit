from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from pdf2md.models import ConversionConfig


@runtime_checkable
class Engine(Protocol):
    """Common interface for all PDF extraction backends.

    ``convert`` returns a raw Markdown string with no metadata front matter.
    All post-processing (metadata, chunking, file writing) is handled by the
    caller (``converter.py``).
    """

    def convert(self, config: "ConversionConfig") -> str: ...
